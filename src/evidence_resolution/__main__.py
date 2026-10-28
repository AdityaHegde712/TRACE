"""Command-line entry point for reviewer-facing scenario artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .scenario import load_scenario, run_scenario


def main() -> int:
    """Run one scenario and write its causal trace plus oracle result."""
    parser = argparse.ArgumentParser(description="Run an evidence-resolution scenario.")
    parser.add_argument("--scenario", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    arguments = parser.parse_args()

    scenario = load_scenario(arguments.scenario)
    result = run_scenario(scenario)
    contract_trace = result.contract_trace()
    oracle_passed = contract_trace == scenario.expected_trace

    arguments.output_dir.mkdir(parents=True, exist_ok=True)
    trace_path = arguments.output_dir / f"{scenario.scenario_id}.trace.jsonl"
    report_path = arguments.output_dir / f"{scenario.scenario_id}.oracle.json"
    trace_path.write_text(result.to_jsonl(), encoding="utf-8", newline="\n")
    report = {
        "scenario_id": scenario.scenario_id,
        "oracle_passed": oracle_passed,
        "trace_event_count": len(contract_trace),
    }
    report_path.write_text(
        json.dumps(report, sort_keys=True), encoding="utf-8", newline="\n"
    )
    return 0 if oracle_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
