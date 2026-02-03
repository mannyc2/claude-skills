import { TwitterClient } from '../client'
import { buildQuery } from '../query-builder'
import type { OutputFormat } from '../types'

export async function profileCommand(
  username: string,
  limit: number = 10,
  format: OutputFormat = 'text'
): Promise<string> {
  const cleanUsername = username.replace(/^@/, '')
  const client = new TwitterClient()

  // Fetch user profile and tweets in parallel
  const [user, tweets] = await Promise.all([
    client.getUser(cleanUsername),
    client.search(
      buildQuery({
        from: cleanUsername,
        noRetweets: true,
        noReplies: true,
      }),
      limit
    ),
  ])

  if (format === 'json') {
    return JSON.stringify({ user, tweets }, null, 2)
  }

  // Compact text output
  const lines: string[] = []

  // User info
  const followers = formatFollowers(user.followersCount)
  lines.push(`@${user.username} · ${followers} followers`)
  lines.push(user.displayName)
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

  // Tweets
  for (const tweet of tweets) {
    const likes = formatLikes(tweet.likeCount)
    lines.push(`${likes} likes · ${truncate(tweet.text, 200)}`)
    lines.push(`→ twitter.com/${tweet.username}/status/${tweet.id}`)
    lines.push('')
  }

  return lines.join('\n')
}

function formatFollowers(count: number): string {
  if (count >= 1000000) return `${(count / 1000000).toFixed(1)}M`
  if (count >= 1000) return `${(count / 1000).toFixed(1)}K`
  return count.toString()
}

function formatLikes(count: number): string {
  if (count >= 1000000) return `${(count / 1000000).toFixed(1)}M`
  if (count >= 1000) return `${(count / 1000).toFixed(1)}K`
  return count.toString()
}

function truncate(text: string, maxLength: number): string {
  const clean = text.replace(/\n/g, ' ').replace(/\s+/g, ' ').trim()
  if (clean.length <= maxLength) return clean
  return clean.slice(0, maxLength - 3) + '...'
}
