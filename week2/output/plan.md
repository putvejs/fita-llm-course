# Visualization Plan

Generated: 2026-05-11 19:17  
Context: [context.md](../context.md)

---

## 1. Monthly Payment Volume & Revenue Trend (Mar 2018 – Mar 2020)

**Chart type:** `line`  
**X axis:** Month  
**Y axis:** Total Revenue (£)

Tracks how total payment count and GBP revenue have grown over time, revealing seasonality, growth phases, and any revenue dips that need attention.

> **SQL hint:** JOIN payments → mandates → organisations; GROUP BY DATE_FORMAT(payments.created_at, '%Y-%m'); aggregate COUNT(*) and SUM(amount/100) WHERE currency='GBP'; order by month ascending

---

## 2. Revenue by Industry Vertical

**Chart type:** `horizontal_bar`  
**X axis:** Total Revenue (£)  
**Y axis:** Industry Vertical

Compares total GBP revenue contributed by each industry vertical to identify the highest-value customer segments and guide sales/marketing prioritisation.

> **SQL hint:** JOIN payments → mandates → organisations; GROUP BY organisations.parent_vertical; aggregate SUM(payments.amount/100) WHERE currency='GBP'; order by revenue descending

---

## 3. Payment Count by Industry Vertical

**Chart type:** `bar`  
**X axis:** Industry Vertical  
**Y axis:** Number of Payments

Shows transaction volume per vertical so that high-volume but lower-value verticals (e.g. Sports & Fitness) can be distinguished from high-value, lower-volume ones (e.g. Digital Services).

> **SQL hint:** JOIN payments → mandates → organisations; GROUP BY organisations.parent_vertical; aggregate COUNT(payments.id); order by count descending

---

## 4. Payment Source Mix: Volume vs Revenue Share

**Chart type:** `bar`  
**X axis:** Payment Source  
**Y axis:** Total Revenue (£)

Compares dashboard, app, and API channels across both payment count and total revenue to reveal which integration channel drives the most value and where to invest in tooling.

> **SQL hint:** FROM payments; GROUP BY source; aggregate COUNT(*) and SUM(amount/100) WHERE currency='GBP'; returns three rows: dashboard, app, api

---

## 5. Mandate Productivity by Scheme (Avg Payments per Mandate)

**Chart type:** `bar`  
**X axis:** Payment Scheme  
**Y axis:** Avg Payments per Mandate

Contrasts BACS and SEPA_CORE mandates on average payments generated per mandate, quantifying the 30% productivity premium of SEPA and informing scheme expansion decisions.

> **SQL hint:** JOIN payments → mandates; GROUP BY mandates.scheme; aggregate COUNT(payments.id) / COUNT(DISTINCT mandates.id) as avg_payments; returns BACS and SEPA_CORE rows

---

## 6. Average Payment Value by Industry Vertical

**Chart type:** `horizontal_bar`  
**X axis:** Average Payment Value (£)  
**Y axis:** Industry Vertical

Reveals which verticals command the highest average transaction size, helping prioritise upsell efforts and identify verticals with premium pricing power.

> **SQL hint:** JOIN payments → mandates → organisations; GROUP BY organisations.parent_vertical; aggregate AVG(payments.amount/100) WHERE currency='GBP'; order by avg value descending

---

## 7. New Mandate Creation vs New Organisation Onboarding Over Time

**Chart type:** `line`  
**X axis:** Month  
**Y axis:** Count

Overlays monthly new mandate authorisations against new organisation sign-ups to assess whether existing merchants are expanding their customer base or whether growth is purely driven by new merchant acquisition.

> **SQL hint:** Two series: (1) SELECT DATE_FORMAT(created_at,'%Y-%m'), COUNT(*) FROM mandates GROUP BY DATE_FORMAT(created_at,'%Y-%m'); (2) SELECT DATE_FORMAT(created_at,'%Y-%m'), COUNT(*) FROM organisations GROUP BY DATE_FORMAT(created_at,'%Y-%m'); join on month
