-- 03_automation.sql  |  The "wow" feature: a KPI breach becomes an owned task with the SOP checklist attached.

-- Creates ONE task per SOP (not per KPI) for every breached KPI, unless an open task for that SOP already exists.
-- Returns how many tasks were created.
create or replace function create_tasks_from_breaches() returns integer
language plpgsql as $$
declare n integer;
begin
  with worst as (
    select distinct on (sop_id) kpi, sop_id, owner_role, value, status
    from v_kpi_status
    where status in ('alert', 'critical') and sop_id is not null
    order by sop_id, (status = 'critical') desc, kpi
  ),
  ins as (
    insert into tasks (kpi, sop_id, owner_role, trigger_value, severity, due_at)
    select w.kpi, w.sop_id, w.owner_role, w.value, w.status, now() + interval '2 days'
    from worst w
    where not exists (select 1 from tasks t where t.sop_id = w.sop_id and t.status <> 'done')
    returning id, sop_id
  ),
  steps as (
    insert into task_steps (task_id, step_no, step, evidence_to_log)
    select ins.id, s.step_no, s.step, s.evidence_to_log from ins join sop_steps s using (sop_id)
    returning 1
  )
  select count(*) into n from ins;
  return n;
end $$;

-- Tasks that still need a Slack/email notification. Your automation tool reads this, sends the message,
-- then runs:  update tasks set notified = true where id = <id>;
create or replace view v_tasks_to_notify as
select t.id, s.name as sop_name, t.kpi, t.severity, t.trigger_value, t.owner_role, t.due_at
from tasks t join sops s using (sop_id)
where t.notified = false and t.status <> 'done';

-- Schedule it daily. First enable the extension: Supabase -> Database -> Extensions -> pg_cron.
-- 02:30 UTC = 08:00 India time. Change the cron expression for the client's timezone.
-- select cron.schedule('daily-breach-check', '30 2 * * *', $$select create_tasks_from_breaches()$$);

-- Test it by hand any time:
-- select create_tasks_from_breaches();
-- select * from v_open_tasks;
