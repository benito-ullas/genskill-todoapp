DROP TABLE IF EXISTS data;
DROP TABLE IF EXISTS users;

CREATE TABLE USERS (
id SERIAL PRIMARY KEY,
public_id text NOT NULL,
username text NOT NULL,
password text NOT NULL,
admin integer DEFAULT 0
);

CREATE TABLE DATA (
id SERIAL PRIMARY KEY,
list text NOT NULL,
completed integer DEFAULT 0,
user_id integer REFERENCES users(id)
);

INSERT INTO DATA (list) VALUES
('clean dishes'),
('sweep the floor'),
('get groceries'),
('pickup kids from school') 
;


