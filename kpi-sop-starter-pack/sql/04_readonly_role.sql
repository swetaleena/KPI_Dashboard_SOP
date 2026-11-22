-- 04_readonly_role.sql  |  Give Metabase / Looker Studio read-only access. Change the password first.
create role bi_readonly login password 'CHANGE_ME_TO_A_LONG_RANDOM_PASSWORD';
grant usage on schema public to bi_readonly;
grant select on all tables in schema public to bi_readonly;
alter default privileges in schema public grant select on tables to bi_readonly;
