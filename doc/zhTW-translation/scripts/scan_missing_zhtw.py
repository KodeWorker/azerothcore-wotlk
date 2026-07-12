import re, os, sys

# ROOT: path to the azerothcore-wotlk repo's data/sql dir. SCRATCH: a scratch dir for
# this script's own output files (point it at your current session's scratchpad, or any
# writable temp dir -- it's just where the *_gaps.txt output lands, nothing repo-permanent).
ROOT = os.path.expanduser("~/github/azerothcore-wotlk/data/sql")
SCRATCH = os.environ.get("ZHTW_SCRATCH", "/tmp/zhtw-scratch")
os.makedirs(SCRATCH, exist_ok=True)

def split_tuples(text):
    """Yield each top-level (...) tuple's inner content from a VALUES block, respecting quotes/escapes."""
    i = 0
    n = len(text)
    while i < n:
        if text[i] == '(':
            depth = 1
            j = i + 1
            in_str = False
            while j < n and depth > 0:
                c = text[j]
                if in_str:
                    if c == '\\':
                        j += 2
                        continue
                    if c == "'":
                        in_str = False
                else:
                    if c == "'":
                        in_str = True
                    elif c == '(':
                        depth += 1
                    elif c == ')':
                        depth -= 1
                j += 1
            yield text[i+1:j-1]
            i = j
        else:
            i += 1

def split_fields(tup):
    """Split a tuple's inner content on top-level commas, respecting quotes/escapes."""
    fields = []
    cur = []
    in_str = False
    i = 0
    n = len(tup)
    while i < n:
        c = tup[i]
        if in_str:
            cur.append(c)
            if c == '\\':
                if i+1 < n:
                    cur.append(tup[i+1])
                    i += 2
                    continue
            elif c == "'":
                in_str = False
            i += 1
            continue
        else:
            if c == "'":
                in_str = True
                cur.append(c)
            elif c == ',':
                fields.append(''.join(cur))
                cur = []
            else:
                cur.append(c)
            i += 1
    fields.append(''.join(cur))
    return [f.strip() for f in fields]

def unquote(s):
    s = s.strip()
    if len(s) >= 2 and s[0] == "'" and s[-1] == "'":
        inner = s[1:-1]
        return inner.replace("\\'", "'").replace('\\\\', '\\')
    if s == "NULL":
        # unquoted literal SQL NULL, not a quoted empty string -- treat as no text.
        # (Bug history: an earlier version of this function returned "NULL" as a
        # literal 4-char string here, which passed `.strip() != ''` filters as if
        # it were real content -- inflated quest_request_items_locale's gap count
        # from 5 real entries to 566 by miscounting NULL rows as translatable.)
        return ""
    return s

def extract_inserts(filepath, table_name):
    """Find INSERT INTO `table_name` ... VALUES (...),(...); blocks, return list of tuples (as field lists)."""
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    results = []
    pattern = re.compile(r"INSERT INTO `" + re.escape(table_name) + r"`\s*(?:\([^)]*\)\s*)?VALUES\s*", re.IGNORECASE)
    for m in pattern.finditer(content):
        start = m.end()
        # find end of statement: the semicolon that terminates this VALUES list (top-level, outside parens/quotes)
        i = start
        n = len(content)
        depth = 0
        in_str = False
        end = n
        while i < n:
            c = content[i]
            if in_str:
                if c == '\\':
                    i += 2
                    continue
                if c == "'":
                    in_str = False
            else:
                if c == "'":
                    in_str = True
                elif c == '(':
                    depth += 1
                elif c == ')':
                    depth -= 1
                elif c == ';' and depth == 0:
                    end = i
                    break
            i += 1
        block = content[start:end]
        for tup in split_tuples(block):
            results.append(split_fields(tup))
    return results

def files_with_insert(table_name, dirs):
    out = []
    for d in dirs:
        full = os.path.join(ROOT, d)
        if not os.path.isdir(full):
            continue
        for fn in sorted(os.listdir(full)):
            if not fn.endswith('.sql'):
                continue
            fp = os.path.join(full, fn)
            with open(fp, 'r', encoding='utf-8', errors='replace') as f:
                head = f.read()
            if f"INSERT INTO `{table_name}`" in head:
                out.append(fp)
    return out

CURRENT_DIRS = ["base/db_world", "updates/db_world", "updates/pending_db_world"]

def get_zhtw_ids(table_name, id_field_idx, locale_field_idx, text_field_idxs, key_fields_idx=None):
    """Return dict: key -> concatenated text (from all zhTW rows across current-state files, last-write-wins by file order)."""
    files = files_with_insert(table_name, CURRENT_DIRS)
    zhtw = {}
    for fp in files:
        rows = extract_inserts(fp, table_name)
        for row in rows:
            if len(row) <= max(id_field_idx, locale_field_idx, *text_field_idxs):
                continue
            locale = unquote(row[locale_field_idx])
            if locale != 'zhTW':
                continue
            if key_fields_idx:
                key = tuple(unquote(row[i]) for i in key_fields_idx)
            else:
                key = unquote(row[id_field_idx])
            text = ''.join(unquote(row[i]) for i in text_field_idxs)
            zhtw[key] = text
    return zhtw, files

def get_base_english(table_name, id_field_idx, text_field_idxs, key_fields_idx=None):
    """Return dict: key -> concatenated text, from the base (non-locale) English table."""
    fp = os.path.join(ROOT, "base/db_world", f"{table_name}.sql")
    if not os.path.isfile(fp):
        return {}
    rows = extract_inserts(fp, table_name)
    out = {}
    for row in rows:
        if len(row) <= max([id_field_idx] + text_field_idxs):
            continue
        if key_fields_idx:
            key = tuple(unquote(row[i]) for i in key_fields_idx)
        else:
            key = unquote(row[id_field_idx])
        text = ''.join(unquote(row[i]) for i in text_field_idxs)
        out[key] = text
    return out

