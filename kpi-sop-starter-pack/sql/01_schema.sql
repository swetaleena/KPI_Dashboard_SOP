-- 01_schema.sql  |  Run in Supabase: SQL Editor -> New query -> paste -> Run
-- Creates all tables. Import the CSVs afterwards (order is in BUILD_GUIDE.md).

create table if not exists products (
  sku text primary key, name text, category text, price numeric, cogs numeric,
  stock_on_hand int, reorder_point int, lead_time_days int
);

create table if not exists customers (
  customer_id bigint primary key, orders_in_period int, revenue_in_period numeric,
  first_seen_in_period date, lifetime_orders int, acquisition_channel text, customer_type text
);

create table if not exists orders (
  order_id bigint primary key, order_ts timestamp, order_date date, customer_id bigint,
  channel text, is_new_customer int, units int, subtotal numeric, discount numeric, shipping numeric,
  revenue numeric, status text, fulfilled_at timestamp, refund_amount numeric, refund_reason text, country text
);

create table if not exists order_items (
  order_id bigint references orders(order_id), sku text, qty int, unit_price numeric, line_total numeric
);

create table if not exists ad_spend_daily (
  date date, platform text, campaign text, spend numeric, impressions bigint, clicks bigint,
  purchases int, revenue_attributed numeric
);

create table if not exists sessions_daily (
  date date, source text, sessions int, add_to_cart_sessions int, checkout_sessions int
);

-- configuration
create table if not exists kpi_thresholds (
  kpi text primary key, direction text check (direction in ('min','max')),
  alert_at numeric, critical_at numeric, sop_id text, owner_role text
);

create table if not exists sops (
  sop_id text primary key, name text, owner_role text, est_minutes int, trigger text, purpose text,
  tools text, done_when text, escalate_to text, version text
);

create table if not exists sop_steps (
  sop_id text references sops(sop_id), step_no int, step text, est_minutes int, evidence_to_log text,
  primary key (sop_id, step_no)
);

-- work tracking (filled by automation and by your team)
create table if not exists tasks (
  id bigserial primary key, kpi text, sop_id text references sops(sop_id), owner_role text, assigned_to text,
  status text default 'open' check (status in ('open','in_progress','done')),
  severity text, trigger_value numeric, notified boolean default false,
  created_at timestamptz default now(), due_at timestamptz, completed_at timestamptz
);

create table if not exists task_steps (
  id bigserial primary key, task_id bigint references tasks(id) on delete cascade,
  step_no int, step text, evidence_to_log text,
  done boolean default false, done_by text, done_at timestamptz, evidence text
);

create table if not exists sop_acknowledgements (
  user_email text, sop_id text references sops(sop_id), version text,
  acknowledged_at timestamptz default now(), primary key (user_email, sop_id, version)
);

create index if not exists idx_orders_date on orders(order_date);
create index if not exists idx_items_order on order_items(order_id);
