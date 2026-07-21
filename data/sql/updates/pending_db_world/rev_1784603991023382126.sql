-- Stonesplinter Trogg clan (Loch Modan) tribe-name correction: `碎石`->`石裂`. DBC-confirmed
-- via AreaTable.dbc AreaID 923 (ParentAreaID 38 = Loch Modan) = "Stonesplinter Valley" ->
-- `石裂之谷`, tier-1 ground truth. Base creature_template_locale had it OpenCC-converted from
-- zhCN as `碎石`, inconsistent with item_template_locale's own `石裂` (Stonesplinter
-- Axe/Dagger/Mace/Blade/Rags, Knowledge: Stonesplinter Disguise), which was already correct.
-- Role suffixes drop the generic `怪` filler: tribe name + role noun directly (e.g. `石裂斥候`,
-- not `石裂怪斥候`).
DELETE FROM `creature_template_locale` WHERE `entry` = 1161 AND `locale` = 'zhTW';
INSERT INTO `creature_template_locale` (`entry`, `locale`, `Name`, `Title`, `VerifiedBuild`) VALUES (1161,'zhTW','石裂穴居人','',0);
DELETE FROM `creature_template_locale` WHERE `entry` = 1162 AND `locale` = 'zhTW';
INSERT INTO `creature_template_locale` (`entry`, `locale`, `Name`, `Title`, `VerifiedBuild`) VALUES (1162,'zhTW','石裂斥候','',0);
DELETE FROM `creature_template_locale` WHERE `entry` = 1163 AND `locale` = 'zhTW';
INSERT INTO `creature_template_locale` (`entry`, `locale`, `Name`, `Title`, `VerifiedBuild`) VALUES (1163,'zhTW','石裂擊顱者','',0);
DELETE FROM `creature_template_locale` WHERE `entry` = 1164 AND `locale` = 'zhTW';
INSERT INTO `creature_template_locale` (`entry`, `locale`, `Name`, `Title`, `VerifiedBuild`) VALUES (1164,'zhTW','石裂斷骨者','',0);
DELETE FROM `creature_template_locale` WHERE `entry` = 1165 AND `locale` = 'zhTW';
INSERT INTO `creature_template_locale` (`entry`, `locale`, `Name`, `Title`, `VerifiedBuild`) VALUES (1165,'zhTW','石裂地卜師','',0);
DELETE FROM `creature_template_locale` WHERE `entry` = 1166 AND `locale` = 'zhTW';
INSERT INTO `creature_template_locale` (`entry`, `locale`, `Name`, `Title`, `VerifiedBuild`) VALUES (1166,'zhTW','石裂先知','',0);
DELETE FROM `creature_template_locale` WHERE `entry` = 1167 AND `locale` = 'zhTW';
INSERT INTO `creature_template_locale` (`entry`, `locale`, `Name`, `Title`, `VerifiedBuild`) VALUES (1167,'zhTW','石裂掘地工','',0);
DELETE FROM `creature_template_locale` WHERE `entry` = 1197 AND `locale` = 'zhTW';
INSERT INTO `creature_template_locale` (`entry`, `locale`, `Name`, `Title`, `VerifiedBuild`) VALUES (1197,'zhTW','石裂薩滿','',0);
DELETE FROM `creature_template_locale` WHERE `entry` = 1398 AND `locale` = 'zhTW';
INSERT INTO `creature_template_locale` (`entry`, `locale`, `Name`, `Title`, `VerifiedBuild`) VALUES (1398,'zhTW','大頭目加爾高西','石裂酋長',0);
DELETE FROM `creature_template_locale` WHERE `entry` = 1399 AND `locale` = 'zhTW';
INSERT INTO `creature_template_locale` (`entry`, `locale`, `Name`, `Title`, `VerifiedBuild`) VALUES (1399,'zhTW','瑪高什','石裂部落薩滿',0);
