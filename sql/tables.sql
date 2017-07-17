CREATE TABLE  protein (
    protein_id integer primary key autoincrement,
    name text not null,
    phosposite_id integer,
    protein_status_id integer not null
);


CREATE TABLE protein_status (
    protein_status_id integer primary key autoincrement,
    name text not null
);


CREATE TABLE site_name (
    site_name_id integer primary key autoincrement,
    name text not null
);


CREATE TABLE site (
    site_id integer primary key autoincrement,
    site_name_id integer not null,
    phosphosite_id integer not null
);


CREATE TABLE control_name (
    control_name_id integer primary key autoincrement,
    name text not null
);


CREATE TABLE control (
    control_id integer primary key autoincrement,
    phosphosite_id integer not null,
    control_name_id integer not null,
    name text not null,
    controller integer not null
);
