#!/usr/bin/env python3
"""
Spaced Repetition Scheduler using SM-2 Algorithm

Implements spaced repetition scheduling for OS topics based on the SuperMemo SM-2 algorithm.
Tracks review intervals, ease factors, and next review dates for each topic.

Usage:
    python spaced_scheduler.py review <topic_id> <quality>  # Record review result
    python spaced_scheduler.py next                         # Get next topic to review
    python spaced_scheduler.py due                          # List all topics due for review
    python spaced_scheduler.py stats <topic_id>             # Show scheduling stats for topic
    python spaced_scheduler.py reset <topic_id>             # Reset scheduling for topic
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, List, Tuple

# SM-2 Algorithm Constants
DEFAULT_EASE_FACTOR = 2.5  # Starting ease factor for new topics
MIN_EASE_FACTOR = 1.3      # Minimum ease factor (prevents decay below this)
EASE_BONUS = 0.1           # Added to ease factor for quality 4-5
EASE_PENALTY = 0.2         # Subtracted from ease factor for quality < 3

# Initial intervals (in days)
INITIAL_INTERVALS = {
    0: 0,      # Quality 0-2: Reset to beginning
    1: 0,
    2: 0,
    3: 1,      # Quality 3: Review tomorrow
    4: 6,      # Quality 4: Review in 6 days
    5: 6       # Quality 5: Review in 6 days
}

# Noise factor to prevent bunching (±5%)
NOISE_FACTOR = 0.05


class SpacedScheduler:
    """SM-2 Spaced Repetition Scheduler"""

    def __init__(self, data_dir: Path = None):
        """Initialize scheduler with data directory."""
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.schedule_file = self.data_dir / "schedule.json"
        self.schedule = self._load_schedule()

    def _load_schedule(self) -> Dict:
        """Load schedule data from JSON file."""
        if self.schedule_file.exists():
            with open(self.schedule_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_schedule(self):
        """Save schedule data to JSON file."""
        with open(self.schedule_file, 'w') as f:
            json.dump(self.schedule, f, indent=2, sort_keys=True)

    def _get_topic_data(self, topic_id: str) -> Dict:
        """Get or initialize topic scheduling data."""
        if topic_id not in self.schedule:
            self.schedule[topic_id] = {
                "ease_factor": DEFAULT_EASE_FACTOR,
                "interval": 0,
                "repetitions": 0,
                "next_review": datetime.now().isoformat(),
                "last_review": None,
                "total_reviews": 0,
                "quality_history": []
            }
        return self.schedule[topic_id]

    def _add_noise(self, interval: float) -> float:
        """Add random noise to interval to prevent bunching.

        Returns interval with ±5% random variation.
        """
        noise = random.uniform(-NOISE_FACTOR, NOISE_FACTOR)
        return interval * (1 + noise)

    def review(self, topic_id: str, quality: int) -> Dict:
        """
        Record a review of a topic and calculate next review date.

        Args:
            topic_id: Unique identifier for the topic
            quality: Quality rating (0-5)
                0: Complete blackout
                1: Incorrect, but recognized
                2: Incorrect, seemed easy
                3: Correct with difficulty
                4: Correct with hesitation
                5: Perfect recall

        Returns:
            Dictionary with updated scheduling information
        """
        if not 0 <= quality <= 5:
            raise ValueError("Quality must be between 0 and 5")

        topic = self._get_topic_data(topic_id)
        now = datetime.now()

        # Update review history
        topic["last_review"] = now.isoformat()
        topic["total_reviews"] += 1
        topic["quality_history"].append({
            "quality": quality,
            "timestamp": now.isoformat()
        })

        # Keep only last 20 reviews in history
        if len(topic["quality_history"]) > 20:
            topic["quality_history"] = topic["quality_history"][-20:]

        # SM-2 Algorithm Implementation

        # 1. Update ease factor based on quality
        if quality >= 3:
            # Successful recall
            topic["ease_factor"] += (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        else:
            # Failed recall
            topic["ease_factor"] -= EASE_PENALTY

        # Ensure ease factor stays within bounds
        topic["ease_factor"] = max(MIN_EASE_FACTOR, topic["ease_factor"])

        # 2. Calculate new interval
        if quality < 3:
            # Failed: Reset to beginning
            topic["repetitions"] = 0
            topic["interval"] = 0
            next_interval = 1  # Review tomorrow
        else:
            # Successful: Calculate next interval
            if topic["repetitions"] == 0:
                next_interval = 1
            elif topic["repetitions"] == 1:
                next_interval = 6
            else:
                next_interval = topic["interval"] * topic["ease_factor"]

            topic["repetitions"] += 1

        # Add noise to prevent bunching
        next_interval = self._add_noise(next_interval)
        topic["interval"] = next_interval

        # 3. Calculate next review date
        next_review = now + timedelta(days=next_interval)
        topic["next_review"] = next_review.isoformat()

        self._save_schedule()

        return {
            "topic_id": topic_id,
            "quality": quality,
            "ease_factor": round(topic["ease_factor"], 2),
            "interval_days": round(next_interval, 1),
            "next_review": next_review.strftime("%Y-%m-%d %H:%M"),
            "repetitions": topic["repetitions"],
            "total_reviews": topic["total_reviews"]
        }

    def get_next_topic(self) -> Optional[str]:
        """
        Get the next topic due for review.

        Returns:
            Topic ID of the most overdue topic, or None if nothing is due
        """
        due_topics = self.get_due_topics()
        if not due_topics:
            return None

        # Return the most overdue topic
        return due_topics[0][0]

    def get_due_topics(self, limit: int = None) -> List[Tuple[str, datetime]]:
        """
        Get all topics that are due for review, sorted by urgency.

        Args:
            limit: Maximum number of topics to return

        Returns:
            List of (topic_id, next_review_date) tuples, sorted by urgency
        """
        now = datetime.now()
        due = []

        for topic_id, data in self.schedule.items():
            next_review = datetime.fromisoformat(data["next_review"])
            if next_review <= now:
                due.append((topic_id, next_review))

        # Sort by next_review date (most overdue first)
        due.sort(key=lambda x: x[1])

        if limit:
            due = due[:limit]

        return due

    def get_upcoming_topics(self, days: int = 7, limit: int = 10) -> List[Tuple[str, datetime]]:
        """
        Get topics that will be due within the next N days.

        Args:
            days: Number of days to look ahead
            limit: Maximum number of topics to return

        Returns:
            List of (topic_id, next_review_date) tuples
        """
        now = datetime.now()
        cutoff = now + timedelta(days=days)
        upcoming = []

        for topic_id, data in self.schedule.items():
            next_review = datetime.fromisoformat(data["next_review"])
            if now < next_review <= cutoff:
                upcoming.append((topic_id, next_review))

        # Sort by next_review date (soonest first)
        upcoming.sort(key=lambda x: x[1])

        return upcoming[:limit] if limit else upcoming

    def get_stats(self, topic_id: str) -> Optional[Dict]:
        """
        Get scheduling statistics for a topic.

        Returns:
            Dictionary with topic stats, or None if topic not found
        """
        if topic_id not in self.schedule:
            return None

        topic = self.schedule[topic_id]
        next_review = datetime.fromisoformat(topic["next_review"])
        now = datetime.now()

        # Calculate average quality from history
        if topic["quality_history"]:
            avg_quality = sum(r["quality"] for r in topic["quality_history"]) / len(topic["quality_history"])
        else:
            avg_quality = 0

        # Calculate days until next review (can be negative if overdue)
        days_until = (next_review - now).total_seconds() / 86400

        return {
            "topic_id": topic_id,
            "ease_factor": round(topic["ease_factor"], 2),
            "current_interval_days": round(topic["interval"], 1),
            "repetitions": topic["repetitions"],
            "total_reviews": topic["total_reviews"],
            "average_quality": round(avg_quality, 2),
            "next_review": next_review.strftime("%Y-%m-%d %H:%M"),
            "days_until_review": round(days_until, 1),
            "status": "overdue" if days_until < 0 else "upcoming",
            "last_review": topic["last_review"],
            "recent_quality": [r["quality"] for r in topic["quality_history"][-5:]]
        }

    def reset_topic(self, topic_id: str):
        """Reset scheduling data for a topic."""
        if topic_id in self.schedule:
            del self.schedule[topic_id]
            self._save_schedule()

    def get_review_queue(self, limit: int = 10) -> List[Dict]:
        """
        Get prioritized review queue combining due and upcoming topics.

        Args:
            limit: Maximum number of topics to return

        Returns:
            List of topic info dictionaries with review details
        """
        queue = []

        # Add overdue topics (highest priority)
        due = self.get_due_topics()
        for topic_id, next_review in due:
            stats = self.get_stats(topic_id)
            stats["priority"] = "overdue"
            queue.append(stats)

        # Add upcoming topics if we haven't hit the limit
        if len(queue) < limit:
            upcoming = self.get_upcoming_topics(days=7, limit=limit - len(queue))
            for topic_id, next_review in upcoming:
                stats = self.get_stats(topic_id)
                stats["priority"] = "upcoming"
                queue.append(stats)

        return queue[:limit]


def main():
    """CLI interface for spaced scheduler."""
    import sys

    scheduler = SpacedScheduler()

    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1]

    if command == "review":
        if len(sys.argv) != 4:
            print("Usage: python spaced_scheduler.py review <topic_id> <quality>")
            return

        topic_id = sys.argv[2]
        quality = int(sys.argv[3])

        result = scheduler.review(topic_id, quality)
        print(json.dumps(result, indent=2))

    elif command == "next":
        topic_id = scheduler.get_next_topic()
        if topic_id:
            print(f"Next topic to review: {topic_id}")
            stats = scheduler.get_stats(topic_id)
            print(json.dumps(stats, indent=2))
        else:
            print("No topics due for review!")

    elif command == "due":
        due_topics = scheduler.get_due_topics()
        if due_topics:
            print(f"Topics due for review ({len(due_topics)}):")
            for topic_id, next_review in due_topics:
                print(f"  - {topic_id} (due: {next_review.strftime('%Y-%m-%d %H:%M')})")
        else:
            print("No topics currently due for review.")

    elif command == "upcoming":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        upcoming = scheduler.get_upcoming_topics(days=days)
        if upcoming:
            print(f"Topics due in next {days} days ({len(upcoming)}):")
            for topic_id, next_review in upcoming:
                print(f"  - {topic_id} (due: {next_review.strftime('%Y-%m-%d %H:%M')})")
        else:
            print(f"No topics due in next {days} days.")

    elif command == "stats":
        if len(sys.argv) != 3:
            print("Usage: python spaced_scheduler.py stats <topic_id>")
            return

        topic_id = sys.argv[2]
        stats = scheduler.get_stats(topic_id)
        if stats:
            print(json.dumps(stats, indent=2))
        else:
            print(f"Topic '{topic_id}' not found in schedule.")

    elif command == "reset":
        if len(sys.argv) != 3:
            print("Usage: python spaced_scheduler.py reset <topic_id>")
            return

        topic_id = sys.argv[2]
        scheduler.reset_topic(topic_id)
        print(f"Reset scheduling for topic: {topic_id}")

    elif command == "queue":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        queue = scheduler.get_review_queue(limit=limit)
        if queue:
            print(f"Review Queue (top {limit}):")
            print(json.dumps(queue, indent=2))
        else:
            print("Review queue is empty.")

    else:
        print(f"Unknown command: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()
