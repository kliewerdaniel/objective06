# Action Result Schema

An **action result** is the outcome of an executed **action request**.

## Attributes

| Attribute | Type | Description |
| --- | --- | --- |
| `request_id` | UUID | Reference to the original action request. |
| `status` | String | The status of the action (e.g., "success", "failure", "partial_success", "cancelled"). |
| `output_data` | Object | The result of the action (e.g., email sent confirmation, file created path, command output). |
| `error_message` | String | Description of the error if the action failed.
| `error_code` | String | Machine-readable error code.
| `execution_time_ms` | Integer | How long the action took to complete.
| `timestamp` | Timestamp | When the action completed.
| `provenance` | Object | Reference to the request and the execution logs. |

## Examples

### Successful Email Send
```json
{
  "request_id": "...",
  "status": "success",
  "output_data": {
    "sent_at": "...",
    "message_id": "..."
  },
  "execution_time_ms": 450,
  "timestamp": "...",
  "provenance": {
    "request_id": "..."
  }
}
```

### Failed Command Execution
```json
{
  "request_id": "...",
  "status": "failure",
  "error_message": "Permission denied: cannot write to /root",
  "error_code": "E_ACCESS_DENIED",
  "execution_time_ms": 50,
  "timestamp": "...",
  "provenance": {
    "request_id": "..."
  }
}
```
