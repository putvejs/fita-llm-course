"""
Step 2: Use Claude to generate a practical Docker Compose cheatsheet from research.
Run standalone: python 2_guide.py  (requires output/research.json from step 1)
"""
import json
import os

import anthropic
from dotenv import load_dotenv

load_dotenv()

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


def run():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    research_path = os.path.join(OUTPUT_DIR, "research.json")
    if not os.path.exists(research_path):
        raise FileNotFoundError("Run 1_research.py first to generate output/research.json")

    with open(research_path) as f:
        research = json.load(f)

    context = "\n\n".join(
        f"### {r['topic']}\n{r['content']}" for r in research["topics"]
    )

    client = anthropic.Anthropic()
    print("  Generating cheatsheet with Claude...")

    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": (
                    "Based on the Docker Compose research below, write a concise, practical "
                    "cheatsheet in Markdown. Structure it as:\n"
                    "1. Quick command reference table\n"
                    "2. Annotated docker-compose.yml template (with inline comments)\n"
                    "3. Networking tips (2-3 bullet points)\n"
                    "4. Logging tips (2-3 bullet points)\n"
                    "5. Top 5 production gotchas\n\n"
                    f"Research:\n\n{context}"
                ),
            }
        ],
    )

    cheatsheet = msg.content[0].text

    out_path = os.path.join(OUTPUT_DIR, "cheatsheet.md")
    with open(out_path, "w") as f:
        f.write(cheatsheet)

    print(f"  Saved cheatsheet to {out_path}")
    print(f"  Tokens used: {msg.usage.input_tokens + msg.usage.output_tokens:,}")
    return cheatsheet


if __name__ == "__main__":
    run()
