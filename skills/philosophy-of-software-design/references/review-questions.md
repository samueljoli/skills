# Review Questions

Use only the questions relevant to the design. Do not mechanically answer every question.

## Problem framing

- What user/system problem does this abstraction solve?
- What should callers be able to ignore afterward?
- What are the likely dimensions of change?
- Which constraints are essential rather than artifacts of the current implementation?

## Complexity

- What change currently amplifies across modules?
- What knowledge must a developer hold simultaneously?
- What dependencies are difficult to discover?
- Which complexity can be removed entirely?
- Which complexity must remain?
- Who has the most context to own the remaining complexity?

## Interface

- What is the smallest coherent interface that supports the real use cases?
- Which public methods/types/errors/configuration could be private?
- Does the interface express intent or mechanism?
- Are there lifecycle or ordering rules the caller must memorize?
- Are defaults safe?
- Can common operations be one call rather than choreography?

## Information hiding

- What design decisions does this module own?
- Who else knows those decisions?
- Which representation details escape the module?
- Would replacing the implementation force unrelated modules to change?

## Layers

- Does each layer provide a different abstraction?
- What complexity does this layer remove for the layer above?
- Are lower-layer types/errors leaking upward?
- Is a layer present only because an architecture diagram says it should be?

## Generality

- Can several special-purpose operations become one coherent general operation?
- Is the proposed generality required by current or credible near-term use cases?
- Is the common path being polluted by one-off behavior?

## Errors

- Does the caller need to distinguish this condition?
- Could semantics make it idempotent or normal?
- Can invalid states be prevented?
- Can the lower layer recover safely with more context?
- Are we hiding an error the caller actually owns?

## Alternatives

- What would this design look like if responsibility moved one layer down?
- What if responsibility moved one layer up?
- What if there were no new abstraction?
- What if the interface had half as many concepts?
- What design would make a likely future change local?

## Outcomes

- What change should become easier if this design succeeds?
- What should callers no longer need to know?
- What evidence would indicate the abstraction is leaking?
- What evidence would falsify our claim that the module is deep?
- When should this decision be revisited?
