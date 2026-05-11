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
| `amount` | double | Payment amount in minor units (pence / cents) |
| `currency` | varchar(50) | `GBP` or `EUR` |
| `created_at` | datetime | When the payment was created |
| `source` | varchar(50) | `dashboard`, `app`, or `api` |
| `charge_date` | datetime | When funds are collected from the customer |
| `mandate_id` | varchar(50) | FK → mandates.id |

> **Note:** `amount` is stored in pence/cents. Divide by 100 for display values (e.g. £125.78 avg).

---

## Key Facts

- **Total GBP revenue:** £3,998,939 across 31,793 payments (avg £125.78)
- **Total EUR revenue:** €280,617 across 1,668 payments (avg €168.24)
- **Top vertical by volume:** Sports & Fitness (12,170 payments, 36% of total)
- **Top vertical by revenue:** Digital Services (£1.19M, avg £297/payment)
- **Top payment source:** Dashboard (52.9% of payments, 64.4% of revenue)
- **SEPA mandates** are 30% more productive per mandate than BACS (4.58 vs 3.53 avg payments)
- **Avg charge lag:** 5–9 days from payment creation to charge date

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
- Amounts are stored as `double` — cast to `DECIMAL(10,2)` for formatted output
