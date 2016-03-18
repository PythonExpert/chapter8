CREATE TABLE ratings
(
	userID	char(150),
	movieID char(150),
	rating NUMERIC,
	date_day NUMERIC,
	date_month	NUMERIC,
	date_year	NUMERIC,
	date_hour	NUMERIC,
	date_minute NUMERIC,
	date_second NUMERIC,
	type char(50) DEFAULT 'explicit'
)
