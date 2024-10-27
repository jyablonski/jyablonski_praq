SELECT rolname FROM pg_roles;
GRANT ALL PRIVILEGES ON DATABASE jacob_Db TO terraform_admin;


alter user terraform_admin with admin option;

SELECT * FROM pg_roles;

SELECT *
FROM pg_roles r
JOIN pg_auth_members m ON r.oid = m.roleid
JOIN pg_roles u ON u.oid = m.member
WHERE u.rolname = 'avnadmin';

revoke terraform_admin from avnadmin;

SELECT *
FROM information_schema.role_table_grants;

GRANT terraform_admin TO avnadmin WITH ADMIN OPTION;
GRANT terraform_admin TO avnadmin WITH ADMIN OPTION;

SELECT * FROM pg_roles WHERE rolname = 'avnadmin';
REVOKE terraform_admin FROM avnadmin;

SELECT
    r.rolname AS schema_owner,
    ns.*
FROM
    pg_namespace ns
JOIN
    pg_roles r 
ON
    ns.nspowner = r.oid;

 SELECT 
    n.nspname AS schema_name
   FROM pg_namespace n
  WHERE  has_schema_privilege('avnadmin',n.nspname, 'CREATE, USAGE');


create table nba_source.team_top_players (

	player text primary key,
	team text,
	rank integer,
	created_at timestamp default current_timestamp,
	modified_at timestamp default current_timestamp
);
	
insert into nba_source.team_top_players (player, team, rank)
values
	('Trae Young', 'ATL', 1),
	('Clint Capela', 'ATL', 2),
	('Jayson Tatum', 'BOS', 1),
	('Jaylen Brown', 'BOS', 2),
	('Ben Simmons', 'BKN', 1),
	('Cam Johnson', 'BKN', 2),
	('LaMelo Ball', 'CHA', 1),
	('Miles Bridges', 'CHA', 2),
	('Zach Lavine', 'CHI', 1),
	('Lonzo Ball', 'CHI', 2),
	('Donovan Mitchell', 'CLE', 1),
	('Darius Garland', 'CLE', 2),
	('Luka Doncic', 'DAL', 1),
	('Kyrie Irving', 'DAL', 2),
	('Nikola Jokic', 'DEN', 1),
	('Jamal Murray', 'DEN', 2),
	('Cade Cunningham', 'DET', 1),
	('Jalen Duren', 'DET', 2),
	('Stephen Curry', 'GSW', 1),
	('Draymond Green', 'GSW', 2),
	('Jalen Green', 'HOU', 1),
	('Fred VanVleet', 'HOU', 2),
	('Tyrese Haliburton', 'IND', 1),
	('Pascal Siakam', 'IND', 2),
	('Kawhi Leonard', 'LAC', 1),
	('James Harden', 'LAC', 2),
	('LeBron James', 'LAL', 1),
	('Anthony Davis', 'LAL', 2),
	('Ja Morant', 'MEM', 1),
	('Jaren Jackson', 'MEM', 2),
	('Jimmy Butler', 'MIA', 1),
	('Bam Adebayo', 'MIA', 2),
	('Giannis Antetokounmpo', 'MIL', 1),
	('Damian Lillard', 'MIL', 2),
    ('Anthony Edwards', 'MIN', 1),
    ('Rudy Gobert', 'MIN', 2),
	('Zion Williamson', 'NOP', 1),
	('Brandon Ingram', 'NOP', 2),
	('Jalen Brunson', 'NYK', 1),
	('Karl-Anthony Towns', 'NYK', 2),
	('Shai Gilgeous-Alexander', 'OKC', 1),
	('Jalen Williams', 'OKC', 2),
	('Paolo Banchero', 'ORL', 1),
	('Jonathan Isaac', 'ORL', 2),
	('Joel Embiid', 'PHI', 1),
	('Paul George', 'PHI', 2),
	('Kevin Durant', 'PHX', 1),
	('Devin Booker', 'PHX', 2),
	('Anfrenee Simons', 'POR', 1),
	('Deandre Ayton', 'POR', 2),
	('De''Aaron Fox', 'SAC', 1),
	('Demantas Sabonis', 'SAC', 2),
	('Victor Wenbanyama', 'SAS', 1),
	('Chris Paul', 'SAS', 2),
	('Immanuel Quickley', 'TOR', 1),
	('RJ Barrett', 'TOR', 2),
	('Lauri Markkanen', 'UTA', 1),
	('Jordan Clarkson', 'UTA', 2),
	('Jordan Poole', 'WAS', 1),
	('Kyle Kuzma', 'WAS', 2);