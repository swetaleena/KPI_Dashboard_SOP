# Pilot Kit: sell it, set it up, deliver it

Everything you need around the build: finding clients, getting their data, running the setup, and demoing.

---

## 1. Discovery call questions (30 min)

Ask these before you show anything. Write the answers down; they become the client's thresholds, SOPs and your case study.

**Numbers**
1. Which 5 numbers do you check every day? Where do you check them?
2. What number do you wish you could see but cannot?
3. What was your best and worst week in the last 3 months, and how did you find out?
4. What is your target for MER or ROAS, CAC, refund rate and fulfilment time? (If they do not know, that is your opening.)

**Processes**
5. When ad performance drops, what happens? Who is told? How long until someone acts?
6. What breaks when your most important person is out for a week?
7. Which tasks do you explain over and over? Where are your processes written down today?
8. Who owns refunds, stock reordering and stuck orders?

**Tools and access**
9. Shopify plan? Which ad platforms? GA4? Klaviyo? Which helpdesk? Slack or WhatsApp?
10. Who can give me read-only access?

**Buying**
11. What would make this obviously worth it in 30 days?
12. Who else needs to say yes?

---

## 2. Qualification: is this a good client?

Good fit: $50k to $2M per month in sales, Shopify, running paid ads, 3 to 20 staff, a founder who is still the bottleneck.
Poor fit: under $20k per month (too small to pay), over $5M per month with an in-house data team, or no one who can own the SOPs.

---

## 3. Data access request (send after the call)

> Hi [Name], thanks for the time today. To build your dashboard I need read-only access so I can see your numbers without being able to change anything:
>
> 1. **Shopify:** add me as a Staff account with only Orders, Products and Analytics permissions (Settings → Users and permissions). Or export Orders for the last 12 months (Orders → Export → CSV) and Products.
> 2. **Meta Ads:** share the ad account with me at "Analyst" (view-only) level in Business Settings.
> 3. **Google Ads:** invite me with "Read only" access.
> 4. **GA4:** add me as "Viewer".
> 5. A list of your team and their roles, and any process documents you already have (even messy ones).
>
> I will confirm everything I can see and delete any exports when we finish if you ask. First dashboard version within 48 hours of access.

Always say what you will see, what you will not touch, and how data is stored.

---

## 4. Delivery plan (2 weeks)

| Day | Work | Output |
|---|---|---|
| 1 | Access, exports, timezone and currency check | Data loaded |
| 2 | Write the metric dictionary with the client (use `kpi_definitions.csv`) | Agreed definitions |
| 3 to 4 | Build the dashboard, reconcile to Shopify (QA checklist) | Live dashboard v1 |
| 5 | Review call: set thresholds from their history | Signed-off thresholds |
| 6 to 8 | Write their 5 to 8 real SOPs with the people who do the work | SOP set v1 |
| 9 | Connect thresholds to SOPs, test alerts, set owners | Working alert loop |
| 10 | Train the team (30 min), each person acknowledges their SOPs | Team in the system |
| 11 to 14 | Watch real alerts, adjust thresholds, fix confusion | Tuned system |

**Done means:** a breach created a task, the right person did the checklist, and the KPI recovered or the cause was found.

---

## 5. Live demo script (10 minutes)

1. **Open with their pain, not the tool (1 min).** "You told me when ROAS drops, it takes about a week for anyone to act. Let me show you how this works on a sample store."
2. **Show the dashboard (2 min).** Eight numbers, week-over-week arrows. "Everything here is defined in writing, so it matches Shopify."
3. **Point at Needs action (1 min).** "Six KPIs are in alert. Three of them have the same cause: ad efficiency."
4. **Create the alert live (3 min).** Change a threshold or run the script. Show the task appear with the checklist, owner and due date.
5. **Show the SOP (1 min).** One step at a time. "A new hire can do this without asking you."
6. **Show the hidden insight (1 min).** Refunds by product: "One product is causing most of the refunds. Nobody saw it in Shopify's summary."
7. **Close (1 min).** "On your real data, this takes about 2 weeks. Want me to build your first dashboard version for free from a 12-month export so you can judge?"

**Tips:** keep the story to one problem. Let the client touch the threshold. Never claim the sample data is real.

---

## 6. Pitch outline (6 to 8 slides)

1. The problem: numbers and processes live in different places, so nothing happens when a number moves.
2. What it costs: one sample figure, for example "$X of wasted spend per week while nobody noticed" (use the client's own numbers).
3. The solution: KPI → threshold → SOP task → owner (one diagram).
4. Live demo (or screenshots).
5. How setup works (the 2-week plan above).
6. What you get: dashboard, 8 SOPs written for your business, alerts, team training.
7. Pricing (see below).
8. Next step: free first dashboard from their export.

**Pricing to test:** setup $800 to $2,500 depending on sources and number of SOPs, plus $149 to $499 per month for maintenance, threshold tuning and one monthly review call. Test it. Do not trust these numbers until three clients have answered.

---

## 7. Case-study template (fill in after each pilot)

- **Client type:** [e.g. home goods, $400k per month]
- **Problem before:** [e.g. found a ROAS drop 8 days late]
- **What we built:** [dashboard, 7 SOPs, Slack alerts]
- **Result after 30 days:** [e.g. breach to action time from 8 days to 1 day; refund rate from 5.4% to 3.1%]
- **Quote from the client:** [one sentence]
- **What the team used:** [dashboard opens per week, SOPs completed, alerts acted on]

Get the numbers from the system itself: task `created_at` vs the time steps were completed.
