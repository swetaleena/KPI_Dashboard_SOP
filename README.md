# KPI Dashboard + SOP System: Starter Pack

Everything needed to build a plug-and-play KPI dashboard with SOP-linked alerts for Shopify brands.
```
data/      Sample store data (synthetic, 90 days): orders, items, customers, products, ads, sessions, daily KPIs
config/    KPI definitions, alert thresholds (KPI → SOP → owner), SOPs as tables
sops/      8 SOP documents + a blank template
sql/       Tables, KPI views, task automation, read-only role (PostgreSQL / Supabase)
scripts/   Apps Script for Sheets, data generator, SOP/config builder
```

Notes
- The data is **synthetic** (a fictional brand, "Kora Home"). Label it as sample data in every demo.
- The data ends on 21 Nov 2026. All KPI formulas anchor to the latest date in the data, so nothing breaks as time passes.
- The SQL targets PostgreSQL 14 or newer. It has not been run against a live database. The guide lists the results you should see so you can verify each step.
- Thresholds in `config/kpi_thresholds.csv` are tuned for the sample store only. Reset them from each real client's history.
