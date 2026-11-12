#!/usr/bin/env python3
"""Every standing check for vra.global, in one place.

  python3 scripts/verify_site.py

Exits 1 if anything fails, so it can gate a commit. Checks:

  pages    one title, meta description, robots and canonical per page; one H1;
           title <=55 and description 140-155 measured AFTER entity decoding
           (a raw count reads "&mdash;" as seven characters and reports a
           compliant description as over-long); every JSON-LD block parses and
           contains no HTML entities, since a parser reads "&amp;" literally
           and the schema then disagrees with the visible text; balanced tags;
           US spelling in visible copy and JSON-LD.
  dates    no page's JSON-LD dateModified is older than the day the file was
           last edited. Search engines and answer engines read dateModified as
           freshness, so a stale one understates a page that has just changed.
  nav      header and footer match nav/*.html once the three per-page
           parameters are applied.
  quotes   every client quote is a faithful excerpt of its video transcript.
  identity nodes sharing an @id agree on name, description, url and logo; the
           Organization node carries what an answer engine needs to resolve it;
           noindex and sitemap.xml never disagree; every sitemapped URL has a
           page behind it; canonicals are self-referential; no two pages share
           a title or description; robots.txt lets the search and answer
           crawlers through.
"""
import io, json, re, subprocess, sys, os, glob, html as H

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENT = re.compile(r'&(?:amp|lt|gt|quot|apos|nbsp|mdash|ndash|rsquo|lsquo|ldquo|rdquo|hellip|#\d+|#x[0-9a-fA-F]+);')

# British spellings. The site is US English; "licence" and "programme" would slide
# past every other check here, and the title, mortgage and insurance pages lean
# hard on "license"/"licensed". Checked against visible copy and JSON-LD only --
# stylesheets and scripts are skipped so CSS class names like "grey-20" and
# third-party URLs cannot trip it.
BRITISH = {
    'programme': 'program', 'programmes': 'programs',
    'organisation': 'organization', 'organisations': 'organizations',
    'organise': 'organize', 'organised': 'organized', 'organising': 'organizing',
    'centre': 'center', 'centres': 'centers',
    'colour': 'color', 'colours': 'colors', 'behaviour': 'behavior',
    'favour': 'favor', 'favourite': 'favorite', 'honour': 'honor',
    'labour': 'labor', 'neighbour': 'neighbor', 'neighbours': 'neighbors', 'humour': 'humor',
    'realise': 'realize', 'realised': 'realized',
    'recognise': 'recognize', 'recognised': 'recognized',
    'apologise': 'apologize', 'specialise': 'specialize', 'specialised': 'specialized',
    'prioritise': 'prioritize', 'optimise': 'optimize', 'optimised': 'optimized',
    'summarise': 'summarize', 'customise': 'customize', 'personalise': 'personalize',
    'minimise': 'minimize', 'maximise': 'maximize', 'utilise': 'utilize',
    'analyse': 'analyze', 'analysed': 'analyzed', 'normalised': 'normalized',
    'licence': 'license', 'licences': 'licenses',
    'defence': 'defense', 'offence': 'offense', 'practise': 'practice',
    'catalogue': 'catalog', 'travelling': 'traveling', 'travelled': 'traveled',
    'cancelled': 'canceled', 'cancelling': 'canceling',
    'fulfil': 'fulfill', 'fulfilment': 'fulfillment',
    'enrolment': 'enrollment', 'instalment': 'installment',
    'cheque': 'check', 'sceptical': 'skeptical', 'judgement': 'judgment',
    # Idioms, not spellings. A British turn of phrase reads as foreign to a US
    # reader even when every word in it is spelled the American way, and no
    # spell check will ever flag one. "queue" is deliberately absent: the title
    # and insurance pages use "service queue" and "renewal queue" correctly.
    'straight away': 'right away', 'whilst': 'while', 'amongst': 'among',
    'fortnight': 'two weeks', 'at the weekend': 'on the weekend',
    'different to': 'different from', 'in hospital': 'in the hospital',
}
BRITISH_RE = re.compile(r'\b(' + '|'.join(sorted(BRITISH, key=len, reverse=True)) + r')\b', re.I)

