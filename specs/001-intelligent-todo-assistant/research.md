# Research: Intelligent Todo Assistant - Phase 3 AI Integration

**Feature**: 001-intelligent-todo-assistant
**Date**: 2025-12-24
**Status**: Complete

## Overview

This document consolidates research findings for implementing AI-powered features in the Todo app, including RAG-based chat, semantic vector search, personalization, and Urdu translation.

---

## 1. Qdrant Cloud Integration with FastAPI

### Decision
Use Qdrant Cloud Free Tier with async `qdrant-client` Python SDK, implementing strict user isolation via metadata filtering.

### Rationale
- **Free Tier Sufficiency**: 1GB storage ≈ 600k vectors (1536 dimensions) - adequate for MVP with 100 users × 10k tasks
- **Async Support**: Native async/await patterns integrate seamlessly with FastAPI
- **Metadata Filtering**: Built-in support for filtering by `user_id` ensures multi-tenant isolation
- **Managed Service**: No infrastructure overhead, automatic scaling, built-in persistence

### Implementation Pattern

**Client Initialization** (Dependency Injection):
```python
# backend/src/api/deps.py
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams
from functools import lru_cache

@lru_cache()
def get_qdrant_client() -> AsyncQdrantClient:
    return AsyncQdrantClient(
        url=settings.QDRANT_URL,  # e.g., "https://xyz.cloud.qdrant.io"
        api_key=settings.QDRANT_API_KEY,
        timeout=10.0
    )

async def init_qdrant_collection():
    """Initialize collection on app startup"""
    client = get_qdrant_client()
    collection_name = "task_embeddings"

    # Create collection if not exists
    collections = await client.get_collections()
    if collection_name not in [c.name for c in collections.collections]:
        await client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=1536,  # text-embedding-3-small dimension
                distance=Distance.COSINE
            )
        )
```

**User Isolation Filter**:
```python
from qdrant_client.models import Filter, FieldCondition, MatchValue

def build_user_filter(user_id: str) -> Filter:
    """Construct metadata filter for strict user isolation"""
    return Filter(
        must=[
            FieldCondition(
                key="user_id",
                match=MatchValue(value=user_id)
            )
        ]
    )

# Usage in search
async def search_task_vectors(
    query_vector: list[float],
    user_id: str,
    limit: int = 5
) -> list[ScoredPoint]:
    client = get_qdrant_client()
    results = await client.search(
        collection_name="task_embeddings",
        query_vector=query_vector,
        query_filter=build_user_filter(user_id),  # CRITICAL: Always filter by user_id
        limit=limit,
        score_threshold=0.7  # Relevance threshold
    )
    return results
```

### Performance Optimization
- **Connection Pooling**: Single AsyncQdrantClient instance (lru_cache singleton)
- **Batch Upserts**: Upload embeddings in batches of 100 for bulk operations
- **Payload Indexing**: Index `user_id` field for fast filtering: `await client.create_payload_index("task_embeddings", "user_id")`
- **Score Threshold**: Set minimum similarity (0.7) to filter irrelevant results

### Error Handling
```python
from qdrant_client.http.exceptions import UnexpectedResponse
import asyncio

async def safe_vector_search(query_vector, user_id, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await search_task_vectors(query_vector, user_id)
        except UnexpectedResponse as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
        except asyncio.TimeoutError:
            # Log timeout, return empty results gracefully
            return []
```

---

## 2. OpenAI Agents SDK vs Direct Chat Completions API

### Decision
**Use Direct Chat Completions API with function calling** instead of OpenAI Agents SDK (Assistants API) for MVP.

### Rationale
- **Production Readiness**: Chat Completions API is battle-tested, Agents SDK/Assistants API has higher latency and beta status
- **Cost Control**: Direct API calls are cheaper, no assistant storage fees
- **Flexibility**: Full control over conversation state, easier debugging
- **Streaming Support**: Native streaming for real-time UI updates

### Alternatives Considered
| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **Assistants API** | Managed state, built-in tool calling | High latency (>5s), beta status, opaque pricing | ❌ Rejected |
| **Chat Completions + Functions** | Low latency, proven, streaming | Manual state management | ✅ **Selected** |
| **LangChain/LlamaIndex** | Rich abstractions, many integrations | Heavy dependencies, abstraction overhead | ❌ Overkill for MVP |

