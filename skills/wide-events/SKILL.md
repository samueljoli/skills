---
name: wide-events
description: "Design, implement, or review wide-event observability: one rich, queryable event per unit of work (request, job, message, workflow). Use when adding OpenTelemetry spans, structured logging, or debugging attributes, reviewing a diff for observability gaps, or evaluating a telemetry architecture."
---

# Wide Events

For every meaningful unit of work, maintain one primary **wide event**: a structured record that accumulates everything learned while the work ran, emitted once at the end, into a columnar store that can filter and GROUP BY any field. This is the canonical-log-line pattern (Stripe, 2016; Morrell's *Practitioner's Guide to Wide Events*, 2024), with corrections for cost, privacy, sampling, and governance.

The wide event is a **materialized analytical summary** of the unit of work. It is the primary index for asking unforeseen questions. It is not the sole forensic record, not a replacement for traces where causality matters, and not a replacement for metrics where alerting matters.

The target: an engineer moves from "something is wrong" to "it happens only for enterprise tenants on build 2.17 in us-east-1 with `feature_flag.checkout_v2` on, and affected requests make 4x the normal database calls" without deploying new instrumentation.

## Modes

Infer the mode from the request; do not default to one.

- **Design mode**: the user is choosing or evaluating an observability architecture. Run the three gates, then the break-tests in *Adversarial review*.
- **Implementation mode**: the user is writing or changing code. Instrumentation is part of the feature. At each point where the code learns a fact an investigator would want, add it to the primary event at that layer.
- **Review mode**: the user is reviewing a diff or preparing a commit. Follow *Review procedure* and emit findings in the *Review output* format. Never say "add more logging."

## Three gates (design mode; check quickly in the other modes)

Stop and tell the user if one fails. Wide events are not free.

1. **Backend (hard gate).** The destination must be a columnar/OLAP store that prices per event or per row and does not penalize cardinality: Honeycomb, ClickHouse-backed tools (SigNoz, HyperDX), Datadog logs, New Relic, DuckDB/Parquet on object storage. If it is Elasticsearch, CloudWatch, Loki, or Splunk on a per-GB or per-indexed-field plan, wide rows cost money and yield little. Recommend a lean structured access log or a backend change before instrumenting width. Evaluate cost end to end (instrumentation, transport, collector, redaction, ingest pricing, query compute, retention), as cost per useful debugging capability, never as cost per stored byte.
2. **Unit of work.** Define the event boundary explicitly: HTTP request, RPC, job run, consumed message, scheduled task, workflow execution, command. It must be large enough to be a meaningful operation and small enough to be analytically comparable. For websockets, streaming, GraphQL, fan-out consumers, or sagas, choose the unit (per message, per resolver batch, per stage) before writing code, and never let the primary event outlive the work it wraps.
3. **Privacy.** Wide events are powerful because they correlate many dimensions, which makes them a sensitive dataset. Agree an allowlist schema and a deny-list before the first event ships. Never capture raw `url.query`, `Authorization` or `Cookie` headers, request or response bodies, passwords, tokens, payment data, health data, or email addresses as identifiers. Use opaque or hashed IDs. Redact before telemetry leaves the trust boundary. Test: would you give broad engineering access to every value in this field?

## Emission pattern

With OpenTelemetry, the wide event is the root server/consumer span; enrich it. Without OTel, keep a request-scoped dictionary and log it once as structured JSON when the work completes. Never emit mid-operation.

Keep a stable handle to the primary event so enrichment deep inside the handler lands on it, not on whichever child span is active. In OTel, store the root span in the context under a private key in middleware and expose `setMainAttributes(...)`; in other stacks use a request-local, contextvar, or context value. Mark the event `main = true` so every query can begin `WHERE main = true`, or use the repository's existing marker. Do not introduce a competing convention.

```js
// Node / OTel sketch; same shape in any language.
const MAIN = createContextKey("main_span");
function mainSpanMiddleware(req, res, next) {
  const span = trace.getActiveSpan();
  span.setAttribute("main", true);
  context.with(context.active().setValue(MAIN, span), next);
}
function setMainAttributes(attrs) {
  context.active().getValue(MAIN)?.setAttributes(attrs);
}
```

Put stable producer metadata (service name, version, host, container, k8s workload, cloud region, runtime) on **OTel Resource attributes**, not on every span. The backend flattens both into one query surface; the instrumentation layer should not duplicate them.

Respect SDK limits. OTel SDKs default to about 128 attributes per span; the limit is configurable. Inventory intended attributes, raise the limit deliberately if needed, and monitor dropped-attribute counts. Do not design a 300-field event and assume it is transmitted.

## Start from questions, then choose dimensions

Before adding fields, list the questions an investigator will ask: did this start after a deploy; is it one tenant or tier; does a flag correlate; is latency tied to dependency call count; is it one region or client version; are slow requests large; which dependency is implicated. Every useful question names dimensions that must coexist on the same record. Prefer dimensions over messages: `cache.user_profile.hit = false`, not "Cache missed."

