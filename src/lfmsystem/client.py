# src/lfmsystem/client.py
import ollama
import logfire
from loguru import logger
from typing import List, Dict, Any, Optional

class LLMClient:
    def __init__(self, model_name: str, options: Optional[Dict[str, Any]] = None):
        self.model_name = model_name
        self.options = options or {}

    def generate(self, messages: List[Dict[str, str]]) -> str:
        # Create a visual span in Logfire called "llm_generate"
        with logfire.span("llm_call", model=self.model_name) as span:
            try:
                logger.debug(f"Generating with {self.model_name}")
                
                response = ollama.chat(
                    model=self.model_name,
                    messages=messages,
                    options=self.options
                )
                
                content = response["message"]["content"]
                
                # Record the output length as a metric
                span.set_attribute("response_length", len(content))
                return content
                
            except Exception as e:
                logger.error(f"LLM Failed: {e}")
                span.record_exception(e) # Visualizes the error trace
                return f"LLM Error: {e}"