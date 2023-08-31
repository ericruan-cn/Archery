-- MySQL dump 10.13  Distrib 5.7.16, for osx10.11 (x86_64)
--
-- Host: 127.0.0.1    Database: archery
-- ------------------------------------------------------
-- Server version	5.7.16-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Dumping data for table `host_conf_business`
--

/*!40000 ALTER TABLE `host_conf_business` DISABLE KEYS */;
INSERT INTO `host_conf_business` VALUES (1,'环球云-生产'),(2,'云商城-生产'),(3,'悦家繁荣-生产'),(4,'环球云-测试'),(5,'云商城-测试'),(6,'悦家繁荣-测试');
/*!40000 ALTER TABLE `host_conf_business` ENABLE KEYS */;

--
-- Dumping data for table `host_conf_dbtype`
--

/*!40000 ALTER TABLE `host_conf_dbtype` DISABLE KEYS */;
INSERT INTO `host_conf_dbtype` VALUES (10,'oracle'),(20,'mysql'),(30,'postgresql'),(40,'tidb'),(50,'mssql');
/*!40000 ALTER TABLE `host_conf_dbtype` ENABLE KEYS */;

--
-- Dumping data for table `host_conf_hostspec`
--

/*!40000 ALTER TABLE `host_conf_hostspec` DISABLE KEYS */;
INSERT INTO `host_conf_hostspec` VALUES (11,'2C / 4G / 300G'),(21,'4C / 8G / 300G'),(22,'4C / 8G / 500G'),(23,'4C / 8G /1000G'),(31,'8C /16G / 500G'),(32,'8C /16G /1000G'),(36,'8C /32G /2048G'),(41,'16C/32G / 500G'),(42,'16C/32G /1000G'),(51,'16C/64G / 500G'),(52,'16C/64G /1000G'),(55,'24C/128G/26T'),(61,'32C/64G / 500G'),(62,'32C/64G /1000G'),(63,'32C/64G /1500G');
/*!40000 ALTER TABLE `host_conf_hostspec` ENABLE KEYS */;

--
-- Dumping data for table `host_conf_hoststat`
--

/*!40000 ALTER TABLE `host_conf_hoststat` DISABLE KEYS */;
INSERT INTO `host_conf_hoststat` VALUES (10,'初创建'),(20,'已上线'),(30,'已下线'),(40,'已回收');
/*!40000 ALTER TABLE `host_conf_hoststat` ENABLE KEYS */;

--
-- Dumping data for table `host_conf_hosttype`
--

/*!40000 ALTER TABLE `host_conf_hosttype` DISABLE KEYS */;
INSERT INTO `host_conf_hosttype` VALUES (10,'PHY'),(20,'VM'),(30,'ECS'),(40,'RDS');
/*!40000 ALTER TABLE `host_conf_hosttype` ENABLE KEYS */;

--
-- Dumping data for table `host_conf_machroom`
--

/*!40000 ALTER TABLE `host_conf_machroom` DISABLE KEYS */;
INSERT INTO `host_conf_machroom` VALUES (1,'老楼机房','聚鲨环球精选-老楼机房',3),(2,'新楼机房','聚鲨环球精选-新楼机房',3),(3,'世纪互联M5','世纪互联M5机房',3),(4,'世纪互联M6','世纪互联M6机房',3),(5,'AliyunCloud','阿里云Cloud',3),(6,'AzureCloud','微软云Cloud',3);
/*!40000 ALTER TABLE `host_conf_machroom` ENABLE KEYS */;

--
-- Dumping data for table `host_conf_ostype`
--

/*!40000 ALTER TABLE `host_conf_ostype` DISABLE KEYS */;
INSERT INTO `host_conf_ostype` VALUES (11,'RedHat6','RedHat Enterprise Linux 6 x86 64bit'),(12,'RedHat7','RedHat Enterprise Linux 7 x86 64bit'),(13,'RedHat8','RedHat Enterprise Linux 8 x86 64bit'),(21,'CentOS6','CentOS Enterprise Linux 6 x86 64bit'),(22,'CentOS7','CentOS Enterprise Linux 7 x86 64bit'),(23,'CentOS8','CentOS Enterprise Linux 8 x86 64bit'),(31,'Ubuntu16','Ubuntu16 Server LTS x86 64bit'),(32,'Ubuntu18','Ubuntu18 Server LTS x86 64bit'),(33,'Ubuntu20','Ubuntu20 Server LTS x86 64bit'),(34,'Ubuntu22','Ubuntu20 Server LTS x86 64bit'),(40,'SUSE11','SUSE Linux Enterprise Server 11 SP1'),(41,'SUSE12','SUSE Linux Enterprise Server 12 SP5'),(86,'OPENFILER','Openfiler ESA, version 2.99.1'),(91,'Windows','Windows Server');
/*!40000 ALTER TABLE `host_conf_ostype` ENABLE KEYS */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-08-31 15:20:46