### Canonical spine (~20 fields, do first)

Auto-instrumentation supplies HTTP, host, and container fields; do not hand-write those. Spend effort on what no SDK can know, in this order of value.

**Actor and business context (highest value, always bespoke):** `user.id` (opaque), `user.type` (free/pro/enterprise), `tenant.id` (org or account), `auth.method`, `user.assumed` and `user.assumed_by` for impersonation, `user.age_days`.

**Deployment:** `service.version` (git SHA; on Resource), `deployment.id`, `deployment.age_minutes`, `deployment.trigger`, plus a PR or diff URL when CI exposes it.

**Outcome:** `error` (bool), `exception.type`, `exception.message`, `exception.expected` (bool), `exception.slug`. Stack traces only where sampling keeps the event anyway; they dominate width. Also the positive outcome: `result = "created"`, `items_processed = 137`.

**Operation:** `http.route` (the template, never the raw path), the one or two path params that identify the tenant or resource, `request.id`, or `job.id` / `messaging.message_id` and `messaging.redelivered` for non-HTTP units.

**Sampling:** `sample_rate` on every event, always, even while it is 1.

**Domain (one to five per service):** what the service exists to do: `document.format`, `payment.provider`, `vcs_integration.vendor`, `queue.depth_at_start`. If a vendor failing would only be visible through one of these, add it.

### Second tier (add when a question demands it)

**Decisions:** every meaningful branch: `feature_flag.<name>`, `cache.<name>.hit`, `retry.count`, `fallback.used`, `rate_limit.allowed`, `storage.backend`, `parser.strategy`. Production bugs usually live on one branch. Record flag states on the primary event even though the OTel convention puts them on span events; they are what you group by. Capture only flags that materially affect behavior.

**Dependency rollups (small automatic set):** per dependency class, count and total duration, derived by instrumentation and named `stats.<dep>.count` / `stats.<dep>.duration_ms`. Plus a handful of named phase timings that explain latency: `auth.duration_ms`, `db.duration_ms`, `external_api.duration_ms`, `queue_wait.duration_ms`. Document them as derived; child spans remain the source of truth for order and causality. Do not turn every function into a timing attribute.

**Environment shape:** `uptime_sec` and `uptime_sec_log10` (cold-start and leak shapes on a heatmap), `ratelimit.remaining`, runtime and framework versions during upgrades, localization fields for i18n-heavy products.

### Field policy (split by risk)

**Default include** a field that is bounded (an enum, a boolean, a number, an opaque ID), non-sensitive, and explainable in one line. The marginal cost is small and the investigative value is real.

**Require justification** before adding a field that is free text or unbounded, identity-bearing or otherwise sensitive, producer-level (belongs on Resource), or that pushes the attribute limit. Answer all eight:

1. What question will this help answer?
2. Is it operation-specific or resource-specific?
3. What is its expected cardinality?
4. Could it contain sensitive information?
5. Is there a bounded, normalized representation?
6. Does it belong on the primary event, a child span, a log, a metric, or Resource?
7. Will sampling destroy the scenario where it is most useful?
8. Will it survive the SDK and backend limits?

No compelling answer to question 1 means no field.

### Width versus cardinality

Many fields is manageable. Unbounded values are the risk. Opaque IDs (user, tenant, trace, transaction, document) are high-cardinality and valuable; modern backends handle them, so do not discard them out of fear. Templated routes over raw paths, `error.category = "database_timeout"` over thousands of unique messages, normalized enums over free strings.

## Error slugs

At each site that raises an unrecoverable error, attach a static string literal, never a variable or formatted string:

```js
setErrorAttributes(err, "err-stripe-charge-retries-exhausted");
```

`WHERE error = true AND exception.slug IS NULL` then lists exactly the code paths whose error handling still needs work. A failed operation without a slug is an observability gap. Prefer a small set of stable slugs per failure site over dynamic ones like `"failed-user-" + id`.

## Naming and governance

Dotted snake_case namespaces, outer to inner: `tenant.id`, `stats.postgres.duration_ms`, `feature_flag.checkout_v2`. Durations carry a unit suffix. Follow OTel semantic conventions where one exists; stop worrying where none does; match the repository's existing conventions over both. Shipping slightly imperfect telemetry now beats perfectly named telemetry that never ships.

One owner per service maintains a lightweight schema: field name, meaning, type, allowed values, cardinality expectation, privacy class, retention. Never let two fields mean one thing (`customer_id` / `account_id` / `tenant_id`). Without ownership, "just add the thing" produces an unqueryable swamp within a year.

## Sampling as a retention policy

Uniform head sampling estimates common behavior and destroys rare events: at 1-in-1000, a once-in-a-million failure has a 0.1% chance of surviving. Because the wide event is complete at the end of the unit of work, the keep/drop decision can be made per event with full knowledge of the outcome, which is cheap even where distributed tail sampling is not. Default:

