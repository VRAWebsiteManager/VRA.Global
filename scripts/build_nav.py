#!/usr/bin/env python3
"""Write the shared header and footer into every page.

The site has no build step, so the nav was hand-copied into each file and drifted:
47 header variants and 10 footers, with 32 pages quietly missing six footer links.
This keeps one copy in nav/ and stamps it into every page, so the shipped HTML
stays fully static -- the links must be in the markup for crawlers, which rules
out writing the nav with JavaScript.

Three things legitimately differ per page and stay as parameters:
  {{A}}    anchor prefix: "" on the homepage, "/" elsewhere, so /#process works
           from a subpage and #process from the homepage.
  {{UTM}}  the Calendly utm_content, preserved from whatever the page already
           used so existing attribution is not broken.
  active   class="active" on the nav link pointing at the current page.

  python3 scripts/build_nav.py           # rewrite every page
  python3 scripts/build_nav.py --check   # exit 1 if any page has drifted
"""
import io, os, re, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEADER = io.open(os.path.join(ROOT, 'nav/header.html'), encoding='utf-8').read().rstrip('\n')
FOOTER = io.open(os.path.join(ROOT, 'nav/footer.html'), encoding='utf-8').read().rstrip('\n')

def pages():
    out = []
    for p in sorted(glob.glob('*.html') + glob.glob('insights/*.html') + glob.glob('watch/*.html')):
        s = io.open(p, encoding='utf-8').read()
        if '<header>' in s and '<footer>' in s:
            out.append(p)
    return out

GENERIC = {'insights', 'virtual', 'assistant', 'assistants', 'va', 'the', 'a',
           'for', 'with', 'and', 'to', 'your', 'in', 'of', 'watch'}

def utm_for(src, path):
    """The page's own Calendly tag, kept unless it names a different page.

    Two kinds of mismatch exist today. Deliberate shorthand ("how-to-hire" for
    /how-to-hire-a-virtual-assistant) is kept, because shortening the tag was a
    choice. A tag naming another page entirely is a copy-paste error that sends
    that page's consults to the wrong row -- every /watch/ page currently
    reports as one insights article -- so those are corrected to the slug.
    """
    slug = os.path.splitext(path)[0].replace('/', '-')
    expect = 'home' if slug == 'index' else slug
    head = re.search(r'<header>.*?</header>', src, re.S)
    m = re.search(r'utm_content=([^"&]+)', head.group(0)) if head else None
    if not m:
        return expect
    cur = m.group(1)
    if cur == expect:
        return cur
    distinctive = [t for t in cur.split('-') if t not in GENERIC]
    if distinctive and all(t in expect.split('-') for t in distinctive):
        return cur                      # a shorthand of this page's own name
    return expect                       # names a different page: corrected

def url_for(path):
    if path == 'index.html':
        return '/'
    return '/' + re.sub(r'\.html$', '', path)

def render(block, path, utm, mark_active=True):
    out = block.replace('{{UTM}}', utm)
    out = out.replace('{{A}}', '' if path == 'index.html' else '/')
    if not mark_active:
        return out
    url = url_for(path)
    # Mark the current page's own nav link, longest href first so that
    # /insights does not claim /insights/some-article.
    for href in sorted(set(re.findall(r'href="(/[^"#]*)"', out)), key=len, reverse=True):
        if href == url:
            out = out.replace('<a href="%s">' % href, '<a href="%s" class="active">' % href, 1)
            break
    return out

def main():
    check = '--check' in sys.argv
    os.chdir(ROOT)
    drifted, written = [], []
    for p in pages():
        s = io.open(p, encoding='utf-8').read()
        utm = utm_for(s, p)
        new = s
        new = re.sub(r'<header>.*?</header>', lambda m: render(HEADER, p, utm), new, count=1, flags=re.S)
        new = re.sub(r'<footer>.*?</footer>', lambda m: render(FOOTER, p, utm, mark_active=False), new, count=1, flags=re.S)
        if new != s:
            drifted.append(p)
            if not check:
                io.open(p, 'w', encoding='utf-8').write(new)
                written.append(p)
    if check:
        if drifted:
            print('Nav drift: %d page(s) differ from nav/header.html or nav/footer.html' % len(drifted))
            for p in drifted[:20]:
                print('   ' + p)
            print('Run: python3 scripts/build_nav.py')
            return 1
        print('Nav in sync across %d pages.' % len(pages()))
        return 0
    print('Rewrote %d of %d pages.' % (len(written), len(pages())))
    return 0

if __name__ == '__main__':
    sys.exit(main())
