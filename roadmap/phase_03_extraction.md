# Phase 03: Extraction

## Status
- **Current Status:** Pending
- **Completion:** 0%

## Overview
Phase 03 implements the Extractor subsystem, which is the semantic interpretation layer of SELF. This phase enables the transformation of raw observation events into structured knowledge objects.

## Objectives
- Implement the Extractor subsystem.
- Develop extraction prompt templates for different knowledge types (beliefs, goals, projects, etc.).
- Implement the Event Batcher for efficient model calls.
- Implement the Model Client for local LLM integration.
- Implement the Output Validator for schema enforcement.
- Implement the Entity Linker for identity graph integration.

## Deliverables
- [ ] Extractor subsystem architecture and schema integration.
- [ ] Prompt library for core knowledge types.
- [ ] Event Batcher implementation.
- [ ] Model Client implementation.
- [ ] Output Validator implementation.
- [ ] Entity Linker implementation.
- [ ] Contradiction Detector implementation.
- [ ] Build evaluation harness for evaluations/extract_belief.md and evaluations/detect_goal.md (create these files if not present).

## Dependencies
- Phase 01: Foundation.
- Phase 02: Observation (provides the input events).

## Risks
- **Hallucination**: Ensuring the LLM does not invent knowledge objects.
- **Model Performance**: Balancing extraction quality with local model limitations.

## Success Criteria
- The system can extract "belief" and "goal" objects from a set of observation events.
- Knowledge objects are correctly linked to existing identity nodes.
- Every extracted object carries full provenance.
- Evaluations `extract_belief.md` and `discover_project.md` pass.
