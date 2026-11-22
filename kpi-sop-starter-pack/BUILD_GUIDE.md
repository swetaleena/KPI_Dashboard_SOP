# Build Guide: KPI Dashboard + SOP System

This guide takes you from the sample data in this pack to a working dashboard with KPI alerts that create SOP tasks. Then it shows you how to swap in a real client's data.

**Who this is for:** a freelancer or consultant who wants to build a demo and later deliver it to Shopify brands.
**Time:** Path A (no-code) about 1 day. Path B (SQL database) about 2 to 3 days.

---

## 1. What is in this pack

| Folder / file | What it is | Used for |
|---|---|---|
| `data/orders.csv` | 13,237 orders, 90 days (Shopify-style) | Raw data |
| `data/order_items.csv` | 19,932 order lines | Refunds and stock by product |
| `data/customers.csv` | 10,350 customers | Retention views |
| `data/products.csv` | 12 products with stock and reorder points | Low-stock alerts |
| `data/ad_spend_daily.csv` | Daily spend by campaign (Meta and Google) | MER, CAC |
| `data/sessions_daily.csv` | Daily sessions by source (GA4-style) | Conversion rate |
| `data/daily_kpis.csv` | One row per day, all KPIs pre-calculated | Fastest start (Path A) |
| `data/metrics_long.csv` | Same KPIs as `date, metric, value, source` | Alternative dashboard layout |
| `config/kpi_definitions.csv` | Exact definition of every KPI | Your metric dictionary |
| `config/kpi_thresholds.csv` | Alert and critical levels, linked SOP and owner | Drives alerts |
| `config/sops.csv`, `config/sop_steps.csv` | 8 SOPs as tables | Import into Notion, Sheets or SQL |
| `sops/*.md` | The same 8 SOPs as readable documents, plus `_TEMPLATE.md` | Hand to the client |
| `sql/01` to `04` | Tables, KPI views, automation, read-only role | Path B |
| `scripts/alerts.gs` | Google Apps Script for alerts and task creation | Path A |
| `scripts/generate_data.py` | Regenerates the sample data | Make a demo for another niche |
| `scripts/build_config.py` | Regenerates config and SOP files from one place | Edit SOP wording once |
| `PILOT_KIT.md` | Discovery questions, data request, onboarding, demo script | Selling and delivering |

**The data is synthetic.** It is generated for a fictional store called Kora Home. Never present it as a real client's results.

---

## 2. The story hidden in the data

Your demo needs a story. The data ends on 21 Nov 2026 and contains these planted problems in the last two weeks:

| Problem | What you will see | KPI that breaches | SOP it triggers |
|---|---|---|---|
| Meta prospecting spend rose while efficiency fell | MER fell from 2.7 to 2.05, CAC rose from $54 to $75, conversion slipped to 2.57% | `mer`, `cac`, `conversion_rate` | Ad account triage |
| Mug set (`KH-CER-004`) arrives damaged | Refund rate around 5.4%. About a third of orders with that SKU are refunded, mostly "damaged in transit" | `refund_rate` | Refund spike review |
| Linen throw (`KH-LIN-006`) is under its reorder point | 38 units in stock, reorder point 60, 42-day lead time | `skus_below_reorder` | Low-stock reorder |
| Orders stuck on hold | 17 orders on hold in the last days | `on_hold_orders` | Order exception handling |

**Expected result:** 6 KPIs in alert, which roll up into **4 SOP tasks** (the 3 ad KPIs share one SOP). If you see something different, a threshold or formula is off. Use this as your test.

---

## 3. Three ideas to understand first

**The data flow:**

```
Shopify + Ads + GA4  →  clean tables  →  KPI layer (daily + 7-day)  →  dashboard
                                                   │
                                      thresholds (kpi_thresholds)
                                                   ↓
                                    breach → task with SOP checklist → Slack / email
```

**Three metric rules that prevent most "your numbers are wrong" arguments:**

1. **Ratios are computed from sums.** MER for a week is `SUM(revenue) / SUM(ad_spend)`, never the average of seven daily MERs. This applies to conversion, CAC, AOV, refund rate and repeat share.
2. **Use Shopify revenue for MER and CAC, not ad-platform revenue.** Platforms over-report. `ad_spend_daily.revenue_attributed` is included so you can show this gap to a client, but do not use it for KPIs.
3. **One timezone, written down.** Use the store's timezone for `order_date`. Write it in the client's metric dictionary.

