#!/usr/bin/env python3
"""
Test script to demonstrate workspace routing in LangGraph
"""
import asyncio
from agent import graph

async def test_workspace_routing():
    """Test different workspace configurations"""
    
    # Test workspace A
    config_a = {
        "configurable": {
            "workspace_id": "workspace_a"
        }
    }
    
    # Test workspace B  
    config_b = {
        "configurable": {
            "workspace_id": "workspace_b"
        }
    }
    
    # Test default workspace
    config_default = {
        "configurable": {}
    }
    
    print("Testing workspace routing...")
    
    # Test workspace A
    print("\n=== Testing Workspace A ===")
    async with graph(config_a) as g:
        result = await g.ainvoke({"response": "", "ls_env_key": ""})
        print(f"Result: {result}")
    
    # Test workspace B
    print("\n=== Testing Workspace B ===")
    async with graph(config_b) as g:
        result = await g.ainvoke({"response": "", "ls_env_key": ""})
        print(f"Result: {result}")
    
    # Test default workspace
    print("\n=== Testing Default Workspace ===")
    async with graph(config_default) as g:
        result = await g.ainvoke({"response": "", "ls_env_key": ""})
        print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(test_workspace_routing())
