import os
import contextlib
from langgraph.graph.state import RunnableConfig
from langsmith import Client
from langsmith import tracing_context
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from dotenv import load_dotenv

load_dotenv()

# Single API key set by LangGraph platform
api_key = os.getenv("LS_CROSS_WORSKPACE_KEY")

workspace_a_client = Client(
    api_key=api_key,
    api_url="https://api.smith.langchain.com",
    workspace_id="1adb79c4-881d-4625-be9c-3118fffb2166" # Replace with your workspace id
)
workspace_b_client = Client(
    api_key=api_key,
    api_url="https://api.smith.langchain.com", 
    workspace_id="ebbaf2eb-769b-4505-aca2-d11de10372a4" # Replace with your workspace id
)

class Configuration(TypedDict):
    workspace_id: str

class State(TypedDict):
    response: str

def personalized_greeting(state: State, config: RunnableConfig) -> State:
    '''Generate personalized greeting.'''
    
    # Get workspace info from environment or state
    workspace_info = "your workspace"
    response = f"Hello welcome to {workspace_info}! Nice to see you again."
    return {"response": response}

base_graph = (
    StateGraph(state_schema=State, config_schema=Configuration)
    .add_node("personalized_greeting", personalized_greeting)
    .set_entry_point("personalized_greeting")
    .set_finish_point("personalized_greeting")
    .compile()
)

@contextlib.asynccontextmanager
async def graph(config):
    """Dynamic workspace routing based on user configuration"""
    # Access workspace_id from config dictionary
    workspace_id = config.get("configurable", {}).get("workspace_id", "workspace_a")
    print(f"Workspace ID: {workspace_id}")
    
    if workspace_id == "workspace_a":
        client = workspace_a_client
        project_name = "math-agent-a"
    elif workspace_id == "workspace_b":
        client = workspace_b_client
        project_name = "math-agent-b"
    else:
        # Default workspace
        client = workspace_a_client
        project_name = "math-agent-default"
    
    with tracing_context(enabled=True, client=client, project_name=project_name):
        yield base_graph