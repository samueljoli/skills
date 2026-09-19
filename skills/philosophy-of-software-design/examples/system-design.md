# Example: System Design — Feature Configuration

## Problem

Dozens of application instances need consistent access to small pieces of operational configuration. The initial proposal exposes a distributed KV client's read/watch/session primitives directly to each service.

## Design Concern

A raw distributed KV API may be powerful but shallow for application teams if every service must learn:

- watch reconnection;
- stale reads;
- namespace conventions;
- serialization;
- default behavior;
- metrics;
- rollout policy.

## Alternative A — Raw KV Client

Each service reads and watches keys directly.

## Alternative B — Configuration Module

```text
config.get<T>(Setting)
config.subscribe(Setting, callback)
```

The module owns namespace, serialization, fallback/default semantics, watch recovery, and observability.

## Tradeoff

Alternative B is deeper, but only if `Setting` remains a coherent application concept. If every underlying KV capability is eventually re-exposed as flags and escape hatches, the abstraction will become shallow.

## Expected Outcomes

- KV vendor migration remains inside the configuration subsystem.
- Services do not implement watch recovery independently.
- New settings follow one ownership and naming model.
- Abstraction bypasses remain rare.
