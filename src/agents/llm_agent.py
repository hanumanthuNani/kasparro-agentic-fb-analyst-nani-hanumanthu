# src/agents/llm_agent.py

import os
import json
import google.generativeai as genai


class LLMAgent:
    """
    Gemini-powered universal LLM Agent.
    Handles:
    - Safe text extraction
    - Strict JSON structured output
    - Gemini incomplete responses (finish_reason = 2)
    """

    def __init__(self,
                 model="models/gemini-2.0-flash",
                 temperature=0.2,
                 max_tokens=800):

        self.model_name = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise EnvironmentError("GOOGLE_API_KEY environment variable is missing.")

        genai.configure(api_key=api_key)

        # Load model
        self.model = genai.GenerativeModel(self.model_name)

    # -----------------------------------------------------------
    # INTERNAL SAFE TEXT EXTRACTION
    # -----------------------------------------------------------
    def _safe_extract_text(self, response):
        """
        Gemini sometimes:
        - does NOT populate response.text
        - stores output inside candidates[x].content.parts[x].text
        """

        # 1) try candidates[0]
        try:
            parts = response.candidates[0].content.parts
            for p in parts:
                if hasattr(p, "text") and p.text:
                    return p.text.strip()
        except:
            pass

        # 2) fallback to response.text
        try:
            if hasattr(response, "text") and response.text:
                return response.text.strip()
        except:
            pass

        # 3) absolute fallback
        raise RuntimeError("Gemini returned no usable text content.")

    # -----------------------------------------------------------
    # BASIC TEXT OUTPUT
    # -----------------------------------------------------------
    def call(self, system_prompt: str, user_prompt: str):
        prompt = f"{system_prompt}\n\nUser: {user_prompt}"

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": self.temperature,
                    "max_output_tokens": self.max_tokens
                }
            )
            return self._safe_extract_text(response)

        except Exception as e:
            raise RuntimeError(f"Gemini LLM call failed: {e}")

    # -----------------------------------------------------------
    # STRICT JSON GENERATION
    # -----------------------------------------------------------
    def structured(self, system_prompt: str, user_prompt: str, json_schema: dict):

        enforce = (
            "\n\nReturn ONLY valid JSON following this schema:\n"
            f"{json.dumps(json_schema)}\n"
            "No explanations. No comments. No markdown. Only JSON."
        )

        full_prompt = system_prompt + "\n\n" + user_prompt + enforce

        try:
            response = self.model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": self.temperature,
                    "max_output_tokens": self.max_tokens
                }
            )

            text = self._safe_extract_text(response)

            # CLEAN ACCIDENTAL MARKDOWN
            text = text.replace("```json", "").replace("```", "").strip()

            return text

        except Exception as e:
            raise RuntimeError(f"Gemini structured JSON failed: {e}")
