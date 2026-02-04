import CoreLocation
import EventKit
import Foundation

// MARK: - Main

let store = EKEventStore()

func requestAccess() async throws {
  if #available(macOS 14.0, *) {
    try await store.requestFullAccessToEvents()
  } else {
    let granted = try await withCheckedThrowingContinuation {
      (cont: CheckedContinuation<Bool, Error>) in
      store.requestAccess(to: .event) { granted, error in
        if let error { cont.resume(throwing: error) } else {
          cont.resume(returning: granted)
        }
      }
    }
    guard granted else {
      throw CalendarError.accessDenied
    }
  }
}

enum CalendarError: Error, CustomStringConvertible {
  case accessDenied
  case calendarNotFound(String)
  case invalidDate(String)
  case missingArgument(String)
  case unknownCommand(String)
  case eventNotFound(String)
  case reminderNotFound(String)
  case reminderAccessDenied

  var description: String {
    switch self {
    case .accessDenied: return "Calendar access denied. Grant access in System Settings > Privacy & Security > Calendars."
    case .calendarNotFound(let name): return "Calendar '\(name)' not found"
    case .invalidDate(let str): return "Invalid date format '\(str)'. Expected: YYYY-MM-DD HH:MM"
    case .missingArgument(let arg): return "Missing required argument: \(arg)"
    case .unknownCommand(let cmd): return "Unknown command: \(cmd)"
    case .eventNotFound(let id): return "Event not found with ID: \(id)"
    case .reminderNotFound(let id): return "Reminder not found with ID: \(id)"
    case .reminderAccessDenied: return "Reminders access denied. Grant access in System Settings > Privacy & Security > Reminders."
    }
  }
}

// MARK: - Date Parsing

let dateFormatter: DateFormatter = {
  let f = DateFormatter()
  f.dateFormat = "yyyy-MM-dd HH:mm"
  f.locale = Locale(identifier: "en_US_POSIX")
  return f
}()

let isoFormatter: ISO8601DateFormatter = {
  let f = ISO8601DateFormatter()
  f.formatOptions = [.withInternetDateTime]
  return f
}()

func parseDate(_ str: String) throws -> Date {
  guard let date = dateFormatter.date(from: str) else {
    throw CalendarError.invalidDate(str)
  }
  return date
}

// MARK: - Event Serialization

func serialize(_ event: EKEvent) -> [String: Any?] {
  return [
    "id": event.eventIdentifier,
    "calendar": event.calendar.title,
    "title": event.title,
    "start": isoFormatter.string(from: event.startDate),
    "end": isoFormatter.string(from: event.endDate),
    "location": event.location,
    "description": event.notes,
    "isAllDay": event.isAllDay,
    "url": event.url?.absoluteString,
    "status": statusString(event.status),
    "availability": availabilityString(event.availability),
    "organizer": event.organizer?.name,
    "structuredLocation": event.structuredLocation.map { loc in
      [
        "title": loc.title,
        "latitude": loc.geoLocation?.coordinate.latitude,
        "longitude": loc.geoLocation?.coordinate.longitude,
        "radius": loc.radius,
      ] as [String: Any?]
    },
    "timeZone": event.timeZone?.identifier,
    "attendees": event.attendees?.map { attendee in
      [
        "name": attendee.name,
        "email": attendee.url.absoluteString.replacingOccurrences(of: "mailto:", with: ""),
        "status": participantStatus(attendee.participantStatus),
        "role": participantRole(attendee.participantRole),
      ] as [String: Any?]
    },
    "hasAlarms": event.hasAlarms,
    "alarms": event.alarms?.map { alarm in
      ["relativeOffset": alarm.relativeOffset]
    },
    "hasRecurrenceRules": event.hasRecurrenceRules,
    "recurrenceRules": event.hasRecurrenceRules ? serializeRecurrenceRules(event.recurrenceRules) : nil,
  ] as [String: Any?]
}

func statusString(_ status: EKEventStatus) -> String {
  switch status {
  case .none: return "none"
  case .confirmed: return "confirmed"
  case .tentative: return "tentative"
  case .canceled: return "canceled"
  @unknown default: return "unknown"
  }
}

