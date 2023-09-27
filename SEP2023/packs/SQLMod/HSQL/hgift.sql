DROP TABLE IF EXISTS `hgift`;

CREATE TABLE `hgift` (
  `ID_Supergruppo` bigint NOT NULL,
  `Mess_ID_Gift` bigint NOT NULL,
  `ID_User_1` bigint NOT NULL,
  `ID_User_2` bigint NOT NULL,
  `Regalo` int NOT NULL,
  PRIMARY KEY (`ID_Supergruppo`,`Mess_ID_Gift`),
  KEY `ID_User_1` (`ID_User_1`),
  KEY `ID_User_2` (`ID_User_2`),
  KEY `Regalo` (`Regalo`),
  CONSTRAINT `regalo_ibfk_1` FOREIGN KEY (`ID_User_1`) REFERENCES `users` (`ID_User`),
  CONSTRAINT `regalo_ibfk_2` FOREIGN KEY (`ID_User_2`) REFERENCES `users` (`ID_User`),
  CONSTRAINT `regalo_ibfk_3` FOREIGN KEY (`ID_Supergruppo`) REFERENCES `supergruppo` (`ID_Supergruppo`),
  CONSTRAINT `regalo_ibfk_4` FOREIGN KEY (`Regalo`) REFERENCES `husbando` (`ID_Husbando`)
) ENGINE=InnoDB;
