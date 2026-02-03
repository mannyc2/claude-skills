#!/usr/bin/env python3
"""
Token Counting for CLI Output Compression

Uses tiktoken if available, falls back to character-based approximation.

Decision: Make tiktoken optional
- Prefer tiktoken for accuracy (matches Claude's actual token counting)
- Fall back to chars/4 approximation if tiktoken not available
- Skill works out of the box with zero setup required
"""

import json
import sys
from typing import Union

# Try importing tiktoken, but don't require it
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False


class TokenCounter:
    """
    Count tokens using tiktoken (cl100k_base encoding - same as Claude).

    Falls back to character-based approximation if tiktoken not installed.
    """

    def __init__(self):
        if TIKTOKEN_AVAILABLE:
            # Use cl100k_base encoding (used by GPT-4, Claude, and modern LLMs)
            self.encoding = tiktoken.get_encoding("cl100k_base")
            self.method = "tiktoken"
        else:
            self.encoding = None
            self.method = "approximation"
            # Only print warning once on first use
            if not hasattr(TokenCounter, '_warned'):
                print(
                    "Note: tiktoken not available, using character-based approximation (chars/4). "
                    "For exact counts, install tiktoken: pip install tiktoken",
                    file=sys.stderr
                )
                TokenCounter._warned = True

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.

        Uses tiktoken if available, otherwise approximates with chars/4.
        Approximation is good enough for threshold checks and compression metrics.
        """
        if isinstance(text, dict) or isinstance(text, list):
            text = json.dumps(text, indent=2)

        if self.encoding:
            # Accurate count using tiktoken
            return len(self.encoding.encode(text))
        else:
            # Approximation: ~4 chars per token (good enough for our use case)
            # This matches Claude Code's own approximation
            return len(text) // 4

    def measure_compression(self, raw: Union[str, dict], compressed: Union[str, dict]) -> dict:
        """
        Calculate compression metrics.

        Returns:
        - raw_tokens: Token count of raw output
        - compressed_tokens: Token count of compressed output
        - tokens_saved: Absolute reduction
        - compression_ratio: Percentage of tokens removed
        - reduction_percent: Human-readable percentage
        - efficiency_multiplier: How many times more efficient
        """
        # Convert to strings if needed
        raw_str = json.dumps(raw, indent=2) if isinstance(raw, (dict, list)) else raw
        comp_str = json.dumps(compressed, indent=2) if isinstance(compressed, (dict, list)) else compressed

        raw_tokens = self.count_tokens(raw_str)
        comp_tokens = self.count_tokens(comp_str)
        tokens_saved = raw_tokens - comp_tokens

        compression_ratio = tokens_saved / raw_tokens if raw_tokens > 0 else 0

        return {
            "raw_tokens": raw_tokens,
            "compressed_tokens": comp_tokens,
            "tokens_saved": tokens_saved,
            "compression_ratio": compression_ratio,
            "reduction_percent": f"{compression_ratio * 100:.1f}%",
            "efficiency_multiplier": f"{raw_tokens / comp_tokens:.1f}x" if comp_tokens > 0 else "∞"
        }


def main():
    """CLI interface for testing token counting."""
    if len(sys.argv) < 2:
        print("Usage: python3 token_counter.py <text_or_file>")
        sys.exit(1)

    input_text = sys.argv[1]

    # Check if it's a file
    from pathlib import Path
    if Path(input_text).exists():
        with open(input_text, 'r') as f:
            input_text = f.read()

    counter = TokenCounter()
    tokens = counter.count_tokens(input_text)

    print(json.dumps({
        "text_length": len(input_text),
        "tokens": tokens,
        "chars_per_token": f"{len(input_text) / tokens:.2f}" if tokens > 0 else "N/A"
    }, indent=2))


if __name__ == "__main__":
    main()