def report(name, universe_keys, zhtw_dict, out_file):
    missing = []
    for k in universe_keys:
        if k not in zhtw_dict:
            missing.append(k)
            continue
        # zhTW row exists but is entirely empty -> effectively no translation
        if zhtw_dict[k].strip() == '':
            missing.append(k)
    missing_sorted = sorted(missing, key=lambda x: (x if isinstance(x, tuple) else (x,)))
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(f"# {name}: quest-universe size={len(universe_keys)}, missing zhTW={len(missing_sorted)}\n")
        for k in missing_sorted:
            f.write((','.join(str(x) for x in k) if isinstance(k, tuple) else str(k)) + "\n")
    print(f"{name}: universe={len(universe_keys)} missing={len(missing_sorted)} -> {out_file}")
    return missing_sorted

def read_universe_quest_ids():
    fp = os.path.join(ROOT, "base/db_world/quest_template.sql")
    rows = extract_inserts(fp, "quest_template")
    return set(unquote(r[0]) for r in rows if r)

QUEST_IDS = read_universe_quest_ids()
print(f"quest_template universe: {len(QUEST_IDS)} quests")

# ---------- 1. quest_template_locale ----------
zhtw, files = get_zhtw_ids("quest_template_locale", id_field_idx=0, locale_field_idx=1,
                            text_field_idxs=[2,3,4,5,6,7,8,9,10])
report("quest_template_locale (quest text)", QUEST_IDS, zhtw,
       os.path.join(SCRATCH, "missing_zhtw_quest_template.txt"))

# ---------- 2. quest_offer_reward_locale ----------
reward_en = get_base_english("quest_offer_reward", id_field_idx=0, text_field_idxs=[9])
reward_universe = set(k for k, v in reward_en.items() if v.strip() != '')
zhtw_reward, _ = get_zhtw_ids("quest_offer_reward_locale", id_field_idx=0, locale_field_idx=1, text_field_idxs=[2])
report("quest_offer_reward_locale (reward text)", reward_universe, zhtw_reward,
       os.path.join(SCRATCH, "missing_zhtw_quest_reward.txt"))

# ---------- 3. quest_request_items_locale ----------
completion_en = get_base_english("quest_request_items", id_field_idx=0, text_field_idxs=[3])
completion_universe = set(k for k, v in completion_en.items() if v.strip() != '')
zhtw_completion, _ = get_zhtw_ids("quest_request_items_locale", id_field_idx=0, locale_field_idx=1, text_field_idxs=[2])
report("quest_request_items_locale (turn-in text)", completion_universe, zhtw_completion,
       os.path.join(SCRATCH, "missing_zhtw_quest_request_items.txt"))

# ---------- 4. quest_greeting_locale ----------
greet_en = get_base_english("quest_greeting", id_field_idx=0, text_field_idxs=[4], key_fields_idx=[0,1])
greet_universe = set(k for k, v in greet_en.items() if v.strip() != '')
zhtw_greet, _ = get_zhtw_ids("quest_greeting_locale", id_field_idx=0, locale_field_idx=2, text_field_idxs=[3], key_fields_idx=[0,1])
report("quest_greeting_locale (quest-giver greeting)", greet_universe, zhtw_greet,
       os.path.join(SCRATCH, "missing_zhtw_quest_greeting.txt"))

# ---------- 5. item_template_locale (quest items only) ----------
qt_fp = os.path.join(ROOT, "base/db_world/quest_template.sql")
qt_rows = extract_inserts(qt_fp, "quest_template")
item_idxs = [19,22,24,26,28,38,40,42,44,46,48,87,88,89,90,91,92]
quest_item_ids = set()
for row in qt_rows:
    for idx in item_idxs:
        if idx < len(row):
            v = unquote(row[idx])
            if v.isdigit() and int(v) != 0:
                quest_item_ids.add(v)
print(f"quest-referenced item ids: {len(quest_item_ids)}")

item_en = get_base_english("item_template", id_field_idx=0, text_field_idxs=None) if False else None
# item_template has Name1 at some index; find it directly instead of hardcoding whole schema
def get_item_name_universe(candidate_ids):
    fp = os.path.join(ROOT, "base/db_world/item_template.sql")
    with open(fp, 'r', encoding='utf-8', errors='replace') as f:
        header = f.read(20000)
    m = re.search(r"CREATE TABLE `item_template`\s*\((.*?)\n\)\s*ENGINE", header, re.S)
    cols = re.findall(r"`(\w+)`", m.group(1))
    name_idx = cols.index("name")
    rows = extract_inserts(fp, "item_template")
    out = {}
    for row in rows:
        if len(row) <= name_idx:
            continue
        iid = unquote(row[0])
        if iid in candidate_ids:
            out[iid] = unquote(row[name_idx])
    return out

item_en_names = get_item_name_universe(quest_item_ids)
item_universe = set(k for k, v in item_en_names.items() if v.strip() != '')
zhtw_item, _ = get_zhtw_ids("item_template_locale", id_field_idx=0, locale_field_idx=1, text_field_idxs=[2])
report("item_template_locale (quest items)", item_universe, zhtw_item,
       os.path.join(SCRATCH, "missing_zhtw_quest_items.txt"))

print("\nDone. Files listed above under scratchpad/.")
