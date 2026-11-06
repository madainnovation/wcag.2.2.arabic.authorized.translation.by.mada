"""Export complete, ordered bilingual passages without guessing sentence matches."""
import copy
import hashlib
import html
import json
import re
from dataclasses import dataclass, field
from bs4 import Tag, NavigableString, Comment
from common import ROOT, soup, source, text, heading, own, glossary_entry

# Generated UI markers are represented by the passage type, not by their counters.
OMIT = '.note-title,.example-title,.marker,.self-link,.permalink,.screenreader'
BLOCK_TAGS = {'p','div','aside','ul','ol','li','dl','dt','dd','details','summary',
              'h1','h2','h3','h4','h5','h6','pre','blockquote','table','figure'}


@dataclass
class Block:
    kind: str
    value: str = ''
    children: list = field(default_factory=list)

    def passage(self):
        return self.value if not self.children else '\n\n'.join(x.passage() for x in self.children)


def clean(fragment):
    dom = soup(str(fragment))
    for node in dom.select(OMIT):
        node.decompose()
    return dom


def compact(value):
    return re.sub(r'\s+', '', value)


def sequence(container):
    """Normalize transparent wrappers and paragraph wrappers inside list items."""
    result, inline = [], []

    def flush():
        if inline:
            value = text(soup(''.join(str(x) for x in inline)))
            if value:
                result.append(Block('paragraph', value))
            inline.clear()

    for node in container.children:
        if isinstance(node, Comment):
            continue
        if isinstance(node, NavigableString) or node.name not in BLOCK_TAGS:
            inline.append(node)
            continue
        flush()
        classes = node.get('class', [])
        if set(classes) & {'change','conformance-level','doclinks'}:
            kind = next(c for c in ['change','conformance-level','doclinks'] if c in classes)
            result.append(Block(kind, text(node)))
        elif 'note' in classes or 'example' in classes:
            kind = 'note' if 'note' in classes else 'example'
            result.append(Block(kind, children=sequence(node)))
        elif node.name in {'div','aside','details'}:
            result.extend(sequence(node))
        elif node.name in {'ol','ul','li','dl','dd'}:
            result.append(Block(node.name, children=sequence(node)))
        elif node.name == 'p':
            result.append(Block('paragraph', text(node)))
        else:
            result.append(Block('heading' if re.fullmatch(r'h[1-6]',node.name) else node.name, text(node)))
    flush()
    return result


def merged_paragraph_runs(nodes):
    """A translator may split/merge paragraphs; keep that entire passage together."""
    result = []
    for node in nodes:
        if node.kind == 'paragraph' and result and result[-1].kind == 'paragraph':
            result[-1] = Block('paragraph', result[-1].passage()+'\n\n'+node.passage())
        else:
            result.append(node)
    return result


def normalize_example_nesting(ident, nodes):
    # Published Arabic 2.1 places two example fragments beside their containers.
    # Group these only in the comparison; no text is added, dropped or reordered.
    for node in nodes:
        if node.children:
            normalize_example_nesting(ident,node.children)
    if ident == 'dfn-assistive-technologies' and len(nodes)>1:
        if nodes[-2].kind=='example' and nodes[-1].kind=='ul':
            nodes[-2].children.append(nodes.pop())
    if ident == 'dfn-keyboard-interface':
        for i in range(1,len(nodes)):
            if nodes[i].kind=='example' and nodes[i-1].kind=='note':
                nodes[i-1].children.append(nodes.pop(i))
                break
    return nodes


LABELS = {'paragraph':'Paragraph', 'heading':'Heading', 'ol':'Numbered list',
          'ul':'Bulleted list', 'li':'Item', 'dl':'Definitions / exceptions',
          'dt':'Term / label', 'dd':'Description', 'note':'Note (informative)',
          'example':'Example (informative)', 'summary':'Details label',
          'change':'New in 2.2 label', 'conformance-level':'Conformance level',
          'doclinks':'Supporting-document links',
          'pre':'Preformatted passage'}


