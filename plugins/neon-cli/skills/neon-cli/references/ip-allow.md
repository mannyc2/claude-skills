# neon ip-allow

Manage IP allowlists for Neon projects. Supports individual addresses, ranges, and CIDR notation.

## Subcommands

| Subcommand | Description |
|------------|-------------|
| `list` | List allowed IPs |
| `add` | Add IPs to allowlist |
| `remove` | Remove IPs from allowlist |
| `reset` | Replace entire allowlist |

## list

```bash
neon ip-allow list --project-id <project-id>
neon ip-allow list --project-id <project-id> --output json
```

## add

```bash
neon ip-allow add <ips...> [options]
```

**Options:**
- `--project-id` - Project ID
- `--protected-only` - Apply only to protected branches

**Examples:**
```bash
# Add single IP
neon ip-allow add 192.0.2.3 --project-id cold-grass-40154007

# Add multiple IPs
neon ip-allow add 192.0.2.1 192.0.2.2 192.0.2.3 --project-id cold-grass-40154007

# Add CIDR range
neon ip-allow add 192.0.2.0/24 --project-id cold-grass-40154007
```

## remove

```bash
neon ip-allow remove <ips...> --project-id <project-id>
```

**Example:**
```bash
neon ip-allow remove 192.0.2.3 --project-id cold-grass-40154007
```

## reset

Clears and replaces the entire allowlist. Omitting addresses removes all entries.

```bash
# Replace with new list
neon ip-allow reset 192.0.2.1 192.0.2.2 --project-id cold-grass-40154007

# Clear all entries
neon ip-allow reset --project-id cold-grass-40154007
```
