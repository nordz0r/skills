---
name: agency-whimsy-injector
description: Deliberate product delight through micro-interactions, celebratory moments, playful copy, brand personality, and memorable but practical UX touches. Use whenever the user wants a product to feel less sterile, more human, or more memorable, or asks for micro-interactions, loading or empty states, success moments, or emotional polish without a broader screen redesign.
metadata:
  author: adapted from msitarzewski/agency-agents
  source: https://github.com/msitarzewski/agency-agents/blob/main/design/design-whimsy-injector.md
  role: delight-and-personality
---

# Agency Whimsy Injector

Add personality and delight without making the product unserious, inaccessible, or annoying.

## Use with companion skills

- Use `agency-ui-designer` when the base visual system still needs work.
- Use `frontend-design` when the delight needs to be implemented in code.
- Use `theme-factory` when the product needs a stronger stylistic point of view, not just a few playful moments.

## Strong routing signals

- The user says the product works but feels sterile, flat, cold, or too generic.
- The ask focuses on loading states, empty states, success moments, microcopy, or subtle animation rather than screen structure.
- The goal is to add personality without a full visual redesign.

## Do not route here when

- The user is asking for a full admin/dashboard/screen redesign, hierarchy fix, table readability pass, or responsive layout overhaul. Use `agency-ui-designer`.
- The problem is primarily about flows, IA, navigation model, or layout architecture across screens. Use `agency-ux-architect`.

## Core workflow

1. Identify where emotion matters: onboarding, success, waiting, recovery, empty states, or discovery.
2. Choose a small number of high-leverage moments instead of scattering novelty everywhere.
3. Tie each delight moment to a function: reduce anxiety, reward progress, humanize failure, or reinforce brand character.
4. Check accessibility and performance before committing to motion or layered effects.
5. Preserve seriousness for security, billing, destructive actions, and critical operational states.

## Default deliverables

- A shortlist of delight moments with purpose and expected effect.
- Microcopy, motion, or interaction proposals with restraint.
- Accessibility and reduced-motion behavior.
- Notes on where whimsy should not be used.

## Guardrails

- Every playful element should serve a functional or emotional purpose.
- Prefer small memorable moments over constant noise.
- Respect `prefers-reduced-motion` and keep interactions performant.
- Avoid jokes or surprise behavior in high-stakes workflows.
- Do not let whimsy obscure status, error meaning, or primary actions.

## Good targets

- Empty states that guide and reassure.
- Success states that reward completion.
- Loading and waiting experiences that reduce uncertainty.
- Small discovery moments that deepen brand memory.

## Output pattern

Use this structure unless the user asked for something else:

1. Where delight belongs
2. Proposed interactions or copy
3. Accessibility and performance constraints
4. Anti-patterns to avoid

<!-- A-EVOLVE-ROUTING-SIGNALS:START -->
## Routing signals: delight personality playful copy micro-interactions loading empty states success moments celebratory subtle restraint brand voice
<!-- A-EVOLVE-ROUTING-SIGNALS:END -->
