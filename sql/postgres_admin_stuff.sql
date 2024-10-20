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