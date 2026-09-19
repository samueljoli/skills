# Complexity Diagnosis

Use this reference when a system feels difficult but the source of difficulty is unclear.

## Change amplification

A change is amplified when a small product or technical requirement triggers edits across many locations.

Look for:

- duplicated policy;
- repeated switch/if chains for the same concept;
- storage representation known outside persistence code;
- protocol rules spread across clients;
- one feature requiring coordinated edits across many unrelated modules;
- configuration duplicated at several levels;
- mirrored types that must be updated together.

Capture a representative change as:

```text
Change: Add a new delivery status
Expected owner: Delivery domain module
Actual modules touched: API, DB adapter, UI mapping, analytics mapper, event serializer, retry worker
Unexpected dependencies: analytics mapper, retry worker
```

## Cognitive load

Cognitive load is the amount of knowledge needed to use or change a design correctly.

Look for callers needing to know:

- ordering rules;
- lifecycle sequencing;
- implementation-specific errors;
- which combination of flags is valid;
- internal data representation;
- retry or transaction semantics;
- hidden global state;
- multiple abstractions for the same concept.

A useful question is:

> What would a competent engineer have to learn before making a safe change here?

Count concepts only as a rough observation, not as a quality score.

## Unknown unknowns

Unknown unknowns exist when engineers cannot readily determine what is affected by a change.

Look for:

- runtime registration with no discoverable ownership;
- implicit global state;
- callbacks whose consumers are hard to locate;
- convention-based behavior without central documentation;
- duplicated knowledge with no canonical owner;
- temporal coupling;
- side effects hidden behind generic names;
- broad interfaces that allow arbitrary cross-module reach.

Evidence can include:

- unexpected files discovered during a change;
- production incidents caused by an unrecognized dependency;
- repeated "where does this happen?" investigation;
- changes that require repository-wide search to determine impact.

## Essential vs accidental complexity

Classify complexity before trying to remove it.

### Essential

Comes from the problem itself: distributed failure, financial rules, consistency requirements, real domain states, security boundaries, regulatory constraints.

### Accidental

Comes from the chosen design: duplicate conversions, leaky interfaces, unnecessary lifecycle steps, pass-through layers, repeated error handling, excessive configuration.

The design should primarily remove accidental complexity and localize essential complexity.

## Complexity placement worksheet

For each complexity source:

| Complexity | Current payer | Best-informed owner | Repeated? | Can it be hidden? | Decision |
|---|---|---|---|---|---|
| Retry semantics | Every API service | HTTP client adapter | Yes | Mostly | Move down |
| Domain validation | Domain service | Domain model | Yes | Yes | Centralize |
| Vendor outage behavior | Integration boundary + product policy | Shared responsibility | No | Partly | Make explicit |

## Baseline measurements

When practical, capture a baseline before refactoring:

- files/modules touched by a representative change;
- public operations/types/errors;
- caller configuration knobs;
- number of implementation concepts exposed;
- recurring support questions;
- known abstraction bypasses.

These measurements are evidence, not a universal score.
