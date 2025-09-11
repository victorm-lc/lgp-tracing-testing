# LangGraph Multi-Workspace Tracing

A LangGraph agent that routes LangSmith traces to different workspaces based on configuration. Perfect for multi-tenant applications or testing across different environments.

## Overview

Route the same agent to different LangSmith workspaces by setting `workspace_id` in the configuration:

```python
config = {
    "configurable": {
        "workspace_id": "workspace_a"  # Routes to workspace A
    }
}
```

## Quick Start with UV

### Prerequisites
- Python 3.11+
- [UV package manager](https://docs.astral.sh/uv/)
- LangSmith account with cross-workspace API key

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd lgp-tracing-alternate-workspace

# Install dependencies with UV
uv sync
```

### 2. Environment Configuration

Create a `.env` file in the project root:

```bash
# .env
LS_CROSS_WORSKPACE_KEY=your_langsmith_api_key_here
```

**Important**: Use a LangSmith API key that has access to multiple workspaces.

### 3. Update Workspace IDs

Edit `agent.py` and replace the workspace IDs with your actual workspace IDs:

```python
workspace_a_client = Client(
    api_key=api_key,
    api_url="https://api.smith.langchain.com",
    workspace_id="your-workspace-a-id-here"  # Replace with your workspace A ID
)
workspace_b_client = Client(
    api_key=api_key,
    api_url="https://api.smith.langchain.com", 
    workspace_id="your-workspace-b-id-here"  # Replace with your workspace B ID
)
```

### 4. Run the Agent

```bash
# Activate the UV environment
uv run langgraph dev
```

The agent will start on `http://localhost:8123` (or the port specified by LangGraph).

### 5. Test Workspace Routing

Open LangGraph Studio at `http://localhost:8123` and test different workspaces:

1. **In the Studio interface**, set the configuration:
   - For Workspace A: `{"configurable": {"workspace_id": "workspace_a"}}`
   - For Workspace B: `{"configurable": {"workspace_id": "workspace_b"}}`
   - Default: `{"configurable": {}}` (falls back to workspace A)

2. **Run the agent** and check your LangSmith workspaces to see traces appearing in the correct workspace.

## Project Structure

```
lgp-tracing-alternate-workspace/
├── agent.py              # Main LangGraph agent with workspace routing
├── example.py             # FastAPI example for reference
├── langgraph.json         # LangGraph configuration
├── pyproject.toml         # UV project configuration
├── .env                   # Environment variables (create this)
└── README.md             # This file
```

## How It Works

The agent uses a configuration-driven approach to route traces:

1. **Configuration**: Set `workspace_id` in the configurable parameters
2. **Client Selection**: Agent selects the appropriate LangSmith client based on workspace_id
3. **Tracing Context**: All operations are traced to the selected workspace using `tracing_context`

### Core Logic
```python
workspace_id = config.get("configurable", {}).get("workspace_id", "workspace_a")

if workspace_id == "workspace_a":
    client = workspace_a_client
    project_name = "test-agent-a"
elif workspace_id == "workspace_b":
    client = workspace_b_client
    project_name = "test-agent-b"

with tracing_context(enabled=True, client=client, project_name=project_name):
    yield base_graph
```

## Deployment

### LangGraph Platform Deployment

When deploying to LangGraph Platform:

1. **Set Environment Variables**: Configure `LS_CROSS_WORSKPACE_KEY` in your deployment environment and make sure that the key has access to the necessary workspaces.


### Package Configuration

The project is configured for proper deployment with:
- `pyproject.toml`: Specifies only the `agent.py` module for packaging

This prevents the "Multiple top-level modules" error during deployment.

## Adding New Workspaces

1. Create a new LangSmith client in `agent.py`:
```python
workspace_c_client = Client(
    api_key=api_key,
    api_url="https://api.smith.langchain.com", 
    workspace_id="your-workspace-c-id"
)
```

2. Add routing logic in the `graph` function:
```python
elif workspace_id == "workspace_c":
    client = workspace_c_client
    project_name = "test-agent-c"
```

## Troubleshooting

- **Authentication Error**: Ensure your API key has access to all target workspaces
- **Workspace Not Found**: Verify workspace IDs are correct in `agent.py`
- **Tracing Not Working**: Check that `LS_CROSS_WORSKPACE_KEY` is set in your `.env` file
