# Phase 06: Persona

## Status
- **Current Status:** Pending
- **Completion:** 0%

## Overview
Phase 06 implements the Persona Engine, which creates a continuous semantic representation of the user. This phase moves the system from discrete data to a fluid "identity vector."

## Objectives
- Implement the Persona Engine.
- Integrate the local embedding model for vector generation.
- Implement the Persona Updater with multiple update strategies (Moving Average, Decay).
- Implement the Consistency Scorer to check new knowledge against the persona.
- Implement the Predictor for behavior extrapolation.
- Implement the Decay Engine for temporal weighting.

## Deliverables
- [ ] Persona Engine architecture and schema integration.
- [ ] Embedding Computer implementation.
- [ ] Persona Vector Store (time-series of vectors).
- [ ] Persona Updater implementation.
- [ ] Consistency Scorer implementation.
- [ ] Predictor implementation.
- [ ] Decay Engine implementation.

## Dependencies
- Phase 03: Extraction (provides knowledge objects).
- Phase 04: Memory (provides storage).
- Phase 05: Identity (provides entity context).

## Risks
- **Vector Drift**: Ensuring the persona doesn't shift too rapidly due to noise.
- **Model Dependency**: Ensuring the persona can be "re-anchored" if the embedding model changes.

## Success Criteria
- The system can produce a persona vector for the user.
- The system can score the consistency of a new belief with the current persona.
- The system can predict the user's next likely interest based on history.
- Evaluation: `evaluations/update_persona.md` passes.
