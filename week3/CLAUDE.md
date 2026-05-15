# week3 — Docker Compose Q&A Assistant

## What this project does

Uses Claude (Sonnet 4.6) to learn about Docker Compose in two ways:
1. **Pipeline** — LLM researches 9 Docker Compose topics and generates a cheatsheet (Markdown output)
2. **Web UI** — Flask chat interface where you ask Docker Compose questions and get answers

All three services run via Docker Compose. Logs are captured by Docker's json-file driver and viewable in Dozzle.

## Services

| Service    | What it does                                  | URL                   |
|------------|-----------------------------------------------|-----------------------|
| `pipeline` | One-shot: research + cheatsheet generation    | —                     |
| `web`      | Always-on: interactive Q&A chat               | http://localhost:5003 |
| `logs`     | Dozzle: Docker-native real-time log viewer    | http://localhost:9999 |

## Models used

See `models.yml`. All LLM calls use `claude-sonnet-4-6` via the `anthropic` Python SDK.

## Quick start

```bash
cp .env.example .env
# Fill in ANTHROPIC_API_KEY

# Run the research pipeline (generates output/research.md + output/cheatsheet.md)
docker compose run pipeline

# Start the Q&A web UI and log viewer
docker compose up web logs

# Or run everything
docker compose up
```

## Running locally (no Docker)

```bash
pip install -r requirements.txt
cp .env.example .env        # add key

python main.py              # pipeline: research + cheatsheet
python app.py               # web UI on port 5003
```

## File structure

| File               | Purpose                                              |
|--------------------|------------------------------------------------------|
| `1_research.py`    | Queries Claude on 9 Docker Compose topics            |
| `2_guide.py`       | Asks Claude to produce a cheatsheet from research    |
| `app.py`           | Flask server: `/api/ask`, `/api/logs`, `/health`     |
| `main.py`          | Sequential pipeline runner (step 1 → step 2)         |
| `models.yml`       | Declares which models and SDK versions are used      |
| `docker-compose.yml` | Defines pipeline, web, and logs services           |
| `Dockerfile`       | python:3.12-slim, copies week3/, exposes 5003        |
| `templates/chat.html` | Chat UI with markdown rendering and live log panel |
| `tests/`           | Unit tests (no API calls — safe to run in CI)        |
| `.github/workflows/ci.yml` | GitHub Actions: run tests + docker build   |
| `output/`          | Generated files (gitignored): research.json/md, cheatsheet.md |

## Logging

`app.py` writes logs to **stdout only** — Docker captures them via the `json-file` driver.

```bash
docker compose logs -f web      # tail web service logs
docker compose logs pipeline    # see pipeline run output
```

Dozzle at http://localhost:9999 gives a browser-based view of all container logs in real time.

## Tests

```bash
pip install pytest
pytest tests/ -v
```

Tests cover: topic list integrity, output JSON structure (if pipeline has run), Flask `/health`, `/api/logs`, and error handling for missing `question`. No real API calls are made in tests.

## CI (GitHub Actions)

`.github/workflows/ci.yml` runs on push/PR to `main`:
- Installs deps and runs `pytest tests/`
- Builds the Docker image to catch Dockerfile regressions

## Environment variables

| Variable           | Required | Description                  |
|--------------------|----------|------------------------------|
| `ANTHROPIC_API_KEY`| Yes      | Anthropic API key            |
