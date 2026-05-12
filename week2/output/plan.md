# Visualization Plan

Generated: 2026-05-12 09:28  
Context: [context.md](../context.md)

---

## 1. Monthly Payment Volume & Revenue Growth (Apr 2018 – Mar 2020)

**Chart type:** `line`  
**X axis:** Month  
**Y axis:** Total Revenue (£)

Tracks the platform's growth trajectory over time, revealing the explosive ramp-up from soft launch through plateau. Helps identify inflection points and assess whether growth is sustained or decelerating heading into Mar 2020.

> **SQL hint:** JOIN payments → mandates → organisations; GROUP BY DATE_FORMAT(p.created_at, '%Y-%m'); aggregate SUM(p.amount) and COUNT(p.id); filter currency = 'GBP' for clean single-currency trend

---

## 2. Revenue vs Payment Volume by Industry Vertical

**Chart type:** `bar`  
**X axis:** Industry Vertical  
**Y axis:** Total Revenue (£)

Contrasts which verticals generate the most money versus the most transactions, exposing the high-value/low-volume (Digital Services, Property) vs high-volume/low-value (Sports & Fitness, Tradesmen) strategic split. Critical for pricing and acquisition decisions.

> **SQL hint:** JOIN payments → mandates → organisations; GROUP BY o.parent_vertical; aggregate SUM(p.amount) as revenue and COUNT(p.id) as payment_count; include avg amount for annotation; filter GBP

---

## 3. Average Payment Value by Industry Vertical

**Chart type:** `horizontal_bar`  
**X axis:** Average Payment (£)  
**Y axis:** Industry Vertical

Ranks verticals by average transaction size to identify premium segments. Highlights that Digital Services customers pay nearly 6x more per transaction than Tradesmen, informing customer lifetime value estimates and targeted upsell strategies.

> **SQL hint:** JOIN payments → mandates → organisations; GROUP BY o.parent_vertical; aggregate AVG(p.amount); ORDER BY AVG(p.amount) DESC; filter currency = 'GBP'

---

## 4. Payment Source Mix: Volume & Revenue Contribution

**Chart type:** `bar`  
**X axis:** Payment Source  
**Y axis:** Total Revenue (£)

Shows how Dashboard, App, and API channels compare on both payment count and revenue share. Reveals the App channel's deprecation after Mar 2019 and the API channel's premium positioning, informing channel investment and migration planning.

> **SQL hint:** SELECT p.source, COUNT(p.id) as payment_count, SUM(p.amount) as revenue, AVG(p.amount) as avg_payment FROM payments p GROUP BY p.source; no joins required

---

## 5. Top 15 Organisations by Revenue Contribution

**Chart type:** `horizontal_bar`  
**X axis:** Total Revenue (£)  
**Y axis:** Organisation ID

Visualises the long-tail revenue concentration, showing how a handful of organisations dominate total revenue. The top org alone accounts for 7.6% of GBP revenue. Essential for key account management and churn risk assessment.

> **SQL hint:** JOIN payments → mandates → organisations; GROUP BY o.id; aggregate SUM(p.amount); ORDER BY SUM(p.amount) DESC; LIMIT 15; filter currency = 'GBP'

---

## 6. Mandate Productivity: Average Payments per Mandate by Vertical

**Chart type:** `bar`  
**X axis:** Industry Vertical  
**Y axis:** Avg Payments per Mandate

Measures how actively mandates are being used across verticals — a proxy for customer engagement and recurring billing health. Low utilisation may signal mandates created but not actioned, representing unrealised revenue.

> **SQL hint:** JOIN mandates → organisations, then LEFT JOIN payments; GROUP BY o.parent_vertical; aggregate COUNT(p.id) / COUNT(DISTINCT m.id) as payments_per_mandate; include both BACS and SEPA

---

## 7. Monthly New Mandate Authorisations Over Time

**Chart type:** `line`  
**X axis:** Month  
**Y axis:** New Mandates Authorised

Tracks the rate at which new end-customers are granting direct debit permissions, serving as a leading indicator of future payment volume. A slowdown in mandate creation predicts revenue growth deceleration before it appears in payment figures.

> **SQL hint:** SELECT DATE_FORMAT(m.created_at, '%Y-%m') as month, COUNT(m.id) as new_mandates FROM mandates m GROUP BY DATE_FORMAT(m.created_at, '%Y-%m') ORDER BY month ASC
