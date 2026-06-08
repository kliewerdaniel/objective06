# BUILDING SELF

> The implementation workflow, contribution standards, and coding-agent protocol for the SELF project.

This document governs how SELF is built. It is the second-highest authority document after `CONSTITUTION.md`. Where this document conflicts with the constitution, the constitution prevails.

---

## 1. Documentation-First Philosophy

SELF is built documentation-first. This is not a stylistic preference; it is a structural commitment.

### 1.1 Why Documentation Comes First

- **A system you cannot describe cannot be built.** If you cannot write down what a subsystem does, you do not yet know what it does.
- **Documentation is the contract.** When the implementation changes, the documentation must change first. When the documentation changes, the implementation must be updated to match.
- **Documentation enables delegation.** A new contributor, human or agent, can read the documentation and begin work without sitting through a meeting.
- **Documentation outlasts code.** The schemas, architecture documents, and ADRs will be readable long after the current code is rewritten.

### 1.2 The Documentation Gate

A subsystem may not be implemented until:

1. Its architecture document exists in `architecture/`.
2. Its data contracts exist in `schemas/`.
3. Its evaluation criteria exist in `evaluations/`.
4. Its dependencies on other subsystems are documented.
5. At least one example of its end-to-end behavior exists in `examples/`.

A subsystem is not "complete" until:

1. The implementation exists.
2. The implementation passes the evaluations.
3. Any deviations from the architecture document are recorded in an ADR.
4. The example has been updated to reflect reality.

---

## 2. Implementation Workflow

The workflow is a loop. It is intentionally simple.

### 2.1 The Loop

```
Read the spec
   ↓
Read the relevant architecture document
   ↓
Read the relevant schema
   ↓
Read the relevant evaluation
   ↓
Read the relevant example
   ↓
Implement the smallest unit that can be evaluated
   ↓
Run the evaluation
   ↓
Fix what fails
   ↓
Update the documentation to match reality
   ↓
Commit
   ↓
Repeat
```

### 2.2 The Phases

The roadmap defines ten phases. Each phase has:

- **Objectives** — what the phase is meant to achieve.
- **Deliverables** — what must exist at the end of the phase.
- **Dependencies** — what must be true to start the phase.
- **Risks** — what could go wrong.
- **Milestones** — checkpoints within the phase.
- **Acceptance criteria** — the conditions under which the phase is considered done.

A phase is not "done" until all of its acceptance criteria are met and its deliverables exist in the repository.

### 2.3 Working in a Phase

Within a phase, contributors work on issues. Each issue is:

- Scoped to a single subsystem or cross-cutting concern.
- Tied to one or more evaluation criteria.
- Documented with its design rationale.

When an issue requires an architectural change, an ADR is opened **before** the code is written. ADRs are cheap; rewrites are expensive.

---

## 3. Development Process

### 3.1 Version Control

- The repository uses Git.
- The default branch is `main`.
- Feature work happens in branches named `phase-XX/short-description`.
- Pull requests are reviewed before merge.
- Commit messages follow the Conventional Commits style:
  - `feat(observer): add filesystem watcher for markdown directories`
  - `fix(memory): correct retention calculation for archived events`
  - `docs(spec): clarify provenance requirements for summaries`
  - `chore(deps): bump duckdb to 1.1.3`
  - `refactor(extraction): split entity extraction into separate prompt`

### 3.2 Branching Strategy

- `main` is always deployable.
- Feature branches are short-lived.
- Releases are tagged semantically: `v0.1.0`, `v0.2.0`, `v1.0.0`.
- Long-running experimental work happens in branches prefixed `experiment/`.

### 3.3 Code Style

- **Language.** Python is the primary implementation language. Other languages may be used where they are uniquely suited (Rust for performance-critical paths, TypeScript for browser-related code), but every language choice requires an ADR.
- **Formatting.** Black for Python, prettier for TypeScript, rustfmt for Rust. Configuration files are committed.
- **Linting.** Ruff or flake8 for Python, eslint for TypeScript, clippy for Rust. Lint errors block merge.
- **Type checking.** mypy in strict mode for Python. Type hints are mandatory for all new code.
- **Naming.** Descriptive names. `extract_belief_from_event` not `process`. No abbreviations in public APIs.

### 3.4 Testing

- **Unit tests** cover individual functions and classes.
- **Integration tests** cover interactions between subsystems.
- **Evaluation tests** are defined in `evaluations/` and are the primary measure of correctness.
- **Property-based tests** are used where appropriate (e.g., for schema validators).
- **Snapshot tests** are used for synthesis outputs to detect unintended changes.
- **Tests must be deterministic.** Time, randomness, and external state must be controlled.

