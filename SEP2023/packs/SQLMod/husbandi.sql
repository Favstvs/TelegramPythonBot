
DROP TABLE IF EXISTS `husbandi`;

CREATE TABLE `husbandi` (
  `ID_Husbando` int NOT NULL AUTO_INCREMENT,
  `Nome_Husbando` varchar(256) DEFAULT NULL,
  `Nome_Anime` varchar(256) DEFAULT NULL,
  `PATH_IMG` varchar(256) DEFAULT NULL,
   PRIMARY KEY (`ID_Husbando`)
) ENGINE=InnoDB AUTO_INCREMENT=161;
 
