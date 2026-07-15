"""Cross-check kill/collect counts in zhTW Objectives+Details against the
true English source (quest_template's LogDescription+QuestDescription).

A text diff can look like harmless paraphrase while silently changing a
count (e.g. "10" -> "6"). This catches those regardless of whether
diff_quest_text.py also flagged the field.

Usage:
    python3 audit_quest_counts.py <lo> <hi>

Prints one line per quest ID in [lo, hi] (skip-list excluded) where a
number appears in the English source but not in the zhTW text, or
vice versa. Expect false positives: ratios ("10 to 1"), percentages,
org names with digits ("SI:7"), spelled-out number words -- verify each
against RequiredNpcOrGoCount/RequiredItemCount before "fixing" anything.
"""
import sys, re
sys.path.insert(0, "/home/kelvinwu/github/azerothcore-wotlk/doc/zhTW-translation/scripts")
from scan_missing_zhtw import extract_inserts, unquote

if len(sys.argv) != 3:
    print(__doc__)
    sys.exit(1)
LO, HI = int(sys.argv[1]), int(sys.argv[2])

EN_ROWS = extract_inserts("/home/kelvinwu/github/azerothcore-wotlk/data/sql/base/db_world/quest_template.sql", "quest_template")
EN_BY_ID = {unquote(r[0]): r for r in EN_ROWS}

TARGET = "/home/kelvinwu/github/azerothcore-wotlk/data/sql/updates/pending_db_world/rev_1783688290124463491.sql"
DB_ROWS = extract_inserts(TARGET, "quest_template_locale")
DB_BY_ID = {unquote(r[0]): r for r in DB_ROWS}

skip_ids = set()
with open("/home/kelvinwu/github/azerothcore-wotlk/doc/zhTW-translation/skip-list.tsv") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if parts and parts[0].isdigit():
            skip_ids.add(int(parts[0]))

ids = [i for i in range(LO, HI + 1) if i not in skip_ids]

def nums_in(s):
    return re.findall(r'(?<![A-Za-z$])\d+(?![A-Za-z])', s)

mismatches = []
for qid in ids:
    en = EN_BY_ID.get(str(qid))
    db = DB_BY_ID.get(str(qid))
    if not en or not db:
        continue
    en_all = unquote(en[75]) + " " + unquote(en[76])  # LogDescription + QuestDescription
    db_obj = unquote(db[4])
    db_details = unquote(db[3])
    en_nums = sorted(set(nums_in(en_all)))
    db_nums = sorted(set(nums_in(db_obj + " " + db_details)))
    missing_from_db = [n for n in en_nums if n not in db_nums and int(n) > 1]
    extra_in_db = [n for n in db_nums if n not in en_nums and int(n) > 1]
    if missing_from_db or extra_in_db:
        mismatches.append((qid, en_nums, db_nums, missing_from_db, extra_in_db))

print(f"{len(mismatches)} quests with possible number mismatches in [{LO}, {HI}]\n")
for qid, en_nums, db_nums, missing, extra in mismatches:
    print(f"{qid}: EN={en_nums}  DB={db_nums}  missing_from_DB={missing}  extra_in_DB={extra}")
