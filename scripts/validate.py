"""Check the Arabic deliverable against the pinned W3C source.

These checks validate structure and selected normative invariants, not the
linguistic accuracy or approval status of the translation.
"""
import collections
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlparse
import html5lib
from bs4 import BeautifulSoup
from common import ROOT, source, text, heading, own, glossary_entry, soup
from comparison import OMIT, compact, render_comparison

output = ROOT/'wcag22-ar'
raw = (output/'index.html').read_text()
ar = BeautifulSoup(raw, 'html5lib')
en = source('wcag22-en')
errors, checks = [], []


def check(label, condition, detail=''):
    checks.append({'check':label, 'passed':bool(condition)})
    if not condition:
        errors.append(label+(': '+str(detail) if detail else ''))


def number(h):
    node = h.select_one('.secno')
    m = re.search(r'\d+(?:\.\d+)*', text(node)) if node else None
    return m.group() if m else None


def level(section):
    p = section.find('p', class_='conformance-level', recursive=False)
    m = re.search(r'\bA{1,3}\b', text(p)) if p else None
    return m.group() if m else None


def list_structure(fragment):
    return [(node.name, len(node.find_all('li',recursive=False)),
             node.get('start'),node.get('reversed'),node.get('type'))
            for node in soup(fragment).select('ul,ol')]


parser = html5lib.HTMLParser()
parser.parse(raw)
check('HTML5 parsing has no errors', not parser.errors, parser.errors[:5])
check('Document declares Arabic and right-to-left direction', ar.html.get('lang')=='ar' and ar.html.get('dir')=='rtl')
ids = [x['id'] for x in ar.select('[id]')]
duplicates = [x for x,n in collections.Counter(ids).items() if n>1]
check('All IDs are unique', not duplicates, duplicates)
broken = sorted({a['href'] for a in ar.select('a[href^="#"]') if unquote(a['href'][1:]) not in ids})
check('Every internal link resolves', not broken, broken)
en_sections = en.select('section[id]')
ar_sections = ar.select('section[id]')
check('All 140 source sections occur in source order', [s['id'] for s in ar_sections]==[s['id'] for s in en_sections] and len(ar_sections)==140)
for sec in en_sections:
    target = ar.find('section', id=sec['id'])
    if target is None:
        continue
    check('Section number: '+sec['id'], number(heading(sec))==number(heading(target)))
    check('Conformance level: '+sec['id'], level(sec)==level(target))
    parent = sec.find_parent('section')
    ar_parent = target.find_parent('section')
    check('Parent section: '+sec['id'], (parent.get('id') if parent else None)==(ar_parent.get('id') if ar_parent else None))
    if sec['id']!='glossary':
        check('List types and item counts: '+sec['id'],
              list_structure(own(heading(sec)))==list_structure(own(heading(target))))
        for kind in ['note','example']:
            check(kind+' count: '+sec['id'], len(soup(own(heading(sec))).select('.'+kind))==len(soup(own(heading(target))).select('.'+kind)))
check('86 active success criteria', sum(bool(level(s)) for s in ar_sections)==86)
expected_new = {'focus-not-obscured-minimum':'AA','focus-not-obscured-enhanced':'AAA','focus-appearance':'AAA',
                'dragging-movements':'AA','target-size-minimum':'AA','consistent-help':'A','redundant-entry':'A',
                'accessible-authentication-minimum':'AA','accessible-authentication-enhanced':'AAA'}
check('Nine new criteria retain their correct levels', all(level(ar.find(id=i))==v for i,v in expected_new.items()))
check('4.1.1 remains only as an obsolete criterion with an informative note', not level(ar.find(id='parsing')) and 'محذوف' in text(heading(ar.find(id='parsing'))) and bool(ar.select('#parsing .note')))
en_defs = en.select('#glossary dfn')
ar_defs = ar.select('#glossary dfn')
check('All 101 glossary definitions occur in source order', [d['id'] for d in ar_defs]==[d['id'] for d in en_defs] and len(ar_defs)==101)
for d in en_defs:
    target = ar.find(id=d['id'])
    if target is None:
        continue
    check('Definition list types and item counts: '+d['id'],
          list_structure(str(glossary_entry(d)[1]))==list_structure(str(glossary_entry(target)[1])))
    for kind in ['note','example']:
        check(kind+' count: '+d['id'], len(glossary_entry(d)[1].select('.'+kind))==len(glossary_entry(target)[1].select('.'+kind)))
check('HTML input-purpose identifiers remain unchanged', [text(x) for x in en.select('#input-purposes li > code')]==[text(x) for x in ar.select('#input-purposes li > code')])
check('All source document-help URLs are preserved', [x['href'] for x in en.select('.doclinks a')]==[x['href'] for x in ar.select('.doclinks a')])
check('Original W3C template header and contents markup are present', bool(ar.select_one('.head h1#title')) and bool(ar.select_one('nav#toc > ol.toc')) and len(ar.select('.header-wrapper'))==len(en.select('.header-wrapper')))
check('Draft status is explicit', text(ar.find(id='translation-status'))=='مسودة الترجمة العربية')
check('Added process explanations are absent from the reading document',
      not ar.select('.translation-note,.translation-link-status') and
      all(value not in text(ar.body) for value in ['تعتمد هذه المسودة','تستند هذه المسودة','تنويه خاص بالترجمة']))
