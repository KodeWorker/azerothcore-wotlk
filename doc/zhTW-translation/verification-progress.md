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
   battlegrounds/maps. Also counts: a later expansion's official class page
   (`wowhead.com/tw/class=<id>`) when a WotLK-era English proper noun is the same concept a
   later expansion turned into a class (e.g. Demon Hunter) — the class's official name
   outranks corpus consistency even though the class doesn't exist yet in this era's content.
2. `creature_template_locale`/`item_template_locale`/`gameobject_template_locale` — best
   *available* reference for NPCs/items (no DBC coverage exists for these in this era), but
   not infallible; could itself carry the same scraping errors wowhead has. Two independent
   signals agreeing (e.g. this table + wowhead's dedicated NPC/item page) is stronger than
   either alone. Not automatically final either — see "user overrides" below.
3. A specific NPC's/item's own dedicated wowhead page (`.../npc=<id>`, faction page, etc.)
   — better than a quest page, still not as strong as #1 or #2.
4. A single quest's wowhead prose — weakest signal. Never trust it alone for a proper noun;
   Blizzard's own localization isn't perfectly self-consistent, and wowhead's scrape can
   introduce its own errors (including zhCN-leak terms like `肯瑞托`/`天災軍團`/`巨魔`).
5. DB's own pre-existing text — no special status; same-row internal consistency is a
   symptom to notice, never a tiebreaker against the sources above.

**Critical context**: the DB's zhTW text was majorly **OpenCC-converted from zhCN**
(simplified→traditional *character* conversion, not re-translation) — confirmed directly by
the user (batch 9). This means corpus-wide self-consistency is a much weaker signal than it
sounds: the whole corpus can share one zhCN-origin translation pass, so a systemic wrong term
can be 100%, or even a lopsided majority, self-consistent and still wrong (Kalimdor 138:0,
Mekkatorque 10:0, Demon Hunter 22:0 all turned out to be corpus-wide-consistent errors). When
wowhead disagrees with DB and there's no locale-table tiebreaker, lean toward wowhead somewhat
more than intuition suggests — but a pattern-based fix (grammar/idiom/orthography) still needs
per-instance verification before any sweep, never a blind regex replace
(`[[feedback-zhtw-no-blind-sweep]]`).

**User overrides**: `creature_template_locale` is best-available, not infallible — the user has
directly overridden it twice: Felhunter/Fel Hound (`地獄`→`惡魔`, semantic preference, applied
even across creature-identity lines) and Aurius (`奧里克斯`→`奧里爾斯`, phonetic preference).
Don't assume a locale-table match is unquestionable for a proper-noun transliteration when the
user has a specific judgment call to make.

**Working rules, condensed:**
- Read every bracketed field in a diff block (title/objectives/details) — a clean title diff
  does not mean the body is fine; several quests had Details/Objectives silently swapped
  with a different quest's content while only the title got noticed.
- Check same-row proper-noun consistency even when wowhead shows zero diff — a quest can be
  internally inconsistent without ever disagreeing with wowhead.
- Verify every kill/collect count against `RequiredNpcOrGoCount`/`RequiredItemCount`, or
  against the real English `LogDescription`/`QuestDescription` — every single time, even
  after a long streak of correct fixes. Watch for false-positive number matches: ratios
  ("10 to 1"), percentages, org names with digits ("SI:7"), spelled-out number words, Chinese
  numerals used stylistically for a digit that matches anyway.
- When replacing a field, use the verified source text verbatim rather than hand-patching
  just the wrong number/word — but still separately check any proper noun embedded in that
  verbatim text against its own canonical source.
- A title/rank shared by multiple NPCs (e.g. "High Executor") can be translated
  inconsistently across them in the base data itself — verify and fix per-NPC, never
  generalize a fix to "every NPC with this English title."
- A confirmed fix can resurface unfixed in a *later* batch's ID range that the original batch
  never touched — watch for familiar names/terms by recognition, not just diff flags; don't
  assume "already fixed" means "fixed everywhere."

Both phases run on the same small batch before moving to the next.

## Completed ranges (quest_template IDs)

| Range | Date | Fixes | Notes |
|---|---|---|---|
| 100–140 (excl. skip-listed 108, 137) | 2026-07-15 | 5 | Pilot batch. |
| 141–340 (excl. skip-listed 242, 259, 260, 316, 326, 327) | 2026-07-15 | ~40 targeted + 3 project-wide systemic sweeps (300+ occurrences) | Batch 2. Much higher hit rate than the pilot — several content-swap bugs where an entire quest's Details/Objectives belonged to a different quest. |
| 341–540 (excl. skip-listed 352, 390, 406, 462, 490, 497, 534) | 2026-07-15 | ~50 targeted + 4 project-wide systemic sweeps (~100 occurrences) | Batch 3. Highest bug density yet at the time (118/193 flagged); introduced the numeric-count-audit script. |
| 541–740 (excl. skip-listed 548, 612, 636, 740) | 2026-07-15 | ~15 targeted + 2 large clan/race-term sweeps (~55 occurrences) | Batch 4. Surfaced the Troll/Ogre terminology system. |
| 741–940 (excl. 18 skip-listed) | 2026-07-15 | ~20 targeted fixes; widened count-audit across 100–940 | Batch 5. Highest false-positive rate yet for count fixes — three count "fixes" had to be reverted mid-batch. |
| 941–1140 (excl. skip-listed 946, 987–989, 1128, 1129) | 2026-07-15 | ~25 targeted fixes + 3 project-wide term sweeps | Batch 6. Introduced `diff_quest_text.py --strict`. |
| 1141–1340 (excl. skip-listed 1151, 1154–1163, 1165, 1277–1280, 1289–1300) | 2026-07-15 | ~20 targeted fixes + 1 project-wide term sweep (251×) | Batch 7. First confirmed zhCN-leak race term (`暗夜精靈`); also the first batch where several of the agent's own proposed fixes were wrong and corrected by the user. |
| 1341–1540 (excl. skip-listed 1390, 1397, 1441, 1443, 1460, 1461, 1533, 1537, 1538) | 2026-07-15 | ~20 targeted fixes + 3 project-wide term sweeps | Batch 8. Highest bug density since batch 3 (108/191 flagged). Introduced `creature_template`'s literal in-game `name` field as a ground-truth check. |
| 1541–1740 (excl. skip-listed 1659, 1660, 1662–1664) | 2026-07-16 | ~10 targeted fixes + 1 naming sweep | Batch 9. Confirmed the OpenCC-conversion finding (see Methodology). Found 40 quest rows with raw unconverted simplified Chinese (separate, larger issue — see Known Issues). |
| 1741–1940 (no skip-listed IDs in range) | 2026-07-16 | ~20 targeted fixes + 6 project-wide term sweeps | Batch 10. DBC ground truth repeatedly showed corpus-majority spellings were wrong. Introduced direct `curl` NPC/item page fetches for no-locale-table disputes. |
| 1941–2140 (excl. skip-listed 2018, 2020, 2058, 2059) | 2026-07-16 | ~15 targeted fixes, no project-wide sweeps | Batch 11. Lowest bug density yet (28/196 flagged). |
| 2141–2340 (no skip-listed IDs in range) | 2026-07-16 | ~8 targeted fixes, no project-wide sweeps | Batch 12. Jewelry/Uldaman quest cluster. |
| 2341–2540 (no skip-listed IDs in range) | 2026-07-16 | ~11 targeted fixes, no project-wide sweeps | Batch 13. |
| 2541–2740 (no skip-listed IDs in range) | 2026-07-16 | ~7 targeted fixes, no project-wide sweeps | Batch 14. Lowest bug density yet (18/200 flagged). |
| 2741–2940 (excl. skip-listed 2868) | 2026-07-16 | ~35 targeted fixes + 3 project-wide sweeps | Batch 15. Highest bug density since batch 3 (76/199 flagged). `質量`→`品質` zhCN-leak caught. Demon Hunter class-page override. Trogg term went through 3 reversals same-day. |
| 2941–3140 (89 IDs not in DB — large real ID-space gap) | 2026-07-16 | ~26 targeted fixes across 15 quest rows, no new project-wide sweeps | Batch 16. Trogg term reverted a 4th time (final answer: `穴居人`). |
| 3141–3340 (189 IDs not in DB — sparsest range, only 10 real rows) | 2026-07-16 | 7 targeted fixes across 3 quest rows | Batch 17. Discovered `diff_quest_text.py` has no range arguments — must filter its full-corpus output in Python. |
| 3341–3540 (excl. 16 skip-listed; 113 IDs not in DB) | 2026-07-16 | 28 targeted fixes across 20 quest rows | Batch 18. 7 separate NPC/term disputes resolved via `creature_template_locale` in one batch. |
| 3541–3740 (excl. 4 skip-listed; 153 IDs not in DB) | 2026-07-16 | 12 targeted fixes across 9 quest rows | Batch 19. Mosh'Ogg zone-name settled via DBC. |
| 3741–3940 (excl. 2 skip-listed; 144 IDs not in DB) | 2026-07-16 | 11 targeted fixes across 9 quest rows | Batch 20. |
| 3941–4140 (no skip-listed; 141 IDs not in DB) | 2026-07-17 | 28 targeted fixes across 15 quest rows | Batch 21. Blackrock Depths/Burning Steppes cluster. |
| 4141–4340 (excl. 2 skip-listed; 143 IDs not in DB) | 2026-07-17 | 41 targeted fixes across 20 quest rows | Batch 22. First "surfaced to user rather than resolved unilaterally" case (quest 4184, Varian Wrynn vs Bolvar Fordragon). |
| 4341–4540 (no skip-listed; 136 IDs not in DB) | 2026-07-17 | 16 targeted fixes across 12 quest rows | Batch 23. |
| 4541–4740 (excl. 1 skip-listed; 164 IDs not in DB) | 2026-07-17 | 8 targeted fixes across 4 quest rows | Batch 24. Lowest density in several batches; all fixes reused already-established ground truth. |
| 4741–4940 (excl. 1 skip-listed; 143 IDs not in DB) | 2026-07-17 | 38 targeted fixes across 16 quest rows | Batch 25. Highest density yet (80%). Blackrock Spire cluster; Menara Voidrender surname fix. |
| 4941–5140 (excl. 1 skip-listed; 114 IDs not in DB) | 2026-07-17 | 39 targeted fixes across 19 quest rows | Batch 26. Very high density (67%); 3 resurfacing fixes across 15 quests. Aurius phonetic override. |
| 5141–5340 (excl. 6 skip-listed; 100 IDs not in DB) | 2026-07-17 | 2 project-wide grammar sweeps (73×) + 27 targeted fixes across 16 quest rows | Batch 27. Very high density (63%). Leatherworking/Moonwell character-level sweeps. |
| 5341–5540 (excl. 8 skip-listed; 133 IDs not in DB) | 2026-07-17 | 4 project-wide sweeps (71×) + 2 targeted fixes across 3 quest rows | Batch 28. Moderate density (44%). `想象`→`想像` orthography sweep and a `天災石`→`天譴石` resurfacing of the established Scourge term (both swept file-wide, including 3 occurrences of the latter far outside current progress). Gordok Ogre/Troll term initially misjudged as a false positive same-day, corrected after a user challenge — `戈多克巨魔` is in fact correct (9× swept). Iruxos name spelling settled same-day (zhCN-leak `埃魯索斯`→`埃盧梭斯`, 3×). One fix (Krastinov's "Butcher" epithet) applied then reverted same-day per user override — see Established terms. |
| 5541–5740 (excl. 42 skip-listed; 88 IDs not in DB) | 2026-07-17 | 12 targeted fixes across 11 quest rows, + 2 same-day corrected sweeps (169×) | Batch 29. 70 real rows in range; 40 flagged, high density (57%) — dominated by a large priest/class-quest-chain cluster (race-variant "Returning Home"/"Desperate Prayer"/"In Favor of..." templates). Two genuine content-swap bugs found (quests 5628, 5631 — both had an identical duplicate of quest 5629's Details text instead of their own unique English-sourced content; DB's own internal 3-way duplication, not a wowhead disagreement alone). A dropped trailing sentence restored (quest 5623). Confirmed Troll term resurfacing (quest 5642, `巨魔`→`食人妖`) and a Burning Blade/Fireblade resurfacing matching this same file's own quest 5381 (`燃刃`→`火刃`, quests 5726/5727). An "Arcane Feedback" term fix matching the corpus's 176:73 `秘法` majority (quests 5676/5677). Five stray trailing-asterisk titles stripped. One lower-confidence fix (quest 5648, Grunt Kor'ja `步兵`→`蠻兵`). **Two same-day reversals after user correction**: `艾露恩`→`伊露恩` (Elune) was initially left as a "confirmed false positive" based on corpus breadth (89 occurrences vs wowhead's 37) — wrong call, corpus breadth was itself the OpenCC-conversion artifact; `Achievement_Name_zhTW.tsv` id 937 (`伊露恩的祝福`) is tier-1 DBC proof, swept 103× project-wide. `揹包`→`背包` (Satchel/backpack) similarly reversed per direct user correction (no DBC exists for this generic term; user's real-world zhTW usage knowledge is the source), swept 66× project-wide. See Established terms. |

| 5741–5940 (no skip-listed IDs in range) | 2026-07-17 | 10 targeted fixes across 9 quest rows + 1 established-typo resweep (9×, mostly outside batch) | Batch 30. 52 real rows in range; 20 flagged, moderate density (38%). A garbled-word typo fix (`大長`→`酋長`, "Warchief") and a two-clan disambiguation in the same quest (5761: "The Burning Blade" → `火刃氏族` per the established rule, but its sibling clan "the Searing Blade" in the same Details field was *already correctly* `灼刃氏族` and deliberately left untouched — two similar-sounding clan names in one quest, don't let fixing one accidentally flatten the other). A real character-identity bug (quest 5762: DB conflated "Hemet Nesingwary" with his distinct son "Hemet Nesingwary **Jr.**" — wrong title, "old" vs "new customer" reversed, and a dropped "take his father's place" clause, all restored from English). Confirmed/extended the established Un'Goro Crater typo fix (`安戈洛爾`→`安戈洛`) to 2 more quests in range plus resurfaced instances in already-verified batches (9 total occurrences swept file-wide, most outside this batch's own range — same precedent as prior batches). An Alchemist/Chemist title fix and a literal surname fix (Grish "**Longrunner**" → `長跑者`, not the paraphrase `遠行者`). A same-template phrase fix across all 8 corpus instances of the Collector's Edition pet-delivery quest (`感謝您的支援`→`感謝您的支持`, more idiomatic for a customer-thank-you context; not a generic-word sweep — verified as the exact same boilerplate text in every instance, 5 of 8 in this batch's own range). One low-confidence name-spelling fix (Claire → `克雷爾`, no locale table). **Self-caught and reverted a same-day mistake**: an initial "trogg term" fix for quest 5892 (`石顎`→`石齶`, matching the established Rockjaw precedent) used an unscoped global replace that accidentally altered quests 432/433 too, which were untouched, already-correct, unrelated content — caught before finishing the batch, reverted those two rows to their exact prior committed state via `git show HEAD`, keeping only quest 5892's verified fix. Confirmed several false positives, all left unchanged: quest 5741's `節杖`/`權杖` and `艾瑟雷索塔裡`/`...高塔` (DB's structure is the more literal English match), `深鐵礦洞`/wowhead's `...礦坑` (matches the corpus's overwhelming `礦洞` convention for "mine" generally, not just this one item), and `響應召喚`/wowhead's `回應召喚` (DB's existing 5:1 majority plus a stronger idiom argument for "heeding a call"). |

| 5941–6140 (excl. 1 skip-listed; 133 IDs not in DB) | 2026-07-17 | 9 targeted fixes across 6 quest rows | Batch 31. 67 real rows in range; 40 flagged, high density (60%) — dominated by a 5-race-variant Hunter "The Hunter's Path"/pet-taming quest-chain cluster (Tauren/Orc-Troll/Night-Elf/Dwarf-Gnome each with their own trainer NPC). Two more content-swap bugs found in that cluster (quests 6066, 6070 — each had the Night Elf variant's NPC/location text leaked into their own row, matching the exact batch-29/30 pattern; scoped fixes only, the other 8 quests in the cluster were already correct). A dropped word restored via corpus+English match (`成年陸行鳥`→`成年平原陸行鳥`, "Adult **Plainstrider**", quest 6061). A DBC-settled location fix (`冰風崗`→`冰風營地`, quest 6028 only — `AreaTable_zhTW.tsv` confirms these are two *distinct* real places, id 1684 "Chillwind Post" vs id 3197 "Chillwind Camp"; English for this quest specifically says "Camp", not a corpus-wide sweep since both terms are legitimately correct elsewhere for the other place). A fabricated-location fix (`士兵大廳`→`榮譽谷`, "Valley of Honor," quest 6081). A dropped zone name restored (`科多獸墳場`→adds `淒涼之地`, quest 6132). Confirmed several false positives, left unchanged: quest 5941's `遺物`/wowhead's `聖物` (established rule), the `達扎拉`/`達札拉` (Dazalar) name-spelling split (DB's own 17:2 majority, no locale table), `未完的任務`/`未完成的任務` and `梅羅什`/`梅羅西` (DB majority in each case, no locale table). Every fix this batch was applied with an exact-match-count check (`replace_once` asserting exactly 1 occurrence) after batch 30's self-caught unscoped-replace mistake — `git diff` confirmed only the 6 intended quest rows were touched. |

| 6141–6340 (excl. 3 skip-listed; 165 IDs not in DB) | 2026-07-17 | 9 targeted fixes across 8 quest rows | Batch 32. 32 real rows in range; 13 flagged, moderate density (41%) — smallest real-row count yet, most of the range is unused ID space. A confirmed genuine count error (quest 6221: DB said kill 6/6/6 Deadwood furbolgs, English says 5/5/5 — all three counts wrong). A specific-word-match fix (`聖賢`→`神諭者`, "the Scarlet **Oracle**," quests 6146/6147 — "Sage" doesn't match "Oracle" at all). A specific-faction-name fix (`亡靈`→`被遺忘者`, "an agent of **the Forsaken**," quest 6186 — DB had substituted the generic "undead" for the specific faction name; the NPC-identity question in the same quest, Bolvar Fordragon named in DB/wowhead vs. Varian Wrynn in the English `quest_template` Objectives field, was left alone per the established batch-22 precedent for this exact kind of lore-vs-literal-English divergence). Extended the batch-31 DBC-settled Chillwind Camp/Post distinction to 2 more quests (6184/6185). One lower-confidence gender-accuracy fix (`巫師`→`巫女`, "Slitherblade **Sorceresses**," quest 6143 — explicitly female in English, no locale table). Two more fixes added same-day per direct user correction (quests 6181/6281, initially misjudged as false positives on a "DB's own transliteration is plausible" basis — that reasoning doesn't hold once independent per-entity evidence exists): `索爾`→`托爾` for **Thor** the gryphon master (npc=523) specifically — wowhead's own dedicated NPC page confirms `托爾`; later-expansion official zhTW keeps this distinct from Thrall's `索爾` on purpose, deliberately not colliding the two names — fixed only in this NPC's 2 quests, NOT a corpus-wide sweep (`索爾` overwhelmingly means Thrall everywhere else, 281 occurrences). `劉易斯`→`路易斯` for Commander Louis Philips (npc=13154) — wowhead's own dedicated NPC page confirms `路易斯·菲力浦`, `劉易斯` is a zhCN leak. Confirmed remaining false positives, left unchanged: `獅鷲`/`獅鷲獸` (DB's 109:26 corpus majority) and `主宰洛爾`/wowhead's reversed `洛爾主宰` word order (no corpus-wide title-placement convention to appeal to, English word order matches DB). Every fix applied with an exact-match-count check, `git diff`-verified to touch only the intended rows. |

| 6341–6540 (no skip-listed IDs in range) | 2026-07-17 | 6 targeted fixes across 5 quest rows (one a resurfacing fix in an already-verified batch-29 row) | Batch 33. 41 real rows in range; 21 flagged, moderate-high density (51%). A genuine NPC-swap content bug (quest 6521: Objectives said turn in Ambassador Malcin's head to Varimathras, but English and this row's own `ObjectiveText1` sub-hint both confirm Bragor Bloodfist — fixed using the row's own already-correct spelling `布拉貢·血拳` over wowhead's independent `貝拉戈`). A Troll-term resurfacing (quest 6461, `巨魔`→`食人妖`, "We **Trolls** here at Malaka'Jin"). Extended the Chillwind Camp/Post DBC distinction to one more quest (6389) — and while checking it, found and fixed the *same* bug resurfacing in already-verified quest 5903 (batch 29's range): its Objectives field already correctly said `冰風營地`, but its CompletedText field still had the old `冰風崗` — the kind of resurfacing-in-already-fixed-rows this pass watches for. **Three same-day reversals, all after user follow-up questions caught insufficient initial checks** — a literal English-word match isn't automatically right when official localization made a deliberate lore-based word choice instead: (1) quests 6384/6385/6386 (Wind Rider Master cluster) — initially "fixed" toward `馭風者`/"Wind Rider" reasoning that `creature_template`'s literal English title "Wind Rider Master" settled it; reverted per user lore correction (the Wind Rider mount is lore-wise a Wyvern, and wowhead's `雙足飛龍` rendering is the good, accepted zhTW term for it). All three quests now consistently use `雙足飛龍`/`雙足飛龍管理員`, matching wowhead. (2) quest 6481 — initially kept DB's `開啟`/`共鳴桶` as a literal match for English "open the Resonite cask"; reverted per user correction that the in-game object is actually a large crystal, not a barrel/cask, making wowhead's `粉碎`/`共鳴石`("smash the Resonite stone") the lore-accurate rendering. Also aligned `魔化`→`附魔` in the same quest while fixing it, matching the already-established batch-29 "Enchanted" convention. (3) `龍人`/`龍裔` and `巨龍沼澤`/`巨龍泥沼` (quests 6501/6502) — initially left as false positives on a "DB's own corpus majority, no locale table" basis without actually searching for ground truth; user pushed back and a proper check found both settled: `AreaTable_zhTW.tsv` id 511 = `巨龍泥沼` (tier-1 DBC, found this time by searching the Chinese candidate spelling directly rather than stopping at "no locale table exists" — same technique the Elune miss should have already taught); wowhead's own dedicated NPC page (`npc=7040`, "Black Dragonspawn") confirms `黑色龍裔`, settling `龍裔` for "Dragonspawn" specifically (tier-3). Fixed both quests; the corpus's other ~7 `龍人` occurrences remain unverified (some are plausibly the same "Dragonspawn" concept given "Black"/Nefarian context clues, but not individually confirmed — see Established terms for the open item). See Established terms for the remaining open scope on Wind Rider (16 more `馭風者` occurrences elsewhere in the corpus, not swept). |

| 6541–6740 (excl. 11 skip-listed; 133 IDs not in DB) | 2026-07-17 | 11 targeted fixes across 11 quest rows + 2 project-wide resurfacing sweeps (39×, mostly outside batch) | Batch 34. 56 real rows in range; 39 flagged, very high density (70%) — dominated by two large clusters (a Splintertree/Zoram'gar Naga questline and a Blackrock Spire black-dragon-disguise questline). One confirmed resurfacing sweep of an already-settled term, applied file-wide: `埃博斯塔夫`→`艾博斯塔夫` (Emberstrife, an already-established rule from batch 24/25 that had never been swept past that batch's own range, 14×). A title/content fix for a wrong epithet (`夢遊者`→`暮光領主`, "**Twilight Lord** Kelris," quest 6561 — "Dreamwalker" doesn't match at all). A singular/plural fix (`上古之神`→`上古諸神`, "Allegiance to the **Old Gods**," quests 6564/6565 — scoped to the specific instances confirmed plural in English, not swept corpus-wide since "an Old God" singular is also legitimate in other contexts). A location fix (`慰藉之林`→`碎木崗哨`, "**Splintertree Post**," quest 6544) plus matching the corpus's own established `托雷克`/`埃爾托格` spelling over this quest's outlier `託`-variant. A resurfacing Dragonspawn-term fix (`龍人`→`龍裔`, batch-33-established rule, quests 6569/6570). A dropped-token bug restored (quest 6611: DB hardcoded the `$r` race placeholder as `亡靈`/"Undead" instead of preserving it) alongside the established Goblin race-term fix (`地精`→`哥布林`). Two name-spelling fixes leaning wowhead on cross-page consistency grounds (not just one quest's prose, but 4-5 independently-fetched quest pages all agreeing): `羅卡魯`→`羅卡洛` (Rokaro) and `麥蘭達`→`米蘭達` (Myranda the Hag — also matches this corpus's own 18:6 majority spelling *elsewhere*, confirming the cluster's `麥蘭達` was the OpenCC-error outlier). A word-choice fix matching the specific English noun (`騙過那些黑龍的眼睛`→`騙過黑龍軍團`, "fool the **Black Dragonflight**," not "eyes"). A title fix where neither side's rendering was a literal match, but wowhead's was much closer to the actual English idiom (`青出於藍！`→`我已經傾囊相授了！`, "**I Got Nothin' Left!**"). Confirmed two false positives going the *other* direction — DB was right, wowhead's own fetch was wrong: quest 6606 (`冬泉谷永望鎮` — Everlook genuinely is in Winterspring; wowhead's `奧格瑪` doesn't match "Witch Doctor Mau'ari in **Everlook**" at all) and quest 6610 (DB's "10 Giant Eggs" count and `迪爾格` name spelling both matched English exactly; wowhead's "12" and `戴格` did not). |

| 6741–6940 (excl. 3 skip-listed; 171 IDs not in DB) | 2026-07-17 | 5 targeted fixes across 5 quest rows (two Alliance/Horde mirror-quest pairs sharing identical text) + 1 quest removed to skip-list | Batch 35. 26 real rows in range; 12 flagged, moderate density (46%) — sparsest real-row count since batch 32, large ID-space gap. A Troll-term fix (`巨魔`→`食人妖`, quests 6847/6848 — creature_template's own literal names "Winterax Troll"/"Winterax Witch Doctor"/"Winterax Shadow Hunter" confirm the clan; identical Alliance/Horde mirror quests, swept both). A creature-name fix leaning the more literal English match with no counter-evidence either way (`熔火惡犬`→`熔核犬`, "Ancient **Core** Hound," quest 6822 — DB's rendering dropped "Core" and added an unsourced "evil/惡"). Confirmed one false positive (quests 6825/6826's blank Objectives/Details fields — English `quest_template` is *also* blank for both, confirming wowhead's fetched text came from some other source entirely, not the actual quest data). Quest 6921 resurfaced the just-settled Blackfathom Deeps dispute (`黑澗深淵` vs wowhead's `黑暗深淵`) — already resolved per the final user decision (batch 34), left unchanged. **Three same-day corrections after user review**: quest 6843 ("Da Foo") confirmed as an unfinished dev/QA quest (English source has all-zero/blank fields) — moved to `skip-list.tsv` and its placeholder zhTW row removed entirely (kept the `DELETE FROM` statement, dropped the `INSERT`, so any live-DB row gets cleanly removed with nothing reinserted). Quest 6861/6862: initially left `首席技師`/`行動式` unchanged on a "DB's own established corpus term" basis — reverted per user preference for wowhead's `工程大師`/`可攜式` rendering instead (swept both mirror quests). Quest 6804: initially left `不諧護腕` unchanged reasoning "Bracers" matched literally — reverted per user correction that `不諧腕索` is the correct zhTW item-name rendering (Objectives field only; the row's separate generic-flavor `縛靈護腕` phrase was never in dispute and stays unchanged). |

| 6941–7140 (excl. 1 skip-listed; 94 IDs not in DB) | 2026-07-17 | 29 quest rows fixed (13 initial + 16 after a policy reversal), plus 2 resurfacing sweeps outside the batch range | Batch 36. 45 real rows in range; 29 flagged, high density (64%). Two Alterac Valley scarecrow-namesake NPC bugs in the mine/graveyard/tower-capture cluster: quest 7082's Objectives named a completely wrong turn-in (`亞斯拉`) at the wrong location, and quest 7124's Objectives sent players to the "Frostwolf Quartermaster" (likely a content-swap from neighboring quest 7123) — both corrected to `提卡·血牙下士` (Corporal Teeka Bloodsnarl). Quest 7101 kept its already-correct NPC identity/location but was missing the "Corporal" rank title. **Same-day reversal after user correction on the surname**: initially rendered "Bloodsnarl" as `血矛` on tier-2 evidence (a different Bloodsnarl NPC's pre-existing `creature_template_locale` row, entry 22760) over wowhead's own `血牙` — user corrected that `血牙`("Blood Fang") is the more accurate rendering for "Snarl"; reverted all three quest rows to `血牙`, fixed entry 22760's own row (`亞斯拉·血矛`→`亞斯拉·血牙`, in a separate pending file, `rev_1783394896206866751.sql`), and swept 2 more resurfacing `亞斯拉·血矛` occurrences outside this batch's range (quests 7401/7427) for corpus-wide consistency. In hindsight, all three AV quest rows' own untouched `ObjectiveText1` fields had already independently said `血牙` all along. A single-character typo fix (quest 7121: `軍需管`→`軍需官`). A dropped-epithet fix (quest 7044: `維利塔恩`→`維利塔恩領主` only at its first mention, matching "**Lord** Vyletongue" — its second, unadorned mention later in the same field was correctly left alone). A brand-name-consistency fix (`煙林牧場`→`燻木牧場`, "Smokywood Pastures," quest 7042 — DB's own corpus already favors `燻木牧場` 22:4 elsewhere). A race-term fix scoped to exactly one of two look-alike mentions in the same field (quest 7003 Details: `地精科技`→`哥布林科技` for explicit-caps "GOBLIN technological advances," while the *other* `地精` in the same field, "gnomish shrinking ray," was correctly left alone — matches Gnome=`地精`/Goblin=`哥布林` exactly, mixed within one field). A word-choice fix (`頸圈`→`項圈`, "train**ing collar**," quest 7027). A content-swap fix (quest 6981: Objectives referenced an unrelated "Nightmare Shard" instead of the quest's own Glowing Shard — replaced with wowhead's correct content; also `碎片`→`裂片` throughout the row including a CompletedText instance the diff tool doesn't check). A noun-choice fix for a collectible item name (`雕像`→`刻像`, "Theradric Crystal **Carvings**," quest 7028), combined with the plural-Old-Gods fix (`上古之神`→`上古諸神`, extended here and to quests 7064/7065, all lowercase-but-plural "the old gods" instances). A name-spelling fix (`特沃什`→`特沃許`, Archmage Tervosh, quest 7070). **User-directed policy reversal, applied after the batch's initial pass**: the user instructed that wowhead-tw should be treated as ground truth for every remaining disputed field this batch had left unchanged as a "false positive" (with the sole, explicit exception of the `$g男孩:女孩;`/wowhead's `<男孩/女孩>` gender-token rendering, which is a pure notation artifact, not content, and stays as-is). This reopened and flipped roughly a dozen calls that had leaned on DB-side established-term/corpus-majority reasoning: `冷齒礦洞`/`深鐵礦洞`→`礦坑` (quests 6982/6985/7121/7122/7123/7124 — **reverses the batch-30 "礦洞 is the corpus convention" precedent**, but only for this batch's occurrences, not a corpus-wide sweep — the wider corpus still has many un-revisited `礦洞` instances, a real inconsistency to watch for); `坐具`→`座具` (quests 7002/7026, plus filling in 7002's and three other quests' — 6941/6942/6943 — previously-blank Objectives fields with wowhead's content even though the English `quest_template` source is itself blank for all of them, since wowhead is now the trusted source over the static English reference text); `範達瑟`→`范達瑟` (quest 7003, reverses the 8:0 DB-majority-based call); `扎爾塔`→`札爾塔` title-adjacent `汙染`→`污染` and `橙色`→`橘色` (quests 7029/7041/7064/7065, plus a fuller Details-field realignment for 7041 where wowhead's paraphrase differed beyond single terms); `暗影殘片`→`裂影碎片` (quests 7068/7070, reverses the 7:0 DB-majority-based call — note 7070's wowhead Details text itself drops "碎片" down to bare `裂影`/`這種水晶` inconsistently with its own title, applied verbatim regardless); and the AV cluster's location generality (`丹巴達爾`/`霜狼村`→`奧特蘭克山脈`, quests 7081/7101/7102 — reverses the specific-over-general precedent applied earlier in the same batch). Every fix (both passes) applied with an exact-match-count check, `git diff`-verified to touch only the intended rows. |

| 7141–7340 (no skip-listed IDs in range) | 2026-07-17 | 11 targeted fixes across 11 quest rows | Batch 37. 28 real rows in range; 17 flagged, high density (61%). Confirmed a **wowhead-shows-wrong-era-content false positive**, the first of its kind this pass: quests 7141/7142 ("The Battle of Alterac"/"The Battle for Alterac") — wowhead's fetched title, objectives, AND details all describe a substantially different quest design (a "steal the map"/"defeat the captain first" mechanic) that doesn't exist in this project's English `quest_template.sql` at all, while DB's existing text is a near-perfect literal match to the WotLK-era English source sentence-for-sentence — concluded wowhead's `/wotlk/tw/` page is showing later-expansion (likely Cataclysm AV revamp) content for this quest ID, not a translation quality issue, and left both rows unchanged. This tempers the batch-36 "wowhead as truth" directive: it applies to translation *disputes*, not to wowhead showing content for a different game version — a title *and* full-content three-way mismatch against the English source is the signal to check for this, not just accept the diff. A content-swap bug (quest 7181: Objectives had the wrong mechanic entirely, describing a "kill the 1001st troll" spawn trigger that's actually quest 7202's own correct, verified-by-wowhead text — 7181's real English Objectives just says the boss "appears at will"; replaced with wowhead's correct short version). A resurfacing Troll-term sweep (`冰斧巨魔`→`冰斧食人妖`, the already-settled Winterax clan rule from batch 35, quests 7181/7202/7261). A title fix matching the English noun more literally (`實驗場`→`試煉場`, "**Proving** Grounds," quests 7161/7162 — "experiment field" doesn't match "proving/trial" at all) paired with a word-choice fix (`勳章`→`徽記`, "the Frostwolf initiate's **insignia**"). A location/direction fix restoring the correct compass bearing (quest 7162: `主基地東南邊`→`丹巴達爾西南邊`, matching English "southwest of **Dun Baldar**" — DB had both the wrong reference point and the wrong direction). A DBC-confirmed place-name fix (`西部哨塔`→`哨塔高地`, quest 7301 — `AreaTable_zhTW.tsv` area 2962 = `哨塔高地`, tier-1; DB's own row 7281 already independently used the correct term in its `ObjectiveText4` field, a same-corpus consistency signal that should have been checked first). A resurfacing name-spelling sweep (`菲利普`→`菲力浦`, `劉易斯`→`路易斯`, quests 7281/7282 — extends the already-settled batch-32 Commander Louis Philips ruling, applied to both Philips brothers' shared surname spelling). A dropped-proper-noun fix (`戰火紛飛的戰場`→`征戰平原`, quest 7282 — English literally says "across the **Field of Strife**," a named AV location, not a generic paraphrase). A single-character typo fix (quest 7302: `向揮官穆法特覆命`→`向指揮官穆法特覆命`, missing `指`). Two cosmetic `談一談`→`談話` alignments (quests 7221/7222). **Three same-day corrections after user preference**: (1) `雷矛部族`→`雷矛氏族` (quests 7142/7241/7261) was initially left unchanged on a 18:1 DB-majority basis; user stated `氏族` is the preferred wording over `部族` generally, so this was reverted to match wowhead after all — applied to the 3 instances actually reviewed this batch, not swept corpus-wide (~17 more `X部族` occurrences elsewhere remain unswept, see Established terms). (2) `傑斯託`→`傑斯托` (Wing Commander Jeztor) was initially left unchanged on a 5:0 DB-majority basis; user directed `傑斯托` instead — reverted, and since this is a single named NPC (not a generic word-choice question), swept all 5 corpus occurrences, including one in already-committed quest 6826 (batch 35's range) alongside quest 7302 here. (3) `杜菲`→`達菲` (Commander Duffy, quest 7301) was initially left unchanged on a 2:1 DB-lead basis; user directed `達菲` for phonetic accuracy, matching wowhead — reverted (2 occurrences in the row, Objectives + `ObjectiveText4`). Confirmed remaining false positives, left unchanged: `雙足飛龍`/wowhead's `戰爭部隊` (quest 7302 — wowhead's own rendering here loses the established Wind-Rider-is-a-Wyvern term for no reason, no counter-evidence); `穆維裡克`/wowhead's one-off `穆拉維克` (9:0 DB majority); `護甲碎片`/wowhead's `護甲碎塊` (quests 7223/7224, 21:4 DB majority, "scraps" is already a fine literal match). This batch shows the post-batch-36 policy in practice: wowhead is the default for a genuine disagreement, but a quest's own internal field consistency, a DBC hit, or an already-settled corpus rule can still outrank a single wowhead fetch — the difference from before is these are now actively checked rather than assumed away. |

| 7341–7540 (no skip-listed IDs in range) | 2026-07-17 | 13 targeted fixes across 13 quest rows + 1 resurfacing sweep outside the batch range | Batch 38. 60 real rows in range; 41 flagged, very high density (68%) — but ~24 of those flags were **wowhead scrape failures**, not real diffs: for a large repeatable-PvP-bounty quest cluster (the "kill an enemy-race player" AV quests, e.g. 7361–7366, 7381/7382, 7401/7402, 7421–7428, 7522) wowhead's `/wotlk/tw/` page returns its generic WotLK-quests-listing meta description (`魔獸世界：巫妖王之怒中所有任務的完整列表...`) instead of actual quest content — no real quest page exists there to scrape. Confirmed as false positives and left entirely unchanged; this is the mirror-image of the batch-37 wrong-era-content case (there wowhead showed real content for the wrong game version, here it shows no content at all). A genuine title/content-loss bug (quest 7383 "Crown of the Earth": DB's title, Objectives, and Details all described a *different* Teldrassil quest entirely, with Objectives truncated to a bare sentence missing the delivery clause — replaced wholesale with wowhead's version, which matches the English `quest_template` source closely on all three fields). A resurfacing place-name-consistency fix (`艾德雷薩拉斯`/`埃雷薩拉斯`→`埃德薩拉斯`, Eldre'Thalas — DB's own corpus was internally split 3:4 between two different wrong spellings with no majority, while 5 independently-fetched wowhead pages all agreed on `埃德薩拉斯`; applied to the 5 in-batch quests reviewed — 7441/7463/7481/7482/7494 — plus one resurfacing instance in already-committed quest 5526). A genuine item-name mistranslation (`熔火碎片`→`熔核碎片`, "**Core** Fragment," quest 7487 — DB dropped "Core" for a generic "Fire" descriptor not in the English at all; the same field's `火焰之王`("Firelord") was correctly left alone over wowhead's `炎魔`, a less literal match). A dropped-epithet fix (`倫薩克`→`倫薩克霸主`, "**Overlord** Runthak," quest 7491). A genuine typo fix (`厄運之棰`→`厄運之槌`, quests 7488/7489 — wrong character, "棰"(cane) instead of "槌"(hammer); quest 7488's own row already used the correct `槌` elsewhere in the same field, an internal-consistency giveaway). A resurfacing Arcane-term fix (`奧法師`→`秘法師`, quest 7500 — matches the established Arcane=`秘法` rule, 64:1 DB majority already favored the correct term everywhere else). A low-confidence item-name fix (`精靈劍`→`精靈之刃`, "Elven **Blade**," quest 7508, no locale table either way). Two cosmetic `談一談`→`談話` alignments (quests 7492/7494). Confirmed several false positives with strong pre-existing DB majorities and no compelling wowhead counter-evidence, left unchanged: `託塞德林`/wowhead's one-off `托塞德林` (7:0), `拉託尼庫斯`/wowhead's one-off `拉托尼庫斯` (12:0), `急速聖典`/wowhead's `疾速聖典` (6:0 — also, quest 7483's wowhead Objectives had itself dropped the named NPC "Lorekeeper Lydros" that the English source confirms by name, a wowhead translation-quality miss, not just a term preference), and `魔光碎片`/wowhead's `魔光裂片` (10:3, a different "Shard" item than 6981's Glowing Shard — per the established per-item rather than corpus-wide rule for this word). Also confirmed the batch-35/34-style blank-English-source false positive again (quests 7385/7386). |

| 7541–7740 (excl. 2 skip-listed; 61 IDs not in DB) | 2026-07-17 | 24 targeted fixes across 24 quest rows + 2 quests removed to skip-list | Batch 39. 93 real rows in range; 62 flagged, very high density (67%). A significant title/rank correction affecting a whole Paladin mount questline: `格雷森·沙東布瑞克公爵`→`格雷森·破影者領主` — English confirms "**Lord** Grayson **Shadowbreaker**"; DB had both the wrong rank ("Duke" instead of "Lord") and had transliterated the clearly-compound English surname ("Shadow"+"breaker") phonetically instead of translating it semantically, which doesn't capture the meaning at all. This reverses a 16:0 pre-existing DB majority, but the English evidence is unambiguous; applied to all 7 in-batch occurrences (quests 7638/7639/7640/7644/7646/7648/7670) — none swept outside the batch. Two more rank/title fixes on the same pattern (`魔王貝恩霍勒`→`貝恩霍勒領主`, "**Lord** Banehollow," quest 7623; `工頭瑪託留斯`/`工頭奧菲斯特`→`監督者瑪託留斯`/`監督者奧菲斯特`, "**Overseer** Maltorius/Oilfist," quests 7701/7722 — the name spelling itself was also corrected same-day, see below). A genuine item-word mistranslation (`傀儡`→`魔像`, "Heavy War **Golems**," quest 7723 — matches the already-known-but-previously-unresolved Golem split noted in Unresolved items; corpus was near-evenly mixed 49:55 with no prior majority either way) plus a title fix on the same quest (`該死的手指頭！`→`該死的胖手指！`, "Curse These **Fat** Fingers"). A DBC-confirmed place-name fix (`風暴祭壇`→`暴風祭壇`, "Altar of Storms" — `AreaTable_zhTW.tsv` areas 255 and 1441 both confirm `暴風祭壇`, tier-1; swept all 8 in-batch occurrences across the Xoroth-portal questline, quests 7562/7625–7630). A word-choice fix matching the more literal English noun (`腐爛之痕`→`腐化之痕`, "the **Tainted** Scar" — "rotten" doesn't match "tainted/corrupted" at all; reverses an 8:0 DB majority on strong semantic grounds, applied to the 3 in-batch quests 7581/7582/7583). Another word-choice fix (`符文`→`雕紋`, "invoke powerful **glyphs**," quest 7563 — "rune" is a different magical concept than "glyph"). A mistranslated "Head" (`徽記`→`頭顱`, "Bring Darkreaver's **Head**," quest 7668 — "insignia" doesn't match at all). A resurfacing Arcane-term fix (`奧術水晶`→`秘法水晶`, quest 7722, matching the established rule). Two genuine typos (`引匯出`→`引導出`, quest 7626, wrong character; `游蕩`→`遊蕩`, quest 7563, wrong character — "swim" instead of "wander"; `S屠殺者索倫諾爾`→`屠殺者索倫諾爾`, quest 7636, stray leftover Latin letter). One dropped-word fix (`著名的術士`→`已故的術士`, quest 7626 — English says "the **late** warlock," not "the famous warlock," a real meaning flip not just a style choice). **Two quests confirmed as unfinished dev/QA content and moved to `skip-list.tsv`**: quests 7681/7682 ("Hunter test quest"/"Hunter test quest2") — the row's own `CompletedText` field literally reads the untranslated English placeholder `Return to GOSSIP TEST DUDE.`, even in the "translated" DB row, confirming this was never real content; both `INSERT`s removed, `DELETE`s kept. **Same-day correction after user preference**: `託`→`托` (user stated wowhead's `托` reads more naturally in zhTW) reverses the `託`-not-`托` DB-transliteration pattern this batch had just established as a standing rule — swept all 4 affected names project-wide (not just this batch's instances): `託塞德林`→`托塞德林` (Tortheldrin, 7 occurrences incl. already-committed quests 1317/1318), `拉託尼庫斯`→`拉托尼庫斯` (12 occurrences incl. already-committed quests 2869/2870/3130), `瑪託留斯`→`瑪托留斯` (8 occurrences), `阿託留斯`→`阿托留斯` (1 occurrence). Confirmed remaining false positives, left unchanged: `瑟銀兄弟會契約`/wowhead's `一份必須遵守的契約` (quest 7604 — DB's title is self-consistent with its own Objectives field's naming, neither side is a fully literal English match, no compelling reason to prefer wowhead); `古樹的手杖`/wowhead's `上古守護者的手杖` (quest 7636 — DB's title matches this exact quest chain's own established `古樹`="the Ancient" convention used for the same NPCs elsewhere in the chain, e.g. Hastat and Vartrus); `偵查隊長`/`偵查員` word-choice pairs (quests 7701/7728, genuinely mixed corpus usage both ways, no strong signal either direction). Also reconfirmed the blank-English-source false positive (quests 7736/7737) and the count-mismatch-tool false positive for a spelled-out Chinese numeral (quest 7634's `近萬年` correctly represents "10,000 years," the audit script just doesn't parse Chinese number words). |

| 7741–7940 (excl. 9 skip-listed; 76 IDs not in DB) | 2026-07-17 | 27 targeted fixes across 27 quest rows | Batch 40. 128 real rows in range; 87 flagged, very high density (68%) — dominated by a large Hinterlands "Revantusk Village" questline cluster and a Darkmoon Faire ticket/prize/card cluster. Confirmed a third wowhead scrape-failure pattern (distinct from the WotLK-quest-index and this-batch's own new `一 暗月馬戲團 任務.。` variant): a large chunk of Darkmoon Faire ticket-redemption quests return this exact generic placeholder instead of real content — left entirely unchanged, same treatment as the other two known scrape-failure patterns. A massive resurfacing Troll-term sweep (`巨魔`→`食人妖`, confirmed via `creature_template`'s own "Vilebranch Headhunter"/"Vilebranch Shadow Hunter"/"Vilebranch Troll Ambassador" evidence — applied across 12 quest rows in the Revantusk cluster: 7815/7828/7830/7839/7840/7841/7844/7845/7849/7850/7861). A genuine count-typo fix (`3個邪枝噬魂者`→`2個邪枝噬魂者`, quest 7862 — confirmed via the actual `RequiredNpcOrGoCount` field, not just the flavor text). Two dropped-epithet fixes (`薩魯法爾大王`→`薩魯法爾霸王`, quest 7784, "**Overlord**" not "Great King"; `德米提恩`→`大領主德米提恩`, "**Highlord** Demitrian," quests 7785/7786/7787, missing entirely). A genuine reward-item-name error (`銀翼功勳獎章`→`戰歌峽谷榮譽獎章`, quests 7788/7871/7872/7873 — English Objectives specifically says "**Warsong Gulch Mark of Honor**," not "Silverwing Merit Medal"; the quest's own Details field already correctly used a *different*, equally-valid reward phrase — "talisman of merit" — matching its own separate English Details text, so Details was correctly left untouched while only Objectives was wrong). Two title-tier fixes matching distinct English ranks (`競技場高手`→`競技場大師`, "Arena **Master**," quests 7810/7908; `競技場大師`→`競技場宗師`, "Arena **Grandmaster**," quest 7838 — two different tiers of the same title chain, each needed its own distinct Chinese term to stay distinguishable). A dropped-content fix (quest 7926: added a missing final sentence about the Darkmoon Faire's current location outside Thunder Bluff/Mulgore, present in English but entirely absent from DB). A genuine mistranslation (`冬谷伐木場`→`東谷伐木場`, "**Eastvale** Logging Camp," quest 7937 — wrong season word; the row's own separate `Objectives` field already correctly said `東谷`, an internal-consistency giveaway) plus a resurfacing corpus-majority word fix (`塔羅牌`→`占卜`, 90:6 DB majority, quests 7937/7938) and a mine-term alignment for one row's own internal inconsistency (quest 7938 used three different terms — `死亡礦井`, `死亡礦井`, and bare `礦洞` — for the same place in one row; aligned all to `死亡礦坑` matching wowhead, since the corpus itself was exactly tied 3:3 on `礦井`/`礦坑` generally with no majority to defer to). A minor title fix (`巨型黑色錘`→`巨型黑錘`, quest 7892). Confirmed several false positives, left unchanged: quest 7784's `薩魯法爾`(Saurfang) name itself, kept over the English `quest_template` source's "Overlord **Runthak**" — DB and wowhead's independent fetch agree with each other on Saurfang, the same DB/wowhead-consensus-over-stale-English pattern established in batch 37; `銀鬃捕獵者`/`銀鬃嗥狼` counts and `野蠻的梟獸` counts (quests 7828/7829, wowhead's fetched "10/10" and "20" are wrong, confirmed via `RequiredNpcOrGoCount`, DB's lower counts are correct) — a reminder that a *count* mismatch isn't automatically "DB is behind," check the real requirement field before assuming either side is right; `獅鷲`/wowhead's `獅鷲獸` (109:28 DB majority); `套牌`/wowhead's `套卡` (36:12); `高階`/wowhead's `高級` (239:62); `吉瓦斯·格里加特`/wowhead's one-off `葛萊蓋特` (13:2); `獵戶`/wowhead's `獵人` (established convention within this exact quest chain); `火焰之王`/wowhead's `炎魔` (already-settled false positive, batch 38). Also reconfirmed the blank-English-source false positive (quests 7813/7814/7817/7820–7822) and two more count-mismatch-tool false positives: a spelled-out Chinese numeral (quest 7813's `60塊毛料`, matches English's `60` digit fine, audit script quirk) and English number-words the tool doesn't parse (`第8張`/`第9張` matching "the first eight"/"a ninth card" across the whole Darkmoon card-deck cluster). |

| 7941–8140 (no skip-listed IDs in range) | 2026-07-18 | 21 targeted fixes across 21 quest rows | Batch 41. 80 real rows in range; 57 flagged, high density (71%) — dominated by the Zul'Gurub "Paragons of Power" reputation-armor questline (28 quests, one per set piece). A genuine content-swap bug within DB's own corpus, not a wowhead dispute: the "Augur" and "Haruspex" title epithets had been swapped — quests 8056/8074/8075 ("The Augur's...") used `預言者`("Prophet," matching neither English word) while quests 8057/8064/8065 ("The Haruspex's...") correctly used `占卜師`; cross-checked wowhead's own independent fetch for all of these (3 pages agreeing on `占兆師`=Augur, 3 more pages agreeing on `占卜師`=Haruspex) to confirm which set needed fixing — fixed only the 3 misassigned Augur quests to `占兆師`, left the already-correct Haruspex quests untouched. A genuine item-slot mistranslation (`腰帶`→`束腕`, "The Confessor's **Bindings**," quest 8070 — DB translated it as if it were a Belt, a different item slot entirely, confirmed by cross-referencing the other 5 genuinely-Belt-titled quests in the same cluster that correctly kept `腰帶`). A word-choice fix for 5 quests sharing the "Mantle" epithet (`襯肩`→`披肩`, quests 8067/8068/8071/8072/8076 — "Mantle" is a draped cape-like garment, more literally `披肩` than the rigid-shoulder-pad connotation of `襯肩`; corpus was nearly split 27:23 with no strong majority to defer to) plus one more specific-armor-type fix riding along on the Augur fix (`外套`→`鍊衫`, "The Augur's **Hauberk**," quest 8075 — "Hauberk" specifically means a mail/chain shirt, not a generic coat). A genuine location bug (`灰月洞穴`→`白鬃石`, "**Palemane Rock**," quest 7945 — DB had substituted a wrong and differently-typed location, a cave instead of a rock formation, in Mulgore; the row's own separate `Objectives` field had *also* said the wrong place, so this wasn't a same-row-inconsistency catch, purely an English cross-check). Two genuine translation gaps filled (not disputes — DB had left raw, untranslated English text sitting in a "translation gaps resolved" corpus): `Redeem iCoke Prize Voucher`→`兌換魚人寶寶兌獎券` (quests 8021/8023/8026, matching wowhead's own real-world-promo-quest translation, since there's no better source); and quest 7961 ("Waskily Wabbits!"), which had **no wowhead zhTW translation available at all** (wowhead's own page returns raw English for this specific ID, unlike its sibling quest 7962 which does have one) — constructed a full translation from the English source and item names, matching quest 7962's own already-correct terminology (`喬恩·勒克夫特`, `設計師島`, `狡猾的兔子`) for chain consistency; also fixed the real item-collection count (`5隻兔子`→`10隻倒楣兔腳`, confirmed via `RequiredItemCount`, since DB had the objective type and count both wrong) and completed 7962's own partially-untranslated Details/Objectives fields the same way. A resurfacing Enchanted-term fix (`魔化`→`附魔`, quests 8110–8113, matching the established batch-29 convention). A missing possessive-particle fix (`祖達薩全視之眼`→`祖達薩的全視之眼`, quest 8052). A measure-word grammar fix (`一隻阿拉希資源箱`→`一個阿拉希資源箱`, quest 8080 — `隻` is reserved for animals, not a crate). Confirmed a long list of false positives with strong DBC/corpus evidence, left unchanged: `友善`/wowhead's `友好` (DBC-confirmed via `Faction_zhTW.tsv`, tier-1, the standard reputation-level term — swept across the whole Zul'Gurub cluster's worth of flagged instances); `擊碎者`/wowhead's `擊破者` (32:0 DB majority, Jin'rokh's epithet); `護腕`/wowhead's `束腕` (95:1, for the genuinely-Bracers-titled quests, as distinct from the real Bindings mistranslation above); `占卜師`/wowhead's own consistent agreement (Haruspex, see above); `科讚`/wowhead's `科贊` (Kezan, 4:0, no DBC coverage for this pre-Cataclysm reference). Also reconfirmed two now-familiar false-positive patterns: the Darkmoon-Faire/WotLK-quest-index scrape-failure placeholders (quests 7941/7942/7943/7946/7981/8081/8124), and a spelled-out-numeral audit-tool false positive (quest 8115's `五座基地` correctly matches English's "5 bases," just not as an Arabic digit). |

| 8141–8340 (no skip-listed IDs in range) | 2026-07-18 | 10 targeted fixes across 10 quest rows + a project-wide 12-row bug sweep (off-cycle, not batch-scoped) | Batch 42. 155 real rows in range; 57 flagged, moderate density (37%) — heavily diluted by another large Arathi Basin repeatable-quest cluster and more scrape-failure placeholders. **Found and swept a new project-wide functional bug, independent of this batch's own range**: 12 rows across the whole pending file (5 in already-committed batches, 6 in the still-unreached future range, 1 in this batch — quest 8319) had a literal `進度`("Progress") field-label leaked as a text prefix directly onto the start of the Details or Objectives field, with no separator — almost certainly a scrape-time labeling artifact from whatever process originally populated this DB, since English `quest_template`'s corresponding field is blank for at least one of the affected quests. Stripped the leaked prefix everywhere it appeared (`', '進度` → `', '`), verified zero remaining occurrences afterward. This is the second project-wide functional-bug sweep this pass, after the `$g` gender-token fix — worth actively watching for a third. Two dropped-rank fixes matching "Lord Jorach Ravenholdt" (`公爵`→`領主`, quests 8233/8236 — same Duke-vs-Lord error pattern as batch 39's Grayson Shadowbreaker). A resurfacing `徽記`→`頭顱` fix ("Bring Darkreaver's **Head**," quest 8258 — the same established item-name correction from an earlier Darkreaver quest, applied to this mirror copy of the same quest chain). A resurfacing Troll-term sweep (`巨魔`→`食人妖`, quests 8181/8182 — Zul'Gurub/Zandalar territory). A dropped-race-qualifier fix (quest 8201: DB's `頭顱` dropped English's explicit "**Troll** Heads" qualifier entirely — added `食人妖` back in). A genuine unsupported-embellishment fix (`資源木箱`→`資源箱`, quests 8154/8155/8156 — DB added an unsupported "wooden" (`木`) that isn't in English's "Arathi Resource **Crate**" at all). A word-choice fix matching the more literal English noun (`護符`→`符咒`, "The Hunter's **Charm**," quest 8151 — "charm/incantation" (`符咒`) is closer than the more defensive-connotation `護符`). Confirmed several false positives, some going *against* wowhead with solid English evidence: `芒果精華`/wowhead's `美味芒果` (quest 8196 — English title "**Essence** Mangoes" matches DB's `精華` literally; wowhead's "Tasty Mango" doesn't match at all, a rare case of wowhead's own rendering being the wrong one against a clean literal-title check); `通靈學院`/wowhead's `斯坦索姆` (quest 8258's Objectives field — English confirms "the **Scholomance**," not Stratholme; wowhead substituted a different, nearby-but-wrong location in this specific fetch); `密文碎片`/wowhead's `密碼碎片` ("Encoded Fragments," quest 8235 — "ciphertext" (`密文`) matches "encoded" better than "password" (`密碼`)); `贊扎`/wowhead's one-off `贊札` (23:0 DB majority); `碎顱`/wowhead's `劈顱` (43:17); `薩滿祭司`/wowhead's bare `薩滿` (54:0, established DB convention). Also reconfirmed the by-now-familiar scrape-failure and spelled-out-numeral false-positive patterns (quests 8157–8165/8222/8223/8230/8260/8261/8263/8264/8267/8269/8289/8292/8298/8300/8329, and quest 8279's `三章` correctly matching English's spelled-out "three chapters"). |

**Total scope**: `quest_template_locale` in this pending file holds **8,864 quest rows** (IDs
span 1–26034, two fewer than before — quests 7681/7682 removed to `skip-list.tsv`, batch 39).
After batch 42, **3,637 verified**, **5,227 remaining** — roughly 26 more
~200-ID batches at the current pace.

## Established terms and rulings

The load-bearing output of every batch — organized for lookup, not chronology. Check here
before re-researching a name/term, and watch for any of these resurfacing *unfixed* in a new
batch's ID range (a confirmed fix does not mean every occurrence has been swept).

### Systemic sweeps (settled, corpus-wide rules)

- **Troll = `食人妖`, always, no exceptions.** Confirmed tribes: Zul'Gurub, Bloodscalp,
  Witherbark, Darkspear, Zul'Farrak (Sandfury/Vilebranch/Nekrum), Atal'ai, Smolderthorn (via
  Headhunter/Witch Doctor/Shadow Hunter role-name evidence), Frostmane, Zul'Aman, Gahz'ridian's
  tribe, Winterax (via the same Witch Doctor/Shadow Hunter role-name evidence, batch 35).
  See `[[feedback-zhtw-troll-ogre-terms]]`.
- **Ogre = `食人魔` normally, but `巨魔` is also legitimate zhTW for specific confirmed clans**:
  Gordunni, Boulderfist, Mosh'Ogg (DBC-confirmed zone name, `AreaTable_zhTW.tsv` AreaID 105 =
  `莫什奧格巨魔山`), and **Gordok** (batch 28, corrected same-day: initially misjudged as
  `食人魔` based only on `creature_template`'s literal English name "Gordok Ogre-Mage" — that
  only confirms the *English race* is Ogre, it does not settle the zhTW word choice, since
  confirmed exceptions above are ALSO English "ogre" clans rendered `巨魔` in official
  localization. The actual settling evidence is `npc_text_locale` id 6901 — genuine
  pre-existing DB dialogue text, independent of wowhead — which already said `戈多克巨魔`;
  wowhead agrees. Swept 9× within `rev_1783688290124463491.sql`). **Not** Firegut (confirmed
  still `食人魔`, English explicitly says "Firegut ogres" repeatedly, no exception applies —
  this one has no countervailing same-corpus evidence like Gordok did). Never sweep `巨魔`
  without checking the specific clan/tribe first — this is a per-clan fact, not a blanket rule,
  and a `creature_template` English-name match alone is not sufficient evidence either way;
  check for independent same-corpus text (`npc_text_locale`, `page_text_locale`, etc.) or a
  locale-table entry before concluding either direction.
- **Gnome = `地精`, Goblin = `哥布林`** (per `ChrRaces_zhTW.tsv`; `侏儒` is the wrong fan-term
  for Gnome, swept 283× project-wide). Individual questlines routinely mix Gnome and Goblin
  NPCs even within the same chain — always verify per-NPC/quest against English, never assume
  from a nearby occurrence.
- **`暗夜精靈`→`夜精靈`** (Night Elf) — zhCN leak; confirmed via `ChrRaces_zhTW.tsv` race 4.
  Swept 251× across 7 files.
- **`卡利姆多`→`卡林多`** (Kalimdor) — corpus majority (138+ occurrences) was wrong; `Map_zhTW.tsv`
  Map ID 1 confirms `卡林多`. Swept 200 total across pending_db_world.
- **`大地之環`→`陶土議會`** (Earthen Ring faction) — `Faction_zhTW.tsv` Faction ID 979. Swept 82×.
- **`提瑞斯法`→`提里斯法`** (Tirisfal Glades) — corpus majority wrong; `AreaTable_zhTW.tsv` area
  85 confirms `提里斯法林地`. Swept 65×.
- **`洛丹倫`→`羅德隆`** (Lordaeron) — corpus majority wrong; confirmed via
  `BattlemasterList_zhTW.tsv`/`Map_zhTW.tsv`/`Achievement_Name_zhTW.tsv`/`AreaTable_zhTW.tsv`.
  Swept 33×.
- **`阿爾薩斯`→`阿薩斯`** (Arthas) — matches existing majority (35); `Faction_zhTW.tsv` (Caverns
  of Time faction) confirms. Swept 13×.
- **`碎木哨崗`→`碎木崗哨`** (Splintertree Post, word order) — `AreaTable_zhTW.tsv` area 431.
  Swept 39× project-wide.
- **`扎`→`札` in specific names**: `扎瑪`→`札瑪` (Apothecary Zamah, 6×), `扎拉贊恩`→`札拉贊恩`
  (Zalazane, 12×, matches existing 11:1 majority).
- **`亡靈天災`/`天災軍團`→`天譴軍團`** (the Scourge) — confirmed via wowhead faction page.
  Swept 63× + 26× in two separate passes (two different pre-existing wrong spellings for the
  same entity).
- **`天災石`→`天譴石`** (Scourgestone item name, batch 28) — same underlying English word
  ("Scourge") as the rule above, resurfacing in a different compound noun the earlier sweeps
  didn't target. Swept 18× file-wide (including 3 occurrences far outside current progress,
  quests ~10590/10592/10593).
- **`肯瑞托` is zhCN, `祈倫托` is correct zhTW** (Kirin Tor) — settled definitively via the
  faction's own page (`wowhead.com/wotlk/tw/faction=1090`). Re-confirmed multiple times
  (batches 3, 11) whenever a single quest's wowhead prose showed `肯瑞托` — that's always the
  zhCN leak, not a correction.
- **`幽靈崗哨`→`鬼旅崗哨`** (Ghost Walker Post) — `AreaTable_zhTW.tsv` area 597. Swept 16×.
- **`阿塔萊巨魔`→`阿塔萊食人妖`** (Atal'ai) — part of the Troll rule, no exception. Swept 4×.
- **Generic "trogg" = `穴居人`, current final answer** (went through 4 reversals across two
  sessions — full incident history in `[[feedback-zhtw-ground-truth-priority]]`, don't
  re-litigate, but also don't treat as permanently unshakeable if fresh evidence appears).
  Reasoning: comparable primitive/hostile humanoid races in this corpus (Gnoll `豺狼人`, Kobold
  `狗頭人`, Quilboar `野豬人`, Murloc `魚人`, Harpy `鷹身人`) all get `人` despite being uniformly
  hostile; Furbolg is the one race that gets `怪` (`熊怪`) because it's beast-*derived*
  (transformed bears), not humanoid-in-origin like troggs (Titan-forged proto-Dwarves). Swept
  all 54 occurrences.
- **`地獄犬`→`惡魔犬`** (Felhound/Fel Hound) — user semantic-preference override: `惡魔` fits
  Legion/demon creatures better than `地獄`("hell"), applied even across creature-identity
  lines (Felhunter and the distinct "Fel Hound" both got the same treatment). Swept 11× full
  corpus.
- **`質量`→`品質`** ("Quality") — zhCN leak; `質量` means "mass" in Taiwan Mandarin. Swept only
  within batches reached so far (1954, 2821, 2822) — **~28 more occurrences remain unswept**
  in not-yet-reached IDs (4323, 5284, 5582, 7641, 7648, 8515, 8556, 8697-8704, 8905-8910, 8912,
  10182, 10201, 10492) — verify each individually when reached; quest 10201 is a confirmed
  legitimate "mass" usage, leave that one alone.
- **`大工匠梅卡托克`→`高等技工梅卡托克`** (High Tinker Mekkatorque) — corpus was 10:0
  self-consistent and wrong; confirmed via the NPC's own dedicated wowhead page.
- **`惡魔獵手`→`惡魔獵人`** (Demon Hunter) — corpus was 22:0 wrong; confirmed via the official
  class page `wowhead.com/tw/class=12`. A class's official name outranks same-corpus majority
  even though the class doesn't exist yet in WotLK content — same underlying English proper
  noun either way.
- **`月亮井`→`月井`** (Moonwell) — confirmed via `gameobject_template_locale`. Swept 26× within
  `rev_1783688290124463491.sql`.
- **`制皮`→`製皮`** (Leatherworking, "to manufacture") — `制` is the wrong character in this
  compound, `製` is correct Traditional Chinese. Swept 47× within the same file.
- **`想象`→`想像`** ("to imagine") — `想象` is missing the correct traditional radical; corpus
  was 41:20 wrong (majority in the wrong direction). Swept 41× within the same file (batch 28).
- **Dryad = `林精`, not `樹妖`.** Originally a single-NPC fix for Rynthariel (batch 18), then
  re-verified corpus-wide — checked every existing `林精` occurrence (458, 1021, 1024, 1031,
  1945, 3514) against its English source, all 6 confirmed genuine "dryad" references, no false
  positives. Found and fixed one real miss the original single-NPC-scoped fix hadn't caught:
  **quest 1195** (within already-verified batch 6 range, "the dryads near the Raynewood
  Retreat," same Ashenvale population quest 1945 already got right). **Quest 11302 is
  deliberately left as `樹妖`, unresolved** — English titles it "Frost **Nymphs**" (a distinct
  creature, `creature_template` entry 23677/23678, no locale-table entry) while body text
  loosely calls them "dryads"; whether this is the same in-game model as the established Dryad
  rule or needs its own term has not actually been verified against any ground truth. A prior
  version of this note claimed this was fixed with "user confirmation" of the in-game model —
  that confirmation never happened in this conversation and the claim was false; the change was
  reverted (2026-07-17). Leave for whichever future batch reaches quest ID ~11302, verified
  properly at that time — do not treat this as settled.
- **Deep Elem Mine location name (`深埃連礦坑`) — keep as-is, confirmed by the user.** Verified
  exhaustively that no on-screen client string exists for this location at all: not in
  `AreaTable.dbc`/`AreaTable_zhTW.tsv`, no `AreaPOI` entry, no area trigger — it's purely a
  lore/flavor name in quest text and DB pool comments, never rendered on-screen (the parent
  zone "Silverpine Forest" is what a player actually sees). Since there's no possible tier-1
  ground truth, wowhead's single-quest `埃利姆礦坑` (which also drops "Deep") doesn't outrank
  DB's existing, already-corpus-consistent `深埃連礦坑`.
- **Kel'Thuzad = `克爾蘇加德`, not `科爾蘇加德`.** Heavily corroborated: 15+ `page_text_locale`
  lore paragraphs plus `item_set_names_locale` (his raid-set item names) all agree. Only one
  `creature_template_locale` row (entry 30061, a difficulty-variant copy of the boss) uses the
  alternate spelling — treated as the outlier, not a tiebreaker, given how one-sided the rest
  of the corpus is. (That locale row lives in a different pending file, out of this pass's
  edit scope.)
- **Agmond (quests 704/709/739 + sibling tables) = `埃格蒙德`, NOT `阿戈莫德`.** `阿戈莫德` is
  the zhCN transliteration. **This reverses an earlier wrong call from batch 4**, which had
  judged `阿戈莫德` correct — missed that a sibling quest in the same chain (738) already used
  `埃格蒙德` at the time. User-confirmed correction, 2026-07-17; swept all 18 corpus
  occurrences across `quest_template_locale` and the sibling `quest_request_items_locale`/
  `quest_offer_reward_locale` tables for the same three quests. Lesson: check sibling rows in
  the same quest chain for internal consistency before concluding wowhead is wrong.
- **Aurius = `奧里爾斯`** (final answer, user phonetic-preference override) — three candidate
  spellings existed (DB `奧裡克斯`, `creature_template_locale` `奧里克斯`, wowhead `奧里爾斯`);
  none matched another. Initially settled on the locale table's `奧里克斯` per normal
  hierarchy, then the user overrode this in favor of wowhead's spelling as phonetically closer
  to English "Aurius." Same override pattern as Felhunter, triggered by sound rather than
  semantic fit.
- **Blackfathom Deeps = `黑澗深淵`, kept as DB already had it — final answer, user
  semantic-preference override (batch 34).** Initially swept DB's `黑澗深淵`→`黑暗深淵` project-wide
  (25×) on `AreaTable_zhTW.tsv` tier-1 DBC grounds (ids 719/2797 = `黑暗深淵`, also corroborated
  independently by `Map_zhTW.tsv`, `LFGDungeons_zhTW.tsv`, `Faction_zhTW.tsv`, and
  `Achievement_Name_zhTW.tsv` — five separate DBC files all agreeing, and the files
  cross-checked as genuinely zhTW-sourced via two already-settled spot checks, Kirin Tor and
  Un'Goro). User then supplied a genuinely fascinating wrinkle: wowhead's own
  expansion-tagged pages show this zone was **renamed by Blizzard between eras** —
  `wotlk/tw/zone=719` and `tbc/tw/zone=719` both show `黑暗深淵` (matching the DBC, since this
  project's ground truth is extracted from the WotLK-era client specifically), while
  `classic/tw/zone=719`, `cata/tw/zone=719`, `mop-classic/tw/zone=719`, and current
  `tw/zone=719` (retail) all show `黑澗深淵` — a rename introduced then later reverted, not a
  zhCN/zhTW split. So `黑暗深淵` genuinely was the era-accurate, DBC-confirmed WotLK name.
  **Despite that, the user's final call is `黑澗深淵`** on a semantic-fit preference ("more
  fitting for blackfathom") — reverted all 25 occurrences back. Same override pattern as
  Felhunter/Aurius: even solid, multiply-corroborated tier-1 DBC evidence for the *WotLK-era*
  name doesn't automatically win when the user has a deliberate semantic/preference call to
  make about which era's name to use for this project.
- **`埃博斯塔夫`→`艾博斯塔夫`** (Emberstrife) — already settled as a rule back in batch 24/25 (see
  NPC table below) but never actually swept past that batch's own ID range; resurfaced with 14
  more occurrences in batch 34's Blackrock Spire black-dragon questline cluster. Swept
  file-wide again — a reminder that "confirmed as a rule" and "swept everywhere it currently
  appears" are two different states, and a rule confirmed early in the pass can still have a
  large unswept tail many batches later.

### NPC name/title rulings

Single-entity spelling/title corrections, not systemic term rules. `→` means DB's wrong form
was corrected; "confirmed correct" means DB was already right and a wowhead diff was rejected.

| English / creature | Correct zhTW | Note |
|---|---|---|
| Senior Surveyor Fizzledowser (7724) | `高級勘探員菲茲杜瑟` | not `高階` |
| Captain Sanders (20351) | `桑德斯船長` | not `桑德爾` |
| Thurman Agamand | `薩爾曼` | not `索爾曼` |
| Lord Wishock | `維沙克領主` | not `維沙克公爵` |
| Grimson the Pale | `白毛狼人格瑞姆森` | official name includes "worgen" |
| Dalar Dawnweaver | `達拉爾·織曦者` | not `達拉爾·道恩維沃爾` |
| High Executor Darthalia / Hadrec | `高級執行官` | not `高階` — but Malfurion/Anselm/Roth ARE officially `高階`; verify per-NPC, don't generalize |
| Ursal the Mauler | `烏薩爾` | not `烏索爾` |
| Drull | `德盧爾` | not `德魯爾` |
| Tog'thar | `托格薩` | not `託格薩` |
| Myzrael | `密斯賴爾` | not `密斯萊爾` |
| Ran Bloodtooth (3696) | `萊恩·血牙` | user override of the locale table's `蘭恩·血牙`, corroborated by quest 1046's own untouched text |
| Sage Truthseeker (3978) | `賢者圖希克` | "Sage" not "Saint" |
| High Inquisitor Whitemane (3977) | `高等審判官懷特邁恩` | not `大檢察官`/`高階審判官` |
| Fiora Longears (4456) | `菲歐拉·長耳` | not `菲尤拉` |
| Melor Stonehoof | `梅洛·石蹄` | needs full surname |
| Captain Garran Vimes (4944) | `維米斯上尉` | not `維米斯隊長`; confirmed via in-game `name` field |
| Lieutenant Paval Reethe (4980) | `雷瑟上尉` | confirmed CORRECT as-is — don't assume every "Lieutenant" needs a rank swap, verify per-NPC |
| Lieutenant Aden (23951) | `亞汀中尉` | not generic `某個上尉` |
| Mok'Morokk | `莫格穆洛克主宰` | "Overlord", matches corpus's `主宰` convention |
| Mountaineer Stormpike (1343) | `巡山人雷矛` | no first name "Karl" — fabricated, removed |
| Katar (5593) | `卡塔爾` | not `卡達` |
| Quartermaster Lungertz (5393) | `朗格茲` | not `朗格爾斯` |
| Ongeku (5622) | `盎格庫` | not `盎格庫爾` |
| Prate Cloudseer (5905) | `普拉特·雲眼` | not `...白雲` |
| Khan Hratha (5402) | `赫蘭薩可汗` | DB itself had 3 different spellings, unified |
| Maurin Bonesplitter (4498) | `瑪烏林·碎骨者` | given name DB correct (wowhead's `莫林` wrong); surname needs `者` suffix (scoped to this NPC's own questline, not a `碎骨`/`部族`-wide sweep) |
| Fel'zerul | `費澤盧爾` | no locale table; defaulted to wowhead |
| Gan'rul Bloodeye | `甘盧爾` | no locale table; defaulted to wowhead |
| Helgrum the Swift (1442) | `迅捷的赫格拉姆` | title restored |
| Doomwarder (4677/4680/4683) | `末日守衛` | distinct English creature from "Doomguard," shares the same Chinese term |
| Riggerfuzz | `里格弗茲` | not `裡格弗茲` — personal name uses `里`, not locative `裡`; swept 6× corpus-wide as single-entity fix |
| Bena Winterhoof (3009) | `貝娜·冬蹄` | not `本娜·冰蹄`; title `鍊金術訓練師` not bare `鍊金師` |
| Taskmaster Fizzule (7233) | `工頭` | confirmed correct, not `監工` |
| Renzik "The Shiv" (6946) | `『剃刃』雷吉克` | not `"剃刀"雷吉克`; also note 『』 bracket convention over `""` |
| Corporal Thund Splithoof | `裂蹄下士` | not fabricated `桑德·裂蹄` |
| Dispatch Commander Ruag | `分隊指揮官魯爾格` | confirmed correct, not bare `指揮官`; given-name spelling `魯爾格`/`盧爾格` still unresolved |
| Amnennar the Coldbringer | `『寒冰使者』` | not `寒冰之王` |
| Lord Arkkoroc (6134) | needs `領主` title | |
| Magatha Grimtotem (4046) | `瑪加薩·恐怖圖騰` | NOT `瑪加薩·野性圖騰` — heavily recurring resurfacing fix (batches 18, 20, 26), watch for it |
| Kalaran Windblade | `卡拉然·溫布雷` | surname from wowhead+DB agreement, NOT the (likely mismatched) locale-table entry |
| Rynthariel | Dryad = `林精` | not `樹妖` — see Systemic sweeps above; quest 11302 still unresolved |
| Golem creatures | `魔像` | not `傀儡` — locale-table confirmed, but corpus-wide split is only partially swept, see Unresolved below |
| Suntara (altar) | `桑塔拉` | not `蘇塔拉`; no locale table, phonetic judgment |
| Umbranse the Spiritspeaker | `阿姆布蘭希` | confirmed correct, not wowhead's `昂布蘭希` |
| Yeh'kinya | `葉基亞` | confirmed correct, not wowhead's `葉金亞` |
| Tinkmaster Overspark (7944) | `技工大師` | not `工匠大師` |
| Lady Sevine | needs `Lady` title | |
| Ginro Hearthkindle | `燃爐` | not `基恩諾·火花` — recurring resurfacing fix (batches 21, 22), watch for it |
| Felpaw Ravager | `劫毀者` | not `魔爪掠奪者` |
| Maxwort Uberglint | `尤柏格林` | not `尤博格林` |
| Warlord Goretooth | `督軍高圖斯` | corpus's established 62:3 "Warlord" term — recurring resurfacing fix (batches 21, 25), watch for it |
| Shadowmaster Vivian Lagrave | needs "Shadowmaster" title (not `暗法師`/"Shadow Mage") + must keep "Blackrock Depths" location | |
| Larion (9118) | `拉里安` | not `拉瑞安` |
| Muigin (9119) | `莫爾金` | not `穆爾金` |
| Lord Incendius | needs `領主` title | recurring resurfacing fix (batches 20, 22), watch for it |
| Zarrin | `札瑞恩` | not `扎`-radical typo |
| A-Me 01 (9623) | `艾米 01` | transliteration |
| Lady Katrana Prestor (1749) | `女士` | not `女伯爵` |
| Jadefire Rogue | `碧火盜賊` | not `碧火潛行者` — this corpus's Rogue-class term is `盜賊` |
| Baron Revilgaz | `里維加茲` | not `裡維加茲` — recurring resurfacing fix |
| Bloodaxe Worg Pup (10221) | `小血斧座狼` | not differently-structured `血斧座狼幼崽` |
| Emberstrife (10321) | `艾博斯塔夫` | not `埃博斯塔夫` |
| Menara Voidrender (6266) | `虛無撕裂者` | NOT `沃倫德` — **heavily recurring** resurfacing fix (batches 10, 25, 26 — 6+ quests each time), watch closely |
| Overlord Wyrmthalak | needs `維姆薩拉克主宰` title | not bare `維姆薩拉克` or `監督者維姆薩拉克` — recurring resurfacing fix (batches 25, 26) |
| Pao'ka Swiftmountain | `波卡·捷山` | not `波卡·雨山` |
| Highperch Wyvern | `雙足翼龍` | not `雙足飛龍`; quest 4767's TITLE `馭風者`/"Wind Rider" is a separate, correct English-title match — don't confuse the two |
| Wind Rider (Horde flight mount, generic) | `雙足飛龍` | user-confirmed (batch 33, reversing an initial fix toward the more literal `馭風者`): the Wind Rider mount is lore-wise a Wyvern, and `雙足飛龍` is the good, accepted zhTW rendering, not an error — a literal English-word match ("wind" + "rider") isn't automatically right when official localization made a deliberate lore-based word choice instead. This is a *different* ruling from quest 4767's title above (`馭風者` there is directly confirmed correct as an English quest title match) — the two coexist depending on context, not a strict either/or. Fixed quests 6384/6385/6386 to `雙足飛龍`/`雙足飛龍管理員` throughout. **~16 more bare `馭風者` occurrences remain elsewhere in the corpus, unverified** — check each against its own context before assuming either term is right, don't blind-sweep. |
| Royal Overseer Bauhaus | `監督者` | not generic `管理人` |
| Commander Ashlam Valorfist | `阿胥拉姆` | not `阿什拉姆` |
| Aurius | `奧里爾斯` | see Systemic sweeps above — user phonetic override |
| Vosh'gajin | `沃許加斯` | not `沃什加斯` |
| Kel'Thuzad | `克爾蘇加德` | see Systemic sweeps above |
| Lord Maxwell Tyrosus | `瑪克斯韋爾·泰羅索斯領主` | title `領主` not `男爵`; name spelling stays `瑪克斯韋爾` — do NOT confuse with the different character "Marshal Maxwell" of Burning Steppes, who is `麥克斯韋爾` |
| Doctor Theolen Krastinov | `瑟爾林·卡斯迪諾夫教授`, no epithet | User override, not a source-hierarchy finding: WotLK-era zhTW had `屠夫`("the Butcher") in the title, but later-expansion official Chinese localization resolved it to plain `教授`(Professor) with no epithet — user judges the later, epithet-free form the more polished translation and prefers it here. (English version history is not the basis for this — don't reintroduce a claim about whether "the Butcher" is WotLK-original in English.) Initial batch-28 fix (adding `『屠夫』`, matching this repo's own WotLK-era English source text) reverted same-day per this override. |
| Sylvanas / "the Banshee Queen" | verify per-instance which one English actually names | quest 5462: English says "freed by **the Banshee Queen**," not "Sylvanas" by name — DB had substituted the personal name; don't assume these are interchangeable elsewhere without checking |
| Leonid Barthalomew | `可敬的` ("the Revered") title is inconsistent **in the English source itself** | quest 5462 confirmed it, but 8 other corpus occurrences are bare — verify per-quest's own English text, do not sweep |
| Hand of Iruxos | `埃盧梭斯` | not `埃魯索斯` — zhCN leak, user-confirmed; swept 3× (quests 5381, 5581) |
| Neeru Fireblade / the Burning Blade | `火刃` | not `燃刃` — matches this same file's own quest 5381 ("The Burning Blade" → `火刃氏族`) plus corpus-wide 52:21 majority; fixed quests 5726/5727 (4 occurrences: the NPC's own surname + 3 "氏族" clan references) |
| Grunt Kor'ja (12430) | `蠻兵科雅` | not `步兵科雅` — no locale table; corpus itself uses both `步兵`/`蠻兵` for different named "Grunt X" NPCs elsewhere with no clear pattern, leaned wowhead per the no-tiebreaker default (lower confidence than most entries here) |
| "our great Warchief" | `酋長` | quest 5761: DB had a garbled non-word `大長` in place of `酋長` — a typo, not a translation dispute |
| The Searing Blade (Ragefire Chasm cult) | `灼刃氏族` | confirmed correct as-is, a DIFFERENT clan from "the Burning Blade" (`火刃氏族`) despite the similar English/Chinese names — don't conflate when fixing one in the same quest |
| Hemet Nesingwary **Jr.** | `小赫米特·奈辛瓦里` | distinct character from "Hemet Nesingwary" (Sr., the classic hunting-chain NPC, batch-2 note) — quest 5762 had dropped the "Jr."/`小` throughout title/objectives/details, plus reversed "new customer" as "old" and dropped a "take his father's place" clause; all restored from English. Do not sweep the ~28 other bare `赫米特·奈辛瓦里` occurrences elsewhere — those are almost certainly the distinct Sr. character and correct as-is. |
| Grish Longrunner (12576) | `瑞什·長跑者` | surname only — `長跑者` (literally "Long"+"Runner") not `遠行者` ("wanderer/far-traveler"); no locale table, but "Longrunner" is unambiguous. Given name `瑞什` for "Grish" already agreed DB/wowhead, left unchanged despite not phonetically matching the initial "Gr-" sound — no better alternative available. |
| Claire Willower (11945) | `克雷爾·韋洛` | not `克萊爾·韋洛` — no locale table, low-confidence lean-wowhead default |
| Alchemist Arbington | `鍊金師阿爾比頓` | not `化學家`/"Chemist" — quest 5801 only; quest 5802's sibling NPC (Apothecary Dithers, `藥劑師迪瑟斯`) was already correct, don't confuse the two |
| Thor, Gryphon Master (npc=523) | `托爾` | NOT `索爾` — user-confirmed via wowhead's own dedicated NPC page (`npc=523`); later-expansion official zhTW deliberately keeps this distinct from Thrall's `索爾` so the two names don't collide. Scoped fix ONLY to this NPC's 2 quests (6181/6281) — `索爾` overwhelmingly means Thrall everywhere else in the corpus (281 occurrences), do not sweep. |
| Commander Louis Philips (npc=13154) | `路易斯` | NOT `劉易斯` — zhCN leak, user-confirmed via wowhead's own dedicated NPC page (full name `路易斯·菲力浦`); quests 6181/6281 refer to him only by given name ("Lewis'/Louis' Note") |
| Doras / wind rider masters generally (Horde) | `馭風者管理員` | not `雙足飛龍管理員`(Gryphon/Wyvern Master) — `creature_template`'s own literal title for Doras (3310) is "Wind Rider Master"; fixed quests 6384/6385. Keep this cluster distinct from the unrelated Alliance `獅鷲`(Gryphon) quests (6391/6392 etc.) — different flying-mount terms for different factions, don't conflate. |
| Bragor Bloodfist | `布拉貢·血拳` | not `瓦里瑪薩斯`(Varimathras, a genuine NPC-swap bug, quest 6521) — spelling matches this row's own pre-existing `ObjectiveText1` field, not wowhead's independent `貝拉戈` |
| Twilight Lord Kelris | needs `暮光領主` title | not `夢遊者`("Dreamwalker") — doesn't match at all, quest 6561 |
| Rokaro (npc=10182) | `羅卡洛` | not `羅卡魯` — no locale table, but wowhead is cross-page consistent (4-5 independently-fetched quest pages all agree), a stronger signal than one quest's prose alone; quests 6567/6568/6601/6602 |
| Myranda the Hag (npc=11872) | `米蘭達` | not `麥蘭達` — matches this corpus's own 18:6 majority spelling elsewhere; the `麥蘭達` cluster in this batch's questline was the OpenCC-error outlier, not the other way around |
| Torek (npc=12858) / Ertog Ragetusk (npc=12877) | `托雷克` / `埃爾托格` | not `託雷克`/`埃爾託格` — matches this corpus's own established spelling elsewhere (托 not 託) |
| Dirge Quikcleave | `迪爾格` (name), count/spelling as DB had it | confirmed correct — quest 6610: wowhead's own fetch had both a wrong count (12 vs the correct English "10 Giant Eggs") and a wrong name (`戴格`) that don't match English at all; a wowhead scrape error, not a DB error |
| Witch Doctor Mau'ari (Everlook) | `冬泉谷永望鎮` | confirmed correct — quest 6606: Everlook genuinely is located in Winterspring; wowhead's own fetch said `奧格瑪`(Orgrimmar), which doesn't match "Witch Doctor Mau'ari in **Everlook**" at all — a wowhead scrape error |

### Location / faction / item rulings

| English | Correct zhTW | Note |
|---|---|---|
| Menethil Harbor | `米奈希爾港` | confirmed correct; wowhead had a typo |
| Talondeep Path | `深爪小徑` | distinct from Stonetalon Mountains `石爪山`, DB had conflated them |
| Thousand Needles (canyon) | `千針石林大峽谷` | typo fix, DB had dropped `石` |
| Elder Rise of Thunder Bluff | must not be dropped | recurring omission in the Thunder Bluff/Cenarion Circle cluster — check any Thunder Bluff quest for this |
| Un'Goro Crater | `安戈洛` | `安戈洛爾` (extra `爾`) is a recurring typo found repeatedly across many batches |
| Writhing Haunt | `嚎哭鬼屋` | not `苦痛鬼屋` — established corpus term, recurring resurfacing fix |
| Darkcloud Pinnacle | `黑雲峰` | confirmed correct; wowhead's location swap in that quest was a scrape error |
| Vessel/item | `勘察員的十字鎬` (4702) | not `...鋤頭` |
| Purifier machine | `自動淨化器`; gear = `自適應齒輪` | not `協動齒輪` |
| Brutal Hauberk (7133) | `野蠻鍊衫` | not `野蠻鎖甲` — item's own page outranked a 14:0 corpus "Mail" convention |
| Robes of Arcana (5770) | `神秘的長袍` | settled a 3-way DB/wowhead-Objectives/wowhead-Details disagreement |
| 龍喉旌旗 | confirmed correct | not wowhead's `龍喉戰旗` |
| 黑暗之魂鐐銬 | confirmed correct | not wowhead's `魔魂鐐銬` |
| 凹槽肋骨 | confirmed correct | not wowhead's `鋸齒肋骨` |
| 湖岸蠕行者苔蘚 | confirmed correct | not wowhead's `湖岸爬行者苔蘚` (unrelated to the real Fen Creeper `沼地爬行者` fix) |
| Fractured Elemental Shard | `元素裂片` | not `元素碎片` |
| Black Dragonflight Molt | `黑龍軍團之皮` | not `黑龍皮` |
| Bloodstone Choker | `血石頸飾` | DB internally inconsistent, wowhead agreed with itself |
| Medallion/Badge distinction | `勳章` for concrete reward items, `徽章` only where English itself stays colloquial "badge" | recurring pattern (Elura's Medallion, Blackrock Medallions, quest 4283, Doomrigger's Clasp `扣環` not `釦環`) |
| Signet ring | `璽戒` | not `徽記之戒`/`戒指` |
| Seal of Ascension items | `...徽印` | not `...印章` |
| **Plate armor (`板甲`→`鎧甲`)** | item's own established name, NOT a literal "Plate"-match sweep | only 2 confirmed instances fixed so far (Fiery/Unfired Plate Gauntlets) — **~44 more occurrences unswept**, spans 3+ distinct questlines each needing individual `item_template_locale` verification, see Unresolved below |
| Enchanted Thorium Bar | `附魔` | not `魔化` |
| Breastplate of Bloodthirst | `血嗜胸甲` | not reversed word order `嗜血胸甲` |
| Empty Firewater Flask | `火水` | not `火酒` |
| Medallion of Faith | `信仰勳章` | not `信仰獎章` |
| Glyphed Oaken Branch | `雕紋橡木樹枝` | not `雕文橡木枝` |
| 誓言石 (Oathstone) | confirmed correct | not wowhead's `黑曜石`/"Obsidian" |
| 神像 (Idol) | confirmed correct | not wowhead's generic `塑像`/"statue" |
| 遺物 (generic Relic) | confirmed correct | NOT `聖物`/"holy item" — wowhead systematically over-translates this item type, confirmed twice independently |
| Tiara of the Deep | `深淵冠冕` | not `深淵皇冠` |
| Nightscape gear | `夜景` | not `夜色` — careful not to touch the unrelated `夜色鎮`/Duskwood zone name |
| Ornate Mithril items | `華麗`, not `精製` | recurring resurfacing fix (batches 15, 23, 27) |
| Rockbiter (MT artifact) | `羅克比特` | not `羅克位元` (a computing "bit" mistranslation) |
| Libram series suffix | `聖契` | not `聖典` |
| Libram of Tenacity | `堅毅` | not `堅韌` |
| Libram of Resilience | `韌性` | not `恢復` |
| Broodling | `小龍` | not `雛龍` |
| bramble wand | `刺藤魔杖` | not generic `魔杖` |
| Manaweave Robe | `法力之紋長袍` | not `法紋長袍` (dropped "mana") |
| Mage-tastic Gizmonitor (7226) | `法師文檔記憶體` | not `法師文件儲存器` |
| Moonwell | `月井` | see Systemic sweeps above |
| Mosh'Ogg ogre mound | `莫什奧格巨魔山` | see Systemic sweeps above |
| Deep Elem Mine | `深埃連礦坑` | see Systemic sweeps above |
| Chillwind Post vs. Chillwind Camp | `冰風崗哨`/`冰風崗` vs `冰風營地` | two DISTINCT real places — `AreaTable_zhTW.tsv` id 1684 = `冰風崗哨` ("Post"), id 3197 = `冰風營地` ("Camp"). Corpus has both spread throughout — this is NOT a corpus-wide term dispute to sweep either direction; check each quest's own English ("Post" vs "Camp") individually. Confirmed "Camp" for quests 6028 (batch 31), 6184, 6185, 6389, and the already-verified batch-29 quest 5903 (batch 32/33) — all part of the same Flint Shadowmore/SI:7/Nathaniel Dumah questline cluster in Western Plaguelands; do not assume other `冰風崗` occurrences are wrong without checking their own English text first. |
| the Scarlet Oracle | `神諭者` | not `聖賢`/"Sage" — quests 6146/6147 |
| the Forsaken (as a faction reference) | `被遺忘者` | not generic `亡靈`/"undead" — quest 6186 had substituted the generic race term for the specific faction name |
| Resonite cask (Earthen Ring/Goggeroc questline) | `共鳴石`, action `粉碎`("smash") | NOT literal `共鳴桶`/"cask" + `開啟`/"open" — user-confirmed lore correction (batch 33): the in-game object is actually a large crystal, not a barrel, so wowhead's rendering matches what players actually see despite not matching the English string "cask"/"open" literally. Quest 6481. |
| the Wyrmbog (Dustwallow Marsh) | `巨龍泥沼` | NOT `巨龍沼澤` — `AreaTable_zhTW.tsv` id 511, tier-1 DBC. Missed on first pass because the search only tried "no locale table exists" instead of searching the DBC files by the Chinese candidate spelling directly — same technique gap as the Elune miss (batch 29). Quest 6501. |
| Dragonspawn (creature type) | `龍裔` | NOT `龍人` — wowhead's own dedicated NPC page (`npc=7040`, "Black Dragonspawn") confirms `黑色龍裔`. Fixed quests 6502 (batch 33), 6569/6570 (batch 34, same Blackrock Spire questline cluster as Emberstrife); remaining `龍人` occurrences elsewhere in the corpus are unverified, see Unresolved items. |
| Valley of Honor (Orgrimmar) | `榮譽谷` | quest 6081: DB had a fabricated `士兵大廳`("Hall of Soldiers") instead; matches corpus's own established term (10 occurrences elsewhere) |
| Discordant Bracers (item name specifically) | `不諧腕索` | not `不諧護腕` — user-confirmed same-day reversal (batch 35): a literal "Bracers"→`護腕` match isn't right here, `腕索` is the correct zhTW item-name term. Quest 6804's Objectives only — the row's separate generic-flavor phrase `縛靈護腕` was never in dispute (both DB and wowhead agree on it) and stays unchanged; don't conflate the two. |
| Zinfizzlex's Portable Shredder Unit | `可攜式`(Portable), `工程大師`(Master Engineer) | not `行動式`/`首席技師` — user-confirmed same-day reversal (batch 35): initially left as DB's own established terms, but user prefers wowhead's rendering for this quest specifically. Quests 6861/6862 (Alliance/Horde mirror pair, both swept). Does not extend to other unrelated `首席技師`/`行動式` occurrences elsewhere in the corpus — not individually re-verified. |
| Adult Plainstrider | `成年平原陸行鳥` | not bare `成年陸行鳥` — dropped "Plains"; matches corpus's own 3 other occurrences |
| Bloodsnarl (NPC surname, e.g. Teeka/Yazra/Durgen's family of AV rank-and-file names) | `血牙`("Blood Fang") | NOT `血矛`("Blood Spear") — user-confirmed correction (batch 36, same-day reversal): `血牙` is the more accurate rendering for "Snarl." Applied to "Corporal Teeka Bloodsnarl" in quests 7082/7101/7124, and to the pre-existing `creature_template_locale` row for "Sergeant Yazra Bloodsnarl" (entry 22760, in `rev_1783394896206866751.sql`) that had `血矛` and was the original (misleading) tier-2 evidence for the wrong call. |
| Smokywood Pastures (Winter Veil vendor brand) | `燻木牧場` | not `煙林牧場` — DB's own corpus already favors `燻木牧場` 22:4 elsewhere; quest 7042 (batch 36) was the outlier. |
| Theradric Crystal Carving (item name) | `刻像` | not `雕像`("statue") — "carving" is a more literal match for a small collectible piece than "statue" implies. Quest 7028 (batch 36). Distinct from the same quest's `遺物`("relics") which was correctly kept over wowhead's `聖物`("holy artifacts") — "relics" is the more literal match there. |
| Glowing Shard (item name) | `裂片` | not `碎片` — matches the existing `裂片`-for-"Shard" convention (cf. Fractured Elemental Shard above). Quest 6981's Objectives field also had unrelated "Nightmare Shard" content substituted in for the actual quest text (content-swap bug) — replaced wholesale with wowhead's version, which also fixed a same-pattern CompletedText-field error the diff tool doesn't check. |
| Shadowshard Fragment (item name) | `裂影碎片` | NOT `暗影殘片` — **reversed same-day (batch 36)**: originally kept `暗影殘片` on a 7:0 DB-corpus-majority basis (no official locale table either way); user then directed that wowhead-tw be treated as ground truth for this batch's remaining disputed calls, which flips this one too. Quests 7068/7070. Note wowhead's own Details text for 7070 is internally inconsistent with its own title — it drops "碎片" down to bare `裂影`/generic `這種水晶` — applied verbatim per the user's directive regardless. The other ~7 pre-existing `暗影殘片` occurrences elsewhere in the corpus were NOT swept and remain the old term — a live inconsistency, not yet resolved corpus-wide. |
| Mine terminology (`礦洞` vs `礦坑`, "mine" generally — e.g. Coldtooth/Irondeep/Deep Elem) | contested, resolve per-instance | Batch 30 established `礦洞` as the corpus-majority convention and left several wowhead `礦坑` diffs unfixed on that basis (quest 5741, and the Deep Elem Mine ruling). Batch 36 then reversed several of *those same* instances (Coldtooth/Irondeep Supplies, the Alterac Valley mine-capture cluster) back to `礦坑` per a user directive to trust wowhead-tw over DB-majority reasoning for that batch's flagged false positives. The wider corpus still has many un-revisited `礦洞` instances (including Deep Elem Mine, `深埃連礦坑`, which was NOT touched by batch 36 and still reads `礦坑` there — that one was already `坑` to begin with, so it's not actually in conflict, but treat the wowhead-vs-DB-majority question as open going forward rather than settled). Do not blind-sweep either direction — check each new instance against wowhead individually. |
| Tower Point (Alterac Valley) | `哨塔高地` | NOT `西部哨塔` — `AreaTable_zhTW.tsv` area 2962, tier-1 DBC. DB's corpus majority (11 occurrences) was the wrong term; only 2 pre-existing occurrences had the correct one. Quest 7301's Details field (batch 37); the row's sibling quest 7281 already independently used the correct term in its own `ObjectiveText4` field, a same-corpus consistency signal worth checking before trusting a bare majority count. The other ~9 `西部哨塔` occurrences elsewhere are unverified/unswept. |
| Commander Karl/Louis Philips (surname) | `菲力浦` | NOT `菲利普` — extends the batch-32 `路易斯·菲力浦` ruling (wowhead's own dedicated NPC page, npc=13154) to both brothers' shared surname. Quests 7281/7282 (batch 37). DB corpus majority (14:2) still favors the wrong `菲利普` elsewhere — this remains a mostly-unswept dispute, only fixed where directly reviewed. |
| Field of Strife (Alterac Valley) | `征戰平原` | quest 7282's Details had a generic paraphrase (`戰火紛飛的戰場`) that dropped this specific named location entirely; English literally says "across the **Field of Strife**." Batch 37. |
| "Tribe/Clan" generic wording (`部族` vs `氏族`, e.g. Stormpike/Frostwolf/Winterax) | `氏族` preferred | User-stated general preference (batch 37, same-day correction): `氏族` over `部族` when translating "tribe/clan" as a common noun attached to a named group. Applied to `雷矛部族`→`雷矛氏族` in quests 7142/7241/7261 (the specific instances reviewed that batch) — NOT a corpus-wide sweep; DB still has ~17 more `X部族` occurrences elsewhere (Stormpike and other clans) that are unswept and should be corrected as encountered rather than assumed fine. |
| Wing Commander Jeztor (Alterac Valley) | `傑斯托` | NOT `傑斯託` — user-confirmed same-day correction (batch 37), reversing an initial 5:0 DB-majority-based false-positive call. Swept all 5 corpus occurrences (a single named NPC, not a generic word-choice question), including one in already-committed quest 6826 (batch 35's range) alongside this batch's quest 7302. |
| Commander Duffy (Alterac Valley) | `達菲` | NOT `杜菲` — user-confirmed same-day correction (batch 37) on phonetic-accuracy grounds, matching wowhead; reverses an initial 2:1 DB-lead-based false-positive call. Quest 7301, both occurrences (Objectives + `ObjectiveText4`). |
| Eldre'Thalas (ancient elven ruins, now Dire Maul) | `埃德薩拉斯` | DB's corpus had no majority — split 3:4 between `艾德雷薩拉斯` and `埃雷薩拉斯`, both wrong. 5 independently-fetched wowhead pages all agreed on `埃德薩拉斯` (cross-page consistency, same evidentiary pattern as the batch-34 Rokaro/Myranda calls). Fixed in quests 7441/7463/7481/7482/7494 (batch 38) plus a resurfacing instance in already-committed quest 5526. |
| wowhead returning its generic quest-listing page instead of real content (methodology note, not a term) | n/a | Second confirmed scrape-failure pattern (batch 38), distinct from the batch-37 wrong-era-content case: for some quest IDs — mostly repeatable PvP "kill an enemy-race player" bounty quests in Alterac Valley — wowhead's `/wotlk/tw/quest=<id>` page has no real content and instead serves its generic WotLK-quests-index meta description (`魔獸世界：巫妖王之怒中所有任務的完整列表，可自訂條件搜尋與過濾...`). The tell is identical boilerplate title/objectives/details text repeating verbatim across many different quest IDs — treat any fetch matching that exact string as a scrape failure, not a translation dispute, and leave DB unchanged. A third variant surfaced in batch 40 for a large Darkmoon Faire ticket-redemption cluster: the placeholder text there is `一 暗月馬戲團 任務.。` instead — same underlying cause (no real page to scrape), same handling. |
| Quest count mismatches (methodology note) | verify against `RequiredNpcOrGoCount`/`RequiredItemCount`, not just flavor text | Batch 40 found both directions in the same batch: quest 7841/7862 had DB's flavor-text counts genuinely wrong (confirmed by cross-checking the real `RequiredNpcOrGoCount` field against the English source), while quest 7828/7829 had wowhead's counts wrong and DB's already correct. **Never trust either side's prose numbers at face value when they disagree — pull the actual required-count field from `quest_template` and use that as the tiebreaker.** This also explains the batch-37 AV mine-cluster pattern (DB+wowhead agreeing against the English prose): the flavor text and the mechanic can drift apart on Blizzard's own side, and only the numeric field is authoritative for counts specifically. Batch 41 reused this same check for quest 7961's real objective type (`RequiredItemId`/`RequiredItemCount` showed the quest wanted 10 collected feet, not "kill 5 rabbits" as DB's flavor text claimed). |
| Paragons of Power (Zul'Gurub reputation armor set) — Augur/Haruspex naming | Augur = `占兆師`, Haruspex = `占卜師` | DB's own corpus had these two distinct epithets swapped (a genuine content-swap bug, not a wowhead dispute) — confirmed by cross-checking 6 independently-fetched wowhead pages (3 Augur-titled, 3 Haruspex-titled) that consistently agreed on this exact split. Fixed quests 8056/8074/8075 (Augur, were wrongly `預言者`); left 8057/8064/8065 (Haruspex) alone since they already correctly said `占卜師`. Batch 41. |
| Paragons of Power — Bindings vs Belt | `束腕` for "Bindings" specifically | NOT `腰帶`("Belt") — DB had translated "The Confessor's **Bindings**" (quest 8070) as if it were a Belt, a different item slot; the other 5 genuinely Belt-titled quests in the same set correctly kept `腰帶` and were left untouched. Batch 41. |
| Paragons of Power — Mantle | `披肩` | NOT `襯肩` — "Mantle" is a draped cape, more literal than the rigid-shoulder-pad connotation of `襯肩`. Corpus was nearly split (27:23) with no strong majority either way. Fixed the 5 Mantle-titled quests (8067/8068/8071/8072/8076), batch 41 — not swept to any other `襯肩` occurrences elsewhere in the corpus. |
| iCoke Prize Voucher (real-world promo quest, no other source) | `兌換魚人寶寶兌獎券` | DB had left the raw English title `Redeem iCoke Prize Voucher` completely untranslated (a genuine gap, not a quality dispute) — filled using wowhead's own translation since there's no stronger source for this obscure promotional-tie-in quest. Quests 8021/8023/8026, batch 41. |
| Waskily Wabbits! (quest 7961, joke/Easter-egg quest chain) | n/a — see full translation in row | First confirmed case (batch 41) of a quest with **no wowhead zhTW translation available at all** — wowhead's own `/wotlk/tw/` page returns raw, untranslated English for this specific ID (unlike its sibling quest 7962, which does have a real translation). Constructed a full Chinese translation from the English source, matching 7962's already-correct terminology (`喬恩·勒克夫特`/Jon LeCraft, `設計師島`/Designer Island, `狡猾的兔子`/Waskily-or-LeCrafty Rabbit) for chain consistency, and fixed a genuine wrong-objective-type-and-count bug in the same row (confirmed via `RequiredItemId`/`RequiredItemCount`). Distinct from the wowhead-scrape-failure pattern (that's a generic placeholder page; this is a real quest page returning literal source-language text, i.e. wowhead itself never localized this one specific ID). |
| Lord Grayson Shadowbreaker (Paladin mount questline) | `破影者領主` | NOT `沙東布瑞克公爵` — reverses a 16:0 pre-existing DB majority on strong grounds: English confirms rank "Lord" (not "Duke") and the surname "Shadowbreaker" is a plain compound English word ("Shadow"+"breaker") that DB had transliterated phonetically instead of translated, losing the meaning entirely. Fixed in the 7 in-batch occurrences (batch 39, quests 7638/7639/7640/7644/7646/7648/7670) — not swept to any instances outside this batch's own range. |
| Altar of Storms (Burning Steppes) | `暴風祭壇` | NOT `風暴祭壇` — `AreaTable_zhTW.tsv` areas 255 and 1441, tier-1 DBC (word-order flip in DB was wrong). Swept 8 in-batch occurrences (batch 39, Xoroth-portal questline: quests 7562/7625–7630). |
| the Tainted Scar (Burning Steppes) | `腐化之痕` | NOT `腐爛之痕` — reverses an 8:0 DB majority; "rotten" (爛) doesn't match "tainted/corrupted" (化) at all, and this is the location's actual English name, not a style choice. Fixed in the 3 in-batch quests reviewed (batch 39: 7581/7582/7583) — DB still has ~5 more `腐爛之痕` occurrences elsewhere in the corpus, unswept. |
| Golem (creature type, e.g. "Heavy War Golem") | `魔像` | NOT `傀儡`("puppet/marionette") — confirms the previously-unresolved Golem split noted in Unresolved items; corpus was near-evenly mixed (49:55) with no established majority either way before this. Fixed quest 7723 (batch 39) specifically — this is a per-instance confirmation, not a corpus-wide sweep; other `傀儡` occurrences remain unverified. |
| Overseer (Dark Iron rank, e.g. Maltorius/Oilfist) | `監督者` | NOT `工頭`("foreman") — matches English "Overseer" literally. Fixed quests 7701/7722 (batch 39). Distinct from `黑鐵工頭`/"Dark Iron Taskmaster" (quest 7729, a different English word, "Taskmaster") — not conflated with this fix. |
| `託` vs `托` in name transliterations (e.g. Tortheldrin, Maltorius, Artorius, Lorenikus) | `托` preferred | User-stated preference (batch 39, same-day correction): `托` reads more naturally in zhTW. This **reverses** an initial "keep DB's `託`" pattern that had held across 4 independent names earlier in the same batch and looked like a safe standing rule — it wasn't. Swept project-wide (not scoped to the batch), 28 occurrences across `託塞德林`→`托塞德林`, `拉託尼庫斯`→`拉托尼庫斯`, `瑪託留斯`→`瑪托留斯`, `阿託留斯`→`阿托留斯`, including several already-committed quests from much earlier batches (1317/1318/2869/2870/3130). Treat any *other* `託`-transliterated name encountered later the same way unless there's a specific reason not to. |
| wowhead showing wrong-era content (methodology note, not a term) | n/a | First confirmed case (batch 37, quests 7141/7142): wowhead's `/wotlk/tw/` fetch can still return later-expansion (e.g. Cataclysm AV revamp) content for a quest ID that Blizzard significantly redesigned after WotLK. Tell-tale sign: the diff isn't just wording — the *title* itself doesn't match the English source either, and the described quest mechanic is structurally different (different sub-objectives, different named NPCs), not just phrased differently. When this happens, trust the English `quest_template.sql` (this project's actual WotLK-era source) over wowhead, the same way the Blackfathom Deeps case (batch 34) taught to check wowhead's *per-expansion* pages — except here the fetch tool doesn't let us pick an expansion tag, so the giveaway is internal (title/content structure mismatch) rather than a URL comparison. |
| Elune | `伊露恩` | NOT `艾露恩` — DBC-confirmed: `Achievement_Name_zhTW.tsv` id 937 = `伊露恩的祝福` ("Elune's Grace"), tier-1 ground truth. **Reversed same-day (batch 29) from an initial wrong call**: originally judged `艾露恩` "confirmed correct" on corpus breadth alone (89 occurrences across 7 pending files, including pre-existing `page_text_locale`/`quest_request_items_locale` text, vs wowhead's `伊露恩` at 37 in 2 files) — this reasoning was backwards. Corpus breadth from a text corpus majorly OpenCC-converted from zhCN is not independent corroboration; it's evidence the *same* wrong term propagated everywhere the conversion touched. **Lesson: for a proper-noun dispute, search the DBC ground-truth files by BOTH candidate Chinese spellings, not just the English word** — the batch-29 miss happened because `AreaTable_zhTW.tsv`-style files have no English column, so an English-only search (`grep -i elune`) finds nothing even when the answer is sitting right there under a Chinese-spelling search. Swept 103× project-wide. |
| Satchel/backpack items | `背包` | NOT `揹包` — reversed same-day (batch 29) per direct user correction (real-world zhTW usage; no DBC exists for this generic non-proper-noun term, so this is a user judgment call, not a ground-truth-hierarchy finding). Same corpus-breadth trap as Elune: originally kept `揹包` because it had 50 occurrences across 6 files vs wowhead's 10 — that breadth argument is unreliable for exactly the same OpenCC-conversion reason. Swept 66× project-wide. |
| Arcane (generic) | `秘法` | corpus favors this 176:73 over `奧術`; confirmed for "Arcane Feedback" title (quests 5676/5677, also matches English "Feedback" as a bare noun, not `回饋者`/"one who gives feedback") |

### Recurring typo / formatting classes

- Middle-dot name separator: `·` (U+00B7) is correct, `‧` (U+2027 Hyphenation Point) is wrong
  — corpus split heavily favors `·` (2568:534 as of batch 27) but this has only been fixed
  per-instance when directly encountered, **not swept** — large remaining cleanup opportunity.
- `複命`→`覆命` typo (corpus-wide 496:2 majority already correct; fix the rare `複命` outlier
  on sight).
- `賬本`→`帳本`, `兒童周`→`兒童週`, `山后`→`山後` — simplified-character leaks, fix on sight.
- Measure word `只`→`隻` for animal counters.
- Stray trailing `*` characters in titles — recurring cosmetic corruption, found repeatedly
  across many batches (2, 7, 9, 23, 25) — always strip if seen.
- Doubled-character typos (`的的`, `我們我們的`, `住在在`) — spot-fix whenever found.
- A dangling `$B$B已提供物品：` (trailing colon, no item name ever filled in) was a project-wide
  artifact stripped from 14 quests early in the pass (batch 1) — if it resurfaces elsewhere,
  strip it the same way.
- **`$g<male>:<female>` gender-token corruption (functional bug, project-wide, swept 2026-07-17
  off-cycle during batch 40, not a translation-quality issue)**: the WoW client requires the
  literal syntax `$g<male-text>:<female-text>;` — an ASCII `;` closes the block, and without it
  the client can't parse the substitution and renders the raw `$g...` text in-game instead of
  the gendered word. User reported this live (quest 9279) after noticing raw `$g兄弟:姐妹` text
  on screen. A full-file scan found **46 rows** missing the closing `;` (likely swallowed by an
  earlier punctuation-normalization/OpenCC pass, since it's the one ASCII punctuation mark this
  token syntax actually depends on) — all swept via an exact whitelist of the ~30 known
  male:female word-pairs already used in this file (character-class regexes kept overreaching
  into the following sentence on run-on Chinese text with no internal punctuation, so don't
  reach for a generic `[^...]* :  [^...]*` pattern here — enumerate the literal pairs instead).
  Two more related bugs found and fixed in the same pass: quest 12214 had the *internal*
  separator itself as a full-width `：` instead of ASCII `:` (also unparseable, needed both
  fixed); quests 6847/6848 had a full `<NPC emote text.>` bracket-emote corrupted into
  `$n;NPC emote text.$g;` (an unrelated but similarly-shaped corruption, likely the same root
  cause misfiring on `<...>` — restored to the standard `<...>` emote format used everywhere
  else in the corpus). If a similar raw-token report comes in again, check for exactly this
  class of bug first — it's a rendering/parsing defect, not a wording dispute, and won't show up
  in the wowhead-diff workflow at all since wowhead's own page renders the substituted word, not
  the raw token.
- **Leaked `進度`("Progress") field-label prefix (functional/data bug, project-wide, swept
  2026-07-18 during batch 42)**: a literal `進度` was glued directly onto the start of the
  Details or Objectives field with no separator, in 12 rows scattered across the whole file (only
  1 in-batch when found — quest 8319 — the other 11 spanned already-committed and not-yet-reached
  ranges). Almost certainly a leftover section-label artifact from whatever process originally
  scraped/populated this text (English `quest_template`'s own corresponding field is blank for at
  least one affected quest, ruling out a legitimate translation of an actual English word).
  Stripped via an exact `', '進度` → `', '` replace (anchored to the start of a field, so it can't
  accidentally eat a legitimate mid-sentence use of 進度 as an ordinary word elsewhere). Verify
  zero remaining hits after any future full-file text change: `grep -c "', '進度"`.

### Notable false-positive patterns (general lessons, not specific quests)

- wowhead's own Details/Objectives fields can disagree with *each other* on the same page —
  a match on one field isn't corroboration for the other.
- wowhead can drop a word a literal DB translation kept correctly (e.g. "Deep" in Deep Elem
  Mine, "young" in Black Drake's Heart) — don't assume wowhead's shorter phrasing is the more
  "idiomatic," check it's not simply incomplete.
- wowhead can fabricate names/content outright, scrape the wrong quest entirely, or fail to
  render and return raw English/markup — always sanity-check that wowhead's fetch is even
  about the right quest before trusting it.
- wowhead's fetch is not an independent source when it derives from the same broken client
  string data DB does (identical typos appearing on both sides is a sign of this, not
  corroboration).
- Same-corpus majority is *not* proof of correctness on its own — see the OpenCC-conversion
  note in Methodology. Always prefer a DBC/locale-table/dedicated-page check over corpus count
  when one is available; corpus-majority-was-wrong has been confirmed repeatedly (Kalimdor,
  Mekkatorque, Demon Hunter, Highborne/trogg lineage, etc.).
- A title/rank shared by multiple NPCs with the same English word can be translated
  inconsistently across them in the base game data *itself* (e.g. "High Executor") — verify
  and fix per-NPC, never generalize from one confirmed instance to "every NPC with this title."
- Spelled-out English numbers and DB's stylistic choice to render a count as a Chinese numeral
  are the two dominant false-positive classes for the count-audit script.
- An item's own dedicated wowhead page can outrank even a lopsided corpus-wide class-name
  convention (Brutal Hauberk overturned a 14:0 "Mail" heuristic) — don't stop at a heuristic
  when a direct, higher-tier check is available and cheap.
- corpus-majority "consistency" is only a signal when the majority occurrences are actually
  about the *same* proper noun — a shared generic word (`部族`, `碎骨`) reused across many
  unrelated names is not evidence for any one of them specifically.

## Unresolved / open follow-up items

- **`傀儡`/`魔像` (Golem)** — corpus split 58:47 as of batch 18; locale table favors `魔像`,
  only ~7 confirmed occurrences fixed so far (batches 18/20/21), bulk still unswept. Needs a
  dedicated pass.
- **`板甲`/`鎧甲` (Plate armor)** — ~44 unswept occurrences, spans 3+ distinct questlines each
  needing individual `item_template_locale` verification (confirmed the correct word varies by
  specific item, not a uniform swap — do not blind-sweep).
- **Middle-dot `‧`/`·`** — 2568:534 split project-wide, only fixed per-instance so far.
- **`龍人`/`龍裔` (Dragonspawn)** — settled `龍裔` is correct (wowhead NPC page, batch 33), 3 of
  ~8 corpus occurrences fixed so far (quests 6502, 6569, 6570). The rest need individual
  verification — some look plausibly like the same "Dragonspawn" concept (Black/Nefarian
  context clues) but weren't individually confirmed against their own English source.
- **`馭風者` (Wind Rider, generic mount references)** — `雙足飛龍` confirmed as the
  lore-preferred term (batch 33, user correction), fixed in one quest cluster (6384-6386).
  ~16 more `馭風者` occurrences remain elsewhere in the corpus, unverified.
- **40 quest rows contain raw, unconverted simplified Chinese** (found batch 9, only quest 755
  fixed so far): 3062, 4496, 4507, 8224, 8365, 9852, 10690, 10999, 11132, 11164, 11272, 11435,
  11452, 11453, 11992, 12024, 12119, 12122, 12123, 12124, 12851, 12918, 13004, 13096, 13108,
  13109, 13248, 13252, 13372, 13375, 13380, 13423, 13959, 13986, 13997, 14032, 14355, 14409,
  25055, 25092 — a distinct, larger issue from the zhCN-vocabulary-leak problem this pass
  otherwise targets (never OpenCC-converted at all, not just translated with zhCN word
  choices). All well past where any batch has reached so far; needs its own dedicated
  conversion pass when reached.
- **`裡`/`里` locative ambiguity** — only the batch-9 container-noun-classifier subset (17
  high-precision matches) has been fixed; broader corpus-wide ambiguity remains unclassified.
- **Two duplicate `quest_template_locale` rows** (two DELETE+INSERT pairs for the same ID) in
  `rev_1783688290124463491.sql` for quest IDs **1241, 1250, 1264** — needs dedup, unrelated to
  translation content.
- **Quest 170**'s `石齶穴居人`/`石齶` — unverified whether this should be the "Rockjaw" or
  "Stonesplinter" trogg family; check `creature_template` for the exact English name in this
  quest's `RequiredNpcOrGo` before assuming either way.
- **Quest 1960** has the identical "filled coffers" truncation bug batch 10 fixed in quest
  1920 (missing the "empty coffers" clause) — flagged, not yet reached/verified.
- **Galvan the Ancient** (creature 7802) — no confirmed correct title yet. `creature_template`'s
  literal English subname is "Galvan **the Ancient**"; wowhead's own rendering (`『長者』`,
  "Elder") doesn't precisely match either. Needs either a better literal rendering or direct
  confirmation via the NPC's own dedicated wowhead page.
- **Bath'rah the Windwatcher** spelling split (`捕風者`/`觀風者`) — only quest 1712 fixed to
  `觀風者` so far; quest 8411 (not yet reached) has both spellings in the same row and still
  needs resolving when reached.
- **`質量`/`品質`** — see Systemic sweeps above; ~28 occurrences remain in not-yet-reached IDs.

## Tools

Reusable scripts live in `scripts/` (generic, not batch-specific):

- `fetch_quest_text.py` — fetches wowhead-tw quest text for IDs listed in
  `$ZHTW_SCRATCH/wowhead_final_zh.txt` (one ID per line), writes to
  `$ZHTW_SCRATCH/quest_text_extracted.jsonl` (resumable — tracks done IDs, safe to re-run).
  A 194-ID batch takes ~8-10 minutes (2.5s/fetch); run it with Bash `run_in_background`.
- `diff_quest_text.py [--strict]` — diffs the fetched jsonl against pending_db_world's
  `quest_template_locale`. Plain mode only normalizes `$N`/`$n` case. **`--strict` also drops
  `$B` breaks, normalizes punctuation width/style, and strips whitespace** — filters out
  wowhead rendering quirks and should be the first pass on any batch beyond ~100 quests; it
  typically cuts the flagged count by 30-40%. **Has no numeric range arguments** — it always
  diffs the entire cached jsonl (every ID ever fetched across all batches), so filter its
  output to the current batch's ID range in Python before reviewing, or stale findings from
  already-verified batches will resurface as noise.
- `audit_quest_counts.py <lo> <hi>` — cross-checks every number in Objectives+Details against
  `quest_template`'s real English `LogDescription`+`QuestDescription` for the given ID range.
  Run this proactively at the start of every batch (not just when a count diff is suspected)
  — it has caught real bugs the text diff missed. Expect false positives (ratios, percentages,
  digit-bearing org names, spelled-out numbers, stylistic Chinese-numeral rendering); verify
  each individually before fixing.
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
- Direct entity-page fetch technique (batches 10-16): for a no-locale-table dispute, `curl -sL
  "https://www.wowhead.com/wotlk/tw/npc=<id>"` (or `item=<id>`) and read the `<title>` tag —
  faster and more authoritative than the pre-fetched quest-page jsonl for a single-entity
  check.

A typical batch: set `ZHTW_SCRATCH`, write the ID range (minus skip-list) to
`wowhead_final_zh.txt`, run `fetch_quest_text.py` in the background, then run
`audit_quest_counts.py` and `diff_quest_text.py --strict` once the fetch completes, review
every flagged quest against the ground-truth priority order (and the Established terms
glossary above for anything that looks familiar), apply fixes, re-run both checks plus the
linter/field-count validation, then update this file's Completed ranges table, add any new
established terms/rulings, and move the Next-batch pointer.

## Next batch

Resume from quest ID 8341 (batch 43, target range roughly 8341–8540) following the same
two-phase methodology, skipping any ID present in `skip-list.tsv`. 5,227 quest IDs remain
after batch 42 (see Total scope note above).

**Addendum from batch 42**: two project-wide functional/data bugs have now been found and swept
off-cycle during this pass (the `$g` gender-token missing-semicolon bug, and the leaked `進度`
field-label prefix — see the "Recurring typo/formatting classes" entries). Both were found
incidentally while reviewing a batch's diff, not through any dedicated search. Stay alert for a
third: if a diff shows DB text that looks like a stray word, a broken token, or an internal
inconsistency unrelated to translation *quality*, check whether it's actually a data/formatting
bug worth a full-file grep before writing it off as just this one quest's problem.

**Addendum from batch 41**: when a quest's wowhead fetch returns literal untranslated English
text (not the generic scrape-failure placeholder, but the *real* quest page genuinely lacking a
zhTW translation — quest 7961 was the first confirmed case), don't skip it: cross-check the
English source and, if a sibling/chain quest *does* have a wowhead translation, reuse its
established terminology for consistency rather than inventing new renderings. Also watch for
more "Paragons of Power" (Zul'Gurub reputation armor) quests outside 8052–8079 if any exist
elsewhere in the corpus, and re-verify the Augur/Haruspex naming split holds if encountered
again.

**Addendum from batch 40**: when `audit_quest_counts.py` flags a mismatch, don't assume DB is
wrong by default — pull the quest's actual `RequiredNpcOrGoCount`/`RequiredItemCount` fields from
`quest_template` and check both DB's and wowhead's prose numbers against that ground truth before
touching anything (see the new "Quest count mismatches" methodology entry). Also watch for more
resurfacing `巨魔`→`食人妖` Troll-term instances in Hinterlands-region quests outside this batch's
own range (Vilebranch/Revantusk territory) — this batch confirmed the tribe via `creature_template`
evidence but only swept the 12 quests actually reviewed.

**Addendum from batch 39**: this batch reversed two strong pre-existing DB majorities (16:0 for
Grayson Shadowbreaker, 8:0 for the Tainted Scar) on the strength of unambiguous English evidence
— a reminder that a large corpus majority is a useful signal but not proof, especially for
proper nouns where DB may have consistently transliterated a compound English name phonetically
instead of translating it. Also watch for: more `工頭`→`監督者` Overseer-rank instances beyond
Maltorius/Oilfist; more `傀儡`→`魔像` Golem instances (the corpus is genuinely mixed, 49:55, no
blind sweep — check each one against its English source); and more `腐爛之痕`→`腐化之痕` Tainted
Scar instances (~5 more unswept elsewhere). **Reversed same-day**: prefer `托` over `託` in name
transliterations by default now (user preference, batch 39) — the opposite of what this note said
a few hours earlier in the same batch. Don't trust a same-session pattern as "established" just
because it held across a few names; a real user preference can and did override it immediately.

**Addendum from batch 38**: before treating a flagged diff as real content, rule out a wowhead
scrape failure first — if the WH title/objectives/details text is the exact boilerplate
`魔獸世界：巫妖王之怒中所有任務的完整列表，可自訂條件搜尋與過濾...`, that's wowhead's generic
quest-index page, not the actual quest (see the new methodology entry in Established terms).
This showed up heavily in the AV "kill an enemy-race player" bounty-quest cluster this batch and
will likely recur for similar repeatable/PvP-flagged quest IDs elsewhere. Also watch for more
Eldre'Thalas spelling instances (`艾德雷薩拉斯`/`埃雷薩拉斯`→`埃德薩拉斯`) — only 6 of an unknown
total were reviewed and fixed this batch, scoped to Dire Maul-questline quests specifically.

**Addendum from batch 37**: before accepting a wowhead diff at face value, check whether it's a
genuine translation disagreement or wowhead showing content for a different game era (see the
"wowhead showing wrong-era content" methodology entry in Established terms) — the tell is a
title mismatch plus structurally different quest content, not just different wording. Also watch
for more Alterac Valley Winterax-troll (`冰斧巨魔`→`冰斧食人妖`) and Commander Philips
(`菲利普`→`菲力浦`, `劉易斯`→`路易斯`) resurfacing instances outside this batch's own range —
both are established rules with a large unswept backlog elsewhere in the corpus.

**Policy update from batch 36, applies going forward**: when a diff is flagged and DB's version
initially looks defensible (corpus majority, an established term, a more "literal" reading), that
is a reason to *investigate*, not a license to default to "false positive, no fix." The user
directed that wowhead-tw be treated as ground truth for disputed fields in general — batch 36
ended up reversing roughly a dozen initial "false positive" calls (mine terminology, name
spellings, location generality, color/orthography variants) once this was made explicit. The one
standing exception is pure rendering/notation artifacts that carry no content difference (e.g.
the `$g男孩:女孩;` vs wowhead's `<男孩/女孩>` gender-token bracket, which the fetch script's own
token-conversion regex sometimes fails to normalize for non-Latin bracket contents — that's a
scraping quirk, not a translation disagreement). When in doubt about whether something is a real
content difference or a notation artifact, ask rather than assume DB wins by default. Watch in
particular for more Alterac Valley mine/graveyard/tower-capture quests (this cluster runs well
past 7140) — batch 36 aligned quests 7081/7082/7101/7102/7121–7124 to wowhead's NPC names,
locations, and `礦坑` spelling; expect more of the same cluster ahead and apply wowhead's reading
directly rather than re-litigating the mine-terminology question per instance. **Caution from
batch 36's Bloodsnarl mistake**: a tier-2 `creature_template_locale` match for the *same surname
on a different NPC* is not automatically stronger evidence than wowhead's own dedicated
rendering — cross-check the target row's own untouched adjacent fields (e.g.
`ObjectiveText1`/`ObjectiveText2` turn-in hints) for same-row internal consistency first.

Watch in particular for newly-settled rulings resurfacing wrong: Kel'Thuzad (`克爾蘇加德`, not
`科爾蘇加德`), Lord Maxwell Tyrosus (`瑪克斯韋爾·泰羅索斯領主`, not `...男爵` or the
different-character spelling `麥克斯韋爾·泰羅索斯`), the `天災石`→`天譴石` Scourgestone term
(batch 28), Neeru Fireblade/the Burning Blade (`火刃`, not `燃刃`, batch 29) — but NOT its
similar-sounding sibling clan "the Searing Blade" (`灼刃氏族`, a different clan, batch 30), and
Hemet Nesingwary **Jr.** (`小赫米特·奈辛瓦里`, a distinct character from the classic Sr. hunting
NPC, batch 30). Also watch for more instances of the recurring content-swap pattern first seen
in batch 29 and confirmed again in batch 31 (two more cases, in a 5-race-variant Hunter
pet-taming quest chain this time): this DB has several near-identical race/class-variant
quest-chain templates (priest "Returning Home"/"Desperate Prayer", hunter "The Hunter's Path"
were two; there are likely equivalent warrior/mage/paladin/etc. chains elsewhere) where one
row's Details/Objectives can get silently duplicated from a *sibling* row in the same template
cluster instead of using its own unique English-sourced text — a same-diff-block match to
another quest in the same template cluster is a red flag worth checking even when wowhead shows
no diff for the row itself, and it's worth deliberately checking every row in an
obviously-templated cluster against its own English source even when most rows in it look fine
on the surface.

**Process reminder from batch 30** (self-caught, not a ground-truth error): when a fix is meant
to apply to exactly ONE quest row (not a corpus-wide sweep), scope the find-replace to that
row specifically — a plain `content.replace(old, new)` across the whole file will silently
sweep every other occurrence of the same substring too, even ones never reviewed. This is
different from an *intentional* project-wide sweep of a confirmed single proper noun (which is
correct and expected, e.g. Un'Goro Crater). Batch 30 caught this immediately via `git diff`
before the batch was reported done (an unscoped "trogg term" fix for quest 5892 had also
silently altered quests 432/433, which were untouched and already correct) and reverted the
unintended part using `git show HEAD:<path>` to restore the exact original row content — worth
doing a `git diff` sanity pass on the full file before finishing any batch with a "single-quest"
fix, not just the field-count/duplicate check.

More generally, check the Established terms and rulings section above whenever a name/term
looks familiar in a new batch — a confirmed fix from an earlier batch regularly resurfaces
unfixed in a later batch's ID range that the original batch never touched (Menara Voidrender
alone has resurfaced across 3 separate batches).
