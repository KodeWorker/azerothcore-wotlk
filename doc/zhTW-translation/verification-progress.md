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
| 1541–1740 (excl. skip-listed 1659, 1660, 1662–1664) | 2026-07-16 | ~10 targeted fixes + 1 naming sweep (加科因/黑暗縛靈者→加金/『黑暗縛靈師』, 7 quests) | Batch 9. Lowest bug density yet (42/195 flagged, and 118 of those 195 candidate IDs turned out to be unused quest IDs with no `quest_template` row at all — not gaps, just gaps in the ID space). Several fixes had no `_locale` table to settle them (Gakin/Tormus/Umbral Ore/Bath'rah naming) — resolved by user judgment call rather than the usual ground-truth hierarchy; see below. |
| 1741–1940 (no skip-listed IDs in range) | 2026-07-16 | ~20 targeted fixes + 6 project-wide term sweeps (亡靈天災→天譴軍團 26×, 提瑞斯法→提里斯法 65×, 洛丹倫→羅德隆 33×, 阿爾薩斯→阿薩斯 13×, 碎木哨崗→碎木崗哨 39×, 扎拉贊恩→札拉贊恩 12×) | Batch 10. See below — DBC ground truth (`AreaTable_zhTW.tsv`/`Faction_zhTW.tsv`) again showed the corpus-majority spelling was wrong in every case (Tirisfal 65:41, Lordaeron 33:11), same pattern as batch 6's Kalimdor. Also the first batch to directly fetch item/NPC wowhead pages via `curl` mid-session (not the pre-fetched quest jsonl) to settle no-locale-table disputes — see below. |
| 1941–2140 (excl. skip-listed 2018, 2020, 2058, 2059) | 2026-07-16 | ~15 targeted fixes, no project-wide sweeps | Batch 11. Lowest bug density yet (28/196 flagged). Two genuine truncation bugs found and restored (quest 2038's item list, quest 2118's severely truncated/corrupted Objectives). Confirmed two more cases of wowhead's own quest-page fetch being wrong where DB was already correct (`祈倫托` vs zhCN-leak `肯瑞托`, matching batch 3's established finding; `亡靈哨兵` vs generic `不死生物哨兵`). |
| 2141–2340 (no skip-listed IDs in range) | 2026-07-16 | ~8 targeted fixes, no project-wide sweeps | Batch 12. Lowest bug density yet again (23/200 flagged). A cluster of jewelry/Uldaman-themed quests (2198-2340) had several title/rank disputes settled via a direct `curl` fetch of the NPC's own wowhead page (Renzik "The Shiv" → `『剃刃』雷吉克`, not DB's `“剃刀”`). Fixed a real mistranslation (English "restorative elixirs" rendered as "fine wine" in DB) alongside missing narrative detail. Confirmed DB's literal `"TdK"` engraving (quest 2198) was correct against a fabricated wowhead Chinese-name substitution. |
| 2341–2540 (no skip-listed IDs in range) | 2026-07-16 | ~11 targeted fixes, no project-wide sweeps | Batch 13. One genuine content-swap bug found (quest 2499's Details didn't match its own English source at all) and two truncated Objectives restored (2438, 2518), one of which also carried a wrong location (quest 2518 said "river northeast of here" instead of English's "northern borders of Teldrassil"). Direct NPC-page `curl` fetches settled two more no-locale-table disputes (Bena **Winterhoof** → `貝娜·冬蹄`, not `本娜·冰蹄`; Taskmaster Fizzule confirmed `工頭`, not wowhead's own quest-page `監工`). |
| 2541–2740 (no skip-listed IDs in range) | 2026-07-16 | ~7 targeted fixes, no project-wide sweeps | Batch 14. Lowest bug density yet (18/200 flagged). A wrong location (quest 2561: "door of a nearby room" vs English's "deepest areas of Ban'ethil Barrow Den"), a fabricated NPC name+missing rank (quest 2702, confirmed via `creature_template`'s literal English name "Corporal **Thund** Splithoof" — DB had invented "Sander"), a dropped gender-branch token (quest 2609, hardcoded to one gender instead of the `$g male:female` branch), and a restructured narrative that spoiled its own reveal (quest 2622). |
| 2741–2940 (excl. skip-listed 2868) | 2026-07-16 | ~35 targeted fixes + 3 project-wide sweeps (質量→品質 8×, 大工匠梅卡托克→高等技工梅卡托克 10×, 惡魔獵手→惡魔獵人 22×) | Batch 15. Highest bug density since batch 3 (76/199 flagged, 104 real rows in range). A zhCN-leak term caught mid-batch (`質量` for "Quality" is mainland usage; zhTW uses `品質`, `質量` means "mass" in Taiwan) and confirmed via NPC-page fetch that corpus-majority `大工匠梅卡托克` (10 occurrences) was wrong the whole time — same pattern as batch 10's Kalimdor and batch 13's Bena Winterhoof. Also found genuinely corrupted/duplicated text in 3 quest rows (2771-2773) and an MT-artifact name bug (`羅克位元`, "Rockbiter" mistranslated as the computing term "bit"). Post-batch: Demon Hunter's official class-page name (`惡魔獵人`) overrides a 22:0 same-corpus majority — kept. Generic "trogg" went through three reversals same-day, settling project-wide on `穴居怪` — later reverted a 4th time in batch 16's follow-up, see below; current answer is `穴居人`. |
| 2941–3140 (89 IDs not in DB, incl. all of 3003–3081 except a handful — a large real gap in the ID space, not a scan error) | 2026-07-16 | ~26 targeted fixes across 15 quest rows, no new project-wide sweeps | Batch 16. 111 real rows in range; high bug density among them (81 flagged by the strict diff before dedup against non-existent IDs). One genuine content-swap bug (quest 2949's Details wrongly duplicated quest 2947's Ironforge/"TdK" text instead of its own Orgrimmar/"NOG" content — both are "Return of the Ring" but for different factions). One confirmed wowhead-fetch error going the *other* direction (quest 3121: wowhead's own fetch returned an entirely different NPC/location that contradicts the English source; DB's `夏拉什·火刃`/`莫沙徹營地`/`拉瑞斯小亭` was correct all along — false positive, no change). Extended the already-settled Gordunni-Ogre exception (`戈杜尼食人魔`→`戈杜尼巨魔`, 7 quests) and the Troll-is-always-`食人妖` rule (Vilebranch/Witherbark/Sandfury/Nekrum's Zul'Farrak troll, covering quests 2989/2991/2993/2994/3042). A count fix (quest 3127: DB said kill 12 mountain giants, English/wowhead both say 7). Two more NPC names settled via `creature_template_locale` (Krueg **Skullsplitter** id 4544 → `劈顱` not `碎顱`; Oran **Snakewrithe** id 7825 → `蛇繞` not the phonetic `斯內克威瑟`) plus a title mistranslation each for quests 2969 (`精靈龍的自由`→`所有生物的自由`, English is "Freedom for *All Creatures*") and 2995 (`聯絡中心`→`溝通管道` for the title and closing line only — wowhead agrees with DB's `聯絡中心` for the *opening* sentence describing what the lodge *is*, so that occurrence was left alone; only the "destroy their lines of communication" occurrence changed). Also fixed an item-name pair (`徽記之戒`/`戒指`→`璽戒` for "signet ring", quest 2972) and a badge/medal pair (`徽章`→`勳章`, quest 2991, same pattern as batch 13). Resolved an internal DB inconsistency in the Krueg Skullsplitter quest chain (2973/2974: Objectives said Thousand Needles in one row while EndText said Feralas/Camp Mojache in both — English EndText confirms Feralas ["Wildwind Lake in Feralas"] for both quests, so both were harmonized to Camp Mojache/Feralas, matching each quest's own EndText; also fixed a `莫沙沏`→`莫沙徹` typo). See below for the full per-quest log. |

| 3141–3340 (189 IDs not in DB — the sparsest range yet, only 10 real quest rows) | 2026-07-16 | 7 targeted fixes across 3 quest rows, no project-wide sweeps | Batch 17. Discovered `diff_quest_text.py` takes no numeric range arguments at all — it diffs the *entire* cached jsonl every run, so results had to be filtered to this batch's ID range in Python before review (earlier batches' re-appearing diffs, e.g. quest 2947 showing an unrelated `基瑟爾` wowhead mis-scrape, are stale noise from that full-corpus rerun, not new findings — ignored). Of the 10 real rows, 8 were flagged; 3 held real content errors after checking English `quest_template` (Gahz'ridian quest 3161: `巨魔`→`食人妖`, trolls not ogres; quest 3182's title `證明信`→`證明文件`, "Proof of **Deed**" is a document not a letter, plus its Details opened with a vague paraphrase instead of the specific "axe head still lodged in it" claim; quest 3201's title was fabricated outright — `館長的證明！`→`終於！`, matching English "At Last!" — plus a bracketed stage-direction that named the wrong action entirely). The other 5 flagged quests were confirmed as punctuation/style-only diffs (case, `！`/`!`, minor synonym swaps) and left untouched. Also checked two corpus-wide patterns the diff surfaced (`透過`/`通過` split 128:66, `亡靈`/`不死族` split 231:11) against the specific flagged instance's context — both were legitimate existing usage in context, not the zhCN-leak error pattern from earlier batches, so left alone rather than blindly swept (per `[[feedback-zhtw-no-blind-sweep]]`). |

| 3341–3540 (excl. 16 skip-listed IDs; 113 more IDs not in DB) | 2026-07-16 | 28 targeted fixes across 20 quest rows, no project-wide sweeps | Batch 18. 71 real rows in range; 54 flagged, moderate-to-high bug density. One severe content bug found (quest 3361: DB's entire Details narrative was fabricated/wrong — described a nonsensical earthquake-and-travel story instead of the real "troggs driven out of Gnomeregan, radiation, trolls stole my belongings" plot; rewritten from the English source). Several proper-noun fixes settled via `creature_template_locale` (Amnennar the Coldbringer → `『寒冰使者』`, not `寒冰之王`; Lord Arkkoroc needed the missing `領主` title added across 3 quests; Magatha **Grimtotem** → `恐怖圖騰`, not the fabricated `野性圖騰`; Dryad race term → `林精`, not `樹妖`; a Kalaran Windblade surname typo `溫佈雷`→`溫布雷`; Golem → `魔像`, not `傀儡`). Extended the Troll-is-always-`食人妖` rule to 4 more quests (3373, 3380, 3445, 3527) and a Gnome/Goblin race mix-up fix (Marvon Rivetseeker is explicitly a goblin in English, quests 3380/3445 both said gnome). A missing item descriptor restored (`bramble wand` → `刺藤魔杖`, not generic `魔杖`) and a dropped narrative detail restored (quest 3521's Grell alternate-ingredient-source, using the established `劣魔` term). Also confirmed 3 wowhead-fetch-error false positives going the *other* direction — DB was already correct and wowhead's rendering was wrong (quest 3376: `勇者風羽` matches English "Brave Windfeather" exactly, wowhead fabricated a first name and wrong rank; quest 3523: `誓言石` matches English "Oathstone", wowhead's `黑曜石` is wrong; quest 3525: `神像` matches English "Idol", wowhead's generic `塑像` loses the religious connotation). See below for the full per-quest log. |

| 3541–3740 (excl. 4 skip-listed IDs; 153 more IDs not in DB) | 2026-07-16 | 12 targeted fixes across 9 quest rows, no project-wide sweeps | Batch 19. 43 real rows in range; 29 flagged, moderate density. Mostly a dense run of near-identical Gnome/Goblin Engineering trainer-questline template text (3629–3643), which surfaced a real trainer-identity swap (quest 3638 said "become a Gnome technician" when the quest's own content and trainer are explicitly Goblin) and a confirmed NPC-title fix via `creature_template_locale` (Tinkmaster Overspark → `技工大師`, not `工匠大師` — applied project-wide including one occurrence outside this batch, quest 2922, since it's a single confirmed proper noun). Also fixed a Felhound race-term error (matches the batch-10 established `惡魔` > `地獄` preference for Fel creatures), a missing title (`Lady Sevine`), a location nuance ("overlooking Azshara"), and an Arcane/generic-magic distinction. Quest 3621's `莫什奧格食人魔山` → `莫什奧格巨魔山` (Mosh'Ogg ogre mound): initially left as-is on the theory that both `食人魔`/`巨魔` are valid Ogre terms, but a follow-up DBC check (`AreaTable_zhTW.tsv`, AreaID 105) found this is the *official client zone name* — `莫什奧格巨魔山`, no ambiguity. Fixed project-wide (3 occurrences: quests 591, 2760, 3621 — the first two outside this batch's range, swept anyway since it's a single confirmed proper noun from the highest-tier ground truth). See the corrected note below. Confirmed one race-identity false positive (quest 3542: DB's `上層精靈` correctly matches "Highborne," wowhead's `高等精靈` conflates it with the distinct "High Elf" race). |

