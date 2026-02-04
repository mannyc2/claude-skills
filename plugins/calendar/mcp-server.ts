import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { run } from "./lib/calendar";

const server = new McpServer({
  name: "calendar",
  version: "1.0.0",
});

// ── Formatting helpers ──────────────────────────────────────────────────────

interface CalendarEvent {
  id: string;
  calendar: string;
  title: string;
  start: string;
  end: string;
  location?: string | null;
  description?: string | null;
  isAllDay?: boolean;
  attendees?: Array<{ name?: string; email?: string; status?: string }> | null;
  availability?: string;
  status?: string;
  organizer?: string | null;
  timeZone?: string | null;
}

function formatEvent(e: CalendarEvent): string {
  const lines = [`## ${e.title}`, `- ID: \`${e.id}\``, `- Calendar: ${e.calendar}`];
  if (e.isAllDay) {
    lines.push(`- All day: ${e.start.split("T")[0]}`);
  } else {
    lines.push(`- Start: ${e.start}`, `- End: ${e.end}`);
  }
  if (e.location) lines.push(`- Location: ${e.location}`);
  if (e.description) lines.push(`- Description: ${e.description}`);
  if (e.availability && e.availability !== "notSupported")
    lines.push(`- Availability: ${e.availability}`);
  if (e.organizer) lines.push(`- Organizer: ${e.organizer}`);
  if (e.attendees?.length) {
    lines.push(
      `- Attendees: ${e.attendees.map((a) => a.name || a.email).join(", ")}`
    );
  }
  return lines.join("\n");
}

function respond(text: string, data?: any) {
  const content: Array<{ type: "text"; text: string }> = [
    { type: "text" as const, text },
  ];
  if (data !== undefined) {
    content.push({
      type: "text" as const,
      text: `\n\n<structured_data>\n${JSON.stringify(data, null, 2)}\n</structured_data>`,
    });
  }
  return { content };
}

// ── List Calendars ──────────────────────────────────────────────────────────

server.tool(
  "list_calendars",
  "List all available Apple Calendar calendars on this Mac. Returns name, type, source, and color for each.",
  {},
  async () => {
    const calendars = await run(["list"]);
    const formatted = calendars
      .map(
        (c: any) =>
          `- **${c.name}** (${c.type}${c.source ? `, ${c.source}` : ""})`
      )
      .join("\n");
    return respond(formatted, calendars);
  }
);

// ── Get Events ──────────────────────────────────────────────────────────────

server.tool(
  "get_events",
  "Get calendar events for a date range. Returns full event details including attendees, availability, alarms, and recurrence info.",
  {
    days: z
      .number()
      .optional()
      .default(0)
      .describe(
        "Number of days ahead to fetch (0 = today only, 7 = next week)"
      ),
    calendar: z
      .string()
      .optional()
      .describe("Filter to a specific calendar name"),
  },
  async ({ days, calendar }) => {
    const args = ["events", "--days", String(days)];
    if (calendar) args.push("--calendar", calendar);

    const events: CalendarEvent[] = await run(args);

    if (events.length === 0) {
      return respond("No events found");
    }

    return respond(events.map(formatEvent).join("\n\n"), events);
  }
);

// ── Create Event ────────────────────────────────────────────────────────────

