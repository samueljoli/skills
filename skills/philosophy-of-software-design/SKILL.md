---
name: philosophy-of-software-design
description: Apply John Ousterhout-inspired software design principles when designing or reviewing libraries, applications, APIs, modules, and systems. Use this skill to reduce complexity, build deeper abstractions, compare alternative designs, detect information leakage and shallow modules, and record both principle adherence and real-world outcomes over time.
---

# Philosophy of Software Design

Use this skill as a design discipline, not as a style checklist.

The goal is to reduce the complexity that engineers must understand while changing, using, operating, or extending a system. The principles in this skill are hypotheses and heuristics for achieving that goal. Always separate:

1. **Principle adherence** — whether the design or implementation followed the principle.
2. **Outcome** — whether the resulting system actually became easier to understand, change, use, or operate.

Do not infer a good outcome merely because a principle was followed.

## When to use this skill

Use this skill when any of the following are true:

- Designing a library, crate, package, service, application, subsystem, protocol, API, or module.
- Choosing boundaries between components.
- Introducing or revising an abstraction.
- Designing error semantics or configuration surfaces.
- Reviewing a PR that adds architectural or API complexity.
- Refactoring code whose complexity is difficult to localize.
- Comparing two or more designs for the same problem.
- Revisiting a previous design to determine whether its abstractions held up in practice.

Do not invoke the full workflow for trivial edits whose design impact is negligible.

## Core model

Treat complexity as the primary dependent variable. Look for three symptoms:

- **Change amplification** — a small requirement change forces edits in many places.
- **Cognitive load** — a developer must hold too many concepts, rules, states, or dependencies in mind.
- **Unknown unknowns** — it is difficult to know what must change or what may break.

Ask repeatedly:

> What complexity exists, who currently pays for it, and where can it be hidden most effectively?

Read `references/complexity.md` when diagnosing complexity in an existing design.

## Operating modes

Choose one mode before beginning.

### 1. DESIGN

Use before implementation or before committing to an important abstraction.

Required sequence:

1. Define the problem and constraints.
2. Identify the complexity the design must absorb.
3. Identify information ownership.
4. Produce at least two meaningfully different designs for consequential decisions.
5. Evaluate each design using this skill's principles.
6. Choose a design and record the tradeoffs.
7. State expected outcomes that can later be checked.
8. Produce or update a design decision record.

Use `templates/design-review.md` and `templates/design-decision.md`.

### 2. REVIEW

Use against an implementation, PR, or existing architecture.

Required sequence:

1. Recover the intended abstraction and responsibilities.
2. Trace the public interface and major call paths.
3. Identify leaked knowledge, pass-through layers, duplicated policy, special cases, and unnecessary error states.
4. Compare the implementation with the intended design.
5. Record principle adherence using evidence.
6. Identify likely complexity consequences without claiming they have already occurred.
7. Recommend the smallest changes that materially improve the abstraction.

Use `templates/implementation-review.md`.

### 3. RETROSPECTIVE

Use after the design has experienced real use or meaningful change.

Required sequence:

1. Retrieve the original decision and expected outcomes.
2. Examine what changed since the decision.
3. Record observed evidence: interface churn, bypasses, unexpected dependencies, repeated questions, bugs crossing boundaries, migration pain, or easier-than-expected changes.
4. Compare expected outcomes with observed outcomes.
5. Record lessons without rewriting history.
6. Identify whether the principle was wrong for the context, incorrectly applied, or correctly applied but insufficient.

Use `templates/retrospective.md`.

## Principle set

The detailed reference is in `references/principles.md`. During normal operation, evaluate at least these dimensions:

### Complexity first

Prefer designs that reduce the amount of system knowledge required for common changes. Do not optimize for line count, number of classes, number of services, or conceptual purity by themselves.

### Deep modules

Prefer modules with a simple interface that hide substantial implementation complexity. Flag modules whose interface cost is similar to or greater than the functionality they hide.

### Information hiding

A design decision should have a clear owner. Avoid duplicating knowledge of representations, protocols, invariants, storage layouts, timing rules, or policy across modules.

### Pull complexity downward

