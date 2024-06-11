-- Create table for user_type
CREATE TABLE user_type (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NULL
);

-- Create table for user
CREATE TABLE user (
    username VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NULL,
    password_hash VARCHAR(255) NULL,
    user_type_id INTEGER NULL,
    FOREIGN KEY(user_type_id) REFERENCES user_type(id)
);

-- Create table for vehicle
CREATE TABLE vehicle (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(45) NULL,
    kennzeichen VARCHAR(45) NULL
);

-- Create table for job_status
CREATE TABLE job_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(45) NULL
);

-- Create table for job
CREATE TABLE job (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    auftragsnummer VARCHAR NULL,
    name VARCHAR NULL,
    adresse VARCHAR NULL,
    beschreibung VARCHAR NULL,
    status_id INTEGER,
    FOREIGN KEY(status_id) REFERENCES job_status(id)
);

-- Create table for timeentries
CREATE TABLE timeentries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time DATETIME NULL,
    end_time DATETIME NULL,
    pause_time INTEGER NULL,
    user_id VARCHAR(255),
    job_id INTEGER,
    FOREIGN KEY(user_id) REFERENCES user(username),
    FOREIGN KEY(job_id) REFERENCES job(id)
);

-- Create table for user_in_vehicle
CREATE TABLE user_in_vehicle (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    vehicle_id INTEGER,
    user_id VARCHAR(255),
    FOREIGN KEY(vehicle_id) REFERENCES vehicle(id),
    FOREIGN KEY(user_id) REFERENCES user(username)
);

-- Create table for bild
CREATE TABLE bild (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bild VARCHAR NULL,
    job_id INTEGER,
    FOREIGN KEY(job_id) REFERENCES job(id)
);
