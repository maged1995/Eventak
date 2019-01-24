  create database Eventak;

  create table users(
    id int not null auto_increment, email varchar(40) not null,
    username varchar(24), passwordHash varchar(32) not null,
    birthDate date, unique(email), unique(username),
    constraint chk_email check(email like '%_@__%.__%'),
    primary key(id)
  );

  create table events(
    id int not null auto_increment, name varchar(50) not null,
    locLong varchar(10) not null, locLat varchar(10) not null,
    CreatorID int not null, day date, primary key(id)
  );

  create table eventTypes(
    id int not null auto_increment, name varchar(15), primary key(id)
  );

  create table event_type(
    event int not null, type int not null,
    FOREIGN KEY (event) REFERENCES events(id),
    FOREIGN KEY (type) REFERENCES eventTypes(id)
  );
