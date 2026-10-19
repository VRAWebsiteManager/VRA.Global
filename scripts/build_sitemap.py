#!/usr/bin/env python3
"""Build /site-map from nav/pages.json, and check it against sitemap.xml.

One grouped list drives the human site map. sitemap.xml is not regenerated --
it carries per-URL lastmod, changefreq and priority that are worth keeping --
so instead the two are cross-checked and any disagreement is reported.

  python3 scripts/build_sitemap.py          # write site-map.html
  python3 scripts/build_sitemap.py --check  # exit 1 if the two disagree
"""
import io, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load():
    os.chdir(ROOT)
    data = json.load(io.open('nav/pages.json', encoding='utf-8'))
    locs = set(re.findall(r'<loc>https://vra\.global/([^<]*)</loc>',
                          io.open('sitemap.xml', encoding='utf-8').read()))
    return data, locs

def listed(data):
    out = set()
    for g in data:
        for p in g['pages']:
            if p['path'].startswith('/'):
                out.add(p['path'].lstrip('/'))
    return out

def check():
    data, locs = load()
    mine = listed(data)
    noindex = {'kw-multi-center-brief', 'title-va-brief'}   # deliberately out of sitemap.xml
    only_map = sorted(mine - locs - noindex)
    only_xml = sorted(locs - mine)
    if only_map or only_xml:
        print('site-map and sitemap.xml disagree')
        for s in only_map: print('   in nav/pages.json, not in sitemap.xml: /%s' % s)
        for s in only_xml: print('   in sitemap.xml, not in nav/pages.json: /%s' % s)
        return 1
    print('Site map and sitemap.xml agree on %d URLs.' % len(mine))
    return 0

def build():
    data, _ = load()
    rows = []
    for g in data:
        anchor = re.sub(r'[^a-z0-9]+', '-', g['group'].lower()).strip('-')
        rows.append('      <div class="sitemap-group" id="%s">\n        <h2>%s</h2>\n        <ul>' % (anchor, g['group']))
        for p in g['pages']:
            ext = ' target="_blank" rel="noopener"' if p['path'].startswith('http') else ''
            rows.append('          <li><a href="%s"%s>%s</a></li>' % (p['path'], ext, p['title']))
        rows.append('        </ul>\n      </div>')
    body = '\n'.join(rows)
    page = io.open('site-map.html', encoding='utf-8').read()
    new = re.sub(r'(<div class="sitemap-grid">\n).*?(\n    </div>)',
                 lambda m: m.group(1) + body + m.group(2), page, count=1, flags=re.S)
    io.open('site-map.html', 'w', encoding='utf-8').write(new)
    print('site-map.html: %d groups, %d links' % (len(data), sum(len(g['pages']) for g in data)))
    return 0

if __name__ == '__main__':
    sys.exit(check() if '--check' in sys.argv else build())