func availabilityString(_ availability: EKEventAvailability) -> String {
  switch availability {
  case .notSupported: return "notSupported"
  case .busy: return "busy"
  case .free: return "free"
  case .tentative: return "tentative"
  case .unavailable: return "unavailable"
  @unknown default: return "unknown"
  }
}

func participantStatus(_ status: EKParticipantStatus) -> String {
  switch status {
  case .unknown: return "unknown"
  case .pending: return "pending"
  case .accepted: return "accepted"
  case .declined: return "declined"
  case .tentative: return "tentative"
  case .delegated: return "delegated"
  case .completed: return "completed"
  case .inProcess: return "inProcess"
  @unknown default: return "unknown"
  }
}

func participantRole(_ role: EKParticipantRole) -> String {
  switch role {
  case .unknown: return "unknown"
  case .required: return "required"
  case .optional: return "optional"
  case .chair: return "chair"
  case .nonParticipant: return "nonParticipant"
  @unknown default: return "unknown"
  }
}

// MARK: - Argument Parsing

func getArg(_ args: [String], flag: String) -> String? {
  guard let idx = args.firstIndex(of: flag), idx + 1 < args.count else { return nil }
  return args[idx + 1]
}

func hasFlag(_ args: [String], flag: String) -> Bool {
  args.contains(flag)
}

func findCalendar(named name: String) throws -> EKCalendar {
  guard
    let cal = store.calendars(for: .event).first(where: {
      $0.title.lowercased() == name.lowercased()
    })
  else {
    throw CalendarError.calendarNotFound(name)
  }
  return cal
}

// MARK: - Commands

func listCalendars() -> [[String: Any?]] {
  return store.calendars(for: .event).map { cal in
    [
      "name": cal.title,
      "type": calendarTypeString(cal.type),
      "source": cal.source?.title,
      "color": cal.cgColor != nil ? "#\(hexColor(cal.cgColor!))" : nil,
      "isImmutable": cal.isImmutable,
      "allowsContentModifications": cal.allowsContentModifications,
    ] as [String: Any?]
  }
}

func calendarTypeString(_ type: EKCalendarType) -> String {
  switch type {
  case .local: return "local"
  case .calDAV: return "calDAV"
  case .exchange: return "exchange"
  case .subscription: return "subscription"
  case .birthday: return "birthday"
  @unknown default: return "unknown"
  }
}

func hexColor(_ color: CGColor) -> String {
  guard let components = color.components, components.count >= 3 else { return "000000" }
  let r = Int(components[0] * 255)
  let g = Int(components[1] * 255)
  let b = Int(components[2] * 255)
  return String(format: "%02x%02x%02x", r, g, b)
}

func getEvents(days: Int, calendarName: String?) throws -> [[String: Any?]] {
  let startOfDay = Calendar.current.startOfDay(for: Date())
  let endDate = Calendar.current.date(byAdding: .day, value: days + 1, to: startOfDay)!

  var calendars: [EKCalendar]? = nil
  if let name = calendarName {
    calendars = [try findCalendar(named: name)]
  }

  let predicate = store.predicateForEvents(withStart: startOfDay, end: endDate, calendars: calendars)
  let events = store.events(matching: predicate)

  return events.map { serialize($0) }
}

func parseSpan(_ str: String?) -> EKSpan {
  return str == "future" ? .futureEvents : .thisEvent
}

func parseAvailability(_ str: String) -> EKEventAvailability {
  switch str.lowercased() {
  case "busy": return .busy
  case "free": return .free
  case "tentative": return .tentative
  case "unavailable": return .unavailable
  default: return .busy
  }
}

