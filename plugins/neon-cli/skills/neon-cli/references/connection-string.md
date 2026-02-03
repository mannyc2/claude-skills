# neon connection-string

Get Postgres connection strings for Neon databases.

## Usage

```bash
neon connection-string [branch[@timestamp|@LSN]] [options]
```

When branch is omitted, uses the default branch.

## Options

| Option | Description |
|--------|-------------|
| `--project-id` | Project ID (required if multiple) |
| `--role-name` | Role to connect as |
| `--database-name` | Database to connect to |
| `--pooled` | Enable connection pooling |
| `--prisma` | Optimize for Prisma (extended timeout) |
| `--endpoint-type` | `read_only` or `read_write` (default) |
| `--psql` | Connect directly via psql |
| `--extended` | Show additional information |

## Examples

### Basic connection string

```bash
neon connection-string
neon connection-string mybranch
```

### Pooled connection

```bash
neon connection-string --pooled
```

### Prisma-optimized

```bash
neon connection-string --prisma
```

### Time travel queries

Connect to database at a specific point in time:

```bash
neon connection-string @2024-04-21T00:00:00Z
neon connection-string mybranch@2024-04-21T00:00:00Z
```

### Direct psql connection

```bash
# Open psql session
neon connection-string --psql

# Execute SQL file
neon connection-string --psql -- -f dump.sql

# Run single command
neon connection-string --psql -- -c "SELECT version()"
```

### Read-only endpoint

```bash
neon connection-string --endpoint-type read_only
```
