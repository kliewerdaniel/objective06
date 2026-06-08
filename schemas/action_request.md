# Action Request Schema

An **action request** is a structured intent for the system to do something on the user's behalf.

## Attributes

| Attribute | Type | Description |
| --- | --- | --- |
| `id` | UUID | Unique identifier for the action request. |
| `type` | String | The category of action (e.g., "send_email", "create_file", "run_command", "browser_action"). |
| `description` | String | A human-readable description of what the system will do. |
| `input_data` | Object | The data required to perform the action (e.g., email body, file content, command arguments). |
| `authorization` | Object | Evidence of user authorization (e.g., session token, explicit "yes" for this specific action). |
| `constraints` | Array(String) | Any constraints on the action (e.g., "only between 9am-5pm", "do not mention X"). |
| `priority` | Integer | Relative priority of the action. |
| `timestamp` | Timestamp | When the request was created. |
| `provenance` | Object | Reference to the knowledge objects or twin queries that led to this request. |

## Examples

### Send Email
```json
{
  "id": "...",
  "type": "send_email",
  "description": "Send a follow-up email to John Doe regarding the quantum computing meeting.",
  "input_data": {
    "recipient": "john.doe@example.com",
    "subject": "Quantum Computing Follow-up",
    "body": "Hi John, it was great meeting you..."
  },
  "authorization": {
    "type": "explicit_consent",
    "timestamp": "..."
  },
  "constraints": ["do not mention the budget"],
  "priority": 1,
  "provenance": {
    "source_twin_query": "...",
    "source_knowledge_objects": ["..."]
  }
}
```
