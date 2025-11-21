import re
import logfire
from loguru import logger
from typing import Optional
from .client import LLMClient
from .registry import ToolRegistry

class SimpleBot:
    """A basic conversational bot without tools."""
    def __init__(self, model_name: str, system_prompt: str = "You are a helpful assistant.", **client_opts):
        # Initialize client with the extra options (temperature, min_p, etc.)
        self.client = LLMClient(model_name, options=client_opts)
        self.history = [{"role": "system", "content": system_prompt}]

    def chat(self, user_input: str) -> str:
        self.history.append({"role": "user", "content": user_input})
        response = self.client.generate(self.history)
        self.history.append({"role": "assistant", "content": response})
        return response

class LiquidAgent(SimpleBot):
    """An agent that can use tools defined in a ToolRegistry."""
    def __init__(self, model_name: str, registry: ToolRegistry, **client_opts):
        self.registry = registry
        agent_prompt = f"List of tools: <|tool_list_start|>{registry.get_tools_json()}<|tool_list_end|>"
        super().__init__(model_name, system_prompt=agent_prompt, **client_opts)

    def chat(self, user_input: str) -> str:
        # The PARENT span
        with logfire.span("agent_turn", input=user_input):
            
            self.history.append({"role": "user", "content": user_input})
            
            # 1. Initial generation
            initial_content = self.client.generate(self.history)
            
            # 2. Check Tools
            tool_result = self._check_for_tools(initial_content)
            
            if tool_result:
                self.history.append({"role": "assistant", "content": initial_content})
                
                tool_msg = f"<|tool_response_start|>{tool_result}<|tool_response_end|>"
                self.history.append({"role": "user", "content": tool_msg})
                
                # 3. Final Synthesis
                final_response = self.client.generate(self.history)
                self.history.append({"role": "assistant", "content": final_response})
                
                logger.info(f"🤖 Answer: {final_response}")
                return final_response
            
            else:
                self.history.append({"role": "assistant", "content": initial_content})
                logger.info(f"🤖 Answer: {initial_content}")
                return initial_content

    def _check_for_tools(self, content: str) -> Optional[str]:
        pattern = r"<\|tool_call_start\|>\[(.*?)\]<\|tool_call_end\|>"
        match = re.search(pattern, content)
        if match:
            return self.registry.execute(match.group(1))
        return None