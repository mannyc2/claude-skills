import { TwitterClient } from './client'
import { buildQuery } from './query-builder'
import { applyPreset } from './presets'
import { formatOutput, formatProfileOutput } from './formatter'
import type { SearchOptions, OutputFormat, TwitterUser, TwitterTweet } from './types'

export interface SearchResult {
  query: string
  formatted: string
  tweets: TwitterTweet[]
}

export interface ProfileResult {
  formatted: string
  user: TwitterUser
  tweets: TwitterTweet[]
}

export interface FindResult {
  formatted: string
  users: TwitterUser[]
}

/**
 * Search tweets with optional filters and presets
 */
export async function search(
  options: SearchOptions,
  format: OutputFormat = 'text'
): Promise<SearchResult> {
  const finalOptions = options.preset ? applyPreset(options, options.preset) : options
  const query = buildQuery(finalOptions)

  if (!query.trim()) {
    return { query: '', formatted: 'Error: No search query specified', tweets: [] }
  }

  const client = new TwitterClient()
  const tweets = await client.search(query, finalOptions.limit ?? 20)
  return { query, formatted: formatOutput(tweets, format, query), tweets }
}

/**
 * Get user profile by username
 */
export async function getUser(
  username: string,
  format: OutputFormat = 'text'
): Promise<{ formatted: string; user: TwitterUser }> {
  const client = new TwitterClient()
  const user = await client.getUser(username.replace(/^@/, ''))
  return { formatted: formatOutput(user, format), user }
}

/**
 * Get a user's recent tweets
 */
export async function getUserTweets(
  username: string,
  options: Partial<SearchOptions> = {},
  format: OutputFormat = 'text'
): Promise<SearchResult> {
  const client = new TwitterClient()
  const query = buildQuery({
    from: username.replace(/^@/, ''),
    noRetweets: options.noRetweets ?? true,
    ...options,
  })
  const tweets = await client.search(query, options.limit ?? 20)
  return { query, formatted: formatOutput(tweets, format, query), tweets }
}

/**
 * Get user profile with recent tweets combined
 */
export async function getProfile(
  username: string,
  tweetLimit = 10,
  format: OutputFormat = 'text'
): Promise<ProfileResult> {
  const client = new TwitterClient()
  const cleanUsername = username.replace(/^@/, '')

  const [user, tweets] = await Promise.all([
    client.getUser(cleanUsername),
    client.search(
      buildQuery({ from: cleanUsername, noRetweets: true, noReplies: true }),
      tweetLimit
    ),
  ])

  return { formatted: formatProfileOutput(user, tweets, format), user, tweets }
}

/**
 * Find Twitter users by name/keyword
 */
export async function findUsers(
  name: string,
  format: OutputFormat = 'text'
): Promise<FindResult> {
  const client = new TwitterClient()
  const query = `"${name}"`
  const tweets = await client.search(query, 50)

  const usersMap = new Map<string, TwitterUser>()
  for (const tweet of tweets) {
    if (!usersMap.has(tweet.username)) {
      try {
        const user = await client.getUser(tweet.username)
        usersMap.set(tweet.username, user)
      } catch {
        // Skip if we can't fetch the user
      }
    }
  }

  const users = Array.from(usersMap.values())
    .sort((a, b) => b.followersCount - a.followersCount)
    .slice(0, 10)

  return { formatted: formatOutput(users, format), users }
}

export interface ListTimelineResult {
  formatted: string
  tweets: TwitterTweet[]
}

/**
 * Get tweets from a Twitter list
 */
export async function getListTimeline(
  listId: string,
  options: { limit?: number; days?: number } = {},
  format: OutputFormat = 'text'
): Promise<ListTimelineResult> {
  const client = new TwitterClient()
  const untilDate = options.days
    ? new Date(Date.now() - options.days * 24 * 60 * 60 * 1000)
    : undefined
  const tweets = await client.getListTimeline(listId, {
    limit: options.limit ?? 50,
    untilDate,
  })
  return { formatted: formatOutput(tweets, format), tweets }
}

export interface RepliesResult {
  formatted: string
  tweets: TwitterTweet[]
}

/**
 * Get replies to a tweet
 */
export async function getReplies(
  tweetId: string,
  options: { limit?: number; rankingMode?: 'Recency' | 'Relevance' | 'Likes' } = {},
  format: OutputFormat = 'text'
): Promise<RepliesResult> {
  const client = new TwitterClient()
  const tweets = await client.getComments(
    tweetId,
    options.limit ?? 20,
    options.rankingMode ?? 'Relevance'
  )
  return { formatted: formatOutput(tweets, format), tweets }
}