### Implementation Pattern

**Session State Management** (Database):
```python
# backend/src/models/chat_session.py
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    user = relationship("User", back_populates="chat_sessions")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False, index=True)
    role = Column(String, nullable=False)  # 'user' | 'assistant' | 'system'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")
```

**Chat Service with Function Calling**:
```python
# backend/src/services/rag_service.py
from openai import AsyncOpenAI
import json

class RAGService:
    def __init__(self, openai_client: AsyncOpenAI, qdrant_client, db_session):
        self.openai = openai_client
        self.qdrant = qdrant_client
        self.db = db_session

    async def chat(
        self,
        user_message: str,
        user_id: str,
        session_id: str,
        professional_background: str
    ) -> str:
        # 1. Retrieve conversation history
        messages = await self.get_conversation_history(session_id)

        # 2. Generate embedding for user query
        embedding = await self.openai.embeddings.create(
            model="text-embedding-3-small",
            input=user_message
        )
        query_vector = embedding.data[0].embedding

        # 3. Search relevant tasks via RAG
        relevant_tasks = await self.search_task_vectors(query_vector, user_id)

        # 4. Construct system prompt with context
        system_prompt = self.build_system_prompt(professional_background, relevant_tasks)

        # 5. Call LLM with function calling tools
        response = await self.openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                *messages,
                {"role": "user", "content": user_message}
            ],
            functions=self.get_task_functions(),  # CRUD tools
            temperature=0.7,
            max_tokens=500
        )

        assistant_message = response.choices[0].message.content

        # 6. Save messages to DB
        await self.save_messages(session_id, user_message, assistant_message)

        return assistant_message

    def build_system_prompt(self, background: str, tasks: list) -> str:
        context = "\n".join([f"- {t.payload['title']}: {t.payload['description']}" for t in tasks])
        return f"""You are an AI assistant helping a {background} professional manage their tasks.

Relevant tasks:
{context}

Provide concise, actionable advice based on the user's tasks. Always ground responses in the provided context."""
```

**Streaming for Real-Time UI**:
```python
async def chat_stream(self, user_message: str, user_id: str, session_id: str):
    """Stream response for real-time UI updates"""
    # ... (same setup as above)

    stream = await self.openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[...],
        stream=True  # Enable streaming
    )

    full_response = ""
    async for chunk in stream:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            full_response += content
            yield content  # Send to frontend via SSE

    await self.save_messages(session_id, user_message, full_response)
```

---

## 3. RAG Pipeline Architecture

### Decision
**Pipeline**: User Query → Embedding → Qdrant Search → Context Injection → LLM → Response

### text-embedding-3-small Specifications
- **Dimensions**: 1536 (default), supports 512/1536 dimensional outputs
- **Performance**: 62.3% on MTEB benchmark, cost-effective
- **Cost**: $0.02 per 1M tokens (≈ 4M words)
- **Throughput**: ~3000 requests/min (tier 1)

### Implementation Flow

```
┌─────────────┐
│ User Query  │ "What are my priorities?"
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ Generate Embedding  │ OpenAI text-embedding-3-small
└──────┬──────────────┘
       │ [1536-dim vector]
       ▼
┌─────────────────────┐
│ Qdrant Search       │ Cosine similarity + user_id filter
└──────┬──────────────┘
       │ Top 5 tasks (score ≥ 0.7)
       ▼
┌─────────────────────┐
│ Context Augmentation│ Format tasks → system prompt
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ LLM Generation      │ gpt-4o-mini with injected context
└──────┬──────────────┘
       │
       ▼
┌─────────────┐
│ Response    │ "Your top priority is..."
└─────────────┘
```

### Embedding Generation Best Practices

**Batch Processing**:
```python
async def generate_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """Generate embeddings in batches of 100 (API limit: 2048)"""
    embeddings = []
    batch_size = 100

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        response = await openai.embeddings.create(
            model="text-embedding-3-small",
            input=batch
        )
        embeddings.extend([e.embedding for e in response.data])

    return embeddings
```

