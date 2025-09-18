"""Cross-workspace tracing example for LangGraph.

This example demonstrates how to dynamically route traces to different
LangSmith workspaces based on runtime configuration.
"""
import os
import contextlib
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.state import RunnableConfig
from langsmith import Client, tracing_context

# API key with access to multiple workspaces
# Set this as an environment variable in your deployment
api_key = os.getenv("LS_CROSS_WORKSPACE_KEY")

# Initialize clients for different workspaces
# Replace these with your actual workspace IDs
workspace_a_client = Client(
    api_key=api_key,
    api_url="https://api.smith.langchain.com",
    workspace_id="<YOUR_WORKSPACE_A_ID>"  # e.g., "abc123..."
)
workspace_b_client = Client(
    api_key=api_key,
    api_url="https://api.smith.langchain.com", 
    workspace_id="<YOUR_WORKSPACE_B_ID>"  # e.g., "def456..."
)

# Define configuration schema for workspace routing
class Configuration(TypedDict):
    workspace_id: str

# Define the graph state
class State(TypedDict):
    response: str

def greeting(state: State, config: RunnableConfig) -> State:
    """Generate a workspace-specific greeting.
    
    This node demonstrates how the same graph can produce
    different outputs based on workspace configuration.
    """
    workspace_id = config.get("configurable", {}).get("workspace_id", "workspace_a")
    
    # Demonstrate workspace-specific behavior
    if workspace_id == "workspace_a":
        response = "Hello from Workspace A! Processing with production settings."
    elif workspace_id == "workspace_b":
        response = "Hello from Workspace B! Processing with development settings."
    else:
        response = "Hello from the default workspace!"
    
    return {"response": response}

# Build the base graph
base_graph = (
    StateGraph(state_schema=State, config_schema=Configuration)
    .add_node("greeting", greeting)
    .set_entry_point("greeting")
    .set_finish_point("greeting")
    .compile()
)

@contextlib.asynccontextmanager
async def graph(config):
    """Dynamically route traces to different workspaces based on configuration.
    
    This context manager wraps the graph execution with the appropriate
    tracing context based on the workspace_id in the config.
    """
    # Extract workspace_id from the configuration
    workspace_id = config.get("configurable", {}).get("workspace_id", "workspace_a")
    
    # Route to the appropriate workspace
    if workspace_id == "workspace_a":
        client = workspace_a_client
        project_name = "production-traces"
    elif workspace_id == "workspace_b":
        client = workspace_b_client
        project_name = "development-traces"
    else:
        # Default to workspace A
        client = workspace_a_client
        project_name = "default-traces"
    
    # Apply the tracing context for the selected workspace
    with tracing_context(enabled=True, client=client, project_name=project_name):
        yield base_graph