---
name: authoritative-guidelines
description: Design, implement, and review public Rust APIs using the Rust API Guidelines. Use when adding or changing public types, traits, functions, macros, errors, or Cargo features; reviewing crate interoperability and documentation; or preparing a library release. Cite the original C-* checklist IDs and distinguish recommendations from language requirements.
---

# Authoritative Rust API Guidelines

Use the [Rust API Guidelines Checklist](https://rust-lang.github.io/api-guidelines/checklist.html) and its linked chapters as the primary design source.
The guidelines were authored largely by the Rust library team.
They are recommendations, not compiler rules or a certification standard.
The [About chapter](https://rust-lang.github.io/api-guidelines/about.html) explicitly allows judgment and exceptions.

This skill covers public library interfaces, including re-exports, trait implementations, feature flags, documentation, and dependencies exposed to callers.
For application code, apply only the relevant interface guidance.
This skill is not a complete unsafe-code audit, async guide, performance guide, or security review.

## Source and compatibility policy

Use the linked chapter to resolve the meaning of each `C-*` item.
Do not turn a checklist heading into an absolute rule when its chapter supplies exceptions.
When an old example conflicts with current language behavior, consult the current official documentation and the project's supported compiler.

Use these supplemental sources for current mechanics:

- [Rust Reference](https://doc.rust-lang.org/reference/): Language rules, trait objects, and opaque return types.
- [Standard library documentation](https://doc.rust-lang.org/std/): Trait contracts and available APIs.
- [Cargo SemVer guidance](https://doc.rust-lang.org/cargo/reference/semver.html): Changes that can break downstream code.
- [Rustdoc intra-doc links](https://doc.rust-lang.org/rustdoc/write-documentation/linking-to-items-by-name.html): Links that name Rust items directly.

SemVer means versioning based on compatibility with existing callers.
MSRV means the minimum supported Rust version.
Respect both the crate's compatibility policy and its MSRV before recommending newer syntax or dependencies.
Label supplemental advice as such instead of inventing checklist IDs.
If a source is unavailable, state the limitation instead of claiming a fresh source review.

## Workflow

1. Establish scope. Identify the affected crate, its callers, the requested change, and the existing public interface.
2. Read the constraints. Inspect `Cargo.toml`, the toolchain, CI, feature definitions, release policy, and relevant documentation.
3. Trace caller-visible behavior. Include re-exports, public trait implementations, error types, ownership, and feature-dependent APIs.
4. Identify complexity. Look for repeated caller work, confusing choices, and dependencies that make small changes break unrelated code.
5. Apply the relevant checklist sections below. For a release audit, cover every section and record areas that do not apply.
6. For consequential decisions, compare two materially different designs. Compare caller knowledge, ownership, failure behavior, and future changes.
7. Recommend the smallest justified change. Do not break a published API merely to improve naming or checklist conformance.
8. Run the appropriate validation. Separate observed results from expected benefits and untested assumptions.

For design work, show representative call sites before expanding the interface.
For implementation work, include documentation and tests for the caller-visible contract.
For review work, report evidence and caller impact rather than a list of preferences.

Watch for information leakage through dependency types, repeated validation across callers, and wrappers that only rename operations.
Do not add a trait, newtype, builder, or configuration option without explaining the complexity it removes.
Guideline conformance and design success are separate conclusions.

## Naming

- [C-CASE](https://rust-lang.github.io/api-guidelines/naming.html#c-case): Follow Rust casing conventions.
  Use `UpperCamelCase` for types, traits, and enum variants.
  Use `snake_case` for modules, functions, methods, macros, and local variables.
  Use `SCREAMING_SNAKE_CASE` for constants and statics.
  Treat acronyms as words, such as `Uuid`, not `UUID`.
  Avoid redundant `rust` or `rs` prefixes and suffixes in crate names.

- [C-CONV](https://rust-lang.github.io/api-guidelines/naming.html#c-conv): Let conversion names describe cost and ownership.
  Use `as_` for free views that generally borrow the existing representation.
  Use `to_` for conversion work that retains the original value, including conversions on `Copy` values.
  A `to_` conversion can return a borrow, as `Path::to_str` does after UTF-8 validation.
  Use `into_` when consuming a non-`Copy` value, regardless of conversion cost.
  Use `into_inner` to extract a wrapper's inner value when that operation belongs in the API.
  Follow return-type word order, such as `as_mut_slice`.

- [C-GETTER](https://rust-lang.github.io/api-guidelines/naming.html#c-getter): Name field accessors `field()` and `field_mut()`, not `get_field()`.
  Keep established `get` conventions for indexed lookup or a single obvious contained value.
  Do not rename `get(index)` to satisfy a blanket ban on `get`.
  Do not add unchecked accessors merely because the chapter describes their naming.

- [C-ITER](https://rust-lang.github.io/api-guidelines/naming.html#c-iter): For homogeneous collections, use `iter`, `iter_mut`, and `into_iter` for borrowed, mutable, and owned elements.
  Provide only the iteration forms that preserve the collection's invariants.
  Keep descriptive names when the interpretation differs, such as `str::bytes` and `str::chars`.

- [C-ITER-TY](https://rust-lang.github.io/api-guidelines/naming.html#c-iter-ty): Match named iterator types to their producing methods.
  Examples include `iter` returning `Iter`, `into_iter` returning `IntoIter`, and `keys` returning `Keys`.
  Use the containing module to disambiguate names rather than repeating the collection name everywhere.

- [C-FEATURE](https://rust-lang.github.io/api-guidelines/naming.html#c-feature): Name features after the capability, such as `serde` or `std`.
  Avoid empty prefixes such as `use-` and `with-`.
  Design features to add capabilities rather than negate them with names such as `no-std`.
  When supporting an optional standard library, use the conventional `std` feature.

- [C-WORD-ORDER](https://rust-lang.github.io/api-guidelines/naming.html#c-word-order): Keep word order consistent within the crate and with related standard-library APIs.
  For example, prefer `ParseAddrError` alongside `ParseIntError`, rather than switching to `AddrParseError`.

## Interoperability

- [C-COMMON-TRAITS](https://rust-lang.github.io/api-guidelines/interoperability.html#c-common-traits): Implement common traits when their semantics fit the type.
  Consider `Copy`, `Clone`, `Eq`, `PartialEq`, `Ord`, `PartialOrd`, `Hash`, `Debug`, `Display`, and `Default`.
  Downstream crates generally cannot add foreign trait implementations to your types.
  Make equality, ordering, and hashing agree with their trait contracts.
  Do not derive ordering or invent a default without meaningful semantics.
  If both zero-argument `new()` and `Default` exist, give them the same behavior.

- [C-CONV-TRAITS](https://rust-lang.github.io/api-guidelines/interoperability.html#c-conv-traits): Implement `From` for appropriate infallible conversions and `TryFrom` for fallible conversions.
  Implement `AsRef` and `AsMut` for suitable reference conversions.
  Implement `From` and `TryFrom` rather than `Into` and `TryInto` directly.
  Blanket implementations provide the latter pair automatically.
  This restriction does not prohibit accepting `Into` or `TryInto` as generic bounds.

- [C-COLLECT](https://rust-lang.github.io/api-guidelines/interoperability.html#c-collect): Implement `FromIterator` and `Extend` for collections where those operations make sense.
  Support construction through `collect()` and extension from an iterator.
  Define behavior for duplicates, ordering, and capacity where those details affect callers.

- [C-SERDE](https://rust-lang.github.io/api-guidelines/interoperability.html#c-serde): Provide Serde `Serialize` and `Deserialize` implementations for types that function as data structures.
  Do not apply this mechanically to resource handles or marker types.
  If serialization is optional, gate the implementations behind a feature named `serde`.
  Supplemental safety consideration: make sure that deserialization preserves invariants enforced by constructors.
  Treat the serialized representation as a separate compatibility decision.

- [C-SEND-SYNC](https://rust-lang.github.io/api-guidelines/interoperability.html#c-send-sync): Preserve `Send` and `Sync` when the type's thread-safety properties allow them.
  Prefer the compiler's automatic implementations.
  Add compile-time assertions when callers rely on these guarantees.
  Investigate raw pointers or internal state that changes these properties.
  Never add an `unsafe impl` just to satisfy this guideline.

- [C-GOOD-ERR](https://rust-lang.github.io/api-guidelines/interoperability.html#c-good-err): Return meaningful public error types rather than `Result<T, ()>`.
  Implement `Error`, including its `Debug` and `Display` requirements, using the path supported by the crate's environment and MSRV.
  Preserve underlying causes through `source()` where applicable.
  Make errors `Send + Sync` where possible.
  For erased errors, consider `Error + Send + Sync + 'static` to support common propagation and downcasting needs.
  Use concise error messages with lowercase sentence starts and no trailing punctuation, while preserving proper names.
  Do not implement deprecated `Error::description()`.

- [C-NUM-FMT](https://rust-lang.github.io/api-guidelines/interoperability.html#c-num-fmt): Implement `LowerHex`, `UpperHex`, `Octal`, and `Binary` for number types used in bitwise operations.
  This includes suitable flag types, not every wrapper around a numeric quantity.

- [C-RW-VALUE](https://rust-lang.github.io/api-guidelines/interoperability.html#c-rw-value): Accept generic `R: Read` and `W: Write` parameters by value.
  Callers can still pass `&mut reader` or `&mut writer` through standard reference implementations.
  Show that borrowing option in the documentation so callers know how to retain their stream.

## Macros

- [C-EVOCATIVE](https://rust-lang.github.io/api-guidelines/macros.html#c-evocative): Make input syntax resemble the generated Rust items.
  Use familiar keywords and punctuation, such as `struct` for a generated structure and semicolons for constants.

- [C-MACRO-ATTR](https://rust-lang.github.io/api-guidelines/macros.html#c-macro-attr): Support attributes on generated items where ordinary Rust permits them.
  Include item-specific `cfg` attributes and derives on generated structures or enums.
  Make sure that attributes apply to the intended item rather than an entire unrelated expansion.

- [C-ANYWHERE](https://rust-lang.github.io/api-guidelines/macros.html#c-anywhere): Make item macros work in each scope that permits their generated items.
  Test module scope and function scope at minimum.
  Watch for generated paths that resolve differently inside a function.

- [C-MACRO-VIS](https://rust-lang.github.io/api-guidelines/macros.html#c-macro-vis): Follow normal Rust visibility syntax.
  Generate private items by default and honor explicit visibility such as `pub` and `pub(crate)`.

- [C-MACRO-TY](https://rust-lang.github.io/api-guidelines/macros.html#c-macro-ty): Accept valid type fragments without changing their meaning through expansion scope.
  Test primitives, references, relative paths, absolute paths, `super` paths, and generic types.
  Matching `$t:ty` alone does not prove that generated code resolves the type correctly.

## Documentation

- [C-CRATE-DOC](https://rust-lang.github.io/api-guidelines/documentation.html#c-crate-doc): Explain the crate's purpose and main concepts in crate-level documentation.
  Include a useful starting example and navigation to the main APIs.
  Explain feature requirements when they affect that example.

- [C-EXAMPLE](https://rust-lang.github.io/api-guidelines/documentation.html#c-example): Give public items examples that demonstrate a reason to use them.
  A link to a shared example is sufficient when it exercises the item clearly.
  Prefer executable doctests over examples that only repeat the signature.
  Explain any use of `ignore`, `no_run`, or external prerequisites.

- [C-QUESTION-MARK](https://rust-lang.github.io/api-guidelines/documentation.html#c-question-mark): Use `?` in fallible examples rather than `try!` or unexplained `unwrap()`.
  If needed, hide a `fn main() -> Result<...>` wrapper with rustdoc's `#` lines.
  Keep the displayed example focused while the complete doctest remains executable.

- [C-FAILURE](https://rust-lang.github.io/api-guidelines/documentation.html#c-failure): Document failure contracts for functions and trait methods.
  Use an `Errors` section for error conditions and a `Panics` section for relevant panic conditions.
  Use a `Safety` section on unsafe functions to state every caller obligation.
  Do not replace those obligations with a vague instruction to be careful.
  Cover allowed failure behavior of trait implementations, not only the current implementation.
  Do not enumerate every hypothetical panic in caller-provided code.

- [C-LINK](https://rust-lang.github.io/api-guidelines/documentation.html#c-link): Link relevant types, methods, traits, and concepts.
  Current rustdoc supports intra-doc links such as ``[`Self::new`]`` and ``[`crate::Error`]``.
  Prefer these to brittle generated HTML paths shown in older examples.

- [C-METADATA](https://rust-lang.github.io/api-guidelines/documentation.html#c-metadata): Review `authors`, `description`, `license`, `repository`, `keywords`, and `categories` in `Cargo.toml`.
  The guideline recommends these fields, but they are not all mandatory Cargo fields.
  Set `documentation` when documentation lives somewhere other than the default docs.rs location.
  Set `homepage` only for a distinct project website.
  Do not duplicate the repository URL merely to fill every field.

- [C-RELNOTES](https://rust-lang.github.io/api-guidelines/documentation.html#c-relnotes): Document significant changes and clearly identify breaking changes.
  Make release notes discoverable from crate documentation or the repository.
  For release preparation, make sure that published versions map to version-control tags.
  Do not create tags, push, or publish without authorization.

- [C-HIDDEN](https://rust-lang.github.io/api-guidelines/documentation.html#c-hidden): Keep irrelevant implementation details out of user-facing documentation.
  Prefer private or `pub(crate)` visibility when external access is unnecessary.
  Use `#[doc(hidden)]` selectively for unavoidable implementation details.
  Hiding documentation does not make an item private or remove a public dependency.

## Predictability

- [C-SMART-PTR](https://rust-lang.github.io/api-guidelines/predictability.html#c-smart-ptr): Avoid inherent receiver methods on smart pointers that compete with methods on their targets.
  Use associated functions such as `Box::into_raw(value)` for pointer-specific operations.
  This guideline concerns method-resolution ambiguity, not merely redundant forwarding methods.

- [C-CONV-SPECIFIC](https://rust-lang.github.io/api-guidelines/predictability.html#c-conv-specific): Put conversions on the more specific type involved.
  For example, UTF-8 conversion belongs with strings rather than adding every possible interpretation to a byte slice.
  When specificity does not decide placement, favor convenient method chaining where appropriate.

- [C-METHOD](https://rust-lang.github.io/api-guidelines/predictability.html#c-method): Use a method when an operation has a clear receiver.
  A method improves discovery and supports automatic borrowing at the call site.
  Retain associated functions for the smart-pointer case above.

- [C-NO-OUT](https://rust-lang.github.io/api-guidelines/predictability.html#c-no-out): Return multiple results through tuples or named result structures, not artificial output parameters.
  These return values do not inherently require heap allocation.
  Preserve the explicit exception for modifying caller-owned data or reusing a buffer, such as `Read::read`.

- [C-OVERLOAD](https://rust-lang.github.io/api-guidelines/predictability.html#c-overload): Implement operators only when their meaning matches established expectations for the domain.
  Prefer a named operation when an operator obscures side effects or unusual semantics.

- [C-DEREF](https://rust-lang.github.io/api-guidelines/predictability.html#c-deref): Use `Deref` and `DerefMut` for smart-pointer behavior.
  Do not use them to simulate inheritance or import convenience methods into an unrelated wrapper.
  Remember that `String` to `str` is an intended example, not a violation.

- [C-CTOR](https://rust-lang.github.io/api-guidelines/predictability.html#c-ctor): Define constructors as inherent associated functions without a receiver.
  Use `new` for the primary constructor unless a domain verb such as `open`, `connect`, or `bind` is clearer.
  Use named conversion constructors when safety requirements, extra parameters, or input interpretation cannot fit a conversion trait.

## Flexibility

- [C-INTERMEDIATE](https://rust-lang.github.io/api-guidelines/flexibility.html#c-intermediate): Expose useful results already computed by an operation when callers otherwise repeat the work.
  Examples include an insertion position, the replaced value, or original input recovered from a failed conversion.
  Do not expose internal bookkeeping without a caller need.

- [C-CALLER-CONTROL](https://rust-lang.github.io/api-guidelines/flexibility.html#c-caller-control): Take ownership when the implementation needs ownership.
  Do not borrow only to force an internal clone that the caller cannot avoid.
  When ownership is unnecessary, borrow rather than consume and discard the argument.
  Let callers choose when to clone.
  Do not add a `Copy` bound merely to signal that copying is cheap.

- [C-GENERIC](https://rust-lang.github.io/api-guidelines/flexibility.html#c-generic): Require only the capabilities an operation uses.
  If iteration is sufficient, consider `IntoIterator` instead of requiring a particular collection.
  If contiguous borrowed storage is required, a slice can express that need directly.
  Balance useful generality against signature complexity, type inference, and code size.

- [C-OBJECT](https://rust-lang.github.io/api-guidelines/flexibility.html#c-object): Decide whether callers need to use the trait through `dyn Trait`.
  If they do, preserve dyn compatibility, formerly called object safety.
  Use `where Self: Sized` to exclude methods that only work on concrete types when that preserves the intended interface.
  Consult the [current dyn-compatibility rules](https://doc.rust-lang.org/reference/items/traits.html#dyn-compatibility), especially for generic methods, associated items, and async methods.
  Test an actual `dyn Trait` use instead of guessing from the trait declaration.

## Type safety

- [C-NEWTYPE](https://rust-lang.github.io/api-guidelines/type-safety.html#c-newtype): Use distinct wrapper types for distinct meanings with the same representation.
  These wrappers are called newtypes.
  Examples include `Meters` versus `Seconds`, or `UserId` versus `OrderId`.
  A type alias does not create this distinction.

- [C-CUSTOM-TYPE](https://rust-lang.github.io/api-guidelines/type-safety.html#c-custom-type): Use meaningful types for arguments whose intent is unclear at the call site.
  Prefer named choices over positional flags such as `configure(true, false)`.
  Do not ban `bool` for clear predicates or `Option` for genuine absence.
  Add a custom type when it clarifies meaning or enforces a useful invariant.

- [C-BITFLAG](https://rust-lang.github.io/api-guidelines/type-safety.html#c-bitflag): Use a flags type for independent choices that callers combine.
  The guideline recommends the `bitflags` crate for this representation.
  Use an enum when exactly one alternative is valid.

- [C-BUILDER](https://rust-lang.github.io/api-guidelines/type-safety.html#c-builder): Use a builder when construction has enough choices to obscure a normal constructor.
  Take required inputs in the builder constructor and expose optional configuration through chainable methods.
  Prefer a reusable, borrowed builder when the terminal operation does not need to consume it.
  When construction transfers owned resources, use consuming setters and a consuming terminal operation consistently.
  Test both chained calls and conditional configuration.
  Do not introduce a builder for a simple constructor without a concrete benefit.

## Dependability

- [C-VALIDATE](https://rust-lang.github.io/api-guidelines/dependability.html#c-validate): Enforce valid inputs rather than accepting arbitrary invalid states.
  Prefer types that rule out invalid values, then runtime validation where types cannot express the condition.
  Choose `Result`, `Option`, or documented panics according to the operation's contract.
  Supplemental safety constraint: never rely only on `debug_assert!` for conditions needed to prevent undefined behavior in safe code.
  If an unchecked operation requires callers to uphold memory-safety conditions, make it `unsafe` and document those conditions.
  Do not add unchecked variants without a demonstrated need.

- [C-DTOR-FAIL](https://rust-lang.github.io/api-guidelines/dependability.html#c-dtor-fail): Keep destructors from panicking because cleanup failed.
  A second panic during unwinding can abort the process.
  Provide an explicit fallible operation such as `close` or `finish` when callers need to observe cleanup errors.
  `Drop` can still attempt cleanup and ignore or safely report failures.
  This guideline does not prohibit all fallible operations inside `Drop`.

- [C-DTOR-BLOCK](https://rust-lang.github.io/api-guidelines/dependability.html#c-dtor-block): Avoid unexpected blocking in destructors.
  If teardown can block, provide an explicit operation that prepares for nonblocking destruction where possible.
  Document what happens when callers skip that operation.

## Debuggability

- [C-DEBUG](https://rust-lang.github.io/api-guidelines/debuggability.html#c-debug): Implement `Debug` for public types, with rare and explained exceptions.
  Supplemental security consideration: redact secrets rather than exposing them through a derived implementation.
  Do not treat diagnostic output as a stable serialization format.

- [C-DEBUG-NONEMPTY](https://rust-lang.github.io/api-guidelines/debuggability.html#c-debug-nonempty): Produce nonempty diagnostic output even for an empty value.
  Use a recognizable representation such as a type name, `[]`, or quoted empty text.

## Future proofing

- [C-SEALED](https://rust-lang.github.io/api-guidelines/future-proofing.html#c-sealed): Seal traits intended for implementation only inside the defining crate.
  A private-module supertrait is the usual mechanism.
  Document the restriction so downstream users do not attempt unsupported implementations.
  Keep traits open when downstream implementation is part of their purpose.
  Sealing does not permit arbitrary changes to methods callers use.
  Sealing an already-open public trait can break existing implementations.

- [C-STRUCT-PRIVATE](https://rust-lang.github.io/api-guidelines/future-proofing.html#c-struct-private): Keep fields private when the type owns invariants or representation choices.
  Public fields are appropriate for intentionally passive data structures with a committed representation.
  Do not add unrestricted mutable accessors that defeat the intended validation boundary.

- [C-NEWTYPE-HIDE](https://rust-lang.github.io/api-guidelines/future-proofing.html#c-newtype-hide): Hide implementation types behind a deliberate public contract.
  A newtype can hide a complex iterator representation while exposing useful traits.
  Also consider return-position `impl Trait` when a named public type is unnecessary.
  Current Rust permits multiple bounds, such as `impl Iterator<Item = T> + Clone`.
  Review promised traits and lifetime capture before changing the hidden type.
  Use the [current `impl Trait` rules](https://doc.rust-lang.org/reference/types/impl-trait.html), not limitations inferred from old examples.

- [C-STRUCT-BOUNDS](https://rust-lang.github.io/api-guidelines/future-proofing.html#c-struct-bounds): Do not copy derived trait bounds onto the structure declaration.
  Prefer `#[derive(Clone)] struct Wrapper<T>(T)` over requiring `T: Clone` on the structure itself.
  Put operational bounds on the implementations or methods that need them.
  Retain bounds required for associated types, `?Sized`, or a constrained `Drop` implementation.

## Necessities

- [C-STABLE](https://rust-lang.github.io/api-guidelines/necessities.html#c-stable): For a stable crate, review the stability of dependencies exposed through its public API.
  These are public dependencies.
  Look beyond signatures to re-exports, trait bounds, associated types, and implementations such as `From<dependency::Error>`.
  A private field does not hide a dependency exposed through a public implementation.
  The upstream guideline recommends stable public dependencies for a stable crate.
  This is not a Cargo publishing restriction or a blanket ban on private pre-1.0 dependencies.

- [C-PERMISSIVE](https://rust-lang.github.io/api-guidelines/necessities.html#c-permissive): Review crate and dependency licenses against the project's distribution requirements.
  For broad ecosystem compatibility, the guideline recommends permissive licensing, including `MIT OR Apache-2.0`.
  Make sure that metadata and license files agree.
  Flag conflicts or unknown licenses for maintainer review.
  Do not change licensing without authorization or present this recommendation as legal advice.

## Validation

Use repository CI commands when available.
Otherwise, adapt this starting set to the affected package.
Replace `<crate>` with its package name before running anything.

```bash
cargo fmt --all -- --check
cargo check -p <crate> --all-targets
cargo test -p <crate>
cargo test -p <crate> --doc
cargo clippy -p <crate> --all-targets
cargo doc -p <crate> --no-deps
```

Keep doctests in scope even when another command tests only explicit targets.
Use `--workspace` when the change affects the workspace and its members support the same test environment.
Inspect generated documentation when presentation or links change.

Extend validation to the supported configurations and relevant contracts:

- Test default features and supported `--no-default-features` builds.
- Test supported feature combinations, targets, and the MSRV.
- Use `--all-features` only when enabling every feature together is a supported configuration.
- Apply `-D warnings` when required by repository policy, not as an invented requirement of the checklist.
- Exercise collection traits, conversion failures, error sources, and promised `Send` or `Sync` implementations.
- Exercise macro scopes, visibility, attributes, and type paths when macros change.
- Test downstream call sites when signatures, trait implementations, or public dependencies change.

Compiler, test, and Clippy success do not establish soundness or full API compatibility.
Use compatibility tools already present in the repository as additional evidence, not proof.
Do not install tools, add dependencies, publish, or change project policy merely to complete the checklist.
Record commands that failed or could not run, including missing tools and environment constraints.

## Output contract

For a review, lead with findings ordered by caller impact.
Do not assign an aggregate compliance score.
For each finding, include these details:

- Location: File, line, and public symbol when available.
- Guideline: The relevant linked `C-*` ID, or an explicitly labeled supplemental source.
- Evidence: The signature, implementation, documentation, or failing call site that supports the finding.
- Caller impact: The misuse, repeated work, confusion, or compatibility risk it creates.
- Recommendation: A concrete correction and any migration cost.
- Exception: A reason to retain the design when the guideline does not fit.

Separate guideline adherence from outcome.
For adherence, use `APPLIED`, `PARTIALLY_APPLIED`, `INTENTIONAL_EXCEPTION`, `VIOLATED`, `NOT_APPLICABLE`, or `UNKNOWN` where useful.
Support each evaluated status with evidence, except when the item does not apply.
For an intentional exception, state who pays the complexity cost and when to revisit the decision.
For outcomes, distinguish observed results from expected improvements that remain untested.

For a design, show the proposed interface, representative usage, meaningful alternatives, and the compatibility tradeoff.
Explain what complexity the design removes, what callers still need to know, and which implementation decisions it hides.
State what future evidence can disprove the expected improvement.

End with scope, intentional exceptions, validation results, and remaining uncertainty.
If no actionable findings remain, say so without claiming that every guideline or safety property is proven.
