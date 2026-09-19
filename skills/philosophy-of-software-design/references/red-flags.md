# Design Red Flags

Red flags are prompts for investigation, not automatic violations.

## Shallow module

The interface exposes nearly as much complexity as the implementation hides.

Evidence examples:

- many public methods for very little policy;
- callers still need internal sequencing knowledge;
- the wrapper mostly renames lower-level operations.

## Pass-through layer

A layer forwards calls, arguments, types, and errors without providing a different abstraction.

Ask whether removing the layer would materially increase caller knowledge.

## Information leakage

Implementation decisions appear in neighboring modules through:

- database column names;
- vendor-specific errors;
- serialization details;
- timing constants;
- retry rules;
- protocol states;
- internal identifiers.

## Temporal decomposition

Code is organized by execution order rather than stable responsibility, forcing one conceptual operation to be understood across many modules.

## Repetition of policy

The same business or infrastructure rule appears in multiple call sites.

## Configuration leakage

Callers must select low-level mechanisms they are not qualified to tune.

## Special-case accumulation

The common path contains many branches for one-off clients, states, or exceptions.

## Error proliferation

Every layer introduces or forwards many distinct failures even though callers handle them identically.

## Wrapper type explosion

New types or interfaces are added primarily to satisfy architecture shape, but do not hide knowledge or enforce meaningful invariants.

## Excessive decomposition

Behavior that could be understood locally requires jumping through many tiny units with separate interfaces.

## Mixed abstraction levels

A single method combines high-level intent with low-level mechanisms.

Example:

```text
createInvoice()
  -> validate billing policy
  -> build SQL string
  -> retry HTTP connection
  -> emit metrics
```

## Generic names hiding broad responsibility

Names such as `Manager`, `Helper`, `Util`, `Processor`, or `Service` may indicate that the abstraction does not have a coherent concept. Investigate; do not reject based on naming alone.

## Caller choreography

Correct use requires callers to execute a multi-step sequence in the right order.

Ask whether the abstraction can provide one higher-level operation.

## Repeated cross-boundary conversions

The same data is transformed back and forth between representations across layers, increasing interface burden without adding meaning.

## Premature extensibility

Plugin systems, strategy interfaces, generic registries, or callbacks exist for hypothetical variation without current evidence of a change axis.
