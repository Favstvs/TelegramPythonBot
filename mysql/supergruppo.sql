DROP TABLE IF EXISTS `supergruppo`;

CREATE TABLE `supergruppo` (
  `ID_Supergruppo` bigint NOT NULL,
  `Supergruppo_nome` varchar(128) NOT NULL,
  PRIMARY KEY (`ID_Supergruppo`)
) ENGINE=InnoDB;