**Alert logic:** each KPI has a `direction`. `min` means bad when the value is below the threshold (revenue, MER). `max` means bad when above (CAC, refund rate). Each KPI has an `alert_at` and a stricter `critical_at`.

---

## 4. Choose your path

| | **Path A: Google Sheets + Looker Studio** | **Path B: Postgres (Supabase) + Metabase** |
|---|---|---|
| Skill needed | Spreadsheet formulas | Basic SQL |
| Cost | Free | Free tier, then about $25 per month |
| Time | About 1 day | 2 to 3 days |
| Handles | Up to about 50k rows per tab | Millions of rows |
| Alerts and tasks | Apps Script | SQL function + n8n/Make |
| Best for | First demo, small clients | Paid retainers, multiple clients |

**Recommendation:** build Path A first and use it for your first 2 or 3 pitches. Move to Path B when a client pays.

---

# PATH A: Google Sheets + Looker Studio

## A1. Create the sheet and import data (20 min)

1. Create a Google Sheet named `KPI-SOP Demo`.
2. For each file below: **File → Import → Upload → Insert new sheet(s) → Import data**. Then rename the new tab to **exactly** the name shown.

| File | Tab name |
|---|---|
| `data/daily_kpis.csv` | `daily_kpis` |
| `data/products.csv` | `products` |
| `config/kpi_thresholds.csv` | `kpi_thresholds` |
| `config/sop_steps.csv` | `sop_steps` |
| `config/sops.csv` | `sops` |
| `data/orders.csv` (optional, for channel charts) | `orders` |

3. **Check dates.** Click `daily_kpis!A2`. If the date is left-aligned, it imported as text. Select column A, then **Format → Number → Date**.

## A2. Build the `kpi_status` tab (30 min)

Create a new tab named `kpi_status`. Type these headers in row 1:

`kpi | value | direction | alert_at | critical_at | sop_id | owner_role | status`

In `J1` type `end_date`. In `J2` type `=MAX(daily_kpis!A:A)`.

In column A, rows 2 to 12, type the KPI names exactly: `revenue_per_day`, `orders_per_day`, `aov`, `conversion_rate`, `mer`, `cac`, `repeat_order_share`, `refund_rate`, `avg_fulfilment_hours`, `on_hold_orders`, `skus_below_reorder`.

**Columns C to G** pull from the thresholds tab. In row 2, then fill down:

| Cell | Formula |
|---|---|
| C2 | `=VLOOKUP($A2,kpi_thresholds!$A:$F,2,FALSE)` |
| D2 | `=VLOOKUP($A2,kpi_thresholds!$A:$F,3,FALSE)` |
| E2 | `=VLOOKUP($A2,kpi_thresholds!$A:$F,4,FALSE)` |
| F2 | `=VLOOKUP($A2,kpi_thresholds!$A:$F,5,FALSE)` |
| G2 | `=VLOOKUP($A2,kpi_thresholds!$A:$F,6,FALSE)` |
| H2 | `=IF(OR(AND(C2="min",B2<E2),AND(C2="max",B2>E2)),"critical",IF(OR(AND(C2="min",B2<D2),AND(C2="max",B2>D2)),"alert","ok"))` |

**Column B (the value, last 7 days).** Each row gets its own formula. Let `W` stand for `daily_kpis!A:A,">"&($J$2-7)`, and type it out in full in each formula:

| Row (KPI) | Formula in column B |
|---|---|
| revenue_per_day | `=SUMIFS(daily_kpis!B:B,W)/7` |
| orders_per_day | `=SUMIFS(daily_kpis!C:C,W)/7` |
| aov | `=SUMIFS(daily_kpis!B:B,W)/SUMIFS(daily_kpis!C:C,W)` |
| conversion_rate | `=SUMIFS(daily_kpis!C:C,W)/SUMIFS(daily_kpis!F:F,W)` |
| mer | `=SUMIFS(daily_kpis!B:B,W)/SUMIFS(daily_kpis!H:H,W)` |
| cac | `=SUMIFS(daily_kpis!H:H,W)/SUMIFS(daily_kpis!J:J,W)` |
| repeat_order_share | `=1-SUMIFS(daily_kpis!J:J,W)/SUMIFS(daily_kpis!C:C,W)` |
| refund_rate | `=SUMIFS(daily_kpis!M:M,W)/SUMIFS(daily_kpis!B:B,W)` |
| avg_fulfilment_hours | `=AVERAGEIFS(daily_kpis!O:O,W)` |
| on_hold_orders | `=SUMIFS(daily_kpis!P:P,W)` |
| skus_below_reorder | `=SUMPRODUCT(--(products!F2:F100<products!G2:G100))` |