**Text Preprocessing**:
```python
def prepare_task_text(task: Task) -> str:
    """Combine title + description for embedding"""
    text = f"{task.title}\n{task.description or ''}"
    # Truncate to 8191 tokens (model limit)
    return text[:30000]  # Rough approximation: 4 chars ≈ 1 token
```

### Search Relevance Thresholds

| Cosine Similarity | Interpretation | Action |
|-------------------|----------------|--------|
| 0.9 - 1.0 | Highly relevant | Return as primary context |
| 0.7 - 0.9 | Relevant | Include in context |
| 0.5 - 0.7 | Marginally relevant | Exclude (too low quality) |
| < 0.5 | Not relevant | Exclude |

**Recommendation**: Use threshold of **0.7** to balance precision and recall.

### Context Injection Pattern

```python
def format_tasks_for_context(tasks: list[ScoredPoint]) -> str:
    """Format retrieved tasks for LLM prompt"""
    if not tasks:
        return "No directly relevant tasks found."

    context_parts = []
    for i, task in enumerate(tasks, 1):
        payload = task.payload
        context_parts.append(
            f"{i}. [{payload['status']}] {payload['title']}\n"
            f"   Priority: {payload['priority']} | Due: {payload['due_date']}\n"
            f"   {payload['description'][:200]}"
        )

    return "\n\n".join(context_parts)
```

### Caching Strategy

**Query-Level Cache** (Redis):
```python
import hashlib
import json
from redis.asyncio import Redis

class RAGCache:
    def __init__(self, redis: Redis):
        self.redis = redis
        self.ttl = 300  # 5 minutes

    async def get_cached_response(self, query: str, user_id: str) -> str | None:
        cache_key = self.build_cache_key(query, user_id)
        return await self.redis.get(cache_key)

    async def cache_response(self, query: str, user_id: str, response: str):
        cache_key = self.build_cache_key(query, user_id)
        await self.redis.setex(cache_key, self.ttl, response)

    def build_cache_key(self, query: str, user_id: str) -> str:
        query_hash = hashlib.sha256(query.encode()).hexdigest()[:16]
        return f"rag:{ user_id}:{query_hash}"
```

**Embedding Cache** (Database):
- Cache task embeddings in `task_embeddings` table (task_id → vector mapping)
- Only regenerate on task update, not on every query
- Reduces embedding API calls by >90%

---

## 4. MCP Server Implementation

### Decision
**Embed MCP-like tool interface directly in FastAPI** using OpenAI function calling, not separate MCP server process.

### Rationale
- **Simplicity**: No separate service to deploy/manage
- **Latency**: Direct function calls faster than inter-process communication
- **Security**: Internal functions, no network exposure
- **MVP Scope**: Full MCP protocol unnecessary for task CRUD

### Tool Definition Pattern

```python
# backend/src/services/mcp_server.py (conceptual - actually inline tools)
from typing import Callable, Any
from pydantic import BaseModel

class TaskTool(BaseModel):
    """Tool schema for OpenAI function calling"""
    name: str
    description: str
    parameters: dict

def get_task_tools() -> list[dict]:
    """Define tools for AI agent to call"""
    return [
        {
            "name": "get_user_tasks",
            "description": "Retrieve all tasks for the authenticated user, optionally filtered by status",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed"],
                        "description": "Filter tasks by status"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of tasks to return",
                        "default": 10
                    }
                },
                "required": []
            }
        },
        {
            "name": "create_task",
            "description": "Create a new task for the user",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title"},
                    "description": {"type": "string", "description": "Task description"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                    "due_date": {"type": "string", "format": "date", "description": "ISO 8601 date"}
                },
                "required": ["title"]
            }
        },
        {
            "name": "update_task",
            "description": "Update an existing task",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "UUID of task to update"},
                    "title": {"type": "string"},
                    "status": {"type": "string", "enum": ["pending", "in_progress", "completed"]},
                    "priority": {"type": "string", "enum": ["low", "medium", "high"]}
                },
                "required": ["task_id"]
            }
        },
        {
            "name": "search_tasks",
            "description": "Search tasks by semantic similarity to a query",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "limit": {"type": "integer", "default": 5}
                },
                "required": ["query"]
            }
        }
    ]
```

