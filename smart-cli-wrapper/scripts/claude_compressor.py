#!/usr/bin/env python3
"""
Claude Compressor - Meta-Optimization Using Claude Code

Uses Claude Code programmatically (`claude --print`) to intelligently compress
CLI output. This is meta: Claude Code calling itself to optimize its own context.

Decision: Let Claude compress instead of hardcoded rules
- Adapts to ANY CLI tool automatically
- No maintenance needed for new tools
- Improves as Claude models improve
- Uses Claude Max subscription (no API costs)
"""

import subprocess
import sys
import json


class ClaudeCompressor:
    """
    Calls Claude Code programmatically to compress CLI output.

    This is the core innovation: Claude Code using itself to optimize context.
    """

    def __init__(self, model: str = "haiku", timeout: int = 30):
        """
        Initialize compressor.

        Args:
        - model: "haiku" (fast, default) or "sonnet" (higher quality)
        - timeout: Max seconds to wait for compression (default: 30)
        """
        self.model = model
        self.timeout = timeout

    def compress(
        self,
        raw_output: str,
        command: str,
        user_intent: str = None,
        compression_instructions: str = None
    ) -> str:
        """
        Use Claude Code to intelligently compress output.

        Decision: Let Claude decide how to compress based on context
        - Command that was run
        - User's intent/goal
        - Output structure and content
        - Custom compression instructions (optional)

        This is more adaptive than hardcoded rules.

        Args:
        - raw_output: Raw CLI output to compress
        - command: Command that generated output (for context)
        - user_intent: What user is trying to accomplish (optional)
        - compression_instructions: Custom instructions on HOW to compress (optional)
          Examples:
          - "Focus on errors and warnings only"
          - "Keep all resource IDs intact"
          - "Summarize as a table"
          - "Extract only failed items"

        Returns:
        - Compressed output as string

        Raises:
        - subprocess.TimeoutExpired: If compression takes >30s
        - subprocess.CalledProcessError: If claude command fails
        """
        # Build compression prompt
        prompt = self._build_compression_prompt(raw_output, command, user_intent, compression_instructions)

        try:
            # Call claude --print (uses Claude Max subscription)
            # Decision: Use --print for non-interactive mode
            result = subprocess.run(
                ["claude", "--print", prompt],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=True  # Raise exception on non-zero exit
            )

            return result.stdout.strip()

        except subprocess.TimeoutExpired:
            print(f"Warning: Compression timed out after {self.timeout}s", file=sys.stderr)
            raise

        except subprocess.CalledProcessError as e:
            print(f"Warning: Claude compression failed: {e.stderr}", file=sys.stderr)
            raise

        except FileNotFoundError:
            print("Error: 'claude' command not found. Is Claude Code installed?", file=sys.stderr)
            raise

    def _build_compression_prompt(
        self,
        raw_output: str,
        command: str,
        user_intent: str,
        compression_instructions: str = None
    ) -> str:
        """
        Build prompt that guides Claude to compress effectively.

        Decision: Provide compression guidelines in prompt
        - Preserve ALL actionable information
        - Remove verbose metadata, UUIDs, timestamps
        - Summarize collections (show recent + aggregate old)
        - Extract key info from errors
        - Target 80-95% reduction
        - Allow custom compression instructions for fine-grained control

        The prompt is the core of this system - it defines what "good compression" means.
        """
        # Truncate extremely large outputs to prevent prompt overflow
        # Decision: Claude's context window is 200K tokens
        # Reserve 50K for prompt + instructions = max 150K for raw output
        # Approximate: 150K tokens ~= 600K chars (4 chars/token average)
        MAX_OUTPUT_CHARS = 500_000  # Conservative limit

        if len(raw_output) > MAX_OUTPUT_CHARS:
            truncated = True
            # Show first 80% + last 20% if truncated
            split_point = int(MAX_OUTPUT_CHARS * 0.8)
            remaining = MAX_OUTPUT_CHARS - split_point
            output_for_prompt = (
                raw_output[:split_point] +
                f"\n\n[... {len(raw_output) - MAX_OUTPUT_CHARS:,} characters omitted ...]\n\n" +
                raw_output[-remaining:]
            )
        else:
            truncated = False
            output_for_prompt = raw_output

        # Build custom instructions section if provided
        custom_section = ""
        if compression_instructions:
            custom_section = f"""
**CUSTOM COMPRESSION INSTRUCTIONS** (highest priority - follow these first):
{compression_instructions}
"""

        return f"""You are helping optimize CLI command output for token efficiency in Claude Code.

Command executed: {command}
User intent: {user_intent or "Not specified"}
{f"[Note: Output was truncated for processing]" if truncated else ""}
{custom_section}

Raw output ({len(raw_output):,} chars, ~{len(raw_output) // 4:,} tokens):
```
{output_for_prompt}
```

**Your task**: Compress this output to 10-20% of original size while preserving 100% of actionable information.

**Compression Guidelines**:

1. **Preserve critical data**:
   - Errors, warnings, status codes
   - Resource states (running, pending, failed, etc.)
   - Versions, counts, timestamps (if actionable)
   - User-facing messages

2. **Remove noise**:
   - UUIDs, internal IDs, request/trace IDs
   - Debug timestamps (unless part of error)
   - Verbose metadata (created_by, updated_by, internal_* fields)
   - Redundant object wrappers

3. **Summarize collections**:
   - If >7 items: Show 5 most recent/relevant + aggregate rest
   - Example: "8 failed pods" instead of listing all 8
   - Provide status breakdown (e.g., "185 running, 8 pending, 3 failed")

4. **Extract error essence**:
   - Root cause message
   - Location in user's code (not framework internals)
   - Actionable suggestion
   - Skip verbose stack traces (keep top 2-3 frames max)

5. **Maintain structure**:
   - Keep JSON structure if it aids clarity
   - Use markdown formatting for readability
   - Group related information together

6. **Be ruthless**:
   - If data isn't actionable by the user, omit it
   - Users can always see raw output if needed
   - Your job is radical compression while preserving utility

**Target**: 80-95% token reduction with 0% information loss.

**Output format**: Return ONLY the compressed output (no preamble, no explanations, no "Here's the compressed version:").

Compressed output:"""

    def test_compression(self, test_command: str = "kubectl get pods -A") -> dict:
        """
        Test compression with a sample command.

        Useful for verifying Claude Code is accessible and compression works.

        Returns dict with test results.
        """
        # Create sample verbose output
        sample_output = """NAME                                     READY   STATUS             RESTARTS   AGE
coredns-5d78c9869d-7xqjp                1/1     Running            0          45d
coredns-5d78c9869d-qmz8r                1/1     Running            0          45d
etcd-minikube                           1/1     Running            0          45d
kube-apiserver-minikube                 1/1     Running            0          45d
kube-controller-manager-minikube        1/1     Running            0          45d
kube-proxy-8c9jk                        1/1     Running            0          45d
kube-scheduler-minikube                 1/1     Running            0          45d
storage-provisioner                     1/1     Running            0          45d"""

        try:
            compressed = self.compress(
                sample_output,
                test_command,
                "Testing compression system"
            )

            from token_counter import TokenCounter
            counter = TokenCounter()
            metrics = counter.measure_compression(sample_output, compressed)

            return {
                "success": True,
                "sample_output": sample_output[:100] + "...",
                "compressed_output": compressed,
                "metrics": metrics
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }


def main():
    """CLI interface for testing compression."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 claude_compressor.py test                    # Run test")
        print("  python3 claude_compressor.py compress <file>         # Compress file")
        print("  python3 claude_compressor.py compress <file> <cmd>   # With command context")
        sys.exit(1)

    command = sys.argv[1]
    compressor = ClaudeCompressor()

    if command == "test":
        print("Running compression test...", file=sys.stderr)
        result = compressor.test_compression()

        if result["success"]:
            print("\n✓ Compression test successful!\n", file=sys.stderr)
            print(f"Sample output ({len(result['sample_output'])} chars):", file=sys.stderr)
            print(result["sample_output"], file=sys.stderr)
            print(f"\nCompressed output:", file=sys.stderr)
            print(result["compressed_output"], file=sys.stderr)
            print(f"\nMetrics:", file=sys.stderr)
            print(json.dumps(result["metrics"], indent=2))
        else:
            print(f"\n✗ Compression test failed: {result['error']}", file=sys.stderr)
            sys.exit(1)

    elif command == "compress":
        if len(sys.argv) < 3:
            print("Error: Provide file to compress", file=sys.stderr)
            sys.exit(1)

        file_path = sys.argv[2]
        cmd_context = sys.argv[3] if len(sys.argv) > 3 else "unknown command"

        try:
            with open(file_path, 'r') as f:
                raw_output = f.read()

            print(f"Compressing {len(raw_output)} chars...", file=sys.stderr)
            compressed = compressor.compress(raw_output, cmd_context)

            # Output compressed result
            print(compressed)

        except FileNotFoundError:
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            sys.exit(1)

    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