Example, fully written out for `mer`:
`=SUMIFS(daily_kpis!B:B,daily_kpis!A:A,">"&($J$2-7))/SUMIFS(daily_kpis!H:H,daily_kpis!A:A,">"&($J$2-7))`

**Check your work.** You should get: `mer` ≈ 2.05, `cac` ≈ 74.8, `conversion_rate` ≈ 0.0257, `refund_rate` ≈ 0.0536, `on_hold_orders` = 17, `skus_below_reorder` = 1. Status `alert` on exactly those six rows and `ok` on the rest.

Add conditional formatting on column H: **Format → Conditional formatting**, "Text is exactly" `critical` = red, `alert` = orange, `ok` = green.

## A3. Create the `tasks` tab (5 min)

New tab named `tasks`. Row 1 headers, exactly:

`task_id | created_at | kpi | sop_id | owner_role | severity | step_no | step | evidence_to_log | done`

Select column J → **Insert → Checkbox** so the team can tick steps.

## A4. Turn on alerts and task creation (20 min)

1. **Extensions → Apps Script.** Delete the default code and paste the contents of `scripts/alerts.gs`. Save.
2. Optional: paste a Slack incoming-webhook URL into `SLACK_WEBHOOK`. If you leave it empty, the script emails you.
3. Click **Run** on `checkKpisAndCreateTasks` and approve permissions.
4. Open the `tasks` tab. You should see **4 tasks** (ads_triage, refund_spike, order_exceptions, low_stock), each with its checklist rows. You should also get an email or Slack message.
5. Run it again. **Nothing new should appear**, because an open task for each SOP already exists.
6. Automate: in Apps Script click the clock icon (Triggers) → **Add trigger** → function `checkKpisAndCreateTasks`, event source "Time-driven", "Day timer", pick 8 to 9 am.

**Live-demo trick:** in `kpi_thresholds`, change the `mer` alert from `2.5` to `5`. Delete the matching task rows and run the script. Watch it fire.

## A5. Build the dashboard in Looker Studio (2 to 3 hours)

1. Go to lookerstudio.google.com → **Create → Report → Google Sheets** → pick `KPI-SOP Demo` → `daily_kpis` → **Add**.
2. **Fix the ratios with calculated fields** (Resource → Manage added data sources → Edit → Add a field). Never use the daily ratio columns for scorecards, because averaging daily ratios gives wrong answers (rule 1 above).

| New field | Formula |
|---|---|
| MER | `SUM(revenue) / SUM(ad_spend)` |
| CAC | `SUM(ad_spend) / SUM(new_customers)` |
| Conversion | `SUM(orders) / SUM(sessions)` |
| AOV | `SUM(revenue) / SUM(orders)` |
| Refund rate | `SUM(refunds) / SUM(revenue)` |
| Repeat share | `1 - SUM(new_customers) / SUM(orders)` |

Set the type of Conversion, Refund rate and Repeat share to **Numeric → Percent**.

3. **Layout (top to bottom):**

| Row | Content |
|---|---|
| Header | Client name, a **Date range control** (default: Last 7 days), a note "Data: demo" |
| Row 1 | 8 scorecards: Revenue, Orders, AOV, Conversion, MER, CAC, Refund rate, Repeat share. In each scorecard: **Setup → Comparison date range → Previous period**. This gives the up and down arrows. |
| Row 2 | Time series: Revenue and Orders by `date`; MER and CAC by `date` |
| Row 3 | Add a second data source for the `kpi_status` tab. Insert a table with `kpi, value, status, sop_id, owner_role`. Add conditional formatting so `critical` is red and `alert` is orange. **Title this block "Needs action"**. |
| Row 4 | Optional: from `orders`, a bar chart of revenue by `channel` |

4. **Share → Manage access → Anyone with the link → Viewer.** Send the link.

Time series charts of MER and CAC by day will look noisy. That is fine. The status table gives the 7-day view.

---

# PATH B: Postgres (Supabase) + Metabase

## B1. Create the database (10 min)

1. Sign up at supabase.com → **New project**. Choose the region nearest your clients. Save the database password.
2. Open **SQL Editor → New query**. Paste all of `sql/01_schema.sql`. Click **Run**. You should see "Success".