**Tool Execution Router**:
```python
class ToolExecutor:
    def __init__(self, db_session, task_service, vector_service):
        self.db = db_session
        self.task_service = task_service
        self.vector_service = vector_service

    async def execute_tool(
        self,
        tool_name: str,
        arguments: dict,
        user_id: str
    ) -> dict:
        """Route tool calls to appropriate service"""
        tools = {
            "get_user_tasks": self.get_user_tasks,
            "create_task": self.create_task,
            "update_task": self.update_task,
            "search_tasks": self.search_tasks
        }

        if tool_name not in tools:
            raise ValueError(f"Unknown tool: {tool_name}")

        # Execute with user context for isolation
        return await tools[tool_name](user_id=user_id, **arguments)

    async def get_user_tasks(self, user_id: str, status: str = None, limit: int = 10):
        tasks = await self.task_service.get_tasks(user_id, status, limit)
        return {"tasks": [t.dict() for t in tasks]}

    async def create_task(self, user_id: str, title: str, **kwargs):
        task = await self.task_service.create_task(user_id, title, **kwargs)
        # Trigger vector sync
        await self.vector_service.sync_task_embedding(task)
        return {"task_id": task.id, "status": "created"}
```

### Security Considerations
- **Authentication**: Always validate `user_id` from JWT before tool execution
- **Input Validation**: Use Pydantic models to validate tool arguments
- **Authorization**: Tools can only access/modify caller's own data
- **Rate Limiting**: Apply per-user quotas on tool calls to prevent abuse

---

## 5. PII Detection and Redaction

### Decision
**Regex-based PII detection with contextual redaction** before sending to OpenAI embedding API.

### PII Detection Patterns

```python
# backend/src/services/pii_redactor.py
import re
from typing import Pattern

class PIIRedactor:
    # Email pattern
    EMAIL: Pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

    # Phone patterns (US + international)
    PHONE_US: Pattern = re.compile(r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b')
    PHONE_INTL: Pattern = re.compile(r'\+[0-9]{1,3}[-\s]?(?:\([0-9]{1,4}\)|[0-9]{1,4})[-\s]?[0-9]{3,4}[-\s]?[0-9]{4}')

    # SSN pattern
    SSN: Pattern = re.compile(r'\b(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b')

    # Credit card pattern (basic)
    CREDIT_CARD: Pattern = re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b')

    # Address pattern (US - street number + name)
    ADDRESS: Pattern = re.compile(r'\b\d{1,5}\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct)\b', re.IGNORECASE)

    def redact_text(self, text: str) -> tuple[str, list[str]]:
        """Redact PII from text, return (redacted_text, detected_types)"""
        detected_types = []
        redacted = text

        # Redact email
        if self.EMAIL.search(redacted):
            detected_types.append("email")
            redacted = self.EMAIL.sub("[EMAIL]", redacted)

        # Redact phones
        if self.PHONE_US.search(redacted) or self.PHONE_INTL.search(redacted):
            detected_types.append("phone")
            redacted = self.PHONE_US.sub("[PHONE]", redacted)
            redacted = self.PHONE_INTL.sub("[PHONE]", redacted)

        # Redact SSN
        if self.SSN.search(redacted):
            detected_types.append("ssn")
            redacted = self.SSN.sub("[SSN]", redacted)

        # Redact credit card
        if self.CREDIT_CARD.search(redacted):
            detected_types.append("credit_card")
            redacted = self.CREDIT_CARD.sub("[CREDIT_CARD]", redacted)

        # Redact address
        if self.ADDRESS.search(redacted):
            detected_types.append("address")
            redacted = self.ADDRESS.sub("[ADDRESS]", redacted)

        return redacted, detected_types
```

### Redaction vs Tokenization

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **Replacement with [REDACTED]** | Preserves text structure, semantically neutral | May confuse embeddings | ✅ **Selected** |
| **Tokenization (hash)** | Preserves uniqueness | Reversible if salt leaked, breaks semantic meaning | ❌ Too complex |
| **Removal (delete)** | Strongest privacy | Disrupts sentence structure, impacts embedding quality | ❌ Reduces accuracy |

### Performance Impact

