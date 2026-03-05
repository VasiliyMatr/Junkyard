#!/usr/bin/env python3
"""
Test script for Lua Validator MCP Server

Tests the server with various valid and invalid Lua table inputs.
"""

import asyncio
import json
import subprocess
import sys


async def send_mcp_request(process, request):
    """Send an MCP request and get the response."""
    request_json = json.dumps(request) + "\n"
    process.stdin.write(request_json.encode())
    await process.stdin.drain()

    response_line = await process.stdout.readline()
    return json.loads(response_line.decode())


async def test_server():
    """Run tests against the MCP server."""
    print("Starting MCP server...")

    # Start the server process
    process = await asyncio.create_subprocess_exec(
        sys.executable, "lua_validator_server.py",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    try:
        # Initialize the connection
        print("\n1. Initializing connection...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }

        response = await send_mcp_request(process, init_request)
        print(f"   ✓ Server initialized: {response.get('result', {}).get('serverInfo', {}).get('name')}")

        # List tools
        print("\n2. Listing available tools...")
        list_tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }

        response = await send_mcp_request(process, list_tools_request)
        tools = response.get("result", {}).get("tools", [])
        print(f"   ✓ Found {len(tools)} tool(s): {[t['name'] for t in tools]}")

        # Test cases
        test_cases = [
            {
                "name": "Valid simple table",
                "code": '{name = "test", value = 42}',
                "expected_valid": True
            },
            {
                "name": "Valid nested table",
                "code": '{user = {name = "John", age = 30}, active = true}',
                "expected_valid": True
            },
            {
                "name": "Valid array-like table",
                "code": '{1, 2, 3, 4, 5}',
                "expected_valid": True
            },
            {
                "name": "Invalid syntax - missing value",
                "code": '{name = "test", value = }',
                "expected_valid": False
            },
            {
                "name": "Invalid syntax - malformed",
                "code": '{{{',
                "expected_valid": False
            },
            {
                "name": "Invalid - not a table",
                "code": '"just a string"',
                "expected_valid": False
            },
            {
                "name": "Empty table",
                "code": '{}',
                "expected_valid": True
            }
        ]

        print("\n3. Running validation tests...")
        passed = 0
        failed = 0

        for i, test in enumerate(test_cases, start=1):
            call_tool_request = {
                "jsonrpc": "2.0",
                "id": 100 + i,
                "method": "tools/call",
                "params": {
                    "name": "validate_lua_table",
                    "arguments": {
                        "lua_code": test["code"]
                    }
                }
            }

            response = await send_mcp_request(process, call_tool_request)
            result_text = response.get("result", {}).get("content", [{}])[0].get("text", "{}")
            result = json.loads(result_text)

            is_valid = result.get("valid", False)
            expected = test["expected_valid"]

            if is_valid == expected:
                print(f"   ✓ Test {i}: {test['name']}")
                print(f"      Valid: {is_valid}, Details: {result.get('details') or result.get('error')}")
                passed += 1
            else:
                print(f"   ✗ Test {i}: {test['name']}")
                print(f"      Expected valid={expected}, got valid={is_valid}")
                print(f"      Result: {result}")
                failed += 1

        print(f"\n{'='*60}")
        print(f"Test Results: {passed} passed, {failed} failed out of {len(test_cases)} total")
        print(f"{'='*60}")

        return failed == 0

    finally:
        # Clean up
        process.terminate()
        await process.wait()


if __name__ == "__main__":
    success = asyncio.run(test_server())
    sys.exit(0 if success else 1)
