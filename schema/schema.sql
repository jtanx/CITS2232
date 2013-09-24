--This was manually created. Correct?? Dunno

create table User
(
  userid int primary key not null,
  username varchar(40) unique not null,
  password varchar(40) not null,
  lastname varchar(40),
  firstname varchar(40),
  contactid int not null,
  registered date not null,
  usertype int not null,
  foreign key(contactid) references Contact(contactid)
);

create table Contact
(
  contactid int primary key not null,
  email varchar(40) not null,
  address varchar(255),
  facebook varchar(40),
  twitter varchar(40),
  phone varchar(40),
  fax varchar(40)
);

create table Member
(
  memberid int primary key not null,
  lastname varchar(40) not null,
  firstname varchar(40) not null,
  contactid int not null,
  ownerid int not null, --User that created this member
  interests varchar(255),
  foreign key(ownerid) references User(userid),
  foreign key(contactid) references Contact(contactid)
);

create table Club
(
  clubid int primary key,
  name varchar(100) unique not null,
  type varchar(40),
  location varchar(100),
  membercount int,
  recruiting boolean,
  description varchar(255),
  contactid int,
  ownerid int,
  foreign key(ownerid) references User(userid),
  foreign key(contactid) references Contact(contactid)
);

create table Membership
(
  memberid int not null,
  clubid int not null,
  joineddate date not null,
  lastpaid date,
  foreign key(memberid) references Member(memberid),
  foreign key(clubid) references Club(clubid)
);
