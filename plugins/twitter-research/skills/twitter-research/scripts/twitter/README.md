# Twitter Research CLI

Search tweets, look up users, and analyze timelines via RapidAPI Twitter241.

## Usage

```bash
bun run cli research tw <command> [args] [options]
```

## Commands

### search - Search Tweets

```bash
bun run cli research tw search "keywords" [limit] [options]
```

Retweets excluded by default. Use `--with-retweets` to include.

**Filters:**

| Flag | Description |
|------|-------------|
| `--from USER` | Tweets from user |
| `--to USER` | Replies to user |
| `--mention USER` | Mentioning user |
| `--hashtag TAG` | Include hashtag (repeatable) |
| `--exclude WORD` | Exclude word (repeatable) |
| `--or KEYWORD` | OR keyword (repeatable) |
| `--min-likes N` | Minimum likes |
| `--min-retweets N` | Minimum retweets |
| `--min-replies N` | Minimum replies |
| `--since YYYY-MM-DD` | After date |
| `--until YYYY-MM-DD` | Before date |
| `--days N` | Last N days |
| `--with-retweets` | Include retweets |
| `--no-replies` | Exclude replies |
| `--only-replies` | Only replies |
| `--has-media` | Has media |
| `--has-images` | Has images |
| `--has-videos` | Has videos |
| `--has-links` | Has links |
| `--url DOMAIN` | Links to domain |
| `--lang CODE` | Language code |
| `--preset NAME` | indie, viral, recent |
| `--format FORMAT` | text, json |

### user - User Profile

```bash
bun run cli research tw user USERNAME
```

### tweets - User Timeline

```bash
bun run cli research tw tweets USERNAME [limit] [options]
```

Same filters as search (where applicable).

### profile - User + Tweets

```bash
bun run cli research tw profile USERNAME [limit]
```

Shows bio and recent original tweets in one call. Default 10 tweets.

### find - Find Users

```bash
bun run cli research tw find "name"
```

Search users by name/keyword. Returns top 10 by follower count.

## Presets

| Preset | Equivalent |
|--------|------------|
| `--preset indie` | `--min-likes 100 --lang en` |
| `--preset viral` | `--min-likes 1000` |
| `--preset recent` | `--days 7` |

## Examples

```bash
# Popular indie hacker tweets
bun run cli research tw search "indie hacker" 30 --preset indie

# Revenue discussions
bun run cli research tw search "MRR" --or "revenue" --or "ARR" --min-likes 200

# Research a founder
bun run cli research tw profile levelsio
bun run cli research tw tweets levelsio 50 --no-replies

# Track launches
bun run cli research tw search "just shipped" 30 --min-likes 100 --days 7

# Monitor mentions
bun run cli research tw search "" 50 --mention anthropic --days 3
```

## Environment

Requires `RAPIDAPI_KEY_241` in root `.env`.

## Architecture

```
twitter/
├── index.ts          # Entry point, arg parsing
├── types.ts          # Zod schemas, TypeScript types
├── client.ts         # RapidAPI client
├── query-builder.ts  # Twitter query syntax
├── formatter.ts      # Markdown output
├── presets.ts        # Preset definitions
└── commands/
    ├── search.ts
    ├── user.ts
    ├── tweets.ts
    ├── find.ts
    └── profile.ts
```
