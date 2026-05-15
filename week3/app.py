"""
Flask web UI: interactive Docker Compose Q&A assistant with log viewer.
Run: python app.py  (or via Docker Compose — port 5003)

Logs go to stdout so Docker captures them via its json-file driver.
View with: docker compose logs -f web
"""
import collections
import logging
import os

import anthropic
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()

# ── Logging: stdout only — Docker owns persistence via json-file driver ────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger(__name__)

# In-memory ring buffer so the web UI can show recent log lines
_log_buffer: collections.deque[str] = collections.deque(maxlen=100)


class _BufferHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        _log_buffer.append(self.format(record))


_buf_handler = _BufferHandler()
_buf_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logging.getLogger().addHandler(_buf_handler)

# ── App ────────────────────────────────────────────────────────────────────────
app = Flask(__name__)
client = anthropic.Anthropic()

SYSTEM_PROMPT = (
    "You are a Docker Compose expert assistant. Answer questions clearly and concisely. "
    "Include practical examples and commands where relevant. "
    "Focus on Docker Compose specifically unless the question requires broader Docker context. "
    "Format code blocks with triple backticks and the language name."
)


@app.route("/")
def index():
    return render_template("chat.html")


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = (data or {}).get("question", "").strip()
    history = (data or {}).get("history", [])

    if not question:
        return jsonify({"error": "question is required"}), 400

    log.info("Q: %s", question[:120])

    messages = []
    for turn in history[-6:]:  # keep last 3 exchanges as context
        messages.append({"role": turn["role"], "content": turn["content"]})
    messages.append({"role": "user", "content": question})

    try:
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=messages,
        )
        answer = msg.content[0].text
        log.info("A: %s... [%d tokens out]", answer[:80], msg.usage.output_tokens)
        return jsonify({"answer": answer, "model": msg.model})
    except Exception as e:
        log.error("API error: %s", e)
        return jsonify({"error": str(e)}), 500


@app.route("/api/logs")
def get_logs():
    """Return recent log lines from the in-memory buffer (last 50)."""
    lines = list(_log_buffer)[-50:]
    return jsonify({"lines": lines})


if __name__ == "__main__":
    log.info("Starting Docker Compose Q&A assistant on port 5003")
    app.run(host="0.0.0.0", port=5003, debug=False)