| 3741–3940 (excl. 2 skip-listed IDs; 144 more IDs not in DB) | 2026-07-16 | 11 targeted fixes across 9 quest rows, no project-wide sweeps | Batch 20. 54 real rows in range; 31 flagged, moderate density. Two dropped sub-location details (quests 3761/3786, both missing "Elder Rise of Thunder Bluff" — the same location omission recurring across a related quest cluster), two incomplete titles (quests 3762/3763, "Arch Druid Runetotem"/"Arch Druid Staghelm" both missing their surname), a missing "Lord" title (quest 3907, Lord Incendius), a wrong emote fix (quest 3861, `/cheer` mistranslated as a vague "look happy" — fixed to the established `歡呼` emote name, also correcting wowhead's own wrong "flap wings" guess), a dropped narrative clause (quest 3901, "more mindless minions of the Lich King"), and a typo (quest 3914, `安戈洛爾`→`安戈洛`). Also resolved the `傀儡`/`魔像` (Golem) term flagged as an open follow-up item after batch 18 (quest 3911, confirmed `魔像` via `creature_template_locale`). Confirmed a 4-quest false-positive cluster going the *other* direction: quests 3821/3823/3824/3825's "Firegut ogres" — English confirms Ogre, so DB's `火腹食人魔` was already correct throughout and wowhead's `火腹巨魔` is wrong (matching the general default Ogre=`食人魔` rule, no confirmed clan exception here); left untouched. Also confirmed quest 3901's kill-count discrepancy (DB said 8, wowhead said 12) resolved in DB's favor — English confirms 8. |

| 3941–4140 (no skip-listed IDs; 141 more IDs not in DB) | 2026-07-17 | 28 targeted fixes across 15 quest rows, no project-wide sweeps | Batch 21. 59 real rows in range; 39 flagged, high density. A dense Blackrock Depths/Burning Steppes cluster surfaced 4 confirmed proper-noun fixes via `creature_template_locale`/`item_template_locale`: Ginro **Hearthkindle** (`基恩諾·火花`→`燃爐`, 3 quests — the old name didn't match "Hearthkindle" at all), Felpaw **Ravager** (`魔爪掠奪者`→`劫毀者`), Maxwort **Uberglint** (`尤博格林`→`尤柏格林`), and Black Dragonflight Molt / Fractured Elemental Shard (both items DB shortened to generic names, restored to their full established item names, quests 4022/4024/4061/4062/4063). Also resolved a 3-quest title inconsistency for **Warlord** Goretooth (DB rendered his title three different wrong ways — `軍官`/`大人`/`軍閥` — across quests 4081/4082/4132; fixed all to this corpus's established `督軍`), extended the `傀儡`→`魔像` (Golem) fix to 3 more quests (4061/4062/4063), a title fix matching English "Corruption" over DB's "Fallen" (quest 4120), and a title+location fix for Shadowmaster Vivian Lagrave (quest 4133, DB dropped both her rank and the specific "Blackrock Depths" location). |

| 4141–4340 (excl. 2 skip-listed IDs; 143 more IDs not in DB) | 2026-07-17 | 41 targeted fixes across 20 quest rows, no project-wide sweeps | Batch 22. 55 real rows in range; 43 flagged, high density. An Un'Goro Crater quest chain (Muigin and Larion) had both names wrong throughout 5 quests, confirmed via `creature_template_locale`, plus a real count error (20→15, matching `RequiredSourceItemCount`) and the recurring `安戈洛爾`→`安戈洛` typo. 3 more proper-noun fixes via ground truth: Zarrin (missing delivery target restored), the "A-Me 01"→`艾米 01` transliteration (3 quests), and Lady Katrana Prestor's title (`女伯爵`→`女士`). Fixed a creature-type/color mix-up in a dragon-kill quest (`火鱗龍人`→`黑色龍人`, plus disambiguating `龍人`/`龍裔` which DB had conflated). Caught 3 previously-confirmed fixes that had been missed in earlier batches within their own quest chains — Lord Incendius' title, Ginro Hearthkindle's name, and the Golem term — all now applied to their remaining occurrences (quests 4263, 4265, 4282). One item name fix (Badge→Medallion, scoped to just the Objectives field since English's own Details text uses the colloquial "badge" wording too, so that occurrence was left matching its English counterpart). Surfaced a genuinely unusual case to the user rather than resolving it unilaterally: quest 4184's English source explicitly names King Varian Wrynn, but both DB's pre-existing text and wowhead's independent scrape agree with each other on Bolvar Fordragon instead — user confirmed Bolvar is correct lore-wise and the actual quest-ending NPC, so left unchanged (see below). |

**Total scope**: `quest_template_locale` in this pending file holds **8,867 quest rows** (IDs span 1–26034). After batch 22, **2,317 verified**, **6,550 remaining** — roughly 33 more ~200-ID batches at the current pace.

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
  per `creature_template_locale`) — *`碎石穴居人` was revised to `碎石穴居怪` in batch 15, then
  reverted back to `碎石穴居人` in batch 16's follow-up (4th reversal), see the trogg note in
  batch 16's log*: 12 occurrences across 6 quests (170's own `石齶` variant spelling not yet
  checked — flag for a future batch).
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

### Batch 9 (1541–1740) fixes log

Lowest bug density yet (42/195 candidate IDs flagged) — but 118 of those 195 candidates turned
out to be unused quest IDs with no `quest_template` row at all (confirmed by cross-checking
against the base English table, not assumed), leaving only 77 real rows actually reviewed. This
batch surfaced a much bigger structural finding than any single quest bug: **the DB's zhTW text
was majorly OpenCC-converted from zhCN** (a simplified→traditional *character* converter, not a
re-translation) — confirmed directly by the user. This means corpus-wide self-consistency is a
much weaker signal than prior batches treated it as, since the whole corpus can share one
zhCN-origin translation pass. See `[[feedback-zhtw-ground-truth-priority]]` (updated this batch)
for the full implication. Also produced two mid-batch corrections after applying fixes too
broadly on the first attempt — recorded below so future batches don't repeat the mistake.

**Content/name fixes with clear ground truth**:
- Quest 1599 (`開端`): `霜鬃巨魔新兵`→`霜鬃食人妖新兵` — creature_template confirms "Frostmane
  **Troll**" (matches `[[feedback-zhtw-troll-ogre-terms]]`, no exception for this tribe).
- Quest 1678 (`維吉雷克`): `這一地區最強大的巨魔`→`...食人妖` — English explicitly "toughest
  **troll**".
- Quest 1638 (`戰士的訓練`): Objectives dropped the location entirely (`和哈里·伯加德談一談。`)
  while English LogDescription says "Speak with Harry Burlguard **in Stormwind**" — replaced
  with wowhead's verbatim `到暴風城找哈里·伯加德談話。`.
- Quests 1690/1691 (title + body): `總工程師比格維茲`→`首席工程師比格維茲` — quest 1690's own
  EndText already said `首席`, corpus-wide 14:3 majority confirms it. Also 1690 Details:
  `地精們伸張正義`→`哥布林們伸張正義` (English literally says "goblin").
- Quests 1690/1691 **titles**: `廢土的公正`→`制裁廢土遊民`/`制裁更多廢土遊民` — initially
  dismissed as "both valid translations, no clear error" per the pre-OpenCC-insight heuristic;
  the user flagged this specifically as an example of zhCN-style literal noun-phrase titling
  vs wowhead's more idiomatic verb-first zhTW style. Reversed after the OpenCC finding (see
  above) — this is the case that triggered updating the ground-truth-priority memory.
- Quest 1707 (`收集水袋`): `5隻廢土水袋`→`5個廢土水袋` (Objectives + Details) — water pouches
  aren't animals, `隻` is the wrong measure word.
- Quest 1719 (`格鬥考驗`): `複命`→`覆命` (corpus-wide 496:2 majority, DB typo) and
  `圖維基·弗拉海德` left as-is (no ground truth either way — see below).
- Quest 1701: Title `弗倫的鎧甲`→`淬火鎖甲` — sibling quests in the same armor-crafting chain
  (1705 `燃燒之血`, 1708 `鐵珊瑚`, 1710 `曬焦的蛋殼`) all use item-name titles matching their
  English LogTitle exactly; 1701 broke the pattern with a character-name title instead of
  matching "Fire Hardened Mail".
- Quest 1645: stray trailing `*` on the title (`聖潔之書*`→`聖潔之書`) — same cosmetic
  corruption class as batches 2/7.