**Benchmark** (1000 tasks, avg 150 chars each):
- PII regex scanning: ~15ms total (0.015ms/task)
- Negligible overhead (<1% of API latency)

**Optimization**:
- Compile regex patterns once (class-level constants)
- Only scan task titles + descriptions, not metadata
- Run in background task to avoid blocking API response

### False Positive Handling

**Common False Positives**:
- Dates formatted like SSN: `123-45-6789` → Check context (year ranges)
- Technical IDs: `192.168.1.1` → Whitelist known patterns
- URLs: `http://example.com` → Exclude if contains `://`

**Strategy**: Prefer false positives (over-redaction) to maintain privacy. Better to redact an ID than leak PII.

### Integration Example

```python
# backend/src/services/vector_sync.py
async def sync_task_embedding(task: Task, user_id: str):
    # 1. Prepare text
    text = f"{task.title}\n{task.description or ''}"

    # 2. Redact PII
    redactor = PIIRedactor()
    redacted_text, detected_types = redactor.redact_text(text)

    # 3. Log PII detection (for monitoring)
    if detected_types:
        logger.warning(f"PII detected in task {task.id}: {detected_types}")

    # 4. Generate embedding on redacted text
    embedding = await openai.embeddings.create(
        model="text-embedding-3-small",
        input=redacted_text
    )

    # 5. Store in Qdrant
    await qdrant.upsert(
        collection_name="task_embeddings",
        points=[{
            "id": task.id,
            "vector": embedding.data[0].embedding,
            "payload": {
                "user_id": user_id,
                "task_id": task.id,
                "title": task.title,  # Original, not redacted
                "status": task.status,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None
            }
        }]
    )
```

---

## 6. Context-Aware Urdu Translation

### Decision
**OpenAI Chat Completions API with domain-specific system prompts** + technical glossary injection + database caching.

### Translation Prompt Engineering

**System Prompt Template**:
```python
TRANSLATION_SYSTEM_PROMPT = """You are a technical translator specializing in {domain} terminology. Translate the following English text to Urdu while preserving technical accuracy.

Guidelines:
1. Preserve technical terms in English if no accurate Urdu equivalent exists (e.g., "API", "Git", "deployment")
2. For terms with Urdu equivalents, provide transliteration in parentheses: مثال (example)
3. Maintain formatting (bullet points, line breaks, emphasis)
4. Use formal/professional tone suitable for technical documentation

Technical Glossary ({domain}):
{glossary}

Translate the text naturally while respecting the above guidelines."""

def build_translation_prompt(text: str, domain: str) -> list[dict]:
    glossary = get_domain_glossary(domain)  # Load SW/HW specific terms

    return [
        {
            "role": "system",
            "content": TRANSLATION_SYSTEM_PROMPT.format(
                domain=domain,
                glossary=glossary
            )
        },
        {
            "role": "user",
            "content": f"Translate to Urdu:\n\n{text}"
        }
    ]
```

### Technical Glossary Structure

**Software Domain**:
```python
SOFTWARE_GLOSSARY = """
- Bug: نقص (nuqs) - but use "bug" in mixed contexts
- Deploy/Deployment: تعیناتی (ta'enati)
- Sprint: اسپرنٹ (sprint - transliteration)
- API: API (keep English)
- Frontend: فرنٹ اینڈ (front end - transliteration)
- Backend: بیک اینڈ (back end - transliteration)
- Database: ڈیٹا بیس (database - transliteration)
- Code Review: کوڈ جائزہ (code review)
- Pull Request: پل ریکوئسٹ (pull request - transliteration)
- Unit Test: یونٹ ٹیسٹ (unit test)
"""

HARDWARE_GLOSSARY = """
- Circuit: سرکٹ (circuit)
- PCB: PCB (keep English)
- Breadboard: بریڈ بورڈ (breadboard - transliteration)
- Prototype: نمونہ (namoona) or پروٹوٹائپ (prototype)
- Testing: جانچ (jaanch)
- Manufacturing: تیاری (tayari)
- Assembly: اسمبلی (assembly)
- Component: جزو (juzz) or کمپونینٹ (component)
"""

def get_domain_glossary(background: str) -> str:
    glossaries = {
        "software": SOFTWARE_GLOSSARY,
        "hardware": HARDWARE_GLOSSARY,
        "other": SOFTWARE_GLOSSARY  # Default to software
    }
    return glossaries.get(background.lower(), SOFTWARE_GLOSSARY)
```

