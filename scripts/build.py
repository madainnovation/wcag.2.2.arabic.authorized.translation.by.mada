"""Build the Arabic review draft from pinned sources and explicit translations."""
import copy
import shutil
import html
import json
import re
from common import ROOT, soup, source, text, heading, title, own, previous_id, glossary_entry

EN21, AR21, EN22 = (source(n) for n in ['wcag21-en', 'wcag21-ar', 'wcag22-en'])
PATCHES = {s['id']: s for s in soup((ROOT/'translation/changes.html').read_text()).select('section[id]')}
EDITS = json.loads((ROOT/'translation/edits.json').read_text())
NEW = ['focus-not-obscured-minimum', 'focus-not-obscured-enhanced', 'focus-appearance',
       'dragging-movements', 'target-size-minimum', 'consistent-help', 'redundant-entry',
       'accessible-authentication-minimum', 'accessible-authentication-enhanced']
ALIASES = {'target-size': 'target-size-enhanced', 'dfn-target': 'dfn-targets',
           'dfn-conforming-alternate-version': 'dfn-conforming-alternate-versions'}
records, terms, titles, used_edits = [], [], {}, set()

def upgrade(html_text):
    # Replace version references, never success-criterion numbers such as 2.1.1.
    html_text = re.sub(r'(WCAG\s*|مبادئ النفاذ إلى محتوى الويب\s*)2\.1(?!\d)', r'\g<1>2.2', html_text)
    b = soup(html_text)
    for a in b.select('a[href]'):
        href = a['href']
        if href.startswith('#'):
            target = ALIASES.get(href[1:], href[1:])
            if target.startswith('bib-'):
                target = target.lower()
            a['href'] = '#'+target
        else:
            a['href'] = href.replace('/WCAG21/', '/WCAG22/').replace('/TR/UNDERSTANDING-WCAG20/', '/WAI/WCAG22/Understanding/').replace('/TR/UNDERSTANDING-WCAG21/', '/WAI/WCAG22/Understanding/')
    return str(b)

def clean(fragment):
    b = soup(fragment)
    for t in b.select('script,style,.permalink,.self-link,.doclinks,.conformance-level,.new-label'):
        t.decompose()
    for t in b.find_all(True):
        for attr in list(t.attrs):
            if attr.startswith('data-') or attr in ['style','aria-describedby','aria-labelledby']:
                del t[attr]
        if t.get('id', '').startswith(('issue-container-', 'h-note-', 'h-example-', 'ref-for-')):
            del t['id']
        if t.name == 'a':
            t.attrs.pop('title', None)
            t.attrs.pop('aria-label', None)
        if t.name in ['p','li','dt','dd']:
            # Collapse formatting whitespace only; preserve Arabic words and punctuation.
            for child in list(t.children):
                if isinstance(child, str):
                    child.replace_with(re.sub(r'\s+', ' ', child))
    return str(b)

def edited(ident, fragment):
    b = soup(fragment)
    for i, edit in enumerate(EDITS):
        if edit['unit'] != ident:
            continue
        selected = b.select(edit['selector'])
        if edit.get('contains'):
            selected = [x for x in selected if edit['contains'] in text(x)]
        if len(selected) != 1:
            raise ValueError(f'Edit {i}: expected one match in {ident}, found {len(selected)}')
        target = selected[0]
        if edit.get('remove'):
            target.decompose()
        elif 'tag' in edit:
            target.name = edit['tag']
        elif 'attributes' in edit:
            target.attrs.update(edit['attributes'])
        elif 'replace_text' in edit:
            old, new = edit['replace_text']
            matches = [x for x in target.find_all(string=True) if old in str(x)]
            if len(matches) != edit.get('count', 1):
                raise ValueError(f'Edit {i}: ambiguous/missing literal text')
            for match in matches:
                match.replace_with(str(match).replace(old, new))
        else:
            target.clear()
            for node in list(soup(edit['html']).contents):
                target.append(node)
        used_edits.add(i)
    return str(b)

def arabic_heading(sec):
    old = EN21.find(id=previous_id(sec['id']))
    return AR21.find(id=heading(old).get('id')) if old else None

def section_title(sec):
    ident = sec['id']
    if ident in PATCHES and heading(PATCHES[ident]):
        return title(heading(PATCHES[ident]))
    ah = arabic_heading(sec)
    if ah is None:
        raise ValueError('Missing Arabic heading: '+ident)
    value = title(ah)
    value = re.sub(r'^(?:معيار النجاح|معايير النجاح|توجيه|التوجيه)\s*[\d.]+\s*', '', value)
    value = re.sub(r'^أ\.?\s*\d*\s*', '', value) if value.startswith('أ.') else value
    value = value.replace('2.1', '2.2') if 'wcag-2-2' in ident else value
    if ident == 'target-size-enhanced':
        value += ' (محسن)'
    return value.strip()

