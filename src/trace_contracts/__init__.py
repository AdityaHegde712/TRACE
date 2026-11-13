"""Cross-track contracts frozen at milestone M1.

Track B (scenario generation) writes these records, Track C (sweep harness and
baselines) reads them, and Track A (measurement core) implements the policies
and estimators behind them. Only the project lead changes this package; any
change bumps CONTRACT_VERSION. See docs/planning/M1_CONTRACTS.md.
"""

CONTRACT_VERSION: str = "m1-v0"
