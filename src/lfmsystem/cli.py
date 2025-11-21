# src/lfmsystem/cli.py
import click
import inspect
import sys
from typing import List

# Import your system components
from lfmsystem.logging import setup_logging
from lfmsystem.registry import ToolRegistry
from lfmsystem.agent import LiquidAgent, SimpleBot
import lfmsystem.tools as tool_module  # Import the whole module to inspect it

# Default Model (Constant)
DEFAULT_MODEL = "hf.co/LiquidAI/LFM2-1.2B-Tool-GGUF:Q4_K_M"

def get_available_tools() -> dict:
    """
    Scans tools.py and returns a dict: {'func_name': function_object}
    """
    tools = {}
    for name, obj in inspect.getmembers(tool_module):
        # Only include functions defined in valid source code (skip imports like 'random')
        if inspect.isfunction(obj) and obj.__module__ == tool_module.__name__:
            tools[name] = obj
    return tools

AVAILABLE_TOOLS = get_available_tools()  # Lookup dict for valid tools

@click.group()
def main():
    """LFMSystem Command Line Interface."""
    pass

@main.command()
@click.option("--model", default=DEFAULT_MODEL, help="The Ollama model tag to use.")
@click.option("--verbose/--quiet", default=True, help="Enable verbose logging.")
@click.option(
    "--tool", "-t", 
    "selected_tools", 
    multiple=True, 
    type=click.Choice(list(AVAILABLE_TOOLS.keys())),
    help="Enable specific tools by name (can be used multiple times)."
)
@click.option("--all-tools", is_flag=True, help="Enable ALL available tools.")
def chat(model: str, verbose: bool, selected_tools: List[str], all_tools: bool):
    """
    Start a chat session with the agent.
    """
    # 1. Setup Environment
    setup_logging(use_cloud=True, verbose=verbose)
    
    # 2. Configure Tools
    registry = ToolRegistry()
    tools_to_load = []

    if all_tools:
        tools_to_load = list(AVAILABLE_TOOLS.keys())
    else:
        tools_to_load = selected_tools

    if tools_to_load:
        click.echo(click.style(f"🛠️  Loading tools: {', '.join(tools_to_load)}", fg="cyan"))
        for tool_name in tools_to_load:
            func = AVAILABLE_TOOLS[tool_name]
            registry.register(func)
            
        # Initialize Agent WITH tools
        # Pass model settings dynamically if needed
        agent = LiquidAgent(
            model_name=model, 
            registry=registry,
            temperature=0.3,
            min_p=0.15,
            repetition_penalty=1.05
        )
    else:
        click.echo(click.style("💬 Starting simple chat (No tools enabled)", fg="yellow"))
        # Initialize Bot WITHOUT tools
        agent = SimpleBot(
            model_name=model,
            temperature=0.3,
            min_p=0.15,
            repetition_penalty=1.05,
        )

    # 3. The Interaction Loop (REPL)
    click.echo(click.style(f"\n🤖 Agent ready ({model})\nType 'exit' or 'quit' to leave.\n", bold=True))
    
    while True:
        try:
            user_input = click.prompt(click.style("You", fg="green"), type=str)
            
            if user_input.lower() in ["exit", "quit"]:
                # ... exit logic ...
                break
                
            # CHANGE: Capture the return value
            response = agent.chat(user_input)
            
            # NEW: Explicitly print the response to the user
            # This ensures it shows up even in --quiet mode
            click.echo(f"\n{response}\n")
            
        except KeyboardInterrupt:
            click.echo("\nBye! 👋")
            break
        except Exception as e:
            click.echo(click.style(f"Error: {e}", fg="red"))

if __name__ == "__main__":
    main()