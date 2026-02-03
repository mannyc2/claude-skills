# neon auth

Authenticate with Neon from the terminal.

## Usage

```bash
neon auth
```

Opens a browser window for authorization. Credentials are stored in:
```
~/.config/neonctl/credentials.json
```

## Authentication priority

The CLI authenticates in this order:

1. `--api-key` option (highest priority)
2. `NEON_API_KEY` environment variable
3. `credentials.json` file (from `neon auth`)
4. Web authentication flow (if no credentials found)

## Using API keys

Instead of `neon auth`, you can use an API key:

```bash
# Per-command
neon projects list --api-key <your-api-key>

# Via environment variable
export NEON_API_KEY=<your-api-key>
neon projects list
```

## Notes

- Users on Vercel-Managed Integration must use API key authentication
- Create API keys in the Neon Console under Account Settings
