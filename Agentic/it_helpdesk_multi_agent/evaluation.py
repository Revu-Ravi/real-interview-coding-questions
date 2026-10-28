from agents import load_tickets
from workflow import run_helpdesk

def evaluate():
    rows = load_tickets()
    results = []
    for row in rows:
        output = run_helpdesk(row["initial_message"])
        expected = row["resolution_summary"].lower()
        actual = output.get("response", "").lower()
        # Lightweight baseline: count whether a key phrase from the reference appears.
        key = row["resolution_summary"].split(";")[0].strip().lower()
        correct = key in actual
        results.append({"query": row["initial_message"], "correct": correct,
                        "grounded": bool(output.get("tool_results", {}).get("knowledge", {}).get("matched_query"))})
    total = len(results)
    return {"total": total, "correct": sum(r["correct"] for r in results),
            "grounded": sum(r["grounded"] for r in results), "details": results}

if __name__ == "__main__":
    print(evaluate())
