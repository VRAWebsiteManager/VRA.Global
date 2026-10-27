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


def longest_run(a, b):
    """Longest run of consecutive words shared by two strings.

    A quote that drifted from a transcript still shares a long unbroken run with
    it; unrelated prose shares only a few words. That separates the two cleanly,
    where a similarity ratio does not -- any two English sentences of a similar
    length score around 0.5.
    """
    A, B = a.split(), b.split()
    if not A or not B:
        return 0
    prev = [0] * (len(B) + 1)
    best = 0
    for i in range(1, len(A) + 1):
        cur = [0] * (len(B) + 1)
        for j in range(1, len(B) + 1):
            if A[i - 1] == B[j - 1]:
                cur[j] = prev[j - 1] + 1
                if cur[j] > best:
                    best = cur[j]
        prev = cur
    return best

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
    # js/reviews.js holds the review carousel's lines as data rather
    # than markup. They are client words like any other, so they are checked
    # like any other -- the attribution sits on the next line, inside the
    # window the credit lookup already reads.
    r'quote:\s*"(.{40,900}?)",',
]
JUNK = re.compile(r'src=|viewbox|https?:|<div|<span|class=|&ldquo;|&rdquo;|“|”', re.I)

def site_quotes():
    seen, out = set(), []
    for f in sorted(glob.glob('*.html') + glob.glob('insights/*.html') + glob.glob('js/*.js')):
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
                after = soft(re.sub(r'<[^>]+>', ' ', raw[m.end():m.end() + 260]))
                before = soft(re.sub(r'<[^>]+>', ' ', raw[max(m.start() - 260, 0):m.start()]))
                if (f, key(q)) in seen:
                    continue
                seen.add((f, key(q)))
                out.append((f, q, before, after))
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
    def credited(before, after):
        """Who the page credits. Most pages name the speaker under the quote, but
        some articles name them above it, so both sides are searched and the
        nearer name wins."""
        def find(blob, from_end):
            best, pos = None, None
            for sp in speakers:
                ws = [w.lower() for w in sp.split() if len(w) > 2]
                if not ws or not all(w in blob.lower() for w in ws):
                    continue
                at = blob.lower().rindex(ws[0]) if from_end else blob.lower().index(ws[0])
                d = (len(blob) - at) if from_end else at
                if pos is None or d < pos:
                    best, pos = sp, d
            return best, (pos if pos is not None else 10**6)
        a, da = find(after, False)
        b, db = find(before, True)
        return a if da <= db else b

    # Attribution by proximity proved unreliable: some articles credit above the
    # quote, some below, and a written review often sits next to a video client's
    # name. So the source is decided by the text itself, not by who is named.
    #
    #   faithful excerpt of any transcript  -> pass
    #   clearly a mangled version of one    -> fail, with the faithful wording
    #   resembles no transcript             -> skip; it is a written review,
    #                                          live on Trustpilot or captured
    #                                          here before removal, and the
    #                                          capture is the source of truth.
    # Six consecutive words in common means it came from that transcript.
    MIN_RUN = 6

    passed, failed, skipped = [], [], 0
    for f, q, before, after in quotes:
        hit = runs.get(key(q))
        if hit:
            slug, spk, _ = hit
            who = credited(before, after)
            if who and who.lower() != spk.lower():
                failed.append((f, q, 'credited to %s but spoken by %s' % (who, spk), ''))
            else:
                passed.append((f, q))
            continue
        qk = key(q)
        best, run, owner = '', 0, None
        for k, (slug, spk, txt) in runs.items():
            n = longest_run(qk, k)
            if n > run:
                run, best, owner = n, txt, spk
        if run >= MIN_RUN:
            failed.append((f, q, "not a whole-sentence run of %s's transcript "
                           "(shares %d consecutive words with it)" % (owner, run), best))
        else:
            skipped += 1

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
