import type { TwitterUser, TwitterTweet, TwitterCommunity, SearchSummary, OutputFormat } from './types'

function formatLikes(count: number): string {
  if (count >= 1000000) return `${(count / 1000000).toFixed(1)}M`
  if (count >= 1000) return `${(count / 1000).toFixed(1)}K`
  return count.toString()
}

function computeSummary(tweets: TwitterTweet[], query: string): SearchSummary {
  const authors: Record<string, { count: number; likes: number }> = {}

  for (const tweet of tweets) {
    if (!authors[tweet.username]) {
      authors[tweet.username] = { count: 0, likes: 0 }
    }
    authors[tweet.username].count++
    authors[tweet.username].likes += tweet.likeCount
  }

  const topAuthors = Object.entries(authors)
    .map(([username, stats]) => ({ username, ...stats }))
    .sort((a, b) => b.likes - a.likes)
    .slice(0, 5)

  return {
    query,
    total: tweets.length,
    uniqueAuthors: Object.keys(authors).length,
    totalLikes: tweets.reduce((sum, t) => sum + t.likeCount, 0),
    totalRetweets: tweets.reduce((sum, t) => sum + t.retweetCount, 0),
    topAuthors,
  }
}

function truncateText(text: string, maxLength: number = 280): string {
  // Remove newlines and collapse whitespace
  const clean = text.replace(/\n/g, ' ').replace(/\s+/g, ' ').trim()
  if (clean.length <= maxLength) return clean
  return clean.slice(0, maxLength - 3) + '...'
}

/**
 * Build a deduplicated link index across all tweets.
 * Returns a map of expanded URL → index number, and replaces t.co links
 * in each tweet's text with [N] references.
 */
function buildLinkIndex(tweets: TwitterTweet[]): { expandedTexts: Map<string, string>; linkIndex: string[] } {
  const urlToIndex = new Map<string, number>()
  const linkIndex: string[] = []
  const expandedTexts = new Map<string, string>()

  for (const tweet of tweets) {
    if (tweet.urls.length === 0) {
      expandedTexts.set(tweet.id, tweet.text)
      continue
    }

    let text = tweet.text
    for (const u of tweet.urls) {
      let idx = urlToIndex.get(u.expanded)
      if (idx === undefined) {
        idx = linkIndex.length
        urlToIndex.set(u.expanded, idx)
        linkIndex.push(u.expanded)
      }
      text = text.replaceAll(u.short, `[${idx}]`)
    }
    expandedTexts.set(tweet.id, text)
  }

  return { expandedTexts, linkIndex }
}

function formatLinkIndex(linkIndex: string[]): string {
  if (linkIndex.length === 0) return ''
  const lines = ['## Links', '']
  for (let i = 0; i < linkIndex.length; i++) {
    lines.push(`[${i}] ${linkIndex[i]}`)
  }
  return lines.join('\n')
}

export function formatTweetsText(tweets: TwitterTweet[], query: string): string {
  if (tweets.length === 0) {
    return '## Summary\nNo tweets found.'
  }

  const summary = computeSummary(tweets, query)
  const { expandedTexts, linkIndex } = buildLinkIndex(tweets)
  const lines: string[] = []

  // Summary
  lines.push('## Summary')
  lines.push(`Query: ${summary.query}`)
  lines.push(`Found: ${summary.total} tweets · ${summary.uniqueAuthors} authors`)
  lines.push(
    `Engagement: ${formatLikes(summary.totalLikes)} likes · ${formatLikes(summary.totalRetweets)} RTs`
  )

  if (summary.topAuthors.length > 0) {
    const topStr = summary.topAuthors
      .map((a) => `@${a.username} (${a.count}, ${formatLikes(a.likes)})`)
      .join(', ')
    lines.push(`Top: ${topStr}`)
  }

  lines.push('')
  lines.push('## Tweets')
  lines.push('')

  // Tweets with expanded links
  for (const tweet of tweets) {
    const text = expandedTexts.get(tweet.id) || tweet.text
    const followerTag = tweet.authorFollowersCount != null ? ` (${formatLikes(tweet.authorFollowersCount)} followers)` : ''
    lines.push(`@${tweet.username}${followerTag} · ${formatLikes(tweet.likeCount)} likes`)
    lines.push(truncateText(text))
    lines.push(`→ twitter.com/${tweet.username}/status/${tweet.id}`)
    lines.push('')
  }

  // Deduplicated link index
  const linkSection = formatLinkIndex(linkIndex)
  if (linkSection) {
    lines.push(linkSection)
  }

  return lines.join('\n')
}