func createEvent(
  title: String, start: Date, end: Date,
  calendarName: String?, location: String?, description: String?,
  alarmStr: String?, allDay: Bool, availability: String?, urlStr: String?,
  recurrenceFrequency: String?, recurrenceInterval: Int?,
  recurrenceEndDate: String?, recurrenceCount: Int?, recurrenceDays: String?,
  latitude: Double?, longitude: Double?
) throws -> [String: Any?] {
  let event = EKEvent(eventStore: store)
  event.title = title
  event.startDate = start
  event.endDate = end
  event.isAllDay = allDay

  if let name = calendarName {
    event.calendar = try findCalendar(named: name)
  } else {
    event.calendar = store.defaultCalendarForNewEvents
  }

  if let loc = location { event.location = loc }
  if let desc = description { event.notes = desc }
  if let avail = availability { event.availability = parseAvailability(avail) }
  if let u = urlStr, let url = URL(string: u) { event.url = url }

  if let lat = latitude, let lon = longitude {
    let structLoc = EKStructuredLocation(title: location ?? "")
    structLoc.geoLocation = CLLocation(latitude: lat, longitude: lon)
    event.structuredLocation = structLoc
  }

  if let alarmValues = alarmStr {
    for part in alarmValues.split(separator: ",") {
      if let mins = Int(part.trimmingCharacters(in: .whitespaces)) {
        event.addAlarm(EKAlarm(relativeOffset: TimeInterval(-mins * 60)))
      }
    }
  }

  if let freq = recurrenceFrequency {
    let rule = try buildRecurrenceRule(
      frequency: freq,
      interval: recurrenceInterval ?? 1,
      endDate: recurrenceEndDate,
      count: recurrenceCount,
      days: recurrenceDays
    )
    event.addRecurrenceRule(rule)
  }

  try store.save(event, span: .thisEvent)
  return serialize(event)
}

func updateEvent(
  id: String, title: String?, startStr: String?, endStr: String?,
  calendarName: String?, location: String?, description: String?,
  alarmStr: String?, span: EKSpan, allDay: Bool?, availability: String?, urlStr: String?,
  latitude: Double?, longitude: Double?
) throws -> [String: Any?] {
  guard let event = store.event(withIdentifier: id) else {
    throw CalendarError.eventNotFound(id)
  }

  if let t = title { event.title = t }
  if let s = startStr { event.startDate = try parseDate(s) }
  if let e = endStr { event.endDate = try parseDate(e) }
  if let name = calendarName { event.calendar = try findCalendar(named: name) }
  if let loc = location { event.location = loc }
  if let desc = description { event.notes = desc }
  if let ad = allDay { event.isAllDay = ad }
  if let avail = availability { event.availability = parseAvailability(avail) }
  if let u = urlStr, let url = URL(string: u) { event.url = url }

  if let lat = latitude, let lon = longitude {
    let structLoc = EKStructuredLocation(title: location ?? event.location ?? "")
    structLoc.geoLocation = CLLocation(latitude: lat, longitude: lon)
    event.structuredLocation = structLoc
  }

  if let alarmValues = alarmStr {
    // Remove existing alarms, then add new ones
    if let existing = event.alarms {
      for alarm in existing { event.removeAlarm(alarm) }
    }
    for part in alarmValues.split(separator: ",") {
      if let mins = Int(part.trimmingCharacters(in: .whitespaces)) {
        event.addAlarm(EKAlarm(relativeOffset: TimeInterval(-mins * 60)))
      }
    }
  }

  try store.save(event, span: span, commit: true)
  return serialize(event)
}

func deleteEvent(id: String, span: EKSpan) throws -> [String: Any] {
  guard let event = store.event(withIdentifier: id) else {
    throw CalendarError.eventNotFound(id)
  }
  let title = event.title ?? "Untitled"
  try store.remove(event, span: span, commit: true)
  return ["deleted": true, "title": title, "id": id] as [String: Any]
}

// MARK: - Recurrence

func dayOfWeek(_ name: String) -> EKRecurrenceDayOfWeek? {
  switch name.lowercased().prefix(3) {
  case "mon": return EKRecurrenceDayOfWeek(.monday)
  case "tue": return EKRecurrenceDayOfWeek(.tuesday)
  case "wed": return EKRecurrenceDayOfWeek(.wednesday)
  case "thu": return EKRecurrenceDayOfWeek(.thursday)
  case "fri": return EKRecurrenceDayOfWeek(.friday)
  case "sat": return EKRecurrenceDayOfWeek(.saturday)
  case "sun": return EKRecurrenceDayOfWeek(.sunday)
  default: return nil
  }
}

