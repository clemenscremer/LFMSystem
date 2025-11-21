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
        self.history.append({"role": "user", "content": user_input})
        
        # Safety limit: Prevent infinite loops if model goes crazy
        max_turns = 5
        current_turn = 0
        
        while current_turn < max_turns:
            # 1. Ask LLM what to do
            response_content = self.client.generate(self.history)
            
            # 2. check if it wants to use a tool
            tool_result = self._check_for_tools(response_content)
            
            if tool_result:
                # It wants to use a tool!
                
                # A. Log it so the LLM remembers it made the call
                self.history.append({"role": "assistant", "content": response_content})
                
                # B. Add the Result to history
                # We add a hint text to nudge the small model towards answering
                tool_msg = (
                    f"<|tool_response_start|>{tool_result}<|tool_response_end|>"
                    " (Use this result to answer the user's question)"
                )
                self.history.append({"role": "user", "content": tool_msg})
                
                # C. Loop back! 
                # The 'while' loop will run generate() again with this new history.
                current_turn += 1
                continue 
            
            else:
                # No tool call detected -> This is the final text answer
                self.history.append({"role": "assistant", "content": response_content})
                logger.debug(f"🤖 Answer: {response_content}")
                return response_content
        
        # Fallback if it exceeds max_turns
        return "Error: Agent got stuck in a loop and could not produce an answer."


    def _check_for_tools(self, content: str) -> Optional[str]:
        pattern = r"<\|tool_call_start\|>\[(.*?)\]<\|tool_call_end\|>"
        match = re.search(pattern, content)
        if match:
            return self.registry.execute(match.group(1))
        return None