# Phrases that take a word in the middle ("weighing us up"), so a flat list of
# alternatives cannot catch them.
BRITISH_PATTERNS = [
    (re.compile(r'\bweigh(?:s|ed|ing)?\s+(?:\w+\s+){0,2}up\b', re.I), 'comparing'),
]

# A client's own words are never edited to satisfy a copy rule, so if a quote ever
# carries a British spelling, add the exact (file, word) pair here rather than
# changing what they said.
BRITISH_ALLOW = set()

def visible_text(s):
    """Copy a reader or a parser sees: drops <style> and non-JSON-LD <script>."""
    s = re.sub(r'<style\b.*?</style>', ' ', s, flags=re.S | re.I)
    s = re.sub(r'<script(?![^>]*application/ld\+json)\b.*?</script>', ' ', s, flags=re.S | re.I)
    return H.unescape(re.sub(r'<[^>]*>', ' ', s))

def check_pages():
    bad = []
    files = [f for f in sorted(glob.glob('*.html') + glob.glob('insights/*.html') + glob.glob('watch/*.html'))
             if not os.path.basename(f).startswith('google')]
    for f in files:
        s = io.open(f, encoding='utf-8').read()
        for label, pat in (('title', r'<title>'), ('meta description', r'<meta name="description"'),
                           ('robots', r'<meta name="robots"'), ('canonical', r'rel="canonical"')):
            n = len(re.findall(pat, s))
            if n != 1:
                bad.append('%s: %d x %s (want 1)' % (f, n, label))
        m = re.search(r'<title>(.*?)</title>', s, re.S)
        if m and len(H.unescape(m.group(1)).strip()) > 55:
            bad.append('%s: title %d chars' % (f, len(H.unescape(m.group(1)).strip())))
        m = re.search(r'<meta name="description" content="(.*?)">', s, re.S)
        if m and not (140 <= len(H.unescape(m.group(1))) <= 155):
            bad.append('%s: description %d chars' % (f, len(H.unescape(m.group(1)))))
        n = len(re.findall(r'<h1[ >]', s))
        if n != 1:
            bad.append('%s: %d x h1' % (f, n))
        if 'yztj6w70mc' not in s:
            bad.append('%s: Clarity missing' % f)
        for i, b in enumerate(re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)):
            try:
                json.loads(b)
            except Exception as e:
                bad.append('%s: JSON-LD #%d does not parse (%s)' % (f, i + 1, e)); continue
            for e in sorted(set(ENT.findall(b))):
                bad.append('%s: JSON-LD #%d contains %s' % (f, i + 1, e))
        if s.count('<!--') != s.count('-->'):
            bad.append('%s: unbalanced comment markers' % f)
        if len(re.findall(r'<div[ >]', s)) != s.count('</div>'):
            bad.append('%s: div open/close mismatch' % f)
        vis = visible_text(s)
        for w in sorted({m.group(1).lower() for m in BRITISH_RE.finditer(vis)}):
            if (f, w) not in BRITISH_ALLOW:
                bad.append('%s: British usage "%s" (use "%s")' % (f, w, BRITISH[w]))
        for pat, suggestion in BRITISH_PATTERNS:
            for p in sorted({m.group(0).lower() for m in pat.finditer(vis)}):
                if (f, p) not in BRITISH_ALLOW:
                    bad.append('%s: British usage "%s" (use "%s")' % (f, p, suggestion))
    return len(files), bad

def check_plaintext():
    """llms.txt is read by AI crawlers but is not HTML, so check_pages never sees it."""
    bad = []
    for f in ('llms.txt',):
        if not os.path.exists(f):
            continue
        t = io.open(f, encoding='utf-8').read()
        for w in sorted({m.group(1).lower() for m in BRITISH_RE.finditer(t)}):
            bad.append('%s: British spelling "%s" (use "%s")' % (f, w, BRITISH[w]))
    return bad


