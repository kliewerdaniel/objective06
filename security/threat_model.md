# Threat Model: SELF

This document outlines the primary threats to the SELF system and the corresponding mitigation strategies.

## 1. Data Exfiltration
- **Threat**: An attacker gains access to the system and exfiltrates user data (observations, knowledge, persona).
- **Mitigation**:
    - **Locality**: Data resides on the user's hardware.
    - **Encryption**: Sensitive data is encrypted at rest with user-held keys.
    - **Audit Logs**: Every access to data is recorded.
    - **Permission Model**: Subsystems only access data they are explicitly authorized to see.
    - **Network Isolation**: No outbound connections without explicit user consent.

## 2. Prompt Injection
- **Threat**: An attacker provides malicious input (e.g., in an email or a web page) that tricks the LLM into performing unauthorized actions or revealing sensitive information.
- **Mitigation**:
    - **Structural Query Separation**: Treat retrieved content as data, never as instruction.
    - **Trust-Tier Tagging**: Explicit trust-tier tagging on all prompt segments.
    - **Injection Classifier**: A secondary classifier model whose sole job is to flag injection-suspicious content before it reaches the primary model.
    - **Rate-Limiting**: Rate-limiting on re-extracted content from a single source that newly triggers high-confidence knowledge objects.
    - **Sandboxing**: Actions are performed in restricted environments.
    - **Human-in-the-loop**: High-sensitivity actions require explicit confirmation.

## 3. Supply Chain Attack
- **Threat**: A malicious dependency in the software stack (e.g., a library or a model) compromises the system.
- **Mitigation**:
    - **Dependency Pinning**: All dependencies are version-locked.
    - **Security Audits**: Regular audits of dependencies.
    - **Model Provenance**: Use of reputable models with known provenance.
    - **Sandboxing**: Code from third-party libraries runs in isolated environments.

## 4. Model Hallucination
- **Threat**: The system generates false information as if it were fact.
- **Mitigation**:
    - **Grounding**: All assertions must be linked to source records via the provenance chain.
    - **Confidence Scores**: The user is shown the system's confidence in its answers.
    - **Evaluation**: Continuous monitoring of model performance against ground truth.

## 5. Unauthorized Action
- **Threat**: The system takes an action (e.g., sends an email, deletes a file) without user consent.
- **Mitigation**:
    - **Capability-based Permissions**: Actions are gated by granular, user-granted permissions.
    - **Consent Overlays**: Confirmation required for sensitive actions.
    - **Audit Log**: Every action is recorded before execution.
    - **Sandboxing**: Actions are executed in a restricted environment.

## 6. State Corruption
- **Threat**: A bug in the system corrupts the identity graph or the knowledge base.
- **Mitigation**:
    - **Audit Logs**: Every change is recorded, allowing for recovery.
    - **Snapshots**: Regular backups of the system state.
    - **Schema Validation**: Every write is checked against a strict schema.
    - **Immutability**: Observation events are immutable.
    - **Hash-chain Verification**: Audit log tampering is detected via hash-chain verification. The chain is checked on startup and on demand. A broken chain halts the system and alerts the user.

## 7. Denial of Service (DoS)
- **Threat**: A large volume of input (e.g., a huge number of emails) overwhelms the system.
- **Mitigation**:
    - **Backpressure**: The system throttles work when resource limits are reached.
    - **Queue Management**: Prioritized processing of user-initiated actions over background tasks.
    - **Resource Budgets**: Limits on CPU, memory, and network usage per subsystem.
