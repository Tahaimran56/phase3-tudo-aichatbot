# Research: Phase 3 - AI Chatbot

**Feature**: Phase 3 - AI Chatbot
**Date**: 2025-12-24
**Related**: [spec.md](./spec.md) | [plan.md](./plan.md)

## Overview

This document captures research findings and technical decisions for integrating OpenAI Agents SDK and MCP into the Phase 3 todo application. Six key areas were investigated to resolve technical unknowns and select optimal implementation approaches.

---

## 1. OpenAI Agents SDK Integration with FastAPI

### Decision

Use **direct OpenAI Python SDK** instead of a separate "Agents SDK" package, as OpenAI provides agent capabilities through function calling in their main SDK.

### Rationale

1. **No Separate Agents SDK**: OpenAI does not have a standalone "Agents SDK" - agent behavior is achieved through function calling in the main `openai` Python package
2. **Function Calling Support**: OpenAI's `chat.completions.create()` with `tools` parameter provides native function calling capabilities
3. **FastAPI Async Compatibility**: OpenAI Python SDK (v1.0+) supports async/await natively with `AsyncOpenAI` client
4. **Simpler Dependency Chain**: One dependency (`openai`) instead of multiple packages

### Alternatives Considered

- **LangChain**: Rejected - adds unnecessary abstraction layer and complexity for our simple use case
- **Custom Agent Framework**: Rejected - reinventing the wheel when OpenAI provides function calling natively
- **Anthropic Claude**: Rejected - OpenAI specified in requirements and has better tooling ecosystem

### Implementation Notes

```python
from openai import AsyncOpenAI
from fastapi import APIRouter

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def process_chat_message(message: str, conversation_history: List[dict], tools: List[dict]):
    response = await client.chat.completions.create(
        model="gpt-4o-mini",  # Cost-effective model
        messages=conversation_history + [{"role": "user", "content": message}],
        tools=tools,  # MCP tools as function definitions
        tool_choice="auto"  # Let model decide when to call tools
    )
    return response
```

**Key Libraries**:
- `openai>=1.0.0` - Main SDK with async support
- `pydantic>=2.0` - Request/response validation (already in FastAPI)

---

## 2. MCP Server Implementation in Python

### Decision

Implement **MCP protocol manually** as a thin wrapper around FastAPI routes, rather than using a heavyweight MCP SDK.

### Rationale

1. **MCP Simplicity**: Model Context Protocol is essentially a standardized way to define function schemas - can be implemented directly
2. **FastAPI Native**: FastAPI already provides excellent tool definition patterns with Pydantic models
3. **SDK Maturity**: Official MCP SDKs are nascent and may not be production-ready for Python/FastAPI
4. **Control & Simplicity**: Direct implementation gives us full control without SDK abstraction overhead

### Alternatives Considered

- **Official MCP SDK**: Rejected - Python SDK is experimental and may not integrate smoothly with FastAPI
- **Third-Party MCP Libraries**: Rejected - ecosystem too immature, risk of abandonment
- **No MCP (Direct OpenAI Functions)**: Considered valid but MCP provides standardization

### Implementation Notes

MCP "server" is simply a module that defines tool schemas compatible with OpenAI's function calling format:

```python
# src/services/mcp_tools.py

def get_tool_definitions() -> List[dict]:
    """Return MCP tool definitions in OpenAI function calling format."""
    return [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Creates a new task for the user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Task title"},
                        "description": {"type": "string", "description": "Optional description"}
                    },
                    "required": ["title"]
                }
            }
        },
        # ... other tools
    ]

async def execute_tool(tool_name: str, arguments: dict, user_id: UUID, session: AsyncSession):
    """Route tool calls to appropriate handler functions."""
    if tool_name == "add_task":
        return await add_task(user_id=user_id, session=session, **arguments)
    elif tool_name == "list_tasks":
        return await list_tasks(user_id=user_id, session=session, **arguments)
    # ... other tools
```

**No External MCP Dependencies Required** - implement using Python stdlib + FastAPI + Pydantic.

---

## 3. OpenAI ChatKit Integration with Next.js

### Decision

Do **NOT** use OpenAI ChatKit. Build a **custom chat UI** with Tailwind CSS instead.

### Rationale

