# Instruments CLI Workflow

Command-line workflow for recording, exporting, and analyzing `.trace` files using `xctrace`.

## Quick Reference

```bash
# List available templates and instruments
xctrace list templates
xctrace list instruments
xctrace list devices

# Record (attach to running app)
xctrace record --template 'Time Profiler' --attach watchify --output perf.trace --time-limit 30s

# Record (launch app)
xctrace record --template 'Time Profiler' --time-limit 30s --launch -- /path/to/watchify.app/Contents/MacOS/watchify

# Export table of contents
xctrace export --input perf.trace --toc

# Export signposts to XML
xctrace export --input perf.trace --xpath '/trace-toc/run[@number="1"]/data/table[@schema="os-signpost"]' --output signposts.xml

# Symbolicate
xctrace symbolicate --input perf.trace --dsym /path/to/watchify.dSYM
```

## Recording

### Templates for Common Tasks

| Template | Use Case |
|----------|----------|
| `Time Profiler` | CPU sampling, call trees, hang detection |
| `SwiftUI` | View body updates, hitches, cause graphs |
| `Allocations` | Memory allocations, leaks |
| `Leaks` | Memory leak detection |
| `Swift Concurrency` | Task/actor analysis |
| `System Trace` | Low-level system events |
| `App Launch` | Launch time optimization |

### Record by Attaching to Running Process

```bash
# By name
xctrace record --template 'Time Profiler' --attach watchify --output perf.trace

# By PID
xctrace record --template 'Time Profiler' --attach 12345 --output perf.trace

# With time limit
xctrace record --template 'Time Profiler' --attach watchify --time-limit 30s --output perf.trace
```

### Record by Launching App

```bash
# Launch and record
xctrace record --template 'Time Profiler' --output launch.trace \
  --launch -- /path/to/watchify.app/Contents/MacOS/watchify

# With arguments
xctrace record --template 'Time Profiler' --output test.trace \
  --launch -- /path/to/app arg1 arg2

# Capture stdout
xctrace record --template 'Time Profiler' --target-stdout - \
  --launch -- /path/to/app
```

### Record All Processes (System-Wide)

```bash
xctrace record --template 'System Trace' --all-processes --time-limit 10s --output system.trace
```

### Add Specific Instruments to Recording

```bash
xctrace record --template 'Time Profiler' \
  --instrument 'os_signpost' \
  --instrument 'Hangs' \
  --attach watchify --output perf.trace
```

### Useful Instruments

| Instrument | Data Captured |
|------------|---------------|
| `os_signpost` | Custom signpost intervals/events |
| `Time Profiler` | CPU samples with call stacks |
| `Hangs` | Main thread hangs (>250ms) |
| `SwiftUI` | View updates, causes |
| `Swift Tasks` | Async task lifecycle |
| `Swift Actors` | Actor isolation/contention |
| `Allocations` | Heap allocations |
| `Points of Interest` | os_log points of interest |

## Exporting Data

### Export Table of Contents

```bash
xctrace export --input perf.trace --toc
```

Shows available schemas and run info. Use this to find XPath queries.

### Common Export Schemas

```bash
# Signposts (custom intervals)
xctrace export --input perf.trace \
  --xpath '/trace-toc/run[@number="1"]/data/table[@schema="os-signpost"]' \
  --output signposts.xml

# Time profile samples
xctrace export --input perf.trace \
  --xpath '/trace-toc/run[@number="1"]/data/table[@schema="time-sample"]' \
  --output samples.xml

# Hang events
xctrace export --input perf.trace \
  --xpath '/trace-toc/run[@number="1"]/data/table[@schema="potential-hangs"]' \
  --output hangs.xml

# Process info (binary images)
xctrace export --input perf.trace \
  --xpath '/trace-toc/run[@number="1"]/processes' \
  --output processes.xml

# Specific process
xctrace export --input perf.trace \
  --xpath '/trace-toc/run[@number="1"]/processes/process[@name="watchify"]' \
  --output watchify-images.xml
```

### Export from Specific Run

```bash
# Run 1
xctrace export --input perf.trace --xpath '/trace-toc/run[@number="1"]/data/table[@schema="os-signpost"]'

# Run 2
xctrace export --input perf.trace --xpath '/trace-toc/run[@number="2"]/data/table[@schema="os-signpost"]'
```

## Symbolication

```bash
# Auto-locate dSYMs
xctrace symbolicate --input perf.trace

# Specific dSYM
xctrace symbolicate --input perf.trace --dsym /path/to/watchify.dSYM

# Symbolicate and save to new file
xctrace symbolicate --input perf.trace --output perf-symbolicated.trace --dsym /path/to/dSYMs/
```

## Unified Logging (Text Spans)

Since signposts don't work in async code, use text logging with `SPAN_BEGIN`/`SPAN_END`:

```bash
# Stream logs in real-time
log stream --predicate 'subsystem == "cjpher.watchify"' --level debug

# Stream with timestamps
log stream --predicate 'subsystem == "cjpher.watchify"' --level debug --style compact

# Filter to specific category
log stream --predicate 'subsystem == "cjpher.watchify" AND category == "db"' --level debug

# Save to file for analysis
log stream --predicate 'subsystem == "cjpher.watchify"' --level debug > /tmp/app.log &
# ... run app ...
kill %1

# Show historical logs
log show --predicate 'subsystem == "cjpher.watchify"' --last 5m
```

