#!/usr/bin/env python3
"""
MCP Server for Lua Table Validation

This server provides a tool to validate Lua table syntax and structure.
It uses a bundled Lua script to perform validation and returns detailed results.
"""

import asyncio
import json
import os
from pathlib import Path

import lupa
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


# Initialize Lua runtime
lua = lupa.LuaRuntime(unpack_returned_tuples=True)

# Load the validator script
validator_path = Path(__file__).parent / "validator.lua"
with open(validator_path, "r") as f:
    validator_code = f.read()

lua.execute(validator_code)
validate_function = lua.globals().validate_table


# Initialize MCP server
app = Server("lua-validator")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="validate_lua_table",
            description="Validates Lua table syntax and structure. Accepts Lua table code as a string and returns validation results.",
            inputSchema={
                "type": "object",
                "properties": {
                    "lua_code": {
                        "type": "string",
                        "description": "The Lua table code to validate (e.g., '{name = \"test\", value = 42}')",
                    }
                },
                "required": ["lua_code"],
            },
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    if name != "validate_lua_table":
        raise ValueError(f"Unknown tool: {name}")

    lua_code = arguments.get("lua_code", "")

    if not lua_code:
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "valid": False,
                    "error": "No Lua code provided",
                    "details": None
                }, indent=2)
            )
        ]

    try:
        # Call the Lua validation function
        result = validate_function(lua_code)

        # Convert Lua table to Python dict
        result_dict = {
            "valid": bool(result["valid"]),
            "error": result["error"] if result["error"] else None,
            "details": result["details"] if result["details"] else None
        }

        return [
            TextContent(
                type="text",
                text=json.dumps(result_dict, indent=2)
            )
        ]

    except Exception as e:
        # Handle any Python-level errors
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "valid": False,
                    "error": f"Server error: {str(e)}",
                    "details": None
                }, indent=2)
            )
        ]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
