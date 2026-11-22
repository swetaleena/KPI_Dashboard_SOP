"""
Writes the config tables and SOP documents. Edit the dictionaries below, re-run, and everything stays in sync.

Run:  python build_config.py
Output: ../config/*.csv and ../sops/*.md
"""
import os
import csv

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CFG, SOPDIR = os.path.join(ROOT, "config"), os.path.join(ROOT, "sops")
os.makedirs(CFG, exist_ok=True)
os.makedirs(SOPDIR, exist_ok=True)

# ---------------------------------------------------------------- KPI definitions
KPI_DEFS = [
    # kpi, name, definition, formula, sources, rules, unit, window, why
    ("revenue_per_day", "Revenue per day", "Product sales after discounts, before refunds, excluding shipping and tax.",
     "SUM(subtotal - discount) / days", "orders", "Exclude cancelled orders. Use the store timezone for order_date.", "USD", "7-day average",
     "Top-line health. Compare to the prior 7 days."),
    ("orders_per_day", "Orders per day", "Count of non-cancelled orders.", "COUNT(order_id) / days", "orders",
     "Exclude cancelled. Count on_hold orders (they are real demand).", "count", "7-day average", "Volume trend independent of price."),
    ("aov", "Average order value", "Revenue divided by orders.", "SUM(revenue) / COUNT(orders)", "orders",
     "Same exclusions as revenue.", "USD", "7-day", "Shows effect of discounts and bundling."),
    ("conversion_rate", "Conversion rate", "Orders divided by sessions.", "COUNT(orders) / SUM(sessions)", "orders, sessions_daily",
     "Sessions from GA4 or Shopify analytics. Be consistent about which one you use.", "fraction (0.026 = 2.6%)", "7-day",
     "Early signal of traffic quality or site problems."),
    ("mer", "Marketing efficiency ratio (blended ROAS)", "Total revenue divided by total ad spend across all platforms.",
     "SUM(revenue) / SUM(ad_spend)", "orders, ad_spend_daily", "Use Shopify revenue, never platform-reported revenue. Spend in one currency.", "ratio", "7-day",
     "The one ad number that is not distorted by platform attribution."),
    ("cac", "Blended customer acquisition cost", "Ad spend divided by new customers.", "SUM(ad_spend) / SUM(new_customers)",
     "orders, ad_spend_daily", "New customer = first order ever. Does not include agency or creative costs unless you add them.", "USD", "7-day",
     "Tells you if growth is still profitable."),
    ("repeat_order_share", "Repeat order share", "Share of orders placed by returning customers.", "1 - new_customers / orders", "orders",
     "True 90-day repeat rate needs 90+ days of history per cohort. This is the daily proxy.", "fraction", "7-day",
     "Retention health. Cheap to move, expensive to ignore."),
    ("refund_rate", "Refund rate", "Refunded value divided by revenue.", "SUM(refund_amount) / SUM(revenue)", "orders",
     "Attributed to the ORDER date, not the refund date. Real refunds lag, so look back 14 to 30 days when reviewing.", "fraction", "7-day",
     "Catches product, packaging and carrier problems."),
    ("avg_fulfilment_hours", "Average fulfilment time", "Hours from order placed to marked fulfilled.", "AVG(fulfilled_at - order_ts)", "orders",
     "Fulfilled orders only. Orders still unfulfilled are tracked by on_hold_orders and the exceptions SOP.", "hours", "7-day average",
     "Slow fulfilment drives support tickets and refunds."),
    ("on_hold_orders", "Orders on hold", "Orders stuck in on_hold status (fraud review, payment, stock).", "COUNT(status = 'on_hold')", "orders",
     "Counted on order date.", "count", "7-day total", "Stuck orders are lost revenue and angry customers."),
    ("skus_below_reorder", "SKUs below reorder point", "Number of products with stock under their reorder point.",
     "COUNT(stock_on_hand < reorder_point)", "products", "Snapshot, not a time series.", "count", "current", "Prevents stockouts."),
]
with open(f"{CFG}/kpi_definitions.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["kpi", "name", "definition", "formula", "source_tables", "rules", "unit", "window", "why_it_matters"])
    w.writerows(KPI_DEFS)

# ---------------------------------------------------------------- thresholds (edit per client)
# kpi, direction, alert_at, critical_at, sop_id, owner_role
# direction 'min' = bad when value is BELOW the threshold; 'max' = bad when ABOVE.
THRESHOLDS = [
    ("revenue_per_day", "min", 11000, 9500, "weekly_review", "Founder"),
    ("orders_per_day", "min", 115, 100, "weekly_review", "Founder"),
    ("aov", "min", 85, 80, "weekly_review", "Founder"),
    ("conversion_rate", "min", 0.026, 0.024, "ads_triage", "Media buyer"),
    ("mer", "min", 2.5, 2.0, "ads_triage", "Media buyer"),
    ("cac", "max", 60, 75, "ads_triage", "Media buyer"),
    ("repeat_order_share", "min", 0.30, 0.25, "weekly_review", "Founder"),
    ("refund_rate", "max", 0.04, 0.06, "refund_spike", "Support lead"),
    ("avg_fulfilment_hours", "max", 36, 48, "order_exceptions", "Ops manager"),
    ("on_hold_orders", "max", 10, 25, "order_exceptions", "Ops manager"),
    ("skus_below_reorder", "max", 0, 3, "low_stock", "Ops manager"),
]
with open(f"{CFG}/kpi_thresholds.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["kpi", "direction", "alert_at", "critical_at", "sop_id", "owner_role"])
    w.writerows(THRESHOLDS)

# ---------------------------------------------------------------- SOPs
# step = (text, est_min, evidence to log)
SOPS = {
    "ads_triage": dict(
        name="Ad account triage", owner="Media buyer", mins=35,
        trigger="MER, CAC or conversion rate crosses its threshold. Also run every Monday.",
        purpose="Find and stop wasted ad spend within a day of it appearing.",
        tools="Meta Ads Manager, Google Ads, Shopify admin, the KPI dashboard",
        done="Changes are logged, a 48-hour recheck is scheduled, and the summary is posted in the team channel.",
        escalate="Founder, if MER stays below 2.0 for 5 or more days after the changes.",
        steps=[
            ("Open the dashboard. Note which of MER, CAC and conversion breached, and by how much.", 3, "Screenshot of the KPI cards"),
            ("In each ad platform, sort campaigns by spend. List any with spend above 2x target CAC and no purchases.", 8, "List of campaign names"),
            ("Check creative fatigue: frequency above 3.5, or click-through rate down more than 25% vs the prior 14 days.", 6, "List of flagged ads"),
            ("Compare platform-reported purchases with Shopify orders for the last 7 days. A gap above 25% means check the pixel and Conversions API.", 5, "Both numbers"),
            ("Check traffic quality: mobile vs desktop conversion, page speed, and whether any advertised product is out of stock.", 5, "Short notes"),
            ("Pause the waste, move about 20% of budget from the worst to the best campaign, and queue 2 new creatives.", 5, "Change log"),
            ("Set a recheck in 48 hours and post a summary in the team channel.", 3, "Link to the message"),
        ]),
    "order_exceptions": dict(
        name="Order exception handling", owner="Ops manager", mins=20,
        trigger="On-hold orders above threshold, or average fulfilment time above threshold.",
        purpose="Clear stuck, failed and risky orders before customers have to ask.",
        tools="Shopify admin, fraud app, warehouse or 3PL portal, support inbox",
        done="No order has been on hold or unfulfilled for more than 48 hours.",
        escalate="Founder, if more than 5% of weekly orders are affected.",
        steps=[
            ("In Shopify, filter orders that are on hold, unfulfilled for 48 hours or more, or payment pending.", 3, "Count of orders"),
            ("For fraud-flagged orders, check address mismatch, repeated cards and unusual quantities. Approve or cancel each.", 6, "Decision per order"),
            ("For orders stuck in fulfilment, contact the warehouse or 3PL and find out why (stock, picking, carrier).", 5, "Warehouse reply"),
            ("Message affected customers with a new delivery estimate using the saved template.", 3, "Template used"),
            ("Tag resolved orders 'exception-resolved' and note the cause.", 2, "Tag applied"),
            ("If three or more orders share one cause, open a fix ticket.", 1, "Ticket link"),
        ]),
    "refund_spike": dict(
        name="Refund spike review", owner="Support lead", mins=30,
        trigger="Refund rate crosses its threshold.",
        purpose="Find which product or process is causing refunds and fix it at the source.",
        tools="Shopify admin, refund export, carrier tracking, supplier contact",
        done="Cause is identified, a fix has an owner and a date, and support has an updated macro.",
        escalate="Founder, if one SKU shows a refund rate above 15% or a safety issue is suspected.",
        steps=[
            ("Export refunds from the last 14 days. Tag each by reason.", 6, "Export file"),
            ("Group by SKU. Flag any SKU with a refund rate above 8% or three or more refunds with the same reason.", 5, "Flagged SKUs"),
            ("If the reason is damaged in transit: check carrier, packaging and supplier batch. Ask 3 customers for photos.", 8, "Photos and carrier notes"),
            ("If the reason is not as described: compare the product page photos and copy with the real product. Fix the page.", 5, "Page updated"),
            ("Decide the action: pause ads to the SKU, change packaging, or switch carrier. Record the owner and date.", 3, "Decision log"),
            ("Update the support macro and FAQ for this issue.", 2, "Macro link"),
            ("Add findings and cost impact to the weekly review.", 1, "Note added"),
        ]),
    "low_stock": dict(
        name="Low-stock reorder", owner="Ops manager", mins=25,
        trigger="One or more SKUs fall below their reorder point.",
        purpose="Reorder before a bestseller goes out of stock.",
        tools="Products table or inventory app, supplier contacts, purchase order template",
        done="A purchase order is raised for every urgent SKU, and stock messaging is updated.",
        escalate="Founder, if lead time is longer than stock cover for a top-5 SKU.",
        steps=[
            ("List every SKU below its reorder point. Calculate days of cover: stock divided by average daily units over the last 14 days.", 6, "SKU list with cover"),
            ("Mark any SKU where days of cover is shorter than supplier lead time as urgent.", 3, "Urgent list"),
            ("Request a quote and confirm lead time from the supplier.", 5, "Supplier reply"),
            ("Raise the purchase order. Record PO number, quantity and expected arrival.", 5, "PO number"),
            ("For urgent SKUs, reduce ad spend on the product and add 'ships in X days' or backorder messaging.", 4, "Changes made"),
            ("Update the reorder point if demand has changed.", 2, "New reorder point"),
        ]),
    "product_launch": dict(
        name="New product launch checklist", owner="Founder", mins=90,
        trigger="Manual. Start 7 days before a planned launch.",
        purpose="Launch without broken pages, stockouts or unprepared support.",
        tools="Shopify admin, email platform, ad platforms, the KPI dashboard",
        done="Product is live, launch KPIs are on the dashboard, and the 24-hour review is complete.",
        escalate="Founder decides on any go or no-go issue.",
        steps=[
            ("Confirm the product page: photos, copy, size guide, price and shipping info.", 15, "Page link"),
            ("Test checkout end to end on mobile with a real discount code.", 10, "Test order number"),
            ("Confirm inventory counts and set the reorder point.", 5, "Stock and reorder point"),
            ("Schedule email, SMS and social posts.", 15, "Schedule links"),
            ("Brief support on FAQs, returns policy and macros.", 10, "Brief sent"),
            ("Set launch ad budgets and creatives. Add UTM tags.", 15, "Campaign names"),
            ("Add launch KPIs to the dashboard and book a 24-hour review.", 10, "Calendar invite"),
            ("At 24 hours, review sales, conversion and issues. Decide what to change.", 10, "Review notes"),
        ]),
    "support_escalation": dict(
        name="Customer support escalation", owner="Support lead", mins=20,
        trigger="Agent flags a ticket, a chargeback arrives, a VIP writes in, or a customer contacts us a third time.",
        purpose="Resolve high-risk tickets fast and consistently.",
        tools="Helpdesk, Shopify admin, payment provider",
        done="The customer has a resolution, the outcome is logged, and a follow-up is scheduled.",
        escalate="Founder, for legal threats, safety issues or any resolution above the approved limit.",
        steps=[
            ("Review the customer's order and ticket history.", 4, "Summary"),
            ("Set severity. P1: chargeback, legal or safety. P2: repeated failure or high value. P3: everything else.", 2, "Severity tag"),
            ("Reply within 2 hours for P1 and 8 hours for P2.", 4, "Reply sent"),
            ("Offer a resolution within approved limits (refund, replacement or credit).", 4, "Resolution offered"),
            ("Log the outcome and a root-cause tag.", 3, "Tag applied"),
            ("Follow up in 3 days.", 3, "Follow-up sent"),
        ]),
    "weekly_review": dict(
        name="Weekly performance review", owner="Founder", mins=45,
        trigger="Every Monday morning.",
        purpose="Keep every KPI owned and every breach followed up.",
        tools="The KPI dashboard, the task list",
        done="Every red KPI has an owner and a date, and one priority and one experiment are chosen.",
        escalate="Not applicable.",
        steps=[
            ("Open the dashboard and compare the last 7 days with the prior 7.", 5, "Screenshot"),
            ("Review each KPI marked as a breach. Confirm an open task exists for it.", 10, "Task links"),
            ("Review open tasks. Close, reassign or re-date anything overdue.", 10, "Updated task list"),
            ("Review last week's experiment: result and decision.", 8, "Decision"),
            ("Choose one priority and one experiment for this week.", 7, "Written down"),
            ("Post the summary in the team channel.", 5, "Message link"),
        ]),
    "new_hire_onboarding": dict(
        name="New hire onboarding", owner="Ops manager", mins=120,
        trigger="A new team member's start date is confirmed.",
        purpose="Make a new hire productive in their first week.",
        tools="Shopify, email, chat, password manager, the KPI dashboard and SOP system",
        done="The new hire has completed one SOP independently and acknowledged all SOPs for their role.",
        escalate="Founder, if the 30-day check-in raises concerns.",
        steps=[
            ("Create accounts with role-based access: Shopify, email, chat, password manager, dashboard.", 20, "Access checklist"),
            ("Share the company overview, brand voice guide and product catalogue.", 20, "Links shared"),
            ("Walk through the dashboard: what each KPI means and what the thresholds are.", 20, "Walkthrough done"),
            ("Shadow each SOP assigned to the role once.", 30, "SOPs shadowed"),
            ("Complete one SOP independently with a reviewer's sign-off.", 20, "Reviewer sign-off"),
            ("Acknowledge each SOP in the SOP system.", 5, "Acknowledgements"),
            ("Book the 30-day check-in.", 5, "Calendar invite"),
        ]),
}

with open(f"{CFG}/sops.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["sop_id", "name", "owner_role", "est_minutes", "trigger", "purpose", "tools", "done_when", "escalate_to", "version"])
    for sid, s in SOPS.items():
        w.writerow([sid, s["name"], s["owner"], s["mins"], s["trigger"], s["purpose"], s["tools"], s["done"], s["escalate"], "1.0"])

with open(f"{CFG}/sop_steps.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["sop_id", "step_no", "step", "est_minutes", "evidence_to_log"])
    for sid, s in SOPS.items():
        for n, (t, m, e) in enumerate(s["steps"], 1):
            w.writerow([sid, n, t, m, e])

for sid, s in SOPS.items():
    lines = [f"# {s['name']}", "",
             "| | |", "|---|---|",
             f"| SOP ID | `{sid}` |", f"| Owner | {s['owner']} |", f"| Time needed | about {s['mins']} minutes |",
             "| Version | 1.0 |", "", "## Purpose", s["purpose"], "", "## When to run it", s["trigger"], "",
             "## Tools you need", s["tools"], "", "## Steps", ""]
    for n, (t, m, e) in enumerate(s["steps"], 1):
        lines += [f"- [ ] **{n}.** {t}", f"  - Log: {e}"]
    lines += ["", "## Done when", s["done"], "", "## Escalate to", s["escalate"], "",
              "## Version history", "| Version | Date | Change | Changed by |", "|---|---|---|---|", "| 1.0 | | First version | |", ""]
    with open(f"{SOPDIR}/{sid}.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

with open(f"{SOPDIR}/_TEMPLATE.md", "w", encoding="utf-8") as f:
    f.write("""# [SOP name]

| | |
|---|---|
| SOP ID | `short_snake_case_id` |
| Owner | [role, not a person's name] |
| Time needed | about [N] minutes |
| Version | 1.0 |

## Purpose
One sentence: what problem does this prevent or solve?

## When to run it
The exact trigger. If it is a KPI, name the KPI and threshold.

## Tools you need
List every login or document needed.

## Steps
Write each step so a new hire can do it without asking. One action per step. Start with a verb.

- [ ] **1.** [Action]
  - Log: [what evidence to record: a number, a link, a screenshot]
- [ ] **2.** [Action]
  - Log: [evidence]

## Done when
A checkable finish line, not "when it feels fixed".

## Escalate to
Who, and under what condition.

## Version history
| Version | Date | Change | Changed by |
|---|---|---|---|
| 1.0 | | First version | |
""")
print("wrote", len(SOPS), "SOPs and config tables")
