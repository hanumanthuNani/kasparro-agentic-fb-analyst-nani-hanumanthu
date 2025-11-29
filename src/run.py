from src.orchestrator.pipeline import run_pipeline
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python src/run.py \"Analyze ROAS drop\"")
        return

    user_query = sys.argv[1]
    print("Running pipeline for query:", user_query)

    run_pipeline(user_query)

if __name__ == "__main__":
    main()
