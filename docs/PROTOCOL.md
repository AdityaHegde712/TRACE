# Research Protocol

## Evidence Standard

Use primary sources: peer-reviewed proceedings/journals, official project pages, official documentation, and canonical public repositories. Link every material claim directly. Search-result snippets, secondary blogs, and unsourced GitHub forks are discovery aids only.

## Date and Inclusion Rules

- Core paper window: 2022-08-29 through 2026-08-29.
- Include older framework releases only when necessary to compare an actively maintained implementation; label them as background.
- Include a system only if it materially overlaps orchestration, visual shared state, multi-agent task allocation, simulator integration, or open-source deployment.

## Search Clusters

1. `multi robot agent orchestration framework VLM shared world model`
2. `multi robot 3D scene graph shared semantic map task planning`
3. `LLM multi robot coordination simulator framework open source`
4. `ROS 2 multi robot task allocation simulator visual language model`
5. `event sourced world model robotic agents evidence provenance`

## Mandatory Direct Adversarial Pass

For every retained synthesis finding:

1. Verify that its source entails the claim.
2. Search for the closest current counterexample.
3. State a concrete failure mode or implementation burden.
4. Mark the finding `RETAIN`, `NARROW`, or `REJECT`.

## Mandatory Problem Ledger

Before proposing a framework feature, record the existing problem using this schema:

`problem ID | affected mission/operator workflow | observed current-system limitation | source | candidate measurable outcome | closest counterexample | disposition`.

Reject any framework feature that cannot be connected to a source-cited problem and an observable evaluation outcome.

## Claim Categories

- **Verified finding:** direct source support.
- **Design inference:** reasoned recommendation from sources; not a literature fact.
- **Project hypothesis:** must be tested by the future build.
- **Unknown:** no supported conclusion yet.
