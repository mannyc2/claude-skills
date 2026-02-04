---
name: calendar
description: Interact with Apple Calendar and Reminders via EventKit. Use when the user asks to check calendar, view events, create events, update events, delete events, manage schedule, find free time, list calendars, manage reminders, or check tasks. Triggers include "my calendar", "my schedule", "calendar events", "create event", "add to calendar", "what's on my calendar", "free time", "available slots", "when am I free", "upcoming events", "today's events", "update event", "reschedule", "delete event", "cancel event", "reminders", "todo", "task list", "complete reminder". Requires macOS with Calendar/Reminders access permission.
allowed-tools: mcp__calendar__list_calendars, mcp__calendar__get_events, mcp__calendar__create_event, mcp__calendar__search_events, mcp__calendar__update_event, mcp__calendar__delete_event, mcp__calendar__list_reminders, mcp__calendar__create_reminder, mcp__calendar__complete_reminder, mcp__calendar__delete_reminder, mcp__calendar__find_free_time
---

# Calendar & Reminders

Apple Calendar and Reminders management via EventKit. Returns rich event data including attendees, availability, alarms, recurrence info, and structured locations.

## Calendar Tools

### list_calendars

List all calendars with name, type (local/calDAV/exchange/subscription/birthday), source account, and color.

### get_events

Get events for a date range.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `days` | No | Number of days ahead (0 = today only, 7 = next week) |
| `calendar` | No | Filter to a specific calendar name |

Returns: id, title, calendar, start/end (ISO 8601), location, description, all-day status, attendees with RSVP status, availability, alarms, recurrence info, organizer, time zone.

### create_event

Create a new calendar event with optional recurrence, alarms, structured location, and more.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `title` | Yes | Event title |
| `start_date` | Yes | Start in `YYYY-MM-DD HH:MM` format (24-hour) |
| `end_date` | Yes | End in `YYYY-MM-DD HH:MM` format (24-hour) |
| `calendar` | No | Calendar name (defaults to system default) |
| `location` | No | Event location |
| `description` | No | Event description |
| `alarm_minutes` | No | Single alarm before event in minutes |
| `alarms` | No | Multiple alarms in minutes (e.g. [15, 60]) |
| `all_day` | No | Create as all-day event |
| `availability` | No | busy, free, tentative, or unavailable |
| `url` | No | URL associated with the event |
| `recurrence_frequency` | No | daily, weekly, monthly, or yearly |
| `recurrence_interval` | No | Interval (e.g. 2 for every 2 weeks) |
| `recurrence_end_date` | No | End date in YYYY-MM-DD format |
| `recurrence_count` | No | Number of occurrences |
| `recurrence_days` | No | Days of week (e.g. "mon,wed,fri") |
| `latitude` | No | Location latitude |
| `longitude` | No | Location longitude |

### search_events

Search events by keyword across title, description, and location.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `query` | Yes | Search keyword |
| `calendar` | No | Filter to a specific calendar name |
| `days` | No | Days ahead to search (default 365) |

### update_event

Update an existing event by its ID. All fields except `event_id` are optional.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `event_id` | Yes | Event identifier (from get_events or search_events) |
| `title` | No | New event title |
| `start_date` | No | New start date/time |
| `end_date` | No | New end date/time |
| `calendar` | No | Move to a different calendar |
| `location` | No | New location |
| `description` | No | New description |
| `alarm_minutes` | No | Replace alarms with a single alarm |
| `alarms` | No | Replace alarms with multiple alarms |
| `all_day` | No | Set as all-day event |
| `availability` | No | busy, free, tentative, or unavailable |
| `url` | No | URL associated with the event |
| `latitude` | No | Location latitude |
| `longitude` | No | Location longitude |
| `span` | No | For recurring: "this" or "future" |

### delete_event

Delete an event by its ID.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `event_id` | Yes | Event identifier |
| `span` | No | For recurring: "this" or "future" |

### find_free_time

Find available time slots by scanning events during working hours (8:00–18:00).

| Parameter | Required | Description |
|-----------|----------|-------------|
| `days` | No | Days ahead to scan (default 7) |
| `calendar` | No | Filter to a specific calendar |
| `minimum_minutes` | No | Minimum slot duration (default 30) |

## Reminder Tools

### list_reminders

List reminders (incomplete by default).

| Parameter | Required | Description |
|-----------|----------|-------------|
| `calendar` | No | Filter to a specific reminders list |
| `show_completed` | No | Show completed reminders instead |

### create_reminder

Create a new reminder.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `title` | Yes | Reminder title |
| `calendar` | No | Reminders list name |
| `due_date` | No | Due date in YYYY-MM-DD HH:MM format |
| `priority` | No | 1 (high), 5 (medium), 9 (low) |
| `notes` | No | Reminder notes |
| `alarm_minutes` | No | Alarm before due date in minutes |

### complete_reminder

Mark a reminder as completed.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `reminder_id` | Yes | Reminder identifier (from list_reminders) |

### delete_reminder

Delete a reminder.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `reminder_id` | Yes | Reminder identifier (from list_reminders) |

## Output

All tools return human-readable markdown and a `<structured_data>` JSON block with full EventKit data.

**Privacy**: Event and reminder data stays local. Uses macOS EventKit framework directly — no network calls, no Calendar.app dependency.

## Important Notes

- On first use, macOS will prompt for calendar access permission. Reminder commands trigger a separate Reminders access prompt.
- **Always confirm with the user before deleting events or reminders.**
