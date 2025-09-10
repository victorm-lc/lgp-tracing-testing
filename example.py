from langsmith.run_helpers import get_current_run_tree, traceable, tracing_context
import httpx
from langsmith import traceable, Client
from langsmith.middleware import TracingMiddleware
from fastapi import FastAPI, Request
import uvicorn
import asyncio


app = FastAPI() 
app.add_middleware(TracingMiddleware)

# Create clients for different workspaces
project_a_client = Client(
    api_key="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",
    api_url="https://api.smith.langchain.com",
)

project_b_client = Client(
    api_key="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",
    api_url="https://api.smith.langchain.com",
)

@traceable
async def my_client_function():
    headers = {
        "X-Workspace": "workspace_b"
    }
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        return await client.post("/my-route", headers=headers)

@traceable
async def some_function():
    print("some function now")
    return "Hello, world!"

@app.post("/my-route")
async def fake_route(request: Request):
    print(request.headers, "request headers")
    print("tracing agent now")
    workspace = request.headers.get("X-Workspace", "workspace_a")
    client = project_b_client if workspace == "workspace_b" else project_a_client
    project_name = "indeed-project-b" if workspace == "workspace_b" else "indeed-project-a"
    print(workspace, "workspace", project_name, "project name")
    with tracing_context(enabled=True, client=client, project_name=project_name):
        return await some_function()

async def main():
    config = uvicorn.Config(app, host="localhost", port=8000)
    server = uvicorn.Server(config)
    server_task = asyncio.create_task(server.serve())
    # Wait a moment for the server to start
    await asyncio.sleep(1)
    # Call my_client_function
    result = await my_client_function()
    print("Result:", result)
    # Keep the server running
    await server_task

if __name__ == "__main__":
    asyncio.run(main())