When one module has the context to handle a complexity once, prefer that over forcing every caller to handle it repeatedly. Do not push complexity downward blindly when doing so would make the lower layer domain-specific, surprising, or incorrect.

### Different layer, different abstraction

A layer should add a meaningful abstraction. Flag pass-through methods and layers that mostly mirror the API beneath them without hiding complexity or changing the conceptual model.

### General-purpose over special-purpose, within reason

Prefer a small number of broadly useful operations when they simplify the interface and still match real needs. Avoid speculative generality and frameworks built for hypothetical futures.

### Define errors out of existence

Before adding an error case, ask whether the API semantics can make the condition normal, impossible, or internally recoverable. Do not erase errors that callers genuinely need to distinguish.

### Design it twice

For consequential decisions, produce at least two structurally different designs. Compare them on complexity placement, interface simplicity, information ownership, likely change patterns, and failure behavior.

### Comments and names clarify design

Use documentation to explain intent, invariants, non-obvious constraints, ownership, and interface semantics. Do not use comments to compensate for a confusing abstraction when the design itself can be improved.

### Consistency reduces cognitive load

Reuse existing conventions when they are sound. A locally elegant but inconsistent design can increase system-wide cognitive load.

## Principle adherence

Never use a numeric score or aggregate grade. Do not reduce design quality to points.

Use exactly one of these statuses per evaluated principle:

- `APPLIED`
- `PARTIALLY_APPLIED`
- `INTENTIONAL_EXCEPTION`
- `VIOLATED`
- `NOT_APPLICABLE`
- `UNKNOWN`

Every status except `NOT_APPLICABLE` requires evidence. Evidence should point to concrete interfaces, files, call paths, types, configuration, behavior, or decision records.

Bad:

> Deep modules: APPLIED

Good:

> Deep modules: APPLIED — callers use `SessionStore::put/get/delete`; token encoding, persistence format, TTL enforcement, retries, and instrumentation remain internal.

An intentional exception must include:

- the reason for the exception;
- the complexity being accepted;
- who will pay that complexity;
- the condition under which the decision should be revisited.

## Outcome tracking

Track outcomes separately from adherence.

Use three observation windows:

### Immediate

Record facts available at design or merge time, such as:

- public operations and public types introduced;
- exposed configuration;
- caller-visible error cases;
- implementation concepts callers must understand;
- number of modules or layers crossed for a representative operation;
- dependencies exposed through the interface.

### Observed

Record evidence after the abstraction has been used:

- interface changes;
- abstraction bypasses;
- recurring caller workarounds;
- repeated developer questions;
- bugs caused by leaked or duplicated knowledge;
- unplanned modules touched during changes;
- changes that were easier than expected;
- migrations avoided or simplified by information hiding.

### Long-term

Record evidence after multiple meaningful changes:

- change amplification trend;
- interface stability;
- implementation replaceability;
- maintenance burden;
- conceptual consistency;
- frequency of unknown dependencies discovered during change;
- whether the abstraction continued to match the domain.

Do not invent outcome data. If there is no real observation yet, mark it `PENDING`.

## Design workflow

### Step 1: Frame the design problem

State:

- the user or system need;
- what must remain stable;
- likely dimensions of change;
- important constraints;
- what is explicitly out of scope.

Do not start from classes, traits, tables, services, or frameworks.

### Step 2: Map complexity

Identify:

- knowledge callers currently need;
- policy duplicated across call sites;
- sequences callers must perform correctly;
- temporal coupling;
- error cases;
- configuration choices;
- external-system details;
- state transitions and invariants;
- hidden dependencies and likely unknown unknowns.

Distinguish **essential complexity** from **accidental complexity**.

### Step 3: Map information ownership

For each important fact or decision, write one preferred owner.

Examples:

- database representation -> repository/persistence module;
- wire protocol -> protocol adapter;
- retry policy -> integration boundary;
- domain invariant -> domain model;
- cache eviction strategy -> cache implementation;

Flag the same knowledge appearing in multiple unrelated modules.

### Step 4: Design alternatives

Create at least two meaningfully different approaches when the decision is consequential.

Meaningfully different means the alternatives move responsibility or complexity across boundaries. Renaming an interface or adding another wrapper does not count.

For each alternative, describe:

