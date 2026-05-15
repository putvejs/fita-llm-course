"""
Step 1: Use Claude to research Docker Compose topics and save structured output.
Run standalone: python 1_research.py
"""
import json
import os
from datetime import datetime

import anthropic
from dotenv import load_dotenv

load_dotenv()

TOPICS = [
    "What is Docker Compose and what problem does it solve?",
    "Key concepts: services, networks, and volumes",
    "Essential docker compose commands (up, down, ps, logs, exec, build, pull)",
    "docker-compose.yml structure: image, build, ports, env_file, volumes, depends_on, restart",
    "Networking between services: how containers communicate by service name",
    "Environment variables and secrets management (.env files, env_file, environment:)",
    "Health checks and restart policies (restart: unless-stopped, healthcheck:)",
    "Logging configuration: driver options (json-file, syslog), viewing logs with docker compose logs",
    "Production best practices: resource limits, read-only containers, named volumes, multi-stage builds",
]

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


def research_topic(client: anthropic.Anthropic, topic: str) -> dict:
    print(f"  Researching: {topic}")
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        messages=[
            {
                "role": "user",
                "content": (
                    f"You are a Docker Compose expert. Explain clearly and concisely:\n\n{topic}\n\n"
                    "Include a practical example where relevant. Be thorough but focused."
                ),
            }
        ],
    )
    return {
        "topic": topic,
        "content": msg.content[0].text,
        "model": msg.model,
        "input_tokens": msg.usage.input_tokens,
        "output_tokens": msg.usage.output_tokens,
    }


def run():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    client = anthropic.Anthropic()

    results = []
    for topic in TOPICS:
        result = research_topic(client, topic)
        results.append(result)

    json_path = os.path.join(OUTPUT_DIR, "research.json")
    with open(json_path, "w") as f:
        json.dump({"generated_at": datetime.now().isoformat(), "topics": results}, f, indent=2)

    md_path = os.path.join(OUTPUT_DIR, "research.md")
    with open(md_path, "w") as f:
        f.write("# Docker Compose Research\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n---\n\n")
        for r in results:
            f.write(f"## {r['topic']}\n\n{r['content']}\n\n---\n\n")

    total_tokens = sum(r["input_tokens"] + r["output_tokens"] for r in results)
    print(f"  Saved {len(results)} topics to output/. Total tokens: {total_tokens:,}")
    return results


if __name__ == "__main__":
    run()