### 3.5 Documentation Standards

- Every public function, class, and module has a docstring.
- Every non-obvious decision has a comment explaining why.
- Every schema is versioned.
- Every prompt template has an identifier and version.
- Every ADR follows the standard ADR format (see `decisions/ADR-template.md` if it exists, otherwise see the existing ADRs).

### 3.6 Dependency Management

- Python dependencies are managed with `uv` or `poetry`. The lockfile is committed.
- Dependencies are pinned to exact versions in production.
- New dependencies require justification in the PR description.
- Dependencies are audited regularly with `pip-audit` or equivalent.

### 3.7 Configuration

- All configuration is in plain text (YAML or TOML).
- Configuration files are version-controlled.
- Secrets are never committed. The user is responsible for secret management.
- The system must run with a minimal default configuration.

---

## 4. Contribution Standards

### 4.1 Who Can Contribute

Anyone. There is no formal gatekeeping. The constitution is the gate.

### 4.2 What We Accept

- Documentation improvements.
- New evaluation criteria.
- New schema fields (with version bumps).
- New interfaces.
- New examples.
- Bug fixes.
- Performance improvements that do not violate constitutional principles.
- New ADRs that document decisions.

### 4.3 What Requires Extra Scrutiny

- Changes to the constitution.
- Changes to the spec.
- Changes to schemas that break backward compatibility.
- New external dependencies.
- New network calls of any kind.
- New action capabilities.

### 4.4 What We Do Not Accept

- Code without documentation.
- Code without tests.
- Code that violates the constitution.
- Closed-source dependencies.
- Telemetry or analytics of any kind without explicit opt-in.
- Features that are not specified.

### 4.5 Review Process

- All changes go through pull request review.
- At least one maintainer approval is required for merge.
- Constitutional changes require unanimous maintainer approval.
- Trivial changes (typos, formatting) may be merged with one approval.

---

## 5. Definition of Completion

A subsystem is **complete** when:

1. **All architecture documents are up to date.** The implementation matches the documented design.
2. **All schemas are implemented and versioned.** Every field described in the schema exists in the code.
3. **All evaluations pass.** The subsystem produces output that meets the defined pass criteria.
4. **All examples work.** The end-to-end examples in `examples/` can be reproduced from scratch.
5. **All tests pass.** Unit, integration, and evaluation tests are green.
6. **Documentation is current.** README, docs/, and inline docstrings are accurate.
7. **Performance budgets are met.** The subsystem runs within the documented performance budget.
8. **Security review is complete.** The subsystem has been reviewed against `security/threat_model.md`.
9. **Audit logging is in place.** Every state change is recorded.
10. **Migration path is documented.** If the subsystem changes a schema, the migration is described.

A phase is **complete** when all of its constituent subsystems are complete.

A release is **complete** when the version of the spec it implements is itself complete and all of its evaluations pass.

---

## 6. Coding-Agent Workflow

SELF is designed to be implementable by coding agents. This section describes how a coding agent should approach the work.

### 6.1 The Agent's Job

A coding agent is a contributor. The agent is expected to:

1. Read the relevant documentation before writing code.
2. Implement the smallest change that advances the current phase.
3. Write tests that match the evaluations.
4. Update documentation to reflect what was built.
5. Open an ADR if a decision was made that isn't already documented.
6. Report back what was done, what was skipped, and what is uncertain.

### 6.2 The Agent's First Steps

When a coding agent enters this repository, it should:

1. Read `README.md` to understand the project.
2. Read `CONSTITUTION.md` to understand the constraints.
3. Read `spec.md` to understand the system.
4. Read `BUILDING.md` (this document) to understand the workflow.
5. Identify which phase is currently in progress from `roadmap/`.
6. Read the phase document.
7. Identify an issue or sub-task to work on.
8. Read all documentation related to that task.
9. Begin implementation.

### 6.3 The Agent's Loop

```
For each task:
    1. Identify the smallest deliverable.
    2. Read all documentation related to it.
    3. Identify the interfaces you must implement against.
    4. Identify the evaluation you must pass.
    5. Write the code.
    6. Write the tests.
    7. Run the tests.
    8. If tests fail, fix the code or the tests.
    9. Update the documentation if the design changed.
    10. Commit.
    11. Report.
```

