"""Diff pending_db_world's quest_template_locale against a wowhead-tw fetch.

Usage:
    python3 diff_quest_text.py [--strict]

Reads $ZHTW_SCRATCH/quest_text_extracted.jsonl (produced by fetch_quest_text.py)
and compares each row's title/objectives/details against the current
pending_db_world quest_template_locale text for the same ID.

Default mode does a plain strip+trim compare (matches the pilot-batch tool).
--strict additionally normalizes $N/$n/$C/$c/$R/$r case, drops $B breaks,
collapses whitespace, and strips punctuation (half/full-width, ellipsis
variants, quote styles) before comparing -- this filters out wowhead
rendering quirks (documented as a known false-positive class in
verification-progress.md) so only wording/content-level diffs remain.
Use --strict first to triage a large batch; fall back to default mode
if you need to see the raw diff including punctuation-only changes.
"""
import json, sys, os, re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scan_missing_zhtw import extract_inserts, unquote

TARGET = "/home/kelvinwu/github/azerothcore-wotlk/data/sql/updates/pending_db_world/rev_1783688290124463491.sql"
SCRATCH = os.environ.get("ZHTW_SCRATCH", "/tmp/zhtw-scratch")
JSONL = os.path.join(SCRATCH, "quest_text_extracted.jsonl")

STRICT = "--strict" in sys.argv

PUNCT_MAP = str.maketrans({
    '！': '!', '？': '?', '：': ':', '；': ';', '，': ',',
    '。': '.', '（': '(', '）': ')',
    '“': '"', '”': '"', '‘': "'", '’': "'",
    '「': '"', '」': '"', '『': '"', '』': '"',
    '、': ',', '．': '.', '－': '-', '—': '-', '─': '-', '～': '~',
})

def norm_loose(s):
    return re.sub(r'\$[Nn]\b', '$N', s.strip())

def norm_strict(s):
    s = s.strip()
    s = re.sub(r'\$[Nn]\b', '$N', s)
    s = re.sub(r'\$[Cc]\b', '$C', s)
    s = re.sub(r'\$[Rr]\b', '$R', s)
    s = s.replace('$B', ' ').replace('$b', ' ')
    s = re.sub(r'\.{2,}|…+', '', s)
    s = s.translate(PUNCT_MAP)
    s = re.sub(r'[,.!?:;()\'"~-]', '', s)
    s = re.sub(r'\s+', '', s)
    return s

norm = norm_strict if STRICT else norm_loose

rows = extract_inserts(TARGET, "quest_template_locale")
by_id = {}
for r in rows:
    qid = unquote(r[0])
    by_id[qid] = {
        "title": unquote(r[2]),
        "details": unquote(r[3]),
        "objectives": unquote(r[4]),
    }

diff_count = 0
total = 0
for line in open(JSONL, encoding="utf-8"):
    total += 1
    rec = json.loads(line)
    qid = rec["id"]
    if qid not in by_id:
        print(f"=== {qid}: NOT IN DB ===")
        continue
    cur = by_id[qid]
    wh = rec
    lines = []
    for field in ["title", "objectives", "details"]:
        c = cur[field].strip()
        w = wh.get(field, "").strip()
        if norm(c) != norm(w):
            lines.append(f"  [{field}]\n    DB : {c}\n    WH : {w}")
    if lines:
        diff_count += 1
        print(f"\n=== quest {qid} ===")
        print("\n".join(lines))

mode = "strict (punctuation/$B normalized)" if STRICT else "loose ($N/$n case only)"
print(f"\n--- {diff_count} quests with diffs out of {total} fetched [{mode}] ---", file=sys.stderr)
