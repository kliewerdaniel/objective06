# Privacy Model: SELF

This document defines how SELF handles user privacy and data protection.

## 1. Data Minimization
SELF only collects data that is necessary to fulfill its primary purpose of maintaining a persistent, evolving representation of the user's identity. The system does not collect "extra" data for advertising, analytics, or other purposes.

## 2. Local-First Privacy
By default, all data stays on the user's machine. The system is designed to function without any network connectivity. Any remote interaction is an explicit opt-in by the user.

## 3. User Ownership
- **Ownership**: The user owns all data produced by SELF.
- **Access**: The user has the right to read, export, and delete all data in human-readable form.
- **Transparency**: Every data transformation (e.g., observation -> knowledge) is recorded in the audit log with full provenance.

## 4. Consent and Control
- **Granular Consent**: Permissions are granted for specific capabilities, not for the whole system.
- **Revocability**: Consent can be revoked at any time, and the system must stop using that capability immediately.
- **Time-bound Consent**: The user can grant permissions for specific time windows.
- **Use-bound Consent**: The user can restrict permissions to specific contexts (e.g., only for a specific project).

## 5. Anonymization and Redaction
- **PII Detection**: The Extractor subsystem is designed to detect and, if configured, redact Personally Identifiable Information (PII) before it is persisted in the knowledge base.
- **Privacy Filtering**: The user can define privacy filters that are applied to specific sources (e.g., "don't index my health emails").

## 6. Model Privacy
- **Local Inference**: SELF defaults to local inference models.
- **Data Privacy in Models**: When using remote models, the system uses techniques like prompt engineering and data stripping to minimize the amount of sensitive information sent to the third party.
- **Model Anonymization**: When querying a remote model, the system can strip user-specific identifiers from the prompt.

## 7. Auditing
- **Audit Log**: Every interaction with user data, every permission grant, and every action taken by the system is recorded in an immutable audit log.
- **User-Reviewable**: The user can audit the logs at any time to see what the system has done and what data it has accessed.

## 8. Compliance
SELF is designed to be compliant with major privacy regulations (GDPR, CCPA, etc.) by adhering to the principles of data minimization, purpose limitation, storage limitation, and user rights.
