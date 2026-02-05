# refactor-tools

MCP-based plugin providing programmatic code analysis tools for structured refactoring workflows.

## Tools

| Tool | Description |
|------|-------------|
| `get_dependency_graph` | Map imports/exports across the codebase, detect circular dependencies |
| `find_unused_exports` | Detect dead code by finding exports never imported |
| `get_complexity_report` | Analyze LOC, nesting depth, function counts with configurable thresholds |
| `check_orphans` | Find broken imports that reference non-existent files |
| `diff_file_tree` | Git-based file tree diff showing added/deleted/modified/renamed files |

## Usage

Install the plugin in Claude Code:

```bash
claude --plugin-dir /path/to/refactor-tools
```

Then use `/refactor-team` to start a team-based refactoring workflow, or call tools directly.

**Prerequisite:** Requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in your settings (agent teams is an experimental feature).

## Workflow

The `/refactor-team` skill parallelizes analysis and implementation using agent teams:

1. **PARALLEL SCAN** -- Two analyst agents run simultaneously (structure + quality)
2. **SYNTHESIZE** -- Lead combines both reports into unified analysis
3. **PLAN + PARTITION** -- Create manifest and partition into independent file groups
4. **PARALLEL IMPLEMENTATION** -- Multiple implementer agents work on separate file groups
5. **VERIFY** -- Lead runs full verification suite

## Agents

| Agent | Role |
|-------|------|
| `analyst-structure` | Runs dependency graph and orphan checks, produces a Structure Report |
| `analyst-quality` | Runs unused export and complexity analysis, produces a Quality Report |
| `refactor-implementer` | Implements approved changes for an assigned group of files |

Analysts run in parallel during the scan phase. Multiple implementers run in parallel during implementation, each scoped to a non-overlapping set of files.

## Development

```bash
cd refactor-tools
bun install
bun run src/server.ts  # Test standalone
```
