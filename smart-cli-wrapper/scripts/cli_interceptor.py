#!/usr/bin/env python3
"""
CLI Interceptor - Smart Wrapper for Command Execution

Transparently wraps CLI command execution and auto-compresses output
when it exceeds the token threshold.

Decision: Execute first, compress if needed
- Always capture raw output
- Count tokens
- If > threshold: compress using Claude Code
- If <= threshold: return raw unchanged
"""

import subprocess
import sys
import json
from typing import Union, Optional
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from token_counter import TokenCounter
from claude_compressor import ClaudeCompressor


class CLIInterceptor:
    """
    Transparent wrapper for CLI command execution.

    Automatically compresses output when it exceeds token threshold.
    """

    def __init__(
        self,
        threshold_tokens: int = 500,
        compression_timeout: int = 30,
        model: str = "haiku"
    ):
        """
        Initialize interceptor.

        Args:
        - threshold_tokens: Only compress if output > this many tokens (default: 500)
        - compression_timeout: Max seconds for compression (default: 30)
        - model: "haiku" (fast) or "sonnet" (quality)
        """
        self.threshold = threshold_tokens
        self.counter = TokenCounter()
        self.compressor = ClaudeCompressor(model=model, timeout=compression_timeout)

    def execute_with_compression(
        self,
        command: Union[str, list[str]],
        user_intent: Optional[str] = None,
        compression_instructions: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> dict:
        """
        Execute command and auto-compress if output exceeds threshold.

        Args:
        - command: CLI command as string or list (e.g., "kubectl get pods" or ["kubectl", "get", "pods"])
        - user_intent: What user is trying to accomplish (for compression context)
        - compression_instructions: Custom instructions on HOW to compress (optional)
          Examples: "Focus on errors only", "Keep all IDs", "Summarize as table"
        - timeout: Command execution timeout in seconds (default: None = no timeout)

        Returns dict:
        - success: Boolean indicating if command succeeded
        - exit_code: Command exit code
        - raw: Original output
        - compressed: Compressed output (if threshold exceeded, else None)
        - raw_tokens: Token count of raw output
        - compressed_tokens: Token count of compressed output (if compressed)
        - compression_applied: Boolean
        - tokens_saved: Absolute reduction (if compressed)
        - compression_ratio: Percentage reduction (if compressed)
        - error: Error message (if command failed)
        """
        # Convert string command to list if needed
        if isinstance(command, str):
            command_list = command.split()
            command_str = command
        else:
            command_list = command
            command_str = " ".join(command)

        try:
            # Execute the command
            result = subprocess.run(
                command_list,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            # Combine stdout and stderr
            raw_output = result.stdout
            if result.stderr:
                raw_output += f"\n{result.stderr}"

            raw_output = raw_output.strip()

            # Count tokens in raw output
            raw_tokens = self.counter.count_tokens(raw_output)

            # Decision: Compress if exceeds threshold
            if raw_tokens > self.threshold:
                try:
                    compressed_output = self.compressor.compress(
                        raw_output,
                        command_str,
                        user_intent,
                        compression_instructions
                    )

                    compressed_tokens = self.counter.count_tokens(compressed_output)
                    tokens_saved = raw_tokens - compressed_tokens
                    compression_ratio = tokens_saved / raw_tokens if raw_tokens > 0 else 0

                    # Safety check: Don't use compression if it inflates tokens
                    if compressed_tokens >= raw_tokens:
                        print(
                            f"Warning: Compression inflated tokens ({raw_tokens} → {compressed_tokens}). "
                            f"Using raw output.",
                            file=sys.stderr
                        )
                        compression_applied = False
                        compressed_output = None
                        compressed_tokens = None
                        tokens_saved = 0
                        compression_ratio = 0
                    else:
                        compression_applied = True

                except Exception as e:
                    print(f"Warning: Compression failed: {e}. Using raw output.", file=sys.stderr)
                    compression_applied = False
                    compressed_output = None
                    compressed_tokens = None
                    tokens_saved = 0
                    compression_ratio = 0
            else:
                # Below threshold - no compression needed
                compression_applied = False
                compressed_output = None
                compressed_tokens = None
                tokens_saved = 0
                compression_ratio = 0

            return {
                "success": result.returncode == 0,
                "exit_code": result.returncode,
                "raw": raw_output,
                "compressed": compressed_output,
                "raw_tokens": raw_tokens,
                "compressed_tokens": compressed_tokens,
                "compression_applied": compression_applied,
                "tokens_saved": tokens_saved,
                "compression_ratio": compression_ratio,
                "reduction_percent": f"{compression_ratio * 100:.1f}%" if compression_applied else "0.0%"
            }

        except subprocess.TimeoutExpired as e:
            return {
                "success": False,
                "exit_code": -1,
                "error": f"Command timed out after {timeout}s",
                "raw": str(e.stdout) if e.stdout else "",
                "compression_applied": False
            }

        except FileNotFoundError as e:
            return {
                "success": False,
                "exit_code": -1,
                "error": f"Command not found: {command_list[0]}",
                "raw": "",
                "compression_applied": False
            }

        except Exception as e:
            return {
                "success": False,
                "exit_code": -1,
                "error": f"Execution failed: {str(e)}",
                "raw": "",
                "compression_applied": False
            }


def main():
    """CLI interface for testing and using the interceptor."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 cli_interceptor.py execute <command>                           # Execute with compression")
        print("  python3 cli_interceptor.py execute <command> --intent <text>           # With user intent")
        print("  python3 cli_interceptor.py execute <command> --compress <instructions> # Custom compression")
        print("  python3 cli_interceptor.py test                                        # Run test")
        print("")
        print("Examples:")
        print("  python3 cli_interceptor.py execute 'kubectl get pods -A'")
        print("  python3 cli_interceptor.py execute 'kubectl get pods' --intent 'Find failing pods'")
        print("  python3 cli_interceptor.py execute 'aws ec2 describe-instances' --compress 'Show only running instances as table'")
        print("  python3 cli_interceptor.py execute 'kubectl logs pod-name' --compress 'Extract errors and warnings only'")
        sys.exit(1)

    command = sys.argv[1]

    if command == "test":
        # Run a simple test
        print("Running interceptor test...", file=sys.stderr)

        interceptor = CLIInterceptor(threshold_tokens=50)  # Low threshold for testing

        # Test with a simple command that will likely exceed threshold
        result = interceptor.execute_with_compression(
            "ls -la",
            user_intent="Testing compression system"
        )

        if result["success"]:
            print("\n✓ Test successful!\n", file=sys.stderr)
            print("Results:", file=sys.stderr)
            print(f"  Raw output: {len(result['raw'])} chars, {result['raw_tokens']} tokens", file=sys.stderr)

            if result["compression_applied"]:
                print(f"  Compressed: {len(result['compressed'])} chars, {result['compressed_tokens']} tokens", file=sys.stderr)
                print(f"  Savings: {result['tokens_saved']} tokens ({result['reduction_percent']})", file=sys.stderr)
                print("\nCompressed output:", file=sys.stderr)
                print(result["compressed"])
            else:
                print(f"  No compression (below threshold or failed)", file=sys.stderr)
                print("\nRaw output:", file=sys.stderr)
                print(result["raw"])
        else:
            print(f"\n✗ Test failed: {result.get('error', 'Unknown error')}", file=sys.stderr)
            sys.exit(1)

    elif command == "execute":
        if len(sys.argv) < 3:
            print("Error: Provide command to execute", file=sys.stderr)
            sys.exit(1)

        cmd = sys.argv[2]

        # Parse optional flags
        user_intent = None
        compression_instructions = None

        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--intent":
                if i + 1 < len(sys.argv):
                    user_intent = sys.argv[i + 1]
                    i += 2
                else:
                    print("Error: --intent flag requires an argument", file=sys.stderr)
                    sys.exit(1)
            elif sys.argv[i] == "--compress":
                if i + 1 < len(sys.argv):
                    compression_instructions = sys.argv[i + 1]
                    i += 2
                else:
                    print("Error: --compress flag requires an argument", file=sys.stderr)
                    sys.exit(1)
            else:
                print(f"Error: Unknown flag: {sys.argv[i]}", file=sys.stderr)
                sys.exit(1)

        interceptor = CLIInterceptor()

        print(f"Executing: {cmd}", file=sys.stderr)
        if user_intent:
            print(f"Intent: {user_intent}", file=sys.stderr)
        if compression_instructions:
            print(f"Compression instructions: {compression_instructions}", file=sys.stderr)

        result = interceptor.execute_with_compression(cmd, user_intent, compression_instructions)

        if result["success"]:
            print(f"\n✓ Command succeeded (exit code: {result['exit_code']})", file=sys.stderr)
            print(f"Raw output: {result['raw_tokens']} tokens", file=sys.stderr)

            if result["compression_applied"]:
                print(f"Compressed: {result['compressed_tokens']} tokens", file=sys.stderr)
                print(f"Saved: {result['tokens_saved']} tokens ({result['reduction_percent']})", file=sys.stderr)
                print("\n--- Compressed Output ---")
                print(result["compressed"])
            else:
                reason = "below threshold" if result['raw_tokens'] <= interceptor.threshold else "compression failed"
                print(f"No compression applied ({reason})", file=sys.stderr)
                print("\n--- Raw Output ---")
                print(result["raw"])
        else:
            print(f"\n✗ Command failed (exit code: {result['exit_code']})", file=sys.stderr)
            print(f"Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
            if result.get("raw"):
                print("\n--- Output ---")
                print(result["raw"])
            sys.exit(result["exit_code"])

    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
