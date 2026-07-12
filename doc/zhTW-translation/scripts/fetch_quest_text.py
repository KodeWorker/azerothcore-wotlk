import re, os, sys, subprocess, time, json, html

# SCRATCH: a scratch dir for this run's working files (IDS_FILE input, OUT_FILE/DONE_IDS_FILE
# output). Point ZHTW_SCRATCH at your session's scratchpad, or let it default.
SCRATCH = os.environ.get("ZHTW_SCRATCH", "/tmp/zhtw-scratch")
os.makedirs(SCRATCH, exist_ok=True)
IDS_FILE = os.path.join(SCRATCH, "wowhead_final_zh.txt")  # one quest ID per line (or id<TAB>slug), from the check_wowhead2.sh pass
OUT_FILE = os.path.join(SCRATCH, "quest_text_extracted.jsonl")
DONE_IDS_FILE = os.path.join(SCRATCH, "quest_text_done_ids.txt")

METADATA_PREFIXES = ("等級", "新增於", "獎勵", "+")

def fetch_html(qid, timeout=15):
    try:
        out = subprocess.run(
            ["curl", "-sL", "--max-time", str(timeout), f"https://www.wowhead.com/tw/quest={qid}"],
            capture_output=True, timeout=timeout + 5
        )
        return out.stdout.decode("utf-8", errors="replace")
    except Exception:
        return ""

def convert_tokens(text):
    text = re.sub(r'<br\s*/?>', '$B', text)
    text = text.replace('&lt;name&gt;', '$n').replace('&lt;Name&gt;', '$N')
    text = text.replace('&lt;class&gt;', '$c').replace('&lt;Class&gt;', '$C')
    text = text.replace('&lt;race&gt;', '$r').replace('&lt;Race&gt;', '$R')
    text = re.sub(r'<[^>]+>', '', text)
    text = html.unescape(text)
    text = re.sub(r'\s*\n\s*', ' ', text)
    text = text.replace("'", "\\'")
    return text.strip()

def extract(qid, data):
    if not data:
        return None
    result = {"id": qid, "title": "", "objectives": "", "details": ""}

    m = re.search(r'<meta property="twitter:title" content="([^"]*)"', data)
    if m:
        result["title"] = convert_tokens(m.group(1))

    m = re.search(r'<meta name="description" content="(.*?)">', data)
    if m:
        desc = m.group(1)
        chunks = desc.split('​')
        first = chunks[0].strip()
        if first and not first.startswith(METADATA_PREFIXES):
            first = re.sub(r'。+$', '。', first)
            result["objectives"] = convert_tokens(first)

    m = re.search(
        r'<h2 class="heading-size-3">描述</h2>(.*?)(?:<h2 class="heading-size-3">|<div class="pad3">|<script)',
        data, re.S
    )
    if m:
        result["details"] = convert_tokens(m.group(1))

    return result

def load_done():
    if os.path.exists(DONE_IDS_FILE):
        return set(l.strip() for l in open(DONE_IDS_FILE) if l.strip())
    return set()

def main():
    ids = [l.split('\t')[0].strip() for l in open(IDS_FILE) if l.strip() and not l.startswith('#')]
    done = load_done()
    todo = [i for i in ids if i not in done]
    print(f"total={len(ids)} done={len(done)} todo={len(todo)}")

    with open(OUT_FILE, "a", encoding="utf-8") as outf, open(DONE_IDS_FILE, "a") as donef:
        for n, qid in enumerate(todo):
            html_data = fetch_html(qid)
            rec = extract(qid, html_data)
            if rec is None:
                rec = {"id": qid, "error": "fetch_failed"}
            outf.write(json.dumps(rec, ensure_ascii=False) + "\n")
            outf.flush()
            donef.write(qid + "\n")
            donef.flush()
            if (n + 1) % 50 == 0:
                print(f"[{n+1}/{len(todo)}] last={qid}")
            time.sleep(2.5)
            if (n + 1) % 200 == 0:
                print(f"cooldown pause after {n+1}...")
                time.sleep(300)

if __name__ == "__main__":
    main()
