"""Record English 2.1→2.2 differences without rewriting source numbers."""
import difflib
import json
from common import ROOT, source, soup, text, heading, own, previous_id, glossary_entry

a,b=source('wcag21-en'),source('wcag22-en')
coverage=json.loads((ROOT/'reports/translation-coverage.json').read_text())
statuses={x['id']:x['status'] for x in coverage['sections']+coverage['terms']}
def prose(fragment):
    s=soup(fragment)
    for t in s.select('.note-title,.example-title,.marker,.change,.doclinks,.permalink,.self-link'):
        t.decompose()
    return text(s)
def delta(ident,before,after,kind):
    if before==after:return None
    return dict(id=ident,kind=kind,translation_status=statuses.get(ident),
                english_21=before,english_22=after,
                diff=list(difflib.unified_diff(before.splitlines(),after.splitlines(),fromfile='English WCAG 2.1',tofile='English WCAG 2.2',lineterm='')))
results=[]
for s in b.select('section[id]'):
    if s['id']=='glossary':continue
    old=a.find('section',id=previous_id(s['id']))
    item=delta(s['id'],prose(own(heading(old))) if old else '',prose(own(heading(s))),'section-body')
    if item:results.append(item)
for d in b.select('#glossary dfn'):
    old=a.find(id=previous_id(d['id']))
    item=delta(d['id'],prose(str(glossary_entry(old)[1])) if old else '',prose(str(glossary_entry(d)[1])),'definition')
    if item:results.append(item)
(ROOT/'reports/source-differences.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print(f'Recorded {len(results)} English source differences, including editorial changes.')