## B2. Import the data (30 min)

Open **Table Editor**, pick the table, then **Insert → Import data from CSV**. Import **in this order** (foreign keys require it):

| Order | Table | File | Rows expected |
|---|---|---|---|
| 1 | `products` | `data/products.csv` | 12 |
| 2 | `customers` | `data/customers.csv` | 10,350 |
| 3 | `orders` | `data/orders.csv` | 13,237 |
| 4 | `order_items` | `data/order_items.csv` | 19,932 |
| 5 | `ad_spend_daily` | `data/ad_spend_daily.csv` | 360 |
| 6 | `sessions_daily` | `data/sessions_daily.csv` | 450 |
| 7 | `sops` | `config/sops.csv` | 8 |
| 8 | `sop_steps` | `config/sop_steps.csv` | 53 |
| 9 | `kpi_thresholds` | `config/kpi_thresholds.csv` | 11 |

Check each import in the SQL Editor: `select count(*) from orders;` and compare with the table.

**If the dashboard import times out on the large files**, use `psql` instead. Get the connection string from **Project Settings → Database**, then:

```
psql "YOUR_CONNECTION_STRING" -c "\copy orders from 'data/orders.csv' csv header"
```

## B3. Create the KPI layer (10 min)

Run all of `sql/02_views.sql`, then test:

```sql
select kpi, round(value, 4) as value, status, sop_id
from v_kpi_status
order by status, kpi;
```

You should see `alert` on exactly: `cac`, `conversion_rate`, `mer`, `on_hold_orders`, `refund_rate`, `skus_below_reorder`, and `ok` on the other five. Also try `select * from v_refunds_by_sku order by refund_pct desc;`. `KH-CER-004` should be at the top with `damaged in transit`.

> **Note:** the SQL is written for PostgreSQL 14 or newer (what Supabase uses). I could not run it against a live database while preparing this pack, so use the expected results above as your test. If a statement errors, copy the error message and the statement and ask Claude to fix it.

## B4. Turn on task automation (10 min)

Run all of `sql/03_automation.sql`. Then test by hand:

```sql
select create_tasks_from_breaches();   -- expect 4
select * from v_open_tasks;            -- 4 tasks, each with steps_total of 6 to 7
select create_tasks_from_breaches();   -- run again: expect 0 (no duplicates)
```

To run it every day: **Database → Extensions → enable `pg_cron`**, then run the `cron.schedule(...)` line that is commented out at the bottom of the file. It is set to 02:30 UTC, which is 08:00 India time. Change it for your client's timezone.

## B5. Connect Metabase (20 min)

1. Run `sql/04_readonly_role.sql` after changing the password. BI tools should never use your admin login.
2. Get Metabase: **Metabase Cloud** (free trial), or locally with `docker run -d -p 3000:3000 --name metabase metabase/metabase` then open `localhost:3000`.
3. **Admin → Databases → Add database → PostgreSQL.** Use the host, port, database name from Supabase (**Project Settings → Database**; use the **Session pooler** details if the direct host does not connect) and the user `bi_readonly`.

## B6. Build the dashboard (2 to 3 hours)

Create each as **New → SQL query**, save it, then add all to a new dashboard.

| Card | SQL |
|---|---|
| Needs action (table) | `select kpi, round(value::numeric,4) as value, round(100*change_vs_prior::numeric,1) as pct_change, status, sop_id, owner_role from v_kpi_status order by case status when 'critical' then 0 when 'alert' then 1 else 2 end;` |
| Revenue and orders | `select day, revenue, orders from v_daily_kpis order by day;` |
| MER, 7-day rolling | `select day, sum(revenue) over w / nullif(sum(ad_spend) over w,0) as mer_7d from v_daily_kpis window w as (order by day rows between 6 preceding and current row) order by day;` |
| CAC, 7-day rolling | `select day, sum(ad_spend) over w / nullif(sum(new_customers) over w,0) as cac_7d from v_daily_kpis window w as (order by day rows between 6 preceding and current row) order by day;` |
| Spend by campaign | `select date, campaign, sum(spend) as spend from ad_spend_daily group by 1,2 order by 1;` |
| Refunds by product | `select * from v_refunds_by_sku order by refund_pct desc;` |
| Stock cover | `select * from v_stock_cover order by below_reorder desc, days_of_cover;` |
| Revenue by channel | `select * from v_channel_7d order by revenue desc;` |
| Open tasks | `select * from v_open_tasks order by due_at;` |

