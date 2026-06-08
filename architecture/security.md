# Security Subsystem

> The Security subsystem enforces the constitutional principles of user ownership, auditability, consent, and protection. It owns the permission system, the threat model, and the security audit process.

---

## Purpose

Security is not a feature of SELF; it is a constitutional requirement. The Security subsystem is the implementation of that requirement. It enforces:

- The user is the only authority over their data and the system's actions.
- Every state change is auditable.
- Every action is authorized.
- The system is hardened against external attack.
- The system is hardened against user mistakes.
- The system is hardened against supply chain attack.

The Security subsystem is also responsible for documenting the threat model, the privacy model, and the data governance. See `security/`.

## Responsibilities

- Enforcing the permission system.
- Enforcing the consent system.
- Authenticating the user.
- Authenticating subsystems to each other.
- Implementing sandboxing for untrusted code and untrusted models.
- Detecting and responding to anomalies.
- Auditing every privileged operation.
- Maintaining the cryptographic key store.
- Owning the secret management subsystem.
- Documenting the threat model.
- Performing security reviews.
- Responding to security incidents.

## Inputs

- Configuration: policies, permissions, secrets references.
- User actions (login, permission grant, secret rotation).
- Subsystem operations requiring permission checks.
- Anomaly signals from other subsystems.
- The audit log (read for security review).

## Outputs

- Permission grants and revocations.
- Authentication tokens.
- Sandbox environments.
- Anomaly alerts.
- Security reports.
- Metrics: permission grants, denials, anomalies, secret rotations.

## Dependencies

| Dependency | Type | Purpose |
| --- | --- | --- |
| Storage | Required | Audit log, key store. |
| Orchestration | Required | Invoked for security events. |
| All other subsystems | Required | Subject to security enforcement. |

## Trust Boundaries

SELF has the following trust boundaries. Each boundary is enforced:

- **User to system.** The user authenticates. Subsystems do not act on the user's behalf without authorization.
- **Subsystem to subsystem.** Subsystems authenticate to each other. No subsystem has implicit authority over another.
- **System to external.** All external network calls are mediated by the Security subsystem. No subsystem may make an external call directly.
- **System to storage.** Storage is accessed through the Storage API. Direct database access is prohibited.
- **System to model.** Models are accessed through the model adapter. The adapter enforces prompt hygiene and output validation.
- **System to code.** Code execution occurs in sandboxes. The host is not trusted to run arbitrary code.

## Internal Components

### Authentication Manager

Authenticates the user. The manager:

- Supports password, key file, hardware token, and other factors.
- Supports multi-factor authentication.
- Enforces session timeouts.
- Logs all authentication events.
- Supports re-authentication for sensitive actions.

### Authorization Engine

Decides whether an action is allowed. The engine:

- Evaluates permission rules.
- Evaluates consent grants.
- Evaluates default-deny policies.
- Returns yes / no / require-confirmation.
- Logs every decision.

### Permission Store

Stores permission rules. The store:

- Is append-only at the storage layer; revocations are new records.
- Supports per-action, per-session, per-time-window rules.
- Supports time-bound and capability-scoped grants.
- Is user-editable.
- Records every change in the audit log.

### Secret Manager

Manages secrets. The manager:

- Stores secrets encrypted at rest with user-held keys.
- Provides secrets to subsystems on a need-to-know basis.
- Supports secret rotation.
- Logs every access.
- Never logs secret values.

### Sandbox Manager

Manages sandboxes for untrusted execution. The manager:

- Provides isolated environments for code, models, and actions.
- Enforces resource limits.
- Enforces network restrictions.
- Monitors for escape attempts.
- Captures all activity for audit.

### Cryptographic Provider

Provides cryptographic operations. The provider:

- Uses well-known, audited libraries (OpenSSL, libsodium, etc.).
- Provides symmetric and asymmetric primitives.
- Provides secure random number generation.
- Provides key derivation.
- Is itself unit-tested against known vectors.

### Anomaly Detector

Detects anomalies. The detector:

- Monitors system behavior for unusual patterns.
- Monitors user behavior for unusual patterns.
- Monitors external requests for unusual patterns.
- Triggers alerts and protective actions.
- Logs detections.

### Audit Query Engine

Supports queries against the audit log for security review. The engine:

- Supports queries by actor, action, time, entity.
- Supports aggregation queries.
- Supports anomaly queries.
- Supports export for external analysis.

### Incident Responder

Handles security incidents. The responder:

- Receives alerts from the anomaly detector and other sources.
- Implements predefined response playbooks.
- Logs every response action.
- Supports manual override.
- Notifies the user.

## Permission Model

SELF uses a capability-based permission model with consent overlays.

### Capabilities

A capability is a named, scoped action the user can authorize. Examples:

- `read.filesystem` — read files in declared paths.
- `write.filesystem` — write files in declared paths.
- `execute.command` — run commands in declared paths.
- `network.read` — make HTTP GET requests.
- `network.write` — make HTTP POST/PUT requests.
- `email.read` — read email.
- `email.send` — send email.
- `github.read` — read GitHub data.
- `github.write` — modify GitHub data.
- `model.invoke` — invoke language models.

Each capability has a default sensitivity (low, medium, high) that determines whether confirmation is required.

### Consent

Consent is a specific grant of a capability under specific conditions:

- Time-bound: "allow this for the next hour."
- Session-bound: "allow this within the current session."
- Use-bound: "allow only for files matching pattern X."

The user can revoke consent at any time. Revocation is immediate.

### Default Deny

By default, no capability is granted. The system acts with the minimum necessary capabilities and asks before exceeding them.

## Data Contracts

The Security subsystem produces:

- `permission_grant` records.
- `permission_revocation` records.
- `authentication_event` records.
- `anomaly_alert` records.
- `sandbox_creation` records.
- `secret_access` records.

These are all stored in the audit log.

## Failure Modes

| Failure | Detection | Response |
| --- | --- | --- |
| Authentication failure | Auth manager | Lockout, log, alert. |
| Authorization denied | Authz engine | Refuse, log. |
| Sandbox escape | Monitor | Kill, alert, quarantine. |
| Secret exposure | Detector | Rotate, alert. |
| Anomaly detected | Detector | Trigger response playbook. |
| Audit log corruption | Integrity check | Halt, alert. |
| Key compromise | Detector | Rotate, alert. |

## Metrics

- `security.authentications.total` (by outcome)
- `security.authorizations.total` (by capability, by decision)
- `security.anomalies_detected.total` (by type)
- `security.sandboxes_created.total`
- `security.secret_rotations.total`
- `security.incidents.total` (by severity)

## Future Evolution

- **Hardware-backed keys.** Support for TPM, Secure Enclave, and hardware security keys.
- **Multi-party authorization.** Require multiple parties (e.g., the user and a trusted contact) for sensitive actions.
- **Zero-knowledge proofs.** Prove properties of state without revealing the state.
- **Federated identity.** Integrate with external identity providers (with consent).

## Edge Cases

- **User forgets password.** Recovery via pre-configured methods. No backdoor.
- **User is unavailable.** The system operates on the last known authorization. Sensitive actions are blocked.
- **Compromised host.** If the host is compromised, the encrypted secrets remain protected. Audit log integrity is verifiable.
- **Compromised model output.** Model outputs are treated as untrusted. They are validated, never executed directly.
- **Insider threat.** Even an authorized subsystem cannot exceed its declared capabilities.

## Acceptance Criteria for "Security is Complete"

1. All capabilities require explicit grants.
2. Sensitive capabilities require confirmation.
3. All authentication events are logged.
4. All sandbox creations are logged.
5. All secret accesses are logged (without values).
6. Anomaly detection catches known attack patterns.
7. The threat model is documented and reviewed.
8. Security review is part of the definition of completion.
