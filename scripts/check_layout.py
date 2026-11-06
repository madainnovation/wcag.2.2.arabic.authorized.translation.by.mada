"""Inspect winning CSS declarations without pretending to render a browser page.

This checks the default light/screen state and print rules. It deliberately does
not claim pixel-layout, font-shaping, scrolling, or visual conformance testing.
"""
import json
import re
from pathlib import Path
import cssselect2
import html5lib
import tinycss2
from common import ROOT, soup


def media_matches(query, width, medium):
    for alternative in query.split(','):
        part=alternative.strip().lower()
        if part.startswith('not print'):
            if medium=='print':continue
            part=part[len('not print'):]
        elif part.startswith('print'):
            if medium!='print':continue
            part=part[len('print'):]
        elif part.startswith('screen'):
            if medium!='screen':continue
            part=part[len('screen'):]
        elif part.startswith('all'):
            part=part[len('all'):]
        if re.search(r'prefers-(color-scheme|reduced-motion)',part):continue
        conditions=re.findall(r'\((min|max)-width:\s*([\d.]+)(em|px)\)',part)
        remaining=re.sub(r'\((min|max)-width:\s*([\d.]+)(em|px)\)','',part).replace('and','').strip()
        if remaining:continue
        if all((width>=float(n)*(16 if unit=='em' else 1)) if bound=='min' else
               (width<=float(n)*(16 if unit=='em' else 1)) for bound,n,unit in conditions):
            return True
    return False


class Cascade:
    def __init__(self,path,width,medium='screen'):
        self.path,self.width,self.medium=path,width,medium
        self.dom=soup(path.read_text())
        self.root=cssselect2.ElementWrapper.from_html_root(html5lib.parse(path.read_text(),namespaceHTMLElements=False))
        self.matcher=cssselect2.Matcher()
        self.order=0
        self.selector_errors=[]
        for node in self.dom.head.select('style,link[rel="stylesheet"]'):
            if node.name=='style':
                self.rules(tinycss2.parse_stylesheet(node.get_text(),skip_comments=True,skip_whitespace=True),path.parent)
            else:
                if path.parent.name=='references':
                    name='guidelines.css' if node['href']=='guidelines.css' else 'w3c-rec.css'
                    css=path.parent/'template-assets'/name
                else:css=path.parent/node['href']
                self.stylesheet(css)

    def stylesheet(self,path):
        self.rules(tinycss2.parse_stylesheet(path.read_text(),skip_comments=True,skip_whitespace=True),path.parent)

    def rules(self,rules,base):
        for rule in rules:
            if rule.type=='at-rule':
                condition=tinycss2.serialize(rule.prelude).strip()
                if rule.lower_at_keyword=='import':
                    self.stylesheet(base/condition.strip('"\''))
                elif rule.lower_at_keyword=='media' and media_matches(condition,self.width,self.medium):
                    self.rules(tinycss2.parse_rule_list(rule.content,skip_comments=True,skip_whitespace=True),base)
                elif rule.lower_at_keyword=='supports' and not condition.startswith('not '):
                    # Positive feature queries use the modern-CSS branch.
                    self.rules(tinycss2.parse_rule_list(rule.content,skip_comments=True,skip_whitespace=True),base)
                continue
            if rule.type!='qualified-rule':continue
            selector=tinycss2.serialize(rule.prelude)
            try:selectors=cssselect2.compile_selector_list(selector)
            except cssselect2.SelectorError as error:
                self.selector_errors.append({'selector':selector,'error':str(error)})
                continue
            declarations=[]
            for item in tinycss2.parse_declaration_list(rule.content,skip_comments=True,skip_whitespace=True):
                if item.type=='declaration':
                    self.order+=1
                    name=item.lower_name
                    value=tinycss2.serialize(item.value).strip()
                    declarations.append((name,value,item.important,self.order))
                    # Account for later shorthands resetting earlier longhands.
                    # Tokenization preserves calc(...) values containing spaces.
                    parts=[tinycss2.serialize([token]).strip() for token in item.value
                           if token.type not in ['whitespace','comment']]
                    if name in ['margin','padding','inset'] and 1<=len(parts)<=4:
                        top=parts[0];right=parts[1] if len(parts)>1 else top
                        bottom=parts[2] if len(parts)>2 else top
                        left=parts[3] if len(parts)>3 else right
                        for side,v in zip(['top','right','bottom','left'],[top,right,bottom,left]):
                            prop=side if name=='inset' else name+'-'+side
                            declarations.append((prop,v,item.important,self.order))
                    elif name=='overflow' and 1<=len(parts)<=2:
                        for axis,v in [('x',parts[0]),('y',parts[-1])]:
                            declarations.append(('overflow-'+axis,v,item.important,self.order))
            for compiled in selectors:
                self.matcher.add_selector(compiled,(selector,declarations))

    def values(self,selector):
        element=self.root.query(selector) if isinstance(selector,str) else selector
        if element is None:raise ValueError('Missing element: '+selector)
        winners={}
        for specificity,_,pseudo,(matched,declarations) in self.matcher.match(element):
            if pseudo is not None:continue
            for name,value,important,order in declarations:
                priority=(important,specificity,order)
                if name not in winners or priority>winners[name][0]:
                    winners[name]=(priority,value,matched)
        return {name:{'value':value,'selector':matched} for name,(_,value,matched) in winners.items()}


