DROP TABLE IF EXISTS `users`;

CREATE TABLE `users` (
  `ID_User` bigint NOT NULL,
  `Username` varchar(36) NOT NULL,
  PRIMARY KEY (`ID_User`)
) ENGINE=InnoDB;
