---
name: twitter-research
description: Research and analyze Twitter/X content. Use when searching Twitter, analyzing tweets, researching users, tracking conversations, or investigating topics on X/Twitter.
allowed-tools: mcp__twitter-research__search_tweets, mcp__twitter-research__get_user, mcp__twitter-research__get_user_tweets, mcp__twitter-research__get_profile, mcp__twitter-research__find_users, mcp__twitter-research__search_people, mcp__twitter-research__get_users_batch, mcp__twitter-research__get_user_media, mcp__twitter-research__get_user_followers, mcp__twitter-research__get_user_following, mcp__twitter-research__search_communities, mcp__twitter-research__get_community_members, mcp__twitter-research__get_replies, mcp__twitter-research__get_list_timeline
---

# Twitter Research Skill

Research Twitter/X using MCP tools. Search tweets, look up users, and analyze timelines.

## Tools

### `search_tweets` — Search Tweets

Search for tweets matching keywords with optional filters.

**Key parameters:**
| Parameter | Description |
|-----------|-------------|
| `keywords` | Search keywords |
| `from` | Tweets from this user |
| `to` | Replies to this user |
| `mention` | Tweets mentioning this user |
| `hashtags` | Array of hashtags to include |
| `exclude` | Array of words to exclude |
| `minLikes` | Minimum likes |
| `minRetweets` | Minimum retweets |
| `since` / `until` | Date range (YYYY-MM-DD) |
| `days` | Tweets from last N days |
| `noRetweets` | Exclude retweets (default: true) |
| `noReplies` | Exclude replies |
| `hasMedia` / `hasLinks` | Media/link filters |
| `lang` | Language code (en, es, ja, etc.) |
| `limit` | Max results (default: 20) |
| `preset` | Use preset: `indie`, `viral`, `recent` |

### `get_user` — User Profile

Look up a Twitter user's profile by username. Returns ID, username, display name, follower count, bio.

### `get_user_tweets` — User Timeline

Get a user's recent tweets with optional filters (noRetweets, noReplies, since, until, days, limit).

### `get_profile` — Full Profile + Tweets

Get user profile combined with their recent original tweets in one call.

### `find_users` — Find Users (Legacy)

Find Twitter users by name or keyword. Prefer `search_people` for richer results.

### `search_people` — People Search

Search for users by name, keyword, or topic. Returns profiles with bios, follower counts, and verification status.

**Key parameters:**
| Parameter | Description |
|-----------|-------------|
| `query` | Search query for finding users |
| `maxFollowers` | Filter: only return users with fewer than N followers |
| `bioContains` | Filter: bio must contain this text (case-insensitive) |
| `limit` | Max results (default: 20) |
| `cursor` | Pagination cursor |

### `get_users_batch` — Batch User Lookup

Look up multiple users by their numeric IDs in one API call. Pass `userIds` array of rest_ids.

### `get_user_media` — User Media Timeline

Get a user's media posts only (images/videos). Useful for evaluating a creator's visual content.

### `get_user_followers` — User Followers

Get a user's followers. Returns profiles with bios and follower counts.

### `get_user_following` — User Following

Get who a user follows. Returns profiles with bios and follower counts.

### `search_communities` — Community Search

Search for Twitter communities by keyword. Returns names, descriptions, and member counts.

### `get_community_members` — Community Members

Get members of a community by ID. Returns user profiles.

### `get_replies` — Tweet Replies

Get replies to a specific tweet by ID. Supports `rankingMode`: Recency, Relevance (default), Likes.

### `get_list_timeline` — List Timeline

Get recent tweets from a Twitter list by list ID. Supports `limit` and `days` filters.

---

## Research Strategies

### Analyzing a Topic
1. Start with broad search: `search_tweets` with keywords and `minLikes: 100`
2. Note which users appear frequently
3. Deep dive into those users: `get_user_tweets` with `noRetweets: true`
4. Check what they're replying to: `get_user_tweets` with `onlyReplies: true`

### Competitive Intelligence
1. Monitor competitor: `search_tweets` with `mention` set to competitor
2. Track their announcements: `get_user_tweets` with `noRetweets: true, noReplies: true`
3. See customer feedback: `search_tweets` with `to` set to competitor

### Finding Influencers
1. `search_people` with niche keywords + `maxFollowers: 50000` for smaller creators
2. Use `bioContains` to filter by bio keywords
3. Deep dive: `get_profile` for user info + recent tweets
4. Check their media: `get_user_media` for visual content quality

### Discovering via Communities
1. `search_communities` with topic keywords (e.g., "AI video", "AI filmmaking")
2. `get_community_members` on promising communities
3. Filter members by follower count for targeted outreach

### Network Mapping
1. `get_user_following` to see who a key account follows
2. `get_user_followers` to find their audience
3. Cross-reference with `search_people` to find accounts in the same niche

### Tracking Breaking News
1. Recent activity: `search_tweets` with `days: 1, limit: 100`
2. Filter to quality: add `minLikes: 50, noRetweets: true`
3. Find primary sources: add `hasLinks: true`

---

## Output Format

Results are returned as XML optimized for Claude parsing:

```xml
<results>
<summary>
  <query>AI min_faves:100</query>
  <total_tweets>50</total_tweets>
  <unique_authors>35</unique_authors>
  <engagement likes="125000" retweets="8500" replies="3200" />
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

Structured JSON data is also included for programmatic analysis.

---

## Environment

Requires `RAPIDAPI_KEY_241` environment variable (configured via MCP server).

## Tips

1. **Start with `limit: 20`** to validate results before larger fetches
2. **Combine `noRetweets: true` and `noReplies: true`** for original content only
3. **Use `days`** instead of calculating dates manually
4. **Use `get_profile`** instead of separate `get_user` + `get_user_tweets` calls
5. **Use `search_people`** instead of `find_users` for richer results with bio filtering
6. **Tweet results include `authorFollowersCount`** — use this to gauge author reach without extra lookups
7. **Use `get_users_batch`** when you have rest_ids from search results to avoid N+1 lookups
