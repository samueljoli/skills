# Example: Application Design — User Registration

## Problem

Registration currently requires the HTTP handler to validate input, start a transaction, insert a user, insert default preferences, append an outbox event, commit, and translate database failures.

## Complexity Map

The handler owns too much sequencing and infrastructure knowledge. Any persistence or event-delivery change amplifies into the HTTP layer.

## Alternative A — Handler Choreography

Keep each repository operation explicit and let the handler coordinate them.

## Alternative B — Application Operation

```text
RegisterUser.execute(command) -> result
```

The application operation owns the use-case transaction and coordinates domain/persistence behavior. Repositories own storage representation. The outbox implementation owns durable event recording.

## Information Ownership

| Information | Owner |
|---|---|
| Registration policy | domain/application boundary |
| SQL schema | repository |
| transaction coordination for the use case | application operation |
| outbox schema + serialization | messaging infrastructure |
| HTTP status mapping | HTTP adapter |

## Expected Outcomes

- Replacing HTTP with another transport should not change registration behavior.
- Changing the users table should not change the application operation.
- Changing the event broker should not change the registration use case.

The retrospective should later verify those claims rather than assuming them.
