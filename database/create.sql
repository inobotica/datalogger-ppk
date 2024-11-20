DROP TABLE datalogs;
DROP TABLE gis;

CREATE TABLE datalogs (    
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    filename VARCHAR,
    state BOOLEAN DEFAULT false
);

CREATE TABLE gis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    unix_time REAL,
    datalog_id INTEGER NOT NULL,
    photo VARCHAR, 
    lat REAL,
    lon REAL,
    pitch REAL,
    roll  REAL,
    FOREIGN KEY(datalog_id) REFERENCES datalogs(id)
);

INSERT INTO datalogs(state) VALUES (false);
INSERT INTO gis (datalog_id, photo, pitch, roll) VALUES (1, 'DCIM_0001.jpg', 45.0, 60.0);