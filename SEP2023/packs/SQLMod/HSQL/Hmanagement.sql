DROP TABLE IF EXISTS `Hmanagement`;

CREATE TABLE `Hmanagement` (
  `ID_Supergruppo` bigint NOT NULL,
  `ID_Husbando` int DEFAULT NULL,
  `Time_Mess` int unsigned NOT NULL,
  `Started` tinyint NOT NULL,
  `Time_reset` int unsigned NOT NULL,
  PRIMARY KEY (`ID_Supergruppo`),
  KEY `management_ibfk_2` (`ID_Husbando`),
  CONSTRAINT `management_ibfk_1` FOREIGN KEY (`ID_Supergruppo`) REFERENCES `supergruppo` (`ID_Supergruppo`),
  CONSTRAINT `management_ibfk_2` FOREIGN KEY (`ID_Husbando`) REFERENCES `husbando` (`ID_Husbando`)
) ENGINE=InnoDB;