### 6.4 The Agent's Constraints

The agent must not:

- Modify the constitution.
- Add network calls without explicit user authorization.
- Add telemetry of any kind.
- Commit secrets.
- Skip the documentation update step.
- Implement features outside the current phase.
- Make breaking changes to schemas without versioning.
- Bypass the audit log.
- Bypass the permission system.

### 6.5 The Agent's Reporting

When the agent finishes a task, it reports:

1. **What was done.** A summary of the changes.
2. **What was tested.** Which evaluations and tests were run.
3. **What was skipped.** Anything in scope that was not done, and why.
4. **What is uncertain.** Anything the agent is not confident about.
5. **What the human should review.** Anything that needs human attention.

### 6.6 The Agent's Failure Modes

The agent should fail loudly and visibly. Silent failure is the worst outcome. If the agent:

- Cannot understand a requirement, it should ask.
- Discovers a contradiction in the documentation, it should report it.
- Encounters an evaluation it cannot pass, it should report it.
- Finds that an interface is not specified, it should propose a specification and request review.

### 6.7 The Agent's Memory

The agent should:

- Keep a local notes file (`agent_notes.md` or similar, not committed) of decisions made during implementation.
- Update this file as the work progresses.
- Reference this file when continuing work in a future session.

---

## 7. Development Environment

### 7.1 Local Setup

A developer should be able to set up the system with:

1. A recent Python version (3.11+).
2. A package manager (`uv` or `poetry`).
3. Optional: Ollama or another local model runtime.
4. Optional: Docker for containerized development.

### 7.2 Repository Layout

The repository follows the structure defined in `README.md`. The `src/` directory contains the implementation. The structure within `src/` is:

```
src/
├── self/
│   ├── observer/         # Observer subsystem
│   ├── extractor/        # Extractor subsystem
│   ├── memory/           # Memory subsystem
│   ├── identity/         # Identity Graph subsystem
│   ├── persona/          # Persona Engine subsystem
│   ├── twin/             # Digital Twin subsystem
│   ├── action/           # Action Engine subsystem
│   ├── synthesis/        # Synthesis Engine subsystem
│   ├── storage/          # Storage abstraction
│   ├── eval/             # Evaluation framework
│   ├── orchestrator/     # Orchestration
│   ├── security/         # Security primitives
│   ├── interfaces/       # External system adapters
│   └── core/             # Shared types, schemas, utilities
├── tests/
│   ├── unit/
│   ├── integration/
│   └── eval/
├── pyproject.toml
├── README.md
└── ...
```

The directory structure may evolve. Changes to the structure require an ADR if they affect the public API of the system.

---

## 8. Release Process

### 8.1 Versioning

- Versions follow semantic versioning: `MAJOR.MINOR.PATCH`.
- A major version bump indicates a breaking change in the spec, schemas, or constitution.
- A minor version bump indicates new functionality that is backward-compatible.
- A patch version bump indicates bug fixes that are backward-compatible.

### 8.2 Releases

- A release is a tagged commit on `main`.
- A release includes a changelog entry summarizing the changes.
- A release passes the full evaluation suite.
- A release is signed and the signature is published.

### 8.3 Deprecation

- Deprecated features are marked as such in the documentation and the code.
- A deprecation notice appears in the release notes.
- A deprecated feature is removed in the next major version at the earliest.

---

## 9. Communication and Coordination

### 9.1 Issues

Issues are the primary unit of work. An issue should:

- Have a clear title.
- Describe the problem or feature.
- Reference the relevant documentation.
- Define the acceptance criteria.
- Be small enough to be completed in a single PR.

### 9.2 Discussions

Long-form discussions happen in:

- ADRs (for decisions).
- Issue threads (for specific problems).
- A discussion forum or mailing list (to be established).

### 9.3 Meetings

SELF is designed to be built asynchronously. Meetings are not required. If a meeting is necessary, it should be recorded and the notes committed to the repository.

---

## 10. The Long View

SELF is not built in a sprint. It is built in years. The standards in this document are designed to support a project that evolves over decades.

- **Prefer boring technology.** Boring technology is debuggable, replaceable, and well-understood.
- **Prefer simple data shapes.** A schema that fits on a page is a schema a person can hold in their head.
- **Prefer explicit over implicit.** Configuration is explicit. Dependencies are explicit. Authorizations are explicit.
- **Prefer audit over hope.** Every action is logged. Every state change is recorded. Hope is not a strategy.

Welcome to SELF. Build carefully.
