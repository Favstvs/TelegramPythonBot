DROP TABLE IF EXISTS `users`;

CREATE TABLE `users` (
  `ID_User` bigint NOT NULL,
  `Username` varchar(36) NOT NULL,
  `Coins` int NOT NULL AUTO_INCREMENT,
  `Time_Mess` datetime,
  KEY `Coins` (`Coins`),
  PRIMARY KEY (`ID_User`)
) ENGINE=InnoDB;
