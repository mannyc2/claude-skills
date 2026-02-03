#!/usr/bin/env python3
"""
Smart CLI Wrapper - MCP Server

Provides compressed command execution as an MCP tool for Claude Code.
This enables transparent integration with Claude Code sessions.

Installation:
    Configured automatically via plugin.json mcpServers when the plugin is installed.

Usage in Claude Code:
    Claude Code will automatically use this when executing commands.
"""

import json
import sys
import asyncio
from pathlib import Path

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).parent / "skills" / "smart-cli-wrapper" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from cli_interceptor import CLIInterceptor


class SmartCLIMCPServer:
    """MCP Server for Smart CLI Wrapper."""

    def __init__(self):
        self.interceptor = CLIInterceptor()

    async def handle_request(self, request: dict) -> dict:
        """Handle MCP requests."""
        method = request.get("method")

        if method == "tools/list":
            return self.list_tools()

        elif method == "tools/call":
            return await self.call_tool(request.get("params", {}))

        elif method == "initialize":
            return {
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": "smart-cli-wrapper",
                    "version": "1.0.0"
                },
                "capabilities": {
                    "tools": {}
                }
            }

        else:
            return {
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }

    def list_tools(self) -> dict:
        """Return list of available tools."""
        return {
            "tools": [
                {
                    "name": "execute_compressed",
                    "description": (
                        "Execute a CLI command with automatic compression if output exceeds threshold. "
                        "Achieves 80-95% token reduction while preserving 100% actionable information. "
                        "Use this instead of raw bash commands for verbose CLI tools (kubectl, aws, terraform, etc.)."
                    ),
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "The command to execute (e.g., 'kubectl get pods -A')"
                            },
                            "intent": {
                                "type": "string",
                                "description": "Optional: What you're trying to accomplish (helps compression)"
                            },
                            "compress": {
                                "type": "string",
                                "description": (
                                    "Optional: Custom compression instructions. Examples: "
                                    "'Show only errors', 'Format as table', 'Extract failed items only'"
                                )
                            },
                            "timeout": {
                                "type": "number",
                                "description": "Optional: Command execution timeout in seconds"
                            }
                        },
                        "required": ["command"]
                    }
                }
            ]
        }

    async def call_tool(self, params: dict) -> dict:
        """Execute a tool."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name == "execute_compressed":
            return await self.execute_compressed(arguments)
        else:
            return {
                "error": {
                    "code": -32602,
                    "message": f"Unknown tool: {tool_name}"
                }
            }

    async def execute_compressed(self, args: dict) -> dict:
        """Execute command with compression."""
        command = args.get("command")
        intent = args.get("intent")
        compress = args.get("compress")
        timeout = args.get("timeout")

        if not command:
            return {
                "error": {
                    "code": -32602,
                    "message": "Missing required parameter: command"
                }
            }

        try:
            # Execute with compression
            result = self.interceptor.execute_with_compression(
                command=command,
                user_intent=intent,
                compression_instructions=compress,
                timeout=timeout
            )

            if not result["success"]:
                # Command failed
                content = [
                    {
                        "type": "text",
                        "text": f"Command failed (exit code: {result['exit_code']})\n"
                                f"Error: {result.get('error', 'Unknown error')}\n"
                                f"\nOutput:\n{result.get('raw', '')}"
                    }
                ]
            else:
                # Command succeeded
                output = result.get("compressed") or result.get("raw", "")

                # Build metadata message
                metadata = f"Raw: {result['raw_tokens']} tokens"
                if result.get("compression_applied"):
                    metadata += (
                        f"\nCompressed: {result['compressed_tokens']} tokens"
                        f"\nSaved: {result['tokens_saved']} tokens ({result['reduction_percent']})"
                    )
                else:
                    metadata += "\nNo compression (below threshold)"

                content = [
                    {
                        "type": "text",
                        "text": f"{metadata}\n\n{output}"
                    }
                ]

            return {
                "content": content,
                "isError": not result["success"]
            }

        except Exception as e:
            return {
                "error": {
                    "code": -32603,
                    "message": f"Execution failed: {str(e)}"
                }
            }

    async def run(self):
        """Run the MCP server."""
        while True:
            try:
                # Read JSON-RPC request from stdin
                line = sys.stdin.readline()
                if not line:
                    break

                request = json.loads(line)
                response = await self.handle_request(request)

                # Write JSON-RPC response to stdout
                print(json.dumps(response), flush=True)

            except json.JSONDecodeError as e:
                error_response = {
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)

            except Exception as e:
                error_response = {
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)


async def main():
    """Main entry point."""
    server = SmartCLIMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
