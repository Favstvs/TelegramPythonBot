DROP TABLE IF EXISTS `htrade`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `htrade` (
  `ID_Supergruppo` bigint NOT NULL,
  `Mess_ID_Trade` bigint NOT NULL,
  `ID_User_1` bigint NOT NULL,
  `ID_User_2` bigint NOT NULL,
  `Scambio_1` int NOT NULL,
  `Scambio_2` int NOT NULL,
  PRIMARY KEY (`ID_Supergruppo`,`Mess_ID_Trade`),
  KEY `ID_User_1` (`ID_User_1`),
  KEY `ID_User_2` (`ID_User_2`),
  KEY `Scambio_1` (`Scambio_1`),
  KEY `Scambio_2` (`Scambio_2`),
  CONSTRAINT `scambio_ibfk_1` FOREIGN KEY (`ID_User_1`) REFERENCES `users` (`ID_User`),
  CONSTRAINT `scambio_ibfk_2` FOREIGN KEY (`ID_User_2`) REFERENCES `users` (`ID_User`),
  CONSTRAINT `scambio_ibfk_3` FOREIGN KEY (`ID_Supergruppo`) REFERENCES `supergruppo` (`ID_Supergruppo`),
  CONSTRAINT `scambio_ibfk_4` FOREIGN KEY (`Scambio_1`) REFERENCES `husbando` (`ID_Husbando`),
  CONSTRAINT `scambio_ibfk_5` FOREIGN KEY (`Scambio_2`) REFERENCES `husbando` (`ID_Husbando`)
) ENGINE=InnoDB;
