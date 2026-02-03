# neon branches

Manage Neon branches from the terminal.

## Subcommands

| Subcommand | Description |
|------------|-------------|
| `list` | List branches in a project |
| `create` | Create a new branch |
| `reset` | Reset branch to parent's state |
| `restore` | Restore branch to point in time |
| `rename` | Rename a branch |
| `schema-diff` | Compare schemas between branches |
| `set-default` | Set default branch |
| `set-expiration` | Set auto-deletion date |
| `add-compute` | Add compute endpoint |
| `delete` | Delete a branch |
| `get` | Get branch details |

## list

```bash
neon branches list --project-id <id>
neon branches list --output json
```

## create

```bash
neon branches create [options]
```

**Options:**
- `--name` - Branch name
- `--parent` - Parent branch name/ID
- `--cu` - Compute size (fixed or range)
- `--type` - `read_only` or `read_write`
- `--expires-at` - Expiration timestamp (ISO 8601)

**Examples:**
```bash
# Create branch from default parent
neon branches create --name feature-branch

# Create from specific parent
neon branches create --name feature-branch --parent main

# Create with specific compute
neon branches create --name feature-branch --cu 2

# Create with autoscaling
neon branches create --name feature-branch --cu 0.5-3

# Create read-only branch
neon branches create --name analytics --type read_only

# Create with expiration
neon branches create --name temp-branch --expires-at 2025-08-15T18:00:00Z
```

## reset

Reset a child branch to match its parent's current state.

```bash
neon branches reset <id|name> --parent

# Preserve current state before reset
neon branches reset <id|name> --parent --preserve-under-name backup-branch
```

## restore

Restore a branch to a specific point in time.

```bash
# Restore to timestamp (self)
neon branches restore <target> ^self@<timestamp> --preserve-under-name backup

# Restore from another branch
neon branches restore <target> <source-branch>

# Restore from parent at timestamp
neon branches restore <target> ^parent@<timestamp>
```

## rename

```bash
neon branches rename <id|name> <new-name>
```

## schema-diff

Compare schemas between branches.

```bash
# Compare two branches
neon branches schema-diff <base-branch> <compare-branch>

# Compare branch with its past state
neon branches schema-diff <branch> ^self@<timestamp>

# Compare branch with parent
neon branches schema-diff <branch> ^parent
```

## set-default

```bash
neon branches set-default <id|name>
```

## set-expiration

```bash
# Set expiration
neon branches set-expiration <id|name> --expires-at 2025-08-15T18:00:00Z

# Clear expiration
neon branches set-expiration <id|name>
```

## add-compute

```bash
# Add read-only compute
neon branches add-compute <id|name> --type read_only

# Add with specific size
neon branches add-compute <id|name> --cu 2

# Add with autoscaling
neon branches add-compute <id|name> --cu 0.5-3
```

## delete

```bash
neon branches delete <id|name>
```

## get

```bash
neon branches get <id|name>
neon branches get <id|name> --output json
```
