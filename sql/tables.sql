CREATE TABLE  protein (
    protein_id integer primary key autoincrement,
    phosphosite_id integer not null,
    name text not null
);

CREATE TABLE protein_fail (
    name text not null
);


CREATE TABLE site_name (
    site_name_id integer primary key autoincrement,
    name text not null
);

CREATE TABLE site_category (
    site_category_id integer primary key autoincrement,
    name text not null
);


CREATE TABLE site_success (
    phosphosite_id integer not null
);

CREATE TABLE site_fail (
    phosphosite_id integer not null
);


CREATE TABLE site (
    site_id integer primary key autoincrement,
    site_pid integer not null,
    site_category_id integer not null,
    site_name_id integer not null,
    phosphosite_id integer not null
);


CREATE TABLE control_category (
    control_category_id integer primary key autoincrement,
    name text not null
);

CREATE TABLE control_name (
    control_name_id integer primary key autoincrement,
    name text not null
);


CREATE TABLE control (
    phosphosite_id integer not null,
    control_category_id integer not null,
    control_name_id integer not null,
    controller integer not null
);

CREATE TABLE control_success (
    phosphosite_id integer not null
);

CREATE TABLE control_fail (
    phosphosite_id integer not null
);
