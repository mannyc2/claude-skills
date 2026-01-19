# neon databases

Manage databases within Neon projects.

## Subcommands

| Subcommand | Description |
|------------|-------------|
| `list` | List databases |
| `create` | Create a database |
| `delete` | Delete a database |

## list

```bash
neon databases list [options]
```

**Options:**
- `--project-id` - Project ID (required if multiple projects)
- `--branch` - Branch ID or name (defaults to primary)

**Example:**
```bash
neon databases list --branch br-autumn-dust-190886
```

## create

```bash
neon databases create [options]
```

**Options:**
- `--name` - Database name (required)
- `--owner-name` - Role to own the database
- `--branch` - Target branch (defaults to primary)
- `--project-id` - Project ID

**Example:**
```bash
neon databases create --name mynewdb --owner-name john
```

## delete

```bash
neon databases delete <database> [options]
```

**Options:**
- `--project-id` - Project ID
- `--branch` - Branch ID or name

**Example:**
```bash
neon databases delete mydb
```
