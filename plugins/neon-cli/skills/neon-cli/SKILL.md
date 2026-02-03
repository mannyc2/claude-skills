---
name: neon-cli
description: Reference for using the Neon CLI to manage Neon serverless Postgres from the terminal. Covers projects, branches, databases, roles, connection strings, and more.
---

# Neon CLI

Reference for using the Neon CLI to manage Neon serverless Postgres from the terminal.

## Quick Reference

| Command | Description |
|---------|-------------|
| `neon auth` | Authenticate with Neon |
| `neon me` | Show current user |
| `neon orgs list` | List organizations |
| `neon projects` | Manage projects |
| `neon branches` | Manage branches |
| `neon databases` | Manage databases |
| `neon roles` | Manage roles |
| `neon connection-string` | Get connection string |
| `neon set-context` | Set project/org context |
| `neon operations list` | View operations |
| `neon ip-allow` | Manage IP allowlist |
| `neon vpc` | Manage VPC endpoints |

## Installation

```bash
# macOS
brew install neonctl

# npm (all platforms)
npm i -g neonctl

# bun
bun install -g neonctl
```

## Authentication

```bash
# Browser-based auth (recommended)
neon auth

# Or use API key
export NEON_API_KEY=<your-api-key>
```

## Context Setup

Avoid specifying `--project-id` and `--org-id` repeatedly:

```bash
neon set-context --project-id <id> --org-id <org-id>
```

Creates a `.neon` file in current directory.

## Common Workflows

### Create project and connect

```bash
neon projects create --name myapp --set-context
neon connection-string --psql
```

### Create dev branch

```bash
neon branches create --name dev --parent main
neon connection-string dev
```

### Branch with time travel

```bash
# Connect to branch at specific timestamp
neon connection-string main@2024-04-21T00:00:00Z
```

### Compare schemas

```bash
neon branches schema-diff main dev
```

### Reset branch to parent

```bash
neon branches reset dev --parent
```

## Global Options

| Option | Description |
|--------|-------------|
| `-o, --output` | Output format: `json`, `yaml`, `table` (default) |
| `--api-key` | Neon API key |
| `--project-id` | Project ID |
| `--context-file` | Custom context file |
| `-h, --help` | Show help |

## References

See `references/` for detailed command documentation:
- `auth.md` - Authentication
- `projects.md` - Project management
- `branches.md` - Branch management
- `databases.md` - Database management
- `roles.md` - Role management
- `connection-string.md` - Connection strings
- `context.md` - Context setup
- `ip-allow.md` - IP allowlists
- `vpc.md` - VPC configuration
- `operations.md` - Operations
- `orgs.md` - Organizations