def align(en_nodes, ar_nodes, path=''):
    """Pair matching structures; group ambiguous boundaries within the same unit."""
    if not en_nodes and not ar_nodes:
        return []
    if not en_nodes:
        return [(kind,'',value,False) for kind,_,value,_ in align(ar_nodes,ar_nodes,path+'Arabic-only')]
    if not ar_nodes:
        return [(kind,value,'',False) for kind,value,_,_ in align(en_nodes,en_nodes,path+'English-only')]
    ek, ak = [n.kind for n in en_nodes], [n.kind for n in ar_nodes]
    if ek != ak:
        en_nodes = merged_paragraph_runs(en_nodes)
        ar_nodes = merged_paragraph_runs(ar_nodes)
        ek, ak = [n.kind for n in en_nodes], [n.kind for n in ar_nodes]
    if ek != ak:
        return [(path+' / Grouped passage', '\n\n'.join(n.passage() for n in en_nodes),
                 '\n\n'.join(n.passage() for n in ar_nodes), True)]
    result, counters = [], {}
    for e,a in zip(en_nodes,ar_nodes):
        counters[e.kind] = counters.get(e.kind,0)+1
        label = LABELS.get(e.kind,e.kind)+' '+str(counters[e.kind])
        label = (path+' / ' if path else '')+label
        if e.children and a.children:
            result.extend(align(e.children,a.children,label))
        else:
            result.append((label,e.passage(),a.passage(),False))
    return result


def cell(value, language):
    if language=='ar' and re.search(r'[A-Za-z]',value) and not re.search(r'[\u0600-\u06ff]',value):
        language='en'
    value = html.escape(value, quote=False).replace('|','&#124;')
    # Avoid Markdown interpreting literal technical identifiers as emphasis.
    value = value.replace('\\','&#92;').replace('*','&#42;').replace('_','&#95;').replace('`','&#96;')
    value = value.replace('\n\n','<br><br>').replace('\n','<br>')
    return f'<span lang="{language}" dir="{"rtl" if language=="ar" else "ltr"}">{value}</span>' if value else '—'


class Comparison:
    def __init__(self):
        self.units, self.rows, self.blocks = [], [], []

    def unit(self, ident, label, english, arabic, source_url=None, local_id=None, note=None):
        e, a = clean(english), clean(arabic)
        en_nodes = normalize_example_nesting(ident,sequence(e))
        ar_nodes = normalize_example_nesting(ident,sequence(a))
        pairs = align(en_nodes,ar_nodes)
        ev, av = text(e), text(a)
        if compact(ev) != compact(''.join(p[1] for p in pairs)):
            raise ValueError('English comparison coverage differs: '+ident)
        if compact(av) != compact(''.join(p[2] for p in pairs)):
            raise ValueError('Arabic comparison coverage differs: '+ident)
        rows=[]
        for i,(kind,en,ar,grouped) in enumerate(pairs,1):
            row={'id':f'{ident}:{i:03}', 'kind':kind, 'english':en,'arabic':ar,'grouped':grouped}
            rows.append(row)
            self.rows.append(row)
        self.units.append({'id':ident, 'rows':len(rows), 'english_characters':len(ev),
                           'arabic_characters':len(av), 'english_sha256':hashlib.sha256(compact(ev).encode()).hexdigest(),
                           'arabic_sha256':hashlib.sha256(compact(av).encode()).hexdigest()})
        self.blocks += [f'## {label}', '', f'Unit: `{ident}`', '']
        links=[]
        if source_url: links.append(f'[English source]({source_url})')
        if local_id: links.append(f'[Arabic document](index.html#{local_id})')
        if links:self.blocks += [' · '.join(links),'']
        if note:self.blocks += [note,'']
        self.blocks += ['| Passage | English | العربية | Confirmed |', '|---|---|---|---|']
        for row in rows:
            self.blocks.append(f'| {row["id"]}<br>{row["kind"]} | {cell(row["english"],"en")} | {cell(row["arabic"],"ar")} | [ ] |')
        self.blocks += ['']


