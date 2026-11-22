# Order exception handling

| | |
|---|---|
| SOP ID | `order_exceptions` |
| Owner | Ops manager |
| Time needed | about 20 minutes |
| Version | 1.0 |

## Purpose
Clear stuck, failed and risky orders before customers have to ask.

## When to run it
On-hold orders above threshold, or average fulfilment time above threshold.

## Tools you need
Shopify admin, fraud app, warehouse or 3PL portal, support inbox

## Steps

- [ ] **1.** In Shopify, filter orders that are on hold, unfulfilled for 48 hours or more, or payment pending.
  - Log: Count of orders
- [ ] **2.** For fraud-flagged orders, check address mismatch, repeated cards and unusual quantities. Approve or cancel each.
  - Log: Decision per order
- [ ] **3.** For orders stuck in fulfilment, contact the warehouse or 3PL and find out why (stock, picking, carrier).
  - Log: Warehouse reply
- [ ] **4.** Message affected customers with a new delivery estimate using the saved template.
  - Log: Template used
- [ ] **5.** Tag resolved orders 'exception-resolved' and note the cause.
  - Log: Tag applied
- [ ] **6.** If three or more orders share one cause, open a fix ticket.
  - Log: Ticket link

## Done when
No order has been on hold or unfulfilled for more than 48 hours.

## Escalate to
Founder, if more than 5% of weekly orders are affected.

## Version history
| Version | Date | Change | Changed by |
|---|---|---|---|
| 1.0 | | First version | |
