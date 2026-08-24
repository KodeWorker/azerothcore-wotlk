# zhTW Translation — Status Report

Last updated: 2026-07-12, branch `feat/zhTW-translation`.

Tracks the pass to fill/fix Traditional Chinese (zhTW) locale data across
`data/sql/updates/pending_db_world/`. Written so a fresh session can pick up
without prior context.

## Where the SQL lives

All zhTW work is in `data/sql/updates/pending_db_world/`, one file per table.
**Don't hardcode filenames** — they get renamed on re-consolidation. Find the
current file dynamically:
```
grep -l "INSERT INTO \`quest_template_locale\`" data/sql/updates/pending_db_world/*.sql
```
**Never edit `data/sql/base/` or `data/sql/updates/db_world/`** — immutable
per `CLAUDE.md`. Fixes go in `pending_db_world/` as DELETE+INSERT pairs that
override the base row.

## Verifying changes before committing

The SQL style linter doesn't catch two bug classes:
1. Wrong column count in a VALUES tuple (style-passes, MySQL rejects it).
2. A raw literal newline inside a quoted string — breaks the statement
   silently, sometimes even "succeeds" against a real import while
   corrupting whatever the unterminated string swallows.

**Always do both before considering a batch done:**
- Field-count check via `scripts/scan_missing_zhtw.py`'s `extract_inserts()`
  (quote/paren-aware) — assert every row has the expected column count, no
  duplicate IDs.
- Real MySQL validation: `docker compose build ac-db-import && docker compose up ac-db-import`,
  check exit code 0. **Rebuild first** — `up` alone reuses a cached image.

## Current state

| Category | File | Count |
|---|---|---:|
| Skip list | `skip-list.tsv` | 389 quest IDs |
| Manual/original-translation backlog | `quests-no-wowhead-reference.tsv` | **0** (retired) |
| Title-only body gaps | `quest_template_locale-gaps.tsv` | **0** |
| Turn-in dialogue | `quest_request_items_locale-gaps.tsv` | **0** |
| Reward dialogue | `quest_offer_reward_locale-gaps.tsv` | **0** |
| Item names/descriptions | `item_template_locale` | **0** |
| Quest-giver greeting | `quest_greeting_locale-gaps.tsv` | **0** |

**All translation gaps in the project are now resolved.** The
manual-translation backlog stood at 80 quests and the Greeting blocker at
126 entries at the start of this session; both are now zero. The last 118
Greeting entries had no source anywhere (see "The dead end" below) and were
translated directly via LLM, grounded in official NPC/GO names and
corpus-established terminology (see "Hard-won methodology lessons" below).

## Skip-list criteria

A quest is skip-listed if it's unreachable in-game (no creature/GO
queststarter+questender row, no `game_event_*_quest` linkage) **or** carries
a Blizzard/QA debug marker in its English title (`<NYI>`, `<TXT>`,
`<UNUSED>`, `REUSE`, `DEPRECATED`, case-insensitive) **or** is a confirmed
duplicate of an already-translated live quest.

## Hard-won methodology lessons

- **Wowhead's "deprecated" flag reflects current retail status, not WotLK
  status.** Retail's Cataclysm+ revamps cut huge amounts of old-world
  content that was live in 3.3.5a. Never skip-list on the deprecated flag
  alone — cross-check DB reachability first. Prefer
  `wowhead.com/wotlk/quest=<id>` (the WotLK-build page) over the retail
  `/quest=<id>` or `/tw/quest=<id>` pages when checking deprecation status —
  it only shows the "marked obsolete" banner if the quest was actually
  invalid in 3.3.5a. Concrete case: quest `13377` — deprecated on retail,
  not on `/wotlk/`, and reachable in our DB — was real WotLK content.
- **DB reachability is still the decisive signal for this project**, even
  when Wowhead confirms a quest was genuinely real in WotLK. Several
  quests (`9767`, `14351`, `14439`, `9051`, `13649`, `8742`, `24426`,
  `24427`) are confirmed non-deprecated real content but unreachable via any
  creature/GO/game_event table in our DB — kept skip-listed, since nobody
  can start/complete them on this specific server regardless of their
  status on Blizzard's historical realms.
