--triggers, just for you, just *because*

DROP TRIGGER IF EXISTS MembershipCreated;
DROP TRIGGER IF EXISTS MembershipDeleted;

CREATE TRIGGER MembershipCreated
AFTER INSERT ON sportsrec_membership
FOR EACH ROW
BEGIN
UPDATE sportsrec_club
SET member_count=member_count+1
WHERE id=New.club_id;
END;

CREATE TRIGGER MembershipDeleted
AFTER DELETE ON sportsrec_membership
FOR EACH ROW
BEGIN
UPDATE sportsrec_club
SET member_count=member_count-1
WHERE id=Old.club_id;

UPDATE sportsrec_club
SET owner_id=NULL
WHERE id=Old.club_id AND owner_id=Old.member_id;

UPDATE sportsrec_club
SET contact_id=NULL
WHERE id=Old.club_id AND contact_id=Old.member_id;
END;