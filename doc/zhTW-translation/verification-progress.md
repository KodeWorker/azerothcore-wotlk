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
- **Wowhead-tw is treated as ground truth by default for a genuine disagreement** (user
  directive, batch 36) — a defensible-looking DB reading (corpus majority, an established term,
  a more "literal" gloss) is a reason to *investigate*, not a license to default to "false
  positive." The one standing exception is a pure rendering/notation artifact with no content
  difference (e.g. the `$g` gender-token bracket style). This does not override a DBC hit, a
  quest's own internal field consistency, or an already-settled corpus rule — those can still
  outrank a single wowhead fetch; the difference is these get actively checked, not assumed.
- When a fix applies to exactly one quest row, scope the find/replace to that row specifically
  — a blind corpus-wide `content.replace(old, new)` will silently sweep every other occurrence
  of the same substring too, including unrelated, never-reviewed rows (self-caught this exact
  mistake in batch 30). Do a `git diff` sanity pass on the full file before finishing any batch,
  not just the field-count/duplicate check.

Both phases run on the same small batch before moving to the next.

## Completed ranges (quest_template IDs)

| Range | Date | Fixes | Notes |
|---|---|---|---|
| 100–140 (excl. 108, 137) | 2026-07-15 | 5 | Batch 1 (pilot). |
| 141–340 (excl. 242, 259, 260, 316, 326, 327) | 2026-07-15 | ~40 + 3 sweeps (300+×) | Batch 2. First content-swap bugs found (whole quest fields belonging to a different quest). |
| 341–540 (excl. 352, 390, 406, 462, 490, 497, 534) | 2026-07-15 | ~50 + 4 sweeps (~100×) | Batch 3. Highest density yet (118/193); introduced `audit_quest_counts.py`. |
| 541–740 (excl. 548, 612, 636, 740) | 2026-07-15 | ~15 + 2 sweeps (~55×) | Batch 4. Established the Troll/Ogre terminology system. |
| 741–940 (excl. 18 IDs) | 2026-07-15 | ~20 | Batch 5. High count-audit false-positive rate; several count "fixes" reverted mid-batch. |
| 941–1140 (excl. 946, 987–989, 1128, 1129) | 2026-07-15 | ~25 + 3 sweeps | Batch 6. Introduced `diff_quest_text.py --strict`. |
| 1141–1340 (excl. 1151, 1154–1163, 1165, 1277–1280, 1289–1300) | 2026-07-15 | ~20 + 1 sweep (251×) | Batch 7. First confirmed zhCN-leak race term (`暗夜精靈`→`夜精靈`). |
| 1341–1540 (excl. 1390, 1397, 1441, 1443, 1460, 1461, 1533, 1537, 1538) | 2026-07-15 | ~20 + 3 sweeps | Batch 8. High density (108/191); introduced `creature_template`'s literal in-game name as ground truth. |
| 1541–1740 (excl. 1659, 1660, 1662–1664) | 2026-07-16 | ~10 + 1 sweep | Batch 9. Confirmed the OpenCC zhCN→zhTW conversion origin (see Methodology). Found the 40-row raw-unconverted-simplified-Chinese issue, still unresolved (see Unresolved items). |
| 1741–1940 (no skip-listed IDs) | 2026-07-16 | ~20 + 6 sweeps | Batch 10. Introduced direct wowhead NPC/item page fetches for no-locale-table disputes. |
| 1941–2140 (excl. 2018, 2020, 2058, 2059) | 2026-07-16 | ~15 | Batch 11. Lowest density yet (28/196). |
| 2141–2340 (no skip-listed IDs) | 2026-07-16 | ~8 | Batch 12. Jewelry/Uldaman cluster. |
| 2341–2540 (no skip-listed IDs) | 2026-07-16 | ~11 | Batch 13. |
| 2541–2740 (no skip-listed IDs) | 2026-07-16 | ~7 | Batch 14. Lowest density yet (18/200). |
| 2741–2940 (excl. 2868) | 2026-07-16 | ~35 + 3 sweeps | Batch 15. `質量`→`品質` zhCN leak caught; Demon Hunter class-page override; Trogg term reversed 3× same day. |
| 2941–3140 (89 IDs not in DB) | 2026-07-16 | ~26 across 15 rows | Batch 16. Trogg term reverted a 4th time (final answer: `穴居人`). |
| 3141–3340 (189 IDs not in DB, sparsest range) | 2026-07-16 | 7 across 3 rows | Batch 17. `diff_quest_text.py` has no range args — must filter its output in Python. |
| 3341–3540 (excl. 16 IDs; 113 IDs not in DB) | 2026-07-16 | 28 across 20 rows | Batch 18. 7 separate NPC/term disputes resolved via `creature_template_locale`. |
| 3541–3740 (excl. 4 IDs; 153 IDs not in DB) | 2026-07-16 | 12 across 9 rows | Batch 19. Mosh'Ogg zone name settled via DBC. |
| 3741–3940 (excl. 2 IDs; 144 IDs not in DB) | 2026-07-16 | 11 across 9 rows | Batch 20. |
| 3941–4140 (141 IDs not in DB) | 2026-07-17 | 28 across 15 rows | Batch 21. Blackrock Depths/Burning Steppes cluster. |
| 4141–4340 (excl. 2 IDs; 143 IDs not in DB) | 2026-07-17 | 41 across 20 rows | Batch 22. First "surfaced to user rather than resolved unilaterally" case (Varian Wrynn vs. Bolvar Fordragon, quest 4184). |
| 4341–4540 (136 IDs not in DB) | 2026-07-17 | 16 across 12 rows | Batch 23. |
| 4541–4740 (excl. 1 ID; 164 IDs not in DB) | 2026-07-17 | 8 across 4 rows | Batch 24. Lowest density in several batches; all fixes reused already-established ground truth. |
| 4741–4940 (excl. 1 ID; 143 IDs not in DB) | 2026-07-17 | 38 across 16 rows | Batch 25. Highest density yet (80%). Blackrock Spire cluster; Menara Voidrender surname fix. |
| 4941–5140 (excl. 1 ID; 114 IDs not in DB) | 2026-07-17 | 39 across 19 rows | Batch 26. Very high density (67%); Aurius phonetic-preference override. |
| 5141–5340 (excl. 6 IDs; 100 IDs not in DB) | 2026-07-17 | 2 sweeps (73×) + 27 across 16 rows | Batch 27. Very high density (63%). Leatherworking/Moonwell character-level sweeps. |
| 5341–5540 (excl. 8 IDs; 133 IDs not in DB) | 2026-07-17 | 4 sweeps (71×) + 2 targeted | Batch 28. `想象`→`想像` orthography sweep; Gordok Ogre/Troll term settled (`戈多克巨魔`); Iruxos spelling settled; Krastinov epithet fix applied then reverted same-day. |
| 5541–5740 (excl. 42 IDs; 88 IDs not in DB) | 2026-07-17 | 12 + 2 sweeps (169×) | Batch 29. High density (57%), priest class-chain cluster. Two content-swap bugs; **two same-day reversals after user correction** exposed the "corpus breadth ≠ correctness" trap under OpenCC conversion: Elune (`艾露恩`→`伊露恩`, DBC-confirmed, 103× swept) and Satchel (`揹包`→`背包`, 66× swept). |
| 5741–5940 (no skip-listed IDs) | 2026-07-17 | 10 + 1 resweep (9×) | Batch 30. Self-caught an unscoped find-replace that had bled into 2 unrelated rows — reverted via `git show HEAD`; established the "git diff sanity pass before finishing" discipline. |
| 5941–6140 (excl. 1 ID; 133 IDs not in DB) | 2026-07-17 | 9 across 6 rows | Batch 31. High density (60%). Two more content-swap bugs in a Hunter pet-taming quest-chain cluster (same pattern as batch 29). |
| 6141–6340 (excl. 3 IDs; 165 IDs not in DB) | 2026-07-17 | 9 across 8 rows | Batch 32. Genuine count error found (6/6/6 vs correct 5/5/5). Thor-vs-Thrall (`托爾`/`索爾`) and Commander Louis Philips NPC-page disambiguations, both user-confirmed same-day. |
| 6341–6540 (no skip-listed IDs) | 2026-07-17 | 6 across 5 rows | Batch 33. Genuine NPC-swap bug (quest 6521). **Three same-day reversals** after user follow-up: Wind Rider mount (`馭風者`→`雙足飛龍`, lore-based), Resonite cask (item is actually a crystal, not a barrel), Dragonspawn (`龍人`→`龍裔`, wowhead NPC page). |
| 6541–6740 (excl. 11 IDs; 133 IDs not in DB) | 2026-07-17 | 11 + 2 resurfacing sweeps (39×) | Batch 34. Very high density (70%). Splintertree Naga / Blackrock Spire black-dragon-disguise clusters. Two false positives confirmed where wowhead itself was wrong (quests 6606, 6610). |
| 6741–6940 (excl. 3 IDs; 171 IDs not in DB) | 2026-07-17 | 5 + 1 skip-listed | Batch 35. Sparse range. **Three same-day reversals** after user review (Overseer/Portable-Shredder terms, Discordant Bracers item name); quest 6843 confirmed unfinished dev content, skip-listed. |
| 6941–7140 (excl. 1 ID; 94 IDs not in DB) | 2026-07-17 | 29 (13 initial + 16 after a policy reversal) | Batch 36. High density (64%). Two AV scarecrow-NPC bugs; Bloodsnarl surname corrected (`血矛`→`血牙`) after user correction, swept incl. its `creature_template_locale` source row. **User directive: treat wowhead-tw as ground truth by default** for disputed fields going forward (sole exception: pure notation/rendering artifacts) — reopened and flipped roughly a dozen prior "false positive" calls same-day. |
| 7141–7340 (no skip-listed IDs) | 2026-07-17 | 11 across 11 rows | Batch 37. High density (61%). First **wowhead-shows-wrong-era-content** false positive found (quests 7141/7142, later-expansion AV redesign) — tempers the batch-36 directive: it applies to translation disputes, not wowhead showing a different game version's content. Content-swap bug (quest 7181). Three same-day corrections after user preference (`部族`→`氏族`, two AV NPC spellings). |
| 7341–7540 (no skip-listed IDs) | 2026-07-17 | 13 + 1 resweep | Batch 38. Very high density (68%), but ~24 flags were **wowhead scrape failures** (generic quest-index placeholder for a large PvP-bounty cluster) — first confirmed case of this pattern. Genuine title/content-loss bug (quest 7383); Eldre'Thalas spelling settled via 5-page wowhead cross-check. |
| 7541–7740 (excl. 2 IDs; 61 IDs not in DB) | 2026-07-17 | 24 + 2 skip-listed | Batch 39. Very high density (67%). Lord Grayson Shadowbreaker rank/name fix (reverses a 16:0 DB majority); Altar of Storms word-order fix (DBC); two dev/QA quests (7681/7682) skip-listed. Same-day reversal: `託`→`托` preferred in name transliterations, swept 28× project-wide. |
| 7741–7940 (excl. 9 IDs; 76 IDs not in DB) | 2026-07-17 | 27 | Batch 40. Very high density (68%), Revantusk Village/Darkmoon Faire clusters. Third scrape-failure signature found (Darkmoon variant). Established the count-mismatch methodology: always check `RequiredNpcOrGoCount`/`RequiredItemCount`, never trust either side's prose number alone — both directions of error confirmed in the same batch. |
| 7941–8140 (no skip-listed IDs) | 2026-07-18 | 21 | Batch 41. High density (71%), Zul'Gurub "Paragons of Power" cluster. Augur/Haruspex title content-swap fixed via 6-page wowhead cross-check; first confirmed no-wowhead-translation quest (7961), constructed from English source. |
| 8141–8340 (no skip-listed IDs) | 2026-07-18 | 10 + 12-row off-cycle sweep | Batch 42. **Found and swept a second project-wide functional bug**: a leaked `進度` field-label prefix glued onto 12 rows' Details/Objectives text across the whole file (5 already-committed, 6 not-yet-reached, 1 in-batch). |
| 8341–8540 (no skip-listed IDs) | 2026-07-18 | 16 | Batch 43. Templar/Duke content-swap bug (Cenarion Hold cluster). Found the `喚風者梅恩·長角` misnamed-NPC bug (29 corpus occurrences, standing in for ≥3 different real NPCs) — fixed 5 in-batch, flagged the rest for future batches. |
| 8541–8740 (excl. 2 IDs) | 2026-07-21 | 143 (130 bulk + 13 `ObjectiveText4`) | Batch 44. Highest density yet (89%), AQ epic-armor/War-Effort clusters. First full-bulk-replace batch (title/details/objectives wholesale from wowhead, then verified). Fourth scrape-failure signature (Lunar Festival). Extended the `喚風者梅恩·長角` fix to 13 more rows (≥4 real NPCs now confirmed). Fixed hardcoded machine-specific paths in the tooling. |
| 8741–8940 (excl. 1 ID) | 2026-07-21 | 111 | Batch 45. High density (58%). **`喚風者梅恩·長角` bug fully resolved, 0 remaining corpus-wide** — the last 11 occurrences turned out to be a 7-quest content-swap bug (identical wrong donation-quest text copy-pasted across an AQ War-Effort cluster) plus 3 more `ObjectiveText4` fixes. Settled the Deliana (`德莉亞娜`→`德莉娜`) and Beaststalker's (`野獸追獵者`→`馭獸者`) name splits. |
| 8941–9140 (excl. 8 IDs) | 2026-07-21 | 159 | Batch 46. Very high density (81%), Naxxramas Silver Hand reward-chain cluster. Settled Valthalak (`瓦塔拉克`→`瓦薩拉克`) and Bodley (3-way spelling split→`布德利`) name spellings; extended the Deliana/Beaststalker's sweeps. |
| 9141–9340 (excl. 11 IDs) | 2026-07-21 | 71 | Batch 47. Ghostlands/Atiesh questline. Content-swap bug fixed by direct construction (quest 9339, no wowhead translation available); Atiesh spelling settled (`阿泰絲`). |
| 9341–9540 (excl. 15 IDs) | 2026-07-21 | 129 | Batch 48. Very high density (79%), Hellfire Peninsula leveling arc. Same content-swap bug pattern as batch 47 recurred (quest 9365, fixed the same way); 3 genuine count/content bugs caught by `audit_quest_counts.py`. |
| 9541–9740 (excl. 21 IDs) | 2026-07-21 | 92 | Batch 49. Caught and reverted a case of wowhead's own number being wrong (quest 9610) via post-fix count audit — established that the count audit must run *after* the bulk pass, not just before it. |
| 9741–9940 (excl. 2 IDs) | 2026-07-21 | 165 + 1 skip-listed | Batch 50. Extremely high density (89%), Karazhan/Nagrand clusters. **Introduced the proactive pre-fix WH-vs-English count cross-check** — found wowhead's own kill/collect counts wrong in 28 separate quests (DB's pre-existing counts were correct in every one), withheld those Objectives fields from the bulk replace. One dev/QA quest skip-listed (9750). |
| 9941–10140 (no skip-listed IDs) | 2026-07-21 | 135 + 60× corpus-wide sweep | Batch 51. Highest density yet (96%), Terokkar Forest/Hellfire Peninsula clusters. **Self-discovered a corpus-wide proper-noun bug** (Stonebreaker Hold/Camp, `裂石堡`→`碎石堡`), DBC-confirmed, swept 60× across 33 rows far outside the batch's own range. 7 Objectives exclusions (6 wowhead-count-wrong, 1 new field-misalignment class). |
| 10141–10340 (no skip-listed IDs) | 2026-07-21 | 169 + 44× corpus-wide sweep | Batch 52. Highest density yet (97%). Second self-discovered corpus-wide proper-noun bug (Spinebreaker Post/Ridge, `斷背崗哨`/`斷背山`) — genuinely two distinct DBC-confirmed locations, not a uniform sweep. **Discovered `quest_template_locale`'s `ObjectiveText1`-4 columns have never been in any tool's scope** — found and fixed a real bug living there (quests 10145/10147); flagged the ~8,800-row blind spot under Unresolved. **Regression found and fixed retroactively in batch 53**: quest 10149's `apply_fixes.py` pass wrongly wiped its Objectives field to empty and overwrote Title/Details with raw bracketed English — see batch 53's entry and the new Tools note. |

