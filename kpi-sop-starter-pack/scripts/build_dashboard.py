"""Builds dashboard/index.html (single file, data embedded) from the CSVs in data/ and config/.
Run: python build_dashboard.py     Then open dashboard/index.html or upload it to any static host."""
import os, json
import pandas as pd
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
k = pd.read_csv(f"{R}/data/daily_kpis.csv")
cols = ["date", "revenue", "orders", "sessions", "ad_spend", "new_customers", "refunds", "on_hold_orders", "avg_fulfilment_hours"]
daily = k[cols].round(2).to_dict("records")
p = pd.read_csv(f"{R}/data/products.csv")
products = [dict(name=r["name"], stock=int(r.stock_on_hand), reorder=int(r.reorder_point), lead=int(r.lead_time_days)) for _, r in p.iterrows()]
th = pd.read_csv(f"{R}/config/kpi_thresholds.csv")
th = [dict(kpi=r.kpi, direction=r.direction, alert_at=float(r.alert_at), critical_at=float(r.critical_at),
           sop_id=r.sop_id, owner_role=r.owner_role) for _, r in th.iterrows()]
s = pd.read_csv(f"{R}/config/sops.csv")
sops = {r.sop_id: dict(name=r["name"], owner=r.owner_role, mins=int(r.est_minutes)) for _, r in s.iterrows()}
st = pd.read_csv(f"{R}/config/sop_steps.csv").sort_values(["sop_id", "step_no"])
steps = {sid: [[r.step, r.evidence_to_log] for _, r in g.iterrows()] for sid, g in st.groupby("sop_id")}
data = json.dumps(dict(daily=daily, products=products, th=th, sops=sops, steps=steps), separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/")
html = open(f"{R}/dashboard/template.html", encoding="utf-8").read().replace("__DATA__", data)
open(f"{R}/dashboard/index.html", "w", encoding="utf-8").write(html)
print("built dashboard/index.html", round(len(html) / 1024, 1), "KB")