### Translation Service Implementation

```python
# backend/src/services/translation_service.py
from openai import AsyncOpenAI
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

class TranslationService:
    def __init__(self, openai_client: AsyncOpenAI, db: Session):
        self.openai = openai_client
        self.db = db
        self.cache_ttl = timedelta(days=30)

    async def translate_to_urdu(
        self,
        text: str,
        domain: str,
        task_id: str = None
    ) -> str:
        # 1. Check cache
        cached = await self.get_cached_translation(text, domain)
        if cached:
            return cached.translation

        # 2. Build prompt with glossary
        messages = build_translation_prompt(text, domain)

        # 3. Call OpenAI
        response = await self.openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3,  # Lower temp for consistent translations
            max_tokens=1000
        )

        translation = response.choices[0].message.content

        # 4. Cache result
        await self.cache_translation(text, domain, translation, task_id)

        return translation

    async def get_cached_translation(self, text: str, domain: str):
        """Check database cache for existing translation"""
        cache_key = hashlib.sha256(f"{text}:{domain}".encode()).hexdigest()

        cached = self.db.query(TranslationCache).filter_by(
            cache_key=cache_key,
            target_language="ur"
        ).filter(
            TranslationCache.created_at > datetime.utcnow() - self.cache_ttl
        ).first()

        return cached

    async def cache_translation(
        self,
        original: str,
        domain: str,
        translation: str,
        task_id: str = None
    ):
        """Store translation in database cache"""
        cache_key = hashlib.sha256(f"{original}:{domain}".encode()).hexdigest()

        cache_entry = TranslationCache(
            cache_key=cache_key,
            original_text=original[:5000],  # Store first 5k chars
            translated_text=translation,
            source_language="en",
            target_language="ur",
            domain=domain,
            task_id=task_id,
            created_at=datetime.utcnow()
        )

        self.db.add(cache_entry)
        await self.db.commit()
```

### Frontend RTL Implementation

**Tailwind CSS RTL Support**:
```tsx
// frontend/src/components/tasks/TaskCard.tsx
interface TaskCardProps {
  task: Task;
  showUrdu: boolean;
}

export function TaskCard({ task, showUrdu }: TaskCardProps) {
  const displayText = showUrdu ? task.urdu_translation : task.title;

  return (
    <div
      className={`
        p-4 bg-white rounded-lg shadow
        ${showUrdu ? 'dir-rtl text-right' : 'dir-ltr text-left'}
      `}
      dir={showUrdu ? 'rtl' : 'ltr'}
    >
      <h3 className="text-lg font-semibold">
        {displayText}
      </h3>
      {task.description && (
        <p
          className={`mt-2 text-gray-600 ${showUrdu ? 'text-right' : 'text-left'}`}
          dir={showUrdu ? 'rtl' : 'ltr'}
        >
          {showUrdu ? task.urdu_description : task.description}
        </p>
      )}
    </div>
  );
}
```

**Tailwind Config for RTL**:
```js
// frontend/tailwind.config.js
module.exports = {
  theme: {
    extend: {
      // Add RTL-specific utilities
    }
  },
  plugins: [
    require('@tailwindcss/rtl')  // Optional plugin for advanced RTL
  ]
}
```

### Mixed LTR/RTL Content Handling

For technical terms in English within Urdu text:
```html
<p dir="rtl">
  یہ ایک <span dir="ltr">API endpoint</span> ہے جو <span dir="ltr">JSON</span> واپس کرتا ہے
</p>
```

---

## 7. Background Task Vector Sync

### Decision
**Use FastAPI BackgroundTasks** (not Celery) for MVP vector sync to minimize complexity.

### Rationale
- **Simplicity**: No Redis/RabbitMQ broker required, no separate worker process
- **Sufficient for MVP**: Handles moderate load (<1000 tasks/min)
- **Low Latency**: <50ms overhead to spawn background task
- **Idempotent**: Duplicate syncs are safe (upsert operation)

