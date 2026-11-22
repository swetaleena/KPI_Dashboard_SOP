"""
Generates a synthetic 90-day Shopify-style dataset for the fictional brand "Kora Home".

Run:  python generate_data.py
Output: ../data/*.csv

Problems deliberately planted in the last ~2 weeks so your demo has a story:
  1. Ad efficiency drops: Meta prospecting spend rises, MER and conversion fall, CAC climbs.
  2. Refund spike on SKU KH-CER-004 (Hand-Glazed Mug Set), mostly "damaged in transit".
  3. KH-LIN-006 (Linen Throw) is below its reorder point.
  4. A few orders are stuck "on_hold" and fulfilment time is slowing.

To adapt to another niche: edit PRODUCTS, CAMPAIGNS, BRAND-level numbers below, change END, re-run.
"""
import os
import numpy as np
import pandas as pd

SEED = 42
END = pd.Timestamp("2026-11-21")   # last day of data
DAYS = 90
rng = np.random.default_rng(SEED)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
os.makedirs(OUT, exist_ok=True)

dates = pd.date_range(END - pd.Timedelta(days=DAYS - 1), END)

# sku, name, category, price, cogs, stock_on_hand, reorder_point, lead_time_days, popularity
PRODUCTS = [
    ("KH-CAN-001", "Ember Soy Candle", "Candles", 28, 9.5, 420, 150, 21, .16),
    ("KH-CAN-002", "Cedar & Sage Candle", "Candles", 32, 10.5, 380, 150, 21, .12),
    ("KH-CAN-003", "Candle Gift Set", "Candles", 64, 21, 150, 60, 28, .06),
    ("KH-CER-004", "Hand-Glazed Mug Set", "Ceramics", 54, 17, 210, 80, 35, .09),
    ("KH-CER-005", "Speckle Serving Bowl", "Ceramics", 46, 15, 130, 60, 35, .07),
    ("KH-LIN-006", "Stonewashed Linen Throw", "Linen", 89, 31, 38, 60, 42, .08),
    ("KH-LIN-007", "Linen Napkins (set of 4)", "Linen", 36, 11, 300, 100, 28, .09),
    ("KH-LIN-008", "Linen Duvet Cover", "Linen", 129, 46, 95, 40, 42, .04),
    ("KH-LGT-009", "Ceramic Table Lamp", "Lighting", 118, 41, 44, 30, 49, .04),
    ("KH-LGT-010", "Brass Taper Holders", "Lighting", 42, 13, 260, 90, 28, .07),
    ("KH-LGT-011", "Paper Shade Pendant", "Lighting", 76, 25, 120, 40, 49, .05),
    ("KH-DIF-012", "Reed Diffuser", "Fragrance", 34, 10, 390, 140, 21, .07),
]
products = pd.DataFrame(PRODUCTS, columns=["sku", "name", "category", "price", "cogs",
                                            "stock_on_hand", "reorder_point", "lead_time_days", "popularity"])
sku_p = (products.popularity / products.popularity.sum()).values
price_of = dict(zip(products.sku, products.price))
SPIKE_SKU = "KH-CER-004"

channels = ["meta", "google", "email", "organic", "direct"]
base_cvr = {"meta": .019, "google": .030, "email": .050, "organic": .026, "direct": .040}
dow_f = {0: .97, 1: .95, 2: .98, 3: 1.0, 4: 1.02, 5: 1.06, 6: 1.04}
REASONS = ["changed mind", "wrong size or colour", "late delivery", "damaged in transit", "not as described"]
REASON_P = [.30, .22, .18, .15, .15]

pool = list(range(6001, 10000))          # customers who existed before the window
cust_first_channel = {}
next_cid = 10001
orders, items = [], []
oid = 50001
HORIZON = END + pd.Timedelta(days=1)

