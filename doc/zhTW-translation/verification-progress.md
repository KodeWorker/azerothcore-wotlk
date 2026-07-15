# zhTW Content-Accuracy Verification — Progress

Tracks the **second pass** described in `STATUS.md`'s successor work: even after all
translation *gaps* were resolved (2026-07-12), real mistranslations and proper-noun
inconsistencies remained (found via commit `81781c72d`, 2026-07-15). This pass
re-verifies existing translations for *correctness*, not just presence.

## Methodology

**Phase 1** — fetch each quest from `wowhead.com/wotlk/tw/quest=<id>`
(`scripts/fetch_quest_text.py`), diff Title/Details/Objectives against
`quest_template_locale`, fix genuine content errors only (not stylistic paraphrase).

**Phase 2** — cross-check every proper noun (NPC/place/item) against its canonical table
(`creature_template_locale`/`item_template_locale`/`gameobject_template_locale`). Systemic
term-level errors (wrong race/family name, not just one NPC) get grepped and swept
project-wide immediately, not just within the current batch.

**Ground-truth priority** (highest to lowest — see agent memory `feedback_zhtw_*` for full
incident history behind each rule):
1. DBC files extracted from the real client (`wowhead-client-ground-truth/*.tsv`) — genuinely
   unimpeachable, but only covers zones/factions/races/classes/achievements/dungeons/
   battlegrounds/maps.
