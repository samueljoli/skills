# Error Handling and Recovery

Use this reference within the modes and principles in `../SKILL.md`. Keep design principles there. Use this reference to examine failure behavior, recovery ownership, and tests.

Apply only the sections relevant to the operation. For critical operations, trace failures through recovery and the next operation. Do not infer recovery correctness from an error type or a passing success-path test.

## Start with complexity

Identify the knowledge required to handle a failure correctly. Separate essential failure conditions from complexity introduced by the interface. Name who currently pays for each burden:

- Change amplification: Recovery policy appears in several handlers that must change together.
- Cognitive load: Callers must memorize which variants are safe to propagate or retry.
- Unknown unknowns: A conversion, timeout, or partial write hides effects that another handler must understand.

Use the red flags in `red-flags.md`. Repeated handlers can indicate repetition of policy. Vendor errors crossing domain boundaries can indicate information leakage. Types that add no recovery distinction can indicate wrapper type explosion.

## Specify the failure contract

A failure contract states what callers can assume after failure. An invariant is a condition that must remain true. Start from the promised operation, not the available exception classes or error enums.

Trace a representative path:

```text
Operation -> failure detection -> propagation or conversion
          -> recovery owner -> recovery action -> caller outcome -> next operation
```

For each meaningful outcome, record the contract:

| Outcome | State and external effects | Recovery owner and action | Caller-visible result | Evidence |
|---|---|---|---|---|
| <condition> | <guaranteed, possible, or unknown effects> | <owner, action, and scope> | <what the caller must know> | <contract, code, or test> |

Include normal outcomes and expected rejections, not only infrastructure failures. Distinguish these states when they affect recovery:

- The operation completed according to its contract.
- The operation made no change.
- The operation completed only some of its effects.
- The outcome is unknown because completion cannot be established.

Do not infer an unchanged state from an error return. A timeout or cancellation does not prove that remote work stopped. Durability means that completed effects survive specified failures. State what acknowledgment promises about completion and durability.

Identify which resources remain usable after failure. For each outcome, name the invariants that still hold. State what the next operation can safely do. If the implementation provides no guarantee, record the gap instead of inventing one.

## Assign recovery to the right owner

Distinguish detection from recovery. A low-level module can detect failure without knowing the correct application response. Place recovery at the lowest layer with enough context and authority to preserve the contract.

For each boundary, ask:

- Can this layer recover without changing the requested operation?
- Does the caller own a decision that this layer cannot make?
- Does a conversion preserve every distinction needed for that decision?
- Does the next caller need to know that the operation did not complete?
- What happens if recovery itself fails?

Logging, cleanup, and propagation do not by themselves restore the promised outcome. Return success only when the operation's contract permits it. A function that handles an attempt can complete successfully even when the attempted work fails, if that distinction is explicit.

Define the scope of stopping work: operation, request, worker, resource, or process. Do not classify every I/O failure as a reason to terminate the process. Let a module report unusable state while the application owns broader shutdown policy.

Preserve diagnostic context without forcing every caller to understand implementation details. Retain causes for diagnosis when useful. Expose stable distinctions for recovery instead of requiring callers to parse error messages.

## Compare responsibility boundaries

Before adding an error case, consider semantics that make the condition normal, impossible, or safely recoverable inside the operation. Preserve outcomes that callers genuinely need to distinguish. Removing an error variant does not remove the underlying failure condition.

For consequential decisions, compare alternatives that move responsibility:

| Design | Responsibility placement | Tradeoff |
|---|---|---|
| Expose an operation with distinct outcomes | The caller owns domain-specific recovery | The caller learns necessary outcomes but repeats any shared recovery policy |
| Expose a higher-level operation that includes recovery | The module owns shared recovery and its state | The interface hides repeated work but must preserve caller intent |

For example, compare caller-managed compare-and-swap with a module-managed atomic update. Compare-and-swap updates a value only if its current value matches an expected value. The caller can need a conflict result to reject a stale decision.

An atomic-update operation can hide repeated reads and comparison retries when callers share those semantics. If it reruns a caller-supplied function, document that behavior. Keep external effects out of repeated computation unless the contract makes those effects safe.

Do not silently retry compare-and-swap with a different expected value. That changes the condition the caller requested. Changing `Result` to a named enum alone is not a different responsibility boundary.

## Examine propagation and error types

Group errors according to the decisions that handlers must make. Separate concerns when mixing them permits inappropriate propagation. Avoid introducing a distinct public type for every internal failure when callers respond identically.

An enum can represent the coherent failures of one abstraction. A broad error container can also serve a final reporting boundary. Neither choice is automatically a design violation.

Trace conversions, wildcard matches, discarded results, and generic handlers. Make sure that each preserves required recovery decisions. Flag a catch-all handler that treats a new failure as success or propagates a concern past its owner.

### Rust example: expected conflict versus storage failure

Treat this as an interface example, not a requirement to use nested `Result` types. It follows the concern separation described in the sled article linked below. Evaluate the actual caller responsibilities before choosing the representation.

Suppose `Result<(), Error>` combines a comparison conflict and a storage failure. Every caller must remember which variants need different handling. An alternative separates the two concerns:

```rust
Result<Result<(), CompareAndSwapError>, StorageError>
```

At a representative call site:

