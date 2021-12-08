
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

DROP TABLE IF EXISTS "actor" CASCADE;


CREATE TABLE "actor" (
  "actor_id" BIGSERIAL,
  "first_nome" varchar(45) NOT NULL,
  "last_nome" varchar(45) NOT NULL,
  "last_update" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("actor_id") 
);


DROP TABLE IF EXISTS "country" CASCADE;

CREATE TABLE "country" (
  "country_id" BIGSERIAL,
  "country" varchar(50) NOT NULL,
  "last_update" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("country_id")
);

DROP TABLE IF EXISTS "city" CASCADE;

CREATE TABLE "city" (
  "city_id" BIGSERIAL,
  "city" varchar(50) NOT NULL,
  "country_id" BIGINT ,
  "last_update" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("city_id")   
);

ALTER TABLE "city" ADD CONSTRAINT "fk_city_country" FOREIGN KEY ("country_id") REFERENCES "country" ("country_id") ON UPDATE CASCADE;


DROP TABLE IF EXISTS "address" CASCADE;

CREATE TABLE "address" (
  "address_id" BIGSERIAL,
  "address" varchar(50) NOT NULL,
  "address2" varchar(50) DEFAULT NULL,
  "district" varchar(20) NOT NULL,
  "city_id" BIGINT ,
  "postal_code" varchar(10) DEFAULT NULL,
  "phone" varchar(20) NOT NULL,
  "last_update" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("address_id") 
);

ALTER TABLE "address" ADD CONSTRAINT "fk_address_city" FOREIGN KEY ("city_id") REFERENCES "city" ("city_id") ON UPDATE CASCADE;


DROP TABLE IF EXISTS "category" CASCADE;

CREATE TABLE "category" (
  "category_id" BIGSERIAL,
  "nome" varchar(25) NOT NULL,
  "last_update" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("category_id")
);


DROP TABLE IF EXISTS "staff" CASCADE;

CREATE TABLE "staff" (
  "staff_id" BIGSERIAL,
  "first_nome" varchar(45) NOT NULL,
  "last_nome" varchar(45) NOT NULL,
  "address_id" BIGINT ,
  "picture" bytea NULL,
  "email" varchar(50) DEFAULT NULL,
  "store_id" BIGINT ,
  "active" smallint NOT NULL DEFAULT '1',
  "username" varchar(16) NOT NULL,
  "password" varchar(40) DEFAULT NULL,
  "last_update" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("staff_id")  
  
);


ALTER TABLE "staff" ADD CONSTRAINT "fk_staff_address" FOREIGN KEY ("address_id") REFERENCES "address" ("address_id") ON UPDATE CASCADE;

DROP TABLE IF EXISTS "store" CASCADE;

CREATE TABLE "store" (
  "store_id" BIGSERIAL,
  "manager_staff_id" smallint UNIQUE NOT NULL,
  "address_id" BIGINT ,
  "last_update" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("store_id")
);


ALTER TABLE "store" ADD CONSTRAINT  "idx_unique_manager" FOREIGN KEY ("manager_staff_id") REFERENCES "staff" ("staff_id") ON UPDATE CASCADE;
ALTER TABLE "store" ADD CONSTRAINT "fk_store_address" FOREIGN KEY ("address_id") REFERENCES "address" ("address_id") ON UPDATE CASCADE;
ALTER TABLE "store" ADD CONSTRAINT "fk_store_staff" FOREIGN KEY ("manager_staff_id") REFERENCES "staff" ("staff_id") ON UPDATE CASCADE;
ALTER TABLE "staff" ADD CONSTRAINT "fk_staff_store" FOREIGN KEY ("store_id") REFERENCES "store" ("store_id") ON UPDATE CASCADE;

DROP TABLE IF EXISTS "customer" CASCADE;

CREATE TABLE "customer" (
  "customer_id" BIGSERIAL,
  "store_id" BIGINT ,
  "first_nome" varchar(45) NOT NULL,
  "last_nome" varchar(45) NOT NULL,
  "email" varchar(50) DEFAULT NULL,
  "address_id" BIGINT ,
  "active" smallint NOT NULL DEFAULT '1',
  "create_date" timestamp NOT NULL,
  "last_update" timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("customer_id") 
  
);

ALTER TABLE "customer" ADD CONSTRAINT "fk_customer_address" FOREIGN KEY ("address_id") REFERENCES "address" ("address_id") ON UPDATE CASCADE;
ALTER TABLE "customer" ADD CONSTRAINT "fk_customer_store" FOREIGN KEY ("store_id") REFERENCES "store" ("store_id") ON UPDATE CASCADE;


DROP TABLE IF EXISTS "film" CASCADE;

DROP TYPE IF EXISTS rating;
CREATE TYPE rating AS enum('G','PG','PG-13','R','NC-17');
DROP TYPE IF EXISTS special_features;
CREATE TYPE special_features AS enum('Trailers','Commentaries','Deleted Scenes','Behind the Scenes');

