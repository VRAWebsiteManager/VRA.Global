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
  nav      header and footer match nav/*.html once the three per-page
           parameters are applied.
  quotes   every client quote is a faithful excerpt of its video transcript.
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
}
BRITISH_RE = re.compile(r'\b(' + '|'.join(sorted(BRITISH, key=len, reverse=True)) + r')\b', re.I)

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
        for w in sorted({m.group(1).lower() for m in BRITISH_RE.finditer(visible_text(s))}):
            if (f, w) not in BRITISH_ALLOW:
                bad.append('%s: British spelling "%s" (use "%s")' % (f, w, BRITISH[w]))
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


def run(script, *args):
    r = subprocess.run([sys.executable, '-I', os.path.join('scripts', script)] + list(args),
                       capture_output=True, text=True, cwd=ROOT)
    return r.returncode, (r.stdout + r.stderr).strip()

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
    for label, script in (('NAV', 'build_nav.py'), ('QUOTES', 'check_quotes.py')):
        code, out = run(script, '--check') if script == 'build_nav.py' else run(script)
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
