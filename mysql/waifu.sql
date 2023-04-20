DROP TABLE IF EXISTS `waifu`;

CREATE TABLE `waifu` (
  `ID_Waifu` int NOT NULL AUTO_INCREMENT,
  `Nome_Waifu` varchar(256) DEFAULT NULL,
  `Nome_Anime` varchar(256) DEFAULT NULL,
  `PATH_IMG` varchar(256) DEFAULT NULL,
   PRIMARY KEY (`ID_Waifu`)
) ENGINE=InnoDB AUTO_INCREMENT=161;
 
