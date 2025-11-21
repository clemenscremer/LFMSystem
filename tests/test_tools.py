import pytest
from lfmsystem.tools import get_current_time, calculate_bmi
from lfmsystem.registry import ToolRegistry

# --- 1. Testing Pure Functions ---
def test_calculate_bmi():
    result = calculate_bmi(70, 1.75)
    assert "BMI is 22.86" in result

def test_calculate_bmi_error():
    result = calculate_bmi(70, 0)
    assert "Error" in result

# --- 2. Testing the Registry Logic ---
def test_registry_execution():
    registry = ToolRegistry()
    
    # Register a dummy function locally for testing
    @registry.register
    def add(a: int, b: int) -> int:
        """Adds two numbers"""
        return a + b
        
    # Check JSON Schema Generation
    json_str = registry.get_tools_json()
    assert "add" in json_str
    assert "Adds two numbers" in json_str
    
    # Check Execution Logic
    # We simulate the EXACT string the LLM would output
    result = registry.execute("add(a=5, b=10)")
    assert result == "15"

def test_registry_security():
    registry = ToolRegistry()
    
    # Try to execute a dangerous import that wasn't registered
    result = registry.execute("__import__('os').system('echo hack')")
    
    # It should fail because __import__ is not in the local scope
    assert "Error" in result or "name '__import__' is not defined" in result