| 10341–10540 (no skip-listed IDs prior; 2 removed mid-batch) | 2026-07-21 | 128 targeted fixes across 128 quest rows (bulk-replaced) + 5 same-row established-term touch-ups + 2 skip-listed | Batch 53. High density (81%, 128/164 real + 33 bracket + 3 scrape-fail out of 198 fetched). Netherstorm Area 52/Eco-Dome/mana-forge-shutdown wrap-up, Auchindoun/Terokkar Caverns-of-Time lead-in, Nagrand Garadar cluster. Two dev-placeholder quests (`DON'T USE [PH] Fel Orc 1`/`bread`, literal "PH" placeholder in the English source itself) confirmed unfinished, skip-listed (10452/10453). Resurfacing name-spelling sweeps applied directly to 2 bracket-fallback rows outside the normal bulk path (Deliana `德莉亞娜`→`德莉娜`, Anthion `安泰恩`→`安希恩`, Valthalak `瓦塔拉克`→`瓦薩拉克`, Bodley `伯德雷`→`布德利`). **Found and fixed a real `apply_fixes.py` bug** (see the new Tools note): wowhead returning a genuinely blank fetch for one field of an otherwise-bracket quest (title/details untranslated, but the Objectives fetch itself came back empty) was misclassifying the quest as "real" instead of "bracket," then overwriting Objectives with the empty string and Title/Details with raw bracketed English — caught 2 instances in this batch (10401, 10497) plus 1 already-committed regression from batch 52 (10149, fixed retroactively) via a targeted re-scan of every prior batch's cached diff data. Also self-caught and fixed a separate, more severe bug the same review surfaced: an early row-removal script (for skip-listing 10452/10453) used an unanchored non-greedy regex that matched from the file's very first `INSERT` statement through to the target row, deleting ~11,500 lines instead of 2 — caught immediately via the post-edit row-count check, reverted with `git checkout`, and redone with a row-scoped span-finder. Count audit: 0 mismatches. |

| 10541–10740 (no skip-listed IDs) | 2026-07-21 | 138 targeted fixes across 138 quest rows (bulk-replaced) | Batch 54. High density (73%, 138/143 real out of 197 fetched, 3 bracket, 2 scrape-fail). Netherstorm Area 52/wind-scanner cluster wrap-up, the Shadowmoon Valley Legion Front/Path of Glory mirror (Alliance Wildhammer + Horde Deathforge sides), the Auchindoun/Bash'ir Landing intro, and the Violet Eye reputation-reward chain. Confirmed a genuine same-row internal-consistency bug caught by the diff itself, not by manual inspection: quest 10712's Objectives named the wrong delivery location (`永恆樹林` instead of `魯安曠野`), contradicting its own already-correct, untouched Details field — resolved automatically by the bulk pass since wowhead's Objectives text already matched the Details field's location. No exclusions needed; proactive WH-vs-English count check found 0 candidates. Count audit: 4 residual flags, all reconfirmed as established false-positive classes (spelled-out/character-numeral ordinals, a flavor-text percentage, a 3-named-object objective the audit script's digit scan doesn't parse) — 0 real mismatches. |