export function formatTweetsJson(tweets: TwitterTweet[], query: string): string {
  const summary = computeSummary(tweets, query)
  return JSON.stringify({ summary, tweets }, null, 2)
}

export function formatUserText(user: TwitterUser): string {
  const lines: string[] = []
  const verified = user.isBlueVerified ? ' ✓' : ''
  lines.push(`@${user.username}${verified} · ${formatLikes(user.followersCount)} followers · ${formatLikes(user.followingCount)} following`)
  lines.push(`${user.displayName} · ${formatLikes(user.tweetCount)} tweets`)
  if (user.description) {
    lines.push('')
    lines.push(user.description)
  }
  lines.push('')
  lines.push(`→ twitter.com/${user.username}`)
  return lines.join('\n')
}

export function formatUserJson(user: TwitterUser): string {
  return JSON.stringify(user, null, 2)
}

export function formatUsersText(users: TwitterUser[]): string {
  if (users.length === 0) {
    return 'No users found.'
  }

  const lines: string[] = []
  lines.push(`Found ${users.length} users:`)
  lines.push('')

  for (const user of users) {
    const verified = user.isBlueVerified ? ' ✓' : ''
    lines.push(`@${user.username}${verified} · ${formatLikes(user.followersCount)} followers`)
    lines.push(`  ${user.displayName}`)
    if (user.description) {
      lines.push(`  ${truncateText(user.description, 100)}`)
    }
    lines.push('')
  }

  return lines.join('\n')
}

export function formatCommunitiesText(communities: TwitterCommunity[]): string {
  if (communities.length === 0) return 'No communities found.'
  const lines: string[] = [`Found ${communities.length} communities:`, '']
  for (const c of communities) {
    lines.push(`${c.name} · ${formatLikes(c.memberCount)} members`)
    if (c.description) lines.push(`  ${truncateText(c.description, 120)}`)
    lines.push(`  ID: ${c.id}`)
    lines.push('')
  }
  return lines.join('\n')
}

export function formatCommunitiesOutput(
  communities: TwitterCommunity[],
  format: OutputFormat
): string {
  return format === 'json' ? JSON.stringify(communities, null, 2) : formatCommunitiesText(communities)
}

export function formatOutput(
  data: TwitterTweet[] | TwitterUser | TwitterUser[],
  format: OutputFormat,
  query?: string
): string {
  if (Array.isArray(data)) {
    if (data.length === 0) {
      return format === 'json' ? '{"summary":null,"tweets":[]}' : 'No results found.'
    }

    // Check if it's users or tweets
    if ('followersCount' in data[0]) {
      // Users array
      return format === 'json'
        ? JSON.stringify(data, null, 2)
        : formatUsersText(data as TwitterUser[])
    }

    // Tweets array
    return format === 'json'
      ? formatTweetsJson(data as TwitterTweet[], query || '')
      : formatTweetsText(data as TwitterTweet[], query || '')
  }

  // Single user
  return format === 'json' ? formatUserJson(data) : formatUserText(data)
}

/**
 * Format a user profile with their recent tweets
 */
export function formatProfileOutput(
  user: TwitterUser,
  tweets: TwitterTweet[],
  format: OutputFormat
): string {
  if (format === 'json') {
    return JSON.stringify({ user, tweets }, null, 2)
  }

  const lines: string[] = []

  // User info
  const verified = user.isBlueVerified ? ' ✓' : ''
  lines.push(`@${user.username}${verified} · ${formatLikes(user.followersCount)} followers · ${formatLikes(user.followingCount)} following`)
  lines.push(`${user.displayName} · ${formatLikes(user.tweetCount)} tweets`)
  if (user.description) {
    lines.push('')
    lines.push(user.description)
  }
  lines.push('')
  lines.push(`→ twitter.com/${user.username}`)
  lines.push('')
  lines.push('---')
  lines.push('')
  lines.push(`## Recent Tweets (${tweets.length})`)
  lines.push('')

  const { expandedTexts, linkIndex } = buildLinkIndex(tweets)

  // Tweets
  for (const tweet of tweets) {
    const text = expandedTexts.get(tweet.id) || tweet.text
    lines.push(`${formatLikes(tweet.likeCount)} likes · ${truncateText(text, 200)}`)
    lines.push(`→ twitter.com/${tweet.username}/status/${tweet.id}`)
    lines.push('')
  }

  const linkSection = formatLinkIndex(linkIndex)
  if (linkSection) {
    lines.push(linkSection)
  }

  return lines.join('\n')
}
