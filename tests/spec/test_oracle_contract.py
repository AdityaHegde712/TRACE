"""Immutable behavioral contract for the Sprint 1 resolver."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from evidence_resolution.scenario import load_scenario, run_scenario

FIXTURE_DIRECTORY = Path(__file__).parents[1] / "fixtures" / "oracle"


@pytest.mark.parametrize("fixture_name", ["supported", "false", "stale", "conflicting"])
def test_resolver_matches_independent_oracle(fixture_name: str) -> None:
    """Each frozen input sequence must produce the oracle belief/action trace."""
    fixture_path = FIXTURE_DIRECTORY / f"{fixture_name}.json"
    scenario = load_scenario(fixture_path)

    result = run_scenario(scenario)

    assert result.contract_trace() == scenario.expected_trace


def test_simulator_truth_does_not_change_resolution() -> None:
    """Ground truth is scoring metadata and must never influence policy output."""
    fixture_path = FIXTURE_DIRECTORY / "supported.json"
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    inverted_truth = deepcopy(payload)
    inverted_truth["truth"]["blockage_present"] = False

    original_trace = run_scenario(load_scenario(payload)).contract_trace()
    inverted_trace = run_scenario(load_scenario(inverted_truth)).contract_trace()

    assert inverted_trace == original_trace


def test_replay_is_byte_stable_and_causally_complete() -> None:
    """Replay must reproduce every semantic decision from its recorded inputs."""
    scenario = load_scenario(FIXTURE_DIRECTORY / "conflicting.json")
    first_run = run_scenario(scenario)
    replay_run = run_scenario(scenario)

    assert replay_run.to_jsonl() == first_run.to_jsonl()
    for trace_event in first_run.contract_trace():
        assert trace_event["causal_claim_ids"]
        assert trace_event["policy_version"] == "fixed-v1"
