#!/usr/bin/env python3
"""
Bayesian Knowledge Tracing (BKT) for DSA mastery estimation.

Usage:
    knowledge_tracker.py update <topic> <is_correct>  # Update mastery after response
    knowledge_tracker.py get <topic>                   # Get current mastery level
    knowledge_tracker.py status                        # Show all topic mastery levels
    knowledge_tracker.py suggest                       # Suggest next topic to study

BKT Parameters:
    P(L0) = 0.3   Initial probability of knowing skill
    P(T)  = 0.1   Probability of learning after practice
    P(S)  = 0.1   Probability of slip (wrong despite knowing)
    P(G)  = 0.2   Probability of guess (right without knowing)
"""

import json
import sys
from pathlib import Path
from typing import TypedDict

# BKT parameters (can be tuned per topic)
DEFAULT_PARAMS = {
    "p_init": 0.3,   # P(L0): initial knowledge probability
    "p_learn": 0.1,  # P(T): learning rate per attempt
    "p_slip": 0.1,   # P(S): slip rate (error despite mastery)
    "p_guess": 0.2,  # P(G): guess rate (correct despite no mastery)
}

MASTERY_THRESHOLD = 0.95
PROGRESS_FILE = Path(__file__).parent.parent / "data" / "progress.json"


class TopicState(TypedDict):
    p_known: float
    attempts: int
    correct: int
    difficulty: int


def load_progress() -> dict:
    """Load progress from JSON file."""
    if not PROGRESS_FILE.exists():
        return {"topics": {}}
    with open(PROGRESS_FILE) as f:
        return json.load(f)


def save_progress(progress: dict) -> None:
    """Save progress to JSON file."""
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)


def get_topic_state(progress: dict, topic: str) -> TopicState:
    """Get or initialize topic state."""
    if topic not in progress.get("topics", {}):
        progress.setdefault("topics", {})[topic] = {
            "p_known": DEFAULT_PARAMS["p_init"],
            "attempts": 0,
            "correct": 0,
            "difficulty": 1,
        }
    return progress["topics"][topic]


def update_mastery(p_known: float, is_correct: bool) -> float:
    """
    Update P(known) using Bayesian Knowledge Tracing.

    If correct:
        P(known|correct) = P(known) * (1 - P(slip)) / P(correct)
        where P(correct) = P(known) * (1 - P(slip)) + (1 - P(known)) * P(guess)

    If incorrect:
        P(known|incorrect) = P(known) * P(slip) / P(incorrect)
        where P(incorrect) = P(known) * P(slip) + (1 - P(known)) * (1 - P(guess))

    Then apply learning transition:
        P(known_new) = P(known|obs) + (1 - P(known|obs)) * P(learn)
    """
    p_slip = DEFAULT_PARAMS["p_slip"]
    p_guess = DEFAULT_PARAMS["p_guess"]
    p_learn = DEFAULT_PARAMS["p_learn"]

    if is_correct:
        p_obs = p_known * (1 - p_slip) + (1 - p_known) * p_guess
        p_known_given_obs = (p_known * (1 - p_slip)) / p_obs if p_obs > 0 else p_known
    else:
        p_obs = p_known * p_slip + (1 - p_known) * (1 - p_guess)
        p_known_given_obs = (p_known * p_slip) / p_obs if p_obs > 0 else p_known

    # Apply learning transition
    p_known_new = p_known_given_obs + (1 - p_known_given_obs) * p_learn

    # Clamp to valid probability range
    return max(0.01, min(0.99, p_known_new))


def update_topic(topic: str, is_correct: bool) -> dict:
    """Update mastery for a topic after a response."""
    progress = load_progress()
    state = get_topic_state(progress, topic)

    old_mastery = state["p_known"]
    new_mastery = update_mastery(old_mastery, is_correct)

    state["p_known"] = new_mastery
    state["attempts"] += 1
    if is_correct:
        state["correct"] += 1

    # Adjust difficulty based on success rate
    if state["attempts"] >= 3:
        success_rate = state["correct"] / state["attempts"]
        if success_rate > 0.8 and state["difficulty"] < 5:
            state["difficulty"] += 1
        elif success_rate < 0.5 and state["difficulty"] > 1:
            state["difficulty"] -= 1

    save_progress(progress)

    return {
        "topic": topic,
        "old_mastery": round(old_mastery, 3),
        "new_mastery": round(new_mastery, 3),
        "change": round(new_mastery - old_mastery, 3),
        "mastered": new_mastery >= MASTERY_THRESHOLD,
        "attempts": state["attempts"],
        "success_rate": round(state["correct"] / state["attempts"], 2),
        "difficulty": state["difficulty"],
    }