check('Heading decimal numbers are isolated from Arabic labels', all(
    n.get('dir')=='ltr' and not re.search(r'[\u0600-\u06ff]',text(n))
    for n in ar.select('.header-wrapper .secno') if re.match(r'^\d',text(n))))
check('Contents numbers have separate title columns', all(
    n.get('dir')=='ltr' and n.parent.select_one('.toc-title') and 'toc-with-number' in n.parent.get('class',[])
    for n in ar.select('#toc .secno') if re.match(r'^\d',text(n))))

# Translation attribution is checked against the published Arabic reference,
# independently of the English specification's editor and contributor lists.
reference_credits = source('wcag21-ar').select_one('.transheader')
credits = ar.find(id='translation-contributors')
check('Published Arabic organization and coordinator are credited', credits is not None and all(
    value in text(credits) and value in text(reference_credits)
    for value in ['مركز مدى، قطر', 'Mada Center, Qatar', 'أشرف عثمان', 'Achraf Othman', 'aothman@mada.org.qa', '24230']))
reference_links = {a['href'] for a in reference_credits.select('a[href]')}
credit_links = {a['href'] for a in credits.select('a[href]') if urlparse(a['href']).scheme} if credits else set()
committee_url = 'https://aiaeg.mada.org.qa/%d8%a7%d9%84%d8%a3%d8%b9%d8%b6%d8%a7%d8%a1/'
translation_archive_url = 'https://lists.w3.org/Archives/Public/w3c-translators/'
english_source_url = en.select_one('.head a.u-url')['href']
publication = json.loads((ROOT/'publication.json').read_text())
publication_urls = {publication['current_version_url'],publication['latest_version_url']}
check('Translation-header links follow the source references and user-provided replacement addresses',
      bool(credit_links) and credit_links <= reference_links | {committee_url,translation_archive_url,english_source_url} | publication_urls)
check('Current and latest version links use the configured public HTML preview',all(
    ar.find(id=ident) is not None and ar.find(id=ident).get('href')==publication[key] and
    urlparse(publication[key]).scheme=='https'
    for ident,key in [('translation-current-version','current_version_url'),('translation-latest-version','latest_version_url')]))
check('Committee link uses the user-provided address', committee_url in credit_links and
      not any('reviewers-committee-members/' in url for url in credit_links))
check('Comments and errata use the user-provided W3C translators archive',all(
    ar.find(id=ident) is not None and ar.find(id=ident).get('href')==translation_archive_url
    for ident in ['translation-comments-link','translation-errata-link']))
check('Organization and coordinator labels refer to 2.2 as requested', credits is not None and
    credits.find(id='translation-lead-label') is not None and
    text(credits.find(id='translation-lead-label')).replace(' :',':')=='المنظمة المشرفة على ترجمة 2.2:' and
    'منسق ترجمة 2.2' in text(credits))
check('Translation header and contents label refer only to 2.2', credits is not None and
    '2.1' not in str(credits) and not credits.select('a[href*="WCAG21"]') and
    '2.1' not in text(ar.select_one('#toc a[href="#translation-contributors"]')) and all(
    value in text(credits) for value in ['لجنة مراجعة الترجمة العربية 2.2',
    'تعليقات الترجمة العربية 2.2','تصحيحات الترجمة العربية 2.2']))
check('Bilingual translation header follows the Arabic 2.1 structure before the W3C header',
      credits is not None and 'transheader' in credits.get('class',[]) and
      credits.find_next_sibling('div',class_='head') is not None and
      credits.select_one('div[lang="en"][dir="ltr"] > h1.transtitle') is not None and
      credits.select_one('div[lang="ar"][dir="rtl"] > h1.transtitle') is not None and
      credits.select_one('.translation-arabic > dl') is not None)
check('Translation header identifies a dated review draft without inherited approval claims',
      'مسودة للمراجعة' in text(credits) and credits.select_one('time[datetime="2026-11-06"]') is not None and
      all(phrase not in text(credits) for phrase in ['مشروع ترجمة عربية معتمدة','هذه ترجمة معتمدة لوثيقة W3C']))
check('Right-edge status strip identifies the Arabic 2.2 review draft',
      ar.find(id='translation-ribbon') is not None and
      text(ar.find(id='translation-ribbon'))=='WCAG 2.2 — مسودة ترجمة عربية')
check('Local translation-header links resolve', all(
    (output/unquote(a['href'].split('#')[0])).is_file()
    for a in credits.select('a[href]') if not urlparse(a['href']).scheme and not a['href'].startswith('#')))
check('English specification editors are preserved separately',
    [text(x) for x in en.select('.head dd.editor')]==[text(x) for x in ar.select('.head dd.editor')])
