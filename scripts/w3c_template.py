"""Apply translated content to the actual W3C WCAG 2.2 HTML template."""
import copy
import html
import json
import re
from common import ROOT, soup, heading, text, glossary_entry


def replace_contents(target, fragment):
    target.clear()
    for node in list(soup(fragment).contents):
        target.append(node)


def render_template(english, arabic, titles):
    page = copy.deepcopy(english)
    page.html['lang'] = 'ar'
    page.html['xml:lang'] = 'ar'
    page.html['dir'] = 'rtl'
    page.body['id'] = 'wcag22-ar'
    page.body['class'] = page.body.get('class', []) + ['translation-document']
    page.title.string = 'مبادئ النفاذ إلى محتوى الويب (WCAG) 2.2 — مسودة ترجمة عربية'
    # Generated English definition popovers and ReSpec configuration refer to
    # the source text. Static definition links work without those scripts.
    for tag in page.select('script,.dfn-panel,link[rel="canonical"]'):
        tag.decompose()
    for link in page.select('link[rel="stylesheet"]'):
        link['href'] = 'assets/' + ('guidelines.css' if link['href']=='guidelines.css' else 'w3c-rec.css')
    page.head.append(page.new_tag('link', rel='stylesheet', href='assets/translation-rtl.css'))

    # Keep the source section elements, nested hierarchy, header wrappers,
    # heading IDs, permalink anchors and document-link boxes.
    for sec in page.select('section[id]'):
        ident = sec['id']
        translated = arabic.find('section', id=ident)
        if translated is None:
            raise ValueError('No translation for '+ident)
        info = titles[ident]
        sec['data-translation-status'] = translated['data-translation-status']
        h = heading(sec)
        number = h.select_one('.secno')
        raw_number = info['number']
        number_text = raw_number.translate(str.maketrans({'A':'أ','B':'ب','C':'ج'}))
        number_dir = 'rtl' if re.match(r'^[ABC]', raw_number) else 'ltr'
        label = 'معيار النجاح' if info['level'] or ident=='parsing' else 'توجيه' if number is not None and text(number).startswith('Guideline') else ''
        number_html = (f'<span class="section-label">{label}</span> ' if label else '')
        if number:
            number_html += f'<bdi class="secno" dir="{number_dir}">{html.escape(number_text)}</bdi> '
        replace_contents(h, number_html + f'<span class="section-title">{html.escape(info["ar"])}</span>')
        wrapper = h.parent if 'header-wrapper' in h.parent.get('class', []) else h
        for a in wrapper.select('a.self-link'):
            a['aria-label'] = 'رابط دائم إلى '+info['ar']
        children = [x.extract() for x in sec.find_all('section', recursive=False)]
        source_docs = sec.find('div', class_='doclinks', recursive=False)
        if source_docs:
            source_docs = source_docs.extract()
            for i, a in enumerate(source_docs.select('a')):
                a.string = ('فهم ' if i==0 else 'كيفية تلبية ') + info['ar'] + ' (بالإنجليزية)'
        for child in list(sec.children):
            if child is not wrapper:
                child.extract()
        if source_docs:
            sec.append(source_docs)
        for child in translated.find_all(recursive=False):
            if child.name == 'section' or re.fullmatch(r'h[2-6]', child.name or '') or 'doclinks' in child.get('class', []):
                continue
            item = copy.deepcopy(child)
            if 'new-label' in item.get('class', []):
                item['class'] = ['change']
            sec.append(item)
        for child in children:
            sec.append(child)

    # Translate the existing table of contents, preserving its list markup.
    page.find(id='table-of-contents').string = 'جدول المحتويات'
    page.find(id='toc')['aria-labelledby'] = 'table-of-contents'
    for a in page.select('#toc a.tocxref'):
        ident = a['href'][1:]
        num = a.select_one('.secno')
        number = titles[ident]['number'].translate(str.maketrans({'A':'أ','B':'ب','C':'ج'}))
        number_dir = 'rtl' if re.match(r'^[ABC]', titles[ident]['number']) else 'ltr'
        if num:
            a['class'] = a.get('class', []) + ['toc-with-number']
        replace_contents(a, (f'<bdi class="secno" dir="{number_dir}">{html.escape(number)}</bdi>' if num else '') + f'<span class="toc-title">{html.escape(titles[ident]["ar"])}</span>')

    # Retain the template's metadata, source-editor identities and copyright.
    head = page.select_one('div.head')
    replace_contents(head.h1, 'مبادئ النفاذ إلى محتوى الويب <bdi dir="ltr">(WCAG) 2.2</bdi>')
    state = head.find(id='w3c-state')
    replace_contents(state, '<span id="translation-status">مسودة الترجمة العربية</span> لـ <a href="https://www.w3.org/TR/2024/REC-WCAG22-20241212/">توصية W3C</a> الصادرة في <time datetime="2024-12-12">12 كانون الأول/ديسمبر 2024</time>')
    head.find('summary').string = 'المزيد من التفاصيل حول الوثيقة الإنجليزية الأصلية'
    labels = {
        'This version:': 'الإصدار الإنجليزي المترجَم:',
        'Latest published version:': 'أحدث إصدار إنجليزي منشور:',
        "Latest editor\'s draft:": 'أحدث مسودة للمحرر:',
        'History:': 'سجل الإصدارات:', 'Implementation report:': 'تقرير التنفيذ:',
        'Previous Recommendation:': 'التوصية السابقة:',
        'Editors:': 'محررو الأصل الإنجليزي:', 'Feedback:': 'التعليقات على الأصل الإنجليزي:',
        'Errata:': 'تصحيحات الأصل الإنجليزي:',
    }
    for dt in head.select('dt'):
        dt.string = labels[text(dt)]
    link_labels = {'Commit history':'سجل التغييرات', 'pull requests':'طلبات التعديل',
                   'new issue':'مسألة جديدة', 'open issues':'المسائل المفتوحة',
                   'Errata exists':'تتوفر تصحيحات'}
    for a in head.select('a'):
        if text(a) in link_labels:
            a.string = link_labels[text(a)]
    for p in head.find_all('p', recursive=False):
        if 'See also' in text(p):
            replace_contents(p, 'انظر أيضا <a href="https://www.w3.org/Translations/?technology=WCAG22"><strong>الترجمات</strong></a>.')
    for dd in head.select('dd.editor'):
        dd['lang'] = 'en'
        dd['dir'] = 'ltr'
    head.select_one('p.copyright')['lang'] = 'en'
    head.select_one('p.copyright')['dir'] = 'ltr'
    head.hr['title'] = 'فاصل نهاية الترويسة'
    head.img['src'] = 'assets/logos/W3C.svg'
    head.img.attrs.pop('crossorigin', None)

    contributors = soup((ROOT/'translation/contributors.html').read_text()).find(id='translation-contributors')
    if contributors is None:
        raise ValueError('Missing Arabic translation-contributor block')
    publication = json.loads((ROOT/'publication.json').read_text())
    for ident,key in [('translation-current-version','current_version_url'),
                      ('translation-latest-version','latest_version_url')]:
        contributors.find(id=ident)['href'] = publication[key]
    head.insert_before(contributors)
    credit_link = soup('<li class="tocline"><a class="tocxref" href="#translation-contributors"><span class="toc-title">المساهمون ومراجعة الترجمة العربية 2.2</span></a></li>').li
    page.select_one('#toc > ol.toc').insert(0, credit_link)
    back = page.find(id='back-to-top')
    back['aria-label'] = 'التنقل في الوثيقة'
    back.a['aria-label'] = 'العودة إلى الأعلى'
    back.abbr['title'] = 'العودة إلى الأعلى'
    skip = soup('<a class="skip-link" href="#intro">انتقل إلى المحتوى</a>').a
    page.body.insert(0, skip)
    ribbon = soup('<div id="translation-ribbon" aria-hidden="true"><span>WCAG 2.2 — مسودة ترجمة عربية</span></div>').div
    page.body.insert(1, ribbon)

    # Preserve the English template's new-definition treatment.
    for dfn in english.select('#glossary dfn'):
        en_dt, en_dd = glossary_entry(dfn)
        ar_dt, ar_dd = glossary_entry(page.find(id=dfn['id']))
        for en_node, ar_node in [(en_dt, ar_dt), (en_dd, ar_dd)]:
            if en_node.get('class'):
                ar_node['class'] = en_node['class']
        if en_dd.find('p', class_='change', recursive=False):
            ar_dd.insert(0, soup('<p class="change">جديد في WCAG 2.2</p>').p)

    # Rebuild note markers in the W3C style with Arabic labels and unique IDs.
    for index, note in enumerate(page.select('.note,.example'), start=1):
        kind = 'note' if 'note' in note.get('class', []) else 'example'
        if note.name == 'p':
            note.name = 'aside'
        for old in note.select('.note-label,.note-title,.example-title'):
            old.decompose()
        marker = page.new_tag('div', attrs={'class':[kind+'-title','marker'], 'id':f'ar-{kind}-{index}'})
        marker.string = 'ملاحظة' if kind=='note' else 'مثال'
        note.insert(0, marker)
        if kind=='note':
            note['role']='note'
    # Bibliography and technical identifiers retain their original language.
    for a in page.select('a[href^="#dfn-"]'):
        a['class'] = list(set(a.get('class', [])+['internalDFN']))
    for t in page.select('code,bdi[dir="ltr"]'):
        t['dir']='ltr'
    for a in head.select('a[href^="http"]'):
        if text(a).startswith('http'):
            a['dir']='ltr'

    # A full-width RTL element owns scrolling so its scrollbar is on the left.
    # The inner column retains the W3C spacing; fragment IDs and source order
    # stay intact. The named region can receive keyboard scrolling focus.
    scroller = page.new_tag('div', attrs={'id':'document-scroll', 'dir':'rtl',
                                        'tabindex':'0', 'role':'region',
                                        'aria-labelledby':'title'})
    content = page.new_tag('div', id='document-content')
    for node in list(page.body.contents):
        content.append(node.extract())
    scroller.append(content)
    page.body.append(scroller)
    return page
