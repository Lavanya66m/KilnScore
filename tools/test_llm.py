import asyncio

from app.config import get_settings
from app.llm.factory import create_provider
from app.llm.types import LLMRequest, Message


async def main():
    settings = get_settings()
    provider = create_provider(settings)

    request = LLMRequest(
        messages=(
            Message(
                role="user",
                content="Reply with exactly: Gemini connection successful",
            ),
        ),
        model=settings.llm_model,
    )

    print("Testing provider...")
    print("Model:", settings.llm_model)

    async for chunk in provider.stream(request):
        if chunk.text:
            print(chunk.text, end="", flush=True)

    print("\nTest completed.")


if __name__ == "__main__":
    asyncio.run(main())