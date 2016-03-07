BEGIN;

INSERT INTO rdx_user (userid, first_name, last_name) VALUES ('alice', 'Alice', 'Ackerman');
INSERT INTO rdx_user (userid, first_name, last_name) VALUES ('bob', 'Bob', 'Builder');
INSERT INTO rdx_user (userid, first_name, last_name) VALUES ('cc', 'Charlie', 'Cooper');

INSERT INTO rdx_group(group_name) VALUES ('admin');
INSERT INTO rdx_group(group_name) VALUES ('beta');
INSERT INTO rdx_group(group_name) VALUES ('click');
INSERT INTO rdx_group(group_name) VALUES ('delta');
INSERT INTO rdx_group(group_name) VALUES ('zeta');

INSERT INTO rdx_member(userid, group_name) VALUES ('alice', 'admin');
INSERT INTO rdx_member(userid, group_name) VALUES ('bob', 'beta');
INSERT INTO rdx_member(userid, group_name) VALUES ('cc', 'admin');
INSERT INTO rdx_member(userid, group_name) VALUES ('cc', 'beta');

INSERT INTO rdx_member(userid, group_name) VALUES ('alice', 'zeta');
INSERT INTO rdx_member(userid, group_name) VALUES ('bob', 'zeta');
INSERT INTO rdx_member(userid, group_name) VALUES ('cc', 'zeta');