server.tool(
  "create_event",
  "Create a new event in Apple Calendar. Supports alarms, all-day events, availability, and URLs.",
  {
    title: z.string().describe("Event title"),
    start_date: z
      .string()
      .describe("Start date/time in YYYY-MM-DD HH:MM format (24-hour)"),
    end_date: z
      .string()
      .describe("End date/time in YYYY-MM-DD HH:MM format (24-hour)"),
    calendar: z
      .string()
      .optional()
      .describe("Calendar name (defaults to the system default calendar)"),
    location: z.string().optional().describe("Event location"),
    description: z.string().optional().describe("Event description"),
    alarm_minutes: z
      .number()
      .optional()
      .describe("Single alarm before event in minutes (e.g. 15). Use 'alarms' for multiple."),
    alarms: z
      .array(z.number())
      .optional()
      .describe("Multiple alarms before event in minutes (e.g. [15, 60])"),
    all_day: z.boolean().optional().describe("Create as all-day event"),
    availability: z
      .enum(["busy", "free", "tentative", "unavailable"])
      .optional()
      .describe("Event availability status"),
    url: z.string().optional().describe("URL associated with the event"),
    recurrence_frequency: z
      .enum(["daily", "weekly", "monthly", "yearly"])
      .optional()
      .describe("Recurrence frequency"),
    recurrence_interval: z
      .number()
      .optional()
      .describe("Recurrence interval (e.g. 2 for every 2 weeks)"),
    recurrence_end_date: z
      .string()
      .optional()
      .describe("Recurrence end date in YYYY-MM-DD format"),
    recurrence_count: z
      .number()
      .optional()
      .describe("Number of occurrences (alternative to end date)"),
    recurrence_days: z
      .string()
      .optional()
      .describe("Comma-separated days of week for weekly recurrence (e.g. 'mon,wed,fri')"),
    latitude: z.number().optional().describe("Location latitude for structured location"),
    longitude: z.number().optional().describe("Location longitude for structured location"),
  },
  async ({
    title,
    start_date,
    end_date,
    calendar,
    location,
    description,
    alarm_minutes,
    alarms,
    all_day,
    availability,
    url,
    recurrence_frequency,
    recurrence_interval,
    recurrence_end_date,
    recurrence_count,
    recurrence_days,
    latitude,
    longitude,
  }) => {
    const args = [
      "create",
      "--title",
      title,
      "--start",
      start_date,
      "--end",
      end_date,
    ];
    if (calendar) args.push("--calendar", calendar);
    if (location) args.push("--location", location);
    if (description) args.push("--description", description);
    if (all_day) args.push("--all-day");
    if (availability) args.push("--availability", availability);
    if (url) args.push("--url", url);

    // Merge alarm_minutes and alarms into comma-separated string
    const alarmValues: number[] = [];
    if (alarm_minutes !== undefined) alarmValues.push(alarm_minutes);
    if (alarms) alarmValues.push(...alarms);
    if (alarmValues.length > 0)
      args.push("--alarm", alarmValues.join(","));

    if (recurrence_frequency)
      args.push("--recurrence-frequency", recurrence_frequency);
    if (recurrence_interval !== undefined)
      args.push("--recurrence-interval", String(recurrence_interval));
    if (recurrence_end_date)
      args.push("--recurrence-end-date", recurrence_end_date);
    if (recurrence_count !== undefined)
      args.push("--recurrence-count", String(recurrence_count));
    if (recurrence_days) args.push("--recurrence-days", recurrence_days);
    if (latitude !== undefined) args.push("--latitude", String(latitude));
    if (longitude !== undefined) args.push("--longitude", String(longitude));

    const event = await run(args);
    return respond(`Event created: **${event.title}**\n\n${formatEvent(event)}`, event);
  }
);

// ── Update Event ────────────────────────────────────────────────────────────

server.tool(
  "update_event",
  "Update an existing Apple Calendar event by its ID. All fields except event_id are optional — only provided fields are changed.",
  {
    event_id: z.string().describe("Event identifier (from get_events or search_events)"),
    title: z.string().optional().describe("New event title"),
    start_date: z
      .string()
      .optional()
      .describe("New start date/time in YYYY-MM-DD HH:MM format (24-hour)"),
    end_date: z
      .string()
      .optional()
      .describe("New end date/time in YYYY-MM-DD HH:MM format (24-hour)"),
    calendar: z.string().optional().describe("Move to a different calendar"),
    location: z.string().optional().describe("New event location"),
    description: z.string().optional().describe("New event description"),
    alarm_minutes: z
      .number()
      .optional()
      .describe("Replace alarms with a single alarm (minutes before event)"),
    alarms: z
      .array(z.number())
      .optional()
      .describe("Replace alarms with multiple alarms (minutes before event)"),
    all_day: z.boolean().optional().describe("Set as all-day event"),
    availability: z
      .enum(["busy", "free", "tentative", "unavailable"])
      .optional()
      .describe("Event availability status"),
    url: z.string().optional().describe("URL associated with the event"),
    latitude: z.number().optional().describe("Location latitude for structured location"),
    longitude: z.number().optional().describe("Location longitude for structured location"),
    span: z
      .enum(["this", "future"])
      .optional()
      .default("this")
      .describe("For recurring events: 'this' = this occurrence only, 'future' = this and all future occurrences"),
  },
  async ({
    event_id,
    title,
    start_date,
    end_date,
    calendar,
    location,
    description,
    alarm_minutes,
    alarms,
    all_day,
    availability,
    url,
    latitude,
    longitude,
    span,
  }) => {
    const args = ["update", "--id", event_id];
    if (title) args.push("--title", title);
    if (start_date) args.push("--start", start_date);
    if (end_date) args.push("--end", end_date);
    if (calendar) args.push("--calendar", calendar);
    if (location) args.push("--location", location);
    if (description) args.push("--description", description);
    if (all_day) args.push("--all-day");
    if (availability) args.push("--availability", availability);
    if (url) args.push("--url", url);
    if (span === "future") args.push("--span", "future");
    if (latitude !== undefined) args.push("--latitude", String(latitude));
    if (longitude !== undefined) args.push("--longitude", String(longitude));

    const alarmValues: number[] = [];
    if (alarm_minutes !== undefined) alarmValues.push(alarm_minutes);
    if (alarms) alarmValues.push(...alarms);
    if (alarmValues.length > 0)
      args.push("--alarm", alarmValues.join(","));

    const event = await run(args);
    return respond(`Event updated: **${event.title}**\n\n${formatEvent(event)}`, event);
  }
);

