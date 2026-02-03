#!/usr/bin/env python3
"""
Cheat Sheet Builder for OS Study Skill

Manages dynamic exam cheat sheet that builds based on topics you struggle with.
Integrates with BKT tracker to suggest topics with low mastery (P(known) < 0.5).

Usage:
    python cheat_sheet_builder.py check_suggest <topic_id>
    python cheat_sheet_builder.py add <topic_id> [--note "custom note"]
    python cheat_sheet_builder.py remove <topic_id>
    python cheat_sheet_builder.py list
    python cheat_sheet_builder.py generate [--max-topics 30]
    python cheat_sheet_builder.py status
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Paths
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
CHEAT_SHEET_FILE = DATA_DIR / "cheat_sheet.json"
PROGRESS_FILE = DATA_DIR / "progress.json"
OUTPUT_FILE = DATA_DIR / "exam-cheat-sheet.md"


def load_cheat_sheet() -> Dict:
    """Load cheat sheet data from JSON file."""
    if CHEAT_SHEET_FILE.exists():
        with open(CHEAT_SHEET_FILE, 'r') as f:
            return json.load(f)
    return {"items": [], "metadata": {"last_generated": None, "exam_date": None}}


def save_cheat_sheet(data: Dict):
    """Save cheat sheet data to JSON file."""
    with open(CHEAT_SHEET_FILE, 'w') as f:
        json.dump(data, f, indent=2, sort_keys=False)


def load_bkt_state(topic_id: str) -> Optional[Dict]:
    """Load BKT state for a topic from progress.json."""
    if not PROGRESS_FILE.exists():
        return None

    with open(PROGRESS_FILE, 'r') as f:
        progress = json.load(f)

    return progress.get("topics", {}).get(topic_id)


def calculate_priority(topic_id: str, item: Dict) -> float:
    """
    Calculate priority score for cheat sheet inclusion.

    Higher score = more important (should appear first on cheat sheet).
    """
    bkt = load_bkt_state(topic_id)
    if not bkt:
        # No BKT data, use when topic was added as fallback
        return 50.0

    p_known = bkt.get("p_known", 0.5)
    attempts = bkt.get("attempts", 0)

    # Base score: inverse of mastery (struggling topics score higher)
    base_score = (1 - p_known) * 100  # Range: 0-100

    # Struggle bonus: many attempts but still low mastery
    struggle_bonus = 50 if (attempts >= 3 and p_known < 0.4) else 0

    # Manual override
    manual_boost = 50 if item.get("must_include", False) else 0

    return base_score + struggle_bonus + manual_boost


def check_suggest(topic_id: str) -> Dict:
    """
    Check if topic should be suggested for addition to cheat sheet.

    Returns: {"suggest": bool, "reason": str}
    """
    # Load BKT state
    bkt = load_bkt_state(topic_id)
    if not bkt:
        return {"suggest": False, "reason": "No BKT data yet (first attempt)"}

    p_known = bkt.get("p_known", 0.5)
    attempts = bkt.get("attempts", 0)

    # Check if already in cheat sheet
    cheat_sheet = load_cheat_sheet()
    topic_ids = [item["topic_id"] for item in cheat_sheet["items"]]
    if topic_id in topic_ids:
        return {"suggest": False, "reason": "Already in cheat sheet"}

    # Suggestion criteria
    if p_known >= 0.5:
        return {"suggest": False, "reason": f"Mastery good (P(known)={p_known:.0%})"}

    if attempts < 3:
        return {"suggest": False, "reason": f"Need more attempts (only {attempts})"}

    # Suggest!
    return {
        "suggest": True,
        "reason": f"Low mastery (P(known)={p_known:.0%}) after {attempts} attempts"
    }


def add_topic(topic_id: str, user_note: str = ""):
    """Add topic to cheat sheet."""
    cheat_sheet = load_cheat_sheet()

    # Check if already exists
    topic_ids = [item["topic_id"] for item in cheat_sheet["items"]]
    if topic_id in topic_ids:
        print(f"Topic '{topic_id}' already in cheat sheet.")
        return

    # Get BKT state
    bkt = load_bkt_state(topic_id)
    p_known = bkt.get("p_known", 0.0) if bkt else 0.0

    # Infer display name from topic_id
    display_name = topic_id.replace("_", " ").title()

    # Create item
    item = {
        "topic_id": topic_id,
        "display_name": display_name,
        "added_date": datetime.now().isoformat(),
        "p_known_when_added": p_known,
        "must_include": False,
        "user_notes": user_note
    }

    cheat_sheet["items"].append(item)
    save_cheat_sheet(cheat_sheet)

    print(f"✅ Added '{display_name}' to cheat sheet (P(known)={p_known:.0%})")


def remove_topic(topic_id: str):
    """Remove topic from cheat sheet."""
    cheat_sheet = load_cheat_sheet()

    original_count = len(cheat_sheet["items"])
    cheat_sheet["items"] = [
        item for item in cheat_sheet["items"]
        if item["topic_id"] != topic_id
    ]

    if len(cheat_sheet["items"]) == original_count:
        print(f"Topic '{topic_id}' not found in cheat sheet.")
        return

    save_cheat_sheet(cheat_sheet)
    print(f"✅ Removed '{topic_id}' from cheat sheet")


def list_topics():
    """List all topics in cheat sheet sorted by priority."""
    cheat_sheet = load_cheat_sheet()

    if not cheat_sheet["items"]:
        print("Cheat sheet is empty. Add topics with 'add <topic_id>'")
        return

    # Calculate priorities and sort
    topics_with_priority = []
    for item in cheat_sheet["items"]:
        priority = calculate_priority(item["topic_id"], item)
        bkt = load_bkt_state(item["topic_id"])
        current_p_known = bkt.get("p_known", 0.0) if bkt else 0.0

        topics_with_priority.append({
            "topic_id": item["topic_id"],
            "display_name": item["display_name"],
            "priority": priority,
            "p_known": current_p_known,
            "added_when_p_known": item["p_known_when_added"]
        })

    # Sort by priority (highest first)
    topics_with_priority.sort(key=lambda x: x["priority"], reverse=True)

    print(f"\nCheat Sheet Topics ({len(topics_with_priority)} items, sorted by priority):\n")
    print(f"{'Rank':<6} {'Priority':<10} {'P(known)':<12} {'Topic':<40}")
    print("-" * 70)

    for rank, topic in enumerate(topics_with_priority, 1):
        print(
            f"{rank:<6} "
            f"{topic['priority']:<10.0f} "
            f"{topic['p_known']:<12.0%} "
            f"{topic['display_name']:<40}"
        )


def status():
    """Show cheat sheet status summary."""
    cheat_sheet = load_cheat_sheet()
    item_count = len(cheat_sheet["items"])
    last_generated = cheat_sheet["metadata"].get("last_generated")

    print(f"\nCheat Sheet Status:")
    print(f"  Topics: {item_count}")
    print(f"  Last generated: {last_generated or 'Never'}")

    if item_count > 0:
        # Calculate average mastery
        total_p_known = 0
        count = 0
        for item in cheat_sheet["items"]:
            bkt = load_bkt_state(item["topic_id"])
            if bkt:
                total_p_known += bkt.get("p_known", 0)
                count += 1

        if count > 0:
            avg_mastery = total_p_known / count
            print(f"  Average mastery: {avg_mastery:.0%}")


def generate_cheat_sheet(max_topics: int = 30):
    """Generate final exam-cheat-sheet.md file."""
    cheat_sheet = load_cheat_sheet()

    if not cheat_sheet["items"]:
        print("Error: Cheat sheet is empty. Add topics first.")
        return

    # Import content extractor
    try:
        from content_extractor import get_content_for_topic
    except ImportError:
        print("Error: content_extractor.py not found. Make sure it exists in the scripts directory.")
        return

    # Calculate priorities and sort
    topics_with_priority = []
    for item in cheat_sheet["items"]:
        priority = calculate_priority(item["topic_id"], item)
        topics_with_priority.append((priority, item))

    topics_with_priority.sort(key=lambda x: x[0], reverse=True)

    # Limit to max_topics
    if max_topics and len(topics_with_priority) > max_topics:
        topics_with_priority = topics_with_priority[:max_topics]

    # Generate markdown
    lines = []
    lines.append(f"# OS Exam Cheat Sheet")
    lines.append(f"")
    lines.append(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    lines.append(f"Topics: {len(topics_with_priority)} (prioritized by struggle level)")
    lines.append(f"")
    lines.append("---")
    lines.append("")

    # Group by category
    categories = {
        "CPU Scheduling": [],
        "Synchronization": [],
        "Memory Management": [],
        "Page Replacement": [],
        "Virtualization": []
    }

    for priority, item in topics_with_priority:
        topic_id = item["topic_id"]
        display_name = item["display_name"]

        # Get content
        content = get_content_for_topic(topic_id)
        if not content:
            continue

        # Determine category
        category = "CPU Scheduling"  # Default
        if "sync" in topic_id or "semaphore" in topic_id or "mutex" in topic_id:
            category = "Synchronization"
        elif "memory" in topic_id or "tlb" in topic_id or "paging" in topic_id:
            category = "Memory Management"
        elif "page_replacement" in topic_id or "fifo" in topic_id or "lru" in topic_id:
            category = "Page Replacement"
        elif "virtual" in topic_id or "hypervisor" in topic_id:
            category = "Virtualization"

        categories[category].append((display_name, content, priority))

    # Write each category
    for category, items in categories.items():
        if not items:
            continue

        lines.append(f"## {category} ({len(items)} topics)")
        lines.append("")

        for display_name, content, priority in items:
            # Format content densely
            lines.append(f"**{display_name}**:")

            if content.get("formula"):
                lines.append(f"  • Formula: `{content['formula']}`")

            if content.get("table_row"):
                lines.append(f"  • {content['table_row']}")

            if content.get("example"):
                lines.append(f"  • Example: {content['example']}")

            if content.get("notes"):
                lines.append(f"  • {content['notes']}")

            lines.append("")

    # Add footer
    lines.append("---")
    lines.append("")
    lines.append("*Focus on these topics - they're your weak spots based on BKT mastery tracking.*")

    # Write to file
    output_content = "\n".join(lines)
    with open(OUTPUT_FILE, 'w') as f:
        f.write(output_content)

    # Update metadata
    cheat_sheet["metadata"]["last_generated"] = datetime.now().isoformat()
    save_cheat_sheet(cheat_sheet)

    print(f"✅ Generated cheat sheet: {OUTPUT_FILE}")
    print(f"   Topics included: {len(topics_with_priority)}")


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1]

    if command == "check_suggest":
        if len(sys.argv) != 3:
            print("Usage: python cheat_sheet_builder.py check_suggest <topic_id>")
            return

        topic_id = sys.argv[2]
        result = check_suggest(topic_id)
        print(json.dumps(result, indent=2))

    elif command == "add":
        if len(sys.argv) < 3:
            print("Usage: python cheat_sheet_builder.py add <topic_id> [--note \"note\"]")
            return

        topic_id = sys.argv[2]
        user_note = ""

        # Parse optional --note
        if len(sys.argv) > 3 and sys.argv[3] == "--note" and len(sys.argv) > 4:
            user_note = sys.argv[4]

        add_topic(topic_id, user_note)

    elif command == "remove":
        if len(sys.argv) != 3:
            print("Usage: python cheat_sheet_builder.py remove <topic_id>")
            return

        topic_id = sys.argv[2]
        remove_topic(topic_id)

    elif command == "list":
        list_topics()

    elif command == "generate":
        max_topics = 30
        if len(sys.argv) > 2 and sys.argv[2].startswith("--max-topics"):
            if len(sys.argv) > 3:
                max_topics = int(sys.argv[3])
            elif "=" in sys.argv[2]:
                max_topics = int(sys.argv[2].split("=")[1])

        generate_cheat_sheet(max_topics)

    elif command == "status":
        status()

    else:
        print(f"Unknown command: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()