- **Reachability can also be granted by hardcoded C++ logic that SQL tables
  can't show** (BG-queue bonus systems, world events). When a quest looks
  like it might be one of these (part of a known BG/holiday/event family),
  grep the actual C++ source for the quest IDs referenced
  (`src/server/game/Battlegrounds/Battleground.cpp` etc.) before deciding —
  don't infer from indirect signals like sibling-translation state alone.
  This resolved `8742` (AQ40 gate quest — AzerothCore doesn't implement
  that event at all) and `24426`/`24427` (not among the 8 quest IDs the
  Call to Arms achievement code actually hardcodes).
- **The "masking bug"**: the missing-translation scanner flags a row only
  if *all* its fields concatenated are empty — so a row with a blank Title
  but real content elsewhere (or vice versa) slips through undetected.
  Same root cause hit `quest_template_locale` and `item_template_locale`
  independently; `quest_greeting_locale`/`quest_offer_reward_locale`/
  `quest_request_items_locale` are structurally immune (single text field).
- **The regression bug (biggest finding, 2026-07-12): 570 quests in
  `quest_template_locale` had a `pending_db_world` override that reverted
  Title/Details/Objectives back to raw bracketed English, even though
  `base/db_world/quest_template_locale.sql` already had complete,
  professional-quality zhTW translations underneath.** This is why the
  manual-translation backlog kept shrinking every time it was re-checked —
  the original ~1538-quest "bracket-title" backlog was built without ever
  diffing against base. Fixed by deleting all 570 bad override pairs
  (`rev_1783688290124463491.sql`); base's real content now takes effect.
  Swept every other locale table for the same pattern — zero found
  elsewhere, confined to `quest_template_locale`. **Takeaway: always diff
  base vs. pending directly before trusting any "needs translation" list,
  especially one built by an earlier mechanical pass.** Spot-checked 6
  restored quests against Wowhead's WotLK English source afterward — all
  accurate, correct NPC/item/zone names throughout.
- **Wowhead's web display renders the `$g male:female;` gender token as a
  raw `<male/female>` bracket pair** — the extraction pipeline must convert
  it back (`scripts/fetch_quest_text.py`'s `convert_tokens()` handles this
  now) or it silently loses the content to the generic tag-stripper.
- **When no scrapable source exists at all (`quest_greeting`'s final 118
  entries), LLM translation grounded in the project's own established data
  works well** — don't translate proper nouns freehand. Every
  `quest_greeting` row's key IS the speaking NPC/GO's entry ID, so its
  official zhTW name comes straight from `creature_template_locale`/
  `gameobject_template_locale`, no guessing needed. For other proper nouns
  (zone names, faction/cult names, business names), grep the existing
  corpus for precedent before translating — concrete case: "Kibler's
  Exotic Pets" is NOT "異寵店" (a freehand guess); the already-translated
  quest `4729` establishes "基布雷爾的特殊寵物" as the real convention.
  Same for "Burning Blade" → corpus-established `火刃`, not a literal
  `燃燒之刃` guess. Cross-referencing each `quest_greeting` row's linked
  quests (`linked_quests` column) for their already-translated
  Title/Details gives strong grounding context per entry.
