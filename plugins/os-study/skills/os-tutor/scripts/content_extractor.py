#!/usr/bin/env python3
"""
Content Extractor for Cheat Sheet Builder

Extracts relevant content (formulas, tables, examples) from pattern guides
based on topic IDs.
"""

import re
from pathlib import Path
from typing import Dict, Optional

# Paths
SCRIPT_DIR = Path(__file__).parent
PATTERN_DIR = SCRIPT_DIR.parent / "references" / "patterns"

# Topic to content mapping
TOPIC_CONTENT_MAP = {
    "cpu_scheduling_fcfs": {
        "guide": "scheduling.md",
        "display_name": "FCFS Scheduling",
        "formula": "Avg Wait = Σ(wait)/n",
        "table_keyword": "FCFS",
        "notes": "No preemption, convoy effect with long CPU-bound processes"
    },
    "cpu_scheduling_sjf": {
        "guide": "scheduling.md",
        "display_name": "SJF (Shortest Job First)",
        "formula": "Avg Wait = Σ(wait)/n | Optimal (minimum)",
        "table_keyword": "SJF",
        "notes": "Optimal avg wait time, risk of starvation for long jobs"
    },
    "cpu_scheduling_srtf": {
        "guide": "scheduling.md",
        "display_name": "SRTF (Shortest Remaining Time First)",
        "formula": "Preempt when new job with shorter remaining time arrives",
        "table_keyword": "SRTF",
        "notes": "Preemptive SJF, check at each arrival, optimal for preemptive"
    },
    "cpu_scheduling_rr": {
        "guide": "scheduling.md",
        "display_name": "Round Robin",
        "formula": "q=quantum | Overhead = ctx_switch/(quantum+ctx_switch) | Rule: 80% bursts < q",
        "table_keyword": "Round Robin",
        "notes": "Time quantum critical: too small→overhead, too large→FCFS"
    },
    "memory_paging_basic": {
        "guide": "memory-management.md",
        "display_name": "Address Translation (Paging)",
        "formula": "p=LA/PS, d=LA%PS, PA=(Frame×PS)+d",
        "table_keyword": "Paging",
        "notes": "Eliminates external fragmentation, internal frag ≈ PS/2 avg"
    },
    "memory_tlb_eat": {
        "guide": "memory-management.md",
        "display_name": "TLB Effective Access Time",
        "formula": "EAT = (Hit×HR) + (Miss×(1-HR)) | Miss = TLB+PT+Mem",
        "table_keyword": "TLB",
        "notes": "TLB Reach = TLB_size × page_size | Critical for performance"
    },
    "page_replacement_fifo": {
        "guide": "page-replacement.md",
        "display_name": "FIFO Page Replacement",
        "formula": "Replace oldest page in memory",
        "table_keyword": "FIFO",
        "notes": "Belady's Anomaly: MORE frames can cause MORE faults!"
    },
    "page_replacement_lru": {
        "guide": "page-replacement.md",
        "display_name": "LRU Page Replacement",
        "formula": "Replace least recently used page",
        "table_keyword": "LRU",
        "notes": "Approximates Optimal, no Belady's Anomaly, expensive to implement"
    },
    "sync_bounded_buffer": {
        "guide": "synchronization.md",
        "display_name": "Bounded Buffer (Producer-Consumer)",
        "formula": "empty=n, full=0, mutex=1 | Producer: empty.wait() mutex.wait() [add] mutex.signal() full.signal()",
        "table_keyword": "Bounded-Buffer",
        "notes": "Classic sync problem, use counting semaphores for slots"
    },
    "sync_dining_philosophers": {
        "guide": "synchronization.md",
        "display_name": "Dining Philosophers",
        "formula": "Deadlock if all pick up left fork | Solution: Asymmetric, or pick both atomically",
        "table_keyword": "Dining Philosophers",
        "notes": "Illustrates deadlock, monitor solution prevents circular wait"
    }
}


def extract_table_row(content: str, keyword: str) -> Optional[str]:
    """Extract row from markdown table containing keyword."""
    lines = content.split('\n')

    for i, line in enumerate(lines):
        if '|' in line and keyword in line and not line.strip().startswith('|---'):
            # Clean up the row
            row = line.strip()
            # Remove leading/trailing pipes and extra spaces
            cells = [cell.strip() for cell in row.split('|')[1:-1]]
            return " | ".join(cells)

    return None


def extract_section(content: str, header: str, max_lines: int = 20) -> Optional[str]:
    """Extract content between header and next same-level header."""
    lines = content.split('\n')
    header_level = header.count('#')

    in_section = False
    section_lines = []

    for line in lines:
        # Check if we've hit the target header
        if header.lower() in line.lower() and line.startswith('#' * header_level):
            in_section = True
            continue

        # If in section and hit another same-level header, stop
        if in_section and line.startswith('#' * header_level + ' '):
            break

        # Collect lines from section
        if in_section:
            section_lines.append(line)

            if len(section_lines) >= max_lines:
                break

    if not section_lines:
        return None

    return '\n'.join(section_lines).strip()


def condense_example(example: str, max_lines: int = 3) -> str:
    """Condense example to essential parts."""
    lines = example.split('\n')

    # Filter out empty lines and markdown formatting
    essential_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('```') and not stripped.startswith('#'):
            essential_lines.append(stripped)

            if len(essential_lines) >= max_lines:
                break

    return " | ".join(essential_lines)


def get_content_for_topic(topic_id: str) -> Optional[Dict]:
    """
    Get relevant content for a topic from pattern guides.

    Returns:
        {
            "topic_id": "cpu_scheduling_srtf",
            "display_name": "SRTF Scheduling",
            "formula": "...",
            "table_row": "...",
            "example": "...",
            "notes": "..."
        }
    """
    # Check if topic has mapping
    if topic_id not in TOPIC_CONTENT_MAP:
        # Fallback: return basic info
        display_name = topic_id.replace("_", " ").title()
        return {
            "topic_id": topic_id,
            "display_name": display_name,
            "formula": None,
            "table_row": None,
            "example": None,
            "notes": "No content mapping available (add manually)"
        }

    mapping = TOPIC_CONTENT_MAP[topic_id]
    guide_path = PATTERN_DIR / mapping["guide"]

    # Read pattern guide
    if not guide_path.exists():
        return None

    with open(guide_path, 'r') as f:
        content = f.read()

    # Extract table row if keyword provided
    table_row = None
    if "table_keyword" in mapping:
        table_row = extract_table_row(content, mapping["table_keyword"])

    # Get formula from mapping
    formula = mapping.get("formula")

    # Get notes from mapping
    notes = mapping.get("notes")

    # Try to find example section (optional)
    example = None
    if "example_header" in mapping:
        example_section = extract_section(content, mapping["example_header"], max_lines=10)
        if example_section:
            example = condense_example(example_section, max_lines=2)

    return {
        "topic_id": topic_id,
        "display_name": mapping["display_name"],
        "formula": formula,
        "table_row": table_row,
        "example": example,
        "notes": notes
    }


def main():
    """Test content extraction."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python content_extractor.py <topic_id>")
        print(f"\nAvailable topics: {', '.join(TOPIC_CONTENT_MAP.keys())}")
        return

    topic_id = sys.argv[1]
    content = get_content_for_topic(topic_id)

    if content:
        import json
        print(json.dumps(content, indent=2))
    else:
        print(f"No content found for topic: {topic_id}")


if __name__ == "__main__":
    main()
