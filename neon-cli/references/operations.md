# neon operations

View operations within a Neon project.

## Subcommands

| Subcommand | Description |
|------------|-------------|
| `list` | List operations |

## list

```bash
neon operations list [options]
```

**Options:**
- `--project-id` - Project ID (required if multiple projects)
- `--context-file` - Context file path

**Output:**
| Field | Description |
|-------|-------------|
| Id | Operation identifier |
| Action | Operation type (e.g., `apply_config`, `suspend_compute`) |
| Status | Result (e.g., `finished`) |
| Created At | ISO timestamp |

**Example:**
```bash
neon operations list
neon operations list --project-id my-project-id
```