func buildRecurrenceRule(
  frequency: String, interval: Int,
  endDate: String?, count: Int?, days: String?
) throws -> EKRecurrenceRule {
  let freq: EKRecurrenceFrequency
  switch frequency.lowercased() {
  case "daily": freq = .daily
  case "weekly": freq = .weekly
  case "monthly": freq = .monthly
  case "yearly": freq = .yearly
  default: freq = .weekly
  }

  var end: EKRecurrenceEnd? = nil
  if let endStr = endDate {
    let date = try parseDate(endStr + " 23:59")
    end = EKRecurrenceEnd(end: date)
  } else if let c = count {
    end = EKRecurrenceEnd(occurrenceCount: c)
  }

  var daysOfWeek: [EKRecurrenceDayOfWeek]? = nil
  if let dayStr = days {
    daysOfWeek = dayStr.split(separator: ",").compactMap { dayOfWeek(String($0.trimmingCharacters(in: .whitespaces))) }
    if daysOfWeek?.isEmpty == true { daysOfWeek = nil }
  }

  return EKRecurrenceRule(
    recurrenceWith: freq,
    interval: interval,
    daysOfTheWeek: daysOfWeek,
    daysOfTheMonth: nil,
    monthsOfTheYear: nil,
    weeksOfTheYear: nil,
    daysOfTheYear: nil,
    setPositions: nil,
    end: end
  )
}

func recurrenceFrequencyString(_ freq: EKRecurrenceFrequency) -> String {
  switch freq {
  case .daily: return "daily"
  case .weekly: return "weekly"
  case .monthly: return "monthly"
  case .yearly: return "yearly"
  @unknown default: return "unknown"
  }
}

func serializeRecurrenceRules(_ rules: [EKRecurrenceRule]?) -> [[String: Any?]]? {
  guard let rules = rules else { return nil }
  return rules.map { rule in
    var dict: [String: Any?] = [
      "frequency": recurrenceFrequencyString(rule.frequency),
      "interval": rule.interval,
    ]
    if let days = rule.daysOfTheWeek {
      dict["daysOfTheWeek"] = days.map { dayOfWeekName($0.dayOfTheWeek) }
    }
    if let end = rule.recurrenceEnd {
      if let endDate = end.endDate {
        dict["endDate"] = isoFormatter.string(from: endDate)
      } else {
        dict["occurrenceCount"] = end.occurrenceCount
      }
    }
    return dict
  }
}

func dayOfWeekName(_ day: EKWeekday) -> String {
  switch day {
  case .monday: return "monday"
  case .tuesday: return "tuesday"
  case .wednesday: return "wednesday"
  case .thursday: return "thursday"
  case .friday: return "friday"
  case .saturday: return "saturday"
  case .sunday: return "sunday"
  @unknown default: return "unknown"
  }
}

func searchEvents(query: String, calendarName: String?, days: Int) throws -> [[String: Any?]] {
  let startOfDay = Calendar.current.startOfDay(for: Date())
  let searchStart = Calendar.current.date(byAdding: .year, value: -1, to: startOfDay)!
  let searchEnd = Calendar.current.date(byAdding: .day, value: days, to: startOfDay)!

  var calendars: [EKCalendar]? = nil
  if let name = calendarName {
    calendars = [try findCalendar(named: name)]
  }

  let predicate = store.predicateForEvents(withStart: searchStart, end: searchEnd, calendars: calendars)
  let events = store.events(matching: predicate)

  let lowerQuery = query.lowercased()
  let matched = events.filter { event in
    (event.title?.lowercased().contains(lowerQuery) ?? false)
      || (event.notes?.lowercased().contains(lowerQuery) ?? false)
      || (event.location?.lowercased().contains(lowerQuery) ?? false)
  }

  return matched.map { serialize($0) }
}

// MARK: - Free/Busy

