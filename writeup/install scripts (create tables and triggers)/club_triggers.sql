--triggers, just for you, just *because*

DROP TRIGGER IF EXISTS ClubCreated;
DROP TRIGGER IF EXISTS ClubUpdated;
DROP TRIGGER IF EXISTS ClubDeleted;

CREATE TRIGGER ClubCreated
AFTER INSERT ON sportsrec_club
FOR EACH ROW
BEGIN
UPDATE sportsrec_clubtype
SET club_count=club_count+1
WHERE id=New.type_id;
END;

--triggers can't be combined because of django's piss sql parser
--https://code.djangoproject.com/ticket/4374
CREATE TRIGGER ClubUpdated
AFTER UPDATE OF type_id ON sportsrec_club 
FOR EACH ROW
BEGIN
UPDATE sportsrec_clubtype
SET club_count=club_count+1
WHERE id=New.type_id;

UPDATE sportsrec_clubtype
SET club_count=club_count-1
WHERE id=Old.type_id;
END;

CREATE TRIGGER ClubDeleted
AFTER DELETE ON sportsrec_club
FOR EACH ROW
BEGIN
UPDATE sportsrec_clubtype
SET club_count=club_count-1
WHERE id=Old.type_id;
END;

--no signal for you!