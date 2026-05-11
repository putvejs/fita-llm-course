"""
Pipeline entry point — runs all 3 steps in sequence.
Usage: python main.py  (from week2/ directory)
"""
import importlib

from dotenv import load_dotenv

load_dotenv()


def run():
    step1 = importlib.import_module("1_plan")
    step2 = importlib.import_module("2_execute")
    step3 = importlib.import_module("3_report")

    print("=== Step 1: Extract schema + generate visualization plan ===")
    step1.explore_schema()
    step1.generate_plan()

    print("\n=== Step 2: Execute plan — SQL, charts, insights ===")
    step2.execute_plan()

    print("\n=== Step 3: Generate HTML + PDF report ===")
    report_path = step3.generate_report()
    step3.generate_pdf()

    print(f"\nDone. Open {report_path} in your browser or output/report.pdf.")


if __name__ == "__main__":
    run()
