DROP TABLE IF EXISTS tweet CASCADE;

CREATE TABLE tweet (
	id SERIAL PRIMARY KEY,
	node_name VARCHAR(10) NOT NULL,
	content VARCHAR(500),
	pub_datetime TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp,
	rt BOOLEAN DEFAULT FALSE,
	rt_origin_name VARCHAR(100),
	rt_origin_id INTEGER
);
