BEGIN;
CREATE TABLE "sportsrec_member" (
    "id" integer NOT NULL PRIMARY KEY,
    "first_name" varchar(40) NOT NULL,
    "last_name" varchar(40) NOT NULL,
    "email" varchar(75) NOT NULL,
    "address" varchar(255),
    "facebook" varchar(40),
    "twitter" varchar(40),
    "phone" varchar(40),
    "interests" varchar(255),
    "owner_id" integer NOT NULL REFERENCES "auth_user" ("id")
)
;
CREATE TABLE "sportsrec_clubtag" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(40) NOT NULL UNIQUE
)
;
CREATE TABLE "sportsrec_clubtype" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(40) NOT NULL UNIQUE,
    "description" varchar(255) NOT NULL,
    "club_count" integer NOT NULL
)
;
CREATE TABLE "sportsrec_club_tags" (
    "id" integer NOT NULL PRIMARY KEY,
    "club_id" integer NOT NULL,
    "clubtag_id" integer NOT NULL REFERENCES "sportsrec_clubtag" ("id"),
    UNIQUE ("club_id", "clubtag_id")
)
;
CREATE TABLE "sportsrec_club" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(40) NOT NULL UNIQUE,
    "address" varchar(255) NOT NULL,
    "latitude" decimal,
    "longitude" decimal,
    "type_id" integer NOT NULL REFERENCES "sportsrec_clubtype" ("id"),
    "member_count" integer NOT NULL,
    "created" date NOT NULL,
    "recruiting" bool NOT NULL,
    "contact_id" integer REFERENCES "sportsrec_member" ("id"),
    "description" varchar(255) NOT NULL,
    "facebook" varchar(40),
    "twitter" varchar(40),
    "owner_id" integer REFERENCES "sportsrec_member" ("id")
)
;
CREATE TABLE "sportsrec_membership" (
    "id" integer NOT NULL PRIMARY KEY,
    "joined" date NOT NULL,
    "last_paid" date,
    "member_id" integer NOT NULL REFERENCES "sportsrec_member" ("id"),
    "club_id" integer NOT NULL REFERENCES "sportsrec_club" ("id"),
    UNIQUE ("member_id", "club_id")
)
;
CREATE TABLE "sportsrec_membershipapplication" (
    "id" integer NOT NULL PRIMARY KEY,
    "applied" date NOT NULL,
    "member_id" integer NOT NULL REFERENCES "sportsrec_member" ("id"),
    "club_id" integer NOT NULL REFERENCES "sportsrec_club" ("id"),
    "rejected" bool NOT NULL,
    UNIQUE ("member_id", "club_id")
)
;
CREATE INDEX "sportsrec_member_cb902d83" ON "sportsrec_member" ("owner_id");
CREATE INDEX "sportsrec_club_403d8ff3" ON "sportsrec_club" ("type_id");
CREATE INDEX "sportsrec_club_816533ed" ON "sportsrec_club" ("contact_id");
CREATE INDEX "sportsrec_club_cb902d83" ON "sportsrec_club" ("owner_id");
CREATE INDEX "sportsrec_membership_b3c09425" ON "sportsrec_membership" ("member_id");
CREATE INDEX "sportsrec_membership_887dd7e4" ON "sportsrec_membership" ("club_id");
CREATE INDEX "sportsrec_membershipapplication_b3c09425" ON "sportsrec_membershipapplication" ("member_id");
CREATE INDEX "sportsrec_membershipapplication_887dd7e4" ON "sportsrec_membershipapplication" ("club_id");

COMMIT;
