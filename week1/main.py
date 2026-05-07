"""
Pipeline entry point — runs all 3 steps in sequence.
Usage: python main.py  (or via Docker Compose)
"""
import importlib
import sys
from dotenv import load_dotenv

load_dotenv()


def run():
    # Import numbered modules dynamically
    step1 = importlib.import_module("1_explore_schema")
    step2 = importlib.import_module("2_generate_sql")
    step3 = importlib.import_module("3_describe_data")

    print("=== Step 1: Explore schema ===")
    step1.explore_schema()

    print("\n=== Step 2: Generate SQL queries via Claude ===")
    step2.generate_sql()

    print("\n=== Step 3: Run queries and describe data via Claude ===")
    step3.run_queries_and_describe()

    print("\nDone. Results are in the output/ directory.")


if __name__ == "__main__":
    run()
