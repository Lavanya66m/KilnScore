
import json
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.responses import StreamingResponse
from sqlalchemy import func

from app.config import Settings, get_settings
from app.database import SessionLocal
from app.llm.errors import LLMConfigurationError, LLMUnavailable
from app.llm.factory import create_provider
from app.llm.reliable import AsyncReliableLLM
from app.llm.types import LLMRequest, Message
from app.models import UsageRecord
from app.retrieval import retrieve_chunks
from app.schemas import (
    AskRequest,
    AskResponse,
    ChatRequest,
    ChatResponse,
    Citation,
    UsageResponse,
    UsageSummary,
)

app = FastAPI(title="Examate RAG starter", version="0.1.0")

SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_llm(settings: SettingsDep) -> AsyncReliableLLM:
    return create_provider(settings)


LLMDep = Annotated[AsyncReliableLLM, Depends(get_llm)]


@app.get("/hello")
def say_hello():
    return "hello"


@app.get("/")
def say_root():
    return "You are on root page"


@app.get("/health")
def health(settings: SettingsDep) -> dict:
    """Liveness: the process is up. Must be fast and must not call the LLM or DB."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment,
    }


@app.get("/usage", response_model=UsageSummary)
def get_usage():
    with SessionLocal() as db:
        total_requests = db.query(func.count(UsageRecord.id)).scalar() or 0
        total_input_tokens = (
            db.query(func.coalesce(func.sum(UsageRecord.input_tokens), 0)).scalar()
        )
        total_output_tokens = (
            db.query(func.coalesce(func.sum(UsageRecord.output_tokens), 0)).scalar()
        )
        estimated_cost = (
            db.query(func.coalesce(func.sum(UsageRecord.cost_usd), 0.0)).scalar()
        )

    return UsageSummary(
        total_requests=total_requests,
        total_input_tokens=total_input_tokens,
        total_output_tokens=total_output_tokens,
        estimated_cost_usd=float(estimated_cost),
    )


def sse(data: dict, event: str | None = None) -> str:
    prefix = f"event: {event}\n" if event else ""
    return f"{prefix}data: {json.dumps(data)}\n\n"


@app.post("/chat")
async def chat(request: ChatRequest, provider: LLMDep) -> StreamingResponse:
    llm_request = LLMRequest(
        messages=tuple(
            Message(role=message.role, content=message.content)
            for message in request.messages
        ),
        model=request.model,
    )

    async def event_stream() -> AsyncIterator[str]:
        answer_parts: list[str] = []
        usage = None

        try:
            async for chunk in provider.stream(llm_request):
                if chunk.text:
                    answer_parts.append(chunk.text)
                    yield sse({"delta": chunk.text})

                if chunk.usage is not None:
                    usage = chunk.usage

        except (LLMUnavailable, LLMConfigurationError) as error:
            yield sse({"error": str(error)}, event="error")
            return

        response = ChatResponse(answer="".join(answer_parts))
        usage_response = UsageResponse(
            input_tokens=usage.input_tokens if usage else 0,
            output_tokens=usage.output_tokens if usage else 0,
            estimated=usage.estimated if usage else True,
        )

        # Save successful request usage in PostgreSQL.
        with SessionLocal() as db:
            record = UsageRecord(
                input_tokens=usage_response.input_tokens,
                output_tokens=usage_response.output_tokens,
                estimated=usage_response.estimated,
                cost_usd=0.0,
            )
            db.add(record)
            db.commit()

        yield sse(
            {
                "response": response.model_dump(),
                "usage": usage_response.model_dump(),
            },
            event="done",
        )

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
    )


@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest, provider: LLMDep):
    # Step 1: Retrieve relevant chunks from PostgreSQL.
    chunks = retrieve_chunks(request.question, limit=5)

    if not chunks:
        return AskResponse(
            question=request.question,
            answer="I could not find relevant information in the documents.",
            citations=[],
        )

    # Step 2: Build context with document and page details.
    context = "\n\n".join(
        (
            f"Document: {chunk['document']}\n"
            f"Page: {chunk['page']}\n"
            f"Content: {chunk['content']}"
        )
        for chunk in chunks
    )

    # Step 3: Prepare the LLM request.
    llm_request = LLMRequest(
        messages=(
            Message(
                role="system",
                content=(
                    "You are a document-based assistant. "
                    "Answer using only the supplied context. "
                    "If the answer is not present, say so. "
                    "Do not invent facts or citations. "
                    "Mention the document page when relevant."
                ),
            ),
            Message(
                role="user",
                content=(
                    f"Context:\n{context}\n\n"
                    f"Question: {request.question}"
                ),
            ),
        ),
        model=get_settings().llm_model,
    )

    # Step 4: Collect the streamed LLM response.
    answer_parts = []

    async for chunk in provider.stream(llm_request):
        if chunk.text:
            answer_parts.append(chunk.text)

    answer = "".join(answer_parts)

    # Step 5: Prepare citations.
    citations = [
        Citation(
            document=chunk["document"],
            page=chunk["page"],
        )
        for chunk in chunks
    ]

    # Step 6: Return the final response.
    return AskResponse(
        question=request.question,
        answer=answer,
        citations=citations,
    )
