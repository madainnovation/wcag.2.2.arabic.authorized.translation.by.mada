"""Check external HTTP destinations in the portable document and review files."""
import argparse
import collections
import concurrent.futures
import datetime as dt
import hashlib
import json
import re
import subprocess
import tempfile
import threading
import time
from pathlib import Path
from urllib.parse import urlsplit, urldefrag
from bs4 import BeautifulSoup
from common import ROOT

OUT = ROOT/'wcag22-ar'
CACHE = ROOT/'reports/external-link-cache.json'
DOCUMENTS = ['index.html','README.md','TERMINOLOGY.md','SOURCES.md','REVIEW.md','TRANSLATION-COMPARISON.md']
HOST_LOCKS = collections.defaultdict(lambda: threading.Semaphore(3))


def inventory():
    urls=collections.defaultdict(list)
    non_http=collections.defaultdict(list)
    examples=collections.defaultdict(list)
    for name in DOCUMENTS:
        path=OUT/name
        if not path.exists():continue
        if name.endswith('.html'):
            dom=BeautifulSoup(path.read_text(),'html.parser')
            for node in dom.select('a[href]'):
                url=node['href']
                where=node.find_parent(id=True)
                occurrence={'document':name,'location':where.get('id') if where else '',
                            'label':' '.join(node.get_text(' ',strip=True).split())}
                if urlsplit(url).scheme in {'http','https'}:urls[url].append(occurrence)
                elif urlsplit(url).scheme:non_http[url].append(occurrence)
        else:
            for number,line in enumerate(path.read_text().splitlines(),1):
                for match in re.finditer(r'https?://[^\s<>"`]+',line):
                    url=match.group().rstrip(').,;|')
                    host=urlsplit(url).hostname or ''
                    illustrative=any(host==domain or host.endswith('.'+domain) for domain in ['example.com','example.net','example.org'])
                    target=examples if illustrative else urls
                    target[url].append({'document':name,'location':f'line {number}','label':''})
    return urls,non_http,examples


def request(url):
    with tempfile.NamedTemporaryFile() as body:
        command=['curl','--location','--max-redirs','10','--connect-timeout','10',
                 '--max-time','35','--silent','--show-error','--compressed',
                 '--proto','=http,https','--proto-redir','=http,https',
                 '--user-agent','WCAG-Arabic-Link-Check/1.0',
                 '--output',body.name,'--write-out','%{json}',url]
        start=time.monotonic()
        result=subprocess.run(command,capture_output=True,text=True,timeout=40)
        try:meta=json.loads(result.stdout)
        except json.JSONDecodeError:meta={}
        status=int(meta.get('http_code',0))
        title=''
        if 'html' in (meta.get('content_type') or ''):
            raw=Path(body.name).read_bytes()[:1000000]
            match=re.search(br'<title\b[^>]*>(.*?)</title>',raw,flags=re.I|re.S)
            if match:title=BeautifulSoup(match.group(1).decode('utf-8','replace'),'html.parser').get_text(' ',strip=True)
        return {'http_status':status,'final_url':meta.get('url_effective',url),
                'redirects':meta.get('num_redirects',0),'content_type':meta.get('content_type',''),
                'page_title':title,'curl_exit_code':result.returncode,
                'error':result.stderr.strip(),'seconds':round(time.monotonic()-start,2)}


def check_url(url):
    with HOST_LOCKS[urlsplit(url).netloc]:
        attempts=[]
        for i in range(2):
            try:result=request(url)
            except Exception as error:
                result={'http_status':0,'final_url':url,'error':str(error),'curl_exit_code':-1}
            attempts.append(result)
            if result['http_status'] in {404,410,429} or result['http_status']>=500 or result['curl_exit_code']:
                if i==0:time.sleep(1)
            else:break
        code=result['http_status']
        if code==404:classification='404 Not Found'
        elif code==410:classification='410 Gone'
        elif code in {401,403,429}:classification='Blocked or rate-limited — unverified'
        elif result['curl_exit_code'] or not code:classification='Connection error — unverified'
        elif 200<=code<300:
            classification='HTTP success'
            if re.search(r'page not found|404\s*[-–:|]|not found\s*[-–:|]',result.get('page_title',''),re.I):
                classification='Possible soft 404 — inspect page'
        elif 300<=code<400:classification='Unresolved redirect — unverified'
        else:classification='HTTP error — unverified'
        return {'requested_url':url,'checked_at':dt.datetime.now(dt.timezone.utc).isoformat(),
                'classification':classification,'attempts':attempts,**result}