- Keep 100% of `error = true`, duration above the route's p99, top-tier `user.type`, and anything anomalous.
- Keep health checks and other high-volume boring 2xx routes at 1-in-N.
- Everything else at 1-in-M, set by budget.
- Record the applied rate in `sample_rate` so the backend re-weights counts.

Keep child-span sampling consistent with the parent (OTel parent-based sampler) or accept orphaned traces. If volume grows, prefer wider events at a lower keep rate over narrow events at a higher one.

## What the wide event does not replace

**Traces** answer "what exactly happened, in what causal order": ordering, parent/child, fan-out, retries, critical path. Summaries on the wide event are not equivalent to the trace. Keep child spans for meaningful phases; do not create one per function.

**Metrics** answer "how is the system doing over time, cheaply": SLOs, alerting, rates, saturation. Keep a small metric set for alerting; expect to need far fewer than before.

**Crash evidence.** A process that dies by OOM, SIGKILL, node loss, or collector failure never exports its final enriched event. Keep enough independent signal (child spans, discrete structured logs, crash reports, lifecycle events, infra metrics) to diagnose the case where the wide event is missing.

## Anti-patterns

- Log narration ("starting request", "calling database") where a dimension on the primary event says it better.
- Telemetry only at infrastructure boundaries. CPU and status code are not enough; capture domain context.
- Capturing `url.query`, raw headers, or bodies. Extract the one or two named values that matter.
- Attaching periodically sampled system metrics (`metrics.cpu_load`) to every event and alerting on them. Busy instances emit more events and over-represent themselves. Debugging aid only, labeled as such.
- Hand-maintained rollups that can disagree with the trace. Rollups are instrumentation-derived or absent.
- Fields nobody can explain, dynamic field names, dynamic error slugs, competing naming conventions.
- Coupling the domain model to a telemetry vendor when the codebase has an instrumentation abstraction.

## Review procedure (review mode)

1. **Understand the behavior**: what is new or changed, which paths were added, which external systems participate, which outcomes are possible.
2. **Find the primary event**: does the operation have a designated wide event? If not and it is significant, recommend one.
3. **Find new dimensions**: domain concepts, branches, flags, configuration, dependencies, cache and retry behavior, tenant classifications, identifiers, result types. Apply the field policy to each.
4. **Inspect failure paths**: will a failed execution say what failed, can failures be grouped, can the site be located, are expected and unexpected errors distinguishable?
5. **Inspect performance paths**: can a slow request be attributed to this phase? If not, a phase duration or child span.
6. **Inspect rollout behavior**: if behavior depends on a flag, config, version, experiment, or migration state, is the effective state observable?
7. **Queryability test**: imagine the change regresses in production and write the `WHERE ... GROUP BY ...` that would isolate it. Missing dimensions are findings.

### Review output

```text
OBSERVABILITY GAP

Location:
<file / function / behavior>

Missing context:
<attribute or instrumentation>

Why it matters:
<production question that cannot currently be answered>

Suggested attributes:
- ...

Example investigation:
WHERE ...
GROUP BY ...
```

## Adversarial review (design mode)

A design should survive all nine:

- **Rare-event**: a one-in-a-million failure is retained.
- **Crash**: if the process dies mid-request, evidence survives.
- **Privacy**: an internal or external leak of this dataset exposes nothing you could not defend.
- **Cardinality**: no dimension grows without bound.
- **Attribute-limit**: the SDK and backend accept the field count actually produced.
- **Causality**: what flattening the trace loses is known and acceptable.
- **Cost**: the whole pipeline is priced, not storage alone.
- **Governance**: someone owns naming, privacy, and lifecycle per field.
- **Queryability**: an engineer can test an unforeseen hypothesis without redeploying.

## Definition of done

A change is observability-complete when an investigator can answer from telemetry alone: what operation ran, on which version, affecting whom, which path was chosen and why, which dependencies participated and how long the important phases took, what the outcome was, what kind of failure it was and whether failures group, whether it correlates with a deploy or rollout, and whether unusual subsets can be isolated by filtering and grouping.

## Verify after deploying

Run and show the user, adapting syntax to the backend:

1. `COUNT WHERE main = true GROUP BY service.version` (new build emitting; stale instances visible)
2. `COUNT WHERE main = true AND user.id IS NULL GROUP BY http.route` (unauthenticated or mis-instrumented paths)
3. `COUNT WHERE error = true AND exception.slug IS NULL GROUP BY http.route` (unhandled error sites)
4. `HEATMAP(duration_ms) WHERE main = true GROUP BY user.type` (tiers populated, distributions plausible)

When changing code later, change the telemetry with it so the effect of the release is visible in the same query the next day.

## Guiding question

If this behaves strangely in production six months from now, what context would I wish I had captured today? Capture that on the wide event, within the gates above.
