# Philosophy of Software Design Skill

An agent skill for applying design principles inspired by John Ousterhout's *A Philosophy of Software Design* to libraries, applications, and systems.

The skill has three modes:

- **DESIGN** — compare abstractions before implementation.
- **REVIEW** — inspect an implementation or PR for complexity and abstraction quality.
- **RETROSPECTIVE** — compare the original design hypothesis with actual outcomes.

Its two persistent outputs are intentionally separate:

1. **Principle adherence** — did the design follow the principle, with evidence?
2. **Outcome evidence** — did the design actually reduce change amplification, cognitive load, and unknown unknowns?

Suggested repository layout after adopting the skill:

```text
.design/
└── posd/
    ├── decisions/
    ├── reviews/
    └── outcomes/
```

Start with `SKILL.md`.
