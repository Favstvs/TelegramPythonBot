DROP TABLE IF EXISTS `Wrelation`;

CREATE TABLE `Wrelation` (
  `ID_User` bigint NOT NULL,
  `ID_Supergruppo` bigint NOT NULL,
  `ID_Waifu` int NOT NULL,
  `NP` int NOT NULL,
  `Place` int NOT NULL,
  PRIMARY KEY (`ID_User`,`ID_Supergruppo`,`ID_Waifu`),
  KEY `ID_Supergruppo` (`ID_Supergruppo`),
  KEY `ID_Waifu` (`ID_Waifu`),
  CONSTRAINT `relazioni_ibfk_1` FOREIGN KEY (`ID_User`) REFERENCES `users` (`ID_User`),
  CONSTRAINT `relazioni_ibfk_2` FOREIGN KEY (`ID_Supergruppo`) REFERENCES `supergruppo` (`ID_Supergruppo`),
  CONSTRAINT `relazioni_ibfk_3` FOREIGN KEY (`ID_Waifu`) REFERENCES `waifu` (`ID_Waifu`)
) ENGINE=InnoDB;