**Layout:** "Needs action" and the 8 headline numbers at the top. Trend charts in the middle. Refunds by product, stock cover and open tasks at the bottom. For headline numbers use the `v_kpi_status` table with **Visualization → Number** and a filter on one `kpi` per card.

## B7. Send Slack or email alerts (30 min)

Use **n8n** (free self-hosted or cloud trial), Make or Zapier. In n8n:

1. **Schedule Trigger**: every day at 8:00.
2. **Postgres → Execute Query**: `select create_tasks_from_breaches();`
3. **Postgres → Execute Query**: `select * from v_tasks_to_notify;`
4. **Slack → Send message** (runs once per row). Text example: `🟠 {{$json.kpi}} breached ({{$json.severity}}). Run SOP: {{$json.sop_name}}. Owner: {{$json.owner_role}}. Due: {{$json.due_at}}`
5. **Postgres → Execute Query**: `update tasks set notified = true where id = {{$json.id}};`

(If you use `pg_cron` in B4, drop step 2 from n8n.)

## B8. Give the team a place to tick off steps

For a demo, the Supabase Table Editor on `task_steps` is enough (tick `done`). For a client, use one of these on top of the same tables:

- **Retool** or **Appsmith** (free tiers): a table of `v_open_tasks`, click a task, see its `task_steps` with checkboxes.
- **Notion** (next section), with n8n copying tasks in.

---

# THE SOP SYSTEM (both paths)

The `sops/*.md` files are complete documents. Use them as-is to start.

## S1. Put the SOPs where the team already works (30 min, Notion example)

1. In Notion, create a page called **SOP Hub**.
2. **Settings → Import → Text & Markdown.** Select all 8 files in `sops/`. Each becomes a page with checkable steps.
3. Move the 8 pages into a database called **SOP Library** with these properties: `Owner` (select), `Linked KPI` (multi-select), `Version` (text), `Last reviewed` (date), `Review due` (date).
4. Fill `Linked KPI` from `config/kpi_thresholds.csv`. For example `ads_triage` is linked to `mer`, `cac` and `conversion_rate`.
5. Create a second database, **Acknowledgements**, with: `SOP` (relation), `Person` (person), `Version` (text), `Date` (date). Each team member adds a row after reading an SOP. When you publish version 1.1 of an SOP, everyone must acknowledge again.

If you prefer Google Docs or Sheets, `config/sop_steps.csv` imports directly as a checklist table.

## S2. Make the SOPs yours (the part clients pay for)

The 8 SOPs are generic. The value you sell is adapting them. For each client:

1. Run through the SOP with the person who does the job today. Replace generic steps with their real tools, names and limits (for example, "approved refund limit: $75").
2. Edit the text in `scripts/build_config.py` (the `SOPS` dictionary), run `python scripts/build_config.py`, and all files update together.
3. Change the `owner_role` values in `config/kpi_thresholds.csv` to real roles and names.
4. Add the SOP version and date to the footer of each document.

## S3. A good SOP checklist

- Every step starts with a verb and has one action.
- A new hire could do it without asking anyone.
- Each step names the evidence to log (a number, link or screenshot).
- It has a checkable "done when" and a named escalation.
- It is under 10 steps. If it is longer, split it.

---

# SWAP IN A REAL CLIENT'S DATA

Do this only after your demo works end to end on the sample data.

## R1. Get the exports

Ask the client for (details and a message template are in `PILOT_KIT.md`): Shopify admin access (Staff account with "Orders" and "Products" permissions, or exports), ad account viewer access, and GA4 viewer access.

## R2. Map real columns to the pack's tables

**Shopify order export** (Orders → Export → CSV). Shopify writes one row per line item, with order-level fields only on the first row of each order.

| Pack column | Shopify column | Notes |
|---|---|---|
| `order_id` | `Name` | Strip the `#` |
| `order_ts` | `Created at` | Convert to the store timezone |
| `order_date` | `Created at` | Date part |
| `customer_id` | `Email` | Hash it, or map each email to a number |
| `subtotal` | `Subtotal` | |
| `discount` | `Discount Amount` | |
| `shipping` | `Shipping` | |
| `revenue` | `Subtotal` minus `Discount Amount` | Excludes shipping and tax |
| `status` | `Cancelled at`, `Fulfillment Status` | Cancelled if `Cancelled at` is filled. Otherwise `fulfilled`, `unfulfilled` or `on_hold` |
| `fulfilled_at` | `Fulfilled at` | |
| `refund_amount` | `Refunded Amount` | |
| `is_new_customer` | calculated | `1` if it is that email's first order ever. Needs full order history |
| `channel` | `Source` / UTM | Map into meta, google, email, organic, direct |

