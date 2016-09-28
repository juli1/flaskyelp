drop table if exists users;

create table users (
  user_id   integer primary key autoincrement,
  username  text not null,
  email     text not null,
  password  text not null
);


drop table if exists places;

create table places (
  place_id   integer primary key autoincrement,
  name  text not null,
  address     text not null,
  city       text not null,
  zipcode   integer
);


drop table if exists reviews;
create table reviews (
  review_id integer primary key autoincrement,
  rating integer,
  title text not null,
  message text not null,
  pub_date integer,
  user_id integer,
  place_id integer
);