CREATE TABLE "film" (
  "film_id" BIGSERIAL,
  "title" varchar(255) NOT NULL,
  "description" text,
  "release_year" date DEFAULT NULL,
  "language_id" BIGINT ,
  "original_language_id" BIGINT ,
  "rental_duration" INTEGER DEFAULT '3',
  "rental_rate" decimal(4,2) NOT NULL DEFAULT '4.99',
  "length" smallint   DEFAULT NULL,
  "replacement_cost" decimal(5,2) NOT NULL DEFAULT '19.99',
  "rating" rating DEFAULT 'G',
  "special_features" special_features DEFAULT NULL,
  "last_update" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("film_id")   
  
);



DROP TABLE IF EXISTS "film_actor" CASCADE;

CREATE TABLE "film_actor" (
  "actor_id" BIGINT ,
  "film_id" BIGINT ,
  "last_update" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("actor_id","film_id")  
  
);
ALTER TABLE "film_actor" ADD CONSTRAINT "fk_film_actor_actor" FOREIGN KEY ("actor_id") REFERENCES "actor" ("actor_id") ON UPDATE CASCADE;
ALTER TABLE "film_actor" ADD CONSTRAINT "fk_film_actor_film" FOREIGN KEY ("film_id") REFERENCES "film" ("film_id") ON UPDATE CASCADE;

DROP TABLE IF EXISTS "film_category" CASCADE;

CREATE TABLE "film_category" (
  "film_id" BIGSERIAL,
  "category_id" BIGSERIAL,
  "last_update" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("film_id","category_id")  
  
);
ALTER TABLE "film_category" ADD CONSTRAINT "fk_film_category_category" FOREIGN KEY ("category_id") REFERENCES "category" ("category_id") ON UPDATE CASCADE;
ALTER TABLE "film_category" ADD CONSTRAINT "fk_film_category_film" FOREIGN KEY ("film_id") REFERENCES "film" ("film_id") ON UPDATE CASCADE;


DROP TABLE IF EXISTS "inventory" CASCADE;


CREATE TABLE "inventory" (
  "inventory_id" BIGSERIAL,
  "film_id" BIGINT ,
  "store_id" BIGINT ,
  "last_update" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("inventory_id")   
  
);
ALTER TABLE "inventory" ADD CONSTRAINT "fk_inventory_film" FOREIGN KEY ("film_id") REFERENCES "film" ("film_id") ON UPDATE CASCADE;
ALTER TABLE "inventory" ADD CONSTRAINT "fk_inventory_store" FOREIGN KEY ("store_id") REFERENCES "store" ("store_id") ON UPDATE CASCADE;


DROP TABLE IF EXISTS "language" CASCADE;


CREATE TABLE "language" (
  "language_id" BIGSERIAL,
  "nome" char(20) NOT NULL,
  "last_update" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("language_id")
);
ALTER TABLE "film" ADD CONSTRAINT "fk_film_language" FOREIGN KEY ("language_id") REFERENCES "language" ("language_id") ON UPDATE CASCADE;
ALTER TABLE "film" ADD CONSTRAINT "fk_film_language_original" FOREIGN KEY ("original_language_id") REFERENCES "language" ("language_id") ON UPDATE CASCADE;


DROP TABLE IF EXISTS "payment" CASCADE;


CREATE TABLE "payment" (
  "payment_id" BIGSERIAL,
  "customer_id" BIGINT,
  "staff_id" BIGINT,
  "rental_id" int DEFAULT NULL,
  "amount" decimal(5,2) NOT NULL,
  "payment_date" timestamp NOT NULL,
  "last_update" timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("payment_id")   
  
);
ALTER TABLE "payment" ADD CONSTRAINT "fk_payment_customer" FOREIGN KEY ("customer_id") REFERENCES "customer" ("customer_id") ON UPDATE CASCADE;
ALTER TABLE "payment" ADD CONSTRAINT "fk_payment_staff" FOREIGN KEY ("staff_id") REFERENCES "staff" ("staff_id") ON UPDATE CASCADE;


DROP TABLE IF EXISTS "rental" CASCADE;


CREATE TABLE "rental" (
  "rental_id" BIGSERIAL,
  "rental_date" timestamp  NOT NULL,
  "inventory_id" BIGINT NOT NULL,
  "customer_id" BIGINT ,
  "return_date" timestamp  DEFAULT NULL,
  "staff_id" BIGINT ,
  "last_update" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("rental_id")  
);
ALTER TABLE "payment" ADD CONSTRAINT "fk_payment_rental" FOREIGN KEY ("rental_id") REFERENCES "rental" ("rental_id") ON DELETE SET NULL ON UPDATE CASCADE;

ALTER TABLE "rental" ADD CONSTRAINT "fk_rental_customer" FOREIGN KEY ("customer_id") REFERENCES "customer" ("customer_id") ON UPDATE CASCADE;
ALTER TABLE "rental" ADD CONSTRAINT "fk_rental_inventory" FOREIGN KEY ("inventory_id") REFERENCES "inventory" ("inventory_id") ON UPDATE CASCADE;
ALTER TABLE "rental" ADD CONSTRAINT "fk_rental_staff" FOREIGN KEY ("staff_id") REFERENCES "staff" ("staff_id") ON UPDATE CASCADE;

