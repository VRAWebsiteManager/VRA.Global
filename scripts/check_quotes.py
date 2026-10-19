#!/usr/bin/env python3
"""Check every client quote on the site against the video transcript it came from.

The rule (Kami, 2026-10-19): an excerpt may choose where to start and stop, but
may not change anything in between.

  1. Contiguous   - one unbroken run of a single speaker turn, never two passages joined.
  2. Whole sentences - begins at a sentence start and ends at a sentence end.
  3. No substitution - not a word altered inside the run, contractions included.
  4. No ellipsis  - unnecessary once 1 and 2 hold.

A quote PASSES when it is a run of consecutive whole sentences from one speaker's
turn in one transcript. Pass/fail does not depend on the attribution next to it;
the attribution is checked separately, so a quote credited to the wrong person is
reported too.

Run from the repo root:  python3 scripts/check_quotes.py
Exit code 1 if anything fails, so it can gate a commit.
"""
import io, re, html, os, glob, sys, difflib

def soft(s):
    """Readable text: entities resolved, typographic marks normalised."""
    s = html.unescape(s)
    for a, b in [('’', "'"), ('‘', "'"), ('“', '"'), ('”', '"'),
                 ('—', ' - '), ('–', ' - '), (' ', ' ')]:
        s = s.replace(a, b)
    return re.sub(r'\s+', ' ', s).strip()

def key(s):
    """Comparison form. Keeps word boundaries, so "she is" != "she's"."""
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]+', ' ', soft(s).lower())).strip()

def sentences(text):
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return [p.strip() for p in parts if p.strip()]

# ---------------------------------------------------------------- transcripts
def load_transcripts():
    out = {}
    for f in sorted(glob.glob('watch/*.html')):
        raw = io.open(f, encoding='utf-8').read()
        turns = []
        for m in re.finditer(r'<div class="tline"><span class="tspk">(.*?)</span><p>(.*?)</p></div>', raw, re.S):
            spk = soft(re.sub(r'<[^>]+>', '', m.group(1)))
            txt = soft(re.sub(r'<[^>]+>', '', m.group(2)))
            turns.append((spk, txt))
        if turns:
            out[os.path.basename(f)[:-5]] = turns
    return out

def faithful_runs(turns):
    """Every legal excerpt: each consecutive run of whole sentences in a turn."""
    runs = {}
    for spk, txt in turns:
        sents = sentences(txt)
        for i in range(len(sents)):
            for j in range(i + 1, len(sents) + 1):
                runs.setdefault(key(' '.join(sents[i:j])), (spk, ' '.join(sents[i:j])))
    return runs

# --------------------------------------------------------------- site quotes
QUOTE_PATS = [
    r'&ldquo;(.{40,900}?)&rdquo;',
    r'<q>(.{40,900}?)</q>',
    r'class="milestone-quote">"(.{40,900}?)"</div>',
]
JUNK = re.compile(r'src=|viewbox|https?:|<div|<span|class=', re.I)

def site_quotes():
    seen, out = set(), []
    for f in sorted(glob.glob('*.html') + glob.glob('insights/*.html')):
        raw = io.open(f, encoding='utf-8').read()
        raw = re.sub(r'<script type="application/ld\+json">.*?</script>', ' ', raw, flags=re.S)
        for pat in QUOTE_PATS:
            for m in re.finditer(pat, raw, re.S):
                body = m.group(1)
                if JUNK.search(body):
                    continue
                q = soft(re.sub(r'<[^>]+>', '', body))
                if len(q.split()) < 8:
                    continue
                attr = soft(re.sub(r'<[^>]+>', ' ', raw[m.end():m.end() + 260]))
                if (f, key(q)) in seen:
                    continue
                seen.add((f, key(q)))
                out.append((f, q, attr))
    return out

def main():
    transcripts = load_transcripts()
    runs = {}                     # key -> (slug, speaker, text)
    for slug, turns in transcripts.items():
        for k, (spk, txt) in faithful_runs(turns).items():
            runs.setdefault(k, (slug, spk, txt))

    # Michael interviews in every video, so his name sits beside every quote.
    # He is never the client being quoted; excluding him stops VRA's own
    # narration being checked as if it were a testimonial.
    INTERVIEWERS = {'michael bossart'}
    speakers = sorted({spk for t in transcripts.values() for spk, _ in t
                       if spk.strip().lower() not in INTERVIEWERS})
    quotes = site_quotes()

    # Only judge quotes that belong to a video speaker; written reviews have no transcript.
    def credited(attr):
        hits = [s for s in speakers if all(w.lower() in attr.lower() for w in s.split() if len(w) > 2)]
        return hits[0] if len(hits) == 1 else None

    passed, failed, skipped = [], [], 0
    for f, q, attr in quotes:
        who = credited(attr)
        hit = runs.get(key(q))
        if hit:
            slug, spk, _ = hit
            if who and who.lower() != spk.lower():
                failed.append((f, q, 'credited to %s but spoken by %s' % (who, spk), ''))
            else:
                passed.append((f, q))
            continue
        if not who:
            skipped += 1          # no named video speaker: treat as a written review
            continue
        best, ratio = '', 0.0
        for k, (slug, spk, txt) in runs.items():
            if spk.lower() != who.lower():
                continue
            r = difflib.SequenceMatcher(None, key(q), k).ratio()
            if r > ratio:
                ratio, best = r, txt
        failed.append((f, q, 'not a whole-sentence run of %s\'s transcript (closest %.0f%%)' % (who, ratio * 100), best))

    print('Transcripts loaded:        %d' % len(transcripts))
    print('Quotes checked:            %d' % (len(passed) + len(failed)))
    print('Faithful excerpts:         %d' % len(passed))
    print('Need recutting:            %d' % len(failed))
    print('Skipped (no video speaker): %d' % skipped)
    if failed:
        print()
        for f, q, why, best in failed:
            print('FAIL  %s' % f)
            print('      %s' % why)
            print('      ON PAGE:  %s' % q[:200])
            if best:
                print('      FAITHFUL: %s' % best[:200])
            print()
    return 1 if failed else 0

if __name__ == '__main__':
    sys.exit(main())