def _nav_spans(text):
    """Line ranges of the stamped <header> and <footer> blocks, 1-indexed."""
    spans = []
    for tag in ('header', 'footer'):
        for m in re.finditer(r'<%s>.*?</%s>' % (tag, tag), text, re.S):
            spans.append((text.count('\n', 0, m.start()) + 1,
                          text.count('\n', 0, m.end()) + 1))
    return spans


def _nav_only(diff, text):
    """True if every hunk in `diff` falls inside a nav block of `text`."""
    hunks = re.findall(r'^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@', diff, re.M)
    spans = _nav_spans(text)
    if not hunks or not spans:
        return False
    inside = lambda n: any(a <= n <= b for a, b in spans)
    for start, count in hunks:
        start = int(start)
        count = 1 if count in ('', None) else int(count)
        if count == 0:                        # pure deletion: check the seam
            if not (inside(start) and inside(start + 1)):
                return False
        elif not all(inside(n) for n in range(start, start + count)):
            return False
    return True


def _git(*args):
    return subprocess.run(['git'] + list(args), capture_output=True,
                          text=True, cwd=ROOT).stdout


def _last_content_edit(path, dirty):
    """When this page's content last changed, ignoring nav stamps.

    build_nav.py writes nav/header.html and nav/footer.html into all 98 pages,
    so adding one footer link rewrites every page -- in the working tree and
    then in the commit. Neither is a content change, and bumping 48
    dateModified values to claim otherwise is the freshness inflation this
    check exists to catch. So walk back to the most recent edit that touched
    something outside the stamped blocks, and date the page from that.
    """
    if path in dirty:
        text = io.open(os.path.join(ROOT, path), encoding='utf-8').read()
        if not _nav_only(_git('diff', '-U0', '--', path), text):
            return subprocess.run(['date', '+%Y-%m-%d'],
                                  capture_output=True, text=True).stdout.strip()
    for line in _git('log', '--format=%H %cs', '--', path).splitlines():
        sha, date = line.split(None, 1)
        text = _git('show', '%s:%s' % (sha, path))
        if not text:
            return date.strip()               # added or renamed here
        if not _nav_only(_git('show', '-U0', '--format=', sha, '--', path), text):
            return date.strip()
    return None


def check_dates():
    """A page edited after the date its schema claims is a page search engines
    will treat as older than it is. Uncommitted edits count as today."""
    bad = []
    # one git pass: most recent commit date per file
    out = subprocess.run(['git', 'log', '--name-only', '--format=%x00%cs'],
                         capture_output=True, text=True, cwd=ROOT).stdout
    last = {}
    date = None
    for line in out.splitlines():
        if line.startswith('\x00'):
            date = line[1:].strip()
        elif line.strip() and date:
            last.setdefault(line.strip(), date)
    dirty = {l[3:].strip() for l in subprocess.run(['git', 'status', '--short'],
             capture_output=True, text=True, cwd=ROOT).stdout.splitlines()}
    today = subprocess.run(['date', '+%Y-%m-%d'], capture_output=True, text=True).stdout.strip()
    for f in sorted(glob.glob('*.html') + glob.glob('insights/*.html')):
        t = io.open(f, encoding='utf-8').read()
        claimed = re.findall(r'"dateModified"\s*:\s*"(\d{4}-\d{2}-\d{2})', t)
        if not claimed:
            continue
        edited = _last_content_edit(f, dirty)
        if not edited:
            continue
        for c in sorted(set(claimed)):
            if c < edited:
                bad.append('%s: dateModified %s but last edited %s' % (f, c, edited))
    return bad


def run(script, *args):
    r = subprocess.run([sys.executable, '-I', os.path.join('scripts', script)] + list(args),
                       capture_output=True, text=True, cwd=ROOT)
    return r.returncode, (r.stdout + r.stderr).strip()

