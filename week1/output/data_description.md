# Data Description Report

# Direct Payments Database — Data Description Report

> **Source:** `direct_payments` database on server `87.110.123.151`
> **Extracted:** 2026-05-07 | **Tables:** `mandates`, `organisations`, `payments`

---

## 1. Database Overview

The `direct_payments` database supports a **direct debit payment processing platform** — similar in nature to services like GoCardless. It captures the full lifecycle of recurring payment collection across three core entities:

- **Organisations** — the merchant customers (businesses) using the platform, classified by industry vertical.
- **Mandates** — authorisations granted by end-customers to organisations, enabling recurring debits under a specific scheme (e.g. BACS or SEPA).
- **Payments** — individual debit transactions executed against those mandates, carrying amount, currency, source, and charge date information.

The platform serves **431 organisations** across **7 industry verticals**, has processed **33,461 payments** against **9,381 mandates**, and spans activity from approximately **March 2018 through early 2020**. It operates primarily in GBP (UK BACS) with a secondary EUR (SEPA) footprint.

---

## 2. Key Metrics

### 💰 Revenue & Volume

| Metric | Value |
|---|---|
| Total payments processed | 33,461 |
| Total revenue (all currencies) | ~£4.28M equivalent |
| GBP revenue | £3,998,939.69 (31,793 payments) |
| EUR revenue | €280,616.83 (1,668 payments) |
| Overall average payment (GBP) | £125.78 |
| Overall average payment (EUR) | €168.24 |
| Largest single payment (GBP) | £10,160.00 |
| Largest single payment (EUR) | €4,819.50 |

### 🏦 Mandates & Schemes

| Scheme | Mandates | Payments | Avg Payments / Mandate |
|---|---|---|---|
| BACS (GBP) | 9,017 (96.1%) | 31,793 | 3.53 |
| SEPA Core (EUR) | 364 (3.9%) | 1,668 | 4.58 |

### 🏭 Revenue by Industry Vertical (Top 5)

| Vertical | Orgs | Mandates | Payments | Revenue | Avg Payment |
|---|---|---|---|---|---|
| Digital Services / Media / Telecoms | 70 | 720 | 3,995 | £1,186,462 | £296.99 |
| Professional & Financial Services | 44 | 926 | 5,126 | £803,472 | £156.74 |
| Sports & Fitness | 43 | 3,839 | 12,170 | £734,094 | £60.32 |
| Property | 24 | 476 | 2,545 | £634,363 | £249.26 |
| Tradesmen & Non-Professional Services | 17 | 2,205 | 8,080 | £381,776 | £47.25 |

### 📡 Revenue by Payment Source

| Source | Payments | Revenue | Avg Payment | Active Period |
|---|---|---|---|---|
| Dashboard | 17,693 | £2,768,934 | £156.50 | Apr 2018 – Mar 2020 |
| App | 13,452 | £1,081,376 | £80.39 | Apr 2018 – Mar 2019 |
| API | 2,316 | £429,247 | £185.34 | Apr 2018 – Jul 2019 |

---

## 3. Notable Patterns & Insights

### 📈 Rapid Early Growth, Then Plateau
Monthly data shows explosive platform growth from launch:
- **March 2018:** 1 payment (£50) — likely a test transaction.
- **April 2018:** 105 payments (£12,270) — soft launch.
- **May → June 2018:** Volume jumps from 499 to 1,453 payments — clear onboarding acceleration.
- **July 2018:** 2,369 payments — near 5,000% growth within four months of launch.

The dataset covers 13 months of full data, suggesting strong early traction with potential tapering toward the end of the observed window.

### 🏆 Extreme Revenue Concentration at the Top
The top organisation alone (`cb4fb7740...`, **Healthcare**) generated **£305,347** — approximately **7.6% of total GBP revenue** from just 729 payments at a high average of £418.86. The top 10 organisations collectively account for a disproportionate share of total revenue, indicating a **long-tail distribution** typical of B2B payment platforms. This concentration represents both an opportunity (upsell) and a risk (churn sensitivity).

