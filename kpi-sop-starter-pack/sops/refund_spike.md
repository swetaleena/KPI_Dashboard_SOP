# Refund spike review

| | |
|---|---|
| SOP ID | `refund_spike` |
| Owner | Support lead |
| Time needed | about 30 minutes |
| Version | 1.0 |

## Purpose
Find which product or process is causing refunds and fix it at the source.

## When to run it
Refund rate crosses its threshold.

## Tools you need
Shopify admin, refund export, carrier tracking, supplier contact

## Steps

- [ ] **1.** Export refunds from the last 14 days. Tag each by reason.
  - Log: Export file
- [ ] **2.** Group by SKU. Flag any SKU with a refund rate above 8% or three or more refunds with the same reason.
  - Log: Flagged SKUs
- [ ] **3.** If the reason is damaged in transit: check carrier, packaging and supplier batch. Ask 3 customers for photos.
  - Log: Photos and carrier notes
- [ ] **4.** If the reason is not as described: compare the product page photos and copy with the real product. Fix the page.
  - Log: Page updated
- [ ] **5.** Decide the action: pause ads to the SKU, change packaging, or switch carrier. Record the owner and date.
  - Log: Decision log
- [ ] **6.** Update the support macro and FAQ for this issue.
  - Log: Macro link
- [ ] **7.** Add findings and cost impact to the weekly review.
  - Log: Note added

## Done when
Cause is identified, a fix has an owner and a date, and support has an updated macro.

## Escalate to
Founder, if one SKU shows a refund rate above 15% or a safety issue is suspected.

## Version history
| Version | Date | Change | Changed by |
|---|---|---|---|
| 1.0 | | First version | |