for contributor_id in ['ack_participants-active', 'ack_participants-previous']:
    check('English specification contributors: '+contributor_id,
          text(soup(own(heading(en.find(id=contributor_id)))))==text(soup(own(heading(ar.find(id=contributor_id))))))

# Independent numerical and exception checks for requirements introduced in 2.2.
small = ar.find(id='target-size-minimum')
check('2.5.8 has five exception categories and the 24 CSS-pixel threshold', len(small.select('dl > dt'))==5 and '24 × 24' in text(small))
focus = ar.find(id='focus-appearance')
check('2.4.13 retains the 3:1 contrast requirement and two exceptions', '3:1' in text(focus) and len(focus.find_all('ul',recursive=False))==2 and len(focus.find_all('ul',recursive=False)[1].find_all('li',recursive=False))==2)
check('Authentication exceptions: four at AA, two at AAA', len(ar.select('#accessible-authentication-minimum dl > dt'))==4 and len(ar.select('#accessible-authentication-enhanced dl > dt'))==2)
lum = text(glossary_entry(ar.find(id='dfn-relative-luminance'))[1])
check('All three updated sRGB channel formulas are present', all(f'{channel}sRGB <= 0.04045' in lum for channel in 'RGB') and all(f'{channel} = (({channel}sRGB+0.055)/1.055) ^ 2.4' in lum for channel in 'RGB'))
check('Red-flash definition uses the updated CIE threshold', all(x in text(glossary_entry(ar.find(id='dfn-general-flash-and-red-flash-thresholds'))[1]) for x in ['0.8','0.2','CIE 1976 UCS']))

missing_files=[]
for node in ar.select('[src],link[rel="stylesheet"]'):
    url = node.get('src') or node.get('href')
    if not urlparse(url).scheme and not (output/unquote(url.split('#')[0])).is_file():
        missing_files.append(url)
for css in (output/'assets').glob('*.css'):
    for url in re.findall(r'url\([\"\']?([^\)\"\']+)', css.read_text()):
        if not urlparse(url).scheme and not (css.parent/unquote(url)).is_file():
            missing_files.append(str(css)+': '+url)
check('All local style and image dependencies exist', not missing_files, missing_files)
check('No runtime scripts or remote display assets are needed', not ar.select('script,[src^="https:"],link[rel="stylesheet"][href^="https:"]'))

# Exempt source names/bibliography and technical identifiers, never untranslated prose.
english_blocks=[]
for p in ar.select('section p,section li,section dd'):
    if p.find_parent(attrs={'lang':'en'}) or p.get('lang')=='en':
        continue
    t=text(p)
    if len(t)>70 and not re.search(r'[\u0600-\u06ff]',t):
        english_blocks.append(t[:120])
check('No untranslated English prose blocks', not english_blocks, english_blocks)

# The exported file must agree with current inputs. A reviewer may check a row,
# but edits to either passage must go through the translation inputs.
comparison_path=output/'TRANSLATION-COMPARISON.md'
expected_md,comparison=render_comparison(en,ar)
actual_md=comparison_path.read_text() if comparison_path.exists() else ''
unchecked_md=re.sub(r' \| \[[xX]\] \|$', ' | [ ] |',actual_md,flags=re.M)
check('Bilingual Markdown matches the current English and Arabic passages',unchecked_md==expected_md)
unit_ids={u['id'] for u in comparison['units']}
check('Bilingual review includes every source section and glossary entry',
      {s['id'] for s in en_sections} | {d['id'] for d in en_defs} <= unit_ids)
check('Every source review passage has an Arabic counterpart', all(
    row['arabic'] for row in comparison['rows'] if row['english']))
check('Comparison row identifiers are unique',len({r['id'] for r in comparison['rows']})==len(comparison['rows']))

# Independent whole-document accounting catches content accidentally omitted by
# section extraction. Sequence is checked per unit by the exporter; here every
# visible character must also occur exactly as often across the complete export.
for lang,document in [('english',en),('arabic',ar)]:
    visible=soup(str(document.body))
    for node in visible.select(OMIT+',script,style,.dfn-panel,.logos'):
        node.decompose()
    check('Complete document text coverage: '+lang,
          collections.Counter(compact(text(visible))) ==
          collections.Counter(compact(''.join(row[lang] for row in comparison['rows']))))

report = {'passed':not errors, 'checks_run':len(checks), 'errors':errors,
          'counts':{'sections':len(ar_sections),'active_success_criteria':sum(bool(level(s)) for s in ar_sections),'glossary_definitions':len(ar_defs)},
          'comparison_rows':len(comparison['rows']),
          'visual_review':'Not performed: browser access is disabled in the app settings.',
          'linguistic_review':'Draft; human linguistic and normative review is still required.',
          'checks':checks}
(ROOT/'reports/validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
if errors:
    for error in errors:
        print('FAIL:',error)
    raise SystemExit(1)
print(f'PASS: {len(checks)} checks; 140 sections; 86 active success criteria; 101 definitions. Visual and linguistic review remain separate.')
