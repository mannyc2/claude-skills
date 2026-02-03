# neon set-context

Set background context for CLI sessions to avoid specifying project/org IDs repeatedly.

## How it works

Creates a `.neon` file in your project directory containing context data. The CLI searches up the directory tree for this file, stopping at directories containing `.neon`, `package.json`, or `.git`.

Context persists until you reset it or delete the context file.

## Usage

```bash
# Set project context (creates .neon file)
neon set-context --project-id <project-id>

# Set org and project context
neon set-context --org-id <org-id> --project-id <project-id>

# Use custom context file
neon set-context --project-id <project-id> --context-file mycontext
```

## Options

| Option | Description |
|--------|-------------|
| `--project-id` | Set project as context |
| `--org-id` | Set organization context |
| `--context-file` | Custom context file path |

At least one option is required.

## Examples

### Set default context

```bash
neon set-context --project-id patient-frost-50125040 --org-id org-bright-sky-12345678

# Now commands use this context automatically
neon branches list
```

### Multiple context files

```bash
# Create context for dev project
neon set-context --project-id dev-project-123 --context-file dev_context

# Create context for prod project
neon set-context --project-id prod-project-456 --context-file prod_context

# Switch between contexts
neon branches list --context-file dev_context
neon branches list --context-file prod_context
```

### Set context during project creation

```bash
neon projects create --name MyProject --set-context
```

## Context file format

```json
{
  "projectId": "quiet-water-76237589",
  "orgId": "org-solid-base-83603457"
}
```

## Clearing context

```bash
# Reset context
neon set-context

# Or delete the file
rm .neon
```

## Security

Neon does not save auth tokens to the context file - safe to commit to repos.
