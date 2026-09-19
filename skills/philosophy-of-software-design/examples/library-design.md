# Example: Library Design — Lease API

## Problem

Several application components need a short-lived distributed lease. The current design exposes the backing store's compare-and-set operations, TTL units, renewal timing, and vendor-specific errors.

## Complexity Map

- **Change amplification:** a TTL policy change affects every caller.
- **Cognitive load:** callers must understand acquisition, renewal, release, token matching, and vendor error semantics.
- **Unknown unknowns:** some callers renew manually while others do not; it is difficult to know which behavior is safe.

## Alternative A — Thin Store Wrapper

```text
get(key)
compare_and_set(key, old, new, ttl)
delete_if_value(key, value)
```

This hides the client library but not the lease algorithm.

## Alternative B — Lease Abstraction

```text
lease = leases.acquire(resource, duration)
lease.renew()
lease.release()
```

The library owns token generation, compare-and-set behavior, TTL representation, safe release, and vendor error translation.

## Principle Analysis

| Principle | Status | Evidence |
|---|---|---|
| Deep modules | APPLIED | Alternative B exposes the lease concept while hiding store-specific mechanics. |
| Information hiding | APPLIED | TTL encoding and token matching have one owner. |
| Pull complexity downward | APPLIED | Renewal and safe release logic are implemented once. |
| Different layer, different abstraction | APPLIED | The API exposes leases rather than storage commands. |
| Design it twice | APPLIED | Store-wrapper and lease-oriented designs were compared. |

## Expected Outcomes

- Switching the backing store should not change lease callers.
- Changing renewal policy should be local to the lease library.
- Callers should not branch on vendor-specific errors.

## Outcome Status

`PENDING` until the abstraction experiences real use and change.
