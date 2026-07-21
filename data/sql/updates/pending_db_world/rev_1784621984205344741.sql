-- Fill missing zhTW gossip_menu_option_locale row for MenuID 0, OptionID 2
-- ("I want to travel fast"), the shared flight-master travel option used by
-- every flight master NPC in the game (e.g. Laando, entry 17554). Base data
-- has this row translated for deDE/frFR/zhCN but zhTW was entirely absent.
DELETE FROM `gossip_menu_option_locale` WHERE `MenuID` = 0 AND `OptionID` = 2 AND `Locale` = 'zhTW';
INSERT INTO `gossip_menu_option_locale` (`MenuID`, `OptionID`, `Locale`, `OptionText`, `BoxText`) VALUES (0, 2, 'zhTW', '我想要快速旅行。', NULL);