def render_comparison(english, arabic):
    review=Comparison()
    base='https://www.w3.org/TR/2024/REC-WCAG22-20241212/'
    en_head,ar_head=copy.deepcopy(english.select_one('.head')),copy.deepcopy(arabic.select_one('.head'))
    for dom in (en_head,ar_head):
        for node in dom.select('.logos,hr,#translation-contributors'):
            node.decompose()
    review.unit('front-matter','Document title and publication details',en_head,ar_head,base,'title',
                'Publication labels identify the English original and the Arabic draft; they are adapted front matter.')

    for sec in english.select('section[id]'):
        ident=sec['id']; target=arabic.find('section',id=ident)
        source_head=heading(sec); translated_head=heading(target)
        number=source_head.select_one('.secno')
        title_node=translated_head.select_one('.section-title')
        label=(text(number)+' ' if number else '')+(text(title_node) if title_node else text(translated_head))
        en_body=own(source_head); ar_body=own(translated_head)
        if ident=='glossary':
            for_body=[]
            for fragment in (en_body,ar_body):
                dom=soup(fragment)
                for dl in dom.find_all('dl',recursive=False): dl.decompose()
                for_body.append(str(dom))
            en_body,ar_body=for_body
        # Include headings, conformance levels, new labels, and help links once.
        en_parts=[str(source_head)]; ar_parts=[str(translated_head)]
        for cls in ['conformance-level','doclinks']:
            en_item=sec.find(class_=cls,recursive=False); ar_item=target.find(class_=cls,recursive=False)
            if en_item or ar_item:
                en_parts.append(str(en_item) if en_item else '')
                ar_parts.append(str(ar_item) if ar_item else '')
        en_parts.append(en_body); ar_parts.append(ar_body)
        review.unit(ident,label,''.join(en_parts),''.join(ar_parts),base+'#'+ident,ident)
        if ident=='glossary':
            for dfn in sec.select('dfn'):
                en_dt,en_dd=glossary_entry(dfn)
                ar_dt,ar_dd=glossary_entry(arabic.find(id=dfn['id']))
                review.unit(dfn['id'],text(dfn)+' — '+text(arabic.find(id=dfn['id'])),
                            str(en_dt)+str(en_dd),str(ar_dt)+str(ar_dd),base+'#'+dfn['id'],dfn['id'])

    # Include repeated contents labels explicitly so every visible navigation label
    # is reviewable, while passage bodies remain under their own section IDs.
    en_nav,ar_nav=copy.deepcopy(english.find(id='toc')),copy.deepcopy(arabic.find(id='toc'))
    extra=ar_nav.find('a',href='#translation-contributors')
    extra_html=str(extra) if extra else ''
    if extra:extra.parent.decompose()
    review.unit('navigation','Contents and navigation labels',en_nav,ar_nav,base+'#toc','toc')
    review.unit('translation-contents-link','Arabic contributor contents link','',extra_html,
                note='Arabic navigation addition; no English source counterpart.')
    review.unit('back-to-top','Back-to-top label',english.find(id='back-to-top'),arabic.find(id='back-to-top'))
    review.unit('translation-contributors','Bilingual WCAG 2.2 translation header and review resources','',arabic.find(id='translation-contributors'),
                None,'translation-contributors',
                'Translation-specific front matter, including its English contact block; no counterpart in the English WCAG 2.2 Recommendation. The header refers only to WCAG 2.2 at the project owner’s request. The date identifies this review draft. A dash in the English source column is intentional.')
    review.unit('translation-ribbon','Arabic draft status strip','',arabic.find(id='translation-ribbon'),
                note='Visible draft-status label on the right edge; the same status is also stated in the document header.')
    review.unit('skip-link','Arabic navigation addition','',arabic.select_one('.skip-link'),
                note='Arabic navigation addition; no English source counterpart.')
    prefix=['# WCAG 2.2 — English–Arabic translation review','',
            '[English Recommendation, 12 December 2024]('+base+') · [Arabic draft](index.html)','',
            'Each row pairs a heading, paragraph, list item, note, example, or definition. Mark `[ ]` as `[x]` in the Confirmed column after reviewing both texts. Boxes start empty.','',
            'Passages stay in source order. Where paragraph boundaries differ, the corresponding passage is grouped rather than matched sentence by sentence. Notes and examples are identified separately from requirements. Bibliography titles and contributor names retain their source language.','',
            f'Coverage: **140 sections, 86 active success criteria, 101 definitions, {len(review.rows)} comparison rows**. Includes publication details, contents labels, criterion-help labels, and separately identified Arabic-only front matter.','',
            'Rebuilding preserves `[x]` only when the row identifier and both passages remain unchanged. Keep reviewer notes in a separate copy.','']
    return '\n'.join(prefix+review.blocks)+'\n', {'rows':review.rows,'units':review.units}


def preserve_confirmations(md, previous):
    confirmed=set()
    for line in previous.splitlines():
        if line.endswith(' | [x] |') or line.endswith(' | [X] |'):
            confirmed.add(line[:-len(' | [x] |')])
    lines=[]
    for line in md.splitlines():
        if line.endswith(' | [ ] |') and line[:-len(' | [ ] |')] in confirmed:
            line=line.removesuffix(' | [ ] |')+' | [x] |'
        lines.append(line)
    return '\n'.join(lines)+'\n'


def write_comparison(english, arabic):
    md,report=render_comparison(english,arabic)
    destination=ROOT/'wcag22-ar/TRANSLATION-COMPARISON.md'
    previous=destination.read_text() if destination.exists() else ''
    destination.write_text(preserve_confirmations(md,previous))
    (ROOT/'reports/comparison-coverage.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    return report


if __name__=='__main__':
    report=write_comparison(source('wcag22-en'),soup((ROOT/'wcag22-ar/index.html').read_text()))
    print(f'Exported {len(report["rows"])} bilingual rows in {len(report["units"])} units.')
