# LangGraph Multi-Workspace Tracing

A LangGraph agent that demonstrates dynamic workspace routing for LangSmith tracing. This allows you to trace the same agent to different LangSmith workspaces based on configuration.

## Overview

This project shows how to:
- Route LangSmith traces to different workspaces dynamically
- Use LangGraph's configuration system for workspace selection
- Deploy agents that can serve multiple tenants/workspaces

## Architecture

The agent uses a single LangSmith API key with cross-workspace permissions to route traces to different workspaces based on the `workspace_id` configuration parameter.

```python
# Configuration drives workspace routing
config = {
    "configurable": {
        "workspace_id": "workspace_a"  # or "workspace_b"
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

### 5. Test Different Workspaces

You can test the workspace routing by sending requests with different configurations:

**Workspace A:**
```python
config = {
    "configurable": {
        "workspace_id": "workspace_a"
    }
}
```

**Workspace B:**
```python
config = {
    "configurable": {
        "workspace_id": "workspace_b"
    }
}
```

**Default (falls back to workspace A):**
```python
config = {
    "configurable": {}
}
```

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

1. **Configuration Schema**: The agent defines a `Configuration` TypedDict that specifies the expected configuration parameters.

2. **Dynamic Client Selection**: Based on the `workspace_id` in the configuration, the agent selects the appropriate LangSmith client.

3. **Tracing Context**: Uses `tracing_context` to set the LangSmith client and project name for the duration of the graph execution.

4. **Graph Execution**: All traces generated during graph execution are automatically routed to the selected workspace.

## Key Components

### Configuration Schema
```python
class Configuration(TypedDict):
    workspace_id: str
```

### Workspace Routing Logic
```python
@contextlib.asynccontextmanager
async def graph(config):
    workspace_id = config.get("configurable", {}).get("workspace_id", "workspace_a")
    
    if workspace_id == "workspace_a":
        client = workspace_a_client
        project_name = "math-agent-a"
    elif workspace_id == "workspace_b":
        client = workspace_b_client
        project_name = "math-agent-b"
    else:
        client = workspace_a_client
        project_name = "math-agent-default"
    
    with tracing_context(enabled=True, client=client, project_name=project_name):
        yield base_graph
```

## Deployment

### LangGraph Cloud Deployment

When deploying to LangGraph Cloud:

1. **Set Environment Variables**: Configure `LS_CROSS_WORSKPACE_KEY` in your deployment environment
2. **Update Workspace IDs**: Replace the workspace IDs in `agent.py` with your actual workspace IDs
3. **Deploy**: Use `langgraph deploy`

```bash
# Deploy to LangGraph Cloud
langgraph deploy
```

### Package Configuration

The project is configured for proper deployment with:
- `pyproject.toml`: Specifies only the `agent.py` module for packaging

This prevents the "Multiple top-level modules" error during deployment.

## Troubleshooting

### Common Issues

1. **Authentication Error**: Ensure your API key has access to all target workspaces
2. **Workspace Not Found**: Verify workspace IDs are correct
3. **Tracing Not Working**: Check that `LS_CROSS_WORSKPACE_KEY` is set correctly

### Debug Mode

Add debug logging to see workspace selection:
```python
print(f"Selected workspace: {workspace_id}")
print(f"Using client for workspace: {client.workspace_id}")
```

## License

MIT License - see LICENSE file for details.