### 🎯 High-Value vs. High-Volume Verticals — A Clear Divide
Two distinct business models coexist on the platform:

- **High-value, low-volume:** Digital Services (£297 avg), Property (£249 avg), Healthcare — likely subscription services, invoicing, or rent collection with large individual amounts.
- **High-volume, low-value:** Sports & Fitness (£60 avg, 12,170 payments) and Tradesmen (£47 avg, 8,080 payments) — consistent with gym memberships and recurring service fees at modest price points.

Sports & Fitness is the **single highest-volume vertical** (36% of all payments) yet ranks only third by revenue, underscoring the importance of not using payment count alone as a proxy for value.

### 🌍 SEPA Mandates Are More Productive Per Mandate
Despite being only 3.9% of mandates, SEPA Core mandates average **4.58 payments per mandate** versus **3.53 for BACS** — a ~30% higher utilisation rate. This may indicate SEPA organisations have longer-tenured or more frequently billed customers, or that the SEPA segment skews toward higher-frequency billing cycles.

### 🖥️ Dashboard Dominates; App Has Shorter Lifespan
The **dashboard** is the dominant payment creation channel (52.9% of payments, 64.4% of revenue) and remains active through March 2020 — the full observable window. The **app** channel, while significant in volume, has a **latest charge date of March 2019**, suggesting it was either deprecated or migrated into another channel. The **API** channel commands the highest average payment (£185.34), pointing to sophisticated/automated merchant integrations handling larger transactions.

### ⏱️ Collection Lag is Short but Variable
All verticals maintain a minimum lead time of **3 days** between payment creation and charge date — consistent with BACS/SEPA regulatory processing windows. However, outliers are notable:
- **Digital Services** has a maximum lag of **368 days** — suggesting either far-future scheduled payments or potential data quality issues.
- **Sports & Fitness** reaches 175 days maximum, while most other verticals stay within 40–100 days.
- The **average lag of 5–9 days** across all verticals suggests the platform predominantly processes near-term collections rather than long-horizon scheduled payments.

---

## 4. Potential Use Cases

### 🔍 Customer & Revenue Analytics
- **Churn risk modelling:** Identify organisations with declining payment frequency or mandate-to-payment conversion ratios.
- **Revenue forecasting:** Use monthly trend data and average payment cadence to project near-term collection volumes.
- **Customer segmentation:** Cluster organisations by vertical, average payment size, and mandate utilisation to tailor pricing tiers or account management resources.

### 📊 Platform Health & Growth Monitoring
- **Mandate activation rates:** Compare total mandates (9,381) to payment-generating mandates to quantify dormant/inactive mandates and prioritise re-engagement.
- **Onboarding funnel analysis:** Combine organisation creation dates with first mandate and first payment dates to measure time-to-value for new merchants.
- **Channel migration analysis:** Investigate the apparent sunset of the `app` source channel and its impact on volume.

### 💼 Commercial & Strategic Decision-Making
- **Vertical expansion targeting:** Healthcare and Property show high average payment values but relatively few organisations — strong candidates for targeted sales campaigns.
- **SEPA growth opportunity:** SEPA mandates are more productive per mandate yet represent only ~4% of the base. A focused EUR market expansion could yield disproportionate revenue gains.
- **Top-account retention programmes:** Given the revenue concentration in the top 10 organisations, dedicated key account management would protect a significant share of platform revenue.

### ⚙️ Operational & Risk Management
- **Anomalous charge lag investigation:** Payments with charge dates 100–368 days after creation warrant review for scheduling errors, fraud patterns, or legitimate use cases requiring documentation.
- **Scheme compliance monitoring:** Tracking BACS vs. SEPA payment patterns supports regulatory reporting and scheme fee optimisation.
- **API integration health:** The lower volume but higher-value API channel suggests enterprise integrations that merit SLA monitoring and dedicated support.

---

*Report generated from aggregated query results as of 2026-05-07. One query (quarterly onboarding trends) failed due to a SQL `ONLY_FULL_GROUP_BY` mode constraint and could not be included; re-running with an explicit `DATE_FORMAT` on `created_at` in the GROUP BY clause would recover this data.*