| 10741–10940 (no skip-listed IDs) | 2026-07-21 | 146 targeted fixes across 146 quest rows (bulk-replaced, 1 reverted post-fix) | Batch 55. High density (75%, 146/154 real out of 196 fetched, 8 bracket, 0 scrape-fail). Terokkar Forest White Bone Wastes/Skettis Auchindoun-lead-in cluster, Shadowmoon Valley Netherwing dragon-rescue chain, the Naaru Trials of the Naaru heroic-dungeon-key questline, and the Darkmoon Faire card-deck completion quests. **Caught a genuine wowhead-wrong-content case via the post-fix count audit**: quest 10842's bulk-applied Objectives no longer matched the true English source ("defeat 5 Vengeful Draenei") at all — wowhead's fetch for this ID actually returned the title/content belonging to a *different*, still-unfinished dev-placeholder quest (10841, literally titled `[The Vengeful Harbinger]` / `[PH] Activate the thingy` in English) rather than 10842's own real, already-correct content; reverted the row to its pre-batch state. Count audit: 4 residual flags after the revert, all established false-positive classes (Chinese-ordinal-numeral pages, Darkmoon deck flavor-count text) — 0 real mismatches remaining. |

| 10941–11140 (no skip-listed IDs) | 2026-07-21 | 40 targeted fixes across 40 quest rows (bulk-replaced) + 2 pre-existing raw-simplified-Chinese rows converted + 1 pre-existing missing-count gap fixed | Batch 56. Moderate density but heavily bracket-skewed (155/187 flagged, only 50 real vs. 105 bracket — a huge Children's Week orphan-quest cluster plus the Shadowmoon Valley Netherwing Dragonmaw-infiltration questline account for most of the bracket count). **Found a new wowhead-fetch failure mode**: quests 11087 and 11116 returned genuine **Simplified** Chinese content (with several proper nouns left entirely untranslated) from the nominally-`/wotlk/tw/` URL, not just wrong or missing content — excluded both entirely from the bulk pass, keeping DB's own already-correct Traditional Chinese. **Found and fixed a second, more subtle `apply_fixes.py` bug** (see updated Tools note): a quest with one field that's genuinely bracket-fallback (no zhTW translation) and a *different* field that came back blank from wowhead was slipping past the "all fields bracket → treat as bracket" classifier (since the blank field isn't bracket-wrapped), landing in `real_ids`, and then having its bracket field wrongly overwritten with raw English — caught via 8 quests showing an unexplained residual diff after the main pass (11006/11013/11020/11027/11054/11070/11097/11107), reverted all 8 to original state (none had any legitimate field to fix), and hardened the script's guard to skip any bracket-wrapped WH field against non-bracket DB content regardless of the quest's overall classification. A full re-scan of the batch's original data confirmed exactly these 8 rows (14 fields) were affected and nothing else. **Converted 2 of the long-known 40 raw-unconverted-simplified-Chinese rows** (flagged since batch 9, never touched since): quests 10999 and 11132, both bracket-fallback with no wowhead translation to lean on, fixed by direct simplified→traditional conversion preserving the existing translation choice (not a re-translation) — updates the Unresolved-items list accordingly. **Caught a genuine pre-existing content gap via the count audit that the text-diff could never have found**: quest 11026's Objectives has been silently missing its required "15" (demons to banish) in *both* DB's text and wowhead's own zhTW fetch independently (byte-identical strict match, so no diff ever triggered) — confirmed against the true English `RequiredNpcOrGoCount`-backing LogDescription and fixed by direct insertion. Proactive WH-vs-English count check flagged 3 candidates pre-fix, all confirmed as flavor/narrative numbers (not required-count fields), applied normally. Count audit: 8 residual flags after all fixes, all established false-positive classes or minor pre-existing bracket-quest gaps left for a future dedicated pass (quest 11122's dropped "3 times" Brewfest repeat-count, quest 11079's flavor-text "35 shards") — 0 further regressions. |

| 11141–11340 (no skip-listed IDs) | 2026-07-21 | 59 targeted fixes across 59 quest rows (bulk-replaced, 2 with a field excluded) | Batch 57. High real-diff ratio driven mostly by wording-quality differences, not content errors (171/175 flagged, 62 real vs. 107 bracket) — the Westfall Defias-conspiracy/Theramore chain, the Dustwallow Marsh Grimtotem/goblin-zeppelin cluster, and the Alliance/Horde battleground "Call to Arms" quest set. **Confirmed proper-noun fix via tier-2 ground truth**: quest 11216's quest giver "Archmage Alturus" was translated with the zhCN-leaked transliteration `奧圖魯斯` (matches historic zhCN `奥图鲁斯` character-for-character); cross-checked against the pre-existing `locales_item` entry for item 24482 ("Alturus' Report"), whose zhTW field independently already used `艾特羅斯` — matches wowhead's rendering exactly, applied with confidence. Established: **Archmage Alturus → `艾特羅斯`**, not `奧圖魯斯`. **Found a new wowhead-scraper bug variant**: quests 11335/11336's Details field contains an unconverted `$g` gender-token artifact (`<小姑娘/小伙子>` literally, in reversed female/male order vs. DB's working `$g小子:小姑娘;`) — root-caused to `fetch_quest_text.py`'s `convert_tokens()` gender-token regex requiring literal `<`/`>` chars, but this particular occurrence was HTML-entity-escaped in the source (`&lt;.../&gt;`) and only unescaped *after* both the gender-regex and the tag-stripper had already run, so it survives into final text unconverted and in the wrong field order; excluded the Details field for both quests via `EXCLUDE_FIELDS` (title/objectives, which don't contain the token, applied normally) rather than risk a manual reorder. **3 real-classified quests were actually mis-scraped bracket-fallback in disguise** (11243/11290/11291: title+details bracket-wrapped English, objectives blank — same classifier gap as batch 56, but this time every touched field was independently caught by the existing batch-56 guards, so `apply_fixes.py` correctly skipped all 3 with no code changes needed). Proactive WH-vs-English count check: 0 candidates. Count audit: 2 residual flags, both established false-positive classes (`SI:7` org-name digit, spelled-out "ten" rendered as DB's `10`) — 0 real mismatches. |

