import ollama
from typing import List, Dict, Any, Optional

class LLMClient:
    def __init__(self, model_name: str, options: Optional[Dict[str, Any]] = None):
        """
        Args:
            model_name: The Ollama model tag.
            options: The generation parameters (temp, min_p, etc.)
        """
        self.model_name = model_name
        # Default to empty dict if nothing provided
        self.options = options or {}

    def generate(self, messages: List[Dict[str, str]]) -> str:
        """
        Sends messages to Ollama using the configured options.
        """
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                options=self.options  
            )
            return response["message"]["content"]
        except Exception as e:
            return f"LLM Error: {e}"