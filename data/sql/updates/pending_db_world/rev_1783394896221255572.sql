-- Fill missing zhTW item_template_locale rows, converted from zhCN via OpenCC s2twp,
-- with known-official zone-name corrections applied
DELETE FROM `item_template_locale` WHERE `ID` = 13330 AND `locale` = 'zhTW';
INSERT INTO `item_template_locale` (`ID`, `locale`, `Name`, `Description`, `VerifiedBuild`) VALUES (13330,'zhTW','叮噹包',NULL,0);
DELETE FROM `item_template_locale` WHERE `ID` = 20487 AND `locale` = 'zhTW';
INSERT INTO `item_template_locale` (`ID`, `locale`, `Name`, `Description`, `VerifiedBuild`) VALUES (20487,'zhTW','羅克迪洛爾，上古守護者的手杖','',15050);
DELETE FROM `item_template_locale` WHERE `ID` = 20488 AND `locale` = 'zhTW';
INSERT INTO `item_template_locale` (`ID`, `locale`, `Name`, `Description`, `VerifiedBuild`) VALUES (20488,'zhTW','倫魯迪洛爾，上古守護者的長弓','',15050);
DELETE FROM `item_template_locale` WHERE `ID` = 30427 AND `locale` = 'zhTW';
INSERT INTO `item_template_locale` (`ID`, `locale`, `Name`, `Description`, `VerifiedBuild`) VALUES (30427,'zhTW',NULL,'藏寶地點用X標了出來。',0);
DELETE FROM `item_template_locale` WHERE `ID` = 32594 AND `locale` = 'zhTW';
INSERT INTO `item_template_locale` (`ID`, `locale`, `Name`, `Description`, `VerifiedBuild`) VALUES (32594,'zhTW','奧格瑞拉測試外套',NULL,0);
DELETE FROM `item_template_locale` WHERE `ID` = 33350 AND `locale` = 'zhTW';
INSERT INTO `item_template_locale` (`ID`, `locale`, `Name`, `Description`, `VerifiedBuild`) VALUES (33350,'zhTW','霜之哀傷','',15050);
DELETE FROM `item_template_locale` WHERE `ID` = 43517 AND `locale` = 'zhTW';
INSERT INTO `item_template_locale` (`ID`, `locale`, `Name`, `Description`, `VerifiedBuild`) VALUES (43517,'zhTW','企鵝小潘','教你學會召喚企鵝寶寶小潘。',18019);
