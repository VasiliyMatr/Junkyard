# Lua Table Validator MCP Server

A Model Context Protocol (MCP) server that validates Lua table syntax and structure. This server allows AI assistants and other MCP clients to programmatically validate Lua table code.

## Features

- **Syntax validation**: Checks if Lua table code is syntactically correct
- **Structure validation**: Verifies the code evaluates to a valid Lua table
- **Detailed error reporting**: Returns specific error messages with context
- **Stdio transport**: Easy integration with MCP clients

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Server

Start the server directly:
```bash
python lua_validator_server.py
```

Or make it executable and run:
```bash
chmod +x lua_validator_server.py
./lua_validator_server.py
```

### MCP Tool Interface

**Tool Name**: `validate_lua_table`

**Parameters**:
- `lua_code` (string, required): The Lua table code to validate

**Returns**: JSON object with:
- `valid` (boolean): Whether the table is valid
- `error` (string|null): Error message if validation failed
- `details` (string|null): Additional validation details

### Example Requests

Valid table:
```json
{
  "lua_code": "{name = \"test\", value = 42}"
}
```

Response:
```json
{
  "valid": true,
  "error": null,
  "details": "Valid Lua table with 2 keys"
}
```

Invalid table:
```json
{
  "lua_code": "{name = \"test\", value = }"
}
```

Response:
```json
{
  "valid": false,
  "error": "Syntax error: [string \"return {name = \\\"test\\\", value = }\"]:1: unexpected symbol near '}'",
  "details": null
}
```

## Testing

Run the automated test suite:
```bash
python test_server.py
```

The test suite validates:
- Simple tables
- Nested tables
- Array-like tables
- Invalid syntax
- Malformed code
- Non-table values
- Empty tables

## Configuration for MCP Clients

Add to your MCP client configuration (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "lua-validator": {
      "command": "python",
      "args": ["/work/mcp/lua_validator_server.py"]
    }
  }
}
```

## Project Structure

```
/work/mcp/
├── lua_validator_server.py    # Main MCP server implementation
├── validator.lua               # Lua validation script
├── requirements.txt            # Python dependencies
├── test_server.py             # Automated test suite
└── README.md                  # This file
```

## Requirements

- Python 3.8+
- `mcp` - MCP Python SDK
- `lupa` - Python-Lua bridge

## License

MIT
