# neon projects

Manage Neon projects from the terminal.

## Subcommands

| Subcommand | Description |
|------------|-------------|
| `list` | List projects |
| `create` | Create a project |
| `update` | Update project settings |
| `delete` | Delete a project |
| `recover` | Restore deleted project (Early Access) |
| `get` | Get project details |

## list

```bash
neon projects list [options]
```

**Options:**
- `--org-id` - List projects for specific organization
- `--recoverable-only` - List only recoverable deleted projects

## create

```bash
neon projects create [options]
```

**Options:**
- `--name` - Project name
- `--region-id` - Region (default: `aws-us-east-2`)
- `--psql` - Connect via psql immediately after creation
- `--cu` - Compute size, fixed or range (e.g., `0.5-3`)
- `--block-public-connections` - Block public connections
- `--block-vpc-connections` - Block VPC connections
- `--hipaa` - Enable HIPAA compliance
- `--set-context` - Set CLI context to new project

**Examples:**
```bash
# Create project with default settings
neon projects create --name myproject

# Create with specific compute size
neon projects create --name myproject --cu 2

# Create with autoscaling range
neon projects create --name myproject --cu 0.5-3

# Create and connect via psql
neon projects create --name myproject --psql

# Create and set as current context
neon projects create --name myproject --set-context
```

## update

```bash
neon projects update <id> [options]
```

**Options:**
- `--name` - New project name
- `--block-public-connections` - Toggle public connections
- `--block-vpc-connections` - Toggle VPC connections
- `--cu` - Adjust compute resources
- `--hipaa` - Enable HIPAA

## delete

```bash
neon projects delete <id>
```

## recover

```bash
neon projects recover <id>
```

Restores a deleted project within the recovery window.

## get

```bash
neon projects get <id>
neon projects get <id> --output json
```
