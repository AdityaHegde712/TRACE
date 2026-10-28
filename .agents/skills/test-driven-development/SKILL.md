---
name: test-driven-development
description: >-
  Use a test-first Red-Green-Refactor workflow when implementing features,
  fixing bugs, or defining executable behavioral contracts. Documentation-only
  and formatting-only changes do not require this workflow.
---

# Test-Driven Development (TDD)

## 1. Red -> Green -> Refactor Cycle
1. **Red**: Define observable acceptance criteria and write focused assertions
   before changing implementation. For bugs, reproduce the reported failure.
   Run the tests and confirm they fail because the required behavior is missing
   or wrong. Investigate setup errors or unexpectedly passing tests before
   proceeding; neither demonstrates the intended behavioral gap.
2. **Green**: Lock the assertions and implement the smallest change that passes
   them. Fix the implementation rather than weakening the contract.
3. **Refactor**: Improve clarity or remove duplication where useful, without
   adding behavior. Rerun relevant tests and keep assertions unchanged.

## 2. Test Immutability Contract
- **Contract Integrity**: Existing test assertions represent an immutable behavioral specification. Implementation workflows must NEVER modify, weaken, or delete existing assertions.
- **Contract Changes**: Alterations to existing tests require explicit user confirmation. Fix the implementation, not the test.

## 3. Test Stratification & Organization
- **Frozen Contract Tests (`tests/spec/`)**: Immutable behavioral specifications defining acceptance criteria.
- **Integration Tests (`tests/integration/`)**: Dynamic end-to-end tests validating multi-module interactions.
- **Directory Isolation**: All test suites reside strictly in top-level `tests/`; never co-locate tests inside source directories.
- **Golden Fixtures**: Share single, authoritative golden fixture files across modules exchanging identical data schemas.

## 4. Test Quality & Verification
- **Meaningful assertions**: Identify the realistic bug each test catches.
  Assert observable behavior and derive expected values independently of the
  implementation; do not compute both sides with the same production helper.
- **Real behavior**: Keep the behavior under test real. Mock external boundaries
  when needed; assert calls, arguments, or ordering when those interactions are
  themselves contractual. Prefer integration coverage over elaborate mocks.
- **Regression checks**: Run focused tests during development and the project's
  required regression checks before completion. Report failures, skipped checks,
  and blockers; distinguish focused-test success from suite success.
- **Evidence**: Report test commands, the observed Red failure, and final results.
  Do not claim a verified TDD cycle when tests could not run.
- **Existing work**: Preserve existing implementation if test-first ordering was
  missed. Add appropriate characterization or regression coverage and report the
  limitation rather than automatically deleting code to restart the cycle.
