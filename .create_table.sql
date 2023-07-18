
CREATE TABLE IF NOT EXISTS message (
	`created` TIMESTAMP,
	`id`      TEXT,
	`int_id`  CHAR(16) NOT NULL,
	`str`     TEXT,
	`status`  BOOL NOT NULL DEFAULT 0,											
	KEY message_id_pk (id(255)),
	KEY message_created_idx (`created`),
	KEY message_int_id_idx (`int_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1; 


CREATE TABLE IF NOT EXISTS log (
	`created` TIMESTAMP,
	`int_id`  CHAR(16) NOT NULL,
	`str`     TEXT,
	`address` TEXT,
	KEY log_address_idx (address(255))
) ENGINE=InnoDB DEFAULT CHARSET=latin1;



CREATE TABLE IF NOT EXISTS log_v2 (
	`n` int   NOT NULL AUTO_INCREMENT,
	`created` DATETIME     DEFAULT '0000-00-00 00:00:00',
	`id`      VARCHAR(128) DEFAULT '',
	`int_id`  CHAR(16)     DEFAULT '',
	`address` VARCHAR(320) DEFAULT '',
	`flag`    CHAR(2)      DEFAULT '',
	`str`     VARCHAR(512) DEFAULT '',
	`status`  BOOL         DEFAULT '0',											
	PRIMARY KEY (n),
	KEY (`id`),
	KEY (`int_id`),
	KEY (`created`),
	KEY (`address`),
	KEY (`flag`),
	KEY (`status`)
) 	ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=latin1; 