func findFreeTime(days: Int, calendarName: String?, minSlot: Int) throws -> [[String: Any]] {
  let cal = Calendar.current
  let startOfDay = cal.startOfDay(for: Date())
  let endDate = cal.date(byAdding: .day, value: days + 1, to: startOfDay)!

  var calendars: [EKCalendar]? = nil
  if let name = calendarName {
    calendars = [try findCalendar(named: name)]
  }

  let predicate = store.predicateForEvents(withStart: startOfDay, end: endDate, calendars: calendars)
  let events = store.events(matching: predicate).filter { !$0.isAllDay }

  // Merge overlapping busy intervals
  var busy: [(Date, Date)] = events.map { ($0.startDate, $0.endDate) }
  busy.sort { $0.0 < $1.0 }

  var merged: [(Date, Date)] = []
  for interval in busy {
    if let last = merged.last, interval.0 <= last.1 {
      merged[merged.count - 1] = (last.0, max(last.1, interval.1))
    } else {
      merged.append(interval)
    }
  }

  // Find free slots during working hours (8:00 - 18:00)
  var freeSlots: [[String: Any]] = []
  var currentDay = startOfDay

  while currentDay < endDate {
    var workStart = cal.date(bySettingHour: 8, minute: 0, second: 0, of: currentDay)!
    let workEnd = cal.date(bySettingHour: 18, minute: 0, second: 0, of: currentDay)!

    if workStart < Date() { workStart = Date() }
    if workStart >= workEnd {
      currentDay = cal.date(byAdding: .day, value: 1, to: currentDay)!
      continue
    }

    // Find busy intervals that overlap this day's working hours
    let dayBusy = merged.filter { $0.1 > workStart && $0.0 < workEnd }

    var cursor = workStart
    for (busyStart, busyEnd) in dayBusy {
      let slotEnd = min(busyStart, workEnd)
      if slotEnd > cursor {
        let minutes = Int(slotEnd.timeIntervalSince(cursor) / 60)
        if minutes >= minSlot {
          freeSlots.append([
            "start": isoFormatter.string(from: cursor),
            "end": isoFormatter.string(from: slotEnd),
            "minutes": minutes,
          ] as [String: Any])
        }
      }
      cursor = max(cursor, min(busyEnd, workEnd))
    }

    // Remaining time after last busy interval
    if cursor < workEnd {
      let minutes = Int(workEnd.timeIntervalSince(cursor) / 60)
      if minutes >= minSlot {
        freeSlots.append([
          "start": isoFormatter.string(from: cursor),
          "end": isoFormatter.string(from: workEnd),
          "minutes": minutes,
        ] as [String: Any])
      }
    }

    currentDay = cal.date(byAdding: .day, value: 1, to: currentDay)!
  }

  return freeSlots
}

// MARK: - Reminders

func requestReminderAccess() async throws {
  if #available(macOS 14.0, *) {
    try await store.requestFullAccessToReminders()
  } else {
    let granted = try await withCheckedThrowingContinuation {
      (cont: CheckedContinuation<Bool, Error>) in
      store.requestAccess(to: .reminder) { granted, error in
        if let error { cont.resume(throwing: error) } else {
          cont.resume(returning: granted)
        }
      }
    }
    guard granted else {
      throw CalendarError.reminderAccessDenied
    }
  }
}

func findReminderCalendar(named name: String) throws -> EKCalendar {
  guard
    let cal = store.calendars(for: .reminder).first(where: {
      $0.title.lowercased() == name.lowercased()
    })
  else {
    throw CalendarError.calendarNotFound(name)
  }
  return cal
}

func serializeReminder(_ reminder: EKReminder) -> [String: Any?] {
  var dict: [String: Any?] = [
    "id": reminder.calendarItemIdentifier,
    "calendar": reminder.calendar.title,
    "title": reminder.title,
    "isCompleted": reminder.isCompleted,
    "priority": reminder.priority,
    "notes": reminder.notes,
    "hasAlarms": reminder.hasAlarms,
  ]
  if let completionDate = reminder.completionDate {
    dict["completionDate"] = isoFormatter.string(from: completionDate)
  }
  if let dueDateComponents = reminder.dueDateComponents,
     let dueDate = Calendar.current.date(from: dueDateComponents) {
    dict["dueDate"] = isoFormatter.string(from: dueDate)
  }
  if let alarms = reminder.alarms {
    dict["alarms"] = alarms.map { ["relativeOffset": $0.relativeOffset] }
  }
  return dict
}

func fetchReminders(calendarName: String?, showCompleted: Bool) async throws -> [[String: Any?]] {
  var calendars: [EKCalendar]? = nil
  if let name = calendarName {
    calendars = [try findReminderCalendar(named: name)]
  }

  let predicate = showCompleted
    ? store.predicateForCompletedReminders(
        withCompletionDateStarting: nil, ending: nil, calendars: calendars)
    : store.predicateForIncompleteReminders(
        withDueDateStarting: nil, ending: nil, calendars: calendars)

  let reminders = try await withCheckedThrowingContinuation {
    (cont: CheckedContinuation<[EKReminder]?, Error>) in
    store.fetchReminders(matching: predicate) { reminders in
      cont.resume(returning: reminders)
    }
  }

  return (reminders ?? []).map { serializeReminder($0) }
}

func createReminder(
  title: String, calendarName: String?, dueStr: String?,
  priority: Int?, notes: String?, alarmMinutes: Int?
) throws -> [String: Any?] {
  let reminder = EKReminder(eventStore: store)
  reminder.title = title

  if let name = calendarName {
    reminder.calendar = try findReminderCalendar(named: name)
  } else {
    reminder.calendar = store.defaultCalendarForNewReminders()
  }

  if let dueStr = dueStr {
    let date = try parseDate(dueStr)
    reminder.dueDateComponents = Calendar.current.dateComponents(
      [.year, .month, .day, .hour, .minute], from: date)
  }

  if let p = priority { reminder.priority = p }
  if let n = notes { reminder.notes = n }
  if let mins = alarmMinutes {
    reminder.addAlarm(EKAlarm(relativeOffset: TimeInterval(-mins * 60)))
  }

  try store.save(reminder, commit: true)
  return serializeReminder(reminder)
}

func completeReminder(id: String) throws -> [String: Any?] {
  guard let reminder = store.calendarItem(withIdentifier: id) as? EKReminder else {
    throw CalendarError.reminderNotFound(id)
  }
  reminder.isCompleted = true
  reminder.completionDate = Date()
  try store.save(reminder, commit: true)
  return serializeReminder(reminder)
}

func deleteReminder(id: String) throws -> [String: Any] {
  guard let reminder = store.calendarItem(withIdentifier: id) as? EKReminder else {
    throw CalendarError.reminderNotFound(id)
  }
  let title = reminder.title ?? "Untitled"
  try store.remove(reminder, commit: true)
  return ["deleted": true, "title": title, "id": id] as [String: Any]
}

// MARK: - JSON Output

func output(_ value: Any) {
  if let data = try? JSONSerialization.data(
    withJSONObject: value, options: [.prettyPrinted, .sortedKeys])
  {
    // Replace NSNull with proper null representation
    if let str = String(data: data, encoding: .utf8) {
      print(str)
    }
  }
}

func outputError(_ error: Error) {
  let dict: [String: Any] = [
    "error": true,
    "message": "\(error)",
  ]
  output(dict)
}

// MARK: - Entry Point