for i, d in enumerate(dates):
    late = float(np.clip((i - 77) / 12, 0, 1))
    n = int(round(145 * dow_f[d.dayofweek] * (1 + 0.0006 * i) * (1 - 0.12 * late) * rng.normal(1, .05)))
    w = np.array([.28 - .06 * late, .17 - .02 * late, .15, .25, .15])
    w = w / w.sum()
    for _ in range(n):
        ts = d + pd.Timedelta(seconds=int(rng.integers(0, 86400)))
        ch = str(rng.choice(channels, p=w))
        is_new = rng.random() < (.66 - .06 * late)
        if is_new:
            cid = next_cid
            next_cid += 1
            pool.append(cid)
            cust_first_channel[cid] = ch
        else:
            cid = int(pool[int(rng.integers(len(pool)))])
        nl = int(rng.choice([1, 2, 3], p=[.6, .3, .1]))
        skus = rng.choice(products.sku, size=nl, replace=False, p=sku_p)
        lines, units = [], 0
        for s in skus:
            q = int(rng.choice([1, 2, 3], p=[.82, .14, .04]))
            lines.append((str(s), q, price_of[str(s)]))
            units += q
        subtotal = float(sum(q * p for _, q, p in lines))
        discount = 0.0
        if rng.random() < .10 + .12 * late:
            discount = round(subtotal * float(rng.choice([.10, .15, .20])), 2)
        revenue = round(subtotal - discount, 2)
        shipping = 0.0 if revenue >= 75 else 6.95

        r = rng.random()
        status = "cancelled" if r < .015 else "fulfilled"
        fulfilled_at = pd.NaT
        if status == "fulfilled":
            if i >= 87 and rng.random() < .05:
                status = "on_hold"
            else:
                hrs = float(rng.lognormal(np.log(20 + 14 * late), .5))
                fulfilled_at = ts + pd.Timedelta(hours=hrs)
                if fulfilled_at >= HORIZON:
                    status, fulfilled_at = "unfulfilled", pd.NaT

        refund, reason = 0.0, ""
        if status in ("fulfilled", "unfulfilled"):
            has_spike = SPIKE_SKU in [l[0] for l in lines] and i >= 66
            if rng.random() < (.35 if has_spike else .028):
                if has_spike:
                    line_val = [q * p for s, q, p in lines if s == SPIKE_SKU][0]
                    refund = round(min(float(line_val), revenue), 2)
                    reason = str(rng.choice(["damaged in transit", "not as described"], p=[.75, .25]))
                else:
                    refund = round(revenue * float(rng.choice([1.0, .5], p=[.7, .3])), 2)
                    reason = str(rng.choice(REASONS, p=REASON_P))

        country = str(rng.choice(["US", "CA", "GB", "AU"], p=[.78, .08, .09, .05]))
        orders.append(dict(order_id=oid, order_ts=ts.strftime("%Y-%m-%d %H:%M:%S"), order_date=d.strftime("%Y-%m-%d"),
                           customer_id=cid, channel=ch, is_new_customer=int(is_new), units=units,
                           subtotal=round(subtotal, 2), discount=discount, shipping=shipping, revenue=revenue,
                           status=status,
                           fulfilled_at=fulfilled_at.strftime("%Y-%m-%d %H:%M:%S") if pd.notna(fulfilled_at) else "",
                           refund_amount=refund, refund_reason=reason, country=country))
        for s, q, p in lines:
            items.append(dict(order_id=oid, sku=s, qty=q, unit_price=p, line_total=q * p))
        oid += 1

orders = pd.DataFrame(orders)
items = pd.DataFrame(items)

# ---------------- ad spend (platform-reported numbers, deliberately not equal to Shopify) ----------------
CAMPAIGNS = [  # platform, campaign, spend share, base CPA, CTR, CPM
    ("meta", "Meta | Prospecting", .42, 34, .011, 14),
    ("meta", "Meta | Retargeting", .13, 18, .020, 22),
    ("google", "Google | Shopping", .30, 26, .026, 9),
    ("google", "Google | Brand", .15, 12, .090, 4),
]
ads = []
for i, d in enumerate(dates):
    late = float(np.clip((i - 74) / 14, 0, 1))
    base = 4600 * dow_f[d.dayofweek] * rng.normal(1, .04)
    for plat, camp, share, cpa, ctr, cpm in CAMPAIGNS:
        prospect = camp.endswith("Prospecting")
        spend = base * share * (1 + (.80 if prospect else .10) * late) * rng.normal(1, .05)
        cpa_d = cpa * (1 + (.5 if prospect else .05) * late)
        ctr_d = ctr * (1 - (.22 if prospect else 0) * late)
        imps = spend / cpm * 1000
        clicks = imps * ctr_d
        purchases = int(rng.poisson(spend / cpa_d))
        ads.append(dict(date=d.strftime("%Y-%m-%d"), platform=plat, campaign=camp, spend=round(spend, 2),
                        impressions=int(imps), clicks=int(clicks), purchases=purchases,
                        revenue_attributed=round(purchases * float(rng.normal(68, 6)), 2)))
ads = pd.DataFrame(ads)

# ---------------- sessions (GA4-style) ----------------
live = orders.copy()
sess = []
for i, d in enumerate(dates):
    late = float(np.clip((i - 77) / 12, 0, 1))
    day = live[live.order_date == d.strftime("%Y-%m-%d")]
    for ch in channels:
        n_ch = int((day.channel == ch).sum())
        cvr = base_cvr[ch] * (1 - (.20 if ch == "meta" else 0) * late)
        s = int(round(n_ch / cvr * rng.normal(1, .04)))
        sess.append(dict(date=d.strftime("%Y-%m-%d"), source=ch, sessions=s,
                         add_to_cart_sessions=int(s * rng.normal(.085, .004)),
                         checkout_sessions=int(s * rng.normal(.040, .003))))
