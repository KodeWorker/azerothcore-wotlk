import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from scan_missing_zhtw import extract_inserts, unquote

PENDING_DIR = os.path.expanduser("~/github/azerothcore-wotlk/data/sql/updates/pending_db_world")

def find_quest_template_locale_file():
    """As of this writing it's rev_1783688290124463491.sql, but pending files get
    renamed/re-consolidated -- find whichever current file holds this table's INSERTs."""
    for fn in os.listdir(PENDING_DIR):
        if not fn.endswith(".sql"):
            continue
        fp = os.path.join(PENDING_DIR, fn)
        with open(fp, encoding="utf-8", errors="replace") as f:
            if "INSERT INTO `quest_template_locale`" in f.read():
                return fp
    raise FileNotFoundError("no pending_db_world file contains quest_template_locale INSERTs")

TARGET = find_quest_template_locale_file()
SCRATCH = os.environ.get("ZHTW_SCRATCH", "/tmp/zhtw-scratch")
JSONL = os.path.join(SCRATCH, "quest_text_extracted.jsonl")

def esc(s):
    return s.replace("\\", "\\\\").replace("'", "\\'")

rows = extract_inserts(TARGET, "quest_template_locale")
by_id = {}
order = []
for r in rows:
    qid = unquote(r[0])
    order.append(qid)
    by_id[qid] = [unquote(f) for f in r]  # 12 fields, unquoted values

updated = 0
skipped_no_row = []
for line in open(JSONL, encoding="utf-8"):
    rec = json.loads(line)
    qid = rec["id"]
    if qid not in by_id:
        skipped_no_row.append(qid)
        continue
    row = by_id[qid]
    row[2] = rec.get("title", "")
    row[3] = rec.get("details", "")
    row[4] = rec.get("objectives", "")
    updated += 1

print(f"updated {updated} rows; {len(skipped_no_row)} ids not found in current file: {skipped_no_row[:10]}")

header = "-- zhTW quest_template_locale translations, consolidated (base fill + English/mixed-content fixes + Wowhead-sourced mechanical pass + Wowhead TW batch fill for previously-untranslated bracket-title rows)"
with open(TARGET, "w", encoding="utf-8") as f:
    f.write(header + "\n")
    for qid in order:
        row = by_id[qid]
        f.write(f"DELETE FROM `quest_template_locale` WHERE `ID` = {qid} AND `locale` = 'zhTW';\n")
        vals = [qid, "'zhTW'"] + [f"'{esc(v)}'" for v in row[2:11]] + [row[11] if row[11] else "0"]
        f.write(
            "INSERT INTO `quest_template_locale` (`ID`, `locale`, `Title`, `Details`, `Objectives`, `EndText`, `CompletedText`, `ObjectiveText1`, `ObjectiveText2`, `ObjectiveText3`, `ObjectiveText4`, `VerifiedBuild`) VALUES ("
            + ", ".join(vals) + ");\n"
        )
print("done writing", TARGET)