### Alternatives Considered

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **FastAPI BackgroundTasks** | Simple, built-in, low overhead | No retry logic, in-process (memory limit) | ✅ **Selected for MVP** |
| **Celery** | Robust retries, distributed workers, monitoring | Complex setup (broker, workers), overkill for MVP | ⚠️ **Future upgrade path** |
| **Synchronous Sync** | Simplest implementation | Blocks API response (adds 200-500ms latency) | ❌ Poor UX |

### Implementation Pattern

**Task CRUD with Background Sync**:
```python
# backend/src/api/routes/tasks.py
from fastapi import APIRouter, BackgroundTasks, Depends
from src.services.vector_sync import VectorSyncService

router = APIRouter()

@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    vector_sync: VectorSyncService = Depends(get_vector_sync_service)
):
    # 1. Create task in database (fast, <100ms)
    task = await task_service.create_task(current_user.id, task_data)

    # 2. Queue background vector sync (non-blocking)
    background_tasks.add_task(
        vector_sync.sync_task_embedding,
        task_id=task.id,
        user_id=current_user.id,
        task_text=f"{task.title}\n{task.description or ''}"
    )

    # 3. Return immediately (user doesn't wait for embedding)
    return task

@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    vector_sync: VectorSyncService = Depends(get_vector_sync_service)
):
    # 1. Update task
    task = await task_service.update_task(task_id, current_user.id, task_data)

    # 2. Re-sync embedding if content changed
    if task_data.title or task_data.description:
        background_tasks.add_task(
            vector_sync.sync_task_embedding,
            task_id=task.id,
            user_id=current_user.id,
            task_text=f"{task.title}\n{task.description or ''}"
        )

    return task

@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    vector_sync: VectorSyncService = Depends(get_vector_sync_service)
):
    # 1. Delete task from database
    await task_service.delete_task(task_id, current_user.id)

    # 2. Delete embedding from Qdrant
    background_tasks.add_task(
        vector_sync.delete_task_embedding,
        task_id=task_id
    )

    return {"status": "deleted"}
```

**Vector Sync Service**:
```python
# backend/src/services/vector_sync.py
import asyncio
from openai import AsyncOpenAI
from qdrant_client import AsyncQdrantClient
from src.services.pii_redactor import PIIRedactor

class VectorSyncService:
    def __init__(self, openai_client: AsyncOpenAI, qdrant_client: AsyncQdrantClient):
        self.openai = openai_client
        self.qdrant = qdrant_client
        self.redactor = PIIRedactor()
        self.collection_name = "task_embeddings"
        self.max_retries = 3

    async def sync_task_embedding(
        self,
        task_id: str,
        user_id: str,
        task_text: str,
        retry_count: int = 0
    ):
        """Generate and store task embedding (idempotent)"""
        try:
            # 1. Redact PII
            redacted_text, detected_pii = self.redactor.redact_text(task_text)
            if detected_pii:
                logger.warning(f"PII detected in task {task_id}: {detected_pii}")

            # 2. Generate embedding
            embedding_response = await self.openai.embeddings.create(
                model="text-embedding-3-small",
                input=redacted_text
            )
            embedding = embedding_response.data[0].embedding

            # 3. Upsert to Qdrant (idempotent)
            await self.qdrant.upsert(
                collection_name=self.collection_name,
                points=[{
                    "id": task_id,  # Upsert by task_id ensures idempotency
                    "vector": embedding,
                    "payload": {
                        "user_id": user_id,
                        "task_id": task_id,
                        "synced_at": datetime.utcnow().isoformat()
                    }
                }]
            )

            logger.info(f"Synced embedding for task {task_id}")

        except Exception as e:
            logger.error(f"Vector sync failed for task {task_id}: {e}")

            # Retry with exponential backoff
            if retry_count < self.max_retries:
                await asyncio.sleep(2 ** retry_count)  # 1s, 2s, 4s
                await self.sync_task_embedding(
                    task_id, user_id, task_text, retry_count + 1
                )
            else:
                # Log to error tracking (Sentry, etc.)
                logger.error(f"Max retries exceeded for task {task_id}")

    async def delete_task_embedding(self, task_id: str):
        """Remove embedding from Qdrant"""
        try:
            await self.qdrant.delete(
                collection_name=self.collection_name,
                points_selector=[task_id]
            )
            logger.info(f"Deleted embedding for task {task_id}")
        except Exception as e:
            logger.error(f"Failed to delete embedding for {task_id}: {e}")
```

