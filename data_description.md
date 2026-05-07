# Data Description Report

# Direct Payments Database — Data Description Report

---

## 1. Database Overview

The `direct_payments` database captures the operational data of a **direct debit payment processing platform**, likely a GoCardless-style payment collection service used by businesses to collect recurring or one-off payments from their customers via bank debit schemes.

The database models three core entities:

- **Organisations** (431 records) — the merchant businesses onboarded to the platform, each classified by an industry vertical (e.g. healthcare, sports & fitness, property).
- **Mandates** (9,381 records) — authorisation agreements set up between organisations and their end-customers under a specific payment scheme (BACS or SEPA Core), enabling future payment collection.
- **Payments** (33,461 records) — individual payment transactions linked to mandates, carrying amount, currency, payment source, creation timestamp, and scheduled charge date.

The platform supports both **GBP/BACS** (UK domestic) and **EUR/SEPA Core** (European) payment rails, and payments can be initiated via a dashboard UI, a mobile app, or an API integration. The dataset spans approximately **15 months of activity** from March 2018 through to mid-2019, capturing what appears to be a **growth-stage platform** rapidly scaling its merchant base and transaction volume.

---

## 2. Key Metrics

### 💰 Revenue & Payments

| Metric | Value |
|---|---|
| Total payments processed | 33,461 |
| Total revenue (all currencies) | **~£4.28M equivalent** |
| Total GBP revenue | £3,998,939.69 |
| Total EUR revenue | €280,616.83 |
| Overall average payment (GBP) | £125.78 |
| Overall average payment (EUR) | €168.24 |
| Largest single payment (GBP) | £10,160.00 |
| Largest single payment (EUR) | €4,819.50 |
| Smallest payment (both currencies) | £/€1.00 |

### 🏦 Mandates & Schemes

| Scheme | Mandates | Organisations | Payments | Revenue |
|---|---|---|---|---|
| BACS | 9,017 | 213 | 31,793 | £3,998,939.69 |
| SEPA Core | 364 | 15 | 1,668 | €280,616.83 |

### 🏢 Organisations & Verticals

| Metric | Value |
|---|---|
| Total organisations | 431 |
| Total industry verticals | 7 |
| Largest vertical by revenue | Digital Services, Media & Telecoms (~£1.19M) |
| Largest vertical by payment volume | Sports & Fitness (12,170 payments) |
| Highest avg. payment vertical | Digital Services, Media & Telecoms (~£297 avg.) |

### 📅 Cohort Growth (Organisation Sign-ups)

| Month | New Orgs | Mandates Created | Payments Made | Revenue |
|---|---|---|---|---|
| 2018-03 | 10 | 109 | 742 | £307,008.57 |
| 2018-04 | 132 | 3,945 | 15,403 | £1,574,606.53 |
| 2018-05 | 153 | 2,273 | 7,798 | £1,213,435.20 |
| 2018-06 | 136 | 3,054 | 9,518 | £1,184,506.22 |

---

## 3. Notable Patterns & Insights

### 📈 Explosive Early Growth Followed by Rapid Stabilisation
The platform launched in March 2018 with just a single payment of £50.00. By April, payment count jumped to 105, and by July 2018 it reached **2,369 payments per month** — representing more than a **2,000× increase in monthly volume** within five months. All 431 organisations signed up within a four-month window (March–June 2018), suggesting either a **platform launch event** or a **bulk merchant onboarding campaign** rather than organic rolling acquisition.

### 🏆 Extreme Revenue Concentration at the Top
The single highest-revenue organisation — a **healthcare provider** — generated £305,346.57 across just 729 payments, averaging an unusually high **£418.86 per payment**. The top 10 organisations collectively account for a disproportionately large share of total revenue, indicating classic **power-law customer concentration risk**. The top organisation alone represents roughly **7.6% of total GBP revenue**.