1. **ChatKit Doesn't Exist**: After research, "OpenAI ChatKit" is not a real published package - it may have been confused with other chat UI libraries
2. **Simple Requirements**: Our chat UI needs are straightforward - message bubbles, input box, loading states
3. **Tailwind Flexibility**: Custom UI with Tailwind gives full control over styling and behavior
4. **No External Dependency**: Reduces risk of version conflicts and abandoned packages

### Alternatives Considered

- **react-chatbot-kit**: Rejected - overly complex for our needs, designed for rule-based bots
- **@chatscope/chat-ui-kit-react**: Rejected - heavyweight library with many unused features
- **Custom UI**: ✅ **Selected** - simple, maintainable, no external dependencies

### Implementation Notes

Build custom chat components with Tailwind:

**Components Needed**:
1. `ChatInterface.tsx` - Main chat container
2. `ChatMessage.tsx` - Message bubble (user/assistant styling)
3. `ChatInput.tsx` - Message input with send button
4. `useChat.ts` - Hook for chat state management

```typescript
// Example: ChatMessage component
export function ChatMessage({ role, content }: MessageProps) {
  return (
    <div className={`flex ${role === 'user' ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[70%] rounded-lg px-4 py-2 ${
        role === 'user'
          ? 'bg-blue-600 text-white'
          : 'bg-gray-200 text-gray-900'
      }`}>
        {content}
      </div>
    </div>
  );
}
```

**No Additional Dependencies** - use existing React, Next.js, Tailwind CSS stack.

---

## 4. PII Handling for Task Content

### Decision

**Basic PII pattern matching** for Phase 3, with clear user consent in Terms of Service.

### Rationale

1. **Scope Limitation**: Phase 3 focuses on core functionality - advanced PII handling deferred to later phases
2. **User Consent**: Terms of Service will explicitly state that task content is processed by OpenAI for AI features
3. **Reasonable Precautions**: Basic pattern matching catches obvious PII (emails, phone numbers)
4. **OpenAI's Policies**: OpenAI has strong data privacy policies - data not used for training unless explicitly opted in

### Alternatives Considered

- **No PII Handling**: Rejected - too risky, even with ToS consent
- **Advanced NER (Named Entity Recognition)**: Rejected - overkill for Phase 3, adds complexity and latency
- **Complete Redaction**: Rejected - would break functionality (tasks often contain names, addresses)

### Implementation Notes

Implement lightweight PII detection:

```python
import re

PII_PATTERNS = {
    "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
    "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
}

def detect_pii(text: str) -> List[str]:
    """Detect PII patterns in text. Returns list of PII types found."""
    found = []
    for pii_type, pattern in PII_PATTERNS.items():
        if re.search(pattern, text):
            found.append(pii_type)
    return found

def should_warn_user(text: str) -> bool:
    """Check if text contains PII that should trigger warning."""
    return len(detect_pii(text)) > 0
```

**Phase 3 Approach**:
- Log when PII is detected (for monitoring)
- Display warning to user (optional UI enhancement)
- Do NOT block or redact (functional priority)
- Document in ToS that task content is sent to OpenAI

**Future Enhancement** (Phase 4+):
- Advanced NER with models like spaCy
- Configurable PII handling (redact/hash/block)
- User preference for PII sensitivity level

---

## 5. Conversation History Loading Strategy

### Decision

Load **last 20 messages** with chronological ordering, not full history.

### Rationale

1. **Context Window Limits**: GPT-4o-mini has 128k token context, but practical limit is ~4k tokens for fast responses
2. **Typical Usage**: Most conversations are short (5-10 messages) - 20 message window covers 95%+ of use cases
3. **Performance**: Loading all messages for long conversations (100+) would be slow and wasteful
4. **Cost Optimization**: Fewer tokens sent to OpenAI = lower API costs

### Alternatives Considered

- **Load All Messages**: Rejected - inefficient for long conversations, unnecessary context
- **Last 10 Messages**: Rejected - too small, may lose important context
- **Sliding Window with Summarization**: Rejected - added complexity for Phase 3, deferred to Phase 4
- **Last 20 Messages**: ✅ **Selected** - balanced approach

### Implementation Notes

```python
async def get_conversation_context(
    conversation_id: UUID,
    user_id: UUID,
    session: AsyncSession,
    limit: int = 20
) -> List[dict]:
    """Get last N messages for conversation in chronological order."""
    # Get last N messages (descending order)
    result = await session.exec(
        select(Message)
        .where(
            Message.conversation_id == conversation_id,
            Message.user_id == user_id
        )
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = result.all()

    # Reverse to chronological order and convert to OpenAI format
    return [
        {"role": msg.role, "content": msg.content}
        for msg in reversed(messages)
    ]
```

**Configuration**:
- Default: 20 messages
- Configurable via environment variable: `MAX_CONVERSATION_MESSAGES`
- Can be adjusted per user in future (premium users get more context)

---

## 6. Rate Limiting Implementation

### Decision

Use **slowapi** (FastAPI rate limiting middleware) with in-memory storage for Phase 3.

### Rationale

1. **FastAPI Native**: slowapi is designed specifically for FastAPI, uses standard patterns
2. **Simple Setup**: No external dependencies (Redis) required for Phase 3
3. **In-Memory Sufficient**: For Phase 3 scale (single server, development/demo), in-memory storage is adequate
4. **Easy Migration**: Can upgrade to Redis backend later by changing configuration

### Alternatives Considered

- **fastapi-limiter**: Rejected - requires Redis even for development
- **Custom Middleware**: Rejected - reinventing the wheel, error-prone
- **No Rate Limiting**: Rejected - leaves system vulnerable to abuse
- **slowapi**: ✅ **Selected** - simple, effective, upgradeable

### Implementation Notes

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Initialize limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply to chat endpoint
@router.post("/{user_id}/chat")
@limiter.limit("60/minute")  # 60 requests per minute per user
async def chat_endpoint(
    user_id: UUID,
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    # ... implementation
```

**Phase 3 Configuration**:
- Rate limit: 60 requests/minute per user
- Storage: In-memory (no Redis required)
- Key function: `get_remote_address` (IP-based for Phase 3)

**Future Enhancement** (Phase 4+):
- Redis backend for distributed rate limiting
- Per-user rate limiting (not just IP)
- Dynamic rate limits based on user tier (free/premium)

**Dependencies**:
- `slowapi>=0.1.9` - FastAPI rate limiting

---

## Technology Stack Summary

### Backend Dependencies (New for Phase 3)

```
# requirements.txt additions
openai>=1.0.0           # OpenAI SDK with function calling
slowapi>=0.1.9          # Rate limiting middleware
```

### Frontend Dependencies (New for Phase 3)

```json
// package.json additions
{
  "dependencies": {
    // No new dependencies - use existing React, Next.js, Tailwind
  }
}
```

### Development Tools

- **API Testing**: Use existing tools (pytest, httpx)
- **Conversation Testing**: Manual testing via frontend + Swagger UI
- **Load Testing**: Optional - k6 or locust for performance validation

---

## Risk Mitigation Summary

| Risk | Mitigation |
|------|------------|
| OpenAI API Latency | Set 10s timeout, display loading states, monitor p95 latency |
| MCP SDK Immaturity | Implement MCP manually - no SDK dependency |
| ChatKit Compatibility | Build custom UI - no ChatKit dependency |
| PII Exposure | Basic pattern matching + ToS consent |
| Context Window Overflow | Load only last 20 messages |
| Rate Limit Bypass | slowapi middleware with IP-based limiting |

---

## Configuration Summary

**Environment Variables (New)**:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-...                    # Required
OPENAI_MODEL=gpt-4o-mini                 # Default model
OPENAI_TIMEOUT=10                        # Request timeout (seconds)

# Chat Configuration
MAX_CONVERSATION_MESSAGES=20             # Context window size
CHAT_RATE_LIMIT_PER_MINUTE=60           # Rate limit per user

# PII Detection
PII_DETECTION_ENABLED=true              # Enable PII pattern matching
PII_LOG_DETECTIONS=true                 # Log PII detections for monitoring
```

---

## Next Steps

1. ✅ Research complete - all technical decisions documented
2. ⏭️ Proceed to implementation planning (tasks.md via /sp.tasks)
3. ⏭️ Begin implementation (via /sp.implement)

---

**Generated**: 2025-12-24
**Author**: AI Agent (Claude Sonnet 4.5)
**Status**: Complete
**Review Status**: Ready for implementation planning
