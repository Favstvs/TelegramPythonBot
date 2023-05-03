DROP TABLE IF EXISTS `users`;

CREATE TABLE `daily` (
  `ID_User` bigint NOT NULL,
  `Username` varchar(36) NOT NULL,
  `Coins` int NOT NULL AUTO_INCREMENT ,
  KEY `Coins` (`Coins`),
  PRIMARY KEY (`ID_User`)
) ENGINE=InnoDB;
