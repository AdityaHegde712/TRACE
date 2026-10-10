# Agentic Visual Perception in Distributed Autonomous Systems

### Authors: Aditya Hegde, Rishi Sheth, and Pranav Senghal

### Capstone Advisor: Dr. Kaikai Liu

Distributed autonomous systems coordinate teams of drones and robots that perceive and act from different locations. During search, inspection, and incident response, agents divide coverage, compare observations, and adapt assignments as conditions change. This depends on converting partial sensor observations into a shared operational picture without assuming every report is current or correct.

The central challenge is deciding when an uncertain visual report justifies a mission-state change. Occlusion, sensing error, object motion, delayed messages, or mistaken identity can make reports stale, incomplete, duplicated, or contradictory. Premature acceptance may close an unresolved inspection task; verifying every report consumes time and vehicle capacity. Related commercial work includes [Skydio's](https://www.skydio.com/blog/skydios-approach-to-multi-drone-airspace-management) multi-drone inspection systems, [Anduril's](https://www.anduril.com/news/special-operations-command-selects-anduril-as-mission-autonomy-systems-integration-partner) coordination of diverse autonomous systems, and [Shield AI's](https://shield.ai/shield-ai-awarded-u-s-air-force-production-contract/) collaborative aircraft autonomy.

We propose to build and evaluate an evidence-gated visual task-orchestration framework. Each observation becomes a provenance-linked claim recording its source, timestamp, sensor pose, model version, confidence, and visual artifact. Claims update revisable entity beliefs; explicit policies then create, verify, close, reopen, or reassign tasks. Agents receive task-scoped state, and a causal trace records each decision. Controlled simulations will compare the framework with first-report, majority-vote, and always-verify baselines, measuring incorrect task transitions and verification cost while tracking mission completion and replay consistency. Simulator truth is reserved for scoring; navigation and flight control remain outside scope.
