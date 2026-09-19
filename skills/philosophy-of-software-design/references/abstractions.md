# Abstraction Design Guide

## Start from the caller's mental model

Describe what the caller wants to accomplish without referencing implementation mechanisms.

Bad starting point:

> We need a Redis wrapper.

Better starting point:

> Callers need to acquire a short-lived lease for a named resource without understanding distributed lock implementation details.

## Interface budget

Every public concept costs cognitive load:

- methods;
- types;
- errors;
- flags;
- configuration;
- lifecycle states;
- ordering constraints;
- callbacks;
- extension points.

Treat each addition as something that must justify itself by hiding more complexity than it creates.

## Deep-module test

For an abstraction, list:

### Caller must know

Everything required to use it correctly.

### Module handles internally

Everything hidden from the caller.

The abstraction becomes more valuable when the second list is substantial and the first remains compact and coherent.

## Information ownership test

Write down important facts:

```text
Fact: session TTL calculation
Owner: SessionStore
Other modules that currently know it: AuthService, cleanup worker
```

If multiple modules know the same implementation fact, decide whether that duplication is necessary or leakage.

## Change containment test

Pick likely changes and predict where they should land.

Example:

```text
Change: PostgreSQL -> DynamoDB
Expected: persistence adapter + composition root
Should not require: domain model, application services, API handlers
```

The prediction becomes an outcome hypothesis for later retrospectives.

## API semantics test

For each operation ask:

- Is it idempotent where useful?
- Is absence exceptional or normal?
- Are partial failures visible at the right layer?
- Is ordering part of the contract?
- Can invalid combinations be represented?
- Are defaults safe and unsurprising?
- Can callers recover without learning implementation details?

## Configuration test

Configuration is part of the interface.

Flag configuration that:

- exposes an implementation mechanism instead of an intent;
- has coupled options that must be coordinated;
- pushes tuning decisions to callers that lack context;
- differs arbitrarily across similar modules.

Prefer intent-oriented configuration when the module can choose the mechanism.

## Escape hatch test

Ask why a future caller might bypass the abstraction.

Common reasons:

- missing batch operation;
- poor performance due to forced N+1 behavior;
- inability to express a common use case;
- errors too lossy for caller needs;
- transaction boundary placed at the wrong layer;
- abstraction hides information the caller legitimately owns.

An escape hatch can be useful, but frequent bypasses are evidence that the abstraction boundary may be wrong.
