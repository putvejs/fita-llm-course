# FITA LLM Course

Hands-on LLM course project — analysing a MySQL payment database using Claude AI.

---

## Environment Setup

Copy the example env file and fill in your credentials:

```bash
cp week2/.env.example week2/.env   # or week1/.env.example → week1/.env
```

`.env` contents:

```env
ANTHROPIC_API_KEY=sk-ant-...       # https://console.anthropic.com/

DB_HOST=your_mysql_host
DB_PORT=3306
DB_USER=your_db_user
DB_PASS=your_db_password
```

> **Never commit `.env`** — it is gitignored.

---

## Dataset Context

See [context.md](context.md) for the full description of the `direct_payments` database (schema, business domain, key facts, SQL notes).

---

## Week 1 — Text Analysis Pipeline

Connects to MySQL, generates aggregated SQL queries via Claude, runs them, and produces a Markdown report.

```
week1/
├── .env.example
├── requirements.txt
├── main.py              # runs all 3 steps
├── 1_explore_schema.py  # extract DB schema → output/context.json
├── 2_generate_sql.py    # Claude generates SQL queries → output/generated_queries.json
├── 3_describe_data.py   # run queries + Claude writes report → output/data_description.md
└── utils.py
```

### Run locally

```bash
cd week1
pip install -r requirements.txt
python main.py
# output: output/data_description.md
```

### Run with Docker

```bash
cd week1
docker compose up
```

---

## Week 2 — Visualization Pipeline + Interactive Dashboard

Reads `context.md`, generates a chart plan via Claude, executes SQL for each chart, creates matplotlib charts, and produces an HTML + PDF report. Also includes a live interactive web dashboard.

```
week2/
├── .env.example
├── requirements.txt
├── main.py              # runs all 3 pipeline steps
├── 1_plan.py            # reads context.md → Claude creates plan.md + plan.json
├── 2_execute.py         # SQL + matplotlib charts → output/charts/ + results.json
├── 3_report.py          # combines into report.html + report.pdf
├── app.py               # Flask interactive dashboard (port 5002)
├── templates/
│   └── dashboard.html
├── utils.py
├── Dockerfile
├── docker-compose.yml
└── output/
    ├── plan.md          # human-readable visualization plan
    ├── charts/          # generated PNG charts
    ├── report.html      # self-contained HTML report (base64 charts)
    └── report.pdf       # PDF version
```

### Run pipeline locally

```bash
cd week2
pip install -r requirements.txt
python main.py
# output: output/report.html, output/report.pdf
```

### Run steps individually

```bash
python 1_plan.py    # generate plan from context.md (no DB needed)
python 2_execute.py # generate charts (needs DB + Anthropic key)
python 3_report.py  # generate HTML + PDF from existing results
```

### Run interactive dashboard locally

```bash
cd week2
python app.py
# open http://localhost:5002
```

### Run with Docker

```bash
cd week2

# One-shot pipeline (generates report files):
docker compose run --rm pipeline

# Interactive dashboard (stays running):
docker compose up web
# open http://localhost:5002

# Both at once:
docker compose up
```

### Dashboard filters

| Filter | What it affects |
|---|---|
| Currency | GBP / EUR / All |
| Vertical | Industry sector (7 options) |
| Source | dashboard / app / api |
| From / To | Month range (2018-03 → 2020-03) |

All 5 charts and summary stats update live on filter change.

---

## Repository Structure

```
fita-llm-course/
├── context.md       # dataset context (schema, domain, key facts)
├── README.md
├── week1/
└── week2/
```
