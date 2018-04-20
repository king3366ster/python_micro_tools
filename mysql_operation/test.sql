CREATE TABLE `wsw_404_log` (
  `id` int(20) NOT NULL AUTO_INCREMENT,
  `date` varchar(40) DEFAULT NULL,
  `ref` varchar(512) DEFAULT NULL,
  `url` varchar(512) DEFAULT NULL,
  `ip` varchar(40) DEFAULT NULL,
  `ua` varchar(512) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8;