// ── Delete Event ────────────────────────────────────────────────────────────

server.tool(
  "delete_event",
  "Delete an Apple Calendar event by its ID. Always confirm with the user before calling this tool.",
  {
    event_id: z.string().describe("Event identifier (from get_events or search_events)"),
    span: z
      .enum(["this", "future"])
      .optional()
      .default("this")
      .describe("For recurring events: 'this' = this occurrence only, 'future' = this and all future occurrences"),
  },
  async ({ event_id, span }) => {
    const args = ["delete", "--id", event_id];
    if (span === "future") args.push("--span", "future");

    const result = await run(args);
    return respond(`Event deleted: **${result.title}**`, result);
  }
);

// ── Search Events ───────────────────────────────────────────────────────────

server.tool(
  "search_events",
  "Search calendar events by keyword in title, description, or location. Searches past year and upcoming year by default.",
  {
    query: z.string().describe("Search keyword"),
    calendar: z
      .string()
      .optional()
      .describe("Filter to a specific calendar name"),
    days: z
      .number()
      .optional()
      .default(365)
      .describe("Number of days ahead to search (default 365)"),
  },
  async ({ query, calendar, days }) => {
    const args = ["search", "--query", query, "--days", String(days)];
    if (calendar) args.push("--calendar", calendar);

    const events: CalendarEvent[] = await run(args);

    if (events.length === 0) {
      return respond(`No events found matching '${query}'`);
    }

    return respond(
      `# Search Results for "${query}" (${events.length} found)\n\n${events.map(formatEvent).join("\n\n")}`,
      events
    );
  }
);

// ── Find Free Time ──────────────────────────────────────────────────────────

server.tool(
  "find_free_time",
  "Find available time slots by analyzing calendar events. Scans working hours (8:00–18:00) and returns free slots.",
  {
    days: z
      .number()
      .optional()
      .default(7)
      .describe("Number of days ahead to scan (default 7)"),
    calendar: z
      .string()
      .optional()
      .describe("Filter to a specific calendar name"),
    minimum_minutes: z
      .number()
      .optional()
      .default(30)
      .describe("Minimum slot duration in minutes (default 30)"),
  },
  async ({ days, calendar, minimum_minutes }) => {
    const args = [
      "free-busy",
      "--days",
      String(days),
      "--min-slot",
      String(minimum_minutes),
    ];
    if (calendar) args.push("--calendar", calendar);

    const slots: Array<{ start: string; end: string; minutes: number }> =
      await run(args);

    if (slots.length === 0) {
      return respond("No free time slots found in the specified range");
    }

    const formatted = slots
      .map((s) => `- ${s.start} → ${s.end} (${s.minutes} min)`)
      .join("\n");
    return respond(
      `# Free Time Slots (${slots.length} found)\n\n${formatted}`,
      slots
    );
  }
);

// ── Reminder Formatting ─────────────────────────────────────────────────────

