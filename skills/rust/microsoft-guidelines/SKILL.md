---
name: microsoft-guidelines
description: Design, implement, and review Rust code using Microsoft's Pragmatic Rust Guidelines. Use for Rust libraries, applications, workspaces, async APIs, error handling, macros, FFI, performance, testing, and documentation, especially when Microsoft guidance is requested. Cite the original M-* IDs and distinguish project policy from Rust language requirements.
metadata:
  source: https://microsoft.github.io/rust-guidelines/guidelines/checklist/index.html
  source-version: "2026.6"
---

# Microsoft Rust Guidelines

Use [Microsoft's checklist](https://microsoft.github.io/rust-guidelines/guidelines/checklist/index.html) and its linked chapters as the primary source.
This skill summarizes all 90 checklist items from the source version above.
It works independently of other installed skills and does not require a particular coding agent.

The [About chapter](https://microsoft.github.io/rust-guidelines/guidelines/index.html) distinguishes requirements from recommendations and allows teams to adopt the guidance selectively.
Its golden rule is to preserve a guideline's purpose rather than obey its wording blindly.
Consult each linked chapter for its exact strength and exceptions.
Do not describe Microsoft-specific policy as a compiler requirement or universal Rust consensus.

## Scope and source policy

Apply universal guidance first, then the sections relevant to the code.
Library rules target reusable interfaces, while application rules cover executable-level choices.
Do not apply an application allocator or error policy automatically to a reusable library.

Use the [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/checklist.html) as the upstream API baseline.
Use current official Rust documentation for language and toolchain behavior.
Respect the minimum supported Rust version, called the MSRV, and the project's compatibility policy.
Identify disagreements between sources instead of silently combining conflicting rules.

Supplemental safeguards in this skill qualify examples that depend on workload, toolchain, security requirements, or deployment environment.
They do not create new Microsoft guideline IDs.
Soundness is not an optional policy: safe callers must not be able to cause undefined behavior through an abstraction.
A checklist review does not replace a complete unsafe-code or security audit.

Source correction: the checklist currently links `M-SYS-CRATES` to the resilience chapter.
The actual rule is in the building chapter, which this skill links below.
If sources become unavailable or change, report that limitation rather than claiming a fresh source review.

## Workflow

1. Establish the task and affected interface. Identify library, application, macro, FFI, and internal-only crates.
2. Read project constraints. Inspect manifests, toolchains, CI, supported platforms, runtime choices, and compatibility promises.
3. Trace representative callers. Include ownership, errors, public dependencies, feature combinations, and initialization requirements.
4. Identify complexity. Look for repeated caller work, confusing interfaces, and hidden dependencies that make changes spread unexpectedly.
5. Select applicable guidelines. For a complete audit, cover every section and identify areas outside scope.
6. Compare alternatives for consequential decisions. Consider a simpler concrete design before adding wrappers, traits, crate boundaries, or generic parameters.
7. Recommend the smallest justified change. Account for downstream migration and existing conventions.
8. Run targeted validation. Separate observed results from predicted improvements and unresolved risks.

Look for information leakage, repeated policy, unnecessary wrappers, caller sequencing requirements, and speculative extension points.
Do not split code merely to increase the number of modules or crates.
A boundary earns its cost by hiding knowledge or supporting independent use.
Keep design decisions in existing review or decision records, not as agent self-reports inside public API documentation.

## Universal

- [M-UPSTREAM-GUIDELINES](https://microsoft.github.io/rust-guidelines/guidelines/universal/#M-UPSTREAM-GUIDELINES): Apply upstream Rust API, style, design-pattern, and undefined-behavior guidance alongside this collection.
  Pay particular attention to conversion names, getters, applicable common traits, constructors, and feature names.
  When meaningful, provide `new()` even when an equivalent `Default` implementation exists.

- [M-STATIC-VERIFICATION](https://microsoft.github.io/rust-guidelines/guidelines/universal/#M-STATIC-VERIFICATION): Use compiler lints, Clippy, rustfmt, dependency auditing, feature testing, and unused-dependency analysis.
  Microsoft recommends cargo-audit, cargo-hack, cargo-udeps, and Miri for their respective tasks.
  Read the chapter's current lint configuration before proposing changes instead of copying an outdated list.
  Match lint availability to the toolchain and use repository CI as the execution baseline.

- [M-LINT-OVERRIDE-EXPECT](https://microsoft.github.io/rust-guidelines/guidelines/universal/#M-LINT-OVERRIDE-EXPECT): Prefer `#[expect(..., reason = "...")]` for local lint exceptions when the MSRV supports it.
  An unfulfilled expectation reveals a stale exception.
  Keep justified `#[allow]` uses for generated code and macros where an expectation is unsuitable.

- [M-PUBLIC-DEBUG](https://microsoft.github.io/rust-guidelines/guidelines/universal/#M-PUBLIC-DEBUG): Implement `Debug` for public types.
  For sensitive values, use a custom redacted representation and tests that make sure secrets remain absent.
  Test both useful type identification and the absence of sensitive content.

- [M-PUBLIC-DISPLAY](https://microsoft.github.io/rust-guidelines/guidelines/universal/#M-PUBLIC-DISPLAY): Implement `Display` for types intended for people to read, including errors and suitable string wrappers.
  Follow normal display conventions for newlines and escapes.
  Apply the same sensitive-data safeguards as for `Debug`.

- [M-SMALLER-CRATES](https://microsoft.github.io/rust-guidelines/guidelines/universal/#M-SMALLER-CRATES): Favor separate crates for capabilities that callers can use independently.
  Use features for additions that do not stand alone, or to select constituents of an umbrella crate.
  Compare dependency isolation and compilation benefits against added public interfaces and maintenance cost.
  Do not claim faster builds without measurements.

- [M-WEASEL-WORDS](https://microsoft.github.io/rust-guidelines/guidelines/universal/#M-WEASEL-WORDS): Replace vague names such as `Manager`, `Service`, and `Factory` when they add no useful meaning.
  Name the responsibility, such as `BookingDispatcher`.
  Use the builder convention for construction and a callable such as `impl Fn() -> T` for repeatable creation when suitable.

- [M-SHORT-NAMES](https://microsoft.github.io/rust-guidelines/guidelines/universal/#M-SHORT-NAMES): Prefer short identifiers, usually no more than two short words.
  Let module qualification provide context, such as `foo::Id`, instead of repeating it in every item name.
  Use familiar abbreviations without sacrificing meaning and explain necessary exceptions.

- [M-REGULAR-FN](https://microsoft.github.io/rust-guidelines/guidelines/universal/#M-REGULAR-FN): Use free functions for computation with no clear receiver.
  Reserve inherent associated functions mainly for construction and operations that belong to the type.
  This does not prohibit receiver methods or associated trait functions such as `Default::default`.

- [M-DOCUMENTED-MAGIC](https://microsoft.github.io/rust-guidelines/guidelines/universal/#M-DOCUMENTED-MAGIC): Name and document non-obvious constants in production code.
  Explain why the value exists, consequences of changing it, and any external system that constrains it.
  Do not substitute a comment that merely repeats the arithmetic.

- [M-LOG-STRUCTURED](https://microsoft.github.io/rust-guidelines/guidelines/universal/#M-LOG-STRUCTURED): Emit named structured events with separate properties and message templates.
  Use stable event names, relevant OpenTelemetry attribute conventions, and privacy-safe values.
  Avoid eager `format!` allocation when the logging API can retain structured fields.
  Make sure the telemetry backend supports template rendering before copying the chapter's template syntax.

## Library interoperability

- [M-TYPES-SEND](https://microsoft.github.io/rust-guidelines/guidelines/libs/interop/#M-TYPES-SEND): Under Microsoft's interoperability policy, public futures must be `Send`, and most public types also need it.
  Add compile-time assertions for important future-returning entry points and explicit future types.
  Review values held across `.await`, including `Rc` and guards.
  Document genuinely local-only exceptions instead of inventing an unsound `unsafe impl Send`.

- [M-ESCAPE-HATCHES](https://microsoft.github.io/rust-guidelines/guidelines/libs/interop/#M-ESCAPE-HATCHES): Provide native-handle access and conversion when interoperation requires it.
  Distinguish borrowed access from ownership transfer and document validity, lifetime, and destruction obligations.
  Mark a conversion `unsafe` when callers must uphold memory-safety conditions, not merely because a handle is involved.

- [M-DONT-LEAK-TYPES](https://microsoft.github.io/rust-guidelines/guidelines/libs/interop/#M-DONT-LEAK-TYPES): Prefer standard-library types over unnecessary third-party types in public interfaces.
  Exceptions include umbrella-crate siblings, feature-gated integrations, and substantial ecosystem interoperability benefits.
  Treat every exposed foreign type as a compatibility commitment, including types in public trait implementations.

- [M-FOREIGN-REEXPORTS](https://microsoft.github.io/rust-guidelines/guidelines/libs/interop/#M-FOREIGN-REEXPORTS): Normally let users import third-party items from their defining crate.
  Avoid aliases that obscure type identity.
  Preserve exceptions for umbrella crates, technical crate splits, and hidden macro-support paths.

- [M-IMPL-ASREF](https://microsoft.github.io/rust-guidelines/guidelines/libs/interop/#M-IMPL-ASREF): Consider `impl AsRef<str>`, `impl AsRef<Path>`, and `impl AsRef<[u8]>` for flexible function inputs.
  Use this when borrowing is sufficient or owned conversion costs are acceptable.
  If ownership is required on a hot path, accepting the owned value can avoid a forced copy.
  Do not spread `AsRef` type parameters through public structures without a concrete need.

- [M-IMPL-RANGEBOUNDS](https://microsoft.github.io/rust-guidelines/guidelines/libs/interop/#M-IMPL-RANGEBOUNDS): Represent ranges with standard range types rather than pairs of loosely related numbers.
  If arbitrary bounds are supported, accept `impl RangeBounds<T>`.
  Define how inclusive, exclusive, empty, and unbounded ranges behave.

- [M-IMPL-IO](https://microsoft.github.io/rust-guidelines/guidelines/libs/interop/#M-IMPL-IO): Separate parsing and initialization logic from specific files or network transports.
  For synchronous streams, accept suitable `Read` or `Write` implementations.
  Microsoft recommends `futures::io` traits for async functions intended to work across runtimes.
  Do not replace an existing runtime contract without checking adapters and caller needs.

## Library usability

- [M-SIMPLE-ABSTRACTIONS](https://microsoft.github.io/rust-guidelines/guidelines/libs/ux/#M-SIMPLE-ABSTRACTIONS): Avoid deeply nested generic types that users must name in their own structures.
  Prefer simple service handles over crate-imposed types such as `Service<Backend<Store>>`.
  Keep legitimate container parameters and caller-chosen nesting.
  Judge complexity by caller knowledge, not the mere presence of generics.

- [M-AVOID-WRAPPERS](https://microsoft.github.io/rust-guidelines/guidelines/libs/ux/#M-AVOID-WRAPPERS): Hide incidental `Arc`, `Rc`, `Box`, and interior-mutability wrappers behind ordinary owned or borrowed inputs.
  Expose a wrapper when it is fundamental to the API or measurements justify its cost to callers.
  Do not introduce redundant wrapper types solely to hide another wrapper's spelling.

- [M-DI-HIERARCHY](https://microsoft.github.io/rust-guidelines/guidelines/libs/ux/#M-DI-HIERARCHY): For dependencies, prefer concrete types, then generics, then dynamic dispatch as needs grow.
  For internal mock alternatives, consider a private enum before creating a public implementation trait.
  When callers provide implementations, use narrow traits over inherent functionality.
  If generic nesting becomes costly, consider encapsulated dynamic dispatch rather than exposing wrapper-heavy signatures.

- [M-ERRORS-CANONICAL-STRUCTS](https://microsoft.github.io/rust-guidelines/guidelines/libs/ux/#M-ERRORS-CANONICAL-STRUCTS): Microsoft's library convention uses situation-specific error structs with backtraces, optional causes, and useful inspection methods.
  Keep internal error-kind enums private and expose only meaningful recovery queries.
  Implement `Debug`, `Display`, and `Error`, preserving causes through `source()` where applicable.
  The chapter's `Display` convention includes a summary, backtrace, and available cause information.
  Use normal `Backtrace::capture()` behavior rather than forcing expensive captures on every error.
  This is a Microsoft policy choice, not a Rust prohibition on public error enums.

- [M-FROM-ERROR](https://microsoft.github.io/rust-guidelines/guidelines/libs/ux/#M-FROM-ERROR): Centralize canonical conversions with `From` and let `?` apply them.
  Keep `map_err` when adding call-site context or converting foreign errors without a suitable implementation.
  Review public-dependency exposure before adding `From<foreign::Error>`.

- [M-INIT-BUILDER](https://microsoft.github.io/rust-guidelines/guidelines/libs/ux/#M-INIT-BUILDER): Use builders when optional construction choices produce too many constructor combinations.
  The chapter permits inherent constructors for up to two optional inputs and recommends builders beyond that.
  Use `Foo::builder(...)`, a `FooBuilder`, chainable field-named setters, and a final `build()`.
  Avoid a separate public `FooBuilder::new()` entry point.
  Supply required inputs at builder creation, grouping related dependencies when useful.

  For runtime-specific dependencies, use explicit entry points such as `builder_tokio(deps)`.
  A dependency struct does not automatically make future required-field additions backward-compatible.

- [M-INIT-CASCADED](https://microsoft.github.io/rust-guidelines/guidelines/libs/ux/#M-INIT-CASCADED): For initialization with four or more parameters, consider semantic groups such as `Account` and `Currency`.
  Let helper types prevent parameter mix-ups instead of merely packing unrelated values into a bag.

- [M-SERVICES-CLONE](https://microsoft.github.io/rust-guidelines/guidelines/libs/ux/#M-SERVICES-CLONE): Give heavyweight shared service handles cheap, shared-ownership `Clone` semantics.
  An internal `Arc<Inner>` can provide this without exposing `Arc` to callers.
  Document that cloning shares the service rather than duplicating its resources.

- [M-ESSENTIAL-FN-INHERENT](https://microsoft.github.io/rust-guidelines/guidelines/libs/ux/#M-ESSENTIAL-FN-INHERENT): Expose a type's essential operations as inherent methods.
  Let trait implementations forward to those operations rather than requiring hidden trait imports for basic use.
  Preserve standard trait conventions and the upstream exception for smart-pointer method collisions.

- [M-BALANCED-MODULES](https://microsoft.github.io/rust-guidelines/guidelines/libs/ux/#M-BALANCED-MODULES): Put essential entry types at the crate root and group supporting items by use case.
  Prefer meaningful groups such as `account` or `network` over generic buckets such as `traits`.
  Avoid both an overcrowded root and excessive empty navigation layers.

- [M-NO-PRELUDE](https://microsoft.github.io/rust-guidelines/guidelines/libs/ux/#M-NO-PRELUDE): Under Microsoft policy, do not introduce a prelude intended for wildcard import.
  Improve discoverability through module design and explicit imports instead.
  Removing an existing public prelude still requires a compatibility plan.

- [M-PARAMETER-CONSISTENCY](https://microsoft.github.io/rust-guidelines/guidelines/libs/ux/#M-PARAMETER-CONSISTENCY): Keep shared conceptual parameters in the same order across related functions.
  Put call-specific inputs before ubiquitous context and place the closure last.
  Microsoft recommends avoiding multiple closure parameters in one function.

- [M-COLLECTION-TRAITS](https://microsoft.github.io/rust-guidelines/guidelines/libs/ux/#M-COLLECTION-TRAITS): Provide appropriate owned, shared, and mutable iteration for custom collections.
  Include `IntoIterator`, `FromIterator`, `Extend`, and named iterator types where applicable.
  Report truthful `size_hint()` values and implement stronger iterator traits only when their contracts hold.
  Do not expose mutable iteration that violates collection invariants.

- [M-ASYNC-FN](https://microsoft.github.io/rust-guidelines/guidelines/libs/ux/#M-ASYNC-FN): Prefer `async fn` when it expresses the intended contract directly.
  Keep explicit future-returning signatures when trait contracts, `Send` bounds, or measured future-size concerns require them.
  Account for when work executes: before returning a future versus when that future is polled.

## Library resilience

- [M-MOCKABLE-SYSCALLS](https://microsoft.github.io/rust-guidelines/guidelines/libs/resilience/#M-MOCKABLE-SYSCALLS): Make I/O, clocks, randomness, and environment-dependent operations controllable in tests.
  Accept a mockable provider or expose a mocked constructor returning `(instance, controller)`.
  Avoid implicit, non-mockable I/O initialization through `Default`.
  A private enum can select real and mocked implementations without infecting the public API with generics.
  Ordinary allocation does not require mocking, but externally driven memory use still needs reasonable bounds.

- [M-TEST-UTIL](https://microsoft.github.io/rust-guidelines/guidelines/libs/resilience/#M-TEST-UTIL): Gate externally usable testing capabilities behind an explicitly named feature, preferably `test-util`.
  This includes mock controls, fake data, sensitive inspection, and test-only overrides.
  Supplemental safeguard: Cargo features unify, so a feature flag alone is not a security boundary.
  Make sure production builds do not unintentionally enable dangerous test capabilities.

- [M-INTEGRATION-TESTS](https://microsoft.github.io/rust-guidelines/guidelines/libs/resilience/#M-INTEGRATION-TESTS): Put tests that exercise only public APIs under `tests/`.
  Prefer these over internal unit tests when either can test the same behavior.
  Keep unit tests when private implementation details genuinely require direct access.

- [M-STRONG-TYPES](https://microsoft.github.io/rust-guidelines/guidelines/libs/resilience/#M-STRONG-TYPES): Use the appropriate standard type family early, such as `Path` and `PathBuf` for filesystem paths.
  Do not force paths through UTF-8 strings without a domain requirement.
  The chapter preserves ordinary numeric API conventions rather than demanding numeric wrappers everywhere.

- [M-STRONG-TYPES-GUARD](https://microsoft.github.io/rust-guidelines/guidelines/libs/resilience/#M-STRONG-TYPES-GUARD): Make invariant-carrying newtypes enforce their own validity.
  If only some source values are valid, provide fallible construction and `TryFrom` or `FromStr` conversions.
  Do not offer infallible `From` for unrestricted weaker inputs.
  Keep fields private and make all mutation and deserialization paths preserve the invariant.
  Additional panicking constructors are allowed, with `const` construction preferred where appropriate.

- [M-BUILD-RESULT](https://microsoft.github.io/rust-guidelines/guidelines/libs/resilience/#M-BUILD-RESULT): Let builder setters collect configuration without repeated error handling.
  Perform final and cross-field validation in `build()`, returning `Result` when construction is fallible.
  Retain validated input types when they already encode the required invariant.

- [M-NO-GLOB-REEXPORTS](https://microsoft.github.io/rust-guidelines/guidelines/libs/resilience/#M-NO-GLOB-REEXPORTS): Name public re-exports explicitly instead of using `pub use module::*`.
  This keeps accidental additions out of the public interface.
  Preserve narrow technical exceptions such as forwarding a selected platform implementation.

- [M-AVOID-STATICS](https://microsoft.github.io/rust-guidelines/guidelines/libs/resilience/#M-AVOID-STATICS): Avoid correctness-critical library state in statics or thread-local storage.
  Multiple linked versions of a crate can create separate copies of supposedly shared state.
  Performance-only caches are acceptable when duplication cannot change correctness.

- [M-LOG-NOT-PRINT](https://microsoft.github.io/rust-guidelines/guidelines/libs/resilience/#M-LOG-NOT-PRINT): Route production diagnostics through the project's telemetry system instead of `println!` or `dbg!`.
  Preserve intentional stdout output that forms a command-line application's user interface.

## Library building

- [M-OOBE](https://microsoft.github.io/rust-guidelines/guidelines/libs/building/#M-OOBE): Make libraries build on supported platforms without undocumented tools or environment variables.
  Microsoft targets broad Tier 1 support, with explicit exceptions for platform-specific crates and staged support.
  Generate artifacts before publication when consumers do not need the generator.
  Include transitive native dependencies in this review.

- [M-SYS-CRATES](https://microsoft.github.io/rust-guidelines/guidelines/libs/building/#M-SYS-CRATES): For native wrappers, manage the build inside the `-sys` crate and minimize external prerequisites.
  Microsoft favors embedded, verifiable sources, pregenerated bindings, optional external tools, and `cc`-based builds.
  Its policy also calls for static and dynamic loading support where applicable.
  Document justified deviations and make sure downloaded sources match pinned hashes.
  Support offline source roots for hermetic builds, which run without access to external resources.

- [M-FEATURES-ADDITIVE](https://microsoft.github.io/rust-guidelines/guidelines/libs/building/#M-FEATURES-ADDITIVE): Make features add capabilities without removing or changing existing public items.
  Enable prerequisites through Cargo feature relationships rather than relying on callers to combine flags correctly.
  Prefer `std` over `no-std` and test combinations of features supported on the target platform.
  Treat mutually exclusive feature designs as a policy finding, not an excuse to silently skip coverage.

## Macros

- [M-MACRO-LAST-RESORT](https://microsoft.github.io/rust-guidelines/guidelines/macros/#M-MACRO-LAST-RESORT): Prefer ordinary language features when they solve the problem clearly.
  Use macros for predictable repetition that users understand but do not need to write manually.
  Account for compile time, diagnostics, and edition behavior before adding macro machinery.

- [M-EXAMPLE-OVER-PROC](https://microsoft.github.io/rust-guidelines/guidelines/macros/#M-EXAMPLE-OVER-PROC): Prefer `macro_rules!` over procedural macros when it can express the required transformation.
  Do not pay for procedural machinery merely to replace a straightforward declarative macro.

- [M-MACROS-DONT-LIE](https://microsoft.github.io/rust-guidelines/guidelines/macros/#M-MACROS-DONT-LIE): Keep the written item consistent with its generated shape and signature.
  Do not invisibly add parameters, change a struct into an enum, or change whether an operation is async.

- [M-MACRO-MAIN-CRATE](https://microsoft.github.io/rust-guidelines/guidelines/macros/#M-MACRO-MAIN-CRATE): Microsoft permits procedural macros to target their main crate's canonical path only.
  Avoid complex support for direct companion-crate use or renamed dependencies unless the project explicitly promises it.
  Do not remove existing supported invocation paths without reviewing compatibility.

- [M-MACRO-VERSION-PIN](https://microsoft.github.io/rust-guidelines/guidelines/macros/#M-MACRO-VERSION-PIN): Pin tightly coupled companion macro crates to the same exact `=x.y.z` version.
  Apply the pin through the companion chain and coordinate releases.
  Do not apply this rule to independently consumed macro libraries.

- [M-MACRO-HELPERS](https://microsoft.github.io/rust-guidelines/guidelines/macros/#M-MACRO-HELPERS): Re-export third-party expansion dependencies through a hidden `_private` module in the host crate.
  Generate fully qualified paths through that module instead of requiring undocumented downstream dependencies.
  Hidden support items still need compatibility with generated code.

- [M-PROC-IMPL](https://microsoft.github.io/rust-guidelines/guidelines/macros/#M-PROC-IMPL): Keep the procedural-macro crate thin and place transformations in a regular implementation crate.
  Test token transformations there and test consumer-facing failures through compile tests such as trybuild.
  Re-export the macros through the main crate.

- [M-PROC-IMPLIED-ITEMS](https://microsoft.github.io/rust-guidelines/guidelines/macros/#M-PROC-IMPLIED-ITEMS): Avoid inventing invisible public types or collision-prone helper names during expansion.
  Make generated items predictable from the input and test multiple expansions in the same scope.
  The chapter permits carefully designed same-name items in different Rust namespaces, not arbitrary hidden public APIs.

## Applications

- [M-MIMALLOC-APPS](https://microsoft.github.io/rust-guidelines/guidelines/apps/#M-MIMALLOC-APPS): Microsoft recommends mimalloc as an application's global allocator.
  Treat adoption as an executable-level decision and benchmark the actual workload and supported targets.
  Do not promise the chapter's anecdotal gains or install a global allocator from a reusable library.

- [M-APP-ERROR](https://microsoft.github.io/rust-guidelines/guidelines/apps/#M-APP-ERROR): Applications and application-only internal crates can use anyhow, eyre, or another application error type.
  Choose one application-level convention instead of mixing several equivalent frameworks.
  Preserve structured library errors when independent consumers need to inspect or recover from failures.

- [M-TARGET-CPU](https://microsoft.github.io/rust-guidelines/guidelines/apps/#M-TARGET-CPU): Build server applications for the strongest CPU baseline guaranteed across their deployment targets.
  Make sure every deployment target supports the selected CPU features before changing build flags.
  Do not use `target-cpu=native` for distributed artifacts merely because the build host supports it.

## Foreign-function interfaces

FFI means calling across a foreign-language or binary interface.
DLLs are dynamically loaded libraries.
Apply these rules to the whole ownership and lifecycle contract, not just the visible function signature.

- [M-ISOLATE-DLL-STATE](https://microsoft.github.io/rust-guidelines/guidelines/ffi/#M-ISOLATE-DLL-STATE): Exchange only data with a defined representation and portable semantics across independently compiled libraries.
  Do not assume shared Rust layouts, allocators, statics, thread-local state, or `TypeId` identity.
  `repr(C)` alone does not make nested contents or their operations portable.
  Keep opaque resource ownership and destruction with the originating library rather than transferring Rust collection ownership blindly.

- [M-FFI-TRANSLATES](https://microsoft.github.io/rust-guidelines/guidelines/ffi/#M-FFI-TRANSLATES): Keep business logic in a safe, testable Rust core and boundary translation in the FFI crate.
  Translate ownership, buffers, errors, and handles at that boundary instead of imposing C layouts on the core model.
  Supplemental safeguard: document pointer validity, allocation ownership, and unwind behavior for every exported boundary.

- [M-FFI-NAMING](https://microsoft.github.io/rust-guidelines/guidelines/ffi/#M-FFI-NAMING): Use `-sys` for imports from an existing native library and `-ffi` for exports to foreign callers.
  Preserve established package naming where compatibility requires it.

## Correctness

- [M-UNSAFE](https://microsoft.github.io/rust-guidelines/guidelines/correctness/#M-UNSAFE): Justify unsafe code through a necessary abstraction, measured performance need, or FFI and platform interaction.
  Prefer established safe alternatives and keep the unsafe implementation small.
  Document the safety argument and test adversarial callbacks, panic paths, and misbehaving safe trait implementations.
  Use Miri where supported, including adversarial cases.
  Never bypass lifetime or `Send` requirements merely to silence the compiler.

- [M-UNSAFE-IMPLIES-UB](https://microsoft.github.io/rust-guidelines/guidelines/correctness/#M-UNSAFE-IMPLIES-UB): Reserve `unsafe` API contracts for obligations whose violation can cause undefined behavior.
  Do not mark an operation unsafe merely because it deletes data or performs a privileged action.
  Correct use of `unsafe` does not itself imply undefined behavior.

- [M-UNSOUND](https://microsoft.github.io/rust-guidelines/guidelines/correctness/#M-UNSOUND): Reject abstractions that permit undefined behavior through safe use, even under unusual call sequences.
  Enforce invariants within the abstraction's privacy boundary or expose an honest unsafe contract where enforcement is impossible.
  Soundness has no policy exception, and passing tests does not prove it.

- [M-PANIC-IS-STOP](https://microsoft.github.io/rust-guidelines/guidelines/correctness/#M-PANIC-IS-STOP): Treat a panic as a request to stop, not a recoverable error transport mechanism.
  Do not assume unwinding or a catcher exists, because the application can use `panic = "abort"`.
  Maintain memory safety even when unwinding occurs.

- [M-PANIC-ON-BUG](https://microsoft.github.io/rust-guidelines/guidelines/correctness/#M-PANIC-ON-BUG): Under this policy, panic when an unrecoverable programming defect is detected.
  Distinguish violated programmer contracts from expected failure, such as invalid text passed to a parser.
  Return `Result` for ordinary input and operational failures.
  Prefer types that prevent invalid states before adding new panic paths.

- [M-PANIC-CONTINUATION](https://microsoft.github.io/rust-guidelines/guidelines/correctness/#M-PANIC-CONTINUATION): Treat `catch_unwind` as a last-resort boundary, not general library error handling.
  Microsoft's recovery policy favors controlled restart after a panic, allowing unrelated requests to finish where appropriate.
  Do not assume caught state remains valid or that aborting panics can be caught.
  Changing a service restart policy requires explicit operational review.

- [M-PANIC-MESSAGE](https://microsoft.github.io/rust-guidelines/guidelines/correctness/#M-PANIC-MESSAGE): Give intentional production panics a message explaining the violated expectation and useful values.
  Distinguish caller misuse from an internal defect and avoid leaking secrets.
  The chapter does not require custom messages for every test assertion.

## Performance

- [M-THROUGHPUT](https://microsoft.github.io/rust-guidelines/guidelines/performance/#M-THROUGHPUT): Reduce wasted CPU work through batching, independent work partitions, and useful data locality.
  Sleep or yield when idle rather than spinning for individual items.
  Balance throughput against latency requirements and use shared state only when it beats recomputation.

- [M-HOTPATH](https://microsoft.github.io/rust-guidelines/guidelines/performance/#M-HOTPATH): Identify performance-critical paths early and maintain representative benchmarks.
  Profile CPU use and allocations, with benchmark debug symbols where needed.
  Measure total CPU work as well as elapsed time when practical.
  Treat source anecdotes as motivation, not evidence about the current project.

- [M-YIELD-POINTS](https://microsoft.github.io/rust-guidelines/guidelines/performance/#M-YIELD-POINTS): Keep long CPU-heavy async work from starving other tasks.
  Use bounded chunks, explicit yield points, or suitable runtime execution facilities.
  The chapter suggests 10–100 microseconds between yields as an initial tuning range, not a universal deadline.
  An `.await` on an immediately ready future does not guarantee a scheduler handoff.

- [M-MEM-REUSE](https://microsoft.github.io/rust-guidelines/guidelines/performance/#M-MEM-REUSE): Offer ways to reuse caller-owned buffers or workspaces in allocation-heavy paths.
  Use existing capacity and `clear()` where that preserves the required semantics.
  This is the upstream output-parameter exception for real reusable storage, not permission for arbitrary output arguments.

- [M-LOG-OVERHEAD](https://microsoft.github.io/rust-guidelines/guidelines/performance/#M-LOG-OVERHEAD): Evaluate telemetry overhead with collection enabled under realistic load.
  Prefer batch-level diagnostics and structured values over allocated messages in inner loops.
  Do not add high-volume events merely because individual calls look cheap.

- [M-AVOID-INDIRECTION](https://microsoft.github.io/rust-guidelines/guidelines/performance/#M-AVOID-INDIRECTION): Avoid unnecessary nested heap lookups in hot data structures.
  Prefer embedded data or nearby hot fields when shared ownership is unnecessary.
  If caching a field's value, preserve consistency rather than introducing stale duplicated state.

- [M-BOX-DST](https://microsoft.github.io/rust-guidelines/guidelines/performance/#M-BOX-DST): Consider internal `Box<[T]>`, `Box<str>`, or shared equivalents for numerous fixed-size, owned sequences.
  This can remove unused capacity and reduce handle size without exposing storage choices to callers.
  A boxed slice has fixed length but does not automatically make its elements immutable.

- [M-SHRINK-TO-FIT](https://microsoft.github.io/rust-guidelines/guidelines/performance/#M-SHRINK-TO-FIT): Consider shrinking large, long-lived collections after growth finishes.
  Avoid redundant shrinking before conversions that already discard spare capacity.
  Account for reallocation cost and future reuse, and do not assume `shrink_to_fit` guarantees exact capacity.

- [M-FAST-HASHER](https://microsoft.github.io/rust-guidelines/guidelines/performance/#M-FAST-HASHER): Consider a faster non-cryptographic hasher for trusted internal keys.
  Preserve collision-attack resistance when keys are attacker-controlled or influenced by untrusted input.
  Establish the trust boundary and benchmark before replacing the default hasher.

- [M-INITIAL-CAPACITY](https://microsoft.github.io/rust-guidelines/guidelines/performance/#M-INITIAL-CAPACITY): Reserve suitable capacity when a collection's expected size is known.
  Prefer iterator construction when it can use a truthful size hint instead of manual growth.
  Bound reservations derived from untrusted lengths.

- [M-ASYNC-STACK-SIZE](https://microsoft.github.io/rust-guidelines/guidelines/performance/#M-ASYNC-STACK-SIZE): Measure important future sizes with `size_of_val` and track justified limits.
  Reduce large parameters, results, and locals retained across `.await`.
  Consider synchronous setup before returning a future when measurements justify the change.
  Review effects on execution timing, cancellation, and `Send` guarantees.

## Project structure

- [M-CARGO-WORKSPACE](https://microsoft.github.io/rust-guidelines/guidelines/project/#M-CARGO-WORKSPACE): Put related crates in a workspace and inherit shared metadata, lints, and dependency definitions.
  Centralize even crate-specific dependency versions.
  Microsoft's convention disables dependency defaults centrally and enables needed features at member use sites.
  Do not change existing default-feature behavior without reviewing the resulting graph.

- [M-CRATES-IN-WORKSPACE](https://microsoft.github.io/rust-guidelines/guidelines/project/#M-CRATES-IN-WORKSPACE): List project crates as members and declare canonical internal dependencies with path and version at the root.
  Let members use `workspace = true` instead of duplicating sibling paths and versions.

- [M-CRATES-FLAT-FOLDER](https://microsoft.github.io/rust-guidelines/guidelines/project/#M-CRATES-FLAT-FOLDER): Prefer sibling crates under one workspace folder such as `crates/`.
  Group large workspaces by domain without placing production crates inside other crates or their `src/` folders.
  Preserve legitimate fixture-crate exceptions for workspace-processing tests.

- [M-LATEST-EDITION](https://microsoft.github.io/rust-guidelines/guidelines/project/#M-LATEST-EDITION): Use the latest stable edition supported by the intended toolchain for new crates.
  Do not silently migrate existing editions or raise an established MSRV.
  Current Cargo clarification: [virtual workspaces require an explicit resolver](https://doc.rust-lang.org/cargo/reference/workspaces.html#virtual-workspace).
  Do not copy the chapter's general resolver-omission advice into a virtual workspace.

- [M-MSRV](https://microsoft.github.io/rust-guidelines/guidelines/project/#M-MSRV): Declare a library MSRV and update it deliberately as features require newer compilers.
  Microsoft recommends staying a few releases behind the newest compiler and permits minor-release MSRV increases.
  Respect the project's own release contract and test the declared version.

## Documentation

- [M-FIRST-DOC-SENTENCE](https://microsoft.github.io/rust-guidelines/guidelines/docs/#M-FIRST-DOC-SENTENCE): Begin item documentation with a short summary, roughly 15 words or fewer.
  Separate the summary from details so rustdoc listings remain easy to scan.

- [M-MODULE-DOCS](https://microsoft.github.io/rust-guidelines/guidelines/docs/#M-MODULE-DOCS): Add `//!` documentation to public modules.
  Explain purpose, appropriate use, examples, interactions, guarantees, and relevant side effects.
  Include implementation details only when callers need them to use the abstraction correctly.

- [M-CANONICAL-DOCS](https://microsoft.github.io/rust-guidelines/guidelines/docs/#M-CANONICAL-DOCS): Use a summary and applicable `Examples`, `Errors`, `Panics`, `Safety`, and `Abort` sections.
  Explain parameter meaning in prose rather than a mechanical parameter table.
  A safety section does not excuse an unsound safe signature.

- [M-DOC-INLINE](https://microsoft.github.io/rust-guidelines/guidelines/docs/#M-DOC-INLINE): Use `#[doc(inline)]` for deliberate public re-exports of the crate's own items.
  Keep standard-library and third-party re-exports visibly external.
  This does not authorize wildcard re-exports or duplicate public paths.

## AI-assisted development

- [M-DESIGN-FOR-AI](https://microsoft.github.io/rust-guidelines/guidelines/ai/#M-DESIGN-FOR-AI): Use idiomatic APIs, clear contracts, useful examples, strong types, and testable dependencies.
  Provide behavior tests that make refactoring failures visible.
  Do not assume that generated code is correct merely because it follows familiar patterns.

- [M-SINGLE-ITEM-PATH](https://microsoft.github.io/rust-guidelines/guidelines/ai/#M-SINGLE-ITEM-PATH): Give each user-facing item one canonical public path.
  Re-exporting from a private implementation module is compatible with this rule.
  Preserve exceptions for hidden macro support and separately governed foreign re-exports.
  Removing an old public alias can still break callers and requires a migration decision.

- [M-NO-META-DESIGN-DOCUMENTATION](https://microsoft.github.io/rust-guidelines/guidelines/ai/#M-NO-META-DESIGN-DOCUMENTATION): Document the current user-facing contract, not an agent's design journey or compliance report.
  Keep review findings and decision history outside crate and module API documentation.
  Enduring design goals relevant to users remain appropriate.

- [M-TAUTOLOGICAL-TESTS](https://microsoft.github.io/rust-guidelines/guidelines/ai/#M-TAUTOLOGICAL-TESTS): Test meaningful behavior and independently specified properties rather than restating definitions.
  Avoid tests that reproduce the implementation's own logic as the expected answer.
  Do not add meaningless assertions solely to satisfy mutation-testing targets.

- [M-RUST-SHAPED](https://microsoft.github.io/rust-guidelines/guidelines/ai/#M-RUST-SHAPED): Preserve domain behavior when porting code, but redesign language-specific mechanisms for Rust.
  Reconsider ownership, error handling, task management, interface hierarchies, and global state.
  Do not translate object-oriented factories, exception patterns, or reflection assumptions mechanically.

## Validation

Use repository CI commands first and adapt execution to the affected package.
Replace `<crate>` with an actual package name before running these baseline commands:

```bash
cargo fmt --all -- --check
cargo check -p <crate> --all-targets
cargo test -p <crate>
cargo test -p <crate> --doc
cargo clippy -p <crate> --all-targets
cargo doc -p <crate> --no-deps
```

Expand the evidence according to the change:

- Test the MSRV, supported targets, default features, and supported no-default builds.
- Exercise additive feature combinations with cargo-hack when available and review exclusions explicitly.
- Run dependency audits and unused-dependency analysis with the project's configured tools.
- Run Miri for supported unsafe tests and disclose unsupported FFI or platform operations.
- Test public future `Send` guarantees, newtype boundaries, error causes, and redacted formatting where relevant.
- Test macro expansion behavior, downstream diagnostics, and supported companion versions when macros change.
- Benchmark hot paths with representative inputs and telemetry enabled before claiming an optimization.
- Test relevant cancellation, panic, and mock failure paths rather than only successful operations.

Use `--workspace` when the affected members share compatible test prerequisites.
Use `--all-features` for supported targets rather than assuming every platform-specific dependency can build everywhere.
If features conflict on a supported target, report the conflict against the additive-feature policy.
Do not add `-D warnings` unless the project requires it.
Do not install tools, change allocators, add dependencies, publish crates, or rewrite build policy merely to complete a checklist.

Record commands and outcomes, including missing tools and environmental failures.
Passing compiler checks, Clippy, tests, or Miri is evidence, not proof of soundness or full compatibility.
Report unmeasured performance expectations as hypotheses.

## Output contract

For reviews, lead with findings ordered by caller impact, not checklist order.
Do not assign an aggregate compliance score.
For each actionable finding, include these details:

- Location: File, line, and relevant symbol when available.
- Source: Linked `M-*` ID, with supplemental guidance labeled separately.
- Evidence: The actual interface, implementation, documentation, or failing use case.
- Impact: The correctness risk, repeated work, hidden dependency, or compatibility cost.
- Correction: The smallest useful change and its migration implications.
- Exception: Any justified departure, who bears its cost, and when to revisit it.

Separate guideline adherence from outcome.
Use `APPLIED`, `PARTIALLY_APPLIED`, `INTENTIONAL_EXCEPTION`, `VIOLATED`, `NOT_APPLICABLE`, or `UNKNOWN` when recording adherence.
Support each status with evidence except when the guideline does not apply.
Distinguish measured outcomes from expected improvements and missing information.

For designs, show representative call sites and materially different alternatives for consequential choices.
Explain what complexity is removed, what remains for callers, and what knowledge the abstraction hides.
State what later observation can disprove the expected benefit.
Keep this analysis in the review or decision record, not in user-facing API docs.

End with reviewed scope, intentional exceptions, validation results, and remaining uncertainty.
If no actionable findings remain, say so without claiming full compliance or proven safety.