@main
struct CalendarTool {
  static func main() async {
    let args = Array(CommandLine.arguments.dropFirst())

    guard let command = args.first else {
      outputError(CalendarError.missingArgument("command"))
      Darwin.exit(1)
    }

    do {
      try await requestAccess()

      switch command {
      case "list":
        output(listCalendars())

      case "events":
        let days = Int(getArg(args, flag: "--days") ?? "0") ?? 0
        let calendar = getArg(args, flag: "--calendar")
        output(try getEvents(days: days, calendarName: calendar))

      case "create":
        guard let title = getArg(args, flag: "--title") else {
          throw CalendarError.missingArgument("--title")
        }
        guard let startStr = getArg(args, flag: "--start") else {
          throw CalendarError.missingArgument("--start")
        }
        guard let endStr = getArg(args, flag: "--end") else {
          throw CalendarError.missingArgument("--end")
        }

        let start = try parseDate(startStr)
        let end = try parseDate(endStr)
        let calendar = getArg(args, flag: "--calendar")
        let location = getArg(args, flag: "--location")
        let description = getArg(args, flag: "--description")
        let alarm = getArg(args, flag: "--alarm")
        let allDay = hasFlag(args, flag: "--all-day")
        let availability = getArg(args, flag: "--availability")
        let urlStr = getArg(args, flag: "--url")
        let recFreq = getArg(args, flag: "--recurrence-frequency")
        let recInterval = getArg(args, flag: "--recurrence-interval").flatMap { Int($0) }
        let recEndDate = getArg(args, flag: "--recurrence-end-date")
        let recCount = getArg(args, flag: "--recurrence-count").flatMap { Int($0) }
        let recDays = getArg(args, flag: "--recurrence-days")
        let lat = getArg(args, flag: "--latitude").flatMap { Double($0) }
        let lon = getArg(args, flag: "--longitude").flatMap { Double($0) }

        output(
          try createEvent(
            title: title, start: start, end: end,
            calendarName: calendar, location: location, description: description,
            alarmStr: alarm, allDay: allDay, availability: availability, urlStr: urlStr,
            recurrenceFrequency: recFreq, recurrenceInterval: recInterval,
            recurrenceEndDate: recEndDate, recurrenceCount: recCount, recurrenceDays: recDays,
            latitude: lat, longitude: lon
          ))

      case "update":
        guard let id = getArg(args, flag: "--id") else {
          throw CalendarError.missingArgument("--id")
        }
        let span = parseSpan(getArg(args, flag: "--span"))
        let allDay: Bool? = hasFlag(args, flag: "--all-day") ? true : nil
        let lat = getArg(args, flag: "--latitude").flatMap { Double($0) }
        let lon = getArg(args, flag: "--longitude").flatMap { Double($0) }
        output(
          try updateEvent(
            id: id,
            title: getArg(args, flag: "--title"),
            startStr: getArg(args, flag: "--start"),
            endStr: getArg(args, flag: "--end"),
            calendarName: getArg(args, flag: "--calendar"),
            location: getArg(args, flag: "--location"),
            description: getArg(args, flag: "--description"),
            alarmStr: getArg(args, flag: "--alarm"),
            span: span,
            allDay: allDay,
            availability: getArg(args, flag: "--availability"),
            urlStr: getArg(args, flag: "--url"),
            latitude: lat,
            longitude: lon
          ))

      case "delete":
        guard let id = getArg(args, flag: "--id") else {
          throw CalendarError.missingArgument("--id")
        }
        let span = parseSpan(getArg(args, flag: "--span"))
        output(try deleteEvent(id: id, span: span))

      case "search":
        guard let query = getArg(args, flag: "--query") else {
          throw CalendarError.missingArgument("--query")
        }
        let calendar = getArg(args, flag: "--calendar")
        let days = Int(getArg(args, flag: "--days") ?? "365") ?? 365
        output(try searchEvents(query: query, calendarName: calendar, days: days))

      case "free-busy":
        let days = Int(getArg(args, flag: "--days") ?? "7") ?? 7
        let calendar = getArg(args, flag: "--calendar")
        let minSlot = Int(getArg(args, flag: "--min-slot") ?? "30") ?? 30
        output(try findFreeTime(days: days, calendarName: calendar, minSlot: minSlot))

      case "reminders":
        try await requestReminderAccess()
        let calendar = getArg(args, flag: "--calendar")
        let showCompleted = hasFlag(args, flag: "--completed")
        output(try await fetchReminders(calendarName: calendar, showCompleted: showCompleted))

      case "create-reminder":
        try await requestReminderAccess()
        guard let title = getArg(args, flag: "--title") else {
          throw CalendarError.missingArgument("--title")
        }
        let calendar = getArg(args, flag: "--calendar")
        let due = getArg(args, flag: "--due")
        let priority = getArg(args, flag: "--priority").flatMap { Int($0) }
        let notes = getArg(args, flag: "--notes")
        let alarm = getArg(args, flag: "--alarm").flatMap { Int($0) }
        output(try createReminder(
          title: title, calendarName: calendar, dueStr: due,
          priority: priority, notes: notes, alarmMinutes: alarm
        ))

      case "complete-reminder":
        try await requestReminderAccess()
        guard let id = getArg(args, flag: "--id") else {
          throw CalendarError.missingArgument("--id")
        }
        output(try completeReminder(id: id))

      case "delete-reminder":
        try await requestReminderAccess()
        guard let id = getArg(args, flag: "--id") else {
          throw CalendarError.missingArgument("--id")
        }
        output(try deleteReminder(id: id))

      default:
        throw CalendarError.unknownCommand(command)
      }
    } catch {
      outputError(error)
      Darwin.exit(1)
    }
  }
}