SKIP_DIRS = ('_review', 'website-backup-', 'deploy-')
# Not pages: nav/ holds the templates build_nav.py stamps into real pages (served
# as bare fragments and noindexed in _headers), and the google*.html files are
# Search Console verification tokens that must stay reachable and unlisted.
NOT_PAGES = re.compile(r'^(nav/|google[0-9a-f]+(_\d+)?\.html$)')
SITE = 'https://vra.global'

def site_pages():
    """Every page Netlify actually publishes."""
    return [p for p in sorted(glob.glob('**/*.html', recursive=True))
            if not any(p.startswith(d) or ('/' + d) in p for d in SKIP_DIRS)
            and not NOT_PAGES.match(p)]

def clean_url(path):
    p = path[:-5] if path.endswith('.html') else path
    return SITE + '/' if p == 'index' else SITE + '/' + p

def ld_nodes(src):
    for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', src, re.S):
        try:
            j = json.loads(b)
        except Exception:
            continue
        g = j.get('@graph') if isinstance(j, dict) and j.get('@graph') else (j if isinstance(j, list) else [j])
        for n in g:
            if isinstance(n, dict):
                yield n

def check_identity():
    """The checks that would have caught what actually went wrong on this site.

    Two Organization nodes once shared @id https://vra.global/#organization while
    giving different descriptions, the vetting stat reached ten wordings, and a
    page can be sitemapped and noindexed at the same time without anything here
    noticing. An entity is only worth declaring if every page declares it the
    same way, so a disagreement is a build failure, not a style note."""
    bad = []
    pages = site_pages()

    # 1. nodes sharing an @id must agree on the fields that define the entity
    byid = {}
    for p in pages:
        src = io.open(p, encoding='utf-8').read()
        for n in ld_nodes(src):
            nid = n.get('@id')
            if not nid:
                continue
            for field in ('name', 'description', 'url', 'logo'):
                if field not in n:
                    continue
                val = json.dumps(n[field], sort_keys=True)
                byid.setdefault((nid, field), {}).setdefault(val, []).append(p)
    for (nid, field), variants in sorted(byid.items()):
        if len(variants) > 1:
            where = '; '.join('%s in %s' % (v[:40].replace('\n', ' '), ', '.join(f[:28] for f in files[:2]))
                              for v, files in list(variants.items())[:3])
            bad.append('%s disagrees on "%s" across %d spellings: %s' % (nid, field, len(variants), where))

    # 2. the Organization node carries what an answer engine needs to resolve it
    org_required = ('name', 'alternateName', 'url', 'logo', 'description', 'sameAs')
    seen_org = False
    for p in ('index.html',):
        src = io.open(p, encoding='utf-8').read()
        for n in ld_nodes(src):
            if n.get('@id', '').endswith('#organization'):
                seen_org = True
                missing = [k for k in org_required if not n.get(k)]
                if missing:
                    bad.append('%s: Organization node missing %s' % (p, ', '.join(missing)))
    if not seen_org:
        bad.append('index.html: no Organization node with an #organization @id')

    # 3. noindex and the sitemap must not disagree
    sm = io.open('sitemap.xml', encoding='utf-8').read() if os.path.exists('sitemap.xml') else ''
    sitemapped = set(re.findall(r'<loc>([^<]+)</loc>', sm))
    for p in pages:
        src = io.open(p, encoding='utf-8').read()
        m = re.search(r'<meta name="robots" content="([^"]*)"', src)
        noindex = bool(m and 'noindex' in m.group(1).lower())
        url = clean_url(p)
        if noindex and url in sitemapped:
            bad.append('%s: noindex but listed in sitemap.xml' % p)
        if not noindex and url not in sitemapped and p != 'site-map.html':
            bad.append('%s: indexable but missing from sitemap.xml (%s)' % (p, url))

    # 4. every sitemap URL has a file behind it
    have = {clean_url(p) for p in pages}
    for url in sorted(sitemapped - have):
        bad.append('sitemap.xml lists %s with no page behind it' % url)

    # 5. canonical points at the page's own clean URL
    for p in pages:
        src = io.open(p, encoding='utf-8').read()
        m = re.search(r'<link rel="canonical" href="([^"]*)"', src)
        if m and m.group(1).rstrip('/') != clean_url(p).rstrip('/'):
            bad.append('%s: canonical is %s, expected %s' % (p, m.group(1), clean_url(p)))

    # 6. titles and descriptions are unique. Two pages with one description are
    #    two pages competing to be the same answer.
    for label, pat in (('title', r'<title>(.*?)</title>'),
                       ('description', r'<meta name="description" content="(.*?)">')):
        seen = {}
        for p in pages:
            src = io.open(p, encoding='utf-8').read()
            m = re.search(pat, src, re.S)
            if m:
                seen.setdefault(H.unescape(m.group(1)).strip(), []).append(p)
        for val, files in sorted(seen.items()):
            if len(files) > 1:
                bad.append('%d pages share one %s (%s): %s'
                           % (len(files), label, val[:48], ', '.join(files[:4])))

    # 7. robots.txt lets the crawlers that matter through
    if not os.path.exists('robots.txt'):
        bad.append('robots.txt is missing')
    else:
        rb = io.open('robots.txt', encoding='utf-8').read()
        if 'Sitemap:' not in rb:
            bad.append('robots.txt has no Sitemap: directive')
        group = None
        for line in rb.splitlines():
            line = line.strip()
            if line.lower().startswith('user-agent:'):
                group = line.split(':', 1)[1].strip().lower()
            elif line.lower().startswith('disallow:') and group is not None:
                rule = line.split(':', 1)[1].strip()
                if rule == '/':
                    bad.append('robots.txt blocks the whole site for "%s"' % group)
        for bot in ('oai-searchbot', 'gptbot', 'chatgpt-user', 'googlebot', 'bingbot'):
            m = re.search(r'user-agent:\s*' + bot + r'\b(.*?)(?=user-agent:|\Z)', rb, re.S | re.I)
            if m and re.search(r'disallow:\s*/\s*$', m.group(1), re.M | re.I):
                bad.append('robots.txt disallows %s' % bot)
    return bad