sess = pd.DataFrame(sess)

# ---------------- customers ----------------
ok = orders[orders.status != "cancelled"]
cust = ok.groupby("customer_id").agg(orders_in_period=("order_id", "count"),
                                     revenue_in_period=("revenue", "sum"),
                                     first_seen_in_period=("order_date", "min")).reset_index()
prior = {c: int(rng.integers(1, 3)) for c in pool if c < 10001}
cust["lifetime_orders"] = cust.apply(lambda r: r.orders_in_period + prior.get(r.customer_id, 0), axis=1)
cust["acquisition_channel"] = cust.customer_id.map(lambda c: cust_first_channel.get(c, str(rng.choice(channels))))
cust["customer_type"] = np.where(cust.customer_id >= 10001, "new_in_period", "existing")
cust["revenue_in_period"] = cust.revenue_in_period.round(2)

# ---------------- daily KPI table (this is what dashboards read) ----------------
o = ok.copy()
g = o.groupby("order_date")
k = pd.DataFrame({
    "orders": g.order_id.count(),
    "revenue": g.revenue.sum(),
    "units": g.units.sum(),
    "new_customers": g.is_new_customer.sum(),
    "refunds": g.refund_amount.sum(),
})
k["on_hold_orders"] = orders[orders.status == "on_hold"].groupby("order_date").order_id.count()
fh = o[o.status == "fulfilled"].copy()
fh["hrs"] = (pd.to_datetime(fh.fulfilled_at) - pd.to_datetime(fh.order_ts)).dt.total_seconds() / 3600
k["avg_fulfilment_hours"] = fh.groupby("order_date").hrs.mean()
k["sessions"] = sess.groupby("date").sessions.sum()
k["ad_spend"] = ads.groupby("date").spend.sum()
k = k.fillna({"on_hold_orders": 0}).reset_index().rename(columns={"order_date": "date"})
k["aov"] = k.revenue / k.orders
k["conversion_rate"] = k.orders / k.sessions
k["mer"] = k.revenue / k.ad_spend
k["cac"] = k.ad_spend / k.new_customers
k["refund_rate"] = k.refunds / k.revenue
k["repeat_order_share"] = 1 - k.new_customers / k.orders
cols = ["date", "revenue", "orders", "units", "aov", "sessions", "conversion_rate", "ad_spend", "mer",
        "new_customers", "cac", "repeat_order_share", "refunds", "refund_rate", "avg_fulfilment_hours", "on_hold_orders"]
k = k[cols].round(4)

SRC = {"revenue": "shopify", "orders": "shopify", "units": "shopify", "aov": "shopify", "sessions": "ga4",
       "conversion_rate": "shopify+ga4", "ad_spend": "ads", "mer": "shopify+ads", "new_customers": "shopify",
       "cac": "shopify+ads", "repeat_order_share": "shopify", "refunds": "shopify", "refund_rate": "shopify",
       "avg_fulfilment_hours": "shopify", "on_hold_orders": "shopify"}
long = k.melt(id_vars="date", var_name="metric", value_name="value")
long["source"] = long.metric.map(SRC)

products.drop(columns="popularity").to_csv(f"{OUT}/products.csv", index=False)
orders.to_csv(f"{OUT}/orders.csv", index=False)
items.to_csv(f"{OUT}/order_items.csv", index=False)
cust.to_csv(f"{OUT}/customers.csv", index=False)
ads.to_csv(f"{OUT}/ad_spend_daily.csv", index=False)
sess.to_csv(f"{OUT}/sessions_daily.csv", index=False)
k.to_csv(f"{OUT}/daily_kpis.csv", index=False)
long.to_csv(f"{OUT}/metrics_long.csv", index=False)

w1, w0 = k.tail(7), k.iloc[-14:-7]
def roll(x):
    return dict(revenue=x.revenue.sum(), orders=x.orders.sum(), aov=x.revenue.sum() / x.orders.sum(),
                conv=x.orders.sum() / x.sessions.sum(), mer=x.revenue.sum() / x.ad_spend.sum(),
                cac=x.ad_spend.sum() / x.new_customers.sum(), refund=x.refunds.sum() / x.revenue.sum(),
                repeat=1 - x.new_customers.sum() / x.orders.sum(), fulfil=x.avg_fulfilment_hours.mean())
print("last 7d:", {a: round(b, 4) for a, b in roll(w1).items()})
print("prior 7d:", {a: round(b, 4) for a, b in roll(w0).items()})
print(len(orders), "orders;", len(items), "items;", len(cust), "customers")
