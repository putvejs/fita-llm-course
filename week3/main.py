"""
Pipeline entry point — runs research and guide generation in sequence.
Usage: python main.py
"""
import importlib

from dotenv import load_dotenv

load_dotenv()


def run():
    step1 = importlib.import_module("1_research")
    step2 = importlib.import_module("2_guide")

    print("=== Step 1: Research Docker Compose topics ===")
    step1.run()

    print("\n=== Step 2: Generate structured cheatsheet ===")
    step2.run()

    print("\nDone. See output/research.md and output/cheatsheet.md.")


if __name__ == "__main__":
    run()
