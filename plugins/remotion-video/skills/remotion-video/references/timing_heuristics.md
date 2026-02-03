# Timing Heuristics

Frame calculations and pacing guidelines.

## Frame Math

At 30fps (default):

| Seconds | Frames |
|---------|--------|
| 0.5s | 15 |
| 1s | 30 |
| 2s | 60 |
| 3s | 90 |
| 5s | 150 |
| 10s | 300 |
| 12s | 360 |

Formulas:
- `frames = seconds × fps`
- `seconds = frames ÷ fps`

---

## Text Readability Rules

### Reading Speed

Average reading speed: **3 words per second** for body text.

| Word Count | Minimum Time |
|------------|--------------|
| 3-5 words | 1.5s |
| 6-10 words | 3s |
| 11-15 words | 5s |
| 16+ words | Consider splitting |

### Text Types

| Type | Minimum Duration | Notes |
|------|------------------|-------|
| Headline (2-4 words) | 1-1.5s | Can be faster, high contrast |
| Subheadline (5-8 words) | 2s | |
| Body text | word_count ÷ 3 | Round up |
| UI labels | 0.5-1s | If familiar patterns |
| New concept | +50% time | Unfamiliar needs processing |

---

## Interaction Timing

### Button States

| State | Duration | Frames @30fps |
|-------|----------|---------------|
| Hover | 0.3-0.5s | 10-15 |
| Press/click | 0.15-0.3s | 5-10 |
| Release | instant | 1-3 |

### Loading States

| Type | Minimum | Why |
|------|---------|-----|
| Spinner | 1s | Viewer must register "loading" |
| Progress bar | 1.5-2s | Show meaningful progress |
| Skeleton | 0.5-1s | Brief enough to not feel slow |

### Success/Confirmation

| Type | Minimum | Why |
|------|---------|-----|
| Checkmark | 1.5s | Must register as success, not glitch |
| Success message | 2s | Read + emotional payoff |
| Celebration | 2-3s | Let it breathe |

**Critical**: Rushing success states makes videos feel broken.

---

## Scene Duration Guidelines

| Scene Type | Min | Typical | Max |
|------------|-----|---------|-----|
| Context/establishing | 1s | 2s | 3s |
| Simple action | 2s | 3s | 4s |
| Single concept | 2s | 3-4s | 5s |
| Complex concept | 4s | 5-6s | 7s |
| Hero moment | 5s | 6-8s | 10s |

### Hero Moment Rule

The key differentiating feature should get **≥40% of total video time**.

Example for 12s video:
- Hero moment: 5-6s (42-50%)
- Supporting scenes: 6-7s split

---

## Transition Timing

| Transition Type | Duration | Frames @30fps |
|-----------------|----------|---------------|
| Cut | 0 | 0 |
| Fade | 0.5-0.67s | 15-20 |
| Crossfade | 0.67-1s | 20-30 |
| Slide | 0.67-1s | 20-30 |

**Important**: Transition time comes FROM the scenes, not between them.

---

## Common Timing Mistakes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| Biometric too fast | Can't read text | 4s minimum for auth flows |
| Success rushed | Feels like glitch | Hold 1.5-2s minimum |
| Text flashes | Couldn't read | word_count ÷ 3 seconds |
| Loading too short | Doesn't register | 1s minimum for spinners |
| All scenes equal | No emphasis | Vary by timing_intent |

---

## Quick Reference

```
READING:     3 words/second
HEADLINE:    1-1.5s minimum
BUTTON:      0.3s hover, 0.15s click
LOADING:     1s minimum
SUCCESS:     1.5s minimum
HERO:        40%+ of total time
FADE:        15-20 frames
SLIDE:       20-30 frames
```