for sec in EN22.select('section[id]'):
    h = heading(sec)
    no = h.select_one('.secno')
    number = re.search(r'\d+(?:\.\d+)*|^[ABC](?:\.\d+)?', text(no)) if no else None
    number = number.group().rstrip('.') if number else ''
    level = sec.find('p', class_='conformance-level', recursive=False)
    titles[sec['id']] = dict(ar=section_title(sec), en=title(h), number=number,
                             level=re.search(r'\bA{1,3}\b', text(level)).group() if level else None)

def glossary():
    entries = []
    for d in EN22.select('#glossary dfn'):
        ident = d['id']; old = AR21.find(id=previous_id(ident))
        qualifier = ''
        if ident in PATCHES:
            term = title(heading(PATCHES[ident])); body = own(heading(PATCHES[ident]))
            status = 'new-draft' if old is None else 'revised-draft'
        else:
            if old is None:
                raise ValueError('Missing Arabic definition: '+ident)
            dt, dd = glossary_entry(old)
            term = text(old)
            qualifier = text(dt).removeprefix(term).strip()
            body = upgrade(dd.decode_contents())
            status = 'inherited-2.1'
        body = edited(ident, body)
        if any(x['unit']==ident for x in EDITS): status='revised-draft'
        # Source 2.2 reclassifies several inherited notes as examples.
        body_dom = soup(body)
        source_notes = glossary_entry(d)[1].select('.note,.example')
        target_notes = body_dom.select('.note,.example')
        if len(source_notes) != len(target_notes):
            raise ValueError('Glossary note/example count differs: '+ident)
        for en_note, ar_note in zip(source_notes, target_notes):
            kind = 'note' if 'note' in en_note.get('class', []) else 'example'
            ar_note['class'] = [kind]
            ar_note.attrs.pop('role', None)
        body = str(body_dom)
        entries.append(f'<dt><dfn id="{ident}">{html.escape(term)}</dfn> {html.escape(qualifier)}</dt><dd>{clean(body)}</dd>')
        terms.append(dict(id=ident, english=text(d), arabic=term, status=status,
                          reference_id=previous_id(ident) if old else None))
    return '<dl>'+''.join(entries)+'</dl>'

def build_section(sec):
    ident = sec['id']; info = titles[ident]; patch = PATCHES.get(ident)
    ah = arabic_heading(sec)
    body = upgrade(own(ah)) if ah else ''
    status = 'inherited-2.1'
    if ident == 'glossary':
        body = glossary(); status='assembled-glossary'
    elif ident in ['ack_participants-active', 'ack_participants-previous', 'informative-references']:
        body = '<div lang="en" dir="ltr">'+own(heading(sec))+'</div>'
        status='source-names-and-bibliography'
    if patch:
        contents = own(heading(patch)) if heading(patch) else patch.decode_contents()
        body = body+'\n'+contents if patch.get('data-mode')=='append' else contents
        status = 'new-draft' if not ah else 'revised-draft'
    body = edited(ident, body)
    if any(x['unit']==ident for x in EDITS): status='revised-draft'
    body_soup = soup(body)
    # Preserve machine-readable input purpose names exactly as in WCAG 2.2.
    if ident == 'input-purposes':
        source_items = sec.select('ul > li')
        target_items = body_soup.select('ul > li')
        if len(source_items)!=len(target_items): raise ValueError('Input-purpose list mismatch')
        for en, ar in zip(source_items, target_items):
            codes = en.select('code')
            labels = ar.select('strong')
            if len(codes) != len(labels):
                raise ValueError('Input-purpose identifier count mismatch')
            for source_code, label in zip(codes, labels):
                code = copy.deepcopy(source_code)
                code['dir']='ltr';code['lang']='en'
                label.replace_with(code)
    # Render lists from source IDs, so levels/numbering cannot drift.
    for ul in body_soup.select('ul[data-criterion-list]'):
        key = ul['data-criterion-list']
        refs = NEW if key=='new' else [a['href'][1:] for a in EN22.find(id=key+'-summary').select('ul a[href^="#"]')]
        for ref in refs:
            t=titles[ref]
            ul.append(soup(f'<li><bdi dir="ltr">{t["number"]}</bdi> <a href="#{ref}">{html.escape(t["ar"])}</a> (<bdi dir="ltr">{t["level"]}</bdi>)</li>'))
    body = clean(str(body_soup))
    prefix = 'معيار النجاح ' if info['level'] or ident=='parsing' else 'توجيه ' if heading(sec).name=='h3' and sec.get('class')==['guideline'] else ''
    num = info['number'].replace('A','أ').replace('B','ب').replace('C','ج')
    label = (prefix+f'<bdi dir="ltr">{num}</bdi> ' if num else '')+html.escape(info['ar'])
    htag = heading(sec).name
    head = f'<{htag} id="{heading(sec).get("id", ident+"-heading")}">{label} <a class="permalink" href="#{ident}" aria-label="رابط دائم إلى {html.escape(info["ar"])}">§</a></{htag}>'
    extras = ''
    if info['level']:
        extras += f'<p class="conformance-level">(مستوى <bdi dir="ltr">{info["level"]}</bdi>)</p>'
    if ident in NEW:
        extras += '<p class="new-label">جديد في WCAG 2.2</p>'
    for docs in sec.find_all('div', class_='doclinks', recursive=False):
        links=docs.select('a[href]')
        extras += '<p class="doclinks">'+ ' · '.join(f'<a href="{a["href"]}">{"فهم" if i==0 else "كيفية تلبية"} {html.escape(info["ar"])} (بالإنجليزية)</a>' for i,a in enumerate(links))+'</p>'
    children=''.join(build_section(child) for child in sec.find_all('section',recursive=False))
    records.append(dict(id=ident,number=info['number'],title_ar=info['ar'],level=info['level'],status=status,
                        english_source='https://www.w3.org/TR/2024/REC-WCAG22-20241212/#'+ident))
    return f'<section id="{ident}" data-translation-status="{status}">{head}{extras}{body}{children}</section>'

