"""Unit tests for week3 pipeline — no API calls required."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_topics_not_empty():
    import importlib
    m = importlib.import_module("1_research")
    assert len(m.TOPICS) > 0, "TOPICS list must not be empty"


def test_all_topics_are_strings():
    import importlib
    m = importlib.import_module("1_research")
    assert all(isinstance(t, str) and t.strip() for t in m.TOPICS)


def test_output_dir_points_to_output_folder():
    import importlib
    m = importlib.import_module("1_research")
    assert m.OUTPUT_DIR.endswith("output")


def test_research_json_structure_if_exists():
    output_path = os.path.join(os.path.dirname(__file__), "..", "output", "research.json")
    if not os.path.exists(output_path):
        return  # pipeline hasn't run yet; skip
    with open(output_path) as f:
        data = json.load(f)
    assert "generated_at" in data
    assert "topics" in data
    assert all("topic" in t and "content" in t for t in data["topics"])


def test_cheatsheet_has_content_if_exists():
    out = os.path.join(os.path.dirname(__file__), "..", "output", "cheatsheet.md")
    if not os.path.exists(out):
        return
    assert len(open(out).read()) > 100


def test_flask_health():
    import importlib
    app_mod = importlib.import_module("app")
    client = app_mod.app.test_client()
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_flask_ask_requires_question():
    import importlib
    app_mod = importlib.import_module("app")
    client = app_mod.app.test_client()
    resp = client.post("/api/ask", json={})
    assert resp.status_code == 400


def test_flask_logs_endpoint():
    import importlib
    app_mod = importlib.import_module("app")
    client = app_mod.app.test_client()
    resp = client.get("/api/logs")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "lines" in data
    assert isinstance(data["lines"], list)
