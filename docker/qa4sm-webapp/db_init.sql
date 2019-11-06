DROP USER if exists :"db_owner";

CREATE USER :db_owner WITH
  LOGIN
  NOSUPERUSER
  INHERIT
  NOCREATEDB
  NOCREATEROLE
  NOREPLICATION
  encrypted password :'db_owner_pass';
  
CREATE DATABASE :"db_name"
    WITH
    OWNER = :db_owner
    ENCODING = 'UTF8'
    LC_COLLATE = 'C'
    LC_CTYPE = 'en_US.UTF-8'
    TABLESPACE = pg_default
    TEMPLATE = template0
    CONNECTION LIMIT = -1;

GRANT ALL ON DATABASE :"db_name" TO :db_owner;