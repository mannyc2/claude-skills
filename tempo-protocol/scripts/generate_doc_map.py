#!/usr/bin/env python3
"""
Generate a documentation map for Tempo docs by discovering all available paths.

Usage:
    python3 generate_doc_map.py              # Generate map only
    python3 generate_doc_map.py --recache    # Generate map + cache critical docs

This script:
1. Discovers documentation structure (sitemap or crawl)
2. Validates all paths (filters out 404s)
3. Generates/updates references/docs-map.md
4. Optionally caches critical docs for offline use
"""

import sys
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
import re
import html
import os
from pathlib import Path

BASE_URL = "https://docs.tempo.xyz"
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
REFERENCES_DIR = SKILL_DIR / "references"

# Critical docs to cache for offline use
CRITICAL_DOCS = [
    "/protocol/tip20/overview",
    "/protocol/tip20/spec",
    "/guide/payments/send-payments",
    "/guide/use-accounts/embed-passkeys",
    "/quickstart/evm-compatibility",
]


def fetch_sitemap():
    """Try to fetch and parse sitemap.xml."""
    sitemap_url = f"{BASE_URL}/sitemap.xml"

    try:
        req = urllib.request.Request(
            sitemap_url,
            headers={'User-Agent': 'Mozilla/5.0 (compatible; TempoDocs/1.0)'}
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read().decode('utf-8')

        # Parse XML
        root = ET.fromstring(content)

        # Extract all <loc> URLs
        # Handle both with and without namespace
        locs = []
        for loc in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
            locs.append(loc.text)
        for loc in root.findall('.//loc'):  # Fallback without namespace
            locs.append(loc.text)

        # Extract paths from URLs
        paths = []
        for url in locs:
            if url.startswith(BASE_URL):
                path = url[len(BASE_URL):]
                if path and path != '/':
                    paths.append(path)

        return paths
    except Exception as e:
        print(f"Could not fetch sitemap: {e}")
        return None


def crawl_docs():
    """Crawl from homepage to discover docs (fallback if no sitemap)."""
    print("Crawling from homepage...")
    discovered = set()
    to_visit = ['/']
    visited = set()

    while to_visit and len(discovered) < 100:  # Limit to prevent infinite loops
        path = to_visit.pop(0)
        if path in visited:
            continue
        visited.add(path)

        url = f"{BASE_URL}{path}"
        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0 (compatible; TempoDocs/1.0)'}
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                content = response.read().decode('utf-8')

            # Find all internal links
            links = re.findall(r'href=["\']([^"\']*)["\']', content)
            for link in links:
                # Only internal docs links
                if link.startswith('/') and not link.startswith('//'):
                    # Remove anchors and query params
                    clean_link = link.split('#')[0].split('?')[0]
                    if clean_link and clean_link != '/' and clean_link not in visited:
                        discovered.add(clean_link)
                        to_visit.append(clean_link)
        except Exception as e:
            print(f"Could not crawl {path}: {e}")

    return list(discovered)


def validate_path(path):
    """Check if a path exists (200 OK)."""
    url = f"{BASE_URL}{path}"
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (compatible; TempoDocs/1.0)'}
        )
        req.get_method = lambda: 'HEAD'  # HEAD request for efficiency
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.code == 200
    except urllib.error.HTTPError as e:
        if e.code == 405:  # Method not allowed, try GET
            try:
                req = urllib.request.Request(
                    url,
                    headers={'User-Agent': 'Mozilla/5.0 (compatible; TempoDocs/1.0)'}
                )
                with urllib.request.urlopen(req, timeout=10) as response:
                    return response.code == 200
            except:
                return False
        return False
    except:
        return False


def fetch_page_title(path):
    """Fetch a page and extract its title."""
    url = f"{BASE_URL}{path}"
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (compatible; TempoDocs/1.0)'}
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read().decode('utf-8')

        # Try to find h1 or title
        h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.DOTALL | re.IGNORECASE)
        if h1_match:
            title = re.sub(r'<[^>]+>', '', h1_match.group(1))
            return html.unescape(title.strip())

        title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.DOTALL | re.IGNORECASE)
        if title_match:
            title = html.unescape(title_match.group(1).strip())
            # Remove common suffixes
            title = re.sub(r'\s*\|\s*Tempo.*$', '', title)
            return title.strip()

        return "Documentation"
    except:
        return "Documentation"


def categorize_paths(paths):
    """Organize paths by category."""
    categories = {
        'quickstart': [],
        'guide': [],
        'protocol': [],
        'sdk': [],
        'other': []
    }

    for path in paths:
        if path.startswith('/quickstart'):
            categories['quickstart'].append(path)
        elif path.startswith('/guide'):
            categories['guide'].append(path)
        elif path.startswith('/protocol'):
            categories['protocol'].append(path)
        elif path.startswith('/sdk'):
            categories['sdk'].append(path)
        else:
            categories['other'].append(path)

    return categories


