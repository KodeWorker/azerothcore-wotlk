-- Prince Anduin Wrynn (npc=1747) zhTW correction: base row read 安度因·烏瑞恩「國王」/
-- 暴風城的「國王」, contradicting the row's own English Title 'Prince of Stormwind' and
-- the zhCN sibling row ('暴风城的王子'). This is the young Prince Anduin (Varian's son,
-- introduced in WotLK) at model 11874/faction 12, not the historical King Anduin Wrynn
-- (Varian's grandfather, killed pre-Cataclysm at Blackrock Spire) referenced elsewhere in
-- page_text — the two share a name but are different individuals; the base zhTW row
-- appears to have been mixed up with the King, matching Wowhead's own
-- wotlk/tw/npc=1747 mistranslation. Corrected to match the English/zhCN title and drop
-- the erroneous 國王 suffix from the name.
DELETE FROM `creature_template_locale` WHERE `entry` = 1747 AND `locale` = 'zhTW';
INSERT INTO `creature_template_locale` (`entry`, `locale`, `Name`, `Title`, `VerifiedBuild`) VALUES (1747,'zhTW','安度因·烏瑞恩','暴風城的王子',0);
