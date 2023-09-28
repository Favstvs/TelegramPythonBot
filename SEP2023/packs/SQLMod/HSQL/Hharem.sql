CREATE TABLE `harem` (
  `ID_Supergruppo` bigint NOT NULL,
  `ID_User` bigint NOT NULL,
  `Mess_ID_List` bigint NOT NULL,
  `Husbando_Preferito` int DEFAULT NULL,
  PRIMARY KEY (`ID_Supergruppo`,`ID_User`,`Mess_ID_List`),
  KEY `ID_User` (`ID_User`),
  KEY `harem_ibfk_4` (`Husbando_Preferito`),
  CONSTRAINT `harem_ibfk_4` FOREIGN KEY (`Husbando_Preferito`) REFERENCES `husbando` (`ID_Husbando`),
  CONSTRAINT `harem_ibfk_2` FOREIGN KEY (`ID_User`) REFERENCES `users` (`ID_User`),
  CONSTRAINT `harem_ibfk_3` FOREIGN KEY (`ID_Supergruppo`) REFERENCES `supergruppo` (`ID_Supergruppo`)
) ENGINE=InnoDB;