def generate_docs_map_content(categorized_paths):
    """Generate markdown content for docs-map.md."""
    content = []
    content.append("# Tempo Documentation Map")
    content.append("")
    content.append(f"Complete navigation structure for {BASE_URL}. Use `scripts/fetch_docs.py` to retrieve any page.")
    content.append("")
    content.append(f"Last updated: {Path(__file__).name}")
    content.append("")

    category_titles = {
        'quickstart': 'Quickstart / Integration',
        'guide': 'Building Guides',
        'protocol': 'Protocol Specifications',
        'sdk': 'SDKs',
        'other': 'Other Resources'
    }

    for category, title in category_titles.items():
        paths = categorized_paths.get(category, [])
        if not paths:
            continue

        content.append(f"## {title}")
        content.append("")
        content.append("| Path | Description |")
        content.append("|------|-------------|")

        for path in sorted(paths):
            desc = fetch_page_title(path)
            content.append(f"| `{path}` | {desc} |")

        content.append("")

    # Add usage examples
    content.append("## Usage Examples")
    content.append("")
    content.append("```bash")
    content.append("# Fetch a specific docs page")
    content.append("python3 scripts/fetch_docs.py /protocol/tip20/spec")
    content.append("")
    content.append("# Regenerate this map")
    content.append("python3 scripts/generate_doc_map.py")
    content.append("```")
    content.append("")

    return '\n'.join(content)


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
    # Convert links
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


def cache_doc(path):
    """Fetch and cache a documentation page."""
    url = f"{BASE_URL}{path}"

    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (compatible; TempoDocs/1.0)'}
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read().decode('utf-8')
    except Exception as e:
        print(f"  Error fetching {path}: {e}")
        return False

    # Extract main content
    main_match = re.search(r'<main[^>]*>(.*?)</main>', content, re.DOTALL | re.IGNORECASE)
    if main_match:
        content = main_match.group(1)
    else:
        article_match = re.search(r'<article[^>]*>(.*?)</article>', content, re.DOTALL | re.IGNORECASE)
        if article_match:
            content = article_match.group(1)

    # Convert to markdown
    text = strip_html_tags(content)

    # Generate filename
    filename = path.strip('/').replace('/', '-') + '.md'
    filepath = REFERENCES_DIR / filename

    # Write to file
    with open(filepath, 'w') as f:
        f.write(f"# {path}\n\n")
        f.write(f"Source: {url}\n\n")
        f.write("---\n\n")
        f.write(text)

    print(f"  Cached: {filepath.name}")
    return True


def main():
    import sys

    recache = '--recache' in sys.argv

    print("=" * 60)
    print("Tempo Documentation Map Generator")
    print("=" * 60)
    print()

    # Step 1: Discover documentation structure
    print("Step 1: Discovering documentation structure...")
    paths = fetch_sitemap()

    if paths:
        print(f"  ✓ Found {len(paths)} paths from sitemap.xml")
    else:
        print("  ⚠ No sitemap found, crawling from homepage...")
        paths = crawl_docs()
        print(f"  ✓ Discovered {len(paths)} paths from crawling")

    if not paths:
        print("  ✗ Could not discover any paths")
        return 1

    print()

    # Step 2: Validate paths
    print("Step 2: Validating paths...")
    valid_paths = []
    invalid_count = 0

    for i, path in enumerate(paths, 1):
        if i % 10 == 0:
            print(f"  Checked {i}/{len(paths)}...")

        if validate_path(path):
            valid_paths.append(path)
        else:
            invalid_count += 1

    print(f"  ✓ {len(valid_paths)} valid paths")
    if invalid_count > 0:
        print(f"  ⚠ {invalid_count} invalid paths (404s) filtered out")
    print()

    # Step 3: Generate docs map
    print("Step 3: Generating documentation map...")
    categorized = categorize_paths(valid_paths)
    map_content = generate_docs_map_content(categorized)

    # Write to docs-map.md
    docs_map_path = REFERENCES_DIR / "docs-map.md"
    with open(docs_map_path, 'w') as f:
        f.write(map_content)

    print(f"  ✓ Updated {docs_map_path}")
    print()

    # Step 4: Cache critical docs (optional)
    if recache:
        print("Step 4: Caching critical documentation...")
        for path in CRITICAL_DOCS:
            if path in valid_paths:
                cache_doc(path)
            else:
                print(f"  ⚠ Skipping {path} (not found in valid paths)")
        print()

    print("=" * 60)
    print("✓ Documentation map generated successfully!")
    print("=" * 60)
    print()
    print(f"📄 Map file: {docs_map_path}")
    print(f"📁 Cached docs: {REFERENCES_DIR}")
    print()
    print("Usage:")
    print("  python3 scripts/fetch_docs.py <path>")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
