create table User
(
  userid int primary key,
  username varchar(40) unique not null,
  password varchar(40) not null,
  contactid int,
  registered date not null,
  usertype int,
  foreign key(contactid) references Contact(contactid)
);

create table Contact
(
  contactid int primary key,
  --Consider moving lastname/firstname into the User/Member fields - doesn't make sense for Club
  lastname varchar(40) not null,
  firstname varchar(40) not null,
  email varchar(40) not null,
  facebook varchar(40),
  twitter varchar(40),
  phone varchar(40),
  fax varchar(40),
  address varchar(255)  
);

create table Member
(
  memberid int primary key,
  contactid int,
  clubid int,
  interests varchar(255),
  foreign key(clubid) references Club(clubid),
  foreign key(contactid) references Contact(contactid)
);

create table Club
(
  clubid int primary key,
  name varchar(40) unique not null,
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
  memberid int,
  clubid int,
  joineddate date not null,
  lastpaid date,
  foreign key(memberid) references Member(memberid),
  foreign key(clubid) references Club(clubid)
);
