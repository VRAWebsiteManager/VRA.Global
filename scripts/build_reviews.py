#!/usr/bin/env python3
"""Write each page's opening review into its markup.

js/reviews.js rotates one client review at a time on the lead-capture pages.
It shipped an empty <q></q> and filled it on load, so the quote existed only
after JavaScript ran -- invisible to crawlers and to the AI assistants that
are now citing this site. The rotation is worth keeping; the silence before
it starts is not.

So the review a page opens on (its data-start index) is stamped into the
markup here, and the script repaints the same index on load and carries on
rotating. Nothing a visitor sees changes.

Hand-stamping would drift the moment someone edits reviews.js, which is what
build_nav.py exists to prevent, so this reads the list from the script itself.

  python3 scripts/build_reviews.py           # rewrite every page
  python3 scripts/build_reviews.py --check   # exit 1 if any page has drifted
"""
import io, os, re, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STARS = '&#9733;&#9733;&#9733;&#9733;&#9733;'

def reviews():
    src = io.open(os.path.join(ROOT, 'js/reviews.js'), encoding='utf-8').read()
    body = src.split('var REVIEWS = [', 1)[1].split('\n  ];', 1)[0]
    out = []
    for m in re.finditer(r'\{\s*quote:\s*"((?:[^"\\]|\\.)*)"\s*,\s*by:\s*"((?:[^"\\]|\\.)*)"\s*\}', body, re.S):
        out.append((m.group(1).replace('\\"', '"'), m.group(2).replace('\\"', '"')))
    return out

SPOT = re.compile(
    r'(<div class="review-spot" id="reviewSpotlight"[^>]*?>\s*'
    r'<div class="review-stage">\s*)'
    r'<span class="stars">.*?</span>\s*<q>.*?</q>\s*<span class="by">.*?</span>',
    re.S)

def render(src, path, items):
    m = re.search(r'id="reviewSpotlight"[^>]*data-start="(\d+)"', src)
    i = int(m.group(1)) if m else None
    if i is None or i >= len(items):
        return src, None
    quote, by = items[i]
    filled = ('<span class="stars">%s</span>\n        <q>%s</q>\n'
              '        <span class="by">%s</span>' % (STARS, quote, by))
    new = SPOT.sub(lambda mm: mm.group(1) + filled, src, count=1)
    # content ships now, so the element must not start hidden
    new = re.sub(r'(<div class="review-spot" id="reviewSpotlight"[^>]*?)\s+hidden', r'\1', new)
    return new, by

def main():
    check = '--check' in sys.argv
    items = reviews()
    drifted, done = [], 0
    for p in sorted(glob.glob('*.html')):
        src = io.open(p, encoding='utf-8').read()
        if 'id="reviewSpotlight"' not in src:
            continue
        new, by = render(src, p, items)
        if by is None:
            drifted.append('%s: data-start missing or out of range' % p)
            continue
        if new != src:
            if check:
                drifted.append('%s: opening review not in the markup' % p)
            else:
                io.open(p, 'w', encoding='utf-8').write(new)
        done += 1
    if check and drifted:
        print('\n'.join(drifted)); return 1
    print('%s %d page(s) against %d reviews.' %
          ('Checked' if check else 'Stamped', done, len(items)))
    return 0

if __name__ == '__main__':
    sys.exit(main())
