DROP TABLE IF EXISTS `Hrelation`;

CREATE TABLE `Hrelation` (
  `ID_User` bigint NOT NULL,
  `ID_Supergruppo` bigint NOT NULL,
  `ID_Husbando` int NOT NULL,
  `NP` int NOT NULL,
  `Place` int NOT NULL,
  PRIMARY KEY (`ID_User`, `ID_Supergruppo`, `ID_Husbando`),
  KEY `ID_Supergruppo` (`ID_Supergruppo`),
  KEY `ID_Husbando` (`ID_Husbando`),
  CONSTRAINT `relazioni_ibfk_1` FOREIGN KEY (`ID_User`) REFERENCES `users` (`ID_User`),
  CONSTRAINT `relazioni_ibfk_2` FOREIGN KEY (`ID_Supergruppo`) REFERENCES `supergruppo` (`ID_Supergruppo`),
  CONSTRAINT `relazioni_ibfk_3` FOREIGN KEY (`ID_Husbando`) REFERENCES `husbando` (`ID_Husbando`)
) ENGINE=InnoDB;
