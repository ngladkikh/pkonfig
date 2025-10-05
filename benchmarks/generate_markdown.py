"""
Generate Markdown benchmark results from benchmark_results.json.

This script reads benchmark_results.json produced by benchmark_pkonfig_vs_pydantic.py
and writes a human-readable RESULTS.md with a summary table and brief analysis.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "benchmark_results.json"
MD_PATH = ROOT / "RESULTS.md"


def _format_row(scenario: str, pkonfig_avg: float, pydantic_avg: float) -> str:
    if pkonfig_avg <= 0 or pydantic_avg <= 0:
        # Avoid division by zero, show N/A
        if pkonfig_avg < pydantic_avg:
            faster = "pkonfig"
            times = "N/A"
        elif pydantic_avg < pkonfig_avg:
            faster = "pydantic"
            times = "N/A"
        else:
            faster = "equal"
            times = "1.00x"
    else:
        if pkonfig_avg < pydantic_avg:
            faster = "pkonfig"
            times = f"{pydantic_avg / pkonfig_avg:.2f}x"
        elif pydantic_avg < pkonfig_avg:
            faster = "pydantic"
            times = f"{pkonfig_avg / pydantic_avg:.2f}x"
        else:
            faster = "equal"
            times = "1.00x"

    # Convert seconds to milliseconds for display
    pkonfig_ms = pkonfig_avg * 1000.0
    pydantic_ms = pydantic_avg * 1000.0

    return f"| {scenario} | {pkonfig_ms:.3f} | {pydantic_ms:.3f} | {faster} | {times} |"


def main() -> None:
    if not JSON_PATH.exists():
        raise SystemExit(
            f"Benchmark JSON not found: {JSON_PATH}. Run the benchmark script first."
        )

    data: List[Dict[str, Any]] = json.loads(JSON_PATH.read_text())

    # Build rows in the same order as provided
    rows: List[str] = []
    for entry in data:
        scenario = entry.get("scenario") or entry.get("name") or "Unknown"
        pkonfig_avg = float(entry["pkonfig"]["average"])  # type: ignore[index]
        pydantic_avg = float(entry["pydantic"]["average"])  # type: ignore[index]
        rows.append(_format_row(scenario, pkonfig_avg, pydantic_avg))

    header = (
        "# pkonfig vs Pydantic Settings Benchmark Results\n\n"
        "This document presents the results of benchmarking pkonfig against Pydantic Settings in various scenarios.\n\n"
        "## Summary\n\n"
        "| Scenario | pkonfig (ms) | Pydantic (ms) | Faster | Times Faster |\n"
        "|----------|---------------|---------------|--------|--------------|\n"
    )
    body = "\n".join(rows) + "\n\n"

    analysis = (
        "## Methodology\n\n"
        "These benchmarks run multiple iterations per scenario and report average times.\n"
        "See benchmarks/README.md for details and how to reproduce.\n\n"
        "The raw JSON is saved to `benchmarks/benchmark_results.json`.\n"
    )

    MD_PATH.write_text(header + body + analysis)
    print(f"Wrote markdown results to {MD_PATH}")


if __name__ == "__main__":
    main()
