import pytest
from unittest.mock import MagicMock, patch
from lfmsystem.agent import LiquidAgent
from lfmsystem.registry import ToolRegistry

# Setup a fixture for re-use
@pytest.fixture
def mock_registry():
    reg = ToolRegistry()
    @reg.register
    def get_test_data(id: str) -> str:
        return f"Data for {id}"
    return reg

@patch("lfmsystem.agent.LLMClient") # mock the client class inside agent.py
def test_agent_workflow_with_tool(MockClientClass, mock_registry):
    """
    Test the full ReAct loop: User -> LLM (Tool Call) -> Code -> LLM (Final)
    """
    # 1. Setup Mocks
    mock_client_instance = MockClientClass.return_value
    
    # We need to simulate TWO responses from the LLM:
    # Turn 1: The agent decides to use the tool
    # Turn 2: The agent sees the result and gives the answer
    mock_client_instance.generate.side_effect = [
        "<|tool_call_start|>[get_test_data(id='123')]<|tool_call_end|>", # 1st response
        "Here is the data for 123."                                       # 2nd response
    ]

    # 2. Initialize Agent
    agent = LiquidAgent("dummy-model", mock_registry)
    
    # 3. Run Chat
    response = agent.chat("Get data for 123")
    
    # --- ADJUDICATION ---
    
    # Assert final response matches our 2nd mock
    assert response == "Here is the data for 123."
    
    # Check if tool was actually executed in registry
    # (We rely on the registry logic, which we tested in test_tools.py)
    
    # Check History Integrity (Crucial!)
    # The history should have 5 messages:
    # 1. System Prompt
    # 2. User: "Get data..."
    # 3. Asst: "<|tool_call...>"
    # 4. User: "<|tool_response...>Data for 123<|...>"
    # 5. Asst: "Here is the data..."
    assert len(agent.history) == 5
    assert "<|tool_response_start|>Data for 123" in agent.history[3]["content"]

def test_agent_no_tool_trigger(mock_registry):
    """Test a standard chat without tools"""
    with patch("lfmsystem.agent.LLMClient") as MockClientClass:
        mock_client_instance = MockClientClass.return_value
        mock_client_instance.generate.return_value = "Just a normal answer."
        
        agent = LiquidAgent("dummy-model", mock_registry)
        response = agent.chat("Hi")
        
        # Should only call generate once
        assert mock_client_instance.generate.call_count == 1
        assert response == "Just a normal answer."