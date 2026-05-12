# Dataset Context — `direct_payments` Database

## Source

| Property | Value |
|---|---|
| Host | `87.110.123.151` |
| Database | `direct_payments` |
| Extracted | 2026-05-11 |
| Total records | 431 organisations · 9,381 mandates · 33,461 payments |

---

## Business Domain

A **direct debit payment processing platform** (GoCardless-style) covering the full lifecycle of recurring payment collection:

- **Organisations** — merchant customers (businesses) using the platform, grouped by industry vertical
- **Mandates** — authorisations granted by end-customers to organisations, enabling recurring debits under a payment scheme (BACS or SEPA)
- **Payments** — individual debit transactions executed against those mandates

Data spans **March 2018 – March 2020** and operates in GBP (BACS) and EUR (SEPA Core).

---

## Schema

### `organisations` (431 rows)

| Column | Type | Notes |
|---|---|---|
| `id` | varchar(50) | Unique organisation identifier |
| `created_at` | datetime | When the organisation joined the platform |
| `parent_vertical` | varchar(50) | Industry vertical (7 distinct values) |

**Industry verticals:** Digital Services / Media / Telecoms, Professional & Financial Services, Sports & Fitness, Property, Tradesmen & Non-Professional Services, Healthcare, Other

---

### `mandates` (9,381 rows)

| Column | Type | Notes |
|---|---|---|
| `id` | varchar(50) | Unique mandate identifier |
| `created_at` | datetime | When the mandate was authorised |
| `scheme` | varchar(50) | `BACS` (GBP, 96%) or `SEPA_CORE` (EUR, 4%) |
| `organisation_id` | varchar(50) | FK → organisations.id |

---

### `payments` (33,461 rows)

| Column | Type | Notes |
|---|---|---|
| `id` | varchar(50) | Unique payment identifier |
| `amount` | double | Payment amount in pounds / euros (not pence) |
| `currency` | varchar(50) | `GBP` or `EUR` |
| `created_at` | datetime | When the payment was created |
| `source` | varchar(50) | `dashboard`, `app`, or `api` |
| `charge_date` | datetime | When funds are collected from the customer |
| `mandate_id` | varchar(50) | FK → mandates.id |

> **Note:** `amount` is stored as actual currency units (pounds/euros), not pence/cents. Use directly.

---

## Key Metrics

### Revenue & Volume

| Metric | Value |
|---|---|
| Total payments processed | 33,461 |
| Total revenue (all currencies) | ~£4.28M equivalent |
| GBP revenue | £3,998,939 (31,793 payments) |
| EUR revenue | €280,617 (1,668 payments) |
| Avg payment (GBP) | £125.78 |
| Avg payment (EUR) | €168.24 |
| Largest single payment (GBP) | £10,160 |
| Largest single payment (EUR) | €4,819.50 |

### Mandates & Schemes

| Scheme | Mandates | Payments | Avg Payments / Mandate |
|---|---|---|---|
| BACS (GBP) | 9,017 (96.1%) | 31,793 | 3.53 |
| SEPA Core (EUR) | 364 (3.9%) | 1,668 | 4.58 |

### Revenue by Industry Vertical

| Vertical | Orgs | Mandates | Payments | Revenue | Avg Payment |
|---|---|---|---|---|---|
| Digital Services / Media / Telecoms | 70 | 720 | 3,995 | £1,186,462 | £296.99 |
| Professional & Financial Services | 44 | 926 | 5,126 | £803,472 | £156.74 |
| Sports & Fitness | 43 | 3,839 | 12,170 | £734,094 | £60.32 |
| Property | 24 | 476 | 2,545 | £634,363 | £249.26 |
| Tradesmen & Non-Professional Services | 17 | 2,205 | 8,080 | £381,776 | £47.25 |
| Healthcare | — | — | 1,317 | £368,034 | — |
| Societies & Clubs | — | — | 228 | £171,355 | — |

### Revenue by Payment Source

| Source | Payments | Revenue | Avg Payment | Active Period |
|---|---|---|---|---|
| Dashboard | 17,693 | £2,768,934 | £156.50 | Apr 2018 – Mar 2020 |
| App | 13,452 | £1,081,376 | £80.39 | Apr 2018 – Mar 2019 |
| API | 2,316 | £429,247 | £185.34 | Apr 2018 – Jul 2019 |

---

## Notable Patterns & Insights

### Rapid Early Growth
- March 2018: 1 payment (£50) — test transaction
- April 2018: 105 payments (£12,270) — soft launch
- May → June 2018: 499 → 1,453 payments — onboarding acceleration
- July 2018: 2,369 payments — ~5,000% growth in four months
- Growth appears to plateau toward end of observed window (Mar 2020)

### Revenue Concentration
- Top organisation alone generated £305,347 (7.6% of total GBP revenue), 729 payments at £418.86 avg
- Classic long-tail B2B distribution — top 10 orgs hold disproportionate share

### High-Value vs High-Volume Verticals
- **High-value, low-volume:** Digital Services (£297 avg), Property (£249 avg), Healthcare — subscriptions, invoicing, rent
- **High-volume, low-value:** Sports & Fitness (£60 avg, 36% of all payments), Tradesmen (£47 avg) — gym memberships, recurring service fees
- Sports & Fitness is #1 by volume but only #3 by revenue

### SEPA Mandates More Productive
- SEPA mandates: 4.58 avg payments/mandate vs BACS: 3.53 — ~30% higher utilisation
- Despite being only 3.9% of mandate base

### Payment Source Lifecycle
- Dashboard dominates (52.9% payments, 64.4% revenue) — active full window through Mar 2020
- App channel last active Mar 2019 — appears deprecated or migrated
- API channel commands highest avg payment (£185.34) — enterprise integrations

### Collection Lag
- Minimum 3 days between creation and charge date (BACS/SEPA processing window)
- Average lag 5–9 days across verticals
- Digital Services outlier: max 368-day lag (possible data quality issue)
- Sports & Fitness: up to 175 days max

---

## Relationships

```
organisations (431)
    └── mandates (9,381)  via mandate.organisation_id → organisation.id
            └── payments (33,461)  via payment.mandate_id → mandate.id
```

---

## SQL Notes (MySQL)

- Server runs with `ONLY_FULL_GROUP_BY` enabled — every non-aggregated `SELECT` column must appear verbatim in `GROUP BY`
- Use `DATE_FORMAT(created_at, '%Y-%m')` for month-level grouping and include it in `GROUP BY`
- Amounts are stored as `double` in actual currency units (not pence) — cast to `DECIMAL(10,2)` for formatted output
