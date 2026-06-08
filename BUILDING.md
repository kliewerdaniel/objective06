# BUILDING.md

This document defines the standards and workflow for contributing to the SELF project. Because SELF is a documentation-first project, all contributions must follow the "Documentation precedes code" principle.

## Contribution Workflow

Every contribution, whether by a human or an AI agent, must follow these steps:

1.  **Research**: Understand the existing architecture and specifications in `architecture/` and `spec.md`.
2.  **Documentation**: Create or update the relevant architecture document, schema, and evaluation criteria *before* writing any implementation code.
3.  **Design**: If the change is significant, create an Architecture Decision Record (ADR) in `decisions/`.
4.  **Implementation**: Write the code, following the project's style guide and ensuring it meets the definitions of completion.
5.  **Verification**: Run the evaluations defined in `evaluations/` to ensure the implementation is correct and meets the success criteria.
6.  **Documentation Update**: Update any relevant usage examples in `examples/` or prompt specifications in `prompts/`.

## Definition of Completion

A task is considered "complete" only when:
- [ ] The relevant architecture documentation is updated and accurate.
- [ ] All associated schemas are defined and versioned.
- [ ] The implementation code is written, passes all linting/typechecking, and follows project style.
- [ ] All unit and integration tests pass.
- [ ] All relevant evaluations pass.
- [ ] The audit log is correctly populated by the new functionality.
- [ ] The user is notified of the completion (via the summary or interaction).

## Coding-Agent Workflow

When using an agent (like opencode) to perform tasks:
1.  **Context Gathering**: The agent must first read the relevant architecture docs, schemas, and the specific phase it is working on.
2.  **Plan Generation**: The agent must provide a clear plan of action before starting any file edits.
3.  **Iterative Execution**: The agent should perform one logical step at a time (e.g., create schema -> implement store -> implement API).
4.  **Self-Verification**: After each step, the agent must verify the result (e.g., by running a test or checking a schema).
5.  **Final Verification**: The agent must run the final evaluations before declaring the task complete.

## Standards

### Code Style
- **Conciseness**: Write clean, direct code. Avoid unnecessary complexity.
- **Naming**: Use descriptive, consistent names (snake_case for functions/variables, PascalCase for classes).
- **Type Safety**: Use type hints where available.
- **No Comments**: Avoid comments unless they explain *why* something is done, rather than *what* is being done (the code should be self-documenting).
- **Error Handling**: Fail gracefully. Log errors to the audit log and surface clear messages to the user.

### Testing
- **Test-Driven**: Every new capability must have a corresponding evaluation in `evaluations/`.
- **Unit Tests**: Test the smallest units of logic in isolation.
- **Integration Tests**: Test the interaction between subsystems (e.g., Observer -> Extractor -> Memory).
- **Regression Tests**: Ensure that new changes do not break existing capabilities.

### Documentation
- **Architecture Docs**: Must describe responsibilities, inputs, outputs, dependencies, failure modes, and metrics.
- **Schemas**: Must be machine-readable and versioned.
- **ADRs**: Must capture the rationale behind significant architectural choices.
- **Consistency**: Always use the terms defined in `docs/glossary.md`.
