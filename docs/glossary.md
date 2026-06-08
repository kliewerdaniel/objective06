# Glossary
2: 
3: This document provides clear definitions for terms used throughout the SELF project.
4: 
5: | Term | Definition |
6: | --- | --- |
7: | **SELF** | Synthetic Evolutionary Local Framework. A local-first cognitive infrastructure for personal continuity. |
8: | **Observation Event** | The atomic unit of input. A raw, immutable record of an action or change in the user's digital environment. |
9: | **Knowledge Object** | The atomic unit of meaning. A structured representation of a belief, goal, project, interest, etc. |
10: | **Identity Graph** | A temporal graph representation of the user's identity, relationships, and attributes. |
11: | **Persona Vector** | A high-dimensional embedding representing the user's identity at a point in time. |
12: | **Digital Twin** | The conversational interface that allows the user to query and interact with the identity model. |
13: | **Synthesis** | The process of generating human-readable summaries, reflections, and predictions from the system's state. |
14: | **Provenance** | The lineage of a piece of data back to its source observations and the processes that transformed it. |
15: | **Extractor** | The subsystem that turns observation events into knowledge objects. |
16: | **Orchestration** | The core loop that manages the timing, dependencies, and flow between all subsystems. |
17: | **Substrate** | The underlying storage or model layers (DuckDB, Vector DB, LLMs, etc.). |
18: | **Continuity** | The property of a representation that persists and evolves over long periods across different contexts and modalities. |
19: | **Locality** | The principle that the system and its data remain on the user's hardware by default. |
20: | **Auditability** | The ability for the user to trace every state change back to a source observation. |
21: | **Explainability** | The system's ability to provide a human-understandable justification for its beliefs and actions. |
22: | **Hot Tier** | The high-performance storage tier for frequently accessed data. |
23: | **Warm Tier** | The storage tier for data that is accessed less frequently but still needs to be queryable. |
24: | **Cold Tier** | The archival storage tier for data that is rarely accessed. |
25: | **Transaction Time** | In bitemporal modeling, the time at which a fact was recorded by the system. |
26: | **Valid Time** | In bitemporal modeling, the time during which a fact was true in the world. |
27: | **Model Lineage** | The unique identifier for a specific model and its version, used to track which model produced which vector. |
28: | **Capability** | A named, scoped action that a subsystem is authorized to perform. |
29: | **Bitemporal** | Modeling data using both valid time (when it was true) and transaction time (when it was recorded). |
30: | **Injection Classifier** | A model specifically designed to identify and score prompt injection attempts. |
31: | **Write Queue** | A serializing queue that ensures only one process writes to a storage substrate at a time. |
