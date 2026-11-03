import asyncio

from google import genai

from app.config import get_settings


async def main():
    get_settings.cache_clear()
    settings = get_settings()

    client = genai.Client(api_key=settings.llm_api_key)

    try:
        response = await asyncio.to_thread(
            client.models.generate_content,
            model="gemini-3.6-flash",
            contents="Reply with exactly: API connection successful",
        )
        print("Gemini response:", response.text)
    except Exception as error:
        print("Error type:", type(error).__name__)
        print("Error:", str(error)[:500])
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(main())