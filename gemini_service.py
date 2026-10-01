from google import genai
import os
import asyncio

# Get API key from environment variable
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is not set. "
        "Set it in PowerShell before starting Uvicorn."
    )

client = genai.Client(api_key=api_key)


# Models are tried in this order.
# If one is temporarily unavailable, EduGenie tries the next one.
MODELS = [
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.8-flash",
]


async def generate_response(prompt: str) -> str:

    for model in MODELS:

        try:

            print(f"Trying Gemini model: {model}")

            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            print(f"Success with model: {model}")

            return response.text

        except Exception as e:

            error_message = str(e)

            print(
                f"Error with {model}: "
                f"{error_message}"
            )

            # Try another model when Gemini is temporarily unavailable
            if (
                "503" in error_message
                or "UNAVAILABLE" in error_message
            ):

                print(
                    f"{model} is temporarily unavailable. "
                    "Trying next model..."
                )

                await asyncio.sleep(1)

                continue

            # Other errors should be returned directly
            return (
                "Gemini API error:\n\n"
                + error_message
            )

    return (
        "All Gemini models are temporarily unavailable. "
        "Please try again after a few minutes."
    )