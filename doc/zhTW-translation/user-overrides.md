# zhTW User Overrides — Deliberate Preference Decisions

This tracks every case in the zhTW verification pass (`verification-progress.md`) where the
**user deliberately chose a translation that goes against the project's normal ground-truth
hierarchy** (DBC extract > `creature_template_locale`/`item_template_locale`/
`gameobject_template_locale` > dedicated wowhead NPC/item page > wowhead quest-page prose >
DB's own pre-existing text — see `verification-progress.md`'s Methodology section) — not
because the higher-tier source was wrong, but on a stated taste, phonetic, semantic, or
lore-fit preference.

**Why this exists separately**: `verification-progress.md` already logs each of these inline
at the point they were made, but they're scattered across 76+ batches of narrative log entries.
A future batch (human or agent) doing a routine DBC/locale-table cross-check has no way to know
one of these terms was already deliberately litigated — the batch-60 incident (re-flagging
Blackfathom Deeps as a "bug" against the DBC, sweeping it backwards, because the earlier
override wasn't checked first) happened once already and is exactly the failure mode this doc
is meant to prevent. **Before treating any of the terms below as a bug, check here first.**

Each entry below is a deliberate override, not an ordinary source-hierarchy resolution (e.g.
picking wowhead over a corpus majority because wowhead is simply the correct reading — those
are normal verification work, not tracked here). Full incident history and exact occurrence
counts live in `verification-progress.md`; this doc is the lookup index, not a replacement.

## Standing overrides (currently in effect)

### Felhound / Fel Hound → `惡魔犬` (not `地獄犬`)
**Override type**: semantic preference. `惡魔`("demon") fits Legion/demonic creatures better
than `地獄`("hell"). Applied even across two distinct creature identities (Felhunter and the
separate "Fel Hound") getting the same treatment. Swept 11× full corpus.
Source: `verification-progress.md` Systemic sweeps, "地獄犬→惡魔犬".

### Aurius → `奧里爾斯` (not `奧里克斯`)
**Override type**: phonetic preference. Three candidate spellings existed (DB `奧裡克斯`,
`creature_template_locale` `奧里克斯`, wowhead `奧里爾斯`) with no source agreeing with
another. Normal hierarchy would have picked the locale table's `奧里克斯`; the user judged
wowhead's spelling phonetically closer to the English "Aurius" and overrode to that instead.
Source: `verification-progress.md` Systemic sweeps, "Aurius".

### Ran Bloodtooth (npc 3696) → `萊恩·血牙` (not `蘭恩·血牙`)
**Override type**: phonetic preference against `creature_template_locale`, corroborated (not
contradicted) by quest 1046's own untouched text.
Source: `verification-progress.md` NPC name table, "Ran Bloodtooth (3696)".

### Wind Rider, generic Horde flight mount → `雙足飛龍` (not the literal `馭風者`)
**Override type**: lore-fit preference. The mount is lore-wise a Wyvern, and `雙足飛龍` is the
accepted zhTW rendering even though it doesn't literally match the English words "wind" +
"rider." This reversed an earlier, more literal fix. **Does not apply to quest 4767's own
title** — there, `馭風者` is a directly-confirmed-correct English quest-title match, a
different context from the generic mount reference. Fixed in quests 6384/6385/6386; ~16 more
bare `馭風者` occurrences remain elsewhere in the corpus, each needing individual
context-checking (mount reference vs. quest title) before assuming either term applies.
Source: `verification-progress.md` NPC/term table, "Wind Rider (Horde flight mount, generic)".

### Resonite cask (Earthen Ring/Goggeroc questline, quest 6481) → `共鳴石` + `粉碎`("smash")
**Override type**: lore/visual accuracy over literal English. The English quest text says
"cask" (`桶`) and "open" (`開啟`), but the actual in-game object is a large crystal, not a
barrel — wowhead's non-literal rendering matches what players actually see. Not a taste
preference so much as a correction of the English source's own loose wording against observed
in-game reality; documented here because a literal-minded future check would "fix" it back to
the wrong literal reading.
Source: `verification-progress.md` NPC/term table, "Resonite cask".

### Discordant Bracers (item name, quest 6804 Objectives only) → `不諧腕索` (not literal `不諧護腕`)
**Override type**: established zhTW item-naming-convention preference over a literal
"Bracers"→`護腕` match. Scoped only to this quest's Objectives field — the same row's separate
generic-flavor phrase `縛靈護腕` was never in dispute (DB and wowhead already agreed on it) and
is unrelated; don't conflate the two.
Source: `verification-progress.md` NPC/term table, "Discordant Bracers (item name specifically)".

### Zinfizzlex's Portable Shredder Unit (quests 6861/6862) → wowhead's `可攜式`/`工程大師`
**Override type**: quest-scoped stylistic preference for wowhead's phrasing over DB's own
established, otherwise-legitimate terms (`行動式`/`首席技師`). Explicitly **does not extend**
to other unrelated `首席技師`/`行動式` occurrences elsewhere in the corpus — those were not
individually re-verified and should not be assumed to need the same treatment.
Source: `verification-progress.md` NPC/term table, "Zinfizzlex's Portable Shredder Unit".

## Reversed overrides (history — most recent decision wins)

### Blackfathom Deeps: `黑澗深淵` (batch-34 override, 2026-07-xx) → REVERSED 2026-07-25 → now `黑暗深淵`
**Original override**: `AreaTable_zhTW.tsv` (tier-1 DBC, ids 719/2797) plus four other
independently-agreeing DBC files confirmed `黑暗深淵` as the WotLK-era-accurate zone name.
wowhead's own expansion-tagged pages additionally confirmed this zone was renamed by Blizzard
between eras — `wotlk`/`tbc` show `黑暗深淵`, `classic`/`cata`/`mop-classic`/current retail show
`黑澗深淵`. Despite the WotLK-era evidence being solid and multiply corroborated, the user's
batch-34 call was `黑澗深淵` on a stated semantic-fit preference ("more fitting for
blackfathom") — all 25 occurrences swept to that. Batch 60 independently re-discovered the
DBC/locale-table disagreement, didn't check this decision had already been made, and swept it
backward again before being caught and reverted same-batch.

**Reversal**: 2026-07-25, the user explicitly revisited this and reversed their own batch-34
call ("I regret that early decision... use wotlk-era translation 黑暗深淵"). `黑暗深淵` is now
the standing answer — all 26 occurrences (25 `黑澗深淵` instances + 1 previously-unswept
same-zone outlier spelling `黑色深淵` in quest 1198's `ObjectiveText1`) swept in
`rev_1783688290124463491.sql`, committed `39283f5bb`.

**If this resurfaces again, `黑暗深淵` is correct** — do not revert to `黑澗深淵` without a
fresh, explicit user instruction, since this is now the second reversal of the same term.
Source: `verification-progress.md` Established terms, "Blackfathom Deeps".

### Doctor Theolen Krastinov: `瑟爾林·卡斯迪諾夫教授`, no epithet (batch-28 override, reverted same-day) → RESOLVED 2026-07-25 → quest-title epithet `『屠夫』` restored
**Original override**: batch-28 added `『屠夫』`("the Butcher") to quest 5382's Title, matching
this project's own WotLK-era English quest title ("Doctor Theolen Krastinov, the Butcher"). This
was reverted same-day on the belief that a later expansion's official Chinese localization had
deliberately dropped the epithet to plain `教授`(Professor), and the user preferred that more
polished, epithet-free reading.

**Re-examination**: 2026-07-25, prompted by a wowhead link showing npc=11261 carries a "The
Butcher" tag, the base (immutable) `creature_template_locale.sql` dump was checked directly —
not the `2026_03_13_04.sql` migration that had only ever touched the `Name` column. It turned up
a **separate `Title` column** for entry 11261, never touched by that migration:
`Name`=`瑟爾林·卡斯迪諾夫教授`, `Title`=`屠夫`. Every other available locale confirms the
identical Name/Title split (zhCN's own `Title` field is also literally `屠夫`; deDE/esES/esMX/
frFR/koKR/ruRU all pair a plain name with a "the Butcher"-equivalent title). So `屠夫` was never
actually competing with `教授` for the same slot — it's a still-current, multi-locale-
corroborated field sitting in a column nobody had checked. Independently confirmed via
`wowhead.com/wotlk/tw/quest=5382` (title `『屠夫』瑟爾林-卡斯迪諾夫教授`, matching except for a
`-`/`·` name-separator rendering quirk — kept `·` for corpus consistency).

**Resolution**: this was reclassified from "user taste override against valid evidence" to
"the original fix was right, the revert was based on an incomplete check" — restored quest
5382's Title to `『屠夫』瑟爾林·卡斯迪諾夫教授`. `creature_template_locale.Name` (`教授`, no
epithet) was correct all along and is unchanged; only the quest-title epithet was missing.
**Not a precedent for reversing other "later-expansion Chinese localization" calls** — this one
resolved because a previously-unchecked same-row DB column settled it, not because "prefer the
WotLK-era reading" is now a blanket rule. Each such case still needs its own check.
Source: `verification-progress.md` NPC/term table, "Doctor Theolen Krastinov".

## Related, not itself an override

### Gakin the Darkbinder (npc 6122) → `黑暗縛靈者加科因`
Not a preference override — `creature_template_locale` entry 6122 already established this
name; quest text (`『黑暗縛靈師』加金`/bare `加金`) was simply out of date and brought in line
with it. Listed here only because it landed in the same 2026-07-25 session as the Blackfathom
Deeps reversal. Full detail: `verification-progress.md` Established terms, "Gakin the
Darkbinder".

## Maintenance note

When a new override happens, add it here (standing section) with: the term, what the hierarchy
would otherwise say, what was chosen instead, why, and scope (swept everywhere vs. scoped to
specific quest IDs). If a standing override is later reversed, move it to the "Reversed
overrides" section with both the original and new decision dated, rather than deleting the
history — as the Blackfathom Deeps case shows, these can be revisited more than once.