body = ''.join(build_section(s) for s in EN22.body.find_all('section',recursive=False))
if used_edits != set(range(len(EDITS))): raise ValueError('Unused edits: '+str(set(range(len(EDITS)))-used_edits))
from w3c_template import render_template
page = render_template(EN22, soup('<main>'+body+'</main>'), titles)
ids = {x['id'] for x in page.select('[id]')}
for a in page.select('a[href^="#"]'):
    target = a['href'][1:]
    if target not in ids and target.lower() in ids:
        a['href'] = '#'+target.lower()
out = ROOT/'wcag22-ar'
out.mkdir(exist_ok=True)
(out/'.nojekyll').write_text('')
shutil.copytree(ROOT/'references/template-assets', out/'assets', dirs_exist_ok=True)
base_css = (out/'assets/base.css').read_text().replace('https://www.w3.org/StyleSheets/TR/2021/', '')
(out/'assets/base.css').write_text(base_css)
shutil.copyfile(ROOT/'translation/rtl.css', out/'assets/translation-rtl.css')
(out/'index.html').write_text(str(page)+'\n')
from comparison import write_comparison
comparison_report = write_comparison(EN22, page)
(ROOT/'index.html').write_text('''<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=wcag22-ar/index.html"><title>مبادئ النفاذ إلى محتوى الويب 2.2 — المسودة العربية</title></head><body><p><a href="wcag22-ar/index.html">افتح مسودة الترجمة العربية لمبادئ النفاذ إلى محتوى الويب 2.2</a></p></body></html>\n''')
(ROOT/'reports/translation-coverage.json').write_text(json.dumps(dict(sections=records,terms=terms),ensure_ascii=False,indent=2)+'\n')
lines=['# Terminology register','', 'The Arabic WCAG 2.1 text is the terminology authority. New terms below are proposals, pending human review. Existing terms remain as published, including singular/plural forms. Criterion titles remain as published except for the added 2.2 qualifiers.','',
'Core convention: **accessibility → النفاذ**. For new text, use **التركيز** for focus and **مؤشر التركيز** for focus indicator, while retaining the published titles “مسار المؤشر” (2.4.3) and “ظهور المؤشر” (2.4.7). The published 2.1 text uses “مصادقة” in 2.2.5; the proposed new authentication titles build on that usage.','',
'| English term | Arabic term | Basis |','|---|---|---|']
for t in terms:
    basis='Proposed for 2.2' if t['reference_id'] is None else '[Published 2.1](https://www.w3.org/Translations/WCAG21-ar/#'+t['reference_id']+')'
    lines.append(f'| {t["english"]} | {t["arabic"]} | {basis} |')
lines += ['', '## New success-criterion titles','', '| Criterion | English | Proposed Arabic |','|---|---|---|']
for ident in NEW:
    t=titles[ident];lines.append(f'| {t["number"]} | {t["en"]} | {t["ar"]} |')
(ROOT/'TERMINOLOGY.md').write_text('\n'.join(lines)+'\n')
shutil.copyfile(ROOT/'TERMINOLOGY.md', out/'TERMINOLOGY.md')
for document in ['REVIEW.md', 'SOURCES.md']:
    if (ROOT/document).exists():
        shutil.copyfile(ROOT/document, out/document)
print(f'Built {len(records)} sections, {sum(bool(r["level"]) for r in records)} active success criteria, {len(terms)} glossary terms.')
print(f'Exported {len(comparison_report["rows"])} English–Arabic review rows.')