- public interface;
- information owner;
- complexity hidden;
- complexity exposed;
- expected common change;
- failure/error semantics;
- operational consequences;
- likely escape hatches or bypass pressure.

### Step 5: Evaluate abstractions

Use the questions in `references/review-questions.md`.

Especially ask:

- What must a caller know before using this correctly?
- Could the interface be smaller without losing important capability?
- What implementation details are visible through types, errors, configuration, ordering, or naming?
- Which future changes stay inside one module?
- Which future changes cross boundaries?
- Does each layer transform the abstraction, or merely forward calls?
- Are special cases contaminating the common path?

### Step 6: Record the decision

Create a decision record using `templates/design-decision.md`.

Store records in a project-local location such as:

```text
.design/posd/decisions/
```

Use the project's existing ADR or design-doc location instead when one already exists.

### Step 7: State expected outcomes

Expected outcomes must be falsifiable where practical.

Prefer:

> Adding a second broker implementation should require changes inside the messaging adapter and composition root, not inside domain services.

Over:

> The messaging abstraction will be clean.

## Review workflow

During REVIEW mode, inspect for the red flags in `references/red-flags.md`.

For each significant finding:

1. Describe the concrete design issue.
2. Identify which complexity symptom it creates or is likely to create.
3. Identify the relevant principle.
4. Show the evidence.
5. Explain who pays the complexity.
6. Suggest a design change only if it materially improves the abstraction.

Prioritize findings by expected complexity impact, not stylistic preference.

## Retrospective workflow

For each prior design decision:

1. Read its expected outcomes.
2. Gather actual evidence from later changes, issues, PRs, incidents, and developer behavior.
3. Record outcomes using `tracking/record.schema.yaml` or the project's equivalent.
4. Compare prediction to observation.
5. Record lessons.

Classify lessons as one of:

- `PRINCIPLE_HELPED`
- `PRINCIPLE_MISAPPLIED`
- `PRINCIPLE_INSUFFICIENT`
- `CONTEXT_CHANGED`
- `OUTCOME_INCONCLUSIVE`

## Output contract

Unless the user asks for a different format, produce the following.

### DESIGN output

1. Problem and constraints
2. Complexity map
3. Information ownership
4. Alternatives
5. Principle analysis
6. Decision and tradeoffs
7. Expected outcomes
8. Revisit triggers

### REVIEW output

1. Intended abstraction
2. Findings ordered by complexity impact
3. Principle adherence table
4. Likely consequences
5. Recommended changes
6. Outcome status: `PENDING` unless real evidence exists

### RETROSPECTIVE output

1. Original intent
2. Expected vs observed outcomes
3. Principle adherence carried forward from the original review
4. Outcome evidence
5. Lessons
6. Follow-up design changes

## Guardrails

- Do not turn principles into rigid laws.
- Do not reward more abstraction merely because abstraction exists.
- Do not recommend splitting code solely to make units smaller.
- Do not treat short methods or many classes as evidence of good modularity.
- Do not assume microservices, DDD, repositories, dependency injection, event sourcing, or any other architecture is inherently aligned with this philosophy.
- Do not prefer an abstraction if its interface requires callers to learn nearly as much as the implementation it hides.
- Do not claim an outcome without evidence.
- Do not use a single aggregate score.
- Distinguish design problems from implementation bugs and naming/style issues.
- Prefer removing complexity to relocating it; when relocation is necessary, place it where it can be handled once with the most context.

## Reference loading

Load only what is needed:

- Complexity diagnosis -> `references/complexity.md`
- Principle definitions -> `references/principles.md`
- Abstraction/API design -> `references/abstractions.md`
- Code/PR review -> `references/red-flags.md`
- Structured interrogation -> `references/review-questions.md`
- Design work -> `templates/design-review.md`, `templates/design-decision.md`
- Implementation review -> `templates/implementation-review.md`
- Outcome review -> `templates/retrospective.md`, `tracking/record.schema.yaml`

## Final test

Before concluding any design or review, answer these four questions explicitly:

1. What complexity was removed?
2. What complexity remains, and who pays for it?
3. What knowledge is hidden behind the abstraction?
4. What future observation would prove this design was not as good as expected?
