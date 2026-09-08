---
name: hello-skill
description: An example skill demonstrating the structure of a skills.sh skill. Replace this with a real skill. Use when the user asks for a demonstration of the skill format or as a starting template for a new skill.
---

# Hello Skill

This is an example skill. A skill is a Markdown file (`SKILL.md`) with YAML
frontmatter (`name` and `description`) followed by instructions written for an
agent.

## How skills work

- The **frontmatter** `description` is what an agent reads to decide when to
  reach for this skill. Make it specific, and include explicit "Use when..."
  triggers.
- The **body** contains the actual instructions the agent follows once the
  skill is invoked.

## Writing a good skill

1. Keep the `description` tight and trigger-focused so the right skill fires.
2. Write the body as clear, imperative instructions for the agent.
3. Split large skills into supporting files (e.g. `LOGIC.md`, `UI.md`) that
   the `SKILL.md` links to, and reference them by relative path.

## Steps

1. Copy this directory to `skills/<category>/<your-skill-name>/`.
2. Rewrite the frontmatter and body for your skill.
3. Run `./scripts/list-skills.sh` to confirm it is discovered.
