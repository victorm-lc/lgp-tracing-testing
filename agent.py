import os
import contextlib
from langsmith import Client
from langsmith import tracing_context
from typing import TypedDict
from langgraph.graph import StateGraph
from dataclasses import dataclass
from langgraph.runtime import Runtime

ls_client1 = Client(
    workspace_id="1adb79c4-881d-4625-be9c-3118fffb2166",
    project_name="math_agent",
)
ls_client2 = Client(
    workspace_id="ebbaf2eb-769b-4505-aca2-d11de10372a4",
    project_name="math_agent",
)

@dataclass
class Context:  # (1)!
    workspace_id: str

class State(TypedDict):
    response: str
    ls_env_key: str

def personalized_greeting(state: State, runtime: Runtime[Context]) -> State:
    '''Generate personalized greeting using runtime context and store.'''
    workspace_id = runtime.context.workspace_id  # (3)!

    ls_env_key = os.getenv("LANGSMITH_API_KEY")

    response = f"Hello welcome to workspace {workspace_id}! Nice to see you again."
    return {"response": response, "ls_env_key": ls_env_key}

base_graph = (
    StateGraph(state_schema=State, context_schema=Context)
    .add_node("personalized_greeting", personalized_greeting)
    .set_entry_point("personalized_greeting")
    .set_finish_point("personalized_greeting")
    .compile()
)

@contextlib.asynccontextmanager
async def graph(runtime: Runtime[Context]):
    """Dynamic workspace routing based on user configuration"""
    workspace_id = runtime.context.workspace_id
    print(f"Workspace ID: {workspace_id}")
    if workspace_id == "1":
        async with tracing_context(client=ls_client1):
            yield base_graph
    elif workspace_id == "2":
        async with tracing_context(client=ls_client2):
            yield base_graph
    else:
        # Default workspace
        async with tracing_context(client=ls_client1):
            yield base_graph    
