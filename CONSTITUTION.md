# The SELF Constitution

> Non-negotiable principles that constrain every design decision, every implementation, and every contribution to the SELF system.

This constitution is the highest-authority document in the SELF project. It binds every subsystem, every contributor, and every future evolution. Where this constitution conflicts with any other document, this constitution prevails.

Amendments to this document require a formal constitutional amendment process defined in `decisions/`. Routine design choices are recorded in ADRs; constitutional changes are recorded in amendments.

---

## Article I — User Ownership

The user owns every artifact SELF produces.

**Section 1.** All observation data, knowledge objects, identity graphs, persona vectors, summaries, and derived state are the property of the user, regardless of the underlying models, embeddings, or storage systems used to produce or hold them.

**Section 2.** The user has the right to:
- Read the entirety of their data in human-readable form.
- Export their data in a portable, documented format.
- Delete any subset of their data, with downstream effects propagating through the system predictably.
- Migrate their data to another system or implementation.
- Inspect any algorithm that has operated on their data.

**Section 3.** No subsystem may obscure, encrypt, or otherwise render user data inaccessible to the user. Encryption is permitted only for at-rest protection with keys held by the user.

**Section 4.** No contributor, organization, or third party may claim ownership of user data produced by SELF.

---

## Article II — Local-First Operation

SELF runs on the user's hardware.

**Section 1.** Every subsystem of SELF must function with no network connectivity unless the user has explicitly opted into a specific remote capability.

**Section 2.** Default configurations must be entirely local. Remote integrations (cloud models, hosted databases, third-party APIs) must be opt-in, documented, and reversible.

**Section 3.** The system must function with the user fully offline. Loss of internet must not result in data loss, corruption, or unrecoverable state.

**Section 4.** No subsystem may transmit user data off-device without explicit, granular, revocable consent. Consent must be specific to data type, destination, and purpose.

**Section 5.** Network use must be observable. The user must be able to see, log, and audit every outbound request the system makes.

---

## Article III — Auditability

Every state change is traceable.

**Section 1.** Every knowledge object produced by SELF must carry provenance: a reference to the observation(s) that produced it, the model(s) involved, the prompt(s) used, and the time of creation.

**Section 2.** Every mutation to the identity graph, persona vectors, memory, or any other persistent state must be recorded in an append-only audit log.

**Section 3.** The audit log itself must be inspectable by the user in human-readable form. It must not be deleted, modified, or pruned except through explicit, documented user action.

**Section 4.** Given a knowledge object, the user must be able to walk the provenance chain all the way back to the original observation events. Given an observation event, the user must be able to enumerate all derived knowledge.

**Section 5.** Every action the system takes on the user's behalf must be logged with input, output, authorization, and result. Actions without authorization may not occur.

---

## Article IV — Explainability

SELF must be able to justify its beliefs.

**Section 1.** When the system asserts a fact about the user (a belief, a project, a relationship, a prediction), it must be able to cite the supporting evidence: which observations, which extractions, which derivations led to that assertion.

**Section 2.** When the system takes an action, it must be able to explain the reasoning that produced the action in terms the user can understand.

**Section 3.** When the system cannot explain a belief or action, it must say so. The system must not present unjustified inferences as facts.

**Section 4.** Explanations must be available in the same surface as the assertion. A summary that says "you are working on X" must be expandable to show why.

**Section 5.** The system must distinguish between facts (directly observed), inferences (derived from observations), and speculations (extrapolations from inferences). This distinction must be visible in both the data model and the user interface.

---

## Article V — Provenance

Lineage is mandatory.

**Section 1.** Every knowledge object has a `provenance` field that records:
- Source observation event IDs.
- Source extraction IDs.
- Model identifier(s) and version(s).
- Prompt template identifier(s) and version(s).
- Timestamp.
- Confidence score (when applicable).

**Section 2.** Provenance is preserved through transformations. A summary derived from three beliefs must carry the IDs of those beliefs. A belief updated by new evidence must carry the history of its updates.

**Section 3.** Provenance is not a debugging convenience; it is a first-class data field with a schema (`schemas/`).

**Section 4.** Deleting a source observation must require explicit user action and must propagate to all derived objects. Silent cascading deletion is prohibited.

---

## Article VI — Model Independence

The system survives changes in models.

**Section 1.** No model — language, embedding, or otherwise — is a permanent dependency. Every model is accessed through an interface that can be replaced without rewriting callers.

**Section 2.** Knowledge objects must not embed raw model outputs as primary content. Model outputs are inputs to a structuring step. The structured form is the source of truth.

**Section 3.** When a model is swapped, the user must be notified, and any objects whose structure depends on the old model must be re-evaluated for consistency.

**Section 4.** The system must function with multiple model backends concurrently. Local and remote models may coexist.

**Section 5.** Benchmarking, evaluation, and prompt design must be model-class aware but model-instance agnostic. A change in model checkpoint must not require prompt rewrites.

---

## Article VII — Security

SELF protects the user from the system, the system from the user, and both from the outside.

**Section 1.** Defense in depth: security is enforced at multiple layers — the filesystem, the storage layer, the orchestration layer, the interface layer, and the user interface.

**Section 2.** Least privilege: every subsystem has only the permissions it requires. Permissions are explicit, configurable, and revocable.

**Section 3.** Sandboxing: code execution, model execution, and action execution must occur in environments that limit blast radius. A failure in the action engine must not compromise the memory layer.

**Section 4.** Cryptographic hygiene: all cryptographic primitives are well-known, audited, and used correctly. Custom cryptography is prohibited.

**Section 5.** Supply chain integrity: dependencies are pinned, versioned, and auditable. The system must be reproducible from a known dependency set.

**Section 6.** No telemetry without consent. SELF does not phone home. The user must be able to disable every form of outbound communication.

**Section 7.** Adversarial inputs are assumed. Prompts, web content, and email are untrusted. The system must not execute instructions embedded in observed data.

---

## Article VIII — Transparency

SELF is inspectable.

**Section 1.** The user can ask the system what it knows, what it is doing, and why. Answers are honest, complete, and in human-readable form.

**Section 2.** Configuration is plain text. There are no hidden settings, no encrypted configuration blobs, and no opaque binary state.

**Section 3.** The system's source code, schemas, prompts, and evaluation criteria are part of the system. They are not "implementation details" hidden from the user.

**Section 4.** When the system changes — through an update, a model swap, a configuration change — the user is informed.

**Section 5.** Bugs, limitations, and known failure modes are documented openly in the repository. They are not minimized or hidden in release notes.

---

## Article IX — Continuity

SELF is a long-running system.

**Section 1.** Data formats outlive code. A schema version must be readable by every future version of SELF. Deprecated schemas are supported for a documented deprecation period before removal.

**Section 2.** State is portable. The user can copy a SELF installation to a new machine and resume. Backups are first-class.

**Section 3.** Upgrades are non-destructive. Migrations preserve data. Rollbacks are supported where technically feasible.

**Section 4.** The system must be able to run unattended for extended periods. Failures are logged, retried, and surfaced to the user on the next interaction — never silently dropped.

**Section 5.** The system must degrade gracefully. Loss of a model backend, a vector store, or a remote integration must not crash the system; it must produce a documented degraded state.

---

## Article X — Consent and Autonomy

SELF acts only with permission.

**Section 1.** The system has no default authority to act on the user's behalf. Action capabilities are opt-in, scoped, and revocable.

**Section 2.** Consent is granular. The user may authorize the system to read email but not to send it. The user may authorize local actions but not remote ones. The user may authorize the system to act during work hours but not at night.

**Section 3.** Sensitive actions — anything destructive, external, or hard to reverse — require explicit per-action confirmation or an active, scoped session of authorization.

**Section 4.** The system must clearly distinguish between suggestions (presented to the user) and actions (taken on the user's behalf). The user must never be confused about which is occurring.

**Section 5.** Revocation of consent is immediate. The user can revoke any authorization at any time, and the system must stop using that authorization on the next action attempt.

---

## Amendment Process

Amendments to this constitution require:

1. A written proposal in `decisions/` with the prefix `AMENDMENT-`.
2. A clear articulation of the principle being added, modified, or removed.
3. A discussion period documented in the proposal.
4. Acceptance by the project's governance process (to be defined; in the meantime, by unanimous agreement of the active maintainers).
5. A version bump of the constitution itself.

Routine architectural choices are recorded in ADRs, not in constitutional amendments. The constitution is for principles, not preferences.
