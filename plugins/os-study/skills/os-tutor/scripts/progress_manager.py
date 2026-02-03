#!/usr/bin/env python3
"""
Progress Manager for DSA Study skill.

Usage:
    progress_manager.py load                    # Load and display progress
    progress_manager.py save                    # Save current session (updates timestamp)
    progress_manager.py init                    # Initialize fresh progress file
    progress_manager.py streak                  # Get current streak info
    progress_manager.py stats                   # Get global statistics
    progress_manager.py log <topic> <action>    # Log a study action

Progress Schema:
{
    "user_id": "default",
    "last_session": "ISO timestamp",
    "global_stats": {
        "total_problems": int,
        "streak_days": int,
        "longest_streak": int,
        "total_time_minutes": int,
        "sessions_count": int
    },
    "topics": { ... },      # Managed by knowledge_tracker.py
    "review_queue": [ ... ] # Managed by spaced_scheduler.py
    "session_log": [ ... ]  # Recent activity log
}
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import TypedDict

PROGRESS_FILE = Path(__file__).parent.parent / "data" / "progress.json"


class GlobalStats(TypedDict):
    total_problems: int
    streak_days: int
    longest_streak: int
    total_time_minutes: int
    sessions_count: int


def get_default_progress() -> dict:
    """Return default progress structure."""
    return {
        "user_id": "default",
        "created_at": datetime.now().isoformat(),
        "last_session": None,
        "global_stats": {
            "total_problems": 0,
            "streak_days": 0,
            "longest_streak": 0,
            "total_time_minutes": 0,
            "sessions_count": 0,
        },
        "topics": {},
        "review_queue": [],
        "session_log": [],
    }


def load_progress() -> dict:
    """Load progress from JSON file, creating if needed."""
    if not PROGRESS_FILE.exists():
        progress = get_default_progress()
        save_progress_file(progress)
        return progress

    with open(PROGRESS_FILE) as f:
        progress = json.load(f)

    # Ensure all required fields exist
    defaults = get_default_progress()
    for key in defaults:
        if key not in progress:
            progress[key] = defaults[key]

    return progress


def save_progress_file(progress: dict) -> None:
    """Save progress to JSON file."""
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)


def calculate_streak(progress: dict) -> int:
    """Calculate current streak based on session history."""
    last_session = progress.get("last_session")
    if not last_session:
        return 0

    try:
        last_date = datetime.fromisoformat(last_session).date()
    except (ValueError, TypeError):
        return 0

    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    # If last session was today, return current streak
    if last_date == today:
        return progress["global_stats"].get("streak_days", 1)

    # If last session was yesterday, streak continues
    if last_date == yesterday:
        return progress["global_stats"].get("streak_days", 0)

    # Otherwise streak is broken
    return 0


def update_streak(progress: dict) -> dict:
    """Update streak when starting a new session."""
    last_session = progress.get("last_session")
    today = datetime.now().date()
    stats = progress["global_stats"]

    if not last_session:
        # First session ever
        stats["streak_days"] = 1
        stats["longest_streak"] = 1
        return {"streak": 1, "status": "started", "message": "Started your learning streak!"}

    try:
        last_date = datetime.fromisoformat(last_session).date()
    except (ValueError, TypeError):
        stats["streak_days"] = 1
        return {"streak": 1, "status": "reset", "message": "Streak reset due to invalid date"}

    if last_date == today:
        # Already studied today
        return {
            "streak": stats["streak_days"],
            "status": "continued",
            "message": f"Welcome back! Day {stats['streak_days']} streak continues",
        }

    yesterday = today - timedelta(days=1)
    if last_date == yesterday:
        # Streak continues
        stats["streak_days"] += 1
        if stats["streak_days"] > stats.get("longest_streak", 0):
            stats["longest_streak"] = stats["streak_days"]
        return {
            "streak": stats["streak_days"],
            "status": "extended",
            "message": f"Streak extended to {stats['streak_days']} days!",
        }

    # Streak broken
    days_missed = (today - last_date).days - 1
    old_streak = stats["streak_days"]
    stats["streak_days"] = 1
    return {
        "streak": 1,
        "status": "broken",
        "old_streak": old_streak,
        "days_missed": days_missed,
        "message": f"Streak reset after {days_missed} days. Starting fresh!",
    }


def load_and_display() -> dict:
    """Load progress and return summary."""
    progress = load_progress()
    stats = progress["global_stats"]

    streak_info = calculate_streak(progress)
    topics = progress.get("topics", {})
    review_queue = progress.get("review_queue", [])

    # Count mastery levels
    mastered = sum(1 for t in topics.values() if t.get("p_known", 0) >= 0.95)
    in_progress = sum(1 for t in topics.values() if 0 < t.get("p_known", 0) < 0.95)

    # Count due reviews
    today = datetime.now().strftime("%Y-%m-%d")
    due_count = sum(1 for r in review_queue if r.get("due_date", "") <= today)

    return {
        "loaded": True,
        "last_session": progress.get("last_session"),
        "streak_days": streak_info,
        "longest_streak": stats.get("longest_streak", 0),
        "total_problems": stats.get("total_problems", 0),
        "sessions_count": stats.get("sessions_count", 0),
        "topics_mastered": mastered,
        "topics_in_progress": in_progress,
        "reviews_due": due_count,
    }


def save_session() -> dict:
    """Save session with updated timestamp and stats."""
    progress = load_progress()

    # Update streak
    streak_result = update_streak(progress)

    # Update session info
    progress["last_session"] = datetime.now().isoformat()
    progress["global_stats"]["sessions_count"] += 1

    save_progress_file(progress)

    return {
        "saved": True,
        "timestamp": progress["last_session"],
        "streak": streak_result,
        "sessions_count": progress["global_stats"]["sessions_count"],
    }


def init_progress() -> dict:
    """Initialize a fresh progress file."""
    if PROGRESS_FILE.exists():
        # Backup existing
        backup_path = PROGRESS_FILE.with_suffix(".json.bak")
        PROGRESS_FILE.rename(backup_path)

    progress = get_default_progress()
    save_progress_file(progress)

    return {
        "initialized": True,
        "path": str(PROGRESS_FILE),
        "message": "Fresh progress file created",
    }


def get_streak_info() -> dict:
    """Get detailed streak information."""
    progress = load_progress()
    stats = progress["global_stats"]
    current_streak = calculate_streak(progress)

    return {
        "current_streak": current_streak,
        "longest_streak": stats.get("longest_streak", 0),
        "last_session": progress.get("last_session"),
        "sessions_count": stats.get("sessions_count", 0),
    }


def get_global_stats() -> dict:
    """Get global statistics."""
    progress = load_progress()
    stats = progress["global_stats"]
    topics = progress.get("topics", {})

    # Calculate topic stats
    total_attempts = sum(t.get("attempts", 0) for t in topics.values())
    total_correct = sum(t.get("correct", 0) for t in topics.values())
    avg_mastery = (
        sum(t.get("p_known", 0) for t in topics.values()) / len(topics)
        if topics else 0
    )

    return {
        "sessions_count": stats.get("sessions_count", 0),
        "total_problems": stats.get("total_problems", 0),
        "streak_days": calculate_streak(progress),
        "longest_streak": stats.get("longest_streak", 0),
        "total_topics": len(topics),
        "total_attempts": total_attempts,
        "total_correct": total_correct,
        "overall_accuracy": round(total_correct / total_attempts, 2) if total_attempts > 0 else 0,
        "average_mastery": round(avg_mastery, 3),
    }


def log_action(topic: str, action: str) -> dict:
    """Log a study action to session log."""
    progress = load_progress()

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "topic": topic,
        "action": action,
    }

    session_log = progress.setdefault("session_log", [])
    session_log.append(log_entry)

    # Keep only last 100 entries
    if len(session_log) > 100:
        progress["session_log"] = session_log[-100:]

    # Update problem count if action indicates completion
    if action in ("completed", "answered", "reviewed"):
        progress["global_stats"]["total_problems"] += 1

    save_progress_file(progress)

    return {
        "logged": True,
        "entry": log_entry,
        "total_problems": progress["global_stats"]["total_problems"],
    }


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: progress_manager.py <command> [args]")
        print("Commands: load, save, init, streak, stats, log")
        sys.exit(1)

    command = sys.argv[1]

    if command == "load":
        result = load_and_display()
        print(json.dumps(result, indent=2))

    elif command == "save":
        result = save_session()
        print(json.dumps(result, indent=2))

    elif command == "init":
        result = init_progress()
        print(json.dumps(result, indent=2))

    elif command == "streak":
        result = get_streak_info()
        print(json.dumps(result, indent=2))

    elif command == "stats":
        result = get_global_stats()
        print(json.dumps(result, indent=2))

    elif command == "log":
        if len(sys.argv) < 4:
            print("Usage: progress_manager.py log <topic> <action>")
            sys.exit(1)
        topic = sys.argv[2]
        action = sys.argv[3]
        result = log_action(topic, action)
        print(json.dumps(result, indent=2))

    else:
        print(f"Unknown command: {command}")
        print("Commands: load, save, init, streak, stats, log")
        sys.exit(1)


if __name__ == "__main__":
    main()