| 11341–11540 (3 pre-existing skip-listed IDs: 11347, 11425, 11461) | 2026-07-21 | 26 targeted fixes across 26 quest rows (bulk-replaced, 4 with a field excluded) + 6 same-row manual fixes (2 skip-listed, 1 corrupted-EndText repair + 2 duplicate-content mirror-fixes, 1 corpus term sweep across 2 rows) | Batch 58. Moderate real-diff ratio (159/178 flagged, 33 real vs. 122 bracket) — Hellfire Peninsula Bounty Board (Zarevhi's heroic-only reward quests), the Consortium/goblin-cook Shattrath Lower City food chain, Brewfest, and the Isle of Quel'Danas Sunreaver's Armory/Bounty of the Isle daily hubs. **2 new dev/test quests found and skip-listed** (neither caught by the original `<UNUSED>`-bracket skip-list sweep since both lack the angle brackets): quest 11493, English title literally `UNUSED` with a blank Details and wowhead returning garbage placeholder Chinese (`一 任務`) for Objectives; quest 11402, `Clayton's Quest: Extreme!`/`Return to Clayton's Test Creature.`, `RequiredNpcOrGoCount` entirely zeroed (no real kill requirement wired up) and the existing zhTW text itself had a wrong count (12 vs. the unenforced English's 20) plus a garbled English/Chinese-mixed title — both found via the post-fix count audit, not the text diff. **Found a new wowhead-fetch artifact shape**: quest 11442's Objectives/Details came back as a leaked `[PH] ...` placeholder that doesn't fit the whole-field `[...]`-wrap the bracket guard checks for (a stray trailing `。` after the `]` on Objectives, no closing `]` at all on Details) — slips past the guard as if it were a real translation; excluded both fields manually, applied the (properly translated) Title normally. **3 more instances of the batch-57 escaped gender-token bug** (quests 11388, 11497, 11498's Details, `<他/她>` unconverted): 11388's WH text was otherwise byte-identical to DB's already-correct version, so excluded and kept DB's; 11497/11498 had genuine wording improvements worth keeping, so hand-converted the token to `$g他:她;` (the corpus's established male:female order) after excluding the field from the automatic pass rather than losing the improvement. **4 real-classified quests were bracket-fallback in disguise** (11468/11491/11511/11527 — same classifier gap as batches 56/57, all 4 fully guard-protected, 0 fields touched, no code changes needed). **Self-discovered and fixed a corpus-wide term/content bug while reviewing the batch's diff**: the annual Brewfest "Did Someone Say Souvenir?" quest (11321, already fixed batch 57) turned out to have a literal corrupted `\r\n` control sequence embedded mid-word in its EndText field (`丹\r\n莫羅` splitting the place name) — a pre-existing bug unrelated to batch 57's own fix (EndText is outside `apply_fixes.py`'s `FIELD_IDX` scope, part of the batch-52-flagged blind spot), repaired directly (`丹莫洛的貝爾碧`). Found 2 other quest rows (12193, 13932) holding an exact duplicate of this quest's *pre-fix* content under different year-specific titles (an annual repeat-quest pattern) — mirror-applied the now-corrected canonical text to both, far outside this batch's own ID range but same-day self-contained fix, matching the precedent from batches 51/52's systemic sweeps. Also swept the corpus's remaining old `美酒節`→`啤酒節` Brewfest-name term inconsistency (2 more rows, 11486/11487, both `scrape_fail` so untouched by the normal pipeline) — wowhead consistently uses `啤酒節` across every Brewfest quest fetched this session and the corpus already leaned 24:7 toward it before this fix. Proactive WH-vs-English count check: 0 candidates. Count audit: found and fixed the 2 skip-list-worthy quests above; 1 residual false positive remaining (quest 11536, spelled-out English "three" rendered as DB's digit `3`). |

| 11541–11740 (2 pre-existing skip-listed IDs: 11588, 11589) | 2026-07-21 | 2 targeted fixes across 2 quest rows (bulk-replaced) | Batch 59. Low real-diff ratio, heavily bracket/scrape-fail-skewed (141/150 flagged, only 9 real vs. 121 bracket + 11 scrape-fail) — Icecrown Warsong Hold/Garrosh's Landing Kvaldir-mist cluster (mostly bracket-fallback, no wowhead translation yet for this newer content) and a couple of Westfall/Silverpine one-off flavor quests (11580, 11583 — the only two genuine fixes this batch). **Found a new wowhead-fetch failure mode**: quests 11552/11553's Objectives fetch came back as wowhead's own site meta-description tagline ("World of Warcraft: Wrath of the Lich King — full quest list, customizable filter/search...") rather than real quest content — both quests have entirely blank English `LogDescription`/`QuestDescription` too (likely unused/scrapped "gate" mechanic content, titles "Rohendor, the Second Gate"/"Archonisus, the Final Gate"), and the proactive count check's phantom "3, 4" flag turned out to be from the tagline's version number "(3.4.3)", not a real count — excluded the field rather than write site chrome into the DB. **Noted but not resolved**: both quests' Title field already held this exact same generic-tagline-style bogus text (`巫妖王之怒 任務`, "Wrath of the Lich King Quest") *before* this batch touched them, meaning some earlier, undocumented pass fell victim to this identical scrape bug for the Title field and it slipped by undetected until now — added to Unresolved items rather than guessing at a real title with no ground truth available anywhere. **1 more instance of the escaped gender-token bug** (quest 11665's Details, `<小夥子/姑娘>` vs DB's working `$g小夥子:姑娘;`) — byte-identical otherwise, excluded and kept DB's version. **4 real-classified quests were bracket-fallback in disguise** (11643/11656/11705/11717 — same classifier gap as batches 56–58, all fully guard-protected, 0 fields touched). Proactive WH-vs-English count check: 2 candidates (11552/11553 above), both excluded. Count audit: 2 residual flags, both new false-positive subclasses worth naming — quest 11611's English source uses an inline `(1)...(2)...` enumerated list whose markers get misread as counts, and quest 11690's "ten minutes" (spelled-out, flavor text, not a required-count field) rendered as DB's digit `10` — 0 real mismatches. |

| 11741–11940 (no pre-existing skip-listed IDs) | 2026-07-21 | 38 targeted fixes across 38 quest rows (bulk-replaced, 1 with a field excluded) | Batch 60. Moderate real-diff ratio but dominated by one huge failure mode (169/187 flagged, 42 real vs. 46 bracket vs. **81 scrape-fail**) — the Midsummer Fire Festival bonfire-desecrate/honor-the-flame quest cluster (one pair of quests per zone, ~40 zones) plus the Isle of Quel'Danas Bounty Board (Broken Sun offensive reward quests). **The scrape-fail spike is a new, batch-wide instance of batch 59's site-tagline-bleed bug**: wowhead returned its own generic Midsummer-event-category fallback text (`一 仲夏 任務`, "a Midsummer... quest") for 81 quests' Objectives instead of unique per-zone content — left untouched (scrape-fail's default, matches DB's existing blank Objectives for this cluster, no regression). **A second confirmed instance of the exact tagline-title bug from batch 59**: quest 11937, English title literally `FLAG - all torch return quests are complete` (an internal completion-tracking flag for the Midsummer torch questline, blank English description), zhTW Title already held the bogus `巫妖王之怒 任務` tagline from some earlier pass — this time clearly identifiable as non-player-facing internal content, so skip-listed (stronger signal than batch 59's still-undecided 11552/11553). **Mistakenly re-litigated an already-settled term and self-corrected**: flagged `黑澗深淵` (Blackfathom Deeps, quests 11886/11891) as a bug against `creature_template_locale.sql`'s `黑暗深淵` and swept all 18 corpus occurrences (16 outside this batch, back to ID 908) — without checking that this exact question was already fully investigated and explicitly settled in **batch 34** (see Established terms: `黑暗深淵` is genuinely the DBC-confirmed WotLK-era name, five separate DBC files agree, but the user made a deliberate semantic-preference override to keep `黑澗深淵` project-wide anyway). Caught when the user, going from memory, flagged the sweep as backwards; independently re-confirmed via `wowhead.com/classic/tw/zone=719` (`黑澗深淵`) before reverting all 18 occurrences back. **Lesson**: check the Established terms section before treating a DBC/locale-table disagreement as a fresh bug — this one had already been fought over and deliberately decided against the DBC reading. **1 more instance of the escaped gender-token bug** (quest 11875's Details, `<他的/她的>` this time with the possessive particle baked into each branch) — genuine wording improvement worth keeping, hand-converted to `$g他的:她的;` (confirmed the corpus already uses `$g` with multi-character branches elsewhere, e.g. `$g親愛的先生:尊貴的女士;`, so this construction is safe). **3 real-classified quests were bracket-fallback in disguise** (11865/11872/11930 — same classifier gap as batches 56–59, all fully guard-protected). Proactive WH-vs-English count check: 1 candidate (11937's tagline-bleed, resolved via skip-listing). Count audit: 0 mismatches. |

| 11941–12140 (7 pre-existing skip-listed IDs: 11974, 11992, 11997, 12001, 12015, 12103, 12108) | 2026-07-22 | 0 targeted fixes — everything guard-protected or a false positive | Batch 61. Very low real-diff ratio, heavily bracket-skewed (142/163 flagged, only 7 real vs. 133 bracket + 2 scrape-fail) — the Dragonblight taunka-refugee/Agmar's Hammer/Icemist Village questline (recent-ish content with little wowhead-tw translation coverage yet). **All 7 real-classified quests were bracket-fallback in disguise** (11980/12008/12040/12064/12090/12101/12140 — same classifier gap as batches 56–60, all fully guard-protected, 0 fields touched, no manual intervention needed). Proactive WH-vs-English count check: 0 candidates. Count audit: 1 residual flag, a new false-positive subclass worth naming — quest 12099's Objectives correctly translates English's digit `4` as the Chinese numeral word `四` rather than an arabic digit, which the audit tool's digit-only regex structurally can't match (the mirror-image of the already-documented "spelled-out English number → DB digit" class) — 0 real mismatches. |

| 12141–12340 (1 pre-existing skip-listed ID: 12233) | 2026-07-22 | 0 targeted fixes — everything guard-protected or a false positive | Batch 62. Very low real-diff ratio, heavily bracket/scrape-fail-skewed (85/95 flagged, only 1 real vs. 71 bracket + 13 scrape-fail) — the Dragonblight Wyrmrest Temple magnataur-hunt/Drak'Tharon-cleansing/Wintergarde Mausoleum steam-tank questline, same recent-content-little-wowhead-coverage pattern as batch 61. **The 1 real-classified quest was bracket-fallback in disguise** (12258 — same classifier gap as batches 56–61, fully guard-protected, 0 fields touched). Proactive WH-vs-English count check: 0 candidates. Count audit: 3 residual flags, all already-documented false-positive classes — quest 12149 lists 3 named individual targets by name (no digit anywhere, the "N-named-objects" class from batch 54), quest 12238's Objectives correctly renders English's digit `5` as the Chinese numeral word `五` (batch 61's digit-vs-numeral-word class), and quest 12326's `3` comes from spelled-out "three" (crew count) while its `7` is part of "7th Legion" (`第七軍團`, an ordinal-as-proper-noun, not a count at all) — 0 real mismatches. |
| 12341–12540 (4 pre-existing skip-listed IDs: 12426, 12445, 12452, 12493) | 2026-07-22 | 9 targeted fixes across 9 quest rows + 5-row extended sweep outside batch range | Batch 63. Low real-diff ratio, heavily scrape-fail/bracket-skewed (132/143 present-in-DB flagged, only 8 real vs. 53 bracket + 71 scrape-fail) — a large Hallow's End "Candy Bucket" cluster (69 quests, one per zone) plus a Wintergarde Mausoleum/"Conquest Pit" gladiator-arena cluster in Dragonblight. **6 of the 8 real-classified quests were bracket-fallback in disguise** (12428/12429/12430/12462/12467/12540 — same classifier gap as batches 56–62, all fully guard-protected, 0 fields touched). **Don Carlos "Nice Hat..." quest pair fixed** (12513/12515, sibling repeatable-chain quests with identical English source): title `好帽子……`→`漂亮的帽子……` (matches English LogTitle "Nice Hat..." better); Objectives unified on `唐卡洛斯`, confirmed via the already-merged `creature_template_locale` UPDATE for creature entries 28126/28132 (both "Don Carlos") — wowhead's own two fetches disagreed with each other (`唐卡洛斯` vs `卡洛斯大爺`), so the locale-table entry broke the tie rather than either quest's own fetch. **Self-discovered and fully resolved a corpus-wide functional bug while reviewing the Candy Bucket scrape-fail cluster**: wowhead's Hallow's End placeholder text (`一 萬鬼節 任務.。`, a new scrape-fail signature, same underlying cause as the Darkmoon/Midsummer variants from batches 40/60) was found baked directly into DB's own Objectives field for 7 in-batch rows (12346/12347/12375/12379/12385/12405/12410) instead of the correct shared sibling text (`這種糖果桶在各地的旅店都有。來吧…拿點糖果！。`), plus one more already-committed row outside the batch (12338) — all 8 restored to the correct shared text. Also caught quest 12346's Title as a lone `糖罐`("sugar jar") outlier against 68 sibling `糖果桶`("candy bucket") instances for the identical English "Candy Bucket" quest, and found the same outlier plus the same missing-Objectives gap in 4 more sibling rows entirely outside the batch's range (12286, already-committed; 12944/12945/13473, not yet reached) — swept all 4 to match, same same-day self-contained precedent as batches 51/52/58. Corpus-wide grep confirmed 0 remaining `一 萬鬼節 任務` and 0 remaining `糖罐` after the sweep. Proactive WH-vs-English count check: 2 candidates (12465's `第四/五/六/七頁` Chinese-numeral-word ordinals, 12476's spelled-out "twelve" rendered as DB digit `12`), both confirmed as already-documented false-positive classes. Count audit: 0 real mismatches post-fix. |
| 12541–12740 (4 pre-existing skip-listed IDs: 12601, 12602, 12682, 12731) | 2026-07-22 | 65 targeted fixes across 65 quest rows (a corpus-wide functional-bug sweep, not a wowhead-vs-DB translation dispute) + 3 new skip-list additions | Batch 64. Extremely low real-diff ratio, almost entirely bracket-fallback (159/166 present-in-DB flagged, 155 bracket vs. only 3 scrape-fail vs. 1 real) — a Sholazar Basin Nesingwary-camp/Grizzlemaw troll-patrol cluster with heavy wowhead-tw coverage gaps. **Self-discovered and fully resolved a corpus-wide functional bug while reviewing the sole real-diff candidate** (quest 12567): DB's own pre-existing text had literal HTML-entity-escaped `&lt;name&gt;`/`&lt;class&gt;`/`&lt;race&gt;` (67 occurrences across 64 rows scattered through the whole file, most far outside this batch's own range — 8595, 8643-8803, 9127, 9885, 10326-11060, 13012-13093, 24743-25249) instead of the corpus's own overwhelmingly established client-token convention `$n`/`$c`/`$r` (confirmed via 2,560+ existing `$c`/`$C` instances alone, and directly corroborated against the English `quest_offer_reward.RewardText` base file's own `$N` usage for several of the affected IDs) — these would have rendered as literal garbage text in-game instead of substituting the player's name/class/race. Swept all 67 instances corpus-wide via an exact-string replace. Quest 12567 itself had a related but distinct variant of the same underlying bracket-escaping defect — a full NPC-emote sentence wrapped in `&lt;...&gt;` instead of the corpus's standard literal `<...>` emote-bracket format (same defect family as the batch-40 off-cycle `<NPC emote text.>` fix) — fixed individually. **2 new internal-tracking quests found and skip-listed** while triaging the 3 scrape-fail candidates: 12693/12694 ("Wolvar/Oracle Faction Choice Tracker," Sholazar Basin's Wolvar-vs-Oracles reputation-choice bookkeeping, blank English body) match the established `11937`-style internal-FLAG pattern exactly. **1 more instance of the batch-59/60 wowhead-tagline-bleed-into-Title bug found but left unresolved** (quest 12600, "Upper Deck Promo - Bear Mount," a real but body-blank real-world trading-card promotional quest with no ground truth available anywhere to construct a correct title) — added to Unresolved items alongside the still-open 11552/11553 case rather than guessing. **1 more skip-list addition**: quest 10638 (`LogTitle` literally "NOT A QUEST"), found because its Objectives field held a raw, untranslated English template string (`Seek <NAME> in the <DISTRICT> of Silvermoon City.`) with entity-escaped brackets — surfaced by the token-sweep grep but is a different anomaly (verbatim-English bracket-fallback, not the `$n/$c/$r` token class) needing its own skip-list entry rather than a text fix. Proactive WH-vs-English count check: 2 candidates (12550's `三個`, 12585's `二十塊`, both Chinese-numeral-word counts), confirmed as already-documented false-positive classes. Count audit: 0 real mismatches post-fix. Field-count/duplicate validation and linter clean; `git diff` sanity pass confirmed all 79 cumulative uncommitted row changes (14 from batch 63 + 65 from this batch) were exactly the intended rows, no unscoped bleed. |
| 12741–12940 (6 pre-existing skip-listed IDs: 12764, 12765, 12780, 12881, 12911, 12923) | 2026-07-22 | 1 targeted fix (a same-row internal-consistency bug) + 4 new skip-list additions | Batch 65. Very low real-diff ratio, heavily bracket-skewed (123/143 present-in-DB flagged, 113 bracket vs. 2 scrape-fail vs. 8 real) — a Zul'Drak Rageclaw-troll/Storm Peaks dwarven-outpost cluster. **6 of the 8 real-classified quests were guard-protected false positives**: 4 (12825/12834/12835/12837) turned out to be genuine unfinished/placeholder dev content whose English `LogDescription` literally starts `[PLACEHOLDER]` — DB's existing text already correctly translates the marker itself (`[佔位文字]`), so no fix was needed, just skip-listing; 2 more (12859/12904, plus title/details on several others) were the routine blank-WH-field / bracket-in-disguise pattern from batches 56–64, already-good DB content left untouched. **1 genuine same-row proper-noun/location inconsistency fixed** (quest 12863, "Offering Thanks"): Objectives correctly said `格洛梭·硬鬚` (Glorthal Stiffbeard) at `霜堡` (Frosthold), but the same row's EndText independently said `格羅薩·硬須` at `冰霜堡` — two different transliterations of the same NPC and place within one row. Corpus frequency (`格洛梭`4:1`格羅薩`, `硬鬚`4:1`硬須`, `霜堡`15:3`冰霜堡`) confirmed the Objectives' spelling as the established one; EndText corrected to match, also fixing the same field's stray `‧`(U+2027)→`·`(U+00B7) middle-dot typo (a known, still-largely-unswept corpus-wide class) in the process. **2 quests flagged as scrape-fail on inspection were confirmed to already have correct DB content** (12845 "Dalaran Teleport Crystal Flag" — an internal-tracking title, but already a legitimate literal translation, `旗幟`="Flag"; 12940, one more stray Hallow's End Candy Bucket quest outside batch 63's already-fixed range, confirmed to already hold the correct shared sibling text) — both left untouched, no bug. **4 new skip-list additions**: 12825/12834/12835/12837 (see above), matching the established `[ph]`-prefix precedent (25092/25055/10452/10453). Proactive WH-vs-English count check: 5 candidates (12754's `兩百步`=200, 12858's `六片`=6, 12861's `八個`=8, 12891's `五個`=5, 12914's `百呎`=100/`6`=6), all confirmed as the already-documented digit-vs-Chinese-numeral-word false-positive class. Count audit: 0 real mismatches. Linter, row-count/duplicate check, and `git diff` sanity pass all clean — exactly 80 cumulative uncommitted rows changed (79 prior + this batch's 1). |
| 12941–13140 (no skip-listed IDs) | 2026-07-22 | 2 targeted fixes across 2 quest rows | Batch 66. Low real-diff ratio, heavily bracket/scrape-fail-skewed (139/153 present-in-DB flagged, 104 bracket vs. 31 scrape-fail vs. 4 real) — a Storm Peaks dwarven "Elder" title-quest cluster (mirrors the batch-64 Elder-quest pattern almost exactly) plus more stray Hallow's End Candy Bucket quests outside batch 63's fixed range (all already correctly translated, confirmed via inspection, no action needed). **1 genuine count bug fixed** (quest 13008, "Scourge Tactics"): English explicitly says "free **8** Webbed Crusaders," DB's Objectives said `5位` — not a numeral-word variant, a real wrong digit; fixed to `8位`. **1 genuine untranslated-content bug fixed** (quest 13093, "Reading the Bones"): Objectives held raw, entirely untranslated English (`Choose your fate, &lt;name&gt;.。`) that turned out to be `quest_offer_reward.RewardText` verbatim (same field-repurposing pattern documented in batch 64's Elder-quest investigation) — no Chinese translation exists anywhere (wowhead's own page has no body text for this ID, only reward-item names), but the sentence is short and unambiguous, so constructed a direct translation (`選擇你的命運吧，$n。`) rather than leave raw English live in-game; this also incidentally closed out the last remaining instance of batch 64's `&lt;name/class/race&gt;` token-corruption class — confirmed 0 occurrences remain file-wide (this one evidently wasn't swept by batch 64's file-wide replace at the time, cause not fully diagnosed, but now verified clean). **2 other real-flagged fields were confirmed false positives**: 13065/13132 differed from wowhead's fetch only in the `$g`/`$n`-token vs. `&lt;...&gt;`/`<...>` HTML-rendering-artifact distinction already established in batches 57/58/64 — DB's functional-token version is correct, wowhead's bracket rendering is just how the site displays it, no fix needed. Proactive WH-vs-English count check: 1 candidate (13008, above), confirmed genuine and fixed pre-emptively during the audit phase. Count audit re-run post-fix: 0 mismatches. Linter and row-count/duplicate check clean; `git diff` sanity pass confirmed 81 cumulative uncommitted rows changed with no unscoped bleed (one fewer than the raw 80+2 sum, since 13093 was apparently already inside batch 64's sweep scope but not actually swept on disk at the time — reconciled now, 0 `&lt;name/class/race&gt;` occurrences remain file-wide). |
| 13141–13340 (5 pre-existing skip-listed IDs: 13150, 13156, 13210, 13299, 13303) | 2026-07-22 | 10 bulk-replaced quest rows + 5 corpus-wide term/name sweeps (40 rows touched, many outside batch range) + 1 same-row `$B` fix | Batch 67. High real-diff ratio driven by a substantial-wording-difference Icecrown Citadel "Skybreaker" ground-assault cluster (18/165 present-in-DB flagged real, 132 bracket, 1 scrape-fail) — the Alliance-side Skybreaker/Ymirheim/Mord'rethar/Corp'rethar questline (parallels the Horde Orgrim's Hammer chain seen in batch 66). **Bulk-replaced 9 quest rows' Title/Details/Objectives from wowhead** (13294/13295/13296/13297/13298/13300/13309/13335/13339, substantial paraphrase differences, not just wording quirks), fixing one wowhead-own stray double-comma typo (13339) in the process. **4 systemic proper-noun corrections confirmed via tier-1 DBC** (`AreaTable_zhTW.tsv`/`Map_zhTW.tsv`) and swept corpus-wide, reversing the DB's own prior majority in 3 of the 4 cases: `伊米海姆`→`依米海姆` (Ymirheim, DBC area 4513), `莫德雷薩`→`默德雷薩` (Mord'rethar, DBC area 4508), `破天號`→`破天者號` (Skybreaker, DBC area 4511 + Map_zhTW's teleport-menu entries), and confirmed (not reversed) `科雷薩`→`寇普雷薩` (Corp'rethar, DBC area 4518) was already the corpus's own 29:2 majority — the 2 outlier rows were exactly the ones just bulk-replaced. **1 NPC-name correction via cross-page wowhead consistency** (no locale-table entry exists for this NPC): Thassarian `薩薩里安`→`薩沙理安`, corroborated by an already-correct pre-existing instance at quest 13332 plus 5 independently-fetched pages in this batch all agreeing — swept 23× file-wide (was a near-even 18:17 split, not a clear majority, so cross-page fetch agreement was the deciding signal, matching the established Rokaro/Myranda precedent). **1 more single-NPC fix swept via the same-row-inconsistency check**: Absalan the Pious `阿布薩蘭`→`亞柏薩倫`, matching wowhead and the corpus's own pre-existing 3:1 majority (the 1 outlier was 13300's own EndText field, exposed by the bulk-replace touching only Objectives). **1 dropped `$B$B` paragraph break restored** (quest 13226, "Judgment Day Comes!") — DB's Details silently ran two English sentences together where the source has a clear break. **1 new scrape-fail signature found**: a 5-quest "Cloth Scavenging" cluster (13265/13268/13269/13270/13272) returns a bare `一 任務.。` placeholder with no category name filled in (a variant of the batch-38/40/59/60 generic-placeholder family missing even the category word) — DB's existing blank Objectives/Details already correctly match blank English, left untouched. **1 flagged item resolved same-day per user correction**: quests 13241/13249 (both Dalaran Archmage heroic-daily-dungeon quests) had a DB-only `此任務已經絕版。`("This quest is already discontinued") prefix not present in the English source or wowhead's fetch. Initially left as an open Unresolved item pending verification; the user then clarified the likely explanation — a "discontinued" status from checking a *retail/later-expansion* wowhead page does not mean the quest is closed on this WotLK-era server, the same era-mismatch trap the Kel'Thuzad/Blackfathom Deeps precedents warn about. Stripped the prefix from all 4 corpus occurrences (13241, 13249, plus 2 more found via corpus-wide grep: already-committed quest 8344 and not-yet-reached quest 14199) — none of these quests are actually confirmed unreachable on this project, so no skip-listing either, just removed the misleading annotation. Proactive WH-vs-English count check: 7 candidates across both passes, all confirmed as the two already-documented false-positive classes (spelled-out-English-number→DB-digit majority; one English-digit→DB-Chinese-numeral-word case). Count audit re-run post-fix: 0 real mismatches. Linter and row-count/duplicate check clean; `git diff` sanity pass confirmed 121 cumulative uncommitted rows changed (81 prior + 40 from this batch's bulk-replace-plus-sweep), spot-checked several far-outside-range swept rows for legitimacy. |
| 13341–13540 (no skip-listed IDs) | 2026-07-22 | 0 targeted fixes — everything guard-protected or already correct | Batch 68. Very low real-diff ratio, heavily scrape-fail/bracket-skewed (144/145 present-in-DB flagged, 84 bracket vs. 58 scrape-fail vs. only 2 real) — a large Hallow's End Candy Bucket cluster plus a Midsummer Fire Festival bonfire-desecrate/honor-the-flame cluster (both recurring holiday-quest placeholder patterns, batches 40/60/63/65/66), and an Icecrown/Undercity siege-scenario cluster with heavy wowhead-tw coverage gaps. **Both real-classified quests were the routine blank-WH-Objectives-field pattern** (13374/13427, guard-protected, 0 fields touched). **Scanned the entire 58-quest scrape-fail bucket for the batch-63-style baked-in-placeholder corruption pattern — found 0 instances**, a clean batch unlike several recent ones. Proactive WH-vs-English count check: 1 candidate (quest 13423, "Defending Your Title") — turned out to be a full bracket-fallback quest (wowhead has no zhTW translation at all for this ID), so DB's own `六個挑戰者`("six challengers," dropping the English's "Victorious" qualifier) has no ground truth to check against; left as an already-existing, unverifiable paraphrase rather than a confirmed bug. Count audit: 0 real mismatches. Linter and row-count/duplicate check clean; `git diff` sanity pass confirmed 125 cumulative uncommitted rows unchanged from batch 67's follow-up correction (no new edits this batch). |
| 13541–13740 (2 pre-existing skip-listed IDs: 13541, 13649) | 2026-07-22 | 1 targeted fix (gap-fill) + 4 new skip-list additions | Batch 69. Sparse range (128/198 IDs not in DB) — the Argent Tournament daily-quest/Ulduar Sons of Hodir cluster, much of it recent-ish content with thin wowhead-tw coverage. Very low real-diff ratio among present rows (70/70 flagged, 63 bracket vs. 5 scrape-fail vs. 2 real). **1 genuine translation-gap fill** (quest 13559, "Hodir's Tribute"): DB's Objectives was entirely blank (English `LogDescription`/`QuestDescription` both blank too, so no diff ever fired) while wowhead had real, substantive Chinese content — filled the gap using wowhead's text, converting a fresh instance of the `&lt;class&gt;`-entity-escaping artifact (batch 64's token-corruption bug, this time surviving in wowhead's own fetch rather than baked into DB) to the proper `$c` token while applying. **4 more instances of the wowhead-tagline-bleed-into-Title bug found and skip-listed**: 13686/13687/13700/13701, all "Marker"-titled Argent Tournament eligibility/champion-status internal bookkeeping quests — same established Tracker/FLAG pattern as 11937/12693/12694, clear-cut enough to skip-list directly rather than leave open. Proactive WH-vs-English count check: 0 candidates. Count audit: 0 mismatches. Linter and row-count/duplicate check clean; `git diff` sanity pass confirmed 126 cumulative uncommitted rows changed (125 prior + this batch's 1). |
| 13741–13940 (7 pre-existing skip-listed IDs: 13825, 13826, 13840, 13914, 13915, 13916, 13917) | 2026-07-22 | 2 targeted fixes across 2 quest rows | Batch 70. Sparse-ish range (83/193 IDs not in DB), very low real-diff ratio among present rows (108/110 flagged, 104 bracket vs. 2 scrape-fail vs. 2 real) — the Argent Tournament joust/melee-training questline continuing from batch 69, plus a Winterspring/Darkmoon cluster. **1 quest-title correctness fix** (quest 13932, "Another Year, Another Souvenir." — part of the annual Brewfest souvenir chain batch 58 already partially fixed via EndText mirror-application): DB's Title `又是一年美酒飄香時。`("Another year of fragrant beer aroma") was a loose paraphrase that dropped the actual "souvenir" concept the English title names; wowhead's `又過了一年，又一個紀念品。` matches literally, applied along with matching minor Details wording. **1 more instance of the wowhead-tagline-bleed-into-Title bug fixed by direct construction rather than skip-listed** (quest 13827, English `LogTitle` simply "Treasure!", `QuestType`/`Flags` both 0, no clear internal-tracker signal like the Marker/Tracker/FLAG pattern) — unlike the still-open 12600 case, this title is short and unambiguous enough to translate directly with no risk (`寶藏!`), so fixed rather than left open. Proactive WH-vs-English count check: 0 candidates. Count audit: 0 mismatches. Linter and row-count/duplicate check clean; `git diff` sanity pass confirmed 128 cumulative uncommitted rows changed (126 prior + this batch's 2). |
| 13941–14140 (3 pre-existing skip-listed IDs: 14106, 14111, 14119) | 2026-07-22 | 3 targeted fixes (one corpus-wide corruption sweep) | Batch 71. Sparse range (128/197 IDs not in DB), very low real-diff ratio among present rows (55/69 flagged, 53 bracket vs. 1 scrape-fail vs. 1 real) — the Northshire/Elwynn Human-starting-zone cluster plus a Pilgrim's Bounty/Winter Veil holiday-quest cluster. **Self-discovered and fully resolved a corpus-wide functional bug** (quest 13966, "A Winter Veil Gift"): DB's Objectives held the bare `一 冬幕節 任務.。` scrape-fail placeholder baked in as if it were real content — a new Winter Veil variant of the same underlying wowhead-generic-category-placeholder family (Hallow's End/Midsummer/Darkmoon precedents from batches 40/60/63). Corpus-wide grep found 2 more identical occurrences (11528, already-committed; 13203, already reviewed in batch 67 but only its Title was checked at the time) — all 3 quests share byte-identical blank English source, confirming genuine duplicates; fixed all 3 using wowhead's real translated text, converting a fresh `&lt;name&gt;`-entity-escaping artifact (batch 64's token-corruption class) to `$n` while applying. Proactive WH-vs-English count check: 1 candidate (quest 14032, the classic Northshire "Kobold Vermin" starting quest) — English `LogDescription` flavor text says "Kill 8," but the authoritative `RequiredNpcOrGoCount1` field is 10 and DB's `10個` matches that (a direct instance of the batch-40/49 stale-flavor-text-vs-real-count-field lesson, not a bug). Count audit: 0 real mismatches. Linter and row-count/duplicate check clean; `git diff` sanity pass confirmed 131 cumulative uncommitted rows changed (128 prior + this batch's 3). |

**Total scope**: `quest_template_locale` in this pending file holds **8,858 quest rows** (IDs
span 1–26034, eight fewer than before — quests 7681/7682 removed batch 39, quest 9750 removed
batch 50, quests 10452/10453 removed batch 53, quests 11402/11493 removed batch 58, quest 11937
removed batch 60, all to `skip-list.tsv`).
After batch 71, **8,430 verified**, **428 remaining** — roughly 2 more
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
- **`斷背崗哨`→`斷脊氏族崗哨`** (Spinebreaker Post, near Zeth'Gor in Hellfire Peninsula) and
  **`斷背山`→`斷脊氏族山脈`** (Spinebreaker Ridge, a *different*, English-source-confirmed-distinct
  location that a same-NPC quest pair — 10060/10062, Stone Guard Ambelan/Grelag — legitimately
  turns in at instead of the Post) — self-discovered batch 52, same pattern as the batch-51
  Stonebreaker Hold find. `AreaTable_zhTW.tsv` confirms tier-1: AreaID 3812 = `斷脊氏族崗哨`,
  AreaID 3838 = `斷脊氏族山脈` (also 3884 = `斷脊氏族小徑`, not yet encountered in any quest
  text). Swept all 42 `斷背崗哨` occurrences file-wide; only touched 2 of `斷背山`'s 4
  occurrences (10060/10062, both confirmed "Ridge" via English `quest_template`) — the other 2
  (10145/10147) were not a naming-variant case at all, see the new `ObjectiveText1`-4 entry under
  Unresolved. Do not blind-sweep `斷背山` if it resurfaces — confirm Ridge vs. Post per quest
  against English first, the DB is not internally reliable here.
- **`裂石堡`→`碎石堡`** (Stonebreaker Hold, the Horde hub in Terokkar Forest) and
  **`裂石營地`→`碎石營地`** (Stonebreaker Camp) — self-discovered during batch 51's proper-noun
  pass (not from a wowhead diff — wowhead's own text for these quests already said `碎石堡`,
  which is what first drew attention to the mismatch). `AreaTable_zhTW.tsv` confirms tier-1:
  AreaID 3683 = `碎石堡`, AreaID 3902 = `碎石營地`; `AreaPOI_zhTW.tsv` independently agrees for
  3683. DB had `裂石堡`/`裂石營地` in 52/8 occurrences respectively (only 3 pre-existing rows,
  quest 9796 from an earlier batch, already had the correct `碎石堡`). Swept all 60 occurrences
  file-wide across 33 quest rows (batch 51's own range 9947–10105 plus far outside it,
  10196–11506) in one pass, same full-file-sweep treatment as Azuremyst Isle/Stonesplinter.
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
  make about which era's name to use for this project. **Re-flagged and swept backwards by
  mistake in batch 60** (found `creature_template_locale.sql`'s `黑暗深淵` again, didn't check
  here first) — caught and reverted same-batch. If this surfaces again, it is not a new bug.
- **Icecrown Citadel Skybreaker-cluster proper nouns, DBC-confirmed (batch 67)**: `伊米海姆`→`依米海姆` (Ymirheim, `AreaTable_zhTW.tsv` area 4513), `莫德雷薩`→`默德雷薩` (Mord'rethar, area 4508), `破天號`→`破天者號` (Skybreaker, area 4511 + `Map_zhTW.tsv` teleport-menu entries) — all three reversed the DB's own prior corpus majority. `寇普雷薩` (Corp'rethar, area 4518) was already the corpus's 29:2 majority and confirmed correct, not reversed — only 2 outlier rows fixed. Also swept via corroborating (non-DBC) evidence in the same pass: Thassarian `薩薩里安`→`薩沙理安` (cross-page wowhead fetch consistency, no locale-table entry exists), Absalan the Pious `阿布薩蘭`→`亞柏薩倫` (matches corpus's own pre-existing 3:1 majority).
- **`一 萬鬼節 任務.。` Hallow's End "Candy Bucket" wowhead-tagline scrape-fail baked into DB
  (self-discovered and RESOLVED, 0 remaining corpus-wide, batch 63).** A 69-quest Candy Bucket
  cluster (one per zone, `LogTitle` "Candy Bucket" for every ID) is a new scrape-fail signature
  — same underlying cause as the Darkmoon (batch 40) and Midsummer (batch 60) generic-placeholder
  variants, this one specific to Hallow's End. Left untouched where it only ever showed up in the
  wowhead *fetch* (the normal, correct scrape-fail handling). But 8 rows (12338, 12346, 12347,
  12375, 12379, 12385, 12405, 12410) had this exact placeholder text baked directly into DB's own
  Objectives field already — a real pre-existing content bug, not a scrape-fail to leave alone —
  while all other siblings correctly held the shared real text (`這種糖果桶在各地的旅店都有。
  來吧…拿點糖果！。`). Restored all 8. Also found quest 12346's Title as a lone `糖罐`("sugar
  jar") outlier against every other sibling's `糖果桶`("candy bucket") for the identical English
  quest, and the same title-outlier + missing-Objectives pattern in 4 more sibling rows entirely
  outside batch 63's own range (12286, 12944, 12945, 13473) — swept all 4 to match, same
  same-day self-contained-fix precedent as batches 51/52/58.
- **`一 冬幕節 任務.。` Winter Veil "A Winter Veil Gift" wowhead-tagline scrape-fail baked into DB
  (self-discovered and RESOLVED, 0 remaining corpus-wide, batch 71).** Same underlying cause as
  the batch-63 Hallow's End Candy Bucket find and the batch-40/60 Darkmoon/Midsummer variants — a
  new holiday-specific instance of the generic wowhead-category-placeholder family. 3 quest rows
  (11528, 13203, 13966) had this exact placeholder baked into their Objectives field instead of
  the real shared text (`禮物上有一個小牌子寫著:冬幕節快樂，$n!。`); all share byte-identical
  blank English source, confirming genuine duplicates rather than distinct content. Fixed all 3.
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
| Archmage Alturus (17613) | `艾特羅斯` | not `奧圖魯斯` (that's the zhCN transliteration, `奥图鲁斯`, character-leaked in); confirmed via the pre-existing `locales_item` zhTW field for item 24482 ("Alturus' Report"), which independently already used `艾特羅斯` — batch 57 |
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
| Don Carlos (npc=28126/28132, Old Hillsbrad "Nice Hat..." quest pair) | `唐卡洛斯` | NOT `卡洛斯大爺` — wowhead's own two independent fetches (quests 12513/12515, identical English source) disagreed with each other on this name; settled via the already-merged `creature_template_locale` UPDATE for both creature entries, which independently agrees with the `唐卡洛斯` fetch. Also fixed the shared title `好帽子……`→`漂亮的帽子……`, matching English `LogTitle` "Nice Hat..." more literally. Batch 63. |

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
- **`&lt;name&gt;`/`&lt;class&gt;`/`&lt;race&gt;` HTML-entity-escaped client tokens (functional
  bug, project-wide, swept 2026-07-22 during batch 64)**: 67 occurrences across 64
  `quest_template_locale` rows, almost all far outside batch 64's own range, had the literal
  4-character-escaped strings `&lt;name&gt;`/`&lt;class&gt;`/`&lt;race&gt;` baked into Details/
  Objectives instead of the corpus's own overwhelmingly dominant client-token convention
  (`$n`/`$c`/`$r`, 2,560+ existing `$c`/`$C` instances alone; independently corroborated against
  `quest_offer_reward.RewardText`'s own `$N` usage for several of the affected IDs) — these would
  render as literal garbage text in-game rather than substituting the player's name/class/race.
  All lowercase, no `&lt;Name&gt;`-style capitalized variants found. Swept via an exact 3-pair
  string replace (`&lt;name&gt;`→`$n`, `&lt;class&gt;`→`$c`, `&lt;race&gt;`→`$r`); verify zero
  remaining hits after any future full-file text change: `grep -c "&lt;name&gt;\|&lt;class&gt;\|
  &lt;race&gt;"`. One related but distinct variant found the same batch (quest 12567): a full
  NPC-emote sentence wrapped in `&lt;...&gt;` instead of the corpus's standard literal `<...>`
  bracket format — same underlying escaping defect, different content shape (a whole sentence,
  not a token), fixed individually rather than swept. A third variant (quest 10638, `&lt;NAME&gt;`
  /`&lt;DISTRICT&gt;`, capitalized and non-standard) turned out to be an untranslated raw-English
  string on a `LogTitle: "NOT A QUEST"` internal-template row — skip-listed rather than fixed, not
  part of this token class at all despite the superficial `&lt;...&gt;` similarity.

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
- A quest's own DB text can carry an era-mismatch error too, not just wowhead's fetch: a
  translator-added "this quest is discontinued" note likely reflects checking a *retail/later-expansion*
  page rather than this WotLK-era server's own reachability — same underlying trap as the
  Kel'Thuzad/Blackfathom Deeps era-distinction lessons, just sourced from the DB side instead of
  wowhead's side (batch 67 follow-up correction, quests 8344/13241/13249/14199).

## Unresolved / open follow-up items

- **Quests 11552/11553 ("Rohendor, the Second Gate"/"Archonisus, the Final Gate") have a bogus
  Title** (`巫妖王之怒 任務`, literally "Wrath of the Lich King Quest") that some earlier,
  undocumented pass appears to have written from wowhead's own site meta-description tagline
  rather than real quest content — found batch 59 when the *Objectives* field independently
  reproduced the exact same tagline-bleed bug this session, but the Title's identical corruption
  had already been sitting in the DB since before this batch touched the row, undetected because
  DB and WH matched (both wrong) so no diff ever fired on it. Both quests have entirely blank
  English `LogDescription`/`QuestDescription`, so there's no ground truth anywhere (English source
  itself, DBC, or wowhead) to construct a real title from — likely unused/scrapped content, may be
  a skip-list candidate once someone confirms the quest is genuinely unreachable in-game.
- **Quest 12600 ("Upper Deck Promo - Bear Mount") has a bogus Title** (`巫妖王之怒 任務`, the
  same wowhead site-meta-tagline-bleed bug as the still-open 11552/11553 case and the now-resolved
  11937/12693/12694 cases) — found batch 64. Unlike the FLAG/Tracker cases, this one's English
  `LogTitle` describes a real (if obscure) real-world trading-card promotional item-redemption
  quest, not obviously internal/unreachable, but `LogDescription`/`QuestDescription` are both
  blank in English and no ground truth exists anywhere (DBC, locale table, or a working wowhead
  fetch) to construct a correct title from — left unresolved rather than guessing or skip-listing
  on weaker grounds than the FLAG/Tracker precedent.
- **`quest_template_locale` has 4 more per-quest text columns
  (`ObjectiveText1`-`ObjectiveText4`) that no tool in this pass has ever checked.** Discovered
  batch 52: `diff_quest_text.py`/`audit_quest_counts.py` only ever compared `Title`/`Details`/
  `Objectives` (columns 2-4); `ObjectiveText1`-4 (columns 7-10, used for multi-stage/sequential
  quest text) have been sitting outside every batch's scope since batch 1. Found by accident
  while grep-checking a proper-noun sweep's blast radius, not by any systematic check. Confirmed
  at least one genuine bug living only in this blind spot: quests 10145/10147's `ObjectiveText1`
  said `斷背山的前線指揮官金斯頓` (Kingston at "Spinebreaker Ridge") when Kingston is
  established (by the same rows' own `Details` field, and by sibling quest 10143) to be at
  Expedition Point (`遠征隊哨塔`) — fixed by direct construction, not a wowhead diff. No idea how
  many more bugs like this exist in the other ~8,800 rows' `ObjectiveText1`-4 fields across the
  whole file — this needs its own dedicated tooling (extend `diff_quest_text.py`'s field list) and
  a pass, ideally sooner rather than later given it's now a known-nonzero-bug field.
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
- **`喚風者梅恩·長角` wrong-NPC substitution (AQ War Effort / Cenarion Hold cluster, found
  batch 43, extended batch 44, RESOLVED batch 45)** — **CLOSED, 0 remaining occurrences
  corpus-wide.** This name was an incorrect stand-in for **4 different real turn-in NPCs**
  (Windcaller Proudhorn `喚風者傲角`, Bor Wildmane `鮑爾·蠻鬃`, Commander Mar'alith
  `指揮官瑪爾利斯`, Krug Skullsplit `克魯格·碎顱`) across all 29 corpus occurrences: 5 fixed in
  batch 43 (8496/8534/8535/8537/8538), 13 in batch 44 (8556/8697–8704 ring-questline's own
  `喚風者耶薩德拉`, 8738–8740's `喚風者傲角`, 8732's `克魯格·碎顱`), and the final 11 in batch 45
  — 7 turned out to be a genuine content-swap bug (quests 8778/8779/8780/8781/8786/8787/8807,
  each an AQ War-Effort donation quest with an unrelated bandage-quest's text copy-pasted
  wholesale, fixed by replacing with wowhead's per-quest-correct text) plus 3 more same-row
  `ObjectiveText4`-only fixes (8782/8808/8810, confirmed `喚風者傲角`). Every occurrence was
  individually verified against the English source or the row's own `Objectives`/`ObjectiveText4`
  field before fixing — never blind-replaced, since a single find-replace would have been wrong
  for at least 3 of the 4 real identities.
- **`德莉亞娜`→`德莉娜` (Deliana, Ironforge quest-giver, "Just Compensation"/wristguard reward
  chain, found batch 45, extended batch 46)** — corpus had zero prior majority either way;
  wowhead confirmed `德莉娜` unanimously across every real-hit instance. 28 rows swept total
  (16 in batch 45's range 8905–8937, 12 more in batch 46's range 8952–9031, including
  wowhead-no-translation rows fixed directly against DB's own text). 9 occurrences remain
  unswept further out in the corpus (this same NPC's reward chain resurfaces later) — check
  each cluster as it's reached.
- **`野獸追獵者`→`馭獸者` (Beaststalker's [item], found batch 45, extended batch 46)** —
  **RESOLVED, 0 remaining corpus-wide.** Corpus was split with no majority; wowhead confirmed
  `馭獸者` in every real-hit instance.
- **`瓦塔拉克`→`瓦薩拉克` (Lord Valthalak, Blackrock Mountain amulet questline, found batch
  46)** — corpus had three spelling variants (`瓦塔拉克`, `瓦薩拉克`, and the correct one);
  wowhead confirmed `瓦薩拉克` unanimously. Swept within batch 46's own range as part of the
  general bulk pass; not individually tracked outside it.
- **`伯德雷`/`佈德利`→`布德利` (Bodley, same questline, found batch 46)** — corpus had *three*
  different spellings for one NPC; wowhead confirmed `布德利` unanimously across every real-hit
  instance, including 6 wowhead-no-translation rows fixed directly against DB's own
  pre-existing shared text. Swept within batch 46's own range only.
  ~16 more `馭風者` occurrences remain elsewhere in the corpus, unverified.
- **Raw, unconverted simplified Chinese in `quest_template_locale`** (found batch 9) — a
  distinct issue from the zhCN-vocabulary-leak problem this pass otherwise targets (never
  OpenCC-converted at all, not just translated with zhCN word choices). Batch 9's original list
  of 40 IDs was **re-verified against live content in batch 56** — 20 of the 40 were already
  Traditional (fixed as a side effect of other work, note never updated) and 1 (25092) was
  separately unfinished/placeholder content, skip-listed rather than converted. The remaining
  **17 were fetched against wowhead-tw first to check for a real translation to bulk-apply —
  all 17 came back bracket-wrapped (no zhTW translation exists on wowhead for any of them)** —
  so fixed via direct OpenCC simplified→traditional conversion instead (`s2twp` profile,
  Taiwan-standard with phrases; called via `ctypes` against
  `/lib/x86_64-linux-gnu/libopencc.so.1.1` + `/usr/share/opencc/s2twp.json` — the `opencc`
  apt package needs sudo, unavailable in-session, but the runtime lib was already present from
  `libopencc1.1`/`libopencc-data`), preserving each existing translation's wording exactly,
  only fixing the character set: 11164, 11435, 11992, 12024, 12918, 13004, 13096, 13108, 13109,
  13252, 13380, 13986, 13997, 14032, 14355, 14409, 25055. Verified clean via OpenCC round-trip
  (re-running `s2twp` over the fixed text is a no-op iff no simplified chars remain — confirmed
  for all 17) and `audit_quest_counts.py` (no new mismatches). **All 40 of the original batch-9
  list are now resolved** (3 earlier: quest 755 batch 9, 10999/11132 batch 56, both also
  bracket-fallback direct conversions; 20 already-Traditional; 1 skip-listed; these 17). If
  more raw-simplified rows turn up in future batches (this was a corpus-wide grep finding, not
  guaranteed exhaustive), add them here and follow the same wowhead-first-then-OpenCC-fallback
  pattern.
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
- `apply_fixes.py` (not committed to the repo — a per-batch scratch script, rewritten/copied
  forward from the previous batch's scratch dir each time): parses `parsed_diff.json`, and for
  every ID in `real_ids.json` overwrites Title/Details/Objectives with wowhead's text, skipping
  any field in a per-batch `EXCLUDE_FIELDS`/`EXCLUDE_TITLE` map. **Must include this guard**
  (added batch 53 after finding it had silently corrupted 3 rows across 2 batches, 10149/10401/
  10497 — see batch 53's entry): skip a field if wowhead's fetched value is an empty string
  while DB's existing value is not. Without it, a quest correctly classified "bracket" overall
  (no real zhTW translation for its Title/Details) but where wowhead's fetch happened to come
  back *genuinely blank* for the Objectives field specifically gets misclassified as "real"
  (since not *every* field is bracket-wrapped) and then has its real Objectives text silently
  replaced with an empty string, plus Title/Details overwritten with raw bracketed English.
  Re-scan any older batch's saved `parsed_diff.json`/`real_ids.json` for this exact pattern
  (`wh.strip() == "" and db.strip() != ""` for an ID in `real_ids`) if the guard's absence is
  ever suspected before batch 53's date.
- **A second, related guard, added batch 56** (found after the batch-53 blank-field guard alone
  still let 8 rows get corrupted — 11006/11013/11020/11027/11054/11070/11097/11107, all reverted):
  a quest with one field that's genuinely bracket-fallback (no zhTW translation, wowhead returns
  `[English]`) and a *different* field that came back blank slips past the classifier the same
  way — the blank field isn't bracket-wrapped, so "every flagged field is bracket" fails and the
  quest lands in `real_ids` anyway, and the bracket field (not blank, so the batch-53 guard alone
  doesn't catch it) gets its raw English bracket text applied verbatim over DB's real Chinese.
  The fix: skip a field if wowhead's value is bracket-wrapped (`[...]`) while DB's own value for
  that field is not. Unlike the blank-field case, this one is **silent even in the post-fix
  verification diff** when it succeeds — a fully bracket-overwritten field now byte-matches
  wowhead exactly, so no diff shows up. Detecting it requires scanning the *original*
  `parsed_diff.json` for `real_ids` entries where any field's WH value is bracket-wrapped and
  DB's isn't, not just eyeballing the post-fix diff residuals — do this check on every batch's
  original real_ids before trusting the apply step went cleanly, the same way the count audit
  gets run proactively rather than only after the fact.
- When writing any one-off script that removes or replaces a specific SQL row by ID, never use
  an unanchored non-greedy regex like `INSERT INTO ...;.*?VALUES \(<id>,.*?;\n` — `.*?` between
  the statement keyword and the target ID will lazily match from the *first* occurrence of that
  keyword anywhere earlier in the file, not the one immediately preceding the target row, and
  can silently delete or corrupt everything in between (self-caught in batch 53: an unanchored
  removal deleted ~11,500 lines instead of 2). Find the target row's own `VALUES (<id>,` marker
  first with a plain string search, then walk outward (backward to `INSERT INTO`, forward via a
  paren/quote-depth counter to the terminating `;\n`) to get an exact span for just that row.
  Always verify the file's `INSERT` row count immediately after any such edit, before moving on.

A typical batch: set `ZHTW_SCRATCH`, write the ID range (minus skip-list) to
`wowhead_final_zh.txt`, run `fetch_quest_text.py` in the background, then run
`audit_quest_counts.py` and `diff_quest_text.py --strict` once the fetch completes, review
every flagged quest against the ground-truth priority order (and the Established terms
glossary above for anything that looks familiar), apply fixes, re-run both checks plus the
linter/field-count validation, then update this file's Completed ranges table, add any new
established terms/rulings, and move the Next-batch pointer.

## Next batch

Resume from quest ID 14141 (batch 72), skipping any ID present in `skip-list.tsv`. See the
Total scope note above for the current verified/remaining count. Standing process reminders
(wowhead-as-default-ground-truth, scoped find/replace + git-diff sanity pass, proactive
WH-vs-English count cross-check, watch for resurfacing terms) are folded into Methodology and
Established terms above rather than repeated here — check those sections, not batch-specific
addenda, before starting a new batch.
