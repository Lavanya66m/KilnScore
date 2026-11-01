# KilnScore — System Design

## 1. Project Overview

KilnScore is an LLM-powered application designed to answer questions using a reliable language model architecture.

The application provides:
- LLM response streaming.
- Primary and fallback LLM provider support.
- Automatic retries for temporary provider failures.
- Token usage tracking.
- PostgreSQL-based usage persistence.
- Docker-based application deployment.

The current development setup uses a FakeProvider to test the application without requiring paid API access.

## 2. System Architecture

### Architecture Flow

```text
                Client
                  |
                  v
             FastAPI Server
                  |
          +-------+-------+
          |       |       |
          v       v       v
       /health  /chat   /usage
                  |       |
                  v       v
             LLM Factory  PostgreSQL
                  |
                  v
           Reliable LLM Layer
                  |
          +-------+-------+
          |               |
          v               v
     Primary Model   Fallback Model
          |
          v
      LLM Response
          |
          v
     Usage Tracking
          |
          v
      PostgreSQL
```

### Components

| Component | Responsibility |
|---|---|
| FastAPI | Handles HTTP requests and API endpoints |
| LLM Factory | Creates configured LLM providers |
| Reliable LLM | Handles retries and fallback |
| FakeProvider | Provides deterministic test responses |
| PostgreSQL | Stores token usage records |
| SQLAlchemy | Handles database operations |
| Docker | Runs API and database containers |

## 3. API Endpoints

### GET /health

Purpose: Checks whether the API application is running.

Example response:

```json
{
  "status": "ok",
  "app": "examate-rag",
  "environment": "docker"
}
```

### POST /chat

Purpose: Accepts chat messages and streams the LLM response using Server-Sent Events (SSE).

Request:

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Hello"
    }
  ],
  "model": "examate-fake"
}
```

Example streamed response:

```text
data: {"delta": "Hello"}

data: {"delta": " from the fake provider."}

event: done
data: {
  "response": {
    "answer": "Hello from the fake provider."
  },
  "usage": {
    "input_tokens": 0,
    "output_tokens": 2,
    "estimated": true
  }
}
```

### GET /usage

Purpose: Returns aggregated token usage and estimated cost.

Example response:

```json
{
  "total_requests": 4,
  "total_input_tokens": 0,
  "total_output_tokens": 8,
  "estimated_cost_usd": 0.0
}
```

## 4. Database Design

Database: PostgreSQL

Table: `usage_records`

| Column | Data Type | Description |
|---|---|---|
| id | Integer | Primary key |
| input_tokens | Integer | Input token count |
| output_tokens | Integer | Output token count |
| estimated | Boolean | Indicates whether usage is estimated |
| cost_usd | Float | Recorded estimated cost |
| created_at | DateTime | Record creation timestamp |

### Database Responsibilities

- Stores successful chat request usage.
- Maintains token usage history.
- Supports aggregate usage queries.
- Preserves records across API container restarts using a Docker volume.

## 5. LLM Reliability Design

The application uses a reliable LLM layer.

### Retry Mechanism

Temporary failures such as HTTP 429 and 5xx errors can trigger retries.

### Fallback Mechanism

If the primary provider fails before producing partial output, the application can attempt the configured fallback provider.

### Error Handling

The application handles:
- Provider errors.
- Authentication and configuration errors.
- Network failures.
- Request timeouts.

## 6. Docker Deployment Architecture

The application uses Docker Compose with two services.

| Service | Image | Purpose |
|---|---|---|
| api | Custom Python image | Runs FastAPI |
| db | pgvector/pgvector:pg16 | Runs PostgreSQL |

### Docker Networking

The API connects to PostgreSQL using the Docker service hostname:

`db:5432`

### Persistent Storage

A named Docker volume called `postgres_data` stores PostgreSQL data.

This allows database records to remain available when containers are restarted.

## 7. Usage and Cost Tracking

The application records:
- Input tokens.
- Output tokens.
- Whether token counts are estimated.
- Estimated cost in USD.

Current development setup:
- Uses FakeProvider.
- Token usage is estimated.
- Cost is currently recorded as zero.
- Actual provider billing and pricing-based cost calculation are not yet implemented.

## 8. Future Improvements

- Implement pricing-based token cost calculation.
- Add authentication and authorization.
- Add database migrations using Alembic.
- Add more LLM providers.
- Add monitoring and structured logging.
- Deploy the application to a free hosting platform.
- Improve automated integration testing.

## 9. Technology Stack

- **Language:** Python
- **Backend:** FastAPI
- **LLM Integration:** Custom LLM Provider Architecture
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Containerization:** Docker and Docker Compose
- **Testing:** Pytest
- **Code Quality:** Ruff
