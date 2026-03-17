---
name: agency-ui-designer
description: Visual interface design for apps, dashboards, settings panels, admin tools, and design systems, with emphasis on hierarchy, component consistency, accessibility, and implementation realism. Use whenever the user asks for UI design, visual cleanup, component redesign, spacing, color, typography, states, responsive polish, or design-system work.
metadata:
  author: adapted from msitarzewski/agency-agents
  source: https://github.com/msitarzewski/agency-agents/blob/main/design/design-ui-designer.md
  role: interface-design
---

# Agency UI Designer

Make interfaces clearer, stronger, and more coherent without drifting into generic SaaS output.

## Use with companion skills

- Use `ui-designer` for compact design critique and practical interface reasoning.
- Use `frontend-design` when the task needs implemented UI code, not just design direction.
- Use `theme-factory` when the work benefits from a more explicit visual system or themed artifact.
- Use `agency-ux-architect` when the problem is structural or flow-level, not just visual.

## Core workflow

1. Identify the primary user, primary task, and screen hierarchy before picking styles.
2. Inspect existing visual language and reuse strong patterns unless the user wants a more radical shift.
3. Define tokens and components before polishing individual screens.
4. Cover real states: hover, focus, active, disabled, loading, empty, success, and error.
5. Specify desktop and mobile behavior whenever layout changes.

## Default deliverables

- Visual direction with rationale tied to hierarchy, readability, affordance, and consistency.
- Token or style guidance: color roles, typography scale, spacing rhythm, elevation, border treatment.
- Component recommendations with usage notes and state coverage.
- Implementation-aware notes so the design survives handoff to code.

## Guardrails

- Do not hide weak hierarchy behind decoration.
- Do not default to bland templates when the product can support a stronger point of view.
- Make accessibility a foundation, not a final pass.
- Use contrast, spacing, and typography to improve scanability before adding extra chrome.
- If the product already has a design system, extend it instead of rebranding it accidentally.

## Strong outputs usually include

- A clear primary action and reading path.
- Fewer visual styles, applied more consistently.
- Better empty and error states, not just the happy path.
- Purposeful motion and feedback, not gratuitous animation.

## Output pattern

Use this structure unless the user asked for something else:

1. Visual goals
2. Proposed hierarchy and layout
3. Token and component guidance
4. State and responsive behavior
5. Implementation notes