### Parse Span Logs

```bash
# Extract span timings
grep -E 'SPAN_(BEGIN|END)' /tmp/app.log

# Calculate durations (spans include dt=)
grep 'SPAN_END' /tmp/app.log | sed 's/.*dt=\([0-9.]*\)s.*/\1/' | sort -rn | head -10
```

## Workflow Examples

### Profile Store Navigation Performance

```bash
# 1. Build release
~/bin/xcede build

# 2. Launch app, then record
xctrace record --template 'Time Profiler' \
  --instrument 'os_signpost' \
  --attach watchify \
  --time-limit 30s \
  --output store-nav.trace

# 3. Navigate to stores in the app, then wait for recording to complete

# 4. Export signposts
xctrace export --input store-nav.trace --toc
xctrace export --input store-nav.trace \
  --xpath '/trace-toc/run[@number="1"]/data/table[@schema="os-signpost"]' \
  --output store-nav-signposts.xml

# 5. Open in Instruments for visual analysis
open store-nav.trace
```

### Profile SwiftUI View Updates

```bash
# Record with SwiftUI template
xctrace record --template 'SwiftUI' \
  --attach watchify \
  --time-limit 20s \
  --output swiftui.trace

# Open for cause-effect graph analysis
open swiftui.trace
```

### Profile App Launch

```bash
# Record launch
xctrace record --template 'App Launch' \
  --output launch.trace \
  --launch -- ~/Library/Developer/Xcode/DerivedData/watchify-*/Build/Products/Release/watchify.app/Contents/MacOS/watchify

# Analyze
open launch.trace
```

### Headless CI Profiling

```bash
#!/bin/bash
# ci-profile.sh - Run in CI to catch performance regressions

APP_PATH="$1"
OUTPUT_DIR="${2:-/tmp/traces}"
mkdir -p "$OUTPUT_DIR"

# Record 10 seconds of app running
xctrace record --template 'Time Profiler' \
  --time-limit 10s \
  --output "$OUTPUT_DIR/ci-profile.trace" \
  --launch -- "$APP_PATH"

# Export hangs
xctrace export --input "$OUTPUT_DIR/ci-profile.trace" \
  --xpath '/trace-toc/run[@number="1"]/data/table[@schema="potential-hangs"]' \
  --output "$OUTPUT_DIR/hangs.xml"

# Check for hangs (fail CI if any found)
if grep -q '<row>' "$OUTPUT_DIR/hangs.xml" 2>/dev/null; then
  echo "FAIL: Hangs detected"
  cat "$OUTPUT_DIR/hangs.xml"
  exit 1
fi

echo "PASS: No hangs detected"
```

## Tips

1. **Time Profiler vs Processor Trace**: Time Profiler uses sampling (~1ms intervals). Processor Trace (M4+ only) captures every instruction with <1% overhead.

2. **Signposts in async code crash**: Use text logging (`SPAN_BEGIN`/`SPAN_END`) for async spans. Only use `OSSignposter` intervals in synchronous code.

3. **Symbolication**: Always symbolicate before analyzing. Use `--dsym` with your app's dSYM for accurate function names.

4. **Multiple runs**: Use `--append-run` to add runs to an existing trace file for A/B comparison.

5. **Windowed recording**: Use `--window 5s` for ring-buffer mode that keeps only the last N seconds (useful for catching intermittent issues).

## Project Conventions

### Folder Structure

```
traces/                              # Gitignored
├── .gitkeep
├── 2026-01-22-store-nav.trace/
│   └── exports/                     # Parsed data inside trace
│       ├── signposts.xml
│       ├── hangs.xml
│       └── analysis.md
└── 2026-01-22-sync-perf.trace/
```

### Naming

```
YYYY-MM-DD-<description>.trace
```

### Exports

Store exports **inside** the trace bundle at `<trace>/exports/`. Keeps data together, deletes as a unit.

```bash
TRACE="traces/2026-01-22-example.trace"
mkdir -p "$TRACE/exports"

xctrace export --input "$TRACE" --toc > "$TRACE/exports/toc.txt"

xctrace export --input "$TRACE" \
  --xpath '/trace-toc/run[@number="1"]/data/table[@schema="os-signpost"]' \
  --output "$TRACE/exports/signposts.xml"

xctrace export --input "$TRACE" \
  --xpath '/trace-toc/run[@number="1"]/data/table[@schema="potential-hangs"]' \
  --output "$TRACE/exports/hangs.xml"
```

### Helper Script

`scripts/trace.sh` provides shortcuts:

```bash
./scripts/trace.sh record store-nav --time 30    # Record
./scripts/trace.sh export traces/*.trace         # Export
./scripts/trace.sh list                          # List with sizes
./scripts/trace.sh clean --keep 5                # Prune old
```

### .gitignore

```gitignore
traces/*.trace
!traces/.gitkeep
```
