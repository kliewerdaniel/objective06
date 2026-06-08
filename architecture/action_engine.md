# Action Engine Subsystem

> The Action Engine is the only subsystem that produces side effects in the external world. It executes authorized actions on the user's behalf through Objective05-style layers, with full audit, consent, and explainability.

---

## Purpose

The Action Engine is SELF's effector. While every other subsystem observes, models, or reasons, the Action Engine is the only one that does things: it sends emails, creates files, opens browser tabs, runs commands, posts messages, modifies calendars, and interacts with external systems.

Actions are the highest-risk capability of SELF. A mistaken observation is recoverable. A mistaken action can send a wrong email, delete a wrong file, or post a wrong message. The Action Engine is designed with this in mind. Every action is authorized, scoped, logged, reversible where possible, and explainable.

The Action Engine is built on Objective05-style execution layers. Objective05 is the pattern of composing actions from declarative specifications with explicit preconditions, postconditions, and rollback plans. See `interfaces/objective05.md`.

## Responsibilities

- Receiving action proposals (from the Digital Twin) or direct action requests (from the user).
- Validating action requests against the permission system.
- Resolving action requests into Objective05-style execution plans.
- Executing plans in a sandboxed environment.
- Capturing preconditions, postconditions, and rollback plans.
- Logging every action with full provenance and authorization.
- Emitting action results as new observation events (closing the loop).
- Supporting dry-run mode.
- Supporting action cancellation and rollback.

## Inputs

- `action_request` records (from the Twin or directly from the user).
- The user's permission grants.
- The current state of the identity graph and memory (for context).
- The current Objective05 capability registry.
- The configured execution environments (sandbox, network, tools).

## Outputs

- `action_result` records.
- Side effects in the external world.
- New `observation_event` records (the result becomes an event).
- `action_audit` records (full execution trace).
- Metrics: action count, success rate, rollback rate, latency.

## Dependencies

| Dependency | Type | Purpose |
| --- | --- | --- |
| Memory | Required | Persistence of action records. |
| Identity Graph | Required | Context (who, what, where). |
| Security | Required | Permission checks, sandboxing. |
| Objective05 Runtime | Required | Plan execution. |
| Local Models | Optional | Plan synthesis. |
| Orchestration | Required | Scheduling, retries. |

## Internal Components

### Action Intake

Receives action requests. The intake:

- Validates the request against the schema.
- Looks up the user and the session.
- Resolves the request to a capability.
- Logs the intake.

### Permission Resolver

Determines whether the action is permitted. The permission resolver:

- Checks explicit grants.
- Checks session-scoped grants.
- Checks default-deny rules.
- Honors revocations.
- Returns a yes / no / require-confirmation decision with reasons.

### Plan Synthesizer

Synthesizes an Objective05 execution plan from the action request. The synthesizer:

- Looks up the capability definition.
- Resolves parameters against the current state.
- Generates preconditions (what must be true before execution).
- Generates postconditions (what will be true after execution).
- Generates a rollback plan.
- Validates the plan against policies.
- Asks for confirmation if the action is sensitive.

### Capability Registry

The authoritative list of capabilities SELF can perform. Each capability has:

- A unique identifier.
- A human-readable description.
- Required permissions.
- Default sensitivity level.
- An Objective05 specification.
- Test cases.

Capabilities are versioned. New capabilities are added through the standard contribution process.

### Sandbox Manager

Executes plans in a sandboxed environment. The sandbox manager:

- Isolates execution from the host system.
- Limits network access to declared endpoints.
- Limits filesystem access to declared paths.
- Limits subprocess spawning.
- Logs all system calls and network calls.
- Enforces timeouts and resource budgets.

### Executor

Runs the Objective05 plan. The executor:

- Evaluates preconditions; aborts if any fail.
- Executes steps in order.
- Captures outputs and side effects.
- Evaluates postconditions.
- Triggers rollback if postconditions fail.
- Streams progress to the audit log.

### Rollback Engine

Reverts side effects when postconditions fail or the user cancels. The rollback engine:

