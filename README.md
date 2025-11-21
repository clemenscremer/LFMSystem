# Local Liquid Foundation Models via Ollama

## Requirements

## Environment setup

You will need

- Python $\ge$ 3.12.
- [Ollama](https://ollama.com), Or use Homebrew (on Mac)
`brew install ollama` to serve the Language Models locally. 
- [uv](https://docs.astral.sh/uv/) to manage Python dependencies and run the application efficiently without creating virtual environments manually.
- install everyting locally via `uv pip install -e .`

## Download models

They will be stored under ~/.ollama/models/.

- using mostly https://huggingface.co/LiquidAI/LFM2-8B-A1B in Q4_K_M version here
- `ollama list` : lists all installed models
- https://github.com/ollama/ollama-python
- if online logging is desired log in with logfire use `uv run logfire auth` to login. Otherwise turn cloud based logging off via `setup_logging(use_cloud=False)`

## Getting started
* explore the examples in `/notebooks/playground.ipynb`
* Start a chat in the command line via `lfmsystem chat`
* Chat with tool use (see tool definitions in src/lfmsystem/tools.py) via `lfmsystem chat --all-tools` or just selected tools `lfmsystem chat --tool get_weather --tool get_current_time`
* Select depth of logging via `lfmsystem chat --verbose` or `lfmsystem chat --quiet`
* All configuration options
    * --model: Specify the Ollama model tag to use. Default: hf.co/LiquidAI/LFM2-1.2B-Tool-GGUF:Q4_K_M
    * --tool / -t: Name of a tool to enable (repeatable).	Default: None
    * --all-tools: Load all tools from library (tools.py). Default: False
    * --verbose / --quiet: Toggle terminal log output. Even in quiet mode traces are sent to logfire. Default: Verbose


## Structure

```
LFMSystem/
├── pyproject.toml        # Dependencies and whatnot
├── src/
│   └── lfmsystem/        
│       ├── __init__.py
│       ├── logging.py    # sets up logging with logfire and loguru
│       ├── client.py     # Handles Ollama & Model Settings
│       ├── cli.py        # Provides command line interface for chatting and tool use
│       ├── registry.py   # The Tool Manager
│       ├── tools.py      # Tool definitions
│       └── agent.py      # The Chatbot & Agent logic (This integrates the client and registry.)
├── tests/
│   ├── __init__.py
│   ├── test_tools.py     # Testing your python functions
│   └── test_agent.py     # Testing the bot logic (with mocks)
└── notebooks/
    └── playground.ipynb  # solely for illustration and testing
```


## Testing 

- `uv run pytest`to run all tests
- `uv run pytest tests/test_agent.py -v`to just run the agent logic (This proves that IF the Liquid model outputs the correct regex, your python code WILL catch it and handle the loop correctly. This isolates errors in your code from errors in the model's intelligence.)