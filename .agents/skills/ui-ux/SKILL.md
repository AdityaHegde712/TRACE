---
name: ui-ux
description: Govern UI/UX design and decision-making for any application, framework, platform, interface, interaction flow, component, page, or visual experience. Invoke whenever work involves UI/UX choices, including new designs, redesigns, layout changes, user flows, visual styling, components, interaction patterns, or other decisions affecting the user experience.
---

# UI/UX Design Workflow

UI/UX decisions require user clarification, rendered validation, and explicit approval before the design is locked.

## 1. Interview Before Designing
Before committing to material UI/UX decisions, interview the user to resolve relevant ambiguities: user goals, target audience, visual direction, theme, branding, information hierarchy, layout, navigation, interaction flows, component behavior, responsive behavior, accessibility expectations, states/transitions, density, reference products/designs, platform constraints. Ask only questions that materially affect design; never silently invent important preferences.

## 2. Produce a Renderable Prototype
Create an HTML/CSS representation representing intended content hierarchy, layout, spacing, typography, visual language, components, interaction states, and navigation/flow. Do not create token mockups.

## 3. Render With Playwright
Render the HTML prototype using Playwright. Inspect for: clipping, overflow, broken layout, visual hierarchy, spacing, responsive issues, and obvious accessibility/usability problems. Fix visible issues before presenting. If Playwright is unavailable, install it at the project level to proceed.

## 4. Capture and Present Screenshots
Capture screenshots sufficient to communicate the design and present to the user. Use actual rendered results (not only prose, wireframes, or code) as the basis for approval.

## 5. Require Explicit Approval
Design MUST NOT be treated as locked without explicit user approval.
If changes are requested: `feedback -> revise HTML/CSS -> render with Playwright -> inspect -> capture screenshots -> present again` (repeat until explicit approval received; do not skip loop for small changes). Proceed with implementation only after approval.

## Completion Check
Before treating design as approved or implementing:
- [ ] Ambiguities discussed without silently inventing preferences.
- [ ] Non-placeholder HTML/CSS prototype created and rendered with Playwright.
- [ ] Rendered result inspected and relevant screenshots presented to user.
- [ ] Requested revisions rerendered, reshown, and explicitly approved by user.
