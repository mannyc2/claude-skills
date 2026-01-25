---
name: twitter-research
description: Research and analyze Twitter/X content. Use when searching Twitter, analyzing tweets, researching users, tracking conversations, or investigating topics on X/Twitter.
allowed-tools: Read, Bash(python:*)
---

# Twitter Research Skill

Research Twitter/X using a clean CLI interface. Search tweets, look up users, and analyze timelines.

## Quick Reference

```bash
# Search tweets
python scripts/twitter_search.py search "AI" --min-likes 100 --no-retweets

# Get user profile  
python scripts/twitter_search.py user naval

# Get user's tweets
python scripts/twitter_search.py tweets karpathy --limit 50 --no-replies
```

## Environment

Requires `RAPIDAPI_KEY_241` environment variable.

---

## Commands

### `search` - Search Tweets

Search for tweets matching keywords with optional filters.

```bash
python scripts/twitter_search.py search "keywords" [options]
```

**User Filters:**
| Flag | Description |
|------|-------------|
| `--from USER` | Tweets from this user |
| `--to USER` | Replies to this user |
| `--mention USER` | Tweets mentioning this user |

**Content Filters:**
| Flag | Description |
|------|-------------|
| `--hashtag TAG` | Include hashtag (repeatable: `-t ai -t ml`) |
| `--exclude WORD` | Exclude word (repeatable: `-x spam -x ad`) |

**Engagement Filters:**
| Flag | Description |
|------|-------------|
| `--min-likes N` | Minimum likes |
| `--min-retweets N` | Minimum retweets |
| `--min-replies N` | Minimum replies |

**Date Filters:**
| Flag | Description |
|------|-------------|
| `--since YYYY-MM-DD` | Tweets after this date |
| `--until YYYY-MM-DD` | Tweets before this date |
| `--days N` | Tweets from last N days |

**Tweet Type Filters:**
| Flag | Description |
|------|-------------|
| `--no-retweets` | Exclude retweets |
| `--no-replies` | Exclude replies |
| `--only-replies` | Only show replies |

**Media Filters:**
| Flag | Description |
|------|-------------|
| `--has-media` | Has any media |
| `--has-images` | Has images |
| `--has-videos` | Has videos |
| `--has-links` | Has links |
| `--url DOMAIN` | Links to specific domain |

**Other:**
| Flag | Description |
|------|-------------|
| `--lang CODE` | Language (en, es, ja, etc.) |
| `--limit N` | Max results (default: 20) |
| `--format FORMAT` | Output: text, json, csv |
| `-v, --verbose` | Show debug info including generated query |

---

### `user` - User Profile

Look up a Twitter user's profile.

```bash
python scripts/twitter_search.py user USERNAME [--format text|json]
```

Returns: ID, username, display name, follower count, bio.

---

### `tweets` - User Timeline

Get tweets from a specific user.

```bash
python scripts/twitter_search.py tweets USERNAME [options]
```

**Options:**
| Flag | Description |
|------|-------------|
| `--no-retweets` | Exclude retweets |
| `--no-replies` | Exclude replies |
| `--only-replies` | Only show replies |
| `--since YYYY-MM-DD` | After this date |
| `--until YYYY-MM-DD` | Before this date |
| `--days N` | Last N days |
| `--limit N` | Max results (default: 20) |
| `--format FORMAT` | Output: text, json, csv |

---

## Examples

### Find Popular AI Tweets
```bash
python scripts/twitter_search.py search "artificial intelligence" \
  --min-likes 500 --no-retweets --lang en --limit 50
```

### Research a Specific User
```bash
# Get profile
python scripts/twitter_search.py user elonmusk

# Get their original tweets (no RTs/replies)
python scripts/twitter_search.py tweets elonmusk \
  --no-retweets --no-replies --limit 100
```

### Track Startup News
```bash
python scripts/twitter_search.py search "raised funding" \
  --min-likes 100 --has-links --days 7
```

### Find Research Papers Being Shared
```bash
python scripts/twitter_search.py search "" \
  --url arxiv.org --min-likes 50 --limit 30
```

### Monitor Mentions of a Company
```bash
python scripts/twitter_search.py search "" \
  --mention anthropic --days 3 --limit 100 --format json
```

### Get Replies to a User
```bash
python scripts/twitter_search.py search "" \
  --to sama --days 7 --limit 50
```

### Export for Analysis
```bash
# JSON for programmatic processing
python scripts/twitter_search.py search "topic" --format json > data.json

# CSV for spreadsheets
python scripts/twitter_search.py tweets karpathy --format csv > tweets.csv
```

---

## Research Strategies

### Analyzing a Topic
1. Start with broad keyword search: `search "topic" --min-likes 100`
2. Note which users appear frequently
3. Deep dive into those users: `tweets username --no-retweets`
4. Check what they're replying to: `tweets username --only-replies`

### Competitive Intelligence  
1. Monitor competitor: `search "" --mention competitor --days 7`
2. Track their announcements: `tweets competitor --no-retweets --no-replies`
3. See customer feedback: `search "" --to competitor --days 30`

### Finding Influencers
1. Search topic with high engagement: `search "topic" --min-likes 500`
2. Note usernames from top tweets
3. Look up each: `user username`
4. Analyze their content: `tweets username --limit 50`

### Tracking Breaking News
1. Recent activity: `search "event" --days 1 --limit 100`
2. Filter to quality: add `--min-likes 50 --no-retweets`
3. Find primary sources: `--has-links`

---

## Output Formats

**text** (default): XML format optimized for Claude parsing

```xml
<results>
<summary>
  <query>AI min_faves:100</query>
  <total_tweets>50</total_tweets>
  <unique_authors>35</unique_authors>
  <engagement likes="125000" retweets="8500" replies="3200" />
  <avg_likes>2500.0</avg_likes>
  <breakdown original="40" replies="5" retweets="0" quotes="5" with_media="12" />
  <top_authors>
    <author username="influential_user" tweets="3" total_likes="45000" />
  </top_authors>
</summary>
<tweets>
<tweet index="1" id="1234567890">
  <author username="user1">Display Name</author>
  <date>Mon Jan 13 15:30:00 +0000 2025</date>
  <content>Tweet text here...</content>
  <metrics likes="5000" retweets="200" replies="50" views="100000" />
  <url>https://twitter.com/user1/status/1234567890</url>
</tweet>
</tweets>
</results>
```

**json**: Structured JSON with summary and tweets array
```json
{
  "summary": {
    "query": "AI min_faves:100",
    "total": 50,
    "unique_authors": 35,
    "total_likes": 125000,
    "avg_likes": 2500.0,
    "top_authors": [{"username": "user", "tweets": 3, "total_likes": 45000}]
  },
  "tweets": [...]
}
```

**csv**: Spreadsheet-compatible format (no summary)

---

## Tips

1. **Use `--verbose`** to see the generated query for debugging
2. **Start with `--limit 20`** to validate results before larger fetches
3. **Combine `--no-retweets --no-replies`** for original content only
4. **Use `--days N`** instead of calculating dates manually
5. **Export to JSON** for further analysis or archiving
