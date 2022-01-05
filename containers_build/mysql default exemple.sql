
/*!40030 SET NAMES UTF8 */;
/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

DROP SCHEMA IF EXISTS `sakila` ;

CREATE SCHEMA IF NOT EXISTS `sakila` ;
USE `sakila` ;

CREATE TABLE IF NOT EXISTS `actor` (
  `actor_id` SERIAL,
  `first_name` VARCHAR(45) NOT NULL,
  `last_name` VARCHAR(45) NOT NULL,
  `last_update` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`actor_id`)
  )ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS `country` (
  `country_id` SERIAL ,
  `country` VARCHAR(50) NOT NULL,
  `last_update` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`country_id`))ENGINE=InnoDB;

DROP TABLE IF EXISTS `city` CASCADE;

CREATE TABLE IF NOT EXISTS `city` (
  `city_id` SERIAL ,
  `city` VARCHAR(50) NOT NULL,
  `country_id` BIGINT unsigned NOT NULL,
  `last_update` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`city_id`)
  )ENGINE=InnoDB;
 
ALTER TABLE sakila.city ADD CONSTRAINT `fk_city_country` FOREIGN KEY(country_id) REFERENCES sakila.country(country_id) ON UPDATE CASCADE;

CREATE TABLE IF NOT EXISTS `address` (
  `address_id` SERIAL ,
  `address` VARCHAR(50) NOT NULL,
  `address2` VARCHAR(50) NULL DEFAULT NULL,
  `district` varchar(50) NOT NULL,
  `city_id` BIGINT unsigned NOT NULL,
  `postal_code` VARCHAR(10) NULL DEFAULT NULL,
  `phone` VARCHAR(20) NOT NULL,
  `last_update` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`address_id`))ENGINE=InnoDB;

ALTER TABLE `address` ADD CONSTRAINT `fk_address_city` FOREIGN KEY (`city_id`) REFERENCES `city` (`city_id`) ON UPDATE CASCADE;


CREATE TABLE IF NOT EXISTS `category` (
  `category_id` SERIAL ,
  `name` VARCHAR(25) NOT NULL,
  `last_update` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`category_id`))ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS `staff` (
  `staff_id` SERIAL ,
  `first_name` VARCHAR(45) NOT NULL,
  `last_name` VARCHAR(45) NOT NULL,
  `address_id` BIGINT unsigned NOT NULL,
  `email` VARCHAR(50) NULL DEFAULT NULL,
  `store_id` BIGINT unsigned NOT NULL,
  `active` smallint NOT NULL DEFAULT TRUE,
  `username` VARCHAR(30) NOT NULL,
  `password` VARCHAR(40) BINARY NULL DEFAULT NULL,
  `last_update` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`staff_id`))ENGINE=InnoDB;

 
 ALTER TABLE `staff` ADD CONSTRAINT `fk_staff_address` FOREIGN KEY (`address_id`) REFERENCES `address` (`address_id`) ON UPDATE CASCADE;


CREATE TABLE IF NOT EXISTS `store` (
  `store_id` SERIAL,
  `manager_staff_id` BIGINT unsigned ,
  `address_id` BIGINT unsigned NOT NULL,
  `last_update` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`store_id`))ENGINE=InnoDB;

ALTER TABLE `store` ADD CONSTRAINT  `idx_unique_manager` FOREIGN KEY (`manager_staff_id`) REFERENCES `staff` (`staff_id`) ON UPDATE CASCADE;
ALTER TABLE `store` ADD CONSTRAINT `fk_store_address` FOREIGN KEY (`address_id`) REFERENCES `address` (`address_id`) ON UPDATE CASCADE;
ALTER TABLE `store` ADD CONSTRAINT `fk_store_staff` FOREIGN KEY (`manager_staff_id`) REFERENCES `staff` (`staff_id`) ON UPDATE CASCADE;
ALTER TABLE `staff` ADD CONSTRAINT `fk_staff_store` FOREIGN KEY (`store_id`) REFERENCES `store` (`store_id`) ON UPDATE CASCADE;



CREATE TABLE IF NOT EXISTS `customer` (
  `customer_id` SERIAL,
  `store_id` BIGINT unsigned NOT NULL,
  `first_name` VARCHAR(45) NOT NULL,
  `last_name` VARCHAR(45) NOT NULL,
  `email` VARCHAR(50) NULL DEFAULT NULL,
  `address_id` BIGINT unsigned NOT NULL,
  `active` smallint(1) NOT NULL DEFAULT TRUE,
  `create_date` DATETIME NOT NULL,
  `last_update` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`customer_id`))ENGINE=InnoDB;
ALTER TABLE `customer` ADD CONSTRAINT `fk_customer_address` FOREIGN KEY (`address_id`) REFERENCES `address` (`address_id`) ON UPDATE CASCADE;
ALTER TABLE `customer` ADD CONSTRAINT `fk_customer_store` FOREIGN KEY (`store_id`) REFERENCES `store` (`store_id`) ON UPDATE CASCADE;



CREATE TABLE IF NOT EXISTS `language` (
  `language_id` SERIAL,
  `name` CHAR(20) NOT NULL,
  `last_update` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`language_id`))ENGINE=InnoDB;