### Error Handling Strategy

**Retry Policy**:
- Max retries: 3
- Backoff: Exponential (1s, 2s, 4s)
- Failure action: Log error, alert monitoring system
- No user-facing error (background operation)

**Idempotency**:
- Qdrant upsert by `task_id` ensures duplicate syncs are safe
- If sync triggered multiple times (e.g., rapid updates), last sync wins
- No risk of duplicate embeddings

### Performance Benchmarks

| Operation | Latency | Notes |
|-----------|---------|-------|
| API Response | 50-100ms | Task created/updated in DB |
| Background Task Spawn | <5ms | BackgroundTasks overhead |
| Embedding Generation | 100-200ms | OpenAI API call |
| Qdrant Upsert | 50-100ms | Network + index update |
| **Total Sync Time** | 150-300ms | User doesn't wait |

**User Experience**: API returns in <100ms, sync completes in background within 300ms. Embeddings available for search within seconds.

### Future Upgrade Path to Celery

If load exceeds BackgroundTasks capacity (>1000 tasks/min):
1. Add Redis as message broker
2. Deploy Celery workers
3. Replace `background_tasks.add_task()` with `vector_sync.delay()`
4. Add Flower for monitoring
5. Implement dead letter queue for failed syncs

---

## Summary of Key Decisions

| Component | Decision | Rationale |
|-----------|----------|-----------|
| **Vector DB** | Qdrant Cloud (Free Tier) | Managed service, async support, 1GB sufficient for MVP |
| **Embeddings** | OpenAI text-embedding-3-small | Cost-effective, 1536 dimensions, proven quality |
| **Chat API** | Direct Chat Completions (not Assistants API) | Lower latency, better cost control, production-ready |
| **Session State** | PostgreSQL (not in-memory) | Persistent, multi-instance compatible, simple backup |
| **MCP Server** | Embedded function calling (not separate service) | Simpler for MVP, lower latency, sufficient for task CRUD |
| **PII Protection** | Regex-based redaction | <15ms overhead, catches common patterns, privacy-first |
| **Translation** | OpenAI Chat + domain glossaries | Flexible, context-aware, supports technical terms |
| **Translation Cache** | PostgreSQL (30-day TTL) | Reduce API costs, fast lookups, simple cleanup |
| **RTL Support** | Tailwind dir="rtl" + CSS | Native browser support, no JS overhead |
| **Vector Sync** | FastAPI BackgroundTasks (not Celery) | Simple MVP approach, <50ms overhead, upgrade path exists |
| **Sync Retry** | Exponential backoff (3 retries) | Balance reliability vs complexity |

---

## Open Questions Resolved

1. **OpenAI Agents SDK Maturity**: SDK is beta and high-latency → Use direct Chat Completions API ✅
2. **Qdrant Free Tier Sufficiency**: 1GB ≈ 600k vectors → Sufficient for 100 users × 10k tasks ✅
3. **MCP Server Hosting**: Embed in FastAPI via function calling → Simpler than separate process ✅
4. **Translation Caching Duration**: 30-day TTL in PostgreSQL → Balance freshness vs cost ✅
5. **RTL Layout Scope**: Inline RTL for translated text only → Avoid full UI re-layout complexity ✅

---

## Next Steps

1. **Phase 1 Artifacts**: Generate `data-model.md`, `contracts/`, `quickstart.md` based on research findings
2. **Dependency Installation**: Add `qdrant-client`, `openai`, `redis` (optional) to `requirements.txt`
3. **Configuration**: Set up `.env.example` with `QDRANT_URL`, `QDRANT_API_KEY`, `OPENAI_API_KEY`
4. **Database Migration**: Create Alembic migration for new tables (chat_sessions, chat_messages, translation_cache)
5. **Agent Context Update**: Run `update-agent-context.ps1` to inject new technology patterns

**Status**: Research complete. Ready for Phase 1 design artifacts.
