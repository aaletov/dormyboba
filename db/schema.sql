CREATE DATABASE dormyboba;

\c dormyboba;

CREATE TABLE "sent_token" (
    "sent_token_id" serial PRIMARY KEY,
    "token" varchar(1024) UNIQUE,
    "user_id" integer UNIQUE
);

CREATE TABLE "academic_type" (
  "type_id" integer PRIMARY KEY,
  "type_name" varchar(50)
);

CREATE TABLE "institute" (
  "institute_id" integer PRIMARY KEY,
  "institute_name" varchar(50)
);

CREATE TABLE "dormyboba_role" (
  "role_id" serial PRIMARY KEY,
  "role_name" varchar(50) UNIQUE
);

CREATE TABLE "dormyboba_user" (
  "user_id" integer PRIMARY KEY,
  "peer_id" integer UNIQUE,
  "role_id" integer REFERENCES "dormyboba_role" ("role_id"),
  "academic_type_id" integer REFERENCES "academic_type" ("type_id"),
  "institute_id" integer REFERENCES "institute" ("institute_id"),
  "year" integer,
  "group" varchar(5)
);

CREATE TABLE "mailing" (
  "mailing_id" serial PRIMARY KEY,
  "theme" varchar(256),
  "mailing_text" text,
  "at" timestamp,
  "academic_type_id" integer REFERENCES "academic_type" ("type_id"),
  "institute_id" integer REFERENCES "institute" ("institute_id"),
  "year" integer
);

CREATE TABLE "queue" (
  "queue_id" serial PRIMARY KEY,
  "conversation_id" integer,
  "name" varchar(256),
  "open" timestamp,
  "close" timestamp
);

CREATE TABLE "queue_to_user" (
  "user_id" integer REFERENCES "dormyboba_user" ("user_id"),
  "queue_id" integer REFERENCES "queue" ("queue_id"),
  PRIMARY KEY ("user_id", "queue_id")
);