2. `creature_template_locale`/`item_template_locale` — best *available* reference for
   NPCs/items (no DBC coverage exists for these in this era), but not infallible; could
   itself carry the same scraping errors wowhead has. Two independent signals agreeing
   (e.g. this table + wowhead's dedicated NPC/item page) is stronger than either alone.
3. A specific NPC's/item's own dedicated wowhead page (`.../npc=<id>`, faction page, etc.)
   — better than a quest page, still not as strong as #1 or #2.
4. A single quest's wowhead prose — weakest signal. Never trust it alone for a proper noun;
   Blizzard's own localization isn't perfectly self-consistent, and wowhead's scrape can
   introduce its own errors (including zhCN-leak terms like `肯瑞托`/`天災軍團`/`巨魔`).
5. DB's own pre-existing text — no special status; same-row internal consistency is a
   symptom to notice, never a tiebreaker against the sources above.

**Working rules, condensed:**
- Read every bracketed field in a diff block (title/objectives/details) — a clean title diff
  does not mean the body is fine; several quests had Details/Objectives silently swapped
  with a different quest's content while only the title got noticed.
- Check same-row proper-noun consistency even when wowhead shows zero diff — a quest can be
  internally inconsistent without ever disagreeing with wowhead.
- Verify every kill/collect count against `RequiredNpcOrGoCount`/`RequiredItemCount`, or
  against the real English `LogDescription`/`QuestDescription` — every single time, even
  after a long streak of correct fixes. A run of confirmed-good counts is not evidence the
  next one is safe (batch 5 reverted three count "fixes" that were wrong this way). Watch
  for false-positive number matches too: ratios ("10 to 1"), percentages, org names with
  digits ("SI:7"), spelled-out number words, Chinese numerals.
- When replacing a field, use the verified source text verbatim rather than hand-patching
  just the wrong number/word — but still separately check any proper noun embedded in that
  verbatim text against its own canonical source (a correct count can still carry a wrong
  item/NPC name along with it).
- A title/rank shared by multiple NPCs (e.g. "High Executor") can be translated
  inconsistently across them in the base data itself — verify and fix per-NPC, never
  generalize a fix to "every NPC with this English title."

Both phases run on the same small batch before moving to the next.

## Completed ranges (quest_template IDs)

| Range | Date | Fixes | Notes |
|---|---|---|---|
| 100–140 (excl. skip-listed 108, 137) | 2026-07-15 | 5 | Pilot batch. See below. |
| 141–340 (excl. skip-listed 242, 259, 260, 316, 326, 327) | 2026-07-15 | ~40 targeted + 3 project-wide systemic sweeps (300+ occurrences) | Batch 2. See below — much higher hit rate than the pilot; see "Critical lesson" above for why. |
| 341–540 (excl. skip-listed 352, 390, 406, 462, 490, 497, 534) | 2026-07-15 | ~50 targeted + 4 project-wide systemic sweeps (~100 occurrences) | Batch 3. Highest bug density yet — see below. |
| 541–740 (excl. skip-listed 548, 612, 636, 740) | 2026-07-15 | ~15 targeted + 2 large clan/race-term sweeps (~55 occurrences) | Batch 4. See below — surfaced the Troll/Ogre terminology system, and confirmed several more wowhead-fetch errors that would have been regressions if applied blindly. |
| 741–940 (excl. 18 skip-listed) | 2026-07-15 | ~20 targeted fixes; also a widened count-audit across the entire 100–940 range done so far | Batch 5. Highest false-positive rate yet for count fixes — three count fixes had to be reverted mid-batch. |
| 941–1140 (excl. skip-listed 946, 987–989, 1128, 1129) | 2026-07-15 | ~25 targeted fixes + 3 project-wide term sweeps (卡利姆多→卡林多 138×, 大地之環→陶土議會 82×, 扎瑪→札瑪 等) | Batch 6. See below. Introduced `diff_quest_text.py --strict` (punctuation/$B-normalized diff) to cut the false-positive rate on large batches. |
| 1141–1340 (excl. skip-listed 1151, 1154–1163, 1165, 1277–1280, 1289–1300) | 2026-07-15 | ~20 targeted fixes + 1 project-wide term sweep (暗夜精靈→夜精靈, 251×) | Batch 7. See below — first batch with a confirmed zhCN-leak race term (暗夜精靈), confirmed by the user directly (matches `ChrRaces_zhTW.tsv` id 4 = 夜精靈); also the first batch where several of my own proposed fixes (Ogre/Gnome race-term guesses, Vimes/Reethe rank direction) were wrong and corrected by the user — see below for what actually held up. |
| 1341–1540 (excl. skip-listed 1390, 1397, 1441, 1443, 1460, 1461, 1533, 1537, 1538) | 2026-07-15 | ~20 targeted fixes + 3 project-wide term sweeps (幽靈崗哨→鬼旅崗哨 16×, 阿塔萊巨魔→阿塔萊食人妖 4×) | Batch 8. Highest bug density since batch 3 (108/191 flagged). Introduced `creature_template`'s literal in-game `name` field as a first-class ground-truth check (alongside `AreaTable_zhTW.tsv`) for NPC/place-name disputes — see below. |

**Total scope**: `quest_template_locale` in this pending file holds **8,867 quest rows** (IDs span 1–26034). After batch 8, **1,524 verified**, **7,343 remaining** — roughly 37 more ~200-ID batches at the current pace.

## Fixes log

- **Quest 113** (`昆蟲研究`): Details dropped a clause ("甚至整個艾澤拉斯大陸都會捲入其中")
  and mistranslated "this thing has given no indication it will subside" as "顯然已經迫在眉睫了"
  (wrong meaning — restored to "而且這個威脅顯然不會就此平息").
- **Quest 117** (`雷酒`): Details had `$B$B` (double break) x3 where the English source uses
  single `$b` — fixed to single `$B`.
- **Quest 130** (`拜訪草藥師`): Details was missing a `$B$B` paragraph break present in the
  English source — restored.
- **Quest 113 + 992**: NPC 7724 "Senior Surveyor Fizzledowser" is officially
  `高級勘探員菲茲杜瑟` (per `creature_template_locale`) but was referenced as `高階勘探員菲茲杜瑟`
  (wrong term for "Senior") in these two quests — fixed project-wide (4 occurrences).
- **Quests 136, 138, 139, 140** ("Captain Sanders' Hidden Treasure" chain): the person's
  name was spelled `桑德爾` in `quest_template_locale` (Title + Details, 8 occurrences) but
  the official name (creature 20351 in `creature_template_locale`) is `桑德斯船長` — the
  `quest_request_items_locale` turn-in text for quest 136 already correctly used `桑德斯`.
  Fixed all 8 occurrences to `桑德斯`.
- **Project-wide** (found via a broken-artifact check during phase 1, not tied to one
  quest): a dangling `$B$B已提供物品：` (trailing colon, no item name ever filled in —
  present in 0 base rows, not in English source or wowhead) was appended to the Objectives
  field of 14 quests: 138, 139, 140, 635, 695, 772, 894, 1029, 1030, 1781, 5904, 8303,
  10819, 10910. Stripped from all 14.

### Batch 2 (141–340) fixes log

**Content-swap bugs** (Details/Objectives belonged to an entirely different quest —
verified by comparing to `quest_template`'s real English source, not just wowhead):
- **Quest 182** (`食人妖的威脅`→`食人妖洞穴`): body was about "protecting Amberpine" — real
  quest is Grelin Whitebeard's Dun Morogh trogg-investigation quest. Note: wowhead's own
  fetched objectives count ("14") was itself wrong vs our source's `RequiredNpcOrGoCount1=10`
  — used wowhead's narrative but our own count.
- **Quest 218** (`冰與火`→`被竊取的日記`): body was about Thorin/fire elementals/a
  snow valley — real quest is Grelin Whitebeard's stolen-journal quest (retrieve journal
  from a troll). Caught only after a user spot-check; the diff tool *had* flagged this
  correctly, it was an agent reading mistake (see methodology lesson above).
- **Quest 313** (`被迫從遠處觀察`→`灰色洞穴`): body was about relaying Captain Sallow's
  orders to mountaineers — real quest is Pilot Stonegear's Wendigo-mane-collecting quest.
- **Quest 217**: only the Title was wrong (`果斷的一擊`→`保衛國王的領土`); Details/Objectives
  were already correct — verified explicitly after the 218/313/182 pattern emerged, not
  assumed.

**Same-row internal proper-noun inconsistency** (no diff vs. wowhead, found by manual
cross-check):
- **Quest 219**: `基沙恩`/`基山` (Corporal Keeshan) and `赤脊`/`紅嶺`/`紅嶺山脈` (Redridge
  Mountains) each appeared as two different spellings across the row's own fields. Unified
  to `基沙恩下士` and `赤脊山` throughout.

**Kill/collect count mismatches** (verified against `RequiredNpcOrGoCount`/English source,
a small script found all of these by extracting numbers — not reliable to catch by prose
reading alone):
- Quest 187: 5→10 (Elder Stranglethorn Tigers)
- Quest 224: 6→10 twice, and location `塞爾薩瑪`→`南部警戒塔` (contradicted its own
  ObjectiveText1)
- Quest 257: 8→6 (Mountain Buzzards)
- Quest 258: 10→5 (Elder Mountain Boars), and a missing "時限為12分鐘" (within 12 minutes)
  clause restored
- Quest 263: 8→10 twice (Stonesplinter Shaman/Bonesnapper)
- Quest 307: 6→4 (loads of Miners' Gear)
- Quest 315: 7→6 (Shimmerweeds), and location `卡拉諾斯`/`寒風峽谷`→`烈酒村` (Brewnall
  Village) in both Objectives and ObjectiveText1

**Truncated content** (DB was missing whole trailing sentences present in the English
source):
- Quest 279: Objectives was missing "Slay Gobbler and take his head. Bring Gobbler's Head
  to Karl Boran in Menethil Harbor" — appended.
- Quest 290: Objectives was missing "Use the key to open the Intrepid's Locked Strongbox"
  — appended.

**Wrong NPC name within a field**:
- Quest 309: Objectives said `胡達爾` where it should say `米蘭` (Miran) — Details and
  CompletedText in the same row already correctly said 米蘭.

**Project-wide systemic sweeps** (triggered by a batch-2 finding, applied across all of
`pending_db_world`, not just IDs 141–340):
- **`侏儒`→`地精`** (wrong fan-convention term for Gnome; this project's fixed convention
  per `ChrRaces_zhTW.tsv` ground truth is `地精`): 283 occurrences fixed across 7 files.
  Excluded 4 occurrences of `俾格米侏儒` ("pygmies" — a legitimate generic-noun use, verified
  against `npc_text.sql`'s English "pygmies", unrelated to the Gnome race).
- **`石裂`→`碎石怪`/`碎石穴居人`** (wrong term for the "Stonesplinter" trogg family; official
  per `creature_template_locale`): 12 occurrences across 6 quests (170's own `石齶` variant
  spelling not yet checked — flag for a future batch).
- **Goblin/Gnome Engineering questline** (7 quest rows: 3629, 3630, 3632, 3633, 3634, 3637,
  4181): titles and body text had `侏儒`/`地精`/`哥布林` scrambled relative to which trainer
  NPC (Gnome vs Goblin) each quest actually teaches — rebuilt each row's Title/Details/
  Objectives from the verified English source (`quest_template`'s literal "Gnome
  Engineering"/"Goblin Engineering" title per row).
- **`多倫上尉`→`多倫中尉`** (NPC 469 "Lieutenant Doren" is officially `多倫中尉`, not Captain):
  11 occurrences.
- **`索爾森`→`托爾森`** (NPC 738 "Private Thorsen" is officially `士兵托爾森`): 10 occurrences.
- **`沙克斯·比格維茲`→`比格維茲`** (NPC 7407 "Chief Engineer Bilgewhizzle" has no official
  first name — `沙克斯` was fabricated): 14 occurrences.
- **`沼地蠕行者`→`沼地爬行者`** (creature 1040 "Fen Creeper", quest 275's actual kill target):
  3 occurrences.
- **`索爾圖斯`→`薩爾圖斯`** (creature 1353 "Sarltooth", quest 296): 2 occurrences.
- **`兒童周`→`兒童週`** (simplified-Chinese character leak — "week" must be traditional 週):
  30 occurrences across 3 files.

**Skip-list update**: quest 241 (`<TEST> HEY MISTER WILSON!`) added to `skip-list.tsv` —
carries the `<TEST>` QA debug marker per the established skip-list criteria, was missing
from the list.

**Cosmetic**: stray trailing `*` and trailing whitespace inside quoted SQL string fields
cleaned up on quests 171 and 415 (found incidentally, harmless but sloppy).

### Batch 2 — second review pass (same-day follow-up, after re-auditing every field)

Re-running the diff after the fixes above still left 70/194 quests with some diff; a full
re-read of every `[details]`/`[objectives]` line (not just `[title]`) against the true
English source found a few more real bugs the first pass missed:

- **Quest 167**: spurious `$C` (class) token where the English source just says "thieving
  types" (a generic noun, no class-token in the source at all) — fixed to `盜賊`.
- **Quest 278**: Objectives named the wrong NPC (`阿胥蘭·暗石`) and wrong item (`狂熱之血`);
  the correct questgiver (confirmed both via `creature_template` entry 1093 and the NPC's own
  wowhead page) is `首席工程師辛德維爾七世`, and the real item list is 潛伏者的毒液/莫格羅什
  水晶/鱷魚的眼淚 (Lurker Venom/Mo'grosh Crystal/Crocolisk Tear) — ObjectiveText1 in the same
  row already correctly named Hinderweir VII, only Objectives itself was wrong.
- **Quest 309**: same content-swap bug as 218/313/182, just missed on the first pass —
  Details was about "Sten" and Miran unloading powder kegs; real Details (verified against
  English source, which for once matches wowhead's fetch exactly) is "Ready to go, $n?..."
  Fixed.
- **Quests 329 + 622**: `叛軍營地` (mutineer camp) used inconsistently with the same row's own
  other fields and the corpus-wide established term `反抗軍營地` (resistance camp, 12 other
  occurrences) — fixed both.
- **Quest 168 investigated, found correct as-is**: initially looked like it might share
  quest 167's Thistlenettle-naming issue, but its own wowhead page and English source both
  match the DB exactly (`薊草`) — no fix needed. This is the case that led to the "NPC's own
  page, not quest prose" lesson above: quest 167's `希斯耐特` (not 168's `薊草`) was the actual
  outlier once NPC 656's own page was checked directly.

After this second pass, remaining diffs were manually confirmed as either wowhead's own
phrasing quirks (non-standard `$N`/`$n` case, abbreviated place/race names, punctuation
width) or legitimate creative-but-accurate paraphrase (the Nesingwary hunting chain 185-197
in particular — DB's narrative per chain-step was cross-checked against the true English
`QuestDescription` and matches the story beats even where wowhead's fetched text is a
shorter generic line).

### Batch 3 (341–540) fixes log

Highest bug density of any batch so far (118/193 quests flagged, many with multiple issues).
Applied the numeric-count-audit script from the start this time (catches count errors
regardless of whether the diff tool also flags the field), which immediately found 7 clear
mismatches plus several quests where Details/Objectives were **completely wrong content**
(same "content-swap" class as batch 2's 218/313/182), not just wrong counts.

**Content-swap bugs** (verified against real English source):
- **Quest 418** (`塞爾薩瑪血腸`): DB asked for 8 bear meat only; real quest needs 3 bear meat +
  3 boar intestines + 3 spider ichor. DB's own Details even said "I only need bear meat,
  everything else is prepared" — directly contradicting the real 3-item requirement.
- **Quest 432** (`該死的穴居怪!`→`該死的石齶怪!`): DB asked to kill 8+8 of two different
  Rockjaw trogg types; real quest (for Foreman Stonebrow) is 6 of one type only.
- **Quest 433** (`公僕`): DB's whole Details/Objectives was about delivering "Recall Runes to
  7 trapped miners" — real quest (for Senator Mehr Stonehallow) is killing 10 Rockjaw
  Bonesnappers, completely different mechanic.
- **Quest 416** (`補鼠行動`→`逮捕狗頭人`): wrong questgiver NPC (`巡山人雷矛`→should be
  `巡山人卡德雷爾`, confirmed via `creature_template_locale`) and wrong location (`東邊的銀泉
  礦坑`→`塞爾薩瑪北邊的山腳下`) — looks like it was cross-contaminated with quest 307's
  content (same NPC/mine that 307 legitimately uses).
- **Quest 459** (`惡魔小偷`→`森林保衛者`): DB was about retrieving Tarindrella's stolen
  beans/water/bag; real quest is collecting 8 Fel Moss for her — unrelated mechanic, same
  NPC.

**Truncated Objectives** (DB stopped after the first sentence, dropping the actual
turn-in/kill instruction — found in 358, 408, 409, 417, 455, 474, 483, 486, in addition to
batch 2's 279/290):
- 358: missing "bring 8 Embalming Ichors to Magistrate Sevren."
- 408: missing "kill Captain Dargol, bring his skull to Magistrate Sevren."
- 409: missing "summon and kill Lillith Nefara, return to Gunther."
- 417: missing "bring the claw and journal to Pilot Hammerfoot."
- 455: missing the entire "kill 8 Dragonmaw Scouts and 6 Dragonmaw Grunts" clause.
- 474/483/486: each missing the final "bring it to/return to <NPC>" sentence.

**Count mismatches** (7, found by the numeric-audit script): 356 (missing trailing sentence,
not a pure count issue but caught by the same check), 376 (4→6, also fixed wrong measure
words `只`/`張`→`隻`), 384 (4→6), 412 (6→8 both items, plus wrong item name `協動齒輪`→
`自適應齒輪` matching `item_template_locale`, plus Title itself named a non-existent item —
fixed Title to `自動淨化器`, the machine name the Details text already used), 456 (3→4),
457 (6→5) — note wowhead's own fetched counts for 456/457 were themselves wrong (7+4 and
7+7) relative to the true English source (4+4 and 5+5); used the English counts.

**Proper-noun fixes** (verified individually against `creature_template_locale` /
`item_template_locale` / the NPC's or item's own wowhead page, per the lessons above):
- `索爾曼`→`薩爾曼` (Thurman Agamand, quests 354, 362)
- `維沙克公爵`→`維沙克領主` (Lord Wishock, quest 397)
- `蒼白的格瑞姆森`→`白毛狼人格瑞姆森` (Grimson the Pale, quest 424 — despite DB's version
  reading as more literal, the official name includes "worgen")
- `達拉爾·道恩維沃爾`→`達拉爾·織曦者` (Dalar Dawnweaver — wowhead's quest-page transliteration
  was the inconsistent one here; `creature_template_locale` confirms `織曦者`) — 7 occurrences
  across the Dalar Dawnweaver quest chain (421-424)
- `高階執行官達薩利亞`→`高級執行官達薩利亞` and `高階執行官哈德瑞克`→`高級執行官哈德瑞克`
  (18 + 4 occurrences) — but explicitly **not** touching `高階執行官瑪弗倫`/`安賽姆`/`羅思`,
  since those three are officially `高階` per their own `creature_template_locale` records,
  even though it looks inconsistent with Hadrec/Darthalia. Base data itself is inconsistent
  here; each NPC verified individually, not assumed.
- `烏索爾`→`烏薩爾`, `德魯爾`→`德盧爾`, `託格薩`→`托格薩` (Ursal the Mauler, Drull, Tog'thar —
  quests 486, 498)
- Stray `$C` (class) token where the source has no class-token at all, just a generic noun —
  found 3 more instances beyond batch 2's quest 167 (quests 388 `盜賊`, 505 `盜賊組織`)

**Project-wide systemic sweeps** (triggered by batch-3 findings):
- **`天災軍團`→`天譴軍團`** (wrong term for "the Scourge"; verified via quest 428's wowhead
  page; corpus already predominantly used the correct term, this was the minority error):
  63 occurrences.
- **`祈倫托`→`肯瑞托`, then reverted.** Initially "fixed" based on quest 422's wowhead page,
  which showed `肯瑞托` — but that's a single quest's prose, not canonical. The user pointed
  to the *faction's own page*, `wowhead.com/wotlk/tw/faction=1090`, which is unambiguous:
  `祈倫托`. Reverted the full sweep (19 occurrences back to `祈倫托`) — the corpus's
  pre-existing majority usage (13 of 16) was right all along. **`肯瑞托` is in fact the zhCN
  (Simplified Chinese, mainland) translation of "Kirin Tor", not a WotLK-era zhTW variant at
  all** — this is a zhCN-leak error of exactly the kind STATUS.md's ground-truth glossary
  section already warns about (cf. `北風苔原`→`北風凍原`, `諾森德`→`北裂境`), just one my
  quest-page-only check didn't catch. Extends the "check the canonical record, not quest
  prose" rule (Fifth lesson above) to factions: use `wowhead.com/wotlk/tw/faction=<id>`, not
  a quest page, for faction/organization names — and stay alert for zhCN-leak terms
  specifically, not just generic wowhead inconsistency.

**False positives correctly rejected** (worth noting so future batches don't re-litigate):
- Quest 464 `龍喉旌旗` vs wowhead's `龍喉戰旗` — `item_template_locale` confirmed DB's original
  was correct; wowhead's quest-page prose was the outlier.
- Quest 470 `米奈希爾港` — wowhead's own fetch had a typo (`米奈希望港`), DB was already right.
- Quest 424 `深埃連礦坑` (Deep Elem Mine) — wowhead's `埃利姆礦坑` drops "Deep", DB was more
  literal/correct.
- Quest 423 `黑暗之魂鐐銬` — `item_template_locale` confirmed this over wowhead's `魔魂鐐銬`.
- Quest 447/451 `法拉尼爾` title `藥劑大師` — `creature_template_locale` confirmed this over
  wowhead's `大藥劑師`.
- Quest 426 `凹槽肋骨` — `item_template_locale` confirmed this over wowhead's `鋸齒肋骨`.
- Quest 451 `湖岸蠕行者苔蘚` — `item_template_locale` confirmed this over wowhead's `湖岸爬行者
  苔蘚` (a different, unrelated creature-name pattern from quest 275's real Fen
  Creeper/`沼地爬行者` fix in batch 2 — don't conflate the two).
- Quest 379 `首席工程師比格維茲` — kept the batch-2-established correct form (no fabricated
  first name) even though wowhead's quest-page text for 379 itself included the fabricated
  `沙克斯`.

### Batch 4 (541–740) fixes log

Numeric count-audit ran proactively from the start this time (only 1 real hit — quest 642's
truncated Objectives — the rest were regex false positives from Chinese numerals and
implied-singular "a/an"). Most of this batch's real work was the **Troll/Ogre terminology
system**, triggered by a large cluster of `巨魔`/`食人妖`/`食人魔` disagreements with
wowhead across the Grom'gol/Zul'Gurub and Hammerfall/Boulderfist quest chains.

**Troll/Ogre terminology (see `[[feedback-zhtw-troll-ogre-terms]]` in agent memory for the
full rule)**: established via direct user correction that this project's zhTW convention is
**Troll = `食人妖`** (never `巨魔` — that's the zhCN/mainland term) and **Ogre = `食人魔`
normally, but `巨魔` is also a legitimate zhTW term for specific Ogre clans** (confirmed via
`creature_template_locale`: `Gordunni Ogre`→`戈杜尼巨魔`, `Boulderfist Ogre`→`石拳巨魔` — both
correct as-is). This is a *per-clan* fact, not a blanket rule — do not sweep `巨魔` without
checking the specific clan first.
- Fixed (confirmed Troll, `巨魔`→`食人妖`): Zul'Gurub trolls and Gri'lek (troll hero) in
  quests 581, 629, 638, 639; Bloodscalp (`血頂`) in 581, 596; Witherbark (`枯木`) — 24
  occurrences project-wide.
- Fixed (confirmed Ogre, DB's `食人魔`→official `巨魔`): Boulderfist (`石拳`) — 17 occurrences
  project-wide (676, 677, 680, and others sharing the term).
- Left untouched: ~150 other `巨魔` occurrences elsewhere in the corpus (Bloodmaul, Mo'grosh,
  Dunemaul, Gordunni, and unidentified others) — not verified per-clan, do NOT assume these
  need fixing either direction without checking `creature_template_locale` for that specific
  clan first.

**Other proper-noun fixes**: `密斯萊爾`→`密斯賴爾` (Myzrael — DB's own text was internally
inconsistent, 17 occurrences unified to the majority-correct spelling), `地精`→`哥布林` in
quests 705 and 713 (both explicitly confirmed "goblin" in the English source — a Badlands
pearl-diver and Bro'kin in Alterac), `巨魔祭司托爾甘`→`食人妖祭司托爾甘` (quest 640, Tor'gan —
resolved by process of elimination/thematic fit after his own wowhead NPC page gave no race
signal; lower confidence than the other fixes here, flag for re-check if evidence emerges).

**Truncation**: quest 642's Objectives was missing its second sentence (delivery
instruction), same pattern as batches 2-3.

**False positives correctly rejected — wowhead's own fetch was wrong, not DB** (a notably
high count this batch; always verify against the real English source before trusting
wowhead's phrasing, per the established methodology):
- Quest 640: DB's "5 Sigil Fragments" count was correct (matches English exactly); wowhead's
  "11" was wrong — the Details text's "split into eleven pieces" refers to the *total*
  symbol across the whole quest chain, not this specific quest's ask, so it wasn't even a
  real contradiction within DB's own row.
- Quest 679: DB's "7 Boulderfist Shaman and 3 Boulderfist Lords" was exactly right;
  wowhead's "15 and 10" was wrong.
- Quest 706: DB's `黑色幼龍之心` ("Black **Drake's** Heart" — drake = young dragon) was
  correct; wowhead's `黑龍之心` dropped "young" entirely.
- Quests 717, 732, 733: DB's `食人魔` (Ogre) was correct per English source ("the ogres...");
  wowhead's `巨魔` was wrong for these specific Lethlor Ravine ogres.
- Quest 704 (and 738, 739): DB's `阿戈莫德` ("Agmond") was correct; wowhead's `埃格蒙德` was a
  wrong name entirely.

### Batch 5 (741–940) fixes log

- **Quest 746**: item name truncation fix pulled wowhead's verbatim text, but that text named
  the item `勘察員的鋤頭`; `item_template_locale` (4702) confirms the real name is
  `勘察員的十字鎬` — fixed, keeping the verbatim count/sentence but correcting the embedded
  item name.
- **Quest 871**: wowhead's `鋼鬃野豬人` (Razormane Quilboar) was correct and DB's own Details
  field said `剃鬃` — fixed Details to match, confirmed via `creature_template_locale`.
- **Quest 865**: an `Edit` call corrupted the row structure (stale trailing text + duplicated
  Objectives) — caught immediately by the field-count validator, reconstructed the tuple.
- **Quests 788, 789, 792**: applied wowhead's counts (8→10, 8→10, 8→12) without individually
  checking each against `quest_template`'s real `LogDescription` — all three wrong; true
  count was 8 in every case, DB's original was already correct. Reverted all three after user
  caught 789. Triggered a widened audit across the full 100–940 range so far (14 candidates,
  all confirmed false positives — org names with digits, ratios, percentages, spelled-out
  numbers).
- **False positives correctly rejected** (wowhead's own fetch was wrong, not DB): quest 640
  (count), quest 679 (count), quest 706 (`黑色幼龍之心` vs wowhead's `黑龍之心`, dropped
  "young"), quests 717/732/733 (`食人魔` Ogre correct, wowhead's `巨魔` wrong for these
  specific Lethlor Ravine ogres), quest 704/738/739 (`阿戈莫德` correct, wowhead's
  `埃格蒙德` was a different name entirely).

### Batch 6 (941–1140) fixes log

Introduced `diff_quest_text.py --strict` (punctuation/$B/$N-case normalized diff) partway
through — cut the flagged-quest count from 148/194 to 88/194 by filtering out wowhead
rendering quirks, making real content bugs much easier to spot in a large batch.

**Content-swap bugs** (Details/Objectives replaced with a different quest's content,
verified against `quest_template`'s real English source):
- Quest 1016 (`收復密斯特拉湖`→`元素護腕`): DB was entirely about killing water elementals at
  Lake Mystra; real quest is collecting Intact Elemental Bracers and using a divining scroll.
- Quest 1012 (`瘋狂的德魯伊`): DB's backstory (Horde corrupting the Heart of the Forest) was
  wrong; real quest is about the Forsaken poisoning the Dor'danil druids. Objectives was also
  missing the turn-in clause ("...then return to Kayneth Stillwind in Forest Song").
- Quest 1045 (`萊恩的淨化`): Details/Objectives were about a wizard's wand and killing
  furbolgs generically; real quest is killing Ran Bloodtooth + 4 guards and collecting his
  skull, returning to Krolg.
- Quest 1007 (`古代雕像`→`遠古雕像`): Details had a fabricated "I am a species archaeologist"
  sentence not in the English source, and Objectives asked for 10 statuettes when
  `RequiredItemCount1=1` (English source is singular: "Bring **the** Ancient Statuette").
- Quest 971: Objectives sent the player to the wrong turn-in NPC/location (`哨兵受訓員伊薩拉`
  at a camp) instead of the real target, `葛利·硬骨` in Ironforge's Forlorn Cavern (same NPC
  as quest 968, confirmed via `creature_template_locale` 2786).
- Quest 1023 (`萊恩的淨化`): Details named the wrong NPC (`奧蘭迪爾`) as the gem's source and
  said "in the tentacles' hands" (`觸鬚的手裡`) instead of "murlocs" (`魚人`); real source is
  Raene, per English "Raene mentioned it being in the area... Perhaps the murlocs have it."

**Quest-chain title question** (asked user, resolved): quests 1023/1026/1027/1045 all share
the literal English `LogTitle` "Raene's Cleansing" (a repeated chapter title, confirmed via
wowhead showing the same zhTW string for all four) but DB had given each step its own
distinct descriptive title. User chose to match wowhead literally — renamed all to
`萊恩的淨化`. Note 1045's title is about *Raene Wolfrunner* (chain namesake), not *Ran
Bloodtooth* (the creature killed in that specific quest) — the two are different NPCs whose
English names happen to sound similar (also see next point).

**Name-conflict override of `creature_template_locale`**: entry 3696 ("Ran Bloodtooth") gives
`蘭恩·血牙`, but the user directly corrected this to `萊恩·血牙` — confirmed by quest 1046's
own pre-existing (untouched) text, which already used `萊恩·血牙` consistently alongside
`萊恩·狼行者` in the same row. This is a concrete instance of the established rule that
`creature_template_locale` is *best-available*, not infallible — see
`feedback_zhtw_ground_truth_priority` in agent memory.

**Terminology fixes verified against ground-truth tables, then swept project-wide**:
- `卡利姆多`→`卡林多` (Kalimdor) — **138 occurrences** in the current file, **200 total**
  across pending_db_world. Verified via `Map_zhTW.tsv` (DBC ground truth, Map ID 1) — the
  only fully unimpeachable source in the hierarchy. This overturned an initial assumption
  that wowhead's `卡林多` was the error; it was DB's `卡利姆多` that was wrong all along.
- `大地之環`→`陶土議會` (Earthen Ring faction) — **82 occurrences**. Verified via
  `Faction_zhTW.tsv` (DBC ground truth, Faction ID 979). `大地之環` is a literal-sounding but
  incorrect translation; `陶土議會` is Blizzard's actual client string.
- `扎瑪`→`札瑪` (Apothecary Zamah, creature 3419) — 6 occurrences.
- `聖者圖希克`→`賢者圖希克` (Sage Truthseeker, creature 3978) — matches "Sage", not "Saint".
- `高等審判官懷特邁恩`→ replaced DB's `大檢察官懷特邁恩` (creature 3977; "High Inquisitor",
  not "Grand Inquisitor") — 2 occurrences (quests 1048, 1053). Note wowhead's own fetch for
  1053 showed `高階審判官` (a third variant) — neither wowhead occurrence was fully reliable;
  `creature_template_locale` settled it.
- `地精`→`哥布林` for confirmed-Goblin content in the Thousand Needles/Gadgetzan racing
  questline (quests 1099, 1110 dup-word, 1106, 1115, 1117, 1121) — but **not** a blanket
  sweep: this questline genuinely mixes Gnome (`地精`) and Goblin (`哥布林`) NPCs/factions
  (e.g. quest 1093's "Goblin company hired a gnome!", quest 1114 "Delivery to the Gnomes",
  quest 1120 "Get the Gnomes Drunk" vs quest 1121 "Get the Goblins Drunk"), so each occurrence
  was checked individually against its own quest's English source before changing.
- `菲尤拉·長耳`→`菲歐拉·長耳` (Fiora Longears, creature 4456) — also fixed quest 1132's wrong
  turn-in city (`塞拉摩`→`奧伯丁`; confirmed via English "docks at Auberdine in Darkshore" —
  she legitimately relocates to Theramore later in the same chain at quest 1135, so that
  quest's `塞拉摩` was correctly left alone).
- Quest 1131: Objectives dropped Melor Stonehoof's surname (`梅洛`→`梅洛·石蹄`).
- Quest 1101 (`卡爾加·刺肋`→`剃刀沼澤的乾癟老太婆`): title, Details, and Objectives rebuilt
  from wowhead's verbatim text (matches English "The Crone of the Kraul" framing); also fixed
  a `她的的徽章` double-character typo and `徽章`→`大勳章` to match English "Medallion".

**False positives correctly rejected**: quest 963 (`曦奔` confirmed correct via
`creature_template_locale` 3667, wowhead's `晨路` was the outlier), quest 1096 (`東北方`
confirmed correct against English "Northeast of here", wowhead's `西北方` was wrong), quest
1078 (`晶化鱗片` more literal/correct than wowhead's reordered `鱗片晶體`), quest 1009
(`佐拉姆` established-correct per corpus-wide usage, wowhead's one-off `左拉姆` was the
outlier), quest 1014 (`達拉爾·織曦者` already correct per the batch-3 finding; wowhead's
`道恩維沃爾` is the same known inconsistency).

### Batch 7 (1141–1340) fixes log

Highest false-positive rate yet on my *own* proposed fixes — several race/rank-term guesses
were wrong and caught by the user before being applied, not by the established methodology.
Recorded below so future batches don't re-litigate.

**Content-swap bugs** (verified against `quest_template`'s real English source):
- Quest 1218 (`舒心草`→`沼澤青蛙腿`): Details/Objectives were entirely about collecting an
  herb; real quest (confirmed via English `LogDescription` + `RequiredItemId1`=33202 "Marsh
  Frog Leg") is bringing 10 Marsh Frog Legs to "Swamp Eye" Jarl. Title/Details/Objectives
  rebuilt; kept the row's own already-correct EndText (`女巫嶺`/`塺泥沼澤`) unchanged.
- Quest 1221 (`藍葉薯`): Objectives truncated to the first sentence only, dropping the
  crate/gopher/command-stick/turn-in instructions. Restored full text — but corrected
  wowhead's `棘齒城` (Ratchet) back to `貧瘠之地` (Barrens), since the same row's own EndText
  and the English `QuestCompletionLog` both say Barrens; wowhead's location was the outlier.
- Quests 1199 + 1200 (Twilight's Hammer/Aku'Mai chain): Objectives (and 1200's Details closing
  line) named a fabricated NPC/location (`黑澗營地的哨兵阿露溫`, `黑澗營地的阿謝蘭‧北木`) that
  appears nowhere else in the whole corpus, while each row's own EndText already correctly
  said `達納蘇斯` + the right NPC (matches English "Argent Guard Manados"/"Selgorm in
  Darnassus" exactly). Fixed Objectives/Details to match the row's own EndText.

**Rank/title fixes** (verified via `creature_template`'s literal in-game `name` field, the
strongest available signal short of a locale table):
- `維米斯隊長`→`維米斯上尉` (17×): creature 4944's in-game name is literally "Captain Garran
  Vimes" — confirmed both by this and by the user checking wowhead quest=27264 directly.
  Note: `雷瑟上尉` (7×) was **left unchanged** — I initially proposed swapping this too since
  English calls him "Lieutenant Paval Reethe" in quest titles, but the user corrected this:
  wowhead's own quest=27264 page confirms both NPCs are called `上尉` in the zhTW client, and
  creature 4980's in-game name is plain "Paval Reethe" with no rank at all, so the flavor
  text's `上尉` isn't contradicted by anything. Lesson: a quest-title's English rank word isn't
  automatically the client's zhTW rank word — check the NPC's own in-game name/a dedicated
  quest page before swapping ranks project-wide.
- Quest 1219: Objectives had genericized `某個上尉` (some captain), dropping both the name and
  getting the rank wrong. Creature 23951's in-game name is literally "Lieutenant Aden" —
  restored to `亞汀中尉`.
- Quests 1166, 1170, 1173 (`莫格穆洛克大王`→`莫格穆洛克主宰`, 5×): English title is literally
  "Overlord Mok'Morokk"; `主宰` is the corpus's existing convention for "Overlord" elsewhere
  (e.g. `主宰卡魯什`). User confirmed `主宰` is correct.

**Proper-noun fixes**:
- Quest 1144: `紅葉薯`→`藍葉薯` (typo — same Blueleaf Tuber item as quest 1221, confirmed via
  `RequiredItemId`/item_template "Blueleaf Tuber").
- Quest 1152: `石爪小徑`→`深爪小徑` — English says "Talondeep Path," a distinct place from
  "Stonetalon Mountains" (`石爪山`, correctly used two words later in the same sentence); DB
  had conflated the two similarly-named places. Also `連線`→`連接` for "the tunnel that
  connects" the two zones — confirmed via wowhead's own quest=1152 page (`連線` reads as a
  network/telecom term in Chinese, not physical connection).
- Quest 1179: Title `防撞頭盔`→`銅栓兄弟` (English LogTitle is literally "The Brassbolts
  Brothers," matching the established chain title in quests 1190/1191) and `千針林大峽谷`→
  `千針石林大峽谷` (typo, dropped `石`). Note: I also proposed changing `地精兄弟`→`哥布林兄弟`
  in the same row, assuming the Brassbolts brothers were Goblins from lore — **wrong**, the
  user caught this: the English text literally says "a couple of gnome brothers," so `地精`
  (this project's Gnome term) was already correct. Lesson: don't infer race from
  half-remembered lore when the quest's own English text states it directly — check first.
- Quest 1240 (`巨魔巫醫`→`食人妖巫醫`, 3× incl. Title): Kin'weelay is a Darkspear troll
  (`暗矛`); per the established Troll/Ogre convention (`[[feedback-zhtw-troll-ogre-terms]]`),
  Troll = `食人妖`, confirmed again via `ChrRaces_zhTW.tsv` (race 8 = `食人妖`).
- Quest 1339: DB's title/Details/Objectives all called the questgiver `巡山人卡爾·雷矛`, but
  creature 1343's in-game name is plain "Mountaineer Stormpike" — no "Karl" anywhere.
  Fabricated first name removed (3× in-row) → `巡山人雷矛`.
- Quest 1288: stray trailing `*` on the title (`維米斯的報告*`→`維米斯的報告`) — same class of
  cosmetic corruption as batch 2's quests 171/415. Left the skip-listed sibling quest 1289's
  identical `*` alone (out of scope, already skip-listed as `<nyi> Vimes's Report`).
- Measure-word fix (quests 1147, 1148): `只`→`隻` for animal counters (Silithid creatures),
  continuing the convention established in batch 2's quest 376.
- Middle-dot character fix (quests 1141, 1143, 1275): DB used `‧` (U+2027) as a name
  separator where the corpus's dominant convention (4714 vs 970 file-wide) is `·` (U+00B7);
  fixed the 3 in-batch occurrences only, not a full corpus sweep.

**Project-wide systemic sweep**:
- `暗夜精靈`→`夜精靈` (Night Elf), **251 occurrences across 7 files**. Confirmed directly by
  the user: `暗夜精靈` is the zhCN (mainland) term; `夜精靈` is correct zhTW, matching
  `ChrRaces_zhTW.tsv` (race 4 = `夜精靈`) exactly — this DBC ground-truth file had been sitting
  unused as a check for race names until this batch.

**False positives correctly rejected** (wowhead's own fetch was wrong, or DB was already
right; verified against the real English source or in-game data before touching anything):
- Quest 1166/1168/1169/1170 (Brackenwall ogre chain — Mok'Morokk, Tharg, Draz'Zilb): DB's
  `食人魔` was correct throughout (English QuestDescription explicitly says "me smart ogre",
  "ogres not good at running", etc.); wowhead's occasional `巨魔` was wrong, consistent with
  the batch-4-established wowhead Ogre→巨魔 mistranslation pattern.
- Quest 1258: DB's `螃蟹` (crab) was correct despite the item being named "Pristine *Crawler*
  Legs" — the English QuestDescription itself calls it "the shelled leg of a giant **crab**",
  so "Crawler" is just the item name's own flourish, not a distinct creature.
- Quest 1318 (Gordok ogres, Dire Maul): DB's `戈多克食人魔` was correct — confirmed by 9
  corpus-wide occurrences of the same term (including a near-duplicate quest 7703 with
  identical title/body), overwhelming wowhead's one-off `戈多克巨魔` for this quest.
- Quest 1322: DB's count of 5 Acidic Venom Sacs was correct (matches
  `RequiredItemCount1`=5 exactly); wowhead's page said "6" but its own item icon showed
  "(5)" — a wowhead display inconsistency, not a real content disagreement. Also DB's extra
  "Darkmist Cavern, northwest of the village" clause (missing from wowhead's fetch) is
  genuinely in the English `QuestDescription` — DB was more complete, not wrong.
- Quest 1168: DB's `灰尾龍人` and generic `守衛` (vs wowhead's `灰尾龍裔`/`逆鱗守衛`) confirmed
  correct — creatures 4328/4329/4331 (`Firemane Scalebane/Scout/Ash Tail`) are all
  `type=2` (Dragonkin) in `creature_template`, and the corpus uses `龍人` for Dragonkin-type
  creatures dozens of times elsewhere (Nefarian's dragonkin, chromatic/black dragonkin, etc.)
  vs a single one-off `龍裔`; in-game creature data + corpus convention settle this, no fix
  needed. `守衛` for "Scalebane" also left as-is: "Scalebane" is a generic elite-rank suffix
  reused across a dozen unrelated dragonkin (Green/Red/Blue/Cobalt/Nightmare Scalebane, etc.),
  not a unique proper name, so DB's generic rendering isn't wrong.
- Quest 1177 (Mudcrush Durtfeet, `餓！`): fully adopted wowhead's text per user request — the
  user clarified that in this project's convention `巨魔` is *also* a legitimate zhTW term for
  Ogre (not just Troll = `食人妖`), consistent with the established
  `[[feedback-zhtw-troll-ogre-terms]]` rule, so wowhead's `阿泥是大巨魔` does not conflict with
  the English "Mud big ogre" after all. Title/Details/Objectives/EndText replaced with
  wowhead's `碎泥·杜特非`/`阿泥`/`巨魔`/`沼鰭小魚` throughout.
- Quest 1272 (`[Finding Reethe <CHANGE INTO GOSSIP>]`): confirmed unreachable — no
  `creature_queststarter`/`questender`, `gameobject_queststarter`/`questender`, or
  `game_event` link anywhere in the DB (same signature as already-skip-listed 12021).
  Added to `skip-list.tsv`.

### Batch 8 (1341–1540) fixes log

Highest bug density since batch 3 (108/191 quests flagged) — the Desolace centaur/Stonard
storyline and the Orgrimmar shaman "Call of the Elements" chain both turned out to be dense
with proper-noun drift. `creature_template`'s literal in-game `name` field (English) proved
useful as a first-class ground-truth check this batch — several disputes were settled just by
confirming the exact spelling/title in the creature's own `name` column, no locale table
needed. Also several of my own "false positive, leave alone" calls this batch were wrong and
corrected by the user — see the note at the end of this section on when to defer to wowhead.

**Content-swap / truncation fixes** (verified against `quest_template`'s real English source):
- Quest 1420 (`向赫格拉姆報到`): dropped title — creature 1442's in-game name is literally
  "Helgrum **the Swift**"; restored `迅捷的赫格拉姆` throughout (1420, 1423, 1425).
- Quest 1466 (`尋物公司的委託`): the English source is actually about **Doomwarder** (creature
  4677/4680/4683), a different creature from "Doomguard" — confirmed correct as `末日守衛`
  after checking in-game (matches the corpus's dominant spelling for the *unrelated* Doomguard
  creature too, so this one Chinese term now covers two different English creatures — flagged
  here in case it ever needs disambiguating). Also fixed an internal inconsistency: DB's own
  Details already said `噬法魔犬`/`地獄犬` inconsistently for the same creature (Felhound,
  creature 6010) — wowhead's own NPC page (`npc=6010`) shows `惡魔犬`, which outranks same-row
  internal consistency per the established priority order; unified to `惡魔犬`.
- Quest 1491 (`智慧飲料`): Objectives truncated to "收集6份哀嚎香精。", dropping the turn-in
  clause — restored using the row's own already-correct EndText location (`貧瘠之地`) over the
  English `LogDescription`'s "Ratchet" (same Ratchet-is-inside-Barrens precedent as batch 7's
  quest 1221).
- Quests 1380 + 1381 (`赫魯薩可汗`→`赫蘭薩可汗`): same-row proper-noun inconsistency — DB's own
  two rows used **three different spellings** (`赫魯薩`, `薩魯赫`, `赫蘭薩`) for a single NPC,
  confirmed as "Khan **Hratha**" (creature 5402); unified to the spelling wowhead already used
  consistently and that DB's own rows used twice already (`赫蘭薩`).

**Proper-noun fixes**:
- `卡達`→`卡塔爾` (5×, quests 1422/1426/1428): creature 5593's in-game name is "Katar".
- `朗格爾斯`→`朗格茲` (3×, quests 1423/1425): creature 5393's in-game name is "Quartermaster
  **Lungertz**" — `茲` is phonetically closer to the "-tz" ending than `爾斯`.
- `盎格庫爾`→`盎格庫` (quest 1373): creature 5622's in-game name is plain "Ongeku" — no
  extra trailing syllable.
- Quest 1531 + 1532 title `空氣的召喚`→`風的召喚`: English LogTitle is "Call of Air", but the
  parallel quest titles for the other three elements in this same chain are all "X的召喚" using
  the classical element name (`大地的召喚`/水/火), not the literal gas "空氣" — matches
  wowhead and the chain's own established pattern. Also fixed the questgiver's name: creature
  5905 is "Prate **Cloudseer**", not "White Cloud" (`普拉特·白雲`→`普拉特·雲眼`).
- `粗石英`→`劣質石英` (item 6656, "Rough Quartz", 4× in quests 1518/1521): initially assumed
  DB's literal `粗石英` was correct and wowhead's `劣質石英` was a quality-vs-texture
  mistranslation — wrong, user corrected this after checking the item DB; `劣質石英` is right.
- `半人馬部族`/`瑪格拉姆部族`/`吉爾吉斯部族`/`科卡爾部族`→`...氏族` (17× within this batch's
  Desolace centaur questline only, quests 1360–1373): initially left alone as "DB's dominant
  corpus convention" since `部族` has 170 occurrences in this file — but nearly all of those
  are *other, unrelated* tribes (Zandalar trolls, Wildhammer dwarves, Bristleback furbolgs,
  etc.), not evidence for the Centaur tribes specifically; user said to match wowhead's `氏族`
  here. Scoped the fix to just this questline's occurrences, not the other 150+ unrelated
  `部族` uses elsewhere in the file.
- `碎骨`→`碎骨者` (Maurin Bonesplitter, 8× within quests 1433/1435/1480/1481/1482 only): same
  correction as above — DB's bare `碎骨` being the corpus majority doesn't make it right for
  this specific NPC; wowhead's `碎骨者` matches "Bonesplitt**er**" literally.
- `費澤魯爾`→`費澤盧爾` (Fel'zerul, 6×) and `甘魯爾`→`甘盧爾` (Gan'rul Bloodeye, 11×): both are
  homophone-character spelling choices (魯/盧) with no `creature_template_locale` entry to
  settle them one way or the other — per the user's guidance, defaulted to wowhead's spelling
  when there's no zhTW-locale ground truth to check against, rather than keeping DB's version
  by default.

**Project-wide systemic sweeps**:
- `幽靈崗哨`→`鬼旅崗哨` (Ghost Walker Post) — **16 occurrences** across the corpus. Verified via
  `AreaTable_zhTW.tsv` (DBC ground truth, area id 597 = `鬼旅崗哨`) — same class of fix as
  batch 6's `卡利姆多`→`卡林多`.
- `阿塔萊巨魔`/`阿塔萊的巨魔`→`阿塔萊食人妖`/`阿塔萊的食人妖` (4 occurrences fixed, was already
  split 4:2 in the corpus itself before this fix). Atal'ai are Trolls; per the established
  `[[feedback-zhtw-troll-ogre-terms]]` rule, Troll = `食人妖` has **no per-tribe exceptions**
  (unlike Ogre, where `巨魔` is legitimate for specific confirmed clans) — this settles the
  corpus's own pre-existing inconsistency rather than picking a side arbitrarily.

**Lesson on ground-truth priority (updated this batch)**: "DB's existing text is the corpus
majority" is *not* by itself a reason to reject wowhead's version — same-row/same-file
majority only counts as a signal when it's actually about the *same* proper noun. Before
citing "corpus convention" as a reason to keep DB's wording, check that the majority
occurrences are really the same tribe/NPC/item, not just a shared generic word (`部族`,
`碎骨`) reused across many unrelated names. When no `_locale` table exists for a name and
same-row consistency doesn't apply either, default to wowhead's rendering rather than DB's,
absent a specific reason to prefer DB.

**False positives correctly rejected** (wowhead's own fetch was wrong, or DB was already
right):
- Quest 1424: DB's count of 5 Atal'ai Artifacts was correct (`RequiredItemCount1`=5, matches
  English "gather 5 Atal'ai Artifacts" exactly); wowhead's "10" was wrong.
- `瑪烏林`(vs wowhead's `莫林`) for creature 4498 "**Maurin** Bonesplitter": DB's transliteration
  is phonetically closer to the confirmed English name; wowhead's version was the outlier —
  note this is about the *given name* specifically, unlike the `碎骨`→`碎骨者` surname fix above.
- Quest 1526: `火焰之魂`/`火焰之靈體` (Minor Manifestation of Fire) and quest 1516's
  `地獄捕獵者`/`惡魔捕獵者` (Felstalker, creature 3102): no locale table exists for either
  creature and no corpus precedent favors one rendering over the other — left alone.

## Known pre-existing issues found but not yet fixed (out of scope so far)

- `quest_template_locale` in `rev_1783688290124463491.sql` has duplicate rows (two
  DELETE+INSERT pairs for the same ID) for quest IDs **1241, 1250, 1264** — needs
  dedup, unrelated to the batches above.
- Quest 170 uses `石齶穴居怪`/`石齶` for what should likely also be `碎石怪`/`碎石穴居人`
  (Stonesplinter/Rockjaw trogg family) but wasn't part of the confirmed sweep — needs its
  own creature-entry verification (may be a genuinely different trogg family, "Rockjaw" vs
  "Stonesplinter" — don't assume, check `creature_template` for the exact English name used
  in quest 170's `RequiredNpcOrGo`).

## Tools

Reusable scripts live in `scripts/` (generic, not batch-specific):

- `fetch_quest_text.py` — fetches wowhead-tw quest text for IDs listed in
  `$ZHTW_SCRATCH/wowhead_final_zh.txt` (one ID per line), writes to
  `$ZHTW_SCRATCH/quest_text_extracted.jsonl` (resumable — tracks done IDs, safe to re-run).
  A 194-ID batch takes ~8-10 minutes (2.5s/fetch); run it with Bash `run_in_background`.
- `diff_quest_text.py [--strict]` — diffs the fetched jsonl against pending_db_world's
  `quest_template_locale`. Plain mode only normalizes `$N`/`$n` case (matches the pilot
  batch's tool). **`--strict` also drops `$B` breaks, normalizes punctuation width/style, and
  strips whitespace** — this filters out wowhead rendering quirks (established false-positive
  class, see Ground-truth priority above) and should be the first pass on any batch beyond
  ~100 quests; it typically cuts the flagged count by 30-40%.
- `audit_quest_counts.py <lo> <hi>` — cross-checks every number in Objectives+Details against
  `quest_template`'s real English `LogDescription`+`QuestDescription` for the given ID range.
  Run this proactively at the start of every batch (not just when a count diff is suspected)
  — it has caught real bugs the text diff missed. Expect false positives (ratios, percentages,
  digit-bearing org names, spelled-out numbers); verify each individually before fixing.
- `scan_missing_zhtw.py` — provides `extract_inserts()`/`unquote()`, the quote/paren-aware SQL
  tuple parser everything else is built on. Also useful standalone to re-check the
  missing-translation counts (should stay near-zero; a handful of pre-existing gaps in
  `quest_offer_reward_locale`/`quest_request_items_locale`/`item_template_locale` are a
  separate, already-tracked issue from STATUS.md's first pass, not this pass's scope).
- Field-count/duplicate validation: no standalone script, but the pattern (used after every
  batch) is:
  ```python
  rows = extract_inserts(TARGET, "quest_template_locale")
  bad = [r for r in rows if len(r) != 12]          # corrupted row structure
  dupes = [id for id, n in Counter(unquote(r[0]) for r in rows).items() if n > 1]
  ```
  Always run this plus `python3 apps/codestyle/codestyle-sql.py` after every edit batch.

A typical batch: set `ZHTW_SCRATCH`, write the ID range (minus skip-list) to
`wowhead_final_zh.txt`, run `fetch_quest_text.py` in the background, then run
`audit_quest_counts.py` and `diff_quest_text.py --strict` once the fetch completes, review
every flagged quest against the ground-truth priority order, apply fixes, re-run both checks
plus the linter/field-count validation, then update this file's Completed ranges table,
Fixes log, and this Next-batch pointer.

## Next batch

Not started. Resume from quest ID 1541 (batch 9, target range roughly 1541–1740) following
the same two-phase methodology, skipping any ID present in `skip-list.tsv`. 7,343 quest IDs
remain after batch 8 (see Total scope note above).
