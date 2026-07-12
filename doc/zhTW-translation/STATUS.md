# zhTW Translation — Status Report

Last updated: 2026-07-12, branch `feat/zhTW-translation`.

This directory tracks the ongoing pass to fill/fix Traditional Chinese (zhTW)
locale data across `data/sql/updates/pending_db_world/`. This report exists so
a fresh session (no prior context) can pick up exactly where this one left off.

## Where the actual SQL lives

All zhTW work is in `data/sql/updates/pending_db_world/`, one file per table
(consolidated from many smaller revision files earlier in this branch's history).
The main one referenced throughout this doc is whichever pending file currently
contains `quest_template_locale` INSERTs — **don't hardcode its filename**, it
gets renamed on re-consolidation. `scripts/write_quest_sql.py` finds it
dynamically; you can do the same with:
```
grep -l "INSERT INTO \`quest_template_locale\`" data/sql/updates/pending_db_world/*.sql
```

**Never edit `data/sql/base/` or `data/sql/updates/db_world/`** — immutable
per `CLAUDE.md`. All fixes go in `pending_db_world/` as new DELETE+INSERT pairs
that override the base row.

## Verifying changes before committing

This session hit two classes of bugs the SQL style linter (`apps/codestyle/codestyle-sql.py`)
does **not** catch:
1. Wrong column count in a VALUES tuple (e.g. a manually-typed row missing one
   `''`) — style-passes but MySQL rejects it with "Column count doesn't match
   value count".
2. A raw literal newline embedded inside a quoted string (from a bad extraction
   regex, or old pre-existing corruption) — breaks the SQL statement silently;
   sometimes it even still "succeeds" against a real MySQL import by accident
   because the unterminated string swallows subsequent lines until some later
   stray quote closes it, corrupting whatever it swallowed.

**Always do both of these before considering a batch done:**
- Field-count check: parse the file with `scripts/scan_missing_zhtw.py`'s
  `extract_inserts()` (quote/paren-aware, handles multi-line VALUES lists) and
  assert every row has the expected column count for its table, and that the
  ID set has no duplicates and matches the expected total.
- Real MySQL validation: `docker compose build ac-db-import && docker compose up ac-db-import`,
  check for exit code 0. **You must rebuild the image first** — `docker compose up`
  alone reuses a cached image and won't see your file edits.

## Current numbers (as of this report)

### Skip list — 368 quest IDs (`skip-list.tsv`)

Quests that should **not** be translated: unreachable in-game (no
creature/gameobject queststarter+questender row, and no `game_event_*_quest`
linkage either), OR carry a Blizzard/QA debug marker in their **English**
title (`<NYI>`, `[NYI]`, `<TXT>`, `[TXT]`, `<UNUSED>`, `REUSE`, `DEPRECATED`,
case-insensitive, angle- or square-bracket), OR are a confirmed internal
duplicate of an already-translated live quest (e.g. quest 13826 mirrors 6607;
quest 5383/7521/7561 mirror the real live quests 5515/7786; item rewards on
these duplicates are separately flagged UNUSED/DEPRECATED/[PH] by Wowhead too).

**Important caveat, learned the hard way this session:** Wowhead's own
"deprecated" labeling (page text like `此任務被暴雪標記為過期`, or a URL slug
containing the word "deprecated") reflects **current retail** status, not
WotLK-era status. Retail's Cataclysm+ revamps cut/replaced huge amounts of
old-world content that was perfectly live in 3.3.5a. **Do not skip-list a
quest on Wowhead's deprecated flag alone** — cross-check reachability in our
own DB first (creature/GO starter+ender, `game_event_*_quest` tables). Of 43
Wowhead-"deprecated"-slug quests checked this session, 40 were still reachable
in our DB and were correctly *kept* as translation targets; only 3 were
genuinely unreachable both ways.

The reverse mistake also happened: quests with real English titles (e.g.
"Thunderaan the Windseeker") that *are* unreachable in our DB were confirmed
as genuinely obsolete only by finding a duplicate quest ID with the same title
that *is* reachable and already translated (5786↔7521 pattern) — reachability
alone doesn't prove a title-legitimate quest is obsolete; check for a live
duplicate first if you're unsure.

**Policy-consistency follow-up:** early in the session, 7 Wowhead-"deprecated"
quests (`12021, 12162, 12163, 12881, 8489, 8896, 9357`) were kept as
translation candidates purely on the *principle* that the deprecated flag
alone shouldn't be trusted — none of the 7 actually had a *positive*
reachability signal (no starter/ender, no `game_event` link, no documented
successor quest). `8489` got moved to skip-list later when re-checked with
the full rigor developed by that point. The other 6 were still sitting as
candidates on the old, less rigorous basis until a direct request to
re-verify them — moved to skip-list for consistency, since they have the
exact same (lack of) evidence as `8489`. **Takeaway: "keep it because the
deprecated flag alone isn't proof" is not the same as "keep it because
there's positive evidence it's reachable"** — the former is a reason to
withhold judgment pending more evidence, not a reason to permanently commit
to treating something as translatable.

**Resolved:** the 10 quests reachable-but-marker-titled (`REUSE` ×6,
`<NYI> Clear Some Room`, `[NYI] Now this is Ram Racing... Almost.`,
`Warsong Outriders <NYI> <TXT>`, `REUSE ME`) were investigated individually
and all confirmed as incomplete/template content, not real translatable
quests — added to the skip list. Evidence per quest: the six `REUSE`
quests (8971-8976) have blank Details/Objectives, a broken `EndText`
("Return to ." — missing NPC name, a template bug), and are only reachable
via the seasonal-event quest pool (`game_event_seasonal_questrelation`,
Love is in the Air), not a real NPC — consistent with internal
"grant-a-random-reward" stub quests never meant to be player-visible.
`[NYI] Now this is Ram Racing...` has Details/Objectives that are literally
the unfilled placeholder *labels* `Log Descritpion`/`Quest Description`.
`REUSE ME` has `QuestLevel=-1`, the same internal-duplicate-stub signature
as the Thunderfury/Krastinov's finds below — it's a copy-paste template for
the "Crushing the Crown" city-variant quests. `<NYI> Clear Some Room` and
`Warsong Outriders <NYI> <TXT>` both have a broken `EndText` target and
Wowhead has never assigned either a real documented name (slugs are
literally `nyi-clear-some-room` and `warsong-outriders-nyi-txt`).
**Lesson for next time:** `game_event_seasonal_questrelation` reachability
is a weaker signal than a direct creature/GO starter+ender — worth
checking Details/Objectives/EndText content quality too before trusting it.

One more duplicate-item pattern found while resolving `item_template_locale`:
quests 7922/7923/7924/7925/8002/8293/8296/8568 (all blank English titles,
all unreachable) were tied to item 19322 `zzDEPRECATED Warsong Mark of Honor`
— the real item is 20558 `Warsong Gulch Mark of Honor`. Same shape as the
Thunderfury/Krastinov's duplicates: `zz`-prefixed names are a dev convention
for "sort to bottom, hidden." All 8 added to the skip list.

**Broader keyword sweep (31 more added).** A user-flagged example (`8270`
"test copy quest" — plain English, no `<NYI>`/`<TXT>`/etc. marker at all)
showed the marker-regex approach has a blind spot for generic test/debug
words. A follow-up sweep for `test`/`temp`/`blank`/`zzold`/`ph` patterns
found 49 more candidates — **all individually verified against Wowhead
before touching anything** (a plain keyword match is not enough on its own;
e.g. "Test Flight" and "Test of Endurance" are real quest names, not debug
markers). Of the 49: 23 were confirmed junk (English-only Wowhead slug, or
slug still carrying `zzold`, or literally containing `needs-reward`), 2 were
duplicate IDs of an already-translated "Test of Lore"/"Test of Strength"
quest (5 total IDs in that family), and 2 more (`9051` "Toxic Test", `13649`
"Justin's Fun Test") were reachable with no Wowhead documentation — kept per
user judgment as likely deprecated. All 31 added to the skip list. The
other 18 of the 49 were confirmed real (Chinese Wowhead slug matching the
concept) and left untouched.

**3 gaps that slipped through every scan, now fixed.** `12300` "Test of
Mettle" and `12520` "Rhino Mastery: The Test" had **blank Title** while
other fields (EndText/CompletedText/ObjectiveText1) were already filled —
the "missing" scan only flags rows where the *concatenation* of all fields
is empty, so a row with a blank Title but content elsewhere slips through
(same root cause as quest 11623's earlier discovery). Filled both from
Wowhead. `11987` "zzOLDFortune Card: Silver" was also in this state, but
turned out to be a genuine deprecation (Wowhead: `此任務被暴雪標記為過期` +
confirmed unreachable in our own DB, both signals agreeing this time) —
**and its `pending_db_world` override was actively regressing an
already-correct base translation** (`data/sql/base/db_world/quest_template_locale.sql`
already had `幸運卡片：白銀` for it; some earlier mechanical pass had
overwritten that with the raw English `zzOLDFortune Card: Silver` in the
pending override). Deleted the override entirely rather than "fixing" it
with a translation — for confirmed-unreachable content there's no reason
for a pending override to exist at all, and it lets the correct base value
take effect. **Worth a broader check some day:** if one such regression
existed, there may be others in the ~1538-quest bracket-title backlog that
this session's Wowhead pipeline "fixed" without checking whether base
already had something better.

**Systemic gender-token bug found and fixed while investigating the above.**
Wowhead's web display renders the `$g male:female;` token as a raw
`<male/female>` bracket pair, and the extraction pipeline copied that
literally instead of converting it back to `$g...:...;` (the project's
actual convention, confirmed against existing rows like quest 5633).
Found 50 instances across 9 already-translated rows (`5633, 11190, 12520,
13132, 13607, 13614, 13816, 13818`, plus more) using 25 different
male/female word-pair variants. Fixed globally with a regex sub
(`<X/Y>` → `$gX:Y;`) across the whole file, and `scripts/fetch_quest_text.py`'s
`convert_tokens()` now handles this automatically for future runs (added
right before the generic tag-stripper, which would otherwise just delete
the bracket pair and lose the content). Still worth a spot-check for stray
`<.../ ...>` patterns after any future extraction batch, just in case.

**The same "concatenation masks a blank primary field" bug class exists in
`item_template_locale` too** (checked on request; `quest_greeting_locale`
only has one text field, so it's structurally immune). Found 18 items with
blank `Name` but a real, non-empty `Description` — the "missing" scan only
flags rows where Name+Description concatenated is empty. 16 of the 18 are
orphaned deprecated/test items (`Deprecated Writ of Lakeshire`,
`zzOLDCodex of...`, `[PH] Hakkar'i Urn`, `NPC Equip 46371`, etc. — the same
naming patterns established above) with **no quest referencing them at
all**, so out of scope either way. But 2 are real, well-known items that
just happened to have `Name` set to `NULL` by an already-merged migration
(`data/sql/updates/db_world/2026_05_30_06.sql` — immutable, can't be
edited directly, so fixed via a `pending_db_world` override instead):
`38301` "D.I.S.C.O." (the Disco Ball trinket) and `40768` "MOLL-E" (the
portable mailbox trinket), both kept as literal pass-through names (same
convention as `5732` "NG-5" — stylized proper-noun/acronym names aren't
translated). One more (`5550` "Fast Test Gun") has an untranslated English
`Description` ("Testing the LOC trigger") confirming it's genuine test
content, not a real gap — left alone.

### Translated and pushed this session

- **1460** quest_template_locale rows filled from Wowhead TW quest pages
  (Title + Details + Objectives). Two sub-batches: 1022 from the original
  "bracket-title" backlog (rows that existed but Title was still raw English
  wrapped in `[brackets]`), then 157 more from the separately-discovered
  "fully blank row" backlog.
- 1 `gameobject_template_locale` batch: 365 entries' `castBarCaption` (the
  progress-bar text shown while interacting with an object, e.g. picking a
  flower) filled — was blank even where `name` was translated, causing an
  English fallback in-game. Reported by the user in-game (quest 9799,
  "Collecting" instead of "採集").
- 1 `item_template_locale` entry (5732, "NG-5" — kept as-is, it's a code name).

### Remaining gaps, with reference-source status

**Important correction made after this report was first written:** the original
`quest_request_items_locale` count (571, later 566 after skip-list filtering)
had a scanning bug — `scan_missing_zhtw.py`'s `unquote()` returned the literal
4-character string `"NULL"` for unquoted SQL `NULL` values instead of treating
it as empty, so rows with a genuinely-`NULL` English `CompletionText` (nothing
to translate, not a gap at all) were miscounted as "has English text, missing
zhTW." **561 of the 566 were false positives.** The bug is fixed in
`scripts/scan_missing_zhtw.py` (see the comment on `unquote()`); re-running it
now correctly reports far fewer. If you regenerate any gap list, use the fixed
script — don't trust old counts anywhere in git history before this fix.

| File | Table | Field | Count | Status |
|---|---|---|---|---|
| `quests-no-wowhead-reference.tsv` | `quest_template_locale` | Title/Details/Objectives | 75 | From the bracket-title backlog; Wowhead itself has no zhTW translation for these either (confirmed via URL slug still being English/ASCII) |
| `quest_template_locale-gaps.tsv` | `quest_template_locale` | Title/Details/Objectives | 11 | Same as above but from the "fully blank row" backlog |
| `quest_request_items_locale-gaps.tsv` | `quest_request_items_locale` | CompletionText | **5** (corrected from 566 — see above) | **Blocked, no source found** (see below) |
| `quest_offer_reward_locale-gaps.tsv` | `quest_offer_reward_locale` | RewardText | 7 | **Blocked, no source found** (see below) — confirmed all 7 have real English text, no NULL issue here |
| `quest_greeting_locale-gaps.tsv` | `quest_greeting_locale` | Greeting | 126 | **Blocked, no source found** (see below) — confirmed all 126 have real English text, no NULL issue here |
| — | `item_template_locale` | Name/Description | **0** — fully resolved | Was 14 raw gaps; 1 filled (5732), 1 deliberately dropped (33776, Wowhead-flagged `[PH]` placeholder, noted in `skip-list.tsv`'s trailer comment), the other 12 all turned out to be items tied only to skip-listed/duplicate quests (see the `zzDEPRECATED`/`UNUSED`/`DEPRECATED`/`[PH]`/`NPC Equip <id>` pattern discussed above) |

**80 quests (75 + 5) have zero usable translation source anywhere found —
these need original/manual translation**, same as any from-scratch localization
work. The reward/completion/greeting blockers now total a much smaller **138**
entries (5 + 7 + 126), not the ~700 originally estimated — still blocked on
finding a source, but a far smaller problem than first reported.

## The CompletionText / RewardText / Greeting dead end

Investigated thoroughly, documented here so nobody re-does this work:

**What was tried:**
1. Static HTML of the quest page (`wowhead.com/tw/quest=<id>`) — the page
   *does* expose `<h2 class="heading-size-3">描述</h2>...` (Details) and the
   `<meta name="description">` tag (Objectives, see extraction notes below),
   but the "奬勵" (reward) section only contains the item-choice UI HTML
   (rendered client-side), never the NPC's spoken reward line. Checked 3
   quests including one (id 7) with substantial known English RewardText —
   nothing.
2. Wowhead's tooltip API, `nether.wowhead.com/tooltip/quest/<id>?locale=zhTW`
   — works, and does return zhTW text, but it's **retail** game data, not
   classic/WotLK (marks ordinary still-live Elwynn Forest quest 12 as
   "已廢除"/deprecated, since retail literally deleted it in Cataclysm). Even
   if it were the right version, the tooltip only contains Title+Objectives,
   same info as the meta description — no reward/completion dialogue. Tried
   `&detail=1`, `&power=1`, `&full=1` params, no difference.
3. NPC pages (`wowhead.com/tw/npc=<entry>`) for `quest_greeting_locale` —
   same limitation, the gossip/greeting text isn't in the static HTML either.
   Confirmed on creature 10260 "Kibler" (known English greeting text, not
   findable anywhere in the page source).

**Conclusion:** Wowhead does not publicly expose these three fields for
classic/WotLK content in any scrapable form found this session. If picking
this back up, either (a) find a different reference site/dataset, or (b) plan
for manual/original translation.

## Wowhead TW extraction method (for `quest_template_locale`)

Fetch `https://www.wowhead.com/tw/quest=<id>` with `curl -sL` (must follow
the redirect — the bare `quest=<id>` URL 301s to `quest=<id>/<slug>`).

- **Title**: `<meta property="twitter:title" content="...">`.
- **Objectives**: `<meta name="description" content="...">`. Wowhead
  concatenates the real objectives text with template metadata
  (level/zone/reward info), joined by a **zero-width space** (U+200B, NOT a
  regular space). Split on `​`, take the first chunk; if it starts with
  `等級`/`新增於`/`獎勵`/`+<digit>` it's pure metadata (no real objectives
  text for this quest) — otherwise it's real, just collapse a trailing `。。`
  (doubled period, template artifact) down to one `。`.
- **Details**: `<h2 class="heading-size-3">描述</h2>(.*?)` up to the next
  `<h2 class="heading-size-3">` **or** `<div class="pad3">` **or** `<script`
  — the two extra stop conditions matter: quests without a subsequent
  heading (e.g. no separate reward section) will run the capture straight
  into the page's "check completion" macro/script block otherwise, pulling
  in a raw newline + JS source that silently breaks the SQL statement (this
  happened in the first batch, caught 2 already-pushed rows corrupted this
  way — see git log for the fix commit).
- **Token conversion**: `&lt;name&gt;`→`$n`, `&lt;Name&gt;`→`$N`,
  `&lt;class&gt;`→`$c`/`$C`, `&lt;race&gt;`→`$r`/`$R` (lowercase-tag forms
  seen in practice; watch for uppercase-tag variants too). `<br/>` → `$B`
  (each occurrence individually, so `<br/><br/>` naturally becomes `$B$B`,
  matching the project's paragraph-break convention). Strip remaining HTML
  tags, `html.unescape()`, then collapse any stray raw `\n` to a space as a
  safety net.

All of this is implemented in `scripts/fetch_quest_text.py`. Pipeline:
`scripts/check_wowhead2.sh` (one ID → status+slug, run sequentially with
~1.5s sleep) → categorize slugs (CJK = real content, ASCII/hyphen = no zhTW
reference, contains "deprecated" = check reachability before deciding) →
`scripts/fetch_quest_text.py` (full extraction, resumable via a done-ids
file) → `scripts/write_quest_sql.py` (writes DELETE+INSERT pairs into the
pending file, preserving EndText/CompletedText/ObjectiveText1-4 as-is).

**Rate limiting**: Wowhead/CloudFront will 403 after roughly ~300 requests in
a burst. Sequential with 1-1.5s spacing avoids re-triggering it, but even
then this session saw wildly unpredictable throughput (sometimes ~1
req/1.5s, sometimes ~1 req/60s for stretches) with no clear cause found —
plan for it to just take a while, and that it's a *sandbox-execution*
artifact, not a real Wowhead problem (a fresh `curl` test mid-"slowdown"
was always fast). It reliably finishes if left running; just check back
periodically rather than assuming it's hung.

## Ground-truth glossaries (`wowhead-client-ground-truth/`)

Extracted directly from a real WotLK 3.3.5a zhTW client
(`~/WOW_Client_zhTW`, `patch-zhTW-3.MPQ` — the latest patch file, most
complete data) using `scripts/dbc_tool.py` (needs `mpyq`:
`pip install --target=./pylibs mpyq`). These are Blizzard's own official
zhTW strings, useful for validating quest text against known-correct zone/
faction/race/class/dungeon/BG/achievement names — this is how the
`北風苔原`→`北風凍原` (Borean Tundra, a zhCN-leftover leak) and
`諾森德`→`北裂境` (Northrend's actual official zhTW continent name, contrary
to common assumption) bugs were confirmed.

| File | Entries | Source table |
|---|---|---|
| `AreaTable_zhTW.tsv` | 2307 | zone/subzone names |
| `Achievement_Name_zhTW.tsv` | 1817 | achievement titles |
| `AreaPOI_zhTW.tsv` | 738 | map point-of-interest names (**ID space doesn't line up with our server's `points_of_interest` table** on the couple of IDs spot-checked — don't assume a 1:1 ID match without re-verifying) |
| `Faction_zhTW.tsv` | 401 | faction/reputation names |
| `LFGDungeons_zhTW.tsv` | 195 | dungeon/instance names |
| `Map_zhTW.tsv` | 135 | continent/map names |
| `ChrRaces_zhTW.tsv` | 21 | race names |
| `BattlemasterList_zhTW.tsv` | 13 | battleground names |
| `ChrClasses_zhTW.tsv` | 10 | class names |

A generic Simplified→Traditional converter (OpenCC, tried via
`libopencc1.1`/ctypes, see conversation history if picking this up — not
copied into scripts/ since it didn't end up useful) is **not** sufficient
to catch this class of bug: `北風苔原`/`北風凍原` are both valid
*Traditional*-script strings, it's a terminology/word-choice difference
(mainland vs. Taiwan convention), not a simplified-character encoding leak.
OpenCC only catches the latter. The reliable method that worked: cross-
reference against these client-extracted ground-truth glossaries directly.

## Files in this directory

- `STATUS.md` — this file.
- `skip-list.tsv` — 368 quest IDs to exclude from translation, with English
  title and reason.
- `skip-list-non-quest-notes.txt` — the one non-quest (item) skip note.
- `quests-no-wowhead-reference.tsv` — 75 quest_template_locale gaps with no
  translation source anywhere.
- `quest_template_locale-gaps.tsv` — 11 more of the same, different backlog.
- `quest_request_items_locale-gaps.tsv` / `quest_offer_reward_locale-gaps.tsv`
  / `quest_greeting_locale-gaps.tsv` — blocked gaps, see above.
- `wowhead-client-ground-truth/` — official zhTW strings extracted from the
  game client, see above.
- `scripts/` — the extraction/validation pipeline, paths made portable
  (set `ZHTW_SCRATCH` env var to a working dir; defaults to
  `/tmp/zhtw-scratch`).

## Suggested next steps

1. Find a real source (or commit to manual translation) for
   CompletionText/RewardText/Greeting — 138 entries blocked on this alone
   (5 + 7 + 126; see "The CompletionText / RewardText / Greeting dead end"
   above for what was already tried and ruled out).
2. Manual/original translation for the 80 quests with literally no source
   (`quests-no-wowhead-reference.tsv` + `quest_template_locale-gaps.tsv`).

Everything else from this session is fully resolved: the skip list (368
entries), `item_template_locale` (0 real gaps left), and all 10
previously-ambiguous marker-titled quests — nothing pending a decision.
