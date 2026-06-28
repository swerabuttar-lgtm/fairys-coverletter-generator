"""
Thin wrapper around the Gemini streaming API. Keeping this isolated means
swapping providers later only touches this one file.
"""
import os
from typing import Iterator
from google import genai

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
MODEL = "gemini-2.5-flash"

def stream_cover_letter(system_prompt: str, user_prompt: str) -> Iterator[str]:
    """
    Opens a streaming generate_content call and yields text chunks as they arrive.
    Gemini doesn't take a separate system param in the same way, so we prepend
    the system prompt to the user prompt separated clearly.
    """
    full_prompt = f"{system_prompt}\n\n{user_prompt}"

    response = client.models.generate_content_stream(
        model=MODEL,
        contents=full_prompt,
    )
    for chunk in response:
        if chunk.text:
            yield chunk.text


def generate_cover_letter(system_prompt: str, user_prompt: str) -> str:
    """
    Non-streaming version — collects the full response and returns it as one string.
    Used by the /generate endpoint so we can also return word count.
    """
    full_prompt = f"{system_prompt}\n\n{user_prompt}"

    response = client.models.generate_content(
        model=MODEL,
        contents=full_prompt,
    )
    return response.text