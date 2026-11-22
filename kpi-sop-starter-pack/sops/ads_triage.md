# Ad account triage

| | |
|---|---|
| SOP ID | `ads_triage` |
| Owner | Media buyer |
| Time needed | about 35 minutes |
| Version | 1.0 |

## Purpose
Find and stop wasted ad spend within a day of it appearing.

## When to run it
MER, CAC or conversion rate crosses its threshold. Also run every Monday.

## Tools you need
Meta Ads Manager, Google Ads, Shopify admin, the KPI dashboard

## Steps

- [ ] **1.** Open the dashboard. Note which of MER, CAC and conversion breached, and by how much.
  - Log: Screenshot of the KPI cards
- [ ] **2.** In each ad platform, sort campaigns by spend. List any with spend above 2x target CAC and no purchases.
  - Log: List of campaign names
- [ ] **3.** Check creative fatigue: frequency above 3.5, or click-through rate down more than 25% vs the prior 14 days.
  - Log: List of flagged ads
- [ ] **4.** Compare platform-reported purchases with Shopify orders for the last 7 days. A gap above 25% means check the pixel and Conversions API.
  - Log: Both numbers
- [ ] **5.** Check traffic quality: mobile vs desktop conversion, page speed, and whether any advertised product is out of stock.
  - Log: Short notes
- [ ] **6.** Pause the waste, move about 20% of budget from the worst to the best campaign, and queue 2 new creatives.
  - Log: Change log
- [ ] **7.** Set a recheck in 48 hours and post a summary in the team channel.
  - Log: Link to the message

## Done when
Changes are logged, a 48-hour recheck is scheduled, and the summary is posted in the team channel.

## Escalate to
Founder, if MER stays below 2.0 for 5 or more days after the changes.

## Version history
| Version | Date | Change | Changed by |
|---|---|---|---|
| 1.0 | | First version | |