def write_report(urls,non_http,examples,results):
    rows=[]
    for url,occurrences in sorted(urls.items()):
        base,fragment=urldefrag(url)
        rows.append({'url':url,'fragment':fragment,'occurrences':occurrences,**results[base]})
    counts=collections.Counter(row['classification'] for row in rows)
    document_rows=[r for r in rows if any(o['document']=='index.html' for o in r['occurrences'])]
    report={'generated_at':dt.datetime.now(dt.timezone.utc).isoformat(),
            'documents':DOCUMENTS,'unique_http_links':len(rows),'unique_http_pages':len(results),
            'html_links':len(document_rows),'html_counts':dict(collections.Counter(r['classification'] for r in document_rows)),
            'counts':dict(counts),'non_http_links':dict(non_http),'illustrative_urls':dict(examples),'links':rows,
            'file_sha256':{n:hashlib.sha256((OUT/n).read_bytes()).hexdigest() for n in DOCUMENTS if (OUT/n).exists()}}
    (ROOT/'reports/external-links.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    lines=['# External link check','',f'Checked: {report["generated_at"]}','',
           'Scope: the Arabic HTML document and its README, terminology register, sources, review notes, and English–Arabic comparison.','',
           f'**{len(rows)} distinct HTTP(S) links, {len(results)} page requests.** The HTML document contains {len(document_rows)} of these distinct links.','',
           'Checks use GET requests, follow redirects, and retry 404s and connection/server failures once. Fragment variants share their page’s HTTP result; fragment targets are not checked. HTTP success means the destination responded, not that its content is the correct translation resource. Access blocks, rate limits, and connection failures are not classified as 404s. Email links are listed separately and were not contacted.','',
           '| Result | All files | HTML document |','|---|---:|---:|']
    for kind,count in sorted(counts.items()):lines.append(f'| {kind} | {count} | {report["html_counts"].get(kind,0)} |')
    lines+=['','## Links requiring attention','']
    issues=[r for r in rows if r['classification']!='HTTP success']
    if not issues:lines+=['None.','']
    for i,row in enumerate(issues,1):
        places=sorted({x['document'] for x in row['occurrences']})
        lines += [f'{i}. [{row["url"]}]({row["url"]}) — **{row["classification"]}** (HTTP {row["http_status"] or "unavailable"}).',
                  f'   Found in: {", ".join(places)}.']
        if row['final_url']!=row['url']:lines += [f'   Final destination: {row["final_url"]}']
        if row.get('error'):lines += ['   '+row['error'].replace('\n',' ')[:350]]
        lines+=['']
    lines += ['## Complete inventory','','| URL | HTTP | Result | Final destination |','|---|---:|---|---|']
    for row in rows:
        final='Same page' if urldefrag(row['url'])[0]==row['final_url'] else row['final_url']
        lines.append(f'| [{row["url"]}]({row["url"]}) | {row["http_status"] or "—"} | {row["classification"]} | {final} |')
    lines += ['','## Email links','','No email was sent. HTTP status checks do not apply.','']
    for url in sorted(non_http):lines += [f'- `{url}`']
    lines += ['','## Illustrative URLs','','These reserved example-domain URLs occur as literal examples in the translated text, not as resource links. They are preserved and excluded from broken-link totals.','']
    for url in sorted(examples):lines += [f'- `{url}`']
    (OUT/'LINK-CHECK.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:report[k] for k in ['unique_http_links','unique_http_pages','html_links','counts','html_counts']},ensure_ascii=False),flush=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--reuse',action='store_true',help='Reuse results checked within the last hour; check only new/stale pages.')
    args=parser.parse_args()
    urls,non_http,examples=inventory()
    pages=sorted({urldefrag(url)[0] for url in urls})
    cache=json.loads(CACHE.read_text()) if args.reuse and CACHE.exists() else {}
    results={}
    for url in pages:
        old=cache.get(url)
        if old and (dt.datetime.now(dt.timezone.utc)-dt.datetime.fromisoformat(old['checked_at'])).total_seconds()<3600:
            results[url]=old
    todo=[url for url in pages if url not in results]
    print(f'Checking {len(todo)} pages; reusing {len(results)} recent checks; {len(urls)} complete URLs.',flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures={executor.submit(check_url,url):url for url in todo}
        for future in concurrent.futures.as_completed(futures):
            url=futures[future];results[url]=future.result()
            CACHE.write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
            if len(results)%20==0 or results[url]['classification']!='HTTP success':
                print(f'{len(results)}/{len(pages)} {results[url]["classification"]}: {url}',flush=True)
    write_report(urls,non_http,examples,results)


if __name__=='__main__':main()