**No-locale-table naming disputes — resolved by direct user decision** (no
`creature_template_locale`/`item_template_locale` entry exists for any of these; each was DB
self-consistent across multiple rows vs. wowhead also self-consistent, with no third source to
break the tie):
- **Gakin the Darkbinder** (creature 6122, quests 1685/1688/1689/1715/1717/1738/1739, 7 quests):
  switched DB's `加科因`/`黑暗縛靈者` to wowhead's `加金`/『黑暗縛靈師』` — "Gakin" is
  phonetically closer to `加金` (jiā-jīn) than `加科因`. Note wowhead itself was *not* fully
  self-consistent (1685's own title/Details still said `加科因`, only Objectives said `加金`)
  — the DB fix is now more internally consistent than wowhead's own page. Quest 1286's
  unrelated `加科因` (a different NPC, "Balos **Jacken**", confirmed via English
  `quest_template`) was correctly left untouched — coincidental transliteration overlap.
- **Tormus Deepforge** (quests 1618/1680/1681) + **Umbral Ore** (quest 1681): switched DB's
  `託姆斯`/`暗影礦石` to wowhead's `托姆斯`/`陰影礦石`.
- **Bloodstone Choker** (quests 1688/1689) + **Elura's Medallion** (quest 1686): DB was
  internally inconsistent on the Choker itself (`血石項圈` in 1688 vs `血石頸環` in 1689 for the
  *same* item) while wowhead agreed with itself in both — adopted wowhead's `血石頸飾`. Also
  `徽章`→`勳章` for Elura's Medallion (`勳章`/medal is semantically closer to "Medallion").
- **Bath'rah the Windwatcher** (quest 1712 only): corpus was split exactly 8:8 across two
  different quest chains (1712-area uses `捕風者`; a separate chain 8409-8414, outside this
  batch's range, uses `觀風者`) — switched only 1712 to `觀風者` (more literal match for
  "Windwatcher"). Quest 8411 itself has both spellings in the same row — flagged for whichever
  future batch reaches it.
- Left alone (no ground truth, no strong signal either direction): Luglunket's name
  (`魯格倫克`, quest 1707), Twiggy Flathead's name (`圖維基`, quest 1719), Anvilmar's spelling
  (`安威瑪爾` vs `安威瑪`, quest 1599).

**Void terminology — user correction, scoped not swept**: quests 1598/1689/1739 had
`虛空`(DB)/`虛無`(wowhead) diffs. Corpus-wide `虛空` outnumbers `虛無` 449:16, which initially
looked like strong evidence `虛空` was correct — the user first confirmed this directly, then
corrected it: "please use 虛無 for those 3 quests". Applied `虛無` to exactly these 3 quests
only (not a corpus sweep) — corpus-majority counts are a heuristic, not a substitute for direct
confirmation when the user has specific knowledge the count doesn't capture.

**Mid-batch process correction — blind pattern-replace walked back**: attempted a corpus-wide
regex sweep of `透過`→`通過` for the "pass a trial" grammatical sense (26+ raw pattern matches)
without checking each instance's real English source first. The user stopped this immediately:
"no simple match and replace, we replace then due to english 'pass'". The sweep had already
touched 18 rows entirely outside batch 9's scope (spanning already-verified batch 7/8 quests
and far-future IDs up to 10885) — all 18 reverted to their pre-sweep (git HEAD) text. Kept the
fix only for the 3 rows within batch 9 (1698/1699/1719), each individually verified against
`quest_template`'s real English text confirming literal "pass his/the trial/test" wording.
**Lesson: a plausible grammatical pattern is not itself grounds for a corpus-wide sweep — verify
each instance against the real English source, the same rule that already applied to counts and
proper nouns, now confirmed to apply to grammar/idiom choices too.**

**`里`→`裡` locative sweep — built a precision classifier instead of a blind sweep**: initial
survey showed the raw pattern is dominated by false positives (personal-name transliterations
ending in that syllable — 奈辛瓦里/Nesingwary 129×, 塞納里 504×, etc. — none of which should be
touched). Built a classifier requiring the immediately-preceding text to end in a known
container/place noun (`廢墟`, `協會`, `洞穴`, `沼澤`, etc.) and excluding anything adjacent to a
name-boundary interpunct `·` or a known unit/idiom word (`英里`/`公里`/`海里`/`千里`/etc.) —
found 17 high-precision matches (14 are `廢墟裡`/ruins alone) and fixed all 17. Correctly
excluded `迷霧里斯克` (a proper place name, "Mistlereach" — not "in the mist"). This is not a
full sweep of the corpus's `裡`/`里` ambiguity, only the subset matched by the container-noun
whitelist; broader coverage would need either a longer noun list or per-instance manual review.

**Stray fix in an already-verified batch**: while surveying for unconverted-simplified-Chinese
markers (see below), found quest 755 (batch 5, already marked verified) still had `山后`
(simplified "after/behind") where traditional requires `山後` — fixed in place.

**Bigger finding, explicitly out of scope for this batch**: the same survey found **40 quest
rows (IDs 3062–25092, all well past where any batch has reached) containing raw, unconverted
simplified Chinese** — not vocabulary drift, but literally un-OpenCC'd text (e.g. quest 11435:
`你好，$n！谢谢你赶走了无头骑士！`). This is a distinct, larger problem from the zhCN-vocabulary
-leak issue this whole pass has been fixing, and will need its own dedicated pass. Full ID list:
755 (fixed, see above), 3062, 4496, 4507, 8224, 8365, 9852, 10690, 10999, 11132, 11164, 11272,
11435, 11452, 11453, 11992, 12024, 12119, 12122, 12123, 12124, 12851, 12918, 13004, 13096,
13108, 13109, 13248, 13252, 13372, 13375, 13380, 13423, 13959, 13986, 13997, 14032, 14355,
14409, 25055, 25092 (detection method: scan for common simplified-only characters with no
traditional overlap — not yet formalized into `scripts/`).

**False positives correctly rejected** (wowhead punctuation/character-variant quirks, or
legitimate paraphrase — no fix needed): quests 1578/1683 (fullwidth punctuation, 汙/污, 溼/濕
character variants — cosmetic, below the fix threshold), the `一談`→`話` paraphrase pattern
across ~10 quests in the warrior-trainer chain (1639/1640/1661/1666/1679/1684/1698/1718 —
stylistic variance, not a content error), quest 1710 (`雙足飛龍` — briefly reconsidered given
the OpenCC finding above, since the corpus-majority evidence for it is exactly the weak kind of
signal this batch learned to distrust, but confirmed correct as-is after all; no ground truth
exists either way for "Wyvern" specifically — flagged as an open question if a Spell.dbc-style
extract ever becomes available to settle it properly).

### Batch 10 (1741–1940) fixes log

54/200 quests flagged (70 real rows in range, no unused-ID gaps this time — unlike batch 9,
this range is densely populated with real quests). Continued applying the OpenCC-origin lesson
from batch 9: several corpus-majority spellings turned out wrong once checked against DBC
ground truth, and several no-locale-table disputes were settled by fetching the entity's own
dedicated wowhead page directly via `curl` (title-tag scrape) rather than trusting the
quest-page fetch or corpus majority — a new, stronger technique introduced this batch.

**Project-wide DBC-confirmed sweeps** (same class as batch 6's Kalimdor fix — corpus majority
was the error in every case):
- `亡靈天災`→`天譴軍團` (the Scourge), **26 occurrences**. Not itself DBC-sourced, but the same
  entity already established via batch 3's wowhead-faction-page check (63 occurrences of
  `天災軍團`→`天譴軍團` at the time); `亡靈天災` was a second, previously-unswept spelling for
  the identical entity — verified every one of the ~20 affected quest rows individually against
  English `quest_template` text ("the Scourge") before sweeping, unlike batch 9's `透過` mistake,
  because this is a single fixed compound noun (no multi-sense ambiguity), not a general
  grammar pattern. Also caught and fixed one instance in already-verified batch 5 (quest 1648)
  that had been missed.
- `提瑞斯法`→`提里斯法` (Tirisfal Glades), **65 occurrences** — corpus majority was wrong;
  `AreaTable_zhTW.tsv` (area 85) confirms `提里斯法林地`.
- `洛丹倫`→`羅德隆` (Lordaeron), **33 occurrences** — corpus majority was wrong; confirmed via
  `BattlemasterList_zhTW.tsv`/`Map_zhTW.tsv`/`Achievement_Name_zhTW.tsv`/`AreaTable_zhTW.tsv`
  all agreeing on `羅德隆廢墟` (Ruins of Lordaeron).
- `阿爾薩斯`→`阿薩斯` (Arthas), **13 occurrences** — matches the existing corpus majority (35);
  confirmed via `Faction_zhTW.tsv` (`CoT 阿薩斯`, Caverns of Time faction).
- `碎木哨崗`→`碎木崗哨` (Splintertree Post, word-order fix), **39 occurrences project-wide** —
  confirmed via `AreaTable_zhTW.tsv` (area 431); scoped to a full corpus sweep since the DBC
  match is unambiguous, unlike batch 9's `裡`/`里` classifier situation.
- `扎拉贊恩`→`札拉贊恩` (Zalazane), **12 occurrences** — no locale table for the creature, but
  matches the existing corpus majority (11:1) and the `扎`→`札` direction already established in
  batch 6 (`扎瑪`→`札瑪`).

**No-locale-table disputes — settled by fetching the entity's own wowhead page directly**
(technique introduced this batch: `curl` the `npc=<id>`/`item=<id>` page, read the `<title>`
tag — faster and more authoritative than the pre-fetched quest-page jsonl for a single-entity
check):
- Tiza Battleforge (creature 6179) confirmed as `蒂薩·熱爐` via direct page fetch — fixed the
  one stray `蒂薩-熱爐` (hyphen) instance in quest 1778 to match the corpus's already-correct
  majority (8 occurrences).
- Muiredon Battleforge (creature 6178, Tiza's husband) — name spelling `穆裡頓`→`穆里頓` fixed
  (6×) per wowhead's quest-page rendering and the batch-9-established rule that personal names
  use `里`, not the locative `裡`; kept the existing `·` separator (a same-family hyphen claim
  did not hold up once Tiza's own page was checked directly — see note below).
- Item 7133 "Brutal Hauberk" (quest 1848's reward): direct item-page fetch confirmed
  `野蠻鍊衫`, overriding an initial (wrong) decision to keep DB's `野蠻鎖甲` on the reasoning
  that `鎖甲` was corpus's established 14:0 "Mail" armor-class term — that reasoning didn't
  hold once the item's own dedicated page was actually checked. **Lesson: an item's own
  wowhead page outranks corpus-wide class-name convention, even a 14:0 one** — don't stop at
  the heuristic when a direct, higher-tier check is available.
- Item 5770 "Robes of Arcana" (quest 1796): direct item-page fetch confirmed `神秘的長袍`,
  settling a three-way disagreement between DB (`奧法之袍`), wowhead's quest-page Objectives
  field (`秘法之袍`), and wowhead's quest-page Details field (`神秘的長袍`) — the item's own
  page matched the Details field, not the Objectives field, showing wowhead's own quest-page
  fetch was internally inconsistent too.
- Creature 6266 "Menara **Voidrender**" (quest 1796): DB's `梅納拉·沃倫德` doesn't match the
  English name at all (fabricated transliteration); fixed to `梅納拉·虛無撕裂者` (a literal
  match for "Voidrender", not a phonetic name — same class as batch 8's `迅捷的赫格拉姆`
  finding).
- Orm Stonehoof (creature 6410) → `歐姆·石蹄` (5×), Wynne Larson (creature 1309) →
  `威恩·拉爾森` (7×), High Sorcerer Andromath (creature 5694) → `高階巫士安多瑪斯` (5×), Ulag
  the Cleaver (creature 6390) → `『斬擊者』奧拉格` (3×) — all confirmed via the quest-page
  wowhead fetch per the user's explicit direction this batch ("if no ground truth in db, use
  wowhead.com/wotlk/tw as the source").
- Mage-tastic Gizmonitor (item 7226, quest 1880): `法師文件儲存器`→`法師文檔記憶體` (4×), same
  no-locale-table/defer-to-wowhead rule.

**Content fixes verified against the real English source**:
- Quest 1791 (Bath'rah the Windwatcher, `巨魔隱士`→`食人妖隱士`) and quest 1839 (Ula'elek,
  `巨魔鐵匠`→`食人妖鐵匠`) — both confirmed "troll" in English, matching the established
  Troll/Ogre convention. Quest 1791's title/body also updated to `『觀風者』` to match the
  quest-1712 (batch 9) naming decision for the same NPC — note wowhead's own quest-page fetch
  for 1791 still shows the old `捕風者` in the title (only the body was updated on wowhead's
  side), the same kind of internal wowhead inconsistency seen with Gakin in batch 9.
- Quest 1798 (`地精港口城市`→`哥布林港口城市`): English literally says "goblin port" (Ratchet)
  — also fixed a `我們我們的` and `住在在` doubled-character typo in the same row.
- Quest 1899 (`阿斯托的的賬本`→`安德隆的帳本`): English is literally "Andron's Ledger" — DB's
  `阿斯托` was a fabricated name; `安德隆` is also the correct name for the same NPC in the
  immediately-preceding quest 1898's own (already-correct) text, giving internal corroboration.
  Also fixed the doubled-`的` typo and `賬本`→`帳本` character variant in the same row.
- Quest 1920: Objectives dropped "your empty coffers" from "return to me with your filled
  coffers, your empty coffers and the cantation" — restored using wowhead's phrasing. The
  identical pre-fix sentence also appears in quest 1960 (outside this batch's range) — flagged,
  not touched, for whichever future batch reaches it.
- Quest 1844 (`雌奇美拉`→`奇美拉族母`): English literally says "chimaera matriarch"; `族母` is
  an established corpus term (9 other occurrences) for "Matriarch"-titled creatures.
- Quest 1878: DB's Objectives field is empty, matching English `quest_template`'s equally
  empty `LogDescription`/`QuestDescription` — wowhead's fetch pulled unrelated repeat-quest
  greeting text into the Objectives slot. Not a real gap; left as-is.

**False positives correctly rejected**: quest 1782 (`弗倫的鎧甲` — English title is literally
"Furen's Armor", DB's literal rendering is correct; wowhead's `弗倫的護甲` is a looser
paraphrase).

**`地獄獵犬`→`惡魔獵犬` naming, 11 occurrences total, full corpus sweep**: initially left
untouched on the reasoning that wowhead itself disagrees within the 1758/1795/1798/1801
questline (1795's own quest-page fetch uses `地獄獵犬`, matching DB, while the other three use
`惡魔獵犬`) — the user overrode this directly: `惡魔` (demon) is simply the more semantically
correct term than `地獄` (hell) for Burning Legion creatures, regardless of what wowhead's own
inconsistent fetches show. Fixed all 4 in-questline quests (8×). Also swept the 3 remaining
corpus occurrences (9345, 9379, 10910, all outside this batch's 1741–1940 range) at the user's
explicit follow-up request — worth noting these 3 aren't even the same creature as the
questline above: 9345 and 10910's English source says "**felhound**"/"deadly hounds" (a
different Legion creature from "Felhunter"), only 9379 literally says "the **Felhunter**". The
user's call was that `惡魔獵犬` fits both creatures better than `地獄獵犬` regardless, so all 3
were swept too — a rare case of a stylistic/semantic preference override applied across
creature-identity lines, not a ground-truth-hierarchy resolution.

### Batch 11 (1941–2140) fixes log

Lowest bug density yet (28/196 flagged) and no project-wide sweeps this batch — every fix was
scoped to its own quest. Notably quiet on the "corpus majority is wrong" front that dominated
batches 6/10; this range's issues were mostly one-off truncations, typos, and title/rank
disputes rather than systemic zhCN-leak vocabulary.

**Genuine truncation bugs restored** (verified against `quest_template`'s real English source):
- Quest 2038 (`賓格斯的補給品`): Objectives ended abruptly at a bare colon
  (`找回賓格斯的裝備:`), dropping the entire item list. English confirms 4 required items in
  order (`RequiredItemId1-4`: Wrench, Screwdriver, Hammer, Blastencapper) — restored using that
  canonical order rather than wowhead's scrambled item order, and used the row's own established
  `氣壓爆裂物` term for "Blastencapper" (matching the Details field) instead of wowhead's
  `氣壓炸彈` variant.
- Quest 2118 (`瘟疫蔓延`): Objectives was severely truncated and had a corrupted placeholder
  (`你帶回染病的薊熊了嗎，小心慢慢?` — "小心慢慢" is nonsense text, not a `$N`/`$n` token) that
  dropped the entire second half of the sentence (the "if your trap fails, get a new one"
  clause). Restored using wowhead's more complete text, replacing the corrupted placeholder
  with `$N` to match the row's own Details field convention.

**Content/title fixes verified against the real English source**:
- Quest 1943 (`巨魔法師迪諾`→`食人妖法師迪諾`): English literally "the troll mage Deino".
- Quest 1945: `樹妖`→`林精` (Dryad, no locale table, split 6:5 corpus-wide — deferred to
  wowhead per the user's standing rule) and `巨魔裁縫`→`食人妖裁縫` (confirmed "dryads" +
  contextual troll tailor, matching the Troll/Ogre convention).
- Quest 1949 (`隱藏的秘密`): `大法師提爾斯`→`魔導師提爾斯` — English title is literally "Magus
  Tirth", not "Archmage" (a different, higher rank); also `地精與地精的車賽`→
  `地精與哥布林的車賽` — DB had a duplicated-race typo, English confirms "the gnome and goblin
  races".
- Quest 1950 (`解封咒語`): Details said `魔法箱`/`箱子` three times while the row's own
  Objectives field already correctly said `保險箱` — unified to match, and English "magically
  locked strongbox" confirms `保險箱` (strongbox) over the generic `魔法箱` (magic box).
- Quest 1951 (`能量儀祭`→`能量儀式`, title + 2 body occurrences): English title is "**Rituals**
  of Power" — `儀式` (ritual/ceremony) is correct, `儀祭` isn't an established term.
- Quest 1941: Title `法紋長袍`→`法力之紋長袍` — confirmed via item 7509's own dedicated wowhead
  page (`<title>` tag fetch), matching "Manaweave Robe" more completely than DB's version
  which dropped the "mana" (法力) component.
- Quest 1978 (`賬本`→`帳本`) and quest 2098 (`基爾卡可`→`基爾卡克`, typo matching the NPC's own
  name spelled correctly elsewhere in the same row) — both simple typo/variant fixes.

**False positives correctly rejected** (wowhead's own fetch was wrong, or DB was already
right — including two direct re-confirmations of prior-batch findings):
- Quest 1999: DB's `祈倫托` confirmed correct again — wowhead's quest-page fetch showed the
  zhCN-leak `肯瑞托`, the exact error batch 3 already settled via the faction's own page
  (`faction=1090`). Same corpus, same wrong wowhead answer, different quest.
- Quest 1998: DB's `亡靈哨兵` (Deathstalkers, an established faction-title term used
  consistently since batch 10) confirmed correct — English literally says "the
  **Deathstalkers** in Silverpine"; wowhead's `不死生物哨兵` is a generic paraphrase that drops
  the proper title.
- Quest 2098's own `基爾卡可` typo (see above) turned out to also be present in wowhead's own
  fetch — wowhead scraped the same broken source data, another reminder that wowhead isn't an
  independent check when both sides ultimately derive from the same client strings.
- Quest 2019: wowhead's fetch returned page-navigation text ("巫妖王之怒 任務" / a page
  description sentence) instead of real quest content — a scrape failure, not a real diff;
  DB's text was left untouched.
- Quest 1942 (`星結之衣` vs wowhead's `星界之衣`) and quest 1944 (`克薩維亞之水` vs wowhead's
  `薩維亞之水`, missing a character) — DB's version more completely captures the English title
  ("Astral **Knot** Garment") or is simply more complete; no item/locale table to fully settle
  either, left as-is.
- Quest 1958 (`蒼穹之力` vs wowhead's `天國之力` for "Celestial Power") and quest 1963/2040
  (`背袋`/`背包`, `穴居怪`/`穴居人` — synonym-level disagreements with no clear winner) — left
  untouched, genuinely ambiguous with no locale table and no reward/required item to check
  against.

### Batch 12 (2141–2340) fixes log

Lowest bug density yet again (23/200 flagged) and no project-wide sweeps — a tight cluster of
jewelry-repair/Uldaman-themed quests (2198-2340, the "Shattered Necklace" chain) accounted for
most of the real findings, plus a separate SI:7/rogue-trainer cluster.

**Content fix — real mistranslation, not just paraphrase**: quest 2202 (`奧達曼的蘑菇`)
mistranslated English "restorative elixirs" as `好酒` (fine wine) — a substance-changing error,
not just word choice. Also restored missing narrative detail (mushroom cluster
location/description) that DB had compressed away. Replaced the whole Details field with a
corrected, more complete version rather than patching just the wine/elixir word, per the
verbatim-not-patch rule.

**Title/rank fixes verified against the real English source**:
- Quest 2203: title `荒蕪之地的材料 II`→`荒蕪之地的試劑 II` — English title is literally
  "Badlands **Reagent** Run II" (試劑), not the generic "材料" (material).
- Quest 2205: title `軍情七處`→`尋找軍情七處` — English title is "**Seek out** SI: 7"; DB
  dropped the verb. (Quest 2300's identical-looking `軍情七處` title was correctly left
  untouched — its own English title is literally just "SI:7", no "seek out".)
- Quests 2298/2300: Renzik "The Shiv" — DB called him `"剃刀"雷吉克` ("razor," a shaving tool);
  confirmed via a direct `curl` fetch of the NPC's own wowhead page (creature 6946) that the
  correct rendering is `『剃刃』雷吉克` (with the established 『』 bracket convention, not `""`
  quotes) — "Shiv" is a crude blade/knife, not a shaving razor.

**False positive correctly rejected — wowhead fabricated a name**: quest 2198's necklace
inscription. DB says the engraving reads literal Latin letters `"TdK"`, matching English
verbatim ("three tiny, engraved letters: \"TdK\""); wowhead's fetch substituted a fabricated
Chinese name (`「基瑟爾」`, "Kessel") that doesn't correspond to anything in the English source
— a scrape/rendering error, not a translation choice. Left DB unchanged.

**Left as-is, no strong evidence either direction**: `石顎怪`/`石齶怪` (quests 2201/2339, the
same jaw-character ambiguity already flagged as a known issue for quest 170 — corpus split
7:4, no locale table); quest 2258's Objectives being a generic summary while its own Details
field already has the full itemized reagent list (a legitimate summary/detail split pattern
used elsewhere in the corpus, not a content gap).

### Batch 13 (2341–2540) fixes log

Lowest bug density yet again (20/200 flagged), no project-wide sweeps. Two clusters dominated:
an Uldaman/Southshore jewelry-repair chain continuing from batch 12, and a Wetlands rogue-trainer
chain ("Deep Cover"/"The Shattered Salute") that turned out to hold up well under scrutiny.

**Content-swap bug** (verified against `quest_template`'s real English source): quest 2499
(`奧肯斯古爾`) — DB's Details field opened with "我搞明白了！我不得不衝來這裡找你！...腐化是
經由樹精傳染的，但源頭卻只有一個" (a different narrative beat entirely — reads like a *later*
step's dialogue), while the actual English QuestDescription matches wowhead's fetch almost
word-for-word ("In a cave along the southern bank of the lake, a timberling named Oakenscowl is
spreading corruption..."). Replaced the whole field with the verified text.

**Truncated Objectives restored** (verified against English `LogDescription`):
- Quest 2438 (`翡翠攝夢符`): `取得翡翠攝夢符。`→`將翡翠攝夢符交給多蘭納爾的塔隆凱·捷根。` —
  matches the row's own already-correct EndText, which had the turn-in NPC all along.
- Quest 2518 (`月神的淚水`): same truncation pattern, restored the turn-in clause. Also fixed a
  genuine **location error** in the Details field: DB said Sathrah dwells "這裡東北邊的河流附近"
  (near the river northeast of here), but English says "along the northern borders of
  Teldrassil, near Wellspring Lake" — a different location entirely, not just a paraphrase gap.

**Title fixes verified against the real English source**:
- Quest 2341: dropped the fabricated `(地下城)` ["(Dungeon)"] suffix — no such tag exists in
  the English title ("Necklace Recovery, Take 3") or on wowhead.
- Quest 2342: `尋找寶物`→`尋回寶物` — English title "**Reclaimed** Treasures" is past-tense
  recovery, not an active search.
- Quest 2501: `荒蕪之地的材料 II`→`荒蕪之地的試劑 II` — same fix as batch 12's quest 2203
  ("Badlands **Reagent** Run II"), a second instance of the identical title pattern in a
  different (likely Horde-mirror) version of the same questline.

**No-locale-table disputes settled via direct NPC-page `curl` fetch**:
- Bena Winterhoof (creature 3009, quest 2440): confirmed `貝娜·冬蹄` — neither DB's `本娜·冰蹄`
  nor wowhead's own quest-page fetch (which also said `冰蹄`) had the right surname; "Winterhoof"
  literally means `冬`(winter)+`蹄`(hoof), not `冰`(ice). Also fixed her title
  `鍊金師`→`鍊金術訓練師`, matching the creature's own English subname "Alchemy Trainer".
- Taskmaster Fizzule (creature 7233, quests 2458/2460): confirmed `工頭` is correct — wowhead's
  own dedicated NPC page agrees with DB, while wowhead's *quest-page* fetch showed the wrong
  `監工`. Also confirms `碎手氏族`/`碎手軍禮` (DB, 45:7 corpus majority) as likely correct and
  distinct from the unrelated Outland orc clan of the same English name ("Shattered Hand") —
  the quest's own required NPC is a level-30 Wetlands creature, nothing to do with the
  level-69+ Hellfire Peninsula orcs also named "Shattered Hand" in `creature_template`. Left
  unchanged.
- Quest 2418: name spelling `裡格弗茲`→`里格弗茲` (Riggerfuzz, personal name using `裡` instead
  of the correct `里` per the batch-9-established rule) — found and fixed all 6 corpus-wide
  occurrences including 2 in already-completed batch 4/5 range, since this is an unambiguous
  single-entity fix, not a risky pattern sweep.

**False positives correctly rejected** (wowhead was wrong, or its own fetch failed):
- Quest 2358: wowhead's fetch returned raw unrendered English/markup (`[Horns of Nez\'ra]`,
  `[Many years ago...]`) instead of Chinese text — a scrape failure, not a real diff. DB's
  coherent Chinese text was left untouched.