CREATE TABLE IF NOT EXISTS `film` (
  `film_id` SERIAL,
  `title` VARCHAR(255) NOT NULL,
  `description` TEXT NULL,
  `release_year` YEAR NULL,
  `language_id` BIGINT unsigned NOT NULL,
  `original_language_id` BIGINT unsigned NOT NULL,
  `rental_duration` smallint UNSIGNED NOT NULL DEFAULT 3,
  `length` SMALLINT UNSIGNED NULL DEFAULT NULL,
  `rating` ENUM('G','PG','PG-13','R','NC-17') NULL DEFAULT 'G',
  `special_features` ENUM('Trailers','Commentaries','Deleted Scenes','Behind the Scenes') NULL,
  `last_update` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`film_id`))ENGINE=InnoDB;
ALTER TABLE `film` ADD CONSTRAINT `fk_film_language` FOREIGN KEY (`language_id`) REFERENCES `language` (`language_id`) ON UPDATE CASCADE;
ALTER TABLE `film` ADD CONSTRAINT `fk_film_language_original` FOREIGN KEY (`original_language_id`) REFERENCES `language` (`language_id`) ON UPDATE CASCADE;


CREATE TABLE IF NOT EXISTS `film_actor` (
  `actor_id` BIGINT unsigned NOT NULL ,
  `film_id` BIGINT unsigned NOT NULL ,
  `last_update` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)ENGINE=InnoDB;
--  PRIMARY KEY (`actor_id`, `film_id`))ENGINE=InnoDB;
ALTER TABLE `film_actor` ADD CONSTRAINT `fk_film_actor_actor` FOREIGN KEY (`actor_id`) REFERENCES `actor` (`actor_id`) ON UPDATE CASCADE;
ALTER TABLE `film_actor` ADD CONSTRAINT `fk_film_actor_film` FOREIGN KEY (`film_id`) REFERENCES `film` (`film_id`) ON UPDATE CASCADE;



CREATE TABLE IF NOT EXISTS `film_category` (
  `film_id` BIGINT unsigned NOT NULL,
  `category_id` BIGINT unsigned NOT NULL,
  `last_update` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)ENGINE=InnoDB;
 -- PRIMARY KEY (`film_id`, `category_id`))ENGINE=InnoDB;
ALTER TABLE `film_category` ADD CONSTRAINT `fk_film_category_category` FOREIGN KEY (`category_id`) REFERENCES `category` (`category_id`) ON UPDATE CASCADE;
ALTER TABLE `film_category` ADD CONSTRAINT `fk_film_category_film` FOREIGN KEY (`film_id`) REFERENCES `film` (`film_id`) ON UPDATE CASCADE;


CREATE TABLE IF NOT EXISTS `inventory` (
  `inventory_id` SERIAL,
  `film_id` BIGINT unsigned NOT NULL,
  `store_id` BIGINT unsigned NOT NULL,
  `last_update` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`inventory_id`))ENGINE=InnoDB;
ALTER TABLE `inventory` ADD CONSTRAINT `fk_inventory_film` FOREIGN KEY (`film_id`) REFERENCES `film` (`film_id`) ON UPDATE CASCADE;
ALTER TABLE `inventory` ADD CONSTRAINT `fk_inventory_store` FOREIGN KEY (`store_id`) REFERENCES `store` (`store_id`) ON UPDATE CASCADE;



CREATE TABLE IF NOT EXISTS `rental` (
  `rental_id` SERIAL,
  `rental_date` DATETIME NOT NULL,
  `inventory_id` BIGINT unsigned NOT NULL,
  `customer_id` BIGINT unsigned NOT NULL,
  `return_date` DATETIME NULL,
  `staff_id` BIGINT unsigned NOT NULL,
  `last_update` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`rental_id`))ENGINE=InnoDB;
ALTER TABLE `rental` ADD CONSTRAINT `fk_rental_customer` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`customer_id`) ON UPDATE CASCADE;
ALTER TABLE `rental` ADD CONSTRAINT `fk_rental_inventory` FOREIGN KEY (`inventory_id`) REFERENCES `inventory` (`inventory_id`) ON UPDATE CASCADE;
ALTER TABLE `rental` ADD CONSTRAINT `fk_rental_staff` FOREIGN KEY (`staff_id`) REFERENCES `staff` (`staff_id`) ON UPDATE CASCADE;



CREATE TABLE IF NOT EXISTS `payment` (
  `payment_id` SERIAL,
  `customer_id` BIGINT unsigned NOT NULL,
  `staff_id` BIGINT unsigned NOT NULL,
  `rental_id` BIGINT unsigned NOT NULL,
  `amount` DECIMAL(5,2) NOT NULL,
  `payment_date` DATETIME NOT NULL,
  `last_update` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`payment_id`))ENGINE=InnoDB;
ALTER TABLE `payment` ADD CONSTRAINT `fk_payment_customer` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`customer_id`) ON UPDATE CASCADE;
ALTER TABLE `payment` ADD CONSTRAINT `fk_payment_staff` FOREIGN KEY (`staff_id`) REFERENCES `staff` (`staff_id`) ON UPDATE CASCADE;


