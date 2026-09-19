# Principles Reference

This reference paraphrases design ideas associated with *A Philosophy of Software Design* and turns them into operational review questions. It is intentionally concise and does not reproduce the book's text.

## 1. Complexity is the primary design problem

A design is difficult when engineers must understand too much, touch too much, or discover dependencies by surprise.

Evaluate complexity through:

- change amplification;
- cognitive load;
- unknown unknowns.

The goal is not the minimum number of lines, files, functions, objects, or services. The goal is to minimize the knowledge required to make correct changes.

## 2. Prefer deep modules

A deep module provides substantial useful behavior behind a comparatively small, understandable interface.

Questions:

- How much capability does the interface buy the caller?
- How much implementation detail remains hidden?
- Does the caller still need to understand the implementation strategy?
- Would removing the module leave nearly the same conceptual burden?

A small class is not automatically a good module. Splitting behavior into many tiny units can increase total interface surface and coupling.

## 3. Hide information and design decisions

A module should own important design decisions so other modules do not need to know them.

Examples of information that often deserves one owner:

- storage representation;
- wire format;
- retry semantics;
- ordering requirements;
- cache policy;
- identifier construction;
- resource lifecycle;
- state transition rules;
- domain invariants.

When the same fact must be understood in several modules, changes to that fact are likely to amplify.

## 4. Pull complexity downward when one layer can absorb it

If every caller must perform the same sequence, understand the same policy, or handle the same low-level failure, consider moving that responsibility into the lower-level abstraction.

Good downward movement eliminates repeated caller knowledge.

Bad downward movement creates surprising behavior, mixes unrelated domain policy into infrastructure, or makes the lower layer impossible to reuse correctly.

## 5. Each layer should provide a different abstraction

A layer is justified when it changes the conceptual model, hides significant knowledge, enforces policy, combines operations, or shields callers from implementation choices.

Warning signs:

- methods mostly forward arguments unchanged;
- types from the lower layer leak through every boundary;
- errors are passed through unchanged;
- the caller must understand both layers to use either one.

## 6. General-purpose interfaces can be simpler than special-purpose ones

A small set of general operations may support many use cases with less interface surface than a collection of special cases.

This is not permission to predict every future requirement. Prefer generality that emerges from the current problem and known dimensions of change.

## 7. Define avoidable errors out of existence

Some error cases are artifacts of API semantics rather than fundamental failures.

Ask:

- Can the operation be idempotent?
- Can a missing value be a normal result?
- Can the abstraction choose a safe default?
- Can invalid states be unrepresentable?
- Can cleanup succeed even if the target is already absent?

Preserve errors when callers genuinely need to distinguish outcomes.

## 8. Design important interfaces more than once

The first plausible design is often constrained by the first mental model.

For consequential decisions, compare alternatives that differ in responsibility placement, not just naming or syntax.

Evaluate:

- interface surface;
- knowledge exposed;
- change containment;
- error semantics;
- operational behavior;
- migration path;
- likely bypass pressure.

## 9. Separate general-purpose and special-purpose code

Keep the common mechanism coherent. Push one-off policy or use-case-specific behavior toward the edge when mixing it into the general mechanism would make the abstraction harder to understand.

## 10. Consistency is a complexity tool

Consistent naming, lifecycle, error semantics, configuration, and dependency patterns allow engineers to reuse knowledge.

Consistency is not a defense of a poor pattern. Improve a bad convention deliberately and migrate toward the new one rather than creating random local exceptions.

## 11. Comments should capture information the code cannot express clearly

Useful documentation explains:

- why the abstraction exists;
- what the interface guarantees;
- invariants;
- ownership;
- units and ranges;
- surprising constraints;
- why a less-obvious approach was chosen.

Comments are not a substitute for simplifying a confusing interface.

## 12. Names should support the abstraction

Names should expose the concept the caller should think about, not accidental implementation details the caller should ignore.

A naming problem can reveal a design problem when no concise concept accurately describes a module's responsibility.

## 13. Optimize for the common case without contaminating it with exceptions

Special cases create branches in both code and mental models. Prefer designs where exceptional behavior is isolated and the normal path remains conceptually uniform.

## 14. Make complexity obvious where it cannot be hidden

Some complexity is essential. When it cannot be removed or encapsulated, make it explicit in boundaries, types, documentation, and decision records rather than scattering implicit assumptions.
