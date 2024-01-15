CREATE DATABASE dormyboba;

\c dormyboba;

CREATE TABLE "sent_token" (
    "sent_token_id" serial PRIMARY KEY,
    "token" varchar(384),
    "user_id" varchar(50)
);

CREATE TABLE "academic_type" (
  "type_id" integer PRIMARY KEY,
  "name" varchar(50)
);

CREATE TABLE "institute" (
  "institute_id" integer PRIMARY KEY,
  "name" varchar(50)
);

CREATE TABLE "user" (
  "user_id" integer PRIMARY KEY,
  "peer_id" integer UNIQUE,
  "role" integer,
  "academic_type_id" integer,
  "institute_id" integer,
  "year" integer,
  "group" varchar(5)
);

CREATE TABLE "role" (
  "role_id" integer PRIMARY KEY,
  "role_name" varchar(50)
);

CREATE TABLE "mailing" (
  "mailing_id" integer PRIMARY KEY,
  "theme" varchar(256),
  "mailing_text" text,
  "at" timestamp,
  "academic_type_id" integer,
  "institute_id" integer,
  "year" integer
);

CREATE TABLE "queue" (
  "queue_id" integer PRIMARY KEY,
  "conversation_id" integer,
  "name" varchar(256),
  "open" timestamp,
  "close" timestamp
);

CREATE TABLE "queue_to_user" (
  "user_id" integer,
  "queue_id" integer
);

ALTER TABLE "user" ADD FOREIGN KEY ("role") REFERENCES "role" ("role_id");

ALTER TABLE "user" ADD FOREIGN KEY ("academic_type_id") REFERENCES "academic_type" ("type_id");

ALTER TABLE "user" ADD FOREIGN KEY ("institute_id") REFERENCES "institute" ("institute_id");

ALTER TABLE "mailing" ADD FOREIGN KEY ("academic_type_id") REFERENCES "academic_type" ("type_id");

ALTER TABLE "mailing" ADD FOREIGN KEY ("institute_id") REFERENCES "institute" ("institute_id");

ALTER TABLE "queue_to_user" ADD FOREIGN KEY ("user_id") REFERENCES "user" ("user_id");

ALTER TABLE "queue_to_user" ADD FOREIGN KEY ("queue_id") REFERENCES "queue" ("queue_id");
