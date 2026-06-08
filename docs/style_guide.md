# Style Guide

## General Principles
- **Conciseness:** Be direct and to the point.
- **Consistency:** Use the same terminology as defined in `docs/glossary.md`.
- **Readability:** Use clear headings, lists, and tables.
- **Documentation-First:** Every code component must have a corresponding architecture document.

## Markdown Usage
- Use H1 for document titles.
- Use H2 and H3 for sections and subsections.
- Use bold for emphasis and code blocks for examples.
- Use mermaid for diagrams where appropriate.

## Code Style (Future)
- Follow the conventions of the language being used (e.g., Python PEP 8).
- Minimize comments; the code should be self-documenting.
- Use type hints.
- Follow the project's naming conventions (snake_case for variables/functions, PascalCase for classes).

## Documentation Conventions
- **Architecture Docs:** Describe purpose, responsibilities, inputs, outputs, dependencies, internal components, failure modes, metrics, and future evolution.
- **Schemas:** Define the exact data shape, including types, constraints, and provenance requirements.
- **Decisions (ADRs):** Record the "why" behind architectural choices.
- **Roadmap:** Define the phased approach to building the system.

## Agents
- When using agents to generate documentation, provide clear instructions on the target audience (usually the user and other contributors) and the required level of detail.
- Ensure the agent follows the existing style and patterns.