### ⚖️ High Payment Volume ≠ High Revenue (Tradesmen vs. Healthcare)
The **tradesmen & non-professional services** vertical processed 8,080 payments but generated only £381,776 (avg. £47.25/payment), while **healthcare** generated £305,347 from just 729 payments (avg. £418.86). This highlights a **fundamental difference in payment profiles** across verticals — high-frequency/low-value vs. low-frequency/high-value — with important implications for platform economics and customer lifetime value.

### 📊 Dashboard Dominates Revenue; API Delivers Highest Average Value
Despite accounting for only **6.9% of payment volume**, API-sourced payments carry the **highest average value at £185.34**, suggesting API users tend to be larger, more sophisticated merchants processing higher-ticket transactions. Dashboard payments lead in total revenue (£2.77M) and volume (17,693 payments), while app-sourced payments, though second in volume (13,452), have the **lowest average value at £80.39** — likely reflecting consumer-facing or lower-tier merchant use cases.

### 🕐 Digital Services Has the Longest Collection Lag — and an Outlier
The **digital services, media & telecoms** vertical has the highest average days-to-charge at **8.84 days**, compared to the overall minimum of ~5 days seen in most other verticals. More strikingly, this vertical has a **maximum charge lag of 368 days** — nearly a full year between payment creation and charge date — which is a significant outlier warranting investigation. This could indicate scheduled annual billing, a data quality issue, or a backdated mandate.

### 🌍 SEPA/EUR Remains a Minor but Higher-Value Channel
EUR/SEPA Core payments represent only **5% of total payment volume** but command a **34% higher average payment value** (€168.24 vs. £125.78). With just 15 organisations using SEPA, there appears to be a significant **untapped European market opportunity**, particularly if the higher average transaction values observed reflect genuine pricing differences in the EU market.

### 📅 April 2018 Cohort Is Disproportionately Productive
The April 2018 cohort (132 organisations) generated £1.57M in revenue from 15,403 payments and created 3,945 mandates — **more mandates than any other cohort despite not being the largest in organisation count** (May 2018 had 153 organisations). This cohort appears to contain some of the platform's highest-volume merchants and may represent a strategically important group for retention analysis.

---

## 4. Potential Use Cases

### 🔍 Revenue & Financial Analysis
- **Revenue forecasting**: Use monthly trend data and cohort payment curves to model future revenue trajectories.
- **Currency/scheme P&L split**: Assess profitability by scheme to evaluate whether SEPA expansion is financially worthwhile.
- **Payment size distribution analysis**: Segment organisations by average payment size to tailor pricing tiers or fee structures.

### 🎯 Customer Segmentation & Retention
- **High-value customer identification**: Flag organisations in the top revenue decile for dedicated account management or churn prevention programmes.
- **Vertical-based segmentation**: Develop tailored product features or pricing for high-value verticals (e.g. healthcare, property) vs. high-volume verticals (e.g. sports & fitness).
- **Cohort lifetime value analysis**: Track how revenue per cohort evolves over time to identify which sign-up months produced the most durable, high-value customers.

### ⚙️ Operational & Risk Management
- **Charge lag monitoring**: Investigate and remediate outlier charge lags (e.g. the 368-day case in digital services) to reduce settlement risk and improve cash flow predictability.
- **Mandate utilisation analysis**: Identify dormant mandates (mandates with no associated payments) to target re-engagement campaigns or mandate hygiene processes.
- **Source channel optimisation**: Evaluate whether API/dashboard/app channel differences justify differentiated support, onboarding, or feature investment.

### 📣 Growth & Product Strategy
- **Vertical expansion prioritisation**: Use revenue-per-organisation and average payment metrics to evaluate which new verticals to target for merchant acquisition.
- **European market sizing**: Assess SEPA pipeline and higher EUR average values to build a business case for EU-focused sales or localisation efforts.
- **Onboarding effectiveness**: Correlate organisation sign-up month with time-to-first-payment and mandate creation rate to optimise the merchant activation funnel.

---

*Report generated from database `direct_payments` on server `87.110.123.151`, extracted 2026-05-07. All revenue figures reflect raw payment amounts and do not account for refunds, failures, or platform fees.*