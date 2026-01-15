#!/usr/bin/env python3
"""
Fetch a Tempo documentation page by path.

Usage:
    python fetch_docs.py <path>
    
Examples:
    python fetch_docs.py /protocol/tip20/overview
    python fetch_docs.py /guide/payments
    python fetch_docs.py /quickstart/evm-compatibility

The script fetches the page from docs.tempo.xyz and extracts the main content.

Note: Requires network access to docs.tempo.xyz. In Claude Code, ensure your
network settings allow this domain. If network access is restricted, use the
local reference files in references/ directory instead.
"""

import sys
import urllib.request
import urllib.error
import re
import html

def strip_html_tags(text):
    """Remove HTML tags and decode entities."""
    # Remove script and style elements
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    # Remove navigation elements
    text = re.sub(r'<nav[^>]*>.*?</nav>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<header[^>]*>.*?</header>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<footer[^>]*>.*?</footer>', '', text, flags=re.DOTALL | re.IGNORECASE)
    # Convert headers to markdown
    text = re.sub(r'<h1[^>]*>(.*?)</h1>', r'\n# \1\n', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<h2[^>]*>(.*?)</h2>', r'\n## \1\n', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<h3[^>]*>(.*?)</h3>', r'\n### \1\n', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<h4[^>]*>(.*?)</h4>', r'\n#### \1\n', text, flags=re.DOTALL | re.IGNORECASE)
    # Convert code blocks
    text = re.sub(r'<pre[^>]*><code[^>]*>(.*?)</code></pre>', r'\n```\n\1\n```\n', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', text, flags=re.DOTALL | re.IGNORECASE)
    # Convert links - extract href and text
    text = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', text, flags=re.DOTALL | re.IGNORECASE)
    # Convert lists
    text = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1\n', text, flags=re.DOTALL | re.IGNORECASE)
    # Convert paragraphs
    text = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', text, flags=re.DOTALL | re.IGNORECASE)
    # Convert line breaks
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    # Remove remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Decode HTML entities
    text = html.unescape(text)
    # Clean up whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' +', ' ', text)
    return text.strip()

def fetch_docs(path):
    """Fetch a documentation page from docs.tempo.xyz"""
    # Ensure path starts with /
    if not path.startswith('/'):
        path = '/' + path
    
    url = f"https://docs.tempo.xyz{path}"
    
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (compatible; TempoDocs/1.0)'}
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        print(f"Error: HTTP {e.code} - {e.reason}")
        print(f"URL: {url}")
        return None
    except urllib.error.URLError as e:
        print(f"Error: Could not connect - {e.reason}")
        return None
    
    # Try to extract main content area
    main_match = re.search(r'<main[^>]*>(.*?)</main>', content, re.DOTALL | re.IGNORECASE)
    if main_match:
        content = main_match.group(1)
    else:
        # Try article tag
        article_match = re.search(r'<article[^>]*>(.*?)</article>', content, re.DOTALL | re.IGNORECASE)
        if article_match:
            content = article_match.group(1)
    
    # Convert to readable text
    text = strip_html_tags(content)
    
    return text

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nAvailable documentation sections:")
        print("  /quickstart/integrate-tempo    - Getting started guide")
        print("  /quickstart/connection-details - Network connection info")
        print("  /quickstart/evm-compatibility  - EVM differences")
        print("  /quickstart/predeployed-contracts - Contract addresses")
        print("  /guide/use-accounts            - Account creation guide")
        print("  /guide/payments                - Payment guide")
        print("  /guide/issuance                - Stablecoin issuance")
        print("  /guide/stablecoin-exchange     - DEX guide")
        print("  /protocol                      - Protocol overview")
        print("  /protocol/tip20/overview       - TIP-20 token standard")
        print("  /protocol/tip20/spec           - TIP-20 specification")
        print("  /protocol/tip403/overview      - Policy registry")
        print("  /protocol/fees                 - Fee system")
        print("  /protocol/transactions         - Tempo transactions")
        print("  /protocol/blockspace/overview  - Block structure")
        print("  /protocol/exchange             - Stablecoin DEX")
        print("  /sdk/typescript                - TypeScript SDK")
        print("  /sdk/rust                      - Rust SDK")
        print("  /sdk/go                        - Go SDK")
        sys.exit(1)
    
    path = sys.argv[1]
    content = fetch_docs(path)
    
    if content:
        print(f"=== docs.tempo.xyz{path} ===\n")
        print(content)

if __name__ == "__main__":
    main()
