# neon orgs

Manage Neon organizations.

## Subcommands

| Subcommand | Description |
|------------|-------------|
| `list` | List organizations |

## list

```bash
neon orgs list
```

**Table output (default):**
```
Organizations
┌────────────────────────┬──────────────────┐
│ Id                     │ Name             │
├────────────────────────┼──────────────────┤
│ org-xxxxxxxx-xxxxxxxx  │ Example Org      │
└────────────────────────┴──────────────────┘
```

**JSON output:**
```bash
neon orgs list -o json
```

Returns additional fields: `handle`, `created_at`, `updated_at`.
