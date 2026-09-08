# Skills

My agent skills, installable via [skills.sh](https://www.skills.sh/). They are
model- and provider-agnostic: they work with any coding agent skills.sh
supports.

[![skills.sh](https://skills.sh/b/sjoli/skills)](https://skills.sh/sjoli/skills)

## Installation

Copies the skill files into your project as ordinary files you own and can edit:

```bash
npx skills@latest add sjoli/skills
```

Pick the skills you want and which agents to install them on. Pull later
changes with `npx skills update`.

## Repository structure

```
.
├── skills/
│   └── <category>/
│       └── <skill-name>/
│           └── SKILL.md   # one skill per directory
├── scripts/
│   └── list-skills.sh     # lists every discovered SKILL.md
├── package.json
├── LICENSE
└── README.md
```

Each skill lives in its own directory and is defined by a `SKILL.md` file with
YAML frontmatter:

```markdown
---
name: my-skill
description: What it does. Use when <explicit triggers>.
---

# My Skill

Instructions the agent follows once this skill is invoked.
```

A skill can include supporting files (e.g. `LOGIC.md`, `UI.md`) that `SKILL.md`
links to by relative path.

## Adding a skill

1. Create `skills/<category>/<your-skill-name>/SKILL.md`.
2. Write tight, trigger-focused frontmatter and clear instructions.
3. Run `./scripts/list-skills.sh` to confirm it is discovered.

## Skills

### Example

- **[hello-skill](./skills/example/hello-skill/SKILL.md)**: An example skill
  demonstrating the structure. Replace it with a real skill.
