# neon roles

Manage database roles within Neon projects.

## Subcommands

| Subcommand | Description |
|------------|-------------|
| `list` | List roles |
| `create` | Create a role |
| `delete` | Delete a role |

## list

```bash
neon roles list [options]
```

**Options:**
- `--project-id` - Project ID (required if multiple projects)
- `--branch` - Branch ID or name (defaults to primary)
- `--output json` - Get detailed JSON output

## create

```bash
neon roles create [options]
```

**Options:**
- `--name` - Role name (required, max 63 bytes)
- `--no-login` - Create passwordless role without login capability
- `--project-id` - Project ID
- `--branch` - Target branch

**Example:**
```bash
neon roles create --name readonly_user
neon roles create --name service_account --no-login
```

## delete

```bash
neon roles delete <role> [options]
```

**Options:**
- `--project-id` - Project ID
- `--branch` - Branch ID or name

**Example:**
```bash
neon roles delete readonly_user
```
