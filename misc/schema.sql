DROP TABLE IF EXISTS tweets CASCADE;

CREATE TABLE tweets (
	id SERIAL PRIMARY KEY,
	name VARCHAR(10) NOT NULL,
	tweet VARCHAR(200)
);
