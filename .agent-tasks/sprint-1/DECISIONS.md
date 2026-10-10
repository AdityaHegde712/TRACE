# Sprint 1 Decisions

## Accepted

- S1-001: Implement a simulator-agnostic deterministic core before any robotics
  adapter.
- S1-002: Use Python 3.12 managed with `uv`; production code has no runtime
  dependency beyond the standard library.
- S1-003: The only entity is one road-blockage region. Task actions are requests,
  not scheduled or executed assignments.
- S1-004: Belief statuses are `proposed`, `corroborated`, `disputed`, `stale`,
  `verified`, and `invalid`.
- S1-005: The policy interface is swappable. It receives a belief snapshot and
  normalized event, and returns a typed decision with stable reason codes.
- S1-006: Fixed policy: fresh positive -> proposed/create verification;
  independent confirmation -> verified/close; fresh contradiction ->
  disputed/reassign; expiry -> stale/reassign; verifier disproval -> invalid/close.
- S1-007: Oracle fixtures are independently authored expected outputs. They do
  not call policy implementation code or expose ground truth to the resolver.
- S1-008: Sprint 1 reports contract correctness, trace completeness, and replay
  equivalence. It makes no baseline-improvement claim.

## Deferred

- Gazebo/PX4, ROS 2, camera adapters, M3OT, learned or weighted policies,
  allocator integration, and UI visualization.