```rust
let comparison = store.compare_and_swap(key, expected, proposed)?;

match comparison {
    Ok(()) => { /* Continue after the update. */ }
    Err(conflict) => { /* Apply the caller's conflict policy. */ }
}
```

Here, `?` propagates the outer storage error. The caller still receives the comparison outcome. An interface such as `Result<SwapOutcome, StorageError>` can express the same responsibility split with named outcomes.

For Rust boundaries, examine these specific paths:

- `?` propagates an error from a `Result`. It does not perform recovery. A `From` conversion can change its type.
- `From` implementations, `map_err`, and broad error containers can erase a recovery distinction. Require conversions to preserve decisions until they reach the recovery owner.
- With suitable conversions, `??` can propagate both errors from a nested result. Separate types do not prohibit every escape path.
- Ignoring a `Result` normally produces a warning. Explicit discarding still remains possible, even with warnings treated as errors.
- A `bool` or `()` can represent a fully handled concern. Do not use it to hide incomplete work the caller must distinguish.
- An exhaustive match covers variants, not recovery correctness. A handler can match every variant and still violate the contract.
- A panic can unwind or abort, depending on the build. Do not assume destructors run on every termination path.

If cleanup must report failure, provide an explicit operation that can return it. Rust's `Drop` interface cannot return a `Result`. Do not rely on a destructor alone to communicate a required durability or completion guarantee.

State the exact propagation path that the types prohibit. Without an appropriate conversion, a particular `?` propagation path can fail to compile. That does not make all unhandled or incorrectly handled failures unrepresentable.

## Examine retries and recovery failure

An idempotent operation has the same intended effect when repeated. Do not infer this property from a transient error label. A retry is safe only when its effects and the operation's completion state permit it.

For each retry policy, establish:

- Which failures permit another attempt.
- How repeated attempts avoid duplicate effects.
- Which owner sets the attempt limit, deadline, and delay.
- How retries interact across layers.
- How cancellation stops further attempts.
- What callers receive when the retry budget ends.

For unknown completion, consider reconciliation before replay. Reconciliation determines the actual state before choosing the next action. A deduplication mechanism needs its own scope and persistence guarantees.

Trace cleanup and compensation failures too. Compensation is a new action that offsets an earlier effect. It can fail and does not necessarily restore the original state.

Preserve both the original failure and recovery failure when both matter. Identify who owns any unfinished work. State whether the resource remains available, becomes restricted, or stops accepting operations.

## Test failure behavior

Fault injection deliberately triggers failures at selected points. Use it to exercise the contract, not merely to produce an error value. Do not run failure experiments against production without explicit authorization.

Select failure points around the effects that matter:

- Before any externally visible change.
- Between effects in an operation with multiple steps.
- After a change but before its acknowledgment.
- During retry, cleanup, or compensation.
- During cancellation, restart, or concurrent work when relevant.

For each selected point, record a test plan or evidence:

| Failure point | Required property | Evidence or planned test | Execution status |
|---|---|---|---|
| <location and timing> | <state, effect, or recovery guarantee> | <test name, command, and result if run> | <planned, inspected, executed, or blocked> |

Make assertions about state and behavior. Choose properties from the contract. Examples include unchanged state after rejection, no duplicate effects after retries, and rejection of new work by damaged resources. Include the next operation after recovery to expose invalid retained state.

Use deterministic cases for known boundaries. Property tests can vary operation sequences while asserting invariants. Record the seed, operation sequence, and injected failures so that failures can be replayed.

Isolate failure controls between tests. Keep them disabled in normal operation unless the system intentionally supports controlled fault injection. Include persistent failures, not only failures that disappear on the next attempt.

An injected error return does not establish crash safety. If the contract promises crash recovery, test process interruption and restart as appropriate. Compile-fail tests can establish specific forbidden conversions, not runtime recovery correctness.

Do not claim a test passed because its source exists. Separate planned tests, inspected tests, executed results, and operational observations. Record blocked execution and remaining gaps explicitly.

## Record evidence in the existing workflow

Keep the output contract and adherence statuses from `../SKILL.md`. Do not add a separate grading system. Fit the following evidence into the existing mode outputs:

- DESIGN: Record the failure contract, recovery owner, alternatives, and test plan under error semantics and expected outcomes.
- REVIEW: Cite the concrete propagation path, affected contract, complexity symptom, and smallest useful change for each finding.
- RETROSPECTIVE: Compare predicted recovery behavior with tests, incidents, repeated workarounds, and changes to the interface.

Keep design adherence separate from safety evidence. A clear type boundary can follow information-hiding principles while its recovery implementation remains untested. A passing test establishes its exercised behavior, not universal correctness.

Use falsifiable expectations, such as adding a storage failure without changing callers that handle comparison conflicts. Revisit the boundary if callers repeatedly bypass it or duplicate the same recovery sequence. Mark unobserved outcomes `PENDING`.

## Source and limits

[Tyler Neely, Error handling in Rust, April 8, 2020](https://sled.rs/errors.html) motivates the Rust example and failure-injection guidance. The article reports bugs and stability improvements from sled's development. Treat those reports as attributed experience, not independent measurements or universal rules.

The general lesson is to preserve recovery responsibilities across interfaces. Nested results, fatal-only global enums, and local handling are contextual choices. None replaces an explicit failure contract and evidence that recovery preserves it.
