import inspect
import json
from typing import Callable, Dict, List, Any
from pydantic import validate_call

class ToolRegistry:
    def __init__(self):
        self.tools_map: Dict[str, Callable] = {}
        self.schemas: List[dict] = []

    def register(self, func: Callable) -> Callable:
        """Decorator to register a tool and generate its schema."""
        self.tools_map[func.__name__] = func
        
        # Inspect function signature for schema generation
        sig = inspect.signature(func)
        parameters = {"type": "object", "properties": {}, "required": []}
        
        for name, param in sig.parameters.items():
            # Simple type mapping
            param_type = "string"
            if param.annotation == int: param_type = "integer"
            if param.annotation == bool: param_type = "boolean"
            
            parameters["properties"][name] = {
                "type": param_type, 
                "description": f"Argument: {name}"
            }
            
            if param.default == inspect.Parameter.empty:
                parameters["required"].append(name)

        schema = {
            "name": func.__name__,
            "description": func.__doc__.strip().split('\n')[0] if func.__doc__ else "No description",
            "parameters": parameters
        }
        self.schemas.append(schema)
        
        return validate_call(func) # Add validation

    def get_tools_json(self) -> str:
        """Returns the minified JSON string required by LiquidAI."""
        return json.dumps(self.schemas)
    
    def execute(self, tool_call_str: str) -> str:
        """Executes the tool string safely."""
        try:
            # Restrict execution scope to registered tools only
            result = eval(tool_call_str, {"__builtins__": None}, self.tools_map)
            return str(result)
        except Exception as e:
            return f"Tool Execution Error: {e}"