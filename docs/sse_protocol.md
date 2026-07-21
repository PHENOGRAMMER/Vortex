# OmniGen SSE Protocol v1

All Server-Sent Events use:

event: message

The JSON payload has this structure:

```json
{
  "stream_id": "...",
  "event_id": "...",
  "sequence": 1,
  "timestamp": "...",
  "type": "token",
  "data": {}
}
```

## Supported Types

- token
- status
- done
- error
- heartbeat
- tool_start
- tool_result
- rag
- image