- Executes the rollback plan in reverse.
- Verifies rollback success.
- Logs rollback attempts.
- Supports best-effort and strict rollback modes.

### Confirmation Manager

Handles user confirmation for sensitive actions. The confirmation manager:

- Presents the action plan to the user.
- Highlights sensitive aspects.
- Records the user's response.
- Supports "always allow" within a session for low-risk patterns.
- Supports "always deny" as a permanent rule.

### Result Emitter

Emits `action_result` records and produces new `observation_event` records from the result. The result emitter:

- Captures outputs.
- Computes diffs (what changed in the world).
- Produces a structured event.
- Triggers downstream observers.

## Data Contracts

The Action Engine consumes:

- `schemas/action_request.md`

The Action Engine produces:

- `schemas/action_result.md`
- `action_audit` records
- `observation_event` records (from results)

## Action Lifecycle

```
Proposal (from Twin or user)
   ↓
Intake
   ↓
Permission Check
   ↓
   ├── Denied: refuse, log, return to caller
   └── Allowed: continue
   ↓
Plan Synthesis
   ↓
   ├── Requires confirmation: Confirmation Manager
   │     ├── Confirmed: continue
   │     └── Declined: cancel, log
   └── Does not require: continue
   ↓
Execution
   ↓
   ├── Success: emit result, emit observation
   └── Failure: rollback, emit result with failure
```

## Action Categories

Actions are categorized by sensitivity:

- **Read-only local.** Read a file, list a directory. Generally safe.
- **Write local.** Create a file, modify a file. Requires confirmation by default.
- **Execute local.** Run a command. Requires explicit confirmation.
- **Network read.** HTTP GET, RSS poll. Generally safe.
- **Network write.** HTTP POST, send email. Requires explicit confirmation.
- **External system.** Anything that touches a third-party API. Requires explicit confirmation and may be sandboxed.

## Failure Modes

| Failure | Detection | Response |
| --- | --- | --- |
| Permission denied | Permission check | Refuse, log, return reason. |
| Precondition failed | Precondition evaluation | Abort, log, return reason. |
| Sandbox escape attempt | Monitor | Kill execution, alert. |
| Postcondition failed | Postcondition evaluation | Rollback, alert. |
| Network failure | Network error | Retry with backoff, then fail. |
| Timeout | Watchdog | Kill execution, log, return reason. |
| User cancellation | Confirmation timeout | Abort, log, return reason. |
| Rollback failure | Rollback verification | Alert, log, retain for manual cleanup. |

## Metrics

- `action.requests.total` (by category)
- `action.executed.total` (by capability, by outcome)
- `action.denied.total` (by reason)
- `action.rollback_rate`
- `action.execution_latency_ms`
- `action.sensitive_confirmations.total`
- `action.capability_count`

## Future Evolution

- **Multi-step plans.** Plans that span minutes, hours, or days.
- **Scheduled actions.** "Send this email at 9am tomorrow."
- **Triggered actions.** "Whenever X happens, do Y."
- **Learned policies.** The system learns which actions the user is comfortable with.
- **Action marketplace.** Third-party capabilities (with security review).

## Edge Cases

- **Idempotent actions.** Some actions are naturally idempotent (set a variable). Some are not (send an email). The Action Engine must handle both.
- **Long-running actions.** Some actions take minutes or hours. The engine must stream progress and support cancellation.
- **Cascading actions.** An action may trigger another action. The engine must detect and limit cascades.
- **Conflicting concurrent actions.** Two actions may conflict. The engine must serialize or refuse.
- **Out-of-band user intervention.** The user may do something between the action being proposed and being executed. The engine must re-validate.
- **Sensitive data in actions.** Emails may contain PII. The engine must apply the same privacy rules as observations.

## Acceptance Criteria for "Action Engine is Complete"

1. At least three capabilities are implemented and tested.
2. Permission denials are honored.
3. Sensitive actions require confirmation.
4. Rollback works for at least one capability.
5. Every action is logged with full audit trail.
6. The Action Engine survives a sandbox crash without compromising the host.
7. Evaluation: `evaluations/predict_next_task.md` (as it relates to action authorization) passes.
