
import pytest

from app.llm.errors import LLMConfigurationError, LLMUnavailable
from app.llm.fake import FakeProvider
from app.llm.reliable import AsyncReliableLLM
from app.llm.types import (
    LLMRequest,
    Message,
    ProviderError,
    TextChunk,
)

REQUEST = LLMRequest(
    messages=(Message(role="user", content="Say hello"),),
    model="fake-model",
)


class AsyncSequenceProvider:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = 0

    async def stream_async(self, request):
        self.calls += 1
        outcome = self.outcomes[min(self.calls - 1, len(self.outcomes) - 1)]

        if isinstance(outcome, Exception):
            raise outcome

        for chunk in outcome:
            yield chunk


@pytest.mark.anyio
async def test_async_retries_transient_errors_then_succeeds():
    provider = AsyncSequenceProvider(
        [
            ProviderError("busy", status_code=503),
            [TextChunk("success")],
        ]
    )

    llm = AsyncReliableLLM(provider, primary_retries=2)

    chunks = [chunk async for chunk in llm.stream(REQUEST)]

    assert "".join(chunk.text for chunk in chunks) == "success"
    assert provider.calls == 2


@pytest.mark.anyio
async def test_async_fallback_runs_after_primary_failure():
    primary = AsyncSequenceProvider(
        [ProviderError("provider down", status_code=503)]
    )
    fallback = FakeProvider(chunks=("fallback",))

    llm = AsyncReliableLLM(
        primary,
        fallback=fallback,
        primary_retries=1,
    )

    chunks = [chunk async for chunk in llm.stream(REQUEST)]

    assert "".join(chunk.text for chunk in chunks) == "fallback"
    assert primary.calls == 2
    assert fallback.calls == 1


@pytest.mark.anyio
async def test_async_authentication_error_is_not_retried():
    primary = AsyncSequenceProvider(
        [ProviderError("invalid API key", status_code=401)]
    )

    llm = AsyncReliableLLM(primary, primary_retries=3)

    with pytest.raises(LLMConfigurationError):
        _ = [chunk async for chunk in llm.stream(REQUEST)]

    assert primary.calls == 1


@pytest.mark.anyio
async def test_async_partial_output_does_not_trigger_fallback():
    class PartialFailure:
        calls = 0

        async def stream_async(self, request):
            self.calls += 1
            yield TextChunk("partial")
            raise ProviderError("connection lost")

    primary = PartialFailure()
    fallback = FakeProvider(chunks=("fallback",))

    llm = AsyncReliableLLM(primary, fallback=fallback)

    with pytest.raises(LLMUnavailable):
        _ = [chunk async for chunk in llm.stream(REQUEST)]

    assert primary.calls == 1
    assert fallback.calls == 0