interface Reminder {
  id: string;
  calendar: string;
  title: string;
  isCompleted: boolean;
  completionDate?: string | null;
  dueDate?: string | null;
  priority: number;
  notes?: string | null;
  hasAlarms: boolean;
}

function formatReminder(r: Reminder): string {
  const check = r.isCompleted ? "[x]" : "[ ]";
  const lines = [`- ${check} **${r.title}** (ID: \`${r.id}\`)`];
  lines.push(`  - Calendar: ${r.calendar}`);
  if (r.dueDate) lines.push(`  - Due: ${r.dueDate}`);
  if (r.priority > 0) lines.push(`  - Priority: ${r.priority}`);
  if (r.notes) lines.push(`  - Notes: ${r.notes}`);
  if (r.isCompleted && r.completionDate)
    lines.push(`  - Completed: ${r.completionDate}`);
  return lines.join("\n");
}

// ── List Reminders ──────────────────────────────────────────────────────────

server.tool(
  "list_reminders",
  "List Apple Reminders. Shows incomplete reminders by default.",
  {
    calendar: z
      .string()
      .optional()
      .describe("Filter to a specific reminders list"),
    show_completed: z
      .boolean()
      .optional()
      .default(false)
      .describe("Show completed reminders instead of incomplete ones"),
  },
  async ({ calendar, show_completed }) => {
    const args = ["reminders"];
    if (calendar) args.push("--calendar", calendar);
    if (show_completed) args.push("--completed");

    const reminders: Reminder[] = await run(args);

    if (reminders.length === 0) {
      return respond(
        show_completed ? "No completed reminders found" : "No pending reminders"
      );
    }

    const label = show_completed ? "Completed" : "Pending";
    return respond(
      `# ${label} Reminders (${reminders.length})\n\n${reminders.map(formatReminder).join("\n")}`,
      reminders
    );
  }
);

// ── Create Reminder ─────────────────────────────────────────────────────────

server.tool(
  "create_reminder",
  "Create a new Apple Reminder.",
  {
    title: z.string().describe("Reminder title"),
    calendar: z
      .string()
      .optional()
      .describe("Reminders list name (defaults to system default)"),
    due_date: z
      .string()
      .optional()
      .describe("Due date/time in YYYY-MM-DD HH:MM format (24-hour)"),
    priority: z
      .number()
      .optional()
      .describe("Priority: 1 (high), 5 (medium), 9 (low)"),
    notes: z.string().optional().describe("Reminder notes"),
    alarm_minutes: z
      .number()
      .optional()
      .describe("Alarm before due date in minutes"),
  },
  async ({ title, calendar, due_date, priority, notes, alarm_minutes }) => {
    const args = ["create-reminder", "--title", title];
    if (calendar) args.push("--calendar", calendar);
    if (due_date) args.push("--due", due_date);
    if (priority !== undefined) args.push("--priority", String(priority));
    if (notes) args.push("--notes", notes);
    if (alarm_minutes !== undefined)
      args.push("--alarm", String(alarm_minutes));

    const reminder = await run(args);
    return respond(
      `Reminder created: **${reminder.title}**\n\n${formatReminder(reminder)}`,
      reminder
    );
  }
);

// ── Complete Reminder ───────────────────────────────────────────────────────

server.tool(
  "complete_reminder",
  "Mark an Apple Reminder as completed.",
  {
    reminder_id: z
      .string()
      .describe("Reminder identifier (from list_reminders)"),
  },
  async ({ reminder_id }) => {
    const reminder = await run(["complete-reminder", "--id", reminder_id]);
    return respond(`Reminder completed: **${reminder.title}**`, reminder);
  }
);

// ── Delete Reminder ─────────────────────────────────────────────────────────

server.tool(
  "delete_reminder",
  "Delete an Apple Reminder. Always confirm with the user before calling this tool.",
  {
    reminder_id: z
      .string()
      .describe("Reminder identifier (from list_reminders)"),
  },
  async ({ reminder_id }) => {
    const result = await run(["delete-reminder", "--id", reminder_id]);
    return respond(`Reminder deleted: **${result.title}**`, result);
  }
);

// ── Main ────────────────────────────────────────────────────────────────────

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((error) => {
  console.error("Server error:", error);
  process.exit(1);
});
