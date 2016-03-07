BEGIN;

--------
-- TABLES
--------
DROP TABLE rdx_member CASCADE;
DROP TABLE rdx_user CASCADE;
DROP TABLE rdx_group CASCADE;

CREATE TABLE rdx_user (
    userid        VARCHAR(64) UNIQUE NOT NULL,
    first_name      VARCHAR(128) NOT NULL,
    last_name       VARCHAR(128) NOT NULL
);

CREATE TABLE rdx_group (
    group_name      VARCHAR(64) UNIQUE NOT NULL
);

CREATE TABLE rdx_member (
    userid        VARCHAR(64) NOT NULL,
    group_name      VARCHAR(64) NOT NULL,
    FOREIGN KEY(userid)       REFERENCES rdx_user(userid),
    FOREIGN KEY(group_name)     REFERENCES rdx_group(group_name),
    UNIQUE (userid, group_name)
);

CREATE INDEX rdx_member_user_idx ON rdx_member USING BTREE (userid,group_name);
CREATE INDEX rdx_member_group_idx ON rdx_member USING BTREE (group_name,userid);


--------
-- VIEWS
--------
CREATE VIEW user_view AS
    SELECT u.*, (SELECT COALESCE(array_to_json(array_agg(g.group_name)), '[]') AS groups
        FROM (SELECT group_name from rdx_member where userid = u.userid) g
    ) FROM rdx_user u;

CREATE VIEW group_view AS
    SELECT g.group_name, (SELECT COALESCE(array_to_json(array_agg(m.userid)), '[]') AS users
        FROM (SELECT userid FROM rdx_member WHERE group_name = g.group_name) m
    ) FROM rdx_group g;


------------
-- FUNCTIONS
------------

--------
-- USERS
--------
CREATE OR REPLACE FUNCTION user_add(
    __userid VARCHAR,
    __first_name VARCHAR,
    __last_name VARCHAR,
    __groups VARCHAR [],
    OUT js JSON) AS $_$
DECLARE
    __user_exists   BOOLEAN;
    __group_exists  BOOLEAN;
    __g             VARCHAR;
BEGIN
    __user_exists := user_exists(__userid);
    IF (__user_exists = TRUE) THEN
        RETURN;
    END IF;

    INSERT INTO rdx_user(userid,   first_name,   last_name)
                  VALUES(__userid, __first_name, __last_name);

    FOREACH __g IN ARRAY __groups LOOP
        PERFORM group_member_upsert(__g, __userid);
     END LOOP;

    js := row_to_json(r) FROM (SELECT * from user_view WHERE userid = __userid) r;
END;
$_$ Language 'plpgsql' SECURITY DEFINER;


CREATE OR REPLACE FUNCTION user_update(
    __userid      VARCHAR,
    __first_name    VARCHAR,
    __last_name     VARCHAR,
    __groups        VARCHAR [],
    OUT js JSON) AS $_$
DECLARE
    __g       VARCHAR;
BEGIN

    UPDATE rdx_user SET 
        first_name      = __first_name,
        last_name       = __last_name
        WHERE userid = __userid;

    DELETE FROM rdx_member WHERE userid = __userid AND NOT group_name = ANY(__groups);
    FOREACH __g IN ARRAY __groups LOOP
        PERFORM group_member_upsert(__g, __userid);
    END LOOP;
    js := row_to_json(r) FROM (SELECT * from user_view WHERE userid = __userid) r;
END;
$_$ Language 'plpgsql' SECURITY DEFINER;






CREATE OR REPLACE FUNCTION user_exists(in __userid VARCHAR, out __ok BOOLEAN) AS $_$
DECLARE
    __existing_user VARCHAR;
BEGIN
    __ok := FALSE;
    __existing_user := userid FROM rdx_user WHERE userid = __userid;
    if (__existing_user IS NOT NULL) THEN
        __ok := TRUE;
    END IF;
END;
$_$ Language 'plpgsql' SECURITY DEFINER;


CREATE OR REPLACE FUNCTION user_delete(IN __userid VARCHAR, OUT __ok BOOLEAN) AS $_$
BEGIN
    __ok := FALSE;
    DELETE FROM rdx_member r WHERE r.userid = __userid;
    DELETE FROM rdx_user u WHERE u.userid = __userid;
    __ok := TRUE;
END;
$_$ Language 'plpgsql' SECURITY DEFINER;


CREATE OR REPLACE FUNCTION group_member_upsert(IN __group_name VARCHAR, __userid VARCHAR, OUT __ok BOOLEAN) AS $_$
DECLARE
    __group_exists BOOLEAN;
    __g             VARCHAR;
BEGIN
    -- XXX do we need bool here even?
    __ok := TRUE;
    __group_exists := group_exists(__group_name);
    IF (__group_exists IS FALSE) THEN
        __g := group_add(__group_name);
    END IF;
    INSERT INTO rdx_member(group_name, userid)
        SELECT __group_name, __userid 
        WHERE NOT EXISTS (
            SELECT userid FROM rdx_member WHERE userid = __userid AND group_name = __group_name
        );
END;
$_$ Language 'plpgsql' SECURITY DEFINER;



----------
--- GROUPS
----------
CREATE OR REPLACE FUNCTION group_get(IN __group_name VARCHAR, OUT js json) AS $_$
BEGIN
    js := row_to_json(r) FROM (SELECT * from group_view WHERE group_name = __group_name) r;
END;
$_$ Language 'plpgsql' SECURITY DEFINER;


 
CREATE OR REPLACE FUNCTION group_exists(in __group_name VARCHAR, OUT __ok BOOLEAN) AS $_$
DECLARE
    __existing_group VARCHAR;
BEGIN
    __ok := FALSE;
    __existing_group := group_name from rdx_group where group_name = __group_name;
    if (__existing_group is not null) then
        __ok = true;
    END IF;
END;
$_$ Language 'plpgsql' SECURITY DEFINER;



-- TODO return members as ARRAY
CREATE OR REPLACE FUNCTION group_add(IN __group_name VARCHAR, OUT js JSON) AS $_$
BEGIN
    INSERT INTO rdx_group (group_name) VALUES (__group_name);
    js := row_to_json(r) FROM (SELECT * from group_view WHERE group_name = __group_name) r;
END;
$_$ Language 'plpgsql' SECURITY DEFINER;


-- update members
CREATE OR REPLACE FUNCTION group_update(IN __group_name VARCHAR, __members VARCHAR[], OUT js JSON) AS $_$
DECLARE
    __userid          VARCHAR;
BEGIN
    IF (group_exists(__group_name) = FALSE) THEN
        RETURN;
     END IF;

    DELETE FROM rdx_member WHERE group_name = __group_name AND NOT userid = ANY(__members);

    FOREACH __userid IN ARRAY __members LOOP
        PERFORM group_member_upsert(__group_name, __userid);
     END LOOP;

    js := row_to_json(r) FROM (SELECT * from group_view WHERE group_name = __group_name) r;
END;
$_$ Language 'plpgsql' SECURITY DEFINER;


-- update members
CREATE OR REPLACE FUNCTION group_delete(IN __group_name VARCHAR, OUT __ok BOOLEAN) AS $_$
BEGIN
    __ok := FALSE;
    DELETE FROM rdx_member WHERE group_name = __group_name;
    DELETE FROM rdx_group WHERE group_name = __group_name;
    __ok := TRUE;
END;
$_$ Language 'plpgsql' SECURITY DEFINER;