- **When a translated term names a "type of being" (not a unique NPC),
  check whether it's also an actual `creature_template` entry, not just a
  corpus text match** — a Wowhead page or flavor-text mention can still be
  wrong. Caught two real mistakes this way post-translation: "Dark Riders"
  was translated as `黑暗騎士` (freehand), but both a real Wowhead TW page
  (`quest=40838`) and this project's own `creature_template_locale`
  ("Dark Rider of Acherus" → `亞榭洛黑騎兵`) confirm the correct term is
  `黑騎兵`. "Leper Gnomes" was translated as `痲瘋侏儒`, but
  `creature_template_locale`'s own "Leper Gnome" (entry 1211) is
  `麻瘋地精` — confirmed by the client DBC ground truth
  (`ChrRaces_zhTW.tsv` race ID 7) that this project's official term for
  Gnome is `地精`, not the more common fan-convention `侏儒`. Both fixed.
  Not every such term has a single answer, though — "Burning Blade" itself
  is inconsistent even in official base data (`火刃暴徒`/`火刃新兵` vs
  `燃刃狂熱者` on different creatures of the same name), and generic
  English usage of a creature-type word (e.g. "prowler fodder", not
  naming the specific "Prowler" creature) doesn't need to match any one
  creature's exact translation.
- **`$g word1:word2;` gender tokens need their word pair translated too,
  not just carried over verbatim** — 3 of the 118 greeting entries left
  the pair in raw English (`$gboy:girl;`, `$gmister:ma'am;`, `$glad:lass;`)
  since there was no NPC-name-style lookup to catch it automatically. The
  corpus has thousands of already-established pairs for exactly this
  purpose (`grep -rhoP '\$g[^;]{1,20};' ... | sort | uniq -c | sort -rn`
  surfaces them ranked by frequency) — matched to `$g男孩:女孩;` (53 uses),
  `$g先生:女士;` (284 uses), `$g小夥子:姑娘;` (183 uses) respectively. This
  is a different failure mode than the `<male/female>` bracket-pair bug
  documented above (that one loses content to the tag-stripper entirely;
  this one keeps the content but leaves it untranslated) — worth a
  specific check for stray `\$g[a-zA-Z]` patterns after any manual/LLM
  translation batch, the same way the bracket-pair bug gets checked after
  Wowhead extraction batches. Swept the entire project for this pattern
  after finding those 3 (all of `pending_db_world` plus base's zhTW rows,
  which can't be edited but are worth knowing about) — zero further
  instances found anywhere; confirmed fully clean project-wide.

## The CompletionText / RewardText / Greeting dead end

Wowhead does not publicly expose these three fields for classic/WotLK
content in any scrapable form found this session:
1. `wowhead.com/wotlk/tw/quest=<id>` static HTML has Details (`<h2>描述</h2>`)
   and Objectives (`<meta name="description">`), but the reward section is
   client-rendered UI only — no NPC reward line.
2. `nether.wowhead.com/tooltip/quest/<id>?locale=zhTW` returns zhTW text but
   it's **retail** data, not classic/WotLK, and only has Title+Objectives
   anyway.
3. NPC pages (`wowhead.com/wotlk/tw/npc=<entry>`) don't expose gossip/greeting
   text in static HTML either.
4. DBC/client extraction (2026-07-12): checked whether `quest_greeting`
   content exists in the client's static DBC/MPQ data — no, this kind of
   NPC dialogue is server-sent, never baked into client files; WotLK's DBC
   catalog has no such file type. The project's own zhTW client install has
   play-history WDB cache files, but the account is literally named
   "AzerothCore," so that cache only reflects what our own server already
   sent — circular, not an independent source.

**Resolution (2026-07-12): all 126 `quest_greeting` entries are now
translated.** 8 were a free win — cross-referencing the English Greeting
text against `npc_text` (exact string match) found entries whose text is a
verbatim duplicate of an already-translated `npc_text` entry, so those
zhTW translations were copied over directly. The remaining 118 had no
scrapable source anywhere, so they were translated directly (LLM,
grounded in the project's own established data — see "Hard-won
methodology lessons" above for the technique). `RewardText`/
`CompletionText` are also both fully resolved (see the "Recent fixes"
history above) — this whole category is closed out project-wide.

## Wowhead TW extraction method (for `quest_template_locale`)

Fetch `https://www.wowhead.com/wotlk/tw/quest=<id>` with `curl -sL` (must
follow the redirect). Use the `/wotlk/tw/` build-specific path, not the bare
`/tw/` retail-flavored one — same content coverage, but the deprecated-flag
check is only meaningful on the build-specific page (see "Hard-won
methodology lessons" above).

- **Title**: `<meta property="twitter:title" content="...">`.
- **Objectives**: `<meta name="description" content="...">`, split on the
  zero-width space (U+200B) Wowhead uses to join real text with template
  metadata; take the first chunk unless it starts with
  `等級`/`新增於`/`獎勵`/`+<digit>` (pure metadata, no real text).
- **Details**: `<h2 class="heading-size-3">描述</h2>(.*?)` up to the next
  `<h2 class="heading-size-3">`, `<div class="pad3">`, or `<script` — all
  three stop conditions matter, or the capture runs into page JS.
- **Tokens**: `&lt;name&gt;`→`$n`, `&lt;Name&gt;`→`$N`, `&lt;class&gt;`→`$c`/`$C`,
  `&lt;race&gt;`→`$r`/`$R`, `<br/>`→`$B`, `<male/female>`→`$gmale:female;`.
  Strip remaining tags, unescape HTML entities, collapse stray `\n`.

Implemented in `scripts/fetch_quest_text.py`. Pipeline:
`scripts/check_wowhead2.sh` (status+slug check) → categorize → `fetch_quest_text.py`
(extraction) → `scripts/write_quest_sql.py` (writes DELETE+INSERT pairs).

**Rate limiting**: Wowhead/CloudFront 403s after ~300 requests in a burst.
Sequential with 1–1.5s spacing avoids it, but throughput can be
unpredictable in a sandboxed session — not a real Wowhead problem, just
keep it running.

## Ground-truth glossaries (`wowhead-client-ground-truth/`)

Extracted from a real WotLK 3.3.5a zhTW client (`~/WOW_Client_zhTW`,
`patch-zhTW-3.MPQ`) via `scripts/dbc_tool.py` (needs `mpyq`:
`pip install --target=./pylibs mpyq`). Official zhTW strings, used to catch
zhCN-terminology leaks (e.g. `北風苔原`→`北風凍原` Borean Tundra,
`諾森德`→`北裂境` Northrend). A generic Simplified→Traditional converter
(OpenCC) is **not** sufficient for this — both leaked and correct forms are
valid Traditional script, it's a word-choice difference, not an encoding
one. Cross-referencing these client-extracted glossaries directly is the
only method that worked.

| File | Entries |
|---|---:|
| `AreaTable_zhTW.tsv` | 2307 (zone/subzone names) |
| `Achievement_Name_zhTW.tsv` | 1817 |
| `AreaPOI_zhTW.tsv` | 738 (**ID space doesn't line up with our `points_of_interest` table** — verify before trusting a 1:1 match) |
| `Faction_zhTW.tsv` | 401 |
| `LFGDungeons_zhTW.tsv` | 195 |
| `Map_zhTW.tsv` | 135 |
| `ChrRaces_zhTW.tsv` | 21 |
| `BattlemasterList_zhTW.tsv` | 13 |
| `ChrClasses_zhTW.tsv` | 10 |

## Files in this directory

- `STATUS.md` — this file.
- `skip-list.tsv` — 390 quest IDs to exclude, with English title and reason.
- `skip-list-non-quest-notes.txt` — the one non-quest (item) skip note.
- `quests-no-wowhead-reference.tsv`, `quest_template_locale-gaps.tsv`,
  `quest_request_items_locale-gaps.tsv`, `quest_offer_reward_locale-gaps.tsv`,
  `quest_greeting_locale-gaps.tsv` — all empty/retired, kept for their
  header-comment history.
- `wowhead-client-ground-truth/` — official zhTW strings from the client.
- `scripts/` — extraction/validation pipeline. Portable via `ZHTW_SCRATCH`
  env var (defaults to `/tmp/zhtw-scratch`).

## Status

**Every translation gap in this project is resolved.** There is no
outstanding zhTW translation work as of 2026-07-12. If new gaps are found
in the future (e.g. from a data update), use the same tables/scripts and
methodology documented above rather than starting from scratch.