Line items (`Lineitem sku`, `Lineitem quantity`, `Lineitem price`) become `order_items`.

**Ad spend:** Meta Ads Manager → Reports → export with Day, Campaign name, Amount spent, Impressions, Link clicks, Results (Purchases), Purchases conversion value. Google Ads: Day, Campaign, Cost, Impressions, Clicks, Conversions, Conv. value. Both map to `ad_spend_daily`. Add a `platform` column. Convert all spend to one currency.

**Sessions:** GA4 → Reports → Traffic acquisition → Day and Session source/medium → Sessions. Map to `sessions_daily`.

## R3. Or use a connector instead of exports

Airbyte, Fivetran or Windsor.ai can pull Shopify, Meta, Google Ads and GA4 into Postgres or Sheets daily. You then write a small query that reshapes their tables into the pack's tables. The KPI views and everything above stay the same. This is the upgrade path when a client wants live data.

## R4. Set thresholds from the client's own history

Never reuse the sample thresholds. Calculate the client's last 90 days, then set `alert_at` about 10 to 15% worse than their normal 7-day level and `critical_at` about 25 to 30% worse. Show them and ask, "Does this feel right?" Edit `config/kpi_thresholds.csv` (or the `kpi_thresholds` tab or table).

## R5. Make a demo for a different niche

Open `scripts/generate_data.py`. Edit `PRODUCTS`, the brand name and the numbers near `base`. Run `python scripts/generate_data.py`. Then update the thresholds to match.

---

# QA CHECKLIST (before any client sees it)

- [ ] Revenue for a week matches the store's own report to within 1 to 2%, with the same definition (excluding shipping and tax).
- [ ] Order count matches, with cancelled orders excluded.
- [ ] Ad spend equals the platform's own total for the same dates and currency.
- [ ] Dates are in the store's timezone. Check a late-evening order lands on the right day.
- [ ] No duplicate orders: `select count(*), count(distinct order_id) from orders;` returns the same number twice.
- [ ] The newest day is complete. If data stops mid-day, exclude today.
- [ ] Every KPI has a written definition in `kpi_definitions.csv` and the client has read it.
- [ ] Thresholds are set from the client's data and the client agrees.
- [ ] Alert test: lower a threshold, confirm exactly one task appears, with the correct owner and SOP.
- [ ] A second alert run creates no duplicates.
- [ ] The people named as owners know they are owners.
- [ ] Access is read-only for the BI tool, and no passwords are in shared files.

---

# COMMON PROBLEMS

| Symptom | Likely cause | Fix |
|---|---|---|
| All `SUMIFS` return 0 (Sheets) | Dates imported as text | Format column A as Date |
| `#N/A` in `kpi_status` columns C to G | KPI name in column A does not match `kpi_thresholds` exactly | Check spelling and spaces |
| Scorecard MER looks wrong in Looker Studio | Using the daily `mer` column with "Average" | Use the calculated field `SUM(revenue)/SUM(ad_spend)` |
| Import fails on `order_items` | `orders` not imported first | Import in the order shown |
| `create_tasks_from_breaches()` returns 0 on the first run | Views not created, or `kpi_thresholds` / `sops` / `sop_steps` empty | Re-check B2 and B3 |
| Client says "your revenue is different from Shopify" | Different definition (shipping, tax, refunds, timezone) | Show `kpi_definitions.csv` and match their definition |
| Refund rate looks too low for recent days | Refunds arrive days after the order | Review refund rate over 14 to 30 days |
| Alerts feel noisy | Thresholds too tight | Loosen `alert_at`, and keep `critical_at` for real emergencies |

---

# WHAT TO BUILD NEXT (version 2)

1. A connector instead of CSV exports (Shopify, Meta, Google Ads, GA4, then Klaviyo).
2. Per-user logins and roles.
3. Assigning tasks to named people, with reminders for overdue tasks.
4. A weekly digest message summarizing KPI movement and task completion.
5. Proper 90-day LTV and repeat-rate cohorts (needs 6 or more months of history).

Build these only after a paying client asks for them.
