CREATE TABLE ratings
(
	userID	char(150),
	movieID char(150),
	rating NUMERIC,
	created timestamp,
	type char(50) DEFAULT 'explicit'
)

/*


*/