def main():
    checks=[];scenarios=[]
    def check(name,condition):checks.append({'check':name,'passed':bool(condition)})
    for width in [320,390,768,1159,1248,1440,1920]:
        ar=Cascade(ROOT/'wcag22-ar/index.html',width)
        en=Cascade(ROOT/'references/wcag22-en.html',width)
        def value(cascade,selector,property):return cascade.values(selector).get(property,{}).get('value')
        check(f'{width}: source and Arabic body line height are 1.5',
              value(ar,'body','line-height')==value(en,'body','line-height')=='1.5')
        check(f'{width}: source and Arabic content columns are 50em',
              value(ar,'#document-content','max-width')==value(en,'body','max-width')=='50em')
        check(f'{width}: RTL scroll region fills the viewport without clipping content',
              all(value(ar,'#document-scroll',prop)==expected for prop,expected in
                  {'direction':'rtl','width':'100%','height':'100%',
                   'overflow-x':'auto','overflow-y':'auto'}.items()))
        check(f'{width}: outer page leaves scrolling to the document region',
              value(ar,'html','height')=='100%' and value(ar,'html','overflow')=='hidden' and
              all(value(ar,'body',prop)==expected for prop,expected in
                  {'height':'100%','width':'100%','max-width':'none','margin':'0',
                   'padding-left':'0','padding-right':'0','overflow':'hidden'}.items()))
        check(f'{width}: body and help links use the reader-scalable 1rem size',
              value(ar,'body','font-size')==value(ar,'.doclinks','font-size')=='1rem')
        check(f'{width}: every contents level has a 1rem text size',all(
              value(ar,node,'font-size')=='1rem' for node in ar.root.query_all('#toc .toc li')))
        check(f'{width}: copyright and small text have a 1rem text size',all(
              value(ar,node,'font-size')=='1rem' for node in ar.root.query_all('p.copyright,small')))
        check(f'{width}: technical identifiers inherit the surrounding text size',all(
              value(ar,node,'font-size')=='1em' for node in ar.root.query_all('pre,code,kbd,samp')))
        check(f'{width}: help boxes include padding within their width and wrap on narrow screens',
              value(ar,'.doclinks','box-sizing')=='border-box' and
              value(ar,'.doclinks','width')==('auto' if width<=640 else '30%') and
              value(ar,'.doclinks','float')==('none' if width<=640 else 'left'))
        check(f'{width}: paragraph spacing inherits the source 1em rhythm',
              value(ar,'#non-text-content > p:not(.conformance-level)','margin')==value(en,'#non-text-content > p:not(.conformance-level)','margin')=='1em 0')
        check(f'{width}: section-heading top margin stays 3rem',
              value(ar,'#non-text-content h4','margin-top')==value(en,'#non-text-content h4','margin-top')=='3rem')
        check(f'{width}: Arabic heading leading is 1.3',value(ar,'#non-text-content h4','line-height')=='1.3')
        check(f'{width}: notes retain the source half-em padding',
              value(ar,'#orientation .note','padding')==value(en,'#orientation .note','padding')=='.5em')
        check(f'{width}: exception labels retain the source normal flow',
              value(ar,'#non-text-content dt','float')==value(en,'#non-text-content dt','float') and
              value(ar,'#non-text-content dt','float') in [None,'none'])
        check(f'{width}: W3C logo float is mirrored',
              value(ar,'.head p.logos > a','float')=='left' and value(en,'.head p.logos > a','float')=='right')
        check(f'{width}: hidden separators do not have a negative left offset',
              value(ar,'.screenreader','inset')=='auto' and value(ar,'.screenreader','clip-path')=='inset(50%)')
        check(f'{width}: heading and permalink offsets are inactive',
              value(ar,'#non-text-content h4','position')=='static' and value(ar,'#non-text-content .self-link','position')=='static')
        check(f'{width}: contents numbers have no float or negative margins',
              value(ar,'#toc .secno','float')=='none' and value(ar,'#toc .secno','margin')=='0')
        ribbon=ar.values('#translation-ribbon')
        check(f'{width}: blue strip is fixed to the right with source dimensions',all(
            ribbon.get(k,{}).get('value')==v for k,v in {'position':'fixed','right':'0','left':'auto','width':'25px','height':'380px'}.items()))
        check(f'{width}: strip clips only its own rotated label',ribbon.get('overflow',{}).get('value')=='hidden' and
              value(ar,'#document-scroll','overflow-x')=='auto' and
              value(ar,'#document-content','overflow-x') not in ['hidden','clip'])
        if width>=1248:
            check(f'{width}: right sidebar and content column reserve the source spacing',
                  value(ar,'#toc','right')=='0' and value(ar,'#toc','left')=='auto' and
                  value(ar,'#document-content','padding-right')=='29em' and value(ar,'#toc','padding')=='0 calc(1em + 26px) 1em 1em')
        else:
            expected='1em calc(26px + 1em) 4em 1em' if width<=640 else '1.6em calc(26px + 1.5em) 4em 1.5em'
            check(f'{width}: inline layout reserves the right ribbon gutter',value(ar,'#document-content','padding')==expected)
        scenarios.append({'viewport_width':width,'arabic_body':{k:v for k,v in ar.values('body').items() if k in ['line-height','max-width','padding','padding-left','padding-right','box-sizing']},
                          'arabic_content':ar.values('#document-content'),
                          'arabic_scroll_region':ar.values('#document-scroll'),
                          'selector_errors':ar.selector_errors+en.selector_errors})
    printed=Cascade(ROOT/'wcag22-ar/index.html',800,'print')
    check('Print: decorative strip is hidden',printed.values('#translation-ribbon').get('display',{}).get('value')=='none')
    check('Print: body padding is zero',printed.values('body').get('padding',{}).get('value')=='0')
    check('Print: content padding is zero',printed.values('#document-content').get('padding',{}).get('value')=='0')
    check('Print: all document containers allow the full document to print',all(
          printed.values(selector).get(prop,{}).get('value')==expected
          for selector in ['html','body','#document-scroll']
          for prop,expected in [('height','auto'),('overflow-x','visible'),('overflow-y','visible')]))
    report={'passed':all(x['passed'] for x in checks),'checks_run':len(checks),'checks':checks,'scenarios':scenarios,
            'method':'Static selector/cascade inspection using 16px initial em/rem, default light mode, and the modern positive @supports branch. Not browser-computed styles.',
            'visual_review':'Unavailable: local browser use is disabled in Work settings. No browser layout, overflow measurement, font shaping, or screenshot verification was performed.'}
    (ROOT/'reports/layout-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    for item in checks:
        if not item['passed']:print('FAIL:',item['check'])
    print(f'{"PASS" if report["passed"] else "FAIL"}: {len(checks)} static CSS checks across seven screen widths and print. Browser rendering remains unverified.')
    if not report['passed']:raise SystemExit(1)


if __name__=='__main__':main()
