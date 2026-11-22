-- 02_views.sql  |  Run AFTER the CSVs are imported.
-- These views are your KPI layer. Dashboards read the views, never the raw tables.

-- One row per day. Matches data/daily_kpis.csv.
create or replace view v_daily_kpis as
with o as (
  select order_date as day,
         count(*) filter (where status <> 'cancelled')                      as orders,
         sum(revenue) filter (where status <> 'cancelled')                  as revenue,
         sum(units) filter (where status <> 'cancelled')                    as units,
         sum(is_new_customer) filter (where status <> 'cancelled')          as new_customers,
         sum(refund_amount) filter (where status <> 'cancelled')            as refunds,
         count(*) filter (where status = 'on_hold')                         as on_hold_orders,
         avg(extract(epoch from (fulfilled_at - order_ts)) / 3600.0)
             filter (where status = 'fulfilled')                            as avg_fulfilment_hours
  from orders group by order_date
), a as (select date as day, sum(spend) as ad_spend from ad_spend_daily group by date),
   s as (select date as day, sum(sessions) as sessions from sessions_daily group by date)
select o.day, o.revenue, o.orders, o.units,
       o.revenue / nullif(o.orders, 0)                       as aov,
       s.sessions,
       o.orders::numeric / nullif(s.sessions, 0)             as conversion_rate,
       a.ad_spend,
       o.revenue / nullif(a.ad_spend, 0)                     as mer,
       o.new_customers,
       a.ad_spend / nullif(o.new_customers, 0)               as cac,
       1 - o.new_customers::numeric / nullif(o.orders, 0)    as repeat_order_share,
       o.refunds,
       o.refunds / nullif(o.revenue, 0)                      as refund_rate,
       o.avg_fulfilment_hours, o.on_hold_orders
from o left join a using (day) left join s using (day);

-- Last 7 days vs the 7 days before. Ratios are computed from SUMS, never averages of daily ratios.
create or replace view v_kpi_periods as
with anchor as (select max(day) as end_d from v_daily_kpis),
tagged as (
  select k.*, case when k.day > a.end_d - 7 then 'current'
                   when k.day > a.end_d - 14 then 'prior' end as period
  from v_daily_kpis k cross join anchor a
)
select period,
       sum(revenue) / count(*)                              as revenue_per_day,
       sum(orders)::numeric / count(*)                      as orders_per_day,
       sum(revenue) / nullif(sum(orders), 0)                as aov,
       sum(orders)::numeric / nullif(sum(sessions), 0)      as conversion_rate,
       sum(revenue) / nullif(sum(ad_spend), 0)              as mer,
       sum(ad_spend) / nullif(sum(new_customers), 0)        as cac,
       1 - sum(new_customers)::numeric / nullif(sum(orders), 0) as repeat_order_share,
       sum(refunds) / nullif(sum(revenue), 0)               as refund_rate,
       avg(avg_fulfilment_hours)                            as avg_fulfilment_hours,
       sum(on_hold_orders)                                  as on_hold_orders
from tagged where period is not null group by period;

-- One row per KPI with its status. This is the heart of the product.
create or replace view v_kpi_status as
with cur as (select * from v_kpi_periods where period = 'current'),
     pri as (select * from v_kpi_periods where period = 'prior'),
vals as (
  select 'revenue_per_day' as kpi, cur.revenue_per_day::numeric as value, pri.revenue_per_day::numeric as prior_value from cur, pri
  union all select 'orders_per_day', cur.orders_per_day, pri.orders_per_day from cur, pri
  union all select 'aov', cur.aov, pri.aov from cur, pri
  union all select 'conversion_rate', cur.conversion_rate, pri.conversion_rate from cur, pri
  union all select 'mer', cur.mer, pri.mer from cur, pri
  union all select 'cac', cur.cac, pri.cac from cur, pri
  union all select 'repeat_order_share', cur.repeat_order_share, pri.repeat_order_share from cur, pri
  union all select 'refund_rate', cur.refund_rate, pri.refund_rate from cur, pri
  union all select 'avg_fulfilment_hours', cur.avg_fulfilment_hours::numeric, pri.avg_fulfilment_hours::numeric from cur, pri
  union all select 'on_hold_orders', cur.on_hold_orders::numeric, pri.on_hold_orders::numeric from cur, pri
  union all select 'skus_below_reorder', (select count(*) from products where stock_on_hand < reorder_point)::numeric, null::numeric
)
select v.kpi, v.value, v.prior_value,
       (v.value - v.prior_value) / nullif(v.prior_value, 0) as change_vs_prior,
       t.direction, t.alert_at, t.critical_at, t.sop_id, t.owner_role,
       case
         when (t.direction = 'min' and v.value < t.critical_at) or (t.direction = 'max' and v.value > t.critical_at) then 'critical'
         when (t.direction = 'min' and v.value < t.alert_at)    or (t.direction = 'max' and v.value > t.alert_at)    then 'alert'
         else 'ok'
       end as status
from vals v join kpi_thresholds t using (kpi);

-- Refunds by product (last 14 days). Refunds are stored per order, so this is "orders containing this SKU".
create or replace view v_refunds_by_sku as
select i.sku, p.name,
       count(distinct o.order_id) as orders,
       count(distinct o.order_id) filter (where o.refund_amount > 0) as refunded_orders,
       round(100.0 * count(distinct o.order_id) filter (where o.refund_amount > 0) / nullif(count(distinct o.order_id), 0), 1) as refund_pct,
       mode() within group (order by o.refund_reason) filter (where o.refund_amount > 0) as top_reason
from orders o join order_items i using (order_id) join products p using (sku)
where o.status <> 'cancelled' and o.order_date > (select max(order_date) from orders) - 14
group by i.sku, p.name;

-- Stock cover by product.
create or replace view v_stock_cover as
select p.sku, p.name, p.stock_on_hand, p.reorder_point, p.lead_time_days,
       round(coalesce(u.units14, 0) / 14.0, 1) as avg_daily_units,
       case when coalesce(u.units14, 0) = 0 then null else round(p.stock_on_hand / (u.units14 / 14.0), 1) end as days_of_cover,
       (p.stock_on_hand < p.reorder_point) as below_reorder
from products p
left join (
  select i.sku, sum(i.qty) as units14
  from order_items i join orders o using (order_id)
  where o.status <> 'cancelled' and o.order_date > (select max(order_date) from orders) - 14
  group by i.sku
) u using (sku);

-- Revenue by channel, last 7 days.
create or replace view v_channel_7d as
select channel, count(*) as orders, sum(revenue) as revenue
from orders
where status <> 'cancelled' and order_date > (select max(order_date) from orders) - 7
group by channel;

-- Read-only convenience for the team: open tasks with progress.
create or replace view v_open_tasks as
select t.id, s.name as sop, t.kpi, t.severity, t.owner_role, t.assigned_to, t.status, t.created_at, t.due_at,
       count(ts.id) filter (where ts.done) as steps_done, count(ts.id) as steps_total
from tasks t join sops s using (sop_id) left join task_steps ts on ts.task_id = t.id
where t.status <> 'done'
group by t.id, s.name;