- Quest 2459: DB's `他` (he) for the Gnarlpine mystic leader and `墮落的瘤背秘法師` (keeping
  the tribe qualifier) both confirmed correct against English ("their leader... He would
  never realize...", "Gnarlpine mystics"); wowhead's `它` (it) and dropped `瘤背` qualifier
  were the errors.

### Batch 14 (2541–2740) fixes log

Lowest bug density yet (18/200 flagged), no project-wide sweeps. Also the first batch with a
large false-positive cluster from the numeric-count audit — 10 quests flagged, all resolved as
the documented "spelled-out number" class (English "three Snickerfang Jowls, two Blasted Boar
Lungs, and one Scorpok Pincer" vs the audit script's digit-only regex).

**Content fixes verified against the real English source**:
- Quest 2561 (`利爪德魯伊`): Details said "you must approach the door of a nearby room"
  (`附近房室的門`), but English says "explore the deepest areas of the Ban'ethil Barrow Den" —
  a genuine location error, not paraphrase. Restored to match.
- Quest 2622 (`丟失的命令`): Details revealed the survivor's name (`本戈爾`) immediately,
  contradicting English's suspenseful structure ("Only one survived... speak with Bengor").
  Also the closing warning ("這裡到處都是危險的生物，你一定要小心一點" — generic "there are
  dangerous creatures here") didn't match English's actual idiom ("be mindful of what you
  stick your nose into — it may get bitten off"). Restored both the narrative order and the
  correct warning.
- Quest 2702 (`古代英雄`): DB's Objectives named the NPC `桑德·裂蹄` ("Sander Splithoof") — a
  fabricated name. `creature_template`'s literal English name is "**Corporal Thund** Splithoof"
  — neither the first name nor the rank matched; fixed to `裂蹄下士` (matching wowhead, which
  had the rank right even though it dropped the given name).
- Quest 2721 (`基利斯`): Objectives said `找到基利斯的下落` (dropped the rank), while the row's
  own Details already correctly said `基利斯中尉` — same-row inconsistency, confirmed via
  English "Lieutenant Kirith"; unified to include the rank in Objectives too.
- Quest 2609 (`贊吉爾之觸`): DB hardcoded the closing line to `年輕的小姐` (young miss),
  silently dropping the male branch of English's `young $g fella:lady;` gender token. Restored
  to the project's established raw-token format (`$g先生:小姐`, matching the existing
  precedent in quest 2205 — not wowhead's resolved `<先生/小姐>` bracket display style, which
  is just wowhead's own rendering convention, not this project's storage format).

**Title fixes verified against the real English source**:
- Quest 2584: `野豬之魂`→`野豬之靈` — English title "**Spirit** of the Boar"; no locale table
  or corpus precedent, deferred to wowhead per the standing rule for no-ground-truth cases.
- Quest 2605: `口渴的地精`→`口渴的哥布林` — English title is literally "The Thirsty **Goblin**".

**False positives correctly rejected**:
- Quest 2621: DB's `分隊指揮官魯爾格` (Dispatch Commander) confirmed correct against English
  "Speak to **Dispatch Commander** Ruag" — wowhead's `指揮官` drops "Dispatch". Name spelling
  (`魯爾格` vs wowhead's `盧爾格`) left unresolved, no locale table either way.
- Quest 2701: DB's `遺物` (relic) confirmed correct against English "a **relic** of old";
  wowhead's `聖物` (holy/sacred item) overstates the religious connotation not present in the
  source.
- `禿鷲`/`禿鷹` (vulture, quests 2585/2586/2601-2604): left as `禿鷲` — the zoologically
  correct term for "vulture" (鷲=vulture/condor family vs 鷹=hawk/eagle family), matching the
  existing corpus majority (42:11); wowhead's `禿鷹` is the imprecise colloquial substitute.

### Batch 15 (2741–2940) fixes log

Highest bug density since batch 3 (76/199 flagged, 104 real rows reviewed) — a dense run of
crafting-trainer questlines (blacksmithing, leatherworking) and several Zul'Farrak/Sandfury
troll quests. Also the first batch with a large false-positive cluster from the numeric-count
audit for a *second* reason beyond spelled-out numbers: DB rendering small counts as Chinese
numerals (`十`) instead of Arabic digits when English used a digit — both are legitimate
stylistic choices in this corpus, not errors.

**Project-wide sweeps**:
- `質量`→`品質` for "Quality" (8 occurrences, quests 1954/2821/2822 — 1954 in an
  already-verified batch, included since this is a single confirmed compound term, not a
  general pattern needing per-instance risk assessment). `質量` in Taiwan Mandarin means
  "mass" (physics); `品質` is the correct term for product/material quality. Confirmed by
  reading all ~15 corpus-wide contexts individually before scoping — one ambiguous instance
  outside this batch's range ("這種油質量很重", quest 10201) was deliberately left untouched
  since it could plausibly mean either sense without more context.
- `大工匠梅卡托克`→`高等技工梅卡托克` (High Tinker Mekkatorque), 10 occurrences project-wide.
  Corpus was 10:0 self-consistent for the wrong title; confirmed via direct `curl` fetch of
  the NPC's own dedicated wowhead page (creature 7937) — same "corpus majority was wrong"
  pattern as batch 10's Kalimdor and batch 13's Bena Winterhoof.

**Corrupted/duplicated text restored** (a distinct bug class from truncation — these rows had
inserted duplicate phrases, not missing content): quests 2771/2772/2773 (the "A Good Head On
Your Shoulders"/"The World At Your Feet"/"The Mithril Kid" chain) — Objectives read like
`1副精製秘銀護肩帶秘銀護肩交給...` (a duplicated `秘銀護肩` fragment) and similar garbling in
the other two. Rebuilt each Objectives field from the verified English source
(`quest_template`'s `RequiredItemId1-2`), which also surfaced a related term error: `精製`
(DB, "refined") should be `華麗` (Ornate) — English titles are literally "**Ornate** Mithril
Shoulder/Pants/Gloves" — extended the same fix to the parallel Galvan questline (2758-2764,
7 quests) since it's the identical Mithril/Ornate item-naming pattern. Also fixed a stray
`密銀`→`秘銀` typo (Mithril) picked up along the way.

**Fabricated names / MT artifacts**:
- Quest 2845 (`迷路的沙恩`): NPC name `羅克位元` — DB had transliterated "**Rockbit**"'s
  second syllable as the Chinese computing term `位元` (a "bit," as in binary digit) instead
  of continuing the phonetic transliteration. English confirms "Rockbiter's camp"; fixed to
  `羅克比特`.
- Quest 2875 (`通緝：安德雷·費爾比德`→`通緝：安德雷·火鬍`): English title is literally
  "WANTED: Andre **Firebeard**" — a translatable English compound name, not a name meant to
  be transliterated phonetically. Also dropped a fabricated first name `吉羅姆` (Jerome) for
  Security Chief Bilgewhizzle — English confirms no first name ("Security Chief Bilgewhizzle"),
  consistent with this NPC's established no-first-name convention from earlier batches.

**Race-term fixes** (Troll/Ogre convention, `[[feedback-zhtw-troll-ogre-terms]]`): quests
2768/2865/2880/2881/2934/2935/2936 all had `巨魔` where English confirms "troll" (Zul'Farrak
Sandfury trolls, Witherbark trolls) — fixed to `食人妖` throughout. Quest 2843/2843:
`地精傳送器`→`哥布林傳送器` — English literally "Goblin Transponder", a Gnome/Goblin race
mix-up like several seen in earlier batches.

**Item-name fixes verified against English titles/required items**:
- Quest 2846: `深淵皇冠`→`深淵冠冕` — English title "**Tiara** of the Deep"; `冠冕` (tiara/small
  crown) matches better than `皇冠` (royal/king's crown).
- Quests 2850/2851/2857/2858: `夜色`→`夜景` for "Nightscape" gear (items 8175/8176 confirmed
  via `item_template`) — `夜景` (night scenery, matching "-scape" as in landscape) is more
  literal than `夜色` (night's color/hue). Scoped the sed replacement to the specific compound
  words (`夜色外套`, `夜色頭巾`, etc.) to avoid touching the unrelated `夜色鎮` (Duskwood zone
  name) — confirmed 95 untouched `夜色鎮` references survived the sweep intact.

**Post-batch corrections (from user)**:
- `惡魔獵手`→`惡魔獵人` (Demon Hunter, 22 occurrences project-wide) — initially left as-is on
  22:0 corpus dominance, but the user pointed to the actual player-class page
  (`wowhead.com/tw/class=12`, confirmed via `curl` title-tag fetch: `惡魔獵人—職業`) as the
  authoritative source. Even though Demon Hunter isn't a playable class in this WotLK-era
  content, "Demon Hunter" the English proper noun is the same concept Blizzard later named
  as a class, and the class's official zhTW name outranks a same-corpus 22:0 majority — same
  lesson as batch 9/10/13/15's other "corpus majority was wrong" findings, this time from a
  source category (class pages) not previously used in this pass.
- **Generic "trogg" — as of batch 15, ended at `穴居怪` project-wide (all 54 occurrences, zero
  `穴居人` remaining anywhere in the file). This was reverted a 4th time in batch 16's
  follow-up (back to `穴居人`) — see that batch's log for the current, current-as-of-this-
  writing answer; don't treat this batch-15 entry as still current.** Saga at this point:
  swept to `穴居怪` for consistency → reverted to `穴居人` after wowhead NPC pages showed
  Blizzard's own localization is itself inconsistent between bare-family and
  individually-named variants → settled (at the time) on `穴居怪` per the user's lore-based
  call that no trogg in WotLK is friendly. Full up-to-date saga (all 4 reversals) is in
  `[[feedback-zhtw-ground-truth-priority]]`. (Quest 10999, one of the rows in this sweep,
  separately still contains unrelated raw unconverted simplified Chinese — already tracked
  below.)
- `遺物` (Mysterious Relic, item 9248, quests 2870/2871) confirmed correct again — same
  "relic not holy item" finding as batch 13's quest 2701, now a second independent
  confirmation that wowhead systematically over-translates this item type as `聖物`.
- Quests 2741/2749/2878: DB's empty Objectives fields all matched equally-empty English
  `LogDescription`/`QuestDescription` — wowhead's fetch pulled unrelated text into these
  fields each time (same pattern as batches 10/11's quests 1878/2523).
- Generic Gnomeregan "troggs" (quests 2904/2926/2927/2929) were already `穴居怪` at the time
  and needed no change once batch 15's trogg decision landed there — swept to `穴居人` along
  with everything else in batch 16's follow-up reversal (see below).
- `『長者』加爾文` (Elder Galvan) — considered but **not** applied: creature_template's
  literal English name is "Galvan **the Ancient**," which wowhead's `長者` (Elder) doesn't
  precisely match either. Left DB's title-less `加爾文` as-is rather than adopting a
  half-correct alternative; flagged as unresolved rather than silently "fixed."

### Batch 16 (2941–3140) fixes log

High bug density (81 flagged by the strict diff, 111 real rows in range — the range also has
an unusually large gap of 89 non-existent quest IDs, mostly a contiguous block 3003–3081).

**Content-swap bug**: quest 2949 (`戒指歸來`, "Return of the Ring" — paired with quest 2947,
same title/mechanic but different faction) had its entire Details field wrongly duplicated
from quest 2947: DB's 2949 said the ring bore an **Ironforge** seal and "**TdK**" engraving —
identical, word-for-word, to 2947's text. English confirms 2949 should be the **Orgrimmar**
variant with an "**NOG**..." engraving; wowhead's own fetch for 2949 already had the correct
distinct text, used verbatim to replace DB's copy-pasted Details field.

**Wowhead-fetch error (false positive, no DB change)**: quest 3121 ("A Strange Request") —
wowhead's fetched Details named a completely different NPC/location (`尼爾魯·火刃`/`奧格瑪`)
than DB's (`夏拉什·火刃`/`莫沙徹營地`/`拉瑞斯小亭`). Checked English `quest_template` source
directly: it explicitly says "**Xerash Fireblade**, located at the **Lariss Pavilion, north of
Camp Mojache**" — matches DB exactly, contradicts wowhead. Concluded wowhead scraped/matched
the wrong quest for this ID; DB was already correct. Same false-positive class as batches
11/13/15's other wowhead-fetch errors.

**Race-term fixes** (`[[feedback-zhtw-troll-ogre-terms]]`):
- Gordunni Ogre exception (`巨魔`, not the default `食人魔`) extended to quests
  2975/2980/2981 (title `菲拉斯的食人魔`→`菲拉斯的巨魔` in 2975/2980, plus all body-text
  Gordunni references) — same confirmed clan exception from batch 4.
- Troll-is-always-`食人妖` rule applied to: Vilebranch trolls (quests 2989/2993/2994, incl.
  the generic "troll city" descriptor for Zul'Aman), Sandfury trolls (quest 3042, title
  `巨魔調和劑`→`食人妖調和劑`), and Nekrum Gutchewer's own tribe in Zul'Farrak (quest 2991).

**Count fix**: quest 3127 (`山嶺巨人靈魂精華`) — DB said kill "十二個" (12) mountain giants;
English `quest_template` and wowhead both confirm 7 (`RequiredNpcOrGoCount` field + repeated
in both Details and Objectives prose). Fixed to `7個`.

**NPC-name fixes** (via `creature_template_locale`):
- Krueg **Skullsplitter** (id 4544, quests 2973/2974): DB had `碎顱` ("shatter-skull");
  canonical table confirms `劈顱` ("split-skull," matching wowhead too).
- Oran **Snakewrithe** (id 7825, quest 2995): DB had transliterated `斯內克威瑟`; canonical
  table confirms the semantic translation `蛇繞` ("snake-coil"), matching wowhead.

**Title mistranslations**:
- Quest 2969: `精靈龍的自由` ("Freedom of the Sprite Dragons") → `所有生物的自由` — English
  title is literally "Freedom for **All Creatures**".
- Quest 2995: `聯絡中心`→`溝通管道` for the title and the closing "destroy their lines of
  communication" sentence only. Wowhead's own Details field *agrees* with DB's `聯絡中心` for
  the opening sentence ("Quel'Danil Lodge is a center of communication") — left that one
  occurrence alone rather than blanket-replacing every instance of the term in the row.

**Item-name fixes**:
- Quest 2972: "signet ring" rendered generically as `徽記之戒`/`戒指` — fixed to `璽戒`
  (matches wowhead, and `璽` specifically means an official/personal seal, matching "signet").
- Quest 2991: `徽章` (badge) → `勳章` (medallion) — same Badge/Medal distinction established
  in batch 13.

**Internal-consistency fix**: quests 2973/2974 (the Krueg Skullsplitter chain) had their
Objectives and EndText fields disagreeing on location — 2974's Objectives said `千針石林`
(Thousand Needles) while both quests' EndText said `莫沙徹營地`/Feralas. English `quest_template`
EndText confirms "Return to Krueg Skullsplitter at **Wildwind Lake in Feralas**" for both
quests — harmonized both to the Feralas/Camp Mojache wording already used in each quest's own
EndText (note: wowhead's own Details field for 2973 was independently confirmed garbled/wrong
here too — it invented an unrelated "Thousand Needles vs Feralas" tangent not present in
English at all, so its Objectives value for the same quest was not trusted either). Also fixed
a `莫沙沏`→`莫沙徹` typo (Camp Mojache) picked up along the way.

**Post-batch 16 correction (from user) — generic "trogg" reverted a 4th time, back to
`穴居人` (all 54 occurrences project-wide), overturning batch 15's "final" answer.** The user
found fresh evidence that official zhTW translations are inconsistent here too, and asked for
a genuine re-evaluation rather than a re-litigation. Checking the DB's own already-settled
convention for comparable primitive/hostile humanoid races overturned batch 15's lore
argument: Gnoll (`豺狼人`), Kobold (`狗頭人`), Quilboar (`野豬人`), Murloc (`魚人`), and Harpy
(`鷹身人`) are all uniformly hostile in WotLK — exactly like troggs — yet all get `人`, not
`怪`; hostility doesn't predict the split at all. The one race that does get `怪` — Furbolg
(`熊怪`) — is beast-*derived* (transformed bears), not humanoid-in-origin. Troggs are
Titan-forged failed proto-Dwarves — a botched *humanoid* race, same category as
Gnoll/Kobold/Quilboar — so `穴居人` fits the established pattern better. Full saga (now 4
reversals) documented in `[[feedback-zhtw-ground-truth-priority]]`. **`穴居人` is the current
answer — but given this term has flipped four times, don't treat any future answer as
permanently settled either; if fresh evidence surfaces, re-check the comparable-race pattern
again rather than re-asserting either prior conclusion.**

### Batch 17 (3141–3340) fixes log

The sparsest range yet: only 10 of 199 candidate IDs are real quests (matches `quest_template`'s
English base exactly, so this is a genuine gap in the ID space, same pattern as batch 16's
3003–3081 gap — not a scan error).

**Tooling note**: `diff_quest_text.py` has no numeric range arguments — despite the `[lo] [hi]`
in the "Next batch" instructions below, it always diffs the *entire* cached
`quest_text_extracted.jsonl` (every ID ever fetched across all batches), not just the current
batch. Had to filter its output to this batch's ID range in Python before reviewing. One
side-effect worth flagging: the unfiltered run re-surfaced quest 2947 (already verified correct
in batch 16) with a wowhead Details field naming a completely different engraving word
(`基瑟爾` instead of "TdK") — this is stale re-fetched noise from an old mis-scrape, not a new
finding, and was ignored per batch 16's already-confirmed English-source verification.

**Race-term fix**: quest 3161 (`加茲瑞迪安`/Gahz'ridian) — Details said `巨魔` for the tribe that
worshipped Gahz'rilla; English confirms "trolls used to occupy this land" — fixed to `食人妖`
per the settled Troll-is-always-`食人妖` rule.

**Title/content fixes** (Curator Thorius questline, quests 3182/3201):
- Quest 3182: title `證明信` ("proof letter") → `證明文件` — English title is "Proof of
  **Deed**," a legal/certificate document, not a letter. Details also opened with a vague
  paraphrase ("how could a real horn look like this?") where English makes a specific claim
  ("The real horn would have had my broken axe head still lodged into its surface") — rewrote
  to match.
- Quest 3201: title `館長的證明！` ("The Curator's Proof!") → `終於！` — English title is
  literally "At Last!"; DB's title was fabricated, unrelated to the source. Also `你的“意外的
  成功”` ("your 'successful accident'") → `你的「意外」` — English says only "the 'incident'",
  no "successful" qualifier. Also a bracketed stage-direction named the wrong action entirely:
  `<索里奧斯館長從一大堆檔案中翻找東西。>` ("Curator Thorius rummages through a pile of
  files") → `<索里奧斯館長開始填寫一張很大的文件。>` ("Curator Thorius begins to fill out a
  large document"), matching English exactly. Also updated quest 3182's own quest-giver
  Objectives cross-reference (`索里奧斯的證明信`→`索里奧斯的證明文件`) to stay consistent with
  its renamed title.

**Corpus-wide patterns checked but not swept** (per `[[feedback-zhtw-no-blind-sweep]]` — a
skewed corpus split alone doesn't justify a sweep without checking the flagged instance's own
context): quest 3301 flagged both `透過`/`通過` (128:66 split project-wide) and `亡靈`/`不死族`
(231:11 split) against wowhead. Checked English: "Mura ... hope was to bring it new life
**through** her own effort" — this is the "by means of" sense of `透過`, which is standard
correct zhTW (distinct from the previously-confirmed "pass a trial" sense where `通過` is
correct and `透過` is a zhCN looseness, `[[feedback-zhtw-ground-truth-priority]]`). Left
untouched. `亡靈`'s 231:11 corpus dominance for generic "undead" (not the Forsaken faction) was
also left as-is — no contradicting locale-table or DBC evidence found.

### Batch 18 (3341–3540) fixes log

71 real rows in range (113 IDs not in DB); 54 flagged by the strict diff. Moderate-to-high bug
density, and this batch's `creature_template_locale` checks resolved an unusually high number
of proper-noun disputes cleanly (7 separate NPCs/terms), several of them overturning DB's
existing text rather than confirming it.

**Severe content bug**: quest 3361 (`逃難者的困境`, "A Refugee's Quandary") — DB's entire
Details field told a fabricated story (heading to Gnomeregan to meet Gnome brethren, an
unexplained earthquake, Ogres stealing belongings) that doesn't match the real English source
at all: "We drove the **troggs** out of Gnomeregan... our home is completely irradiated... we
gnomes have been scattered... It was the **trolls** that got [my things]." Rewrote the entire
Details field from the English source (using this session's settled `穴居人`/trogg and
`食人妖`/troll terms). Also fixed the Objectives field, which was missing the delivery
destination entirely ("Bring Felix's Box... to **Felix** in **Anvilmar**" — DB only said "find
Felix's box..." with no delivery instruction).

**NPC-name/title fixes** (via `creature_template_locale`):
- Amnennar the Coldbringer (quest 3341): DB's `寒冰之王` ("King of Cold") doesn't match either
  the English epithet or the locale table's `『寒冰使者』` ("Coldbringer," literal) — fixed.
- Lord Arkkoroc (quests 3509/3510/3511): DB dropped the `領主`/"Lord" title throughout; the
  locale table (creature 6134) confirms "Lord" is part of his name. Also fixed `惡魔之王`→
  `惡魔領主` for "demon lord" in the same quest, matching the same `Lord`→`領主` correction.
- Magatha **Grimtotem** (quest 3518): DB had a fabricated `瑪加薩·野性圖騰` ("Wildtotem") —
  the locale table (creature 4046) confirms `瑪加薩·恐怖圖騰`, and "Magatha Grimtotem" is
  also a load-bearing piece of static WoW lore (Grimtotem matriarch), not an ambiguous case.
- Kalaran Windblade (quests 3442/3443): a `溫佈雷`→`溫布雷` typo (the locale table entry for
  this creature ID has an unrelated first name, likely a mismatched/bad entry, but both DB's
  own pre-existing text and wowhead's independent quest-page fetch agree on `卡拉然` for the
  first name — trusted that agreement over the suspect locale-table entry, and only took the
  surname spelling `溫布雷` from the locale table since wowhead's quest fetch agreed with it too).
- Rynthariel's race (quest 3514): English confirms "that scheming **dryad** Rynthariel" — the
  locale table shows this corpus's Dryad race term is consistently `林精` (checked 3 separate
  Dryad-named creatures), not DB's `樹妖`. Fixed.
- Golem terminology (quest 3442, "Golem Oil"/golems): the locale table consistently renders
  named Golem creatures as `魔像`, not `傀儡` — fixed this quest's occurrences. (Corpus-wide,
  `傀儡`/`魔像` is split 58:47 — left everything outside this batch's scope untouched per
  `[[feedback-zhtw-no-blind-sweep]]`; this needs its own dedicated pass later.)

**Race-term fixes** (Troll-is-always-`食人妖`, `[[feedback-zhtw-troll-ogre-terms]]`): quests
3373 (Eranikus questline — English: "ensure that the **trolls** never again bring forth their
abomination of a god"), 3527 (Zul'Farrak — English: "the **troll** city of Zul'Farrak" and "the
long-dead **troll** Theka the Martyr"). Also a Gnome/Goblin mix-up: Marvon Rivetseeker is
explicitly "a **goblin** named Marvon Rivetseeker" in English, but DB called him `地精` (Gnome)
in both quests referencing him (3380, 3445) — fixed to `哥布林` in both, alongside the same
quests' troll-ruins fix (`巨魔遺蹟`/`巨魔遺址`→`食人妖遺蹟`/`食人妖遺址`).

**Missing/dropped content restored**:
- Quest 3520 (`尖嘯者的靈魂`): English specifies a "**bramble** wand," not a generic wand — DB
  said plain `魔杖` throughout; fixed to `刺藤魔杖`.
- Quest 3521 (`埃沃隆的解藥`): DB's Details dropped an entire alternate-ingredient-source detail
  present in English ("you may collect [Hyacinth mushrooms] from the **grell** south of here").
  Restored it using this corpus's established Grell term (`劣魔`, confirmed via
  `creature_template_locale` id 1988).

**Transliteration**: "Suntara" (an altar name, quests 3367/3368/3372) has no locale-table
entry, but `桑塔拉` is phonetically closer to "SUN-tara" than DB's `蘇塔拉` (which drops the
"-n" sound entirely) — swept to `桑塔拉` across all 3 quests plus the related quest 3373.

**Wowhead-fetch-error false positives (DB was already correct, no change)**:
- Quest 3376: DB's `勇者風羽` ("Brave Windfeather") matches English "**Brave** Windfeather"
  exactly; wowhead's fetch fabricated a first name and the wrong rank (`衛兵維薩羅·風羽`,
  "Guard Vasarr Windfeather" — no such name in English).
- Quest 3523: DB's `誓言石` matches English "the **Oathstone** he gave you back to him" —
  wowhead's `黑曜石` ("Obsidian") is simply wrong. (Quest 3374, earlier in this same batch,
  has the identical `誓言石`/`黑曜石` disagreement in an unrelated questline — left untouched
  on the strength of this same confirmed pattern, though not independently re-verified.)
- Quest 3525: DB's `神像` matches English "Extinguishing the **Idol**" — wowhead's generic
  `塑像` ("statue") loses the religious/idol connotation that's actually in the English title.
- Quest 3512 (Umbranse the Spiritspeaker): the locale table confirms DB's `阿姆布蘭希` is
  correct; wowhead's `昂布蘭希` is a different, wrong spelling.
- Quest 3520 (Yeh'kinya): the locale table confirms DB's `葉基亞` is correct; wowhead's
  `葉金亞` is wrong.

### Batch 19 (3541–3740) fixes log

43 real rows in range (153 IDs not in DB — this range is even sparser than batch 18); 29
flagged. A large chunk of the flagged quests (3629–3643) are a single near-identical
Gnome-vs-Goblin Engineering trainer-questline template repeated across ~8 quest rows with only
the trainer's name/location swapped — most of those diffs were confirmed as style-only ($N/$n
case, `：`/`:`, `技師`/`工程師` — the latter a genuine corpus-wide term-choice difference, not
an error, left alone).

**Trainer-identity swap bug**: quest 3638 (`保密的誓言`) — this quest's own content is
unambiguously about **Goblin** engineering (Details opens "Goblin engineering is about
practical uses for high profit...", trainer is Nixx Sprocketspring, matching the Goblin-path
trainer used in sibling quests 3633/3639), but DB's Objectives said "如果你同意成為一名**地精**
技師" (become a **Gnome** technician) — the wrong race entirely for this specific quest. Fixed
to `哥布林技師`.

**NPC-title fix**: Tinkmaster Overspark (quests 3630/3632/3634/3640/3641, plus quest 2922
outside this batch's range) — `creature_template_locale` (id 7944) confirms his zhTW title is
`技工大師`, not DB's `工匠大師`. Applied project-wide since it's a single confirmed proper noun,
not a pattern needing per-instance risk assessment.

**Other confirmed fixes**:
- Quest 3602 (`艾薩拉水晶`): English confirms "**Felhound**" — DB had `地獄犬` ("Hellhound"),
  which doesn't match "Fel" at all. Fixed to `惡魔犬`, consistent with the batch-10 established
  user preference (`惡魔` fits Fel/demon creatures better than `地獄`/"Hell").
- Quest 3627 (`破碎護符的聯合`): English confirms "**Lady** Sevine" — DB's Objectives listed
  her without the title (Grol "the Destroyer" and Archmage Allistarj were already correctly
  titled). Fixed, and added matching `『』` quote-mark styling around "毀滅者" to match this
  corpus's established epithet-quoting convention.
- Quest 3561 (`送貨給大法師克希雷姆`): English says the tower is "overlooking Azshara," not
  merely "on a hilltop in Azshara" (DB's original phrasing) — fixed to match the nuance.
- Quest 3542 (`安德隆·甘特的石版`): English confirms "**arcane** spells," not generic magic —
  fixed `魔法`→`秘法`. (The race term in the same sentence, `上層精靈`/Highborne, was already
  correct on DB's side — see false positives below.)

**Mosh'Ogg ogre mound naming — settled via DBC, 3 occurrences fixed project-wide** (quests
591, 2760, 3621): `莫什奧格食人魔山` → `莫什奧格巨魔山`. This went through two prior framings
before landing here — worth recording since it shows even the troll/ogre `[[feedback-zhtw-troll-ogre-terms]]`
hierarchy has a tier above corpus/wowhead disagreement: (1) initially flagged as a wowhead
scrape error (`巨魔山` looked like a Troll/Ogre race mix-up); (2) the user corrected this —
`巨魔` is a legitimate zhTW Ogre term too (Gordunni precedent), so both `食人魔山`/`巨魔山`
seemed equally valid and DB was left untouched; (3) the user then asked to check for an
*official* in-game zone name, which surfaced `AreaTable_zhTW.tsv` AreaID 105 = `莫什奧格巨魔山`
— DBC ground truth, tier #1, outranks the "both valid" framing entirely. Fixed to match,
including 2 occurrences outside this batch's own range (591, 2760) since it's a single
confirmed proper noun. **Takeaway: "both terms are contextually valid in general" doesn't mean
a *specific* place/entity's name is ambiguous — always check whether a dedicated DBC entry
exists for the specific proper noun before settling for "either is fine."**

**False positive confirmed (DB was already correct, no change)**:
- Quest 3542: DB's `上層精靈` correctly matches "Highborne" (a distinct Night Elf social class
  from antiquity); wowhead's `高等精靈` conflates it with the separate "High Elf" race — same
  distinction already established in `[[feedback-zhtw-ground-truth-priority]]`'s Highborne/Demon
  Hunter class-page precedent.

### Batch 20 (3741–3940) fixes log

54 real rows in range (144 IDs not in DB); 31 flagged, moderate density.

**Dropped sub-location details** (a recurring pattern within one Thunder Bluff/Cenarion Circle
quest cluster): quests 3761 and 3786 both dropped "at the **Elder Rise** of Thunder Bluff" —
English confirms both Ghede and Bashana Runetotem are specifically at Elder Rise, not just
"Thunder Bluff" generically. Fixed both. (Quest 3762 already had this location correctly in its
own Details field, so the pattern isn't universal within the cluster — worth checking any other
Thunder Bluff Cenarion Circle quests reached in later batches for the same omission.)

**Incomplete titles**: quests 3762/3763 — English titles are "Assisting Arch Druid
**Runetotem**"/"Assisting Arch Druid **Staghelm**"; DB's titles were both just `協助大德魯伊`,
dropping the surname entirely. Fixed to `協助大德魯伊符文圖騰`/`協助大德魯伊鹿盔`. Quest 3763
also had an unrelated stray-character typo in its own Details (`伊範達爾·鹿盔`, an extra `伊`
not present anywhere else, including this same quest's own Objectives field) — fixed to match.

**Missing title**: quest 3907 — English confirms "**Lord** Incendius"; DB dropped `領主` in both
the Objectives and Details fields referencing him. Fixed both occurrences.

**Emote fix**: quest 3861 (`咕咕嘎！`) — the quest specifies the `/cheer` emote command
literally in English. DB's Objectives translated it vaguely as "look happy" (`做出高興的表情`),
losing the specific emote name; wowhead's own guess (`拍動翅膀`, "flap wings") is simply wrong
for `/cheer`. Fixed to this project's established emote name `歡呼` ("cheer"), and restored a
dropped "special chicken feed" repetition present in English at the same point.

**Dropped narrative clause**: quest 3901 (`斷骨骷髏`) — English confirms "the Rattlecage
skeletons, more mindless minions of **the Lich King**" — DB's Details dropped this
Lich-King-affiliation clause entirely. Restored it. (The kill count itself, 8, was already
correct on DB's side — see false positives below; DB's Objectives/EndText split the "kill X"
and "return to Y" instructions across two separate fields rather than combining them into one
like wowhead's Objectives does, which is a legitimate DB structural choice, not a gap, so that
part was left alone.)

**Typo fix**: quest 3914 — `安戈洛爾環形山` → `安戈洛環形山` (extra stray `爾`; `安戈洛` is the
already-established spelling for Un'Goro Crater used consistently elsewhere in the corpus,
including this same quest cluster's own quest 3761).

**Open follow-up resolved**: quest 3911's `傀儡`/`魔像` (Golem) dispute, flagged as an
unresolved project-wide item after batch 18 — confirmed `魔像` via `creature_template_locale`
back in that batch; applied the same fix here (`傀儡`→`魔像`, both occurrences). The corpus-wide
58:47 split noted in batch 18 is still open for a future dedicated pass.

**False positives confirmed (DB was already correct, no change)**:
- Quests 3821/3823/3824/3825 (Dreadmaul Rock/Extinguish the Firegut questline): DB used
  `火腹食人魔` throughout; wowhead rendered it `火腹巨魔`. English confirms "**Firegut ogres**"
  explicitly and repeatedly (LogDesc: "15 Firegut Ogre-Mages, 7 Firegut Ogres, and 7 Firegut
  Ogre Brutes") — no troll involved anywhere in this questline, and no confirmed clan exception
  (unlike Gordunni/Mosh'Ogg) applies here, so the default Ogre=`食人魔` rule holds. Wowhead was
  wrong across all 4 quests; DB was already correct. Left untouched.
- Quest 3901: wowhead's Objectives said "kill **12**" Rattlecage Skeletons; English confirms
  **8**, matching DB. Wowhead's count was the error here, not DB's.

### Batch 21 (3941–4140) fixes log

59 real rows in range (141 IDs not in DB); 39 flagged, high density — dominated by a Blackrock
Depths/Burning Steppes/Badlands quest cluster (Warlord Goretooth's Anvilrage campaign, the
Golem-guarded "Rise of the Machines" chain, Bael'Gar's molt).

**NPC-name fixes** (via `creature_template_locale`):
- Ginro **Hearthkindle** (quests 4124/4127/4130): DB had `基恩諾·火花` ("Spark"), which
  doesn't match "Hearthkindle" at all — fixed to `燃爐` ("hearth-kindler").
- Felpaw **Ravager** (quest 4120): `魔爪掠奪者` ("plunderer") → `劫毀者` ("destroyer").
- Maxwort **Uberglint** (quest 4123): `尤博格林` → `尤柏格林` (character-level spelling fix).

**Item-name fixes** (via `item_template_locale`) — DB had shortened both items to a generic
name, dropping their actual established full names:
- "Black Dragonflight Molt" / "Altered Black Dragonflight Molt" (quests 4022/4024): DB's
  `黑龍皮` ("black dragon skin") → `黑龍軍團之皮`/`變化後的黑龍軍團之皮`.
- "Fractured Elemental Shard" (quests 4061/4062/4063): DB's `元素碎片` ("fragment") →
  `元素裂片` ("shard"), matching the item's own established name exactly.

**Title consistency fix**: Warlord Goretooth (quests 4081/4082/4132) — DB rendered his title
three different ways across these three quests, none matching English's consistent "**Warlord**
Goretooth": `軍官`("officer"), `高圖斯大人`("Lord Goretooth"), `高圖斯軍閥`("Warlord Goretooth"
literally, but word order reversed from the naming convention used elsewhere). Fixed all three
to this corpus's established `督軍高圖斯` (62:3 dominant term for "Warlord" project-wide).

**Golem term extended**: quests 4061/4062/4063 — the same `傀儡`→`魔像` fix confirmed in
batches 18/20, applied to 3 more occurrences (`石頭傀儡`/`機械傀儡`/`傀儡統帥`/`狂怒傀儡`/
`戰鬥傀儡` → `石頭魔像`/`機械魔像`/`魔像領主`/`狂怒魔像`/`戰鬥魔像`).

**Other fixes**:
- Quest 4120: title `墮落的力量` → `腐化的力量` — English title is literally "The Strength of
  **Corruption**"; this corpus has substantial precedent for `腐化` as the Corruption term
  (130 occurrences) alongside `墮落` (166, used for a related but distinct "fallen/depraved"
  sense) — picked the one matching this specific English title word.
- Quest 4133 (`薇薇安·拉格雷`): English confirms "**Shadowmaster** Vivian Lagrave... Dark Iron
  dwarves of **Blackrock Depths**" — DB's `暗法師`("Shadow Mage") doesn't match "Shadowmaster"
  precisely, and DB's Details dropped the specific "Blackrock Depths" location entirely
  (just said "something about Dark Iron dwarves"). Fixed both.

### Batch 22 (4141–4340) fixes log

55 real rows in range (143 IDs not in DB); 43 flagged, high density.

**Muigin and Larion questline** (5 quests: 4141/4143/4145/4146/4147, an Un'Goro Crater chain)
— both names were wrong throughout: `creature_template_locale` confirms Larion (id 9118) →
`拉里安` (DB had `拉瑞安`) and Muigin (id 9119) → `莫爾金` (DB had `穆爾金`). Fixed every
occurrence across all 5 quests, titles included. Quest 4141 also had a real count error — DB's
Objectives said "收集20個血瓣花" but English LogDesc explicitly says "Collect **15**
Bloodpetals" (matching `RequiredSourceItemCount1`=15 exactly) — fixed to 15. Also fixed another
instance of the recurring `安戈洛爾`→`安戈洛` typo (Un'Goro Crater; third occurrence found
across batches 20-22, always the same spurious extra `爾`).

**Missed occurrences of already-confirmed fixes** — three separate proper-noun fixes settled in
earlier batches turned out to have more occurrences later in the corpus that weren't caught at
the time (a reminder that a "confirmed fix" from a prior batch should still be re-checked
whenever the same name/term resurfaces, not assumed already-complete):
- Lord Incendius (quest 4263, settled in batch 20's quest 3907): `伊森迪奧斯` → `伊森迪奧斯領主`,
  5 occurrences in this one quest row.
- Ginro Hearthkindle (quest 4265, settled in batch 21's quests 4124/4127/4130): `基恩諾·火花`
  → `基恩諾·燃爐`, 2 occurrences.
- Golem term (quest 4282, settled in batches 18/20/21): `傀儡統帥阿格曼奇` → `魔像領主阿格曼奇`,
  2 occurrences.

**Other proper-noun fixes** (via `creature_template_locale`):
- Zarrin (quest 4161): English LogDesc "Collect 7 Small Spider Legs for **Zarrin** in
  **Dolanaar**" — DB's Objectives dropped the delivery target entirely (`收集7條小蜘蛛腿`, no
  name/location). Restored using the locale table's confirmed spelling `札瑞恩` (also fixed
  this row's own EndText, which already had the name but with a typo'd radical, `扎`→`札`).
- "A-Me 01" (quests 4243/4244/4245): the locale table (id 9623) confirms this untranslated
  literal string should be transliterated `艾米 01` — fixed throughout all 3 quests (titles
  included).
- Lady Katrana Prestor (quest 4185): the locale table (id 1749) confirms her title is `女士`
  ("Lady"), not DB's `女伯爵` ("Countess") — fixed in Details/Objectives/CompletedText.

**Creature-type/color mix-up**: quest 4182 (`黑龍的威脅`) — English LogDesc: "Slay 15 Black
Broodlings, 10 Black Dragonspawn, 4 Black Wyrmkin and 1 Black Drake." DB's Objectives used the
same term `龍人` for two different creature types (Dragonspawn and Wyrmkin, which the locale
table distinguishes as `龍裔` vs `龍人` respectively) and used the wrong color entirely for the
Wyrmkin entry (`火鱗龍人`/"Firescale," should be `黑色龍人`/"Black"). Fixed to match the locale
table's per-creature breakdown exactly.

**Item-name fix**: quest 4283 (`五十個！`) — English LogDesc: "Collect 50 Blackrock
**Medallions**." DB's Objectives said `黑石徽章`("badges"); fixed to `黑石勳章`, matching the
concrete item name (same Badge/Medal pattern as batch 13/20). Left Details' own colloquial
"collecting badges" references (`徽章`) untouched — English's own Details text also uses the
casual word "badges" repeatedly, so that occurrence already matches its English counterpart;
only the Objectives field (which should name the actual required item) needed the fix. Also
reconfirmed Details' `食人魔耳朵` ("ogre ear collection") is correct against English — wowhead's
`巨魔耳朵` there is wrong.

**Surfaced to the user rather than resolved unilaterally**: quest 4184 (`真正的主人`) — its
English `quest_template` source explicitly names **King Varian Wrynn** as the recipient, in
both LogDescription and Details independently. But both DB's pre-existing zhTW text and
wowhead's own scrape agree with each other that the recipient is **Duke/Lord Bolvar Fordragon**
instead — an unusual pattern, since normally a DB/wowhead disagreement means one side is wrong,
not that both agree against the English source. Asked the user directly rather than guessing;
confirmed **Bolvar is correct lore-wise and is the actual quest-ending NPC** (Bolvar was
Stormwind's regent in original vanilla-era lore; Varian Wrynn's return was a later revision that
likely only touched this specific quest_template row's English text, not the actual live
quest content). Left DB's text unchanged. **Worth remembering**: when two independent zhTW
sources agree with each other but disagree with the current `quest_template.sql` English text,
that's a sign the English source itself may reflect a later out-of-band content revision — don't
assume `quest_template.sql` is automatically right just because it's usually the most reliable
ground truth; check with the user when the disagreement pattern itself looks unusual.

## Known pre-existing issues found but not yet fixed (out of scope so far)

- `quest_template_locale` in `rev_1783688290124463491.sql` has duplicate rows (two
  DELETE+INSERT pairs for the same ID) for quest IDs **1241, 1250, 1264** — needs
  dedup, unrelated to the batches above.
- Quest 170 uses `石齶穴居人`/`石齶` (Rockjaw) for what might actually be the "Stonesplinter"
  trogg family (`碎石怪`/established convention) — the `怪` vs `人` suffix question is now
  settled project-wide (see the trogg note above, `穴居人` throughout as of batch 16), but
  *which family name* ("Rockjaw" vs "Stonesplinter") is correct for quest 170 specifically is
  still unverified —
  check `creature_template` for the exact English name used in quest 170's `RequiredNpcOrGo`
  before assuming either way.
- **40 quest rows contain raw, unconverted simplified Chinese** (found batch 9, not yet fixed
  except quest 755): 3062, 4496, 4507, 8224, 8365, 9852, 10690, 10999, 11132, 11164, 11272,
  11435, 11452, 11453, 11992, 12024, 12119, 12122, 12123, 12124, 12851, 12918, 13004, 13096,
  13108, 13109, 13248, 13252, 13372, 13375, 13380, 13423, 13959, 13986, 13997, 14032, 14355,
  14409, 25055, 25092 — a distinct, larger issue from the zhCN-vocabulary-leak problem this
  pass otherwise targets (these rows were never OpenCC-converted at all, not just translated
  with zhCN word choices). All well past where any batch has reached (1–1740 so far); needs
  its own dedicated conversion pass whenever a future batch gets there.
- The `裡`/`里` locative ambiguity is only partially resolved (batch 9's container-noun
  classifier found 17 high-precision matches project-wide and fixed them, but many more
  ambiguous cases remain unclassified corpus-wide — see batch 9's log entry above for the
  classifier logic and its limits).
- Quest 1960 (outside all batches reached so far) has the identical pre-fix "filled coffers"
  sentence that batch 10 fixed in quest 1920 (missing the "empty coffers" clause) — flagged,
  not touched, since it's out of range; verify against its own English source when reached.
- Galvan the Ancient (creature 7802, quests 2758-2765 and others in that questline): DB never
  gives him a title, but `creature_template`'s literal English subname is "Galvan **the
  Ancient**" — wowhead's own quest-page rendering (`『長者』`, "Elder") doesn't precisely match
  "Ancient" either, so batch 15 deliberately left this unresolved rather than adopting a
  half-correct alternative. Needs either a better literal rendering (e.g. `太古的`/`年邁的`) or
  direct confirmation via the NPC's own dedicated wowhead page before touching it.
- `質量`/`品質` ("Quality" vs "mass") has only been swept within batches reached so far
  (1954, 2821, 2822 — see batch 15's log). ~28 more occurrences exist project-wide in
  not-yet-reached quest IDs (4323, 5284, 5582, 7641, 7648, 8515, 8556, 8697-8704, 8905-8910,
  8912, 10182, 10201, 10492) — verify each context individually when that range is reached,
  since `質量` can legitimately mean "mass" in rare cases (one ambiguous instance already
  found at quest 10201, deliberately left untouched).

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

Not started. Resume from quest ID 4341 (batch 23, target range roughly 4341–4540) following
the same two-phase methodology, skipping any ID present in `skip-list.tsv`. 6,550 quest IDs
remain after batch 22 (see Total scope note above). A reminder from batch 22: a proper-noun fix
confirmed via `creature_template_locale` in one batch can still resurface, unfixed, several
batches later — batch 22 caught 3 such cases (Lord Incendius from batch 20's quest 3907, Ginro
Hearthkindle from batch 21's quests, the Golem term from batches 18/20/21) that reappeared in
new quest rows the original batch never touched (they weren't part of that batch's ID range at
all). This isn't something to fix by re-sweeping past batches — just keep the confirmed-term
list in mind when a name/term looks familiar in a new batch, even one already "settled" long
ago. Remember `diff_quest_text.py` has no range
arguments — it always diffs the whole cached jsonl, so filter its output to the current batch's
ID range before reviewing (see batch 17's log for the exact filtering approach and why an
unfiltered run can resurface stale/already-resolved findings from earlier batches). A follow-up
worth doing whenever there's spare time: the `傀儡`/`魔像` (Golem) split is corpus-wide
inconsistent — batch 18 found it at 58:47 with the locale table favoring `魔像`, and batches 20
and 21 fixed 4 more confirmed instances (quests 3911, 4061, 4062, 4063), but the bulk of the
split is still unswept, so it remains an open project-wide cleanup item. Keep the
OpenCC-origin insight in mind (see
`[[feedback-zhtw-ground-truth-priority]]`) — corpus self-consistency is weaker evidence than
earlier batches treated it as, but any pattern-based fix (grammar, idiom, orthography) still
needs per-instance verification against the real English source before a sweep, not a blind
regex replace. Batches 10-16 used a technique for no-locale-table disputes: `curl -sL
"https://www.wowhead.com/wotlk/tw/npc=<id>"` (or `item=<id>`) and read the `<title>` tag —
faster and more authoritative than the pre-fetched quest-page jsonl for single-entity checks;
this caught two more corpus-majority-was-wrong cases in batch 15 (Mekkatorque's title, 10:0
self-consistent but wrong). Also remember: wowhead's own quest-page fetch is not an
independent source when it derives from the same broken client string DB does (batch 11's
quest 2098 `基爾卡可` typo appeared identically on both sides), and can also fabricate content
outright (batch 12's quest 2198) or fail to render entirely, returning raw English/markup
(batch 13's quest 2358) — a match between DB and wowhead isn't automatic proof of correctness
if a locale table or dedicated page contradicts them, and a wowhead/DB disagreement isn't
automatic proof DB is wrong either. Batch 14 confirmed this project's raw `$g male:female`
gender-token storage format is distinct from wowhead's `<male/female>` bracket display
convention. Batch 15 flagged two things worth carrying forward: (1) `質量`/`品質` needs
per-instance verification when the corpus reaches IDs 4323+ (list in Known Issues above) since
`質量` can rarely mean "mass" legitimately; (2) Galvan the Ancient's title is still unresolved
(neither DB's no-title nor wowhead's `長者`/"Elder" matches "the Ancient" precisely) — don't
assume it's settled if it resurfaces in a later batch. Batch 16 reconfirmed that a wowhead/DB
mismatch can go *either* direction even within the same batch (quest 2949 was a real DB
content-swap bug; quest 3121 was a wowhead fetch-error false positive) — always check the raw
English `quest_template` source directly before trusting either side when they disagree on
something as fundamental as which NPC/location a quest is about, not just wording.