def get_topic_mastery(topic: str) -> dict:
    """Get current mastery level for a topic."""
    progress = load_progress()
    state = get_topic_state(progress, topic)
    save_progress(progress)  # Save if newly initialized

    return {
        "topic": topic,
        "p_known": round(state["p_known"], 3),
        "mastered": state["p_known"] >= MASTERY_THRESHOLD,
        "attempts": state["attempts"],
        "correct": state["correct"],
        "success_rate": round(state["correct"] / state["attempts"], 2) if state["attempts"] > 0 else 0,
        "difficulty": state["difficulty"],
    }


def get_all_status() -> dict:
    """Get mastery status for all topics."""
    progress = load_progress()
    topics = progress.get("topics", {})

    result = {
        "total_topics": len(topics),
        "mastered": 0,
        "in_progress": 0,
        "not_started": 0,
        "topics": {},
    }

    for topic_name, state in topics.items():
        p_known = state.get("p_known", DEFAULT_PARAMS["p_init"])
        attempts = state.get("attempts", 0)

        if p_known >= MASTERY_THRESHOLD:
            result["mastered"] += 1
            status = "mastered"
        elif attempts > 0:
            result["in_progress"] += 1
            status = "in_progress"
        else:
            result["not_started"] += 1
            status = "not_started"

        result["topics"][topic_name] = {
            "p_known": round(p_known, 3),
            "status": status,
            "attempts": attempts,
        }

    return result


def suggest_topic() -> dict:
    """Suggest next topic to study based on mastery levels."""
    progress = load_progress()
    topics = progress.get("topics", {})

    # Priority: lowest mastery topics that haven't been mastered
    candidates = []
    for topic_name, state in topics.items():
        p_known = state.get("p_known", DEFAULT_PARAMS["p_init"])
        if p_known < MASTERY_THRESHOLD:
            candidates.append((topic_name, p_known, state.get("attempts", 0)))

    if not candidates:
        return {"suggestion": None, "reason": "All tracked topics are mastered!"}

    # Sort by mastery (ascending), then by attempts (ascending for fresh topics)
    candidates.sort(key=lambda x: (x[1], x[2]))

    topic, mastery, attempts = candidates[0]

    if mastery < 0.5:
        reason = f"Low mastery ({mastery:.1%}) - needs focused practice"
    elif attempts < 3:
        reason = f"Few attempts ({attempts}) - needs more practice"
    else:
        reason = f"Moderate mastery ({mastery:.1%}) - approaching proficiency"

    return {
        "suggestion": topic,
        "mastery": round(mastery, 3),
        "attempts": attempts,
        "reason": reason,
    }


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: knowledge_tracker.py <command> [args]")
        print("Commands: update, get, status, suggest")
        sys.exit(1)

    command = sys.argv[1]

    if command == "update":
        if len(sys.argv) < 4:
            print("Usage: knowledge_tracker.py update <topic> <is_correct>")
            sys.exit(1)
        topic = sys.argv[2]
        is_correct = sys.argv[3].lower() in ("true", "1", "yes", "correct")
        result = update_topic(topic, is_correct)
        print(json.dumps(result, indent=2))

    elif command == "get":
        if len(sys.argv) < 3:
            print("Usage: knowledge_tracker.py get <topic>")
            sys.exit(1)
        topic = sys.argv[2]
        result = get_topic_mastery(topic)
        print(json.dumps(result, indent=2))

    elif command == "status":
        result = get_all_status()
        print(json.dumps(result, indent=2))

    elif command == "suggest":
        result = suggest_topic()
        print(json.dumps(result, indent=2))

    else:
        print(f"Unknown command: {command}")
        print("Commands: update, get, status, suggest")
        sys.exit(1)


if __name__ == "__main__":
    main()
