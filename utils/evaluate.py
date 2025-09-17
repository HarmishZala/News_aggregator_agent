import json
import os
from typing import Optional, List


def run_simple_evaluation(cli_app, dataset_path: Optional[str] = None) -> None:
    """
    Run a minimal evaluation by sending a few prompts through the CLI agent and printing responses.
    If tracing is enabled, runs will be captured in LangSmith for later assessment.

    dataset_path: Optional path to a JSON file with an array of {"question": "..."}.
                  If not provided, use a small built-in set.
    """
    try:
        if dataset_path and os.path.exists(dataset_path):
            with open(dataset_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            prompts: List[str] = [row["question"] for row in data if isinstance(row, dict) and row.get("question")]
        else:
            prompts = [
                "Summarize today’s top AI news.",
                "What’s new in the stock market for NVDA today?",
                "Show recent advances in quantum computing research.",
            ]

        if not prompts:
            print("No evaluation prompts found.")
            return

        print(f"Running evaluation on {len(prompts)} prompts...")
        for idx, q in enumerate(prompts, start=1):
            print(f"\n[{idx}/{len(prompts)}] Q: {q}")
            response = cli_app.process_query(q)
            print("A:", (response[:400] + "...") if len(response) > 400 else response)

        print("\nEvaluation complete. If tracing was ON, results are in LangSmith.")
    except Exception as e:
        print(f"Evaluation failed: {e}")




