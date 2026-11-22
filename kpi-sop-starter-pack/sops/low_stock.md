# Low-stock reorder

| | |
|---|---|
| SOP ID | `low_stock` |
| Owner | Ops manager |
| Time needed | about 25 minutes |
| Version | 1.0 |

## Purpose
Reorder before a bestseller goes out of stock.

## When to run it
One or more SKUs fall below their reorder point.

## Tools you need
Products table or inventory app, supplier contacts, purchase order template

## Steps

- [ ] **1.** List every SKU below its reorder point. Calculate days of cover: stock divided by average daily units over the last 14 days.
  - Log: SKU list with cover
- [ ] **2.** Mark any SKU where days of cover is shorter than supplier lead time as urgent.
  - Log: Urgent list
- [ ] **3.** Request a quote and confirm lead time from the supplier.
  - Log: Supplier reply
- [ ] **4.** Raise the purchase order. Record PO number, quantity and expected arrival.
  - Log: PO number
- [ ] **5.** For urgent SKUs, reduce ad spend on the product and add 'ships in X days' or backorder messaging.
  - Log: Changes made
- [ ] **6.** Update the reorder point if demand has changed.
  - Log: New reorder point

## Done when
A purchase order is raised for every urgent SKU, and stock messaging is updated.

## Escalate to
Founder, if lead time is longer than stock cover for a top-5 SKU.

## Version history
| Version | Date | Change | Changed by |
|---|---|---|---|
| 1.0 | | First version | |