def main():
    os.chdir(ROOT)
    fails = 0
    n, bad = check_pages()
    print('PAGES   %s (%d pages)' % ('ok' if not bad else '%d problem(s)' % len(bad), n))
    for b in bad[:30]:
        print('        ' + b)
    fails += bool(bad)
    pbad = check_plaintext()
    print('TEXT    %s' % ('ok - llms.txt' if not pbad else '%d problem(s)' % len(pbad)))
    for b in pbad[:10]:
        print('        ' + b)
    fails += bool(pbad)
    dbad = check_dates()
    print('DATES   %s' % ('ok - schema dates match last edit'
                          if not dbad else '%d stale' % len(dbad)))
    for b in dbad[:15]:
        print('        ' + b)
    fails += bool(dbad)
    ibad = check_identity()
    print('IDENTITY %s' % ('ok - one entity, unique pages, crawlers allowed'
                           if not ibad else '%d problem(s)' % len(ibad)))
    for b in ibad[:25]:
        print('        ' + b)
    fails += bool(ibad)
    for label, script in (('NAV', 'build_nav.py'), ('REVIEWS', 'build_reviews.py'),
                          ('QUOTES', 'check_quotes.py')):
        code, out = run(script) if script == 'check_quotes.py' else run(script, '--check')
        head = out.splitlines()[0] if out else ''
        print('%-7s %s' % (label, 'ok - ' + head if code == 0 else 'FAILED'))
        if code:
            for l in out.splitlines()[:20]:
                print('        ' + l)
        fails += bool(code)
    print()
    print('ALL CHECKS PASS' if not fails else '%d CHECK GROUP(S) FAILED' % fails)
    return 1 if fails else 0

if __name__ == '__main__':
    sys.exit(main())
