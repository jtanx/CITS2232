BEGIN;
CREATE TABLE "sportsrec_contact" (
    "id" integer NOT NULL PRIMARY KEY,
    "email" varchar(40) NOT NULL,
    "address" varchar(255),
    "facebook" varchar(40),
    "twitter" varchar(40),
    "phone" varchar(40),
    "fax" varchar(40)
)
;
CREATE TABLE "sportsrec_user" (
    "id" integer NOT NULL PRIMARY KEY,
    "username" varchar(40) NOT NULL UNIQUE,
    "password" varchar(40) NOT NULL,
    "lastname" varchar(40),
    "firstname" varchar(40),
    "registered" date NOT NULL,
    "usertype" integer NOT NULL,
    "contact_id" integer NOT NULL REFERENCES "sportsrec_contact" ("id")
)
;
CREATE TABLE "sportsrec_member" (
    "id" integer NOT NULL PRIMARY KEY,
    "lastname" varchar(40) NOT NULL,
    "firstname" varchar(40) NOT NULL,
    "interests" varchar(255),
    "owner_id" integer NOT NULL REFERENCES "sportsrec_user" ("id"),
    "contact_id" integer NOT NULL REFERENCES "sportsrec_contact" ("id")
)
;
CREATE TABLE "sportsrec_club" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(40) NOT NULL UNIQUE,
    "type" varchar(40),
    "location" varchar(40),
    "membercount" integer NOT NULL,
    "created" date NOT NULL,
    "recruiting" bool NOT NULL,
    "description" varchar(255),
    "owner_id" integer NOT NULL REFERENCES "sportsrec_user" ("id"),
    "contact_id" integer NOT NULL REFERENCES "sportsrec_contact" ("id")
)
;
CREATE TABLE "sportsrec_membership" (
    "id" integer NOT NULL PRIMARY KEY,
    "joined" date NOT NULL,
    "lastpaid" date,
    "member_id" integer NOT NULL REFERENCES "sportsrec_member" ("id"),
    "club_id" integer NOT NULL REFERENCES "sportsrec_club" ("id")
)
;
CREATE INDEX "sportsrec_user_816533ed" ON "sportsrec_user" ("contact_id");
CREATE INDEX "sportsrec_member_cb902d83" ON "sportsrec_member" ("owner_id");
CREATE INDEX "sportsrec_member_816533ed" ON "sportsrec_member" ("contact_id");
CREATE INDEX "sportsrec_club_cb902d83" ON "sportsrec_club" ("owner_id");
CREATE INDEX "sportsrec_club_816533ed" ON "sportsrec_club" ("contact_id");
CREATE INDEX "sportsrec_membership_b3c09425" ON "sportsrec_membership" ("member_id");
CREATE INDEX "sportsrec_membership_887dd7e4" ON "sportsrec_membership" ("club_id");

COMMIT;
