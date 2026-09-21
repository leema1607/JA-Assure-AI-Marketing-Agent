import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is missing. Put it in .env.")
        self.client = genai.Client(api_key=api_key)
        self.model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

    def generate(self, prompt: str, use_search: bool = False) -> str:
        tools = []
        if use_search:
            tools = [types.Tool(google_search=types.GoogleSearch())]

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.4,
                    max_output_tokens=3000,
                    tools=tools,
                ),
            )
            return response.text or ""
        except Exception as e:
            print(f"\nGEMINI GENERATE ERROR: {type(e).__name__}: {e}\n")
            raise RuntimeError(f"Gemini unavailable: {e}") from e

    def json_generate(self, prompt: str) -> dict:
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=3000,
                    response_mime_type="application/json",
                ),
            )

            try:
                return json.loads(response.text)
            except Exception:
                return {"raw": response.text or ""}

        except Exception as e:
            print(f"\nGEMINI JSON ERROR: {type(e).__name__}: {e}\n")
            return {}
        
