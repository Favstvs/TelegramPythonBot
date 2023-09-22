DROP TABLE IF EXISTS `management`;

CREATE TABLE `management` (
  `ID_Supergruppo` bigint NOT NULL,
  `ID_Waifu` int DEFAULT NULL,
  `ID_Husbando` int DEFAULT NULL,
  `Time_Mess` int unsigned NOT NULL,
  `Started` tinyint NOT NULL,
  `Time_reset` int unsigned NOT NULL,
  PRIMARY KEY (`ID_Supergruppo`),
  KEY `management_ibfk_2` (`ID_Waifu`),
  KEY `management_ibfk_4` (`ID_Husbando`),
  CONSTRAINT `management_ibfk_1` FOREIGN KEY (`ID_Supergruppo`) REFERENCES `supergruppo` (`ID_Supergruppo`),
  CONSTRAINT `management_ibfk_2` FOREIGN KEY (`ID_Waifu`) REFERENCES `waifu` (`ID_Waifu`),
  CONSTRAINT `management_ibfk_4` FOREIGN KEY (`ID_Husbando`) REFERENCES `husbandi` (`ID_Husbando`)
) ENGINE=InnoDB;
