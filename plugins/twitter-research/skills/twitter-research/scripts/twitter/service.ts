import { TwitterClient } from './client'
import { buildQuery } from './query-builder'
import { applyPreset } from './presets'
import { formatOutput, formatProfileOutput, formatCommunitiesOutput } from './formatter'
import type { SearchOptions, OutputFormat, TwitterUser, TwitterTweet, TwitterCommunity } from './types'

export interface SearchResult {
  query: string
  formatted: string
  tweets: TwitterTweet[]
  nextCursor: string | null
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
  format: OutputFormat = 'text',
  cursor?: string | null
): Promise<SearchResult> {
  const finalOptions = options.preset ? applyPreset(options, options.preset) : options
  const query = buildQuery(finalOptions)

  if (!query.trim()) {
    return { query: '', formatted: 'Error: No search query specified', tweets: [], nextCursor: null }
  }

  const client = new TwitterClient()
  const result = await client.search(query, finalOptions.limit ?? 20, cursor)
  return { query, formatted: formatOutput(result.items, format, query), tweets: result.items, nextCursor: result.nextCursor }
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
  format: OutputFormat = 'text',
  cursor?: string | null
): Promise<SearchResult> {
  const client = new TwitterClient()
  const query = buildQuery({
    from: username.replace(/^@/, ''),
    noRetweets: options.noRetweets ?? true,
    ...options,
  })
  const result = await client.search(query, options.limit ?? 20, cursor)
  return { query, formatted: formatOutput(result.items, format, query), tweets: result.items, nextCursor: result.nextCursor }
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

  const [user, result] = await Promise.all([
    client.getUser(cleanUsername),
    client.search(
      buildQuery({ from: cleanUsername, noRetweets: true, noReplies: true }),
      tweetLimit
    ),
  ])

  return { formatted: formatProfileOutput(user, result.items, format), user, tweets: result.items }
}

/**
 * Find Twitter users by name/keyword (uses People Search via /search-v3)
 */
export async function findUsers(
  name: string,
  format: OutputFormat = 'text'
): Promise<FindResult> {
  const client = new TwitterClient()
  const result = await client.searchPeople(name, 20)
  const users = result.items
    .sort((a, b) => b.followersCount - a.followersCount)
    .slice(0, 10)
  return { formatted: formatOutput(users, format), users }
}

export interface SearchPeopleResult {
  formatted: string
  users: TwitterUser[]
  nextCursor: string | null
}

/**
 * Search for Twitter users by name/keyword with optional filters
 */
export async function searchPeople(
  query: string,
  options: { maxFollowers?: number; bioContains?: string; limit?: number } = {},
  format: OutputFormat = 'text',
  cursor?: string | null
): Promise<SearchPeopleResult> {
  const client = new TwitterClient()
  const result = await client.searchPeople(query, options.limit ?? 20, cursor)
  let users = result.items

  if (options.maxFollowers != null) {
    users = users.filter(u => u.followersCount <= options.maxFollowers!)
  }
  if (options.bioContains) {
    const needle = options.bioContains.toLowerCase()
    users = users.filter(u => u.description.toLowerCase().includes(needle))
  }

  return { formatted: formatOutput(users, format), users, nextCursor: result.nextCursor }
}

/**
 * Get multiple user profiles by IDs in a single call
 */
export async function getUsersBatch(
  userIds: string[],
  format: OutputFormat = 'text'
): Promise<FindResult> {
  const client = new TwitterClient()
  const users = await client.getUsers(userIds)
  return { formatted: formatOutput(users, format), users }
}

/**
 * Get a user's media posts (images/videos)
 */
export async function getUserMedia(
  username: string,
  options: { limit?: number; cursor?: string | null } = {},
  format: OutputFormat = 'text'
): Promise<SearchResult> {
  const client = new TwitterClient()
  const user = await client.getUser(username.replace(/^@/, ''))
  const result = await client.getUserMedia(user.id, options.limit ?? 20, options.cursor)
  return {
    query: `media from @${user.username}`,
    formatted: formatOutput(result.items, format, `media from @${user.username}`),
    tweets: result.items,
    nextCursor: result.nextCursor,
  }
}

export interface UserListResult {
  formatted: string
  users: TwitterUser[]
  nextCursor: string | null
}

/**
 * Get a user's followers
 */
export async function getUserFollowers(
  username: string,
  options: { limit?: number; cursor?: string | null } = {},
  format: OutputFormat = 'text'
): Promise<UserListResult> {
  const client = new TwitterClient()
  const user = await client.getUser(username.replace(/^@/, ''))
  const result = await client.getFollowers(user.id, options.limit ?? 20, options.cursor)
  return { formatted: formatOutput(result.items, format), users: result.items, nextCursor: result.nextCursor }
}

/**
 * Get who a user follows
 */
export async function getUserFollowing(
  username: string,
  options: { limit?: number; cursor?: string | null } = {},
  format: OutputFormat = 'text'
): Promise<UserListResult> {
  const client = new TwitterClient()
  const user = await client.getUser(username.replace(/^@/, ''))
  const result = await client.getFollowing(user.id, options.limit ?? 20, options.cursor)
  return { formatted: formatOutput(result.items, format), users: result.items, nextCursor: result.nextCursor }
}

export interface CommunitiesResult {
  formatted: string
  communities: TwitterCommunity[]
  nextCursor: string | null
}

/**
 * Search for Twitter communities
 */
export async function searchCommunities(
  query: string,
  options: { limit?: number; cursor?: string | null } = {},
  format: OutputFormat = 'text'
): Promise<CommunitiesResult> {
  const client = new TwitterClient()
  const result = await client.searchCommunities(query, options.limit ?? 20, options.cursor)
  return { formatted: formatCommunitiesOutput(result.items, format), communities: result.items, nextCursor: result.nextCursor }
}

/**
 * Get members of a Twitter community
 */
export async function getCommunityMembers(
  communityId: string,
  options: { limit?: number; cursor?: string | null } = {},
  format: OutputFormat = 'text'
): Promise<UserListResult> {
  const client = new TwitterClient()
  const result = await client.getCommunityMembers(communityId, options.limit ?? 20, options.cursor)
  return { formatted: formatOutput(result.items, format), users: result.items, nextCursor: result.nextCursor }
}

export interface ListTimelineResult {
  formatted: string
  tweets: TwitterTweet[]
  nextCursor: string | null
}

/**
 * Get tweets from a Twitter list
 */
export async function getListTimeline(
  listId: string,
  options: { limit?: number; days?: number; cursor?: string | null } = {},
  format: OutputFormat = 'text'
): Promise<ListTimelineResult> {
  const client = new TwitterClient()
  const untilDate = options.days
    ? new Date(Date.now() - options.days * 24 * 60 * 60 * 1000)
    : undefined
  const result = await client.getListTimeline(listId, {
    limit: options.limit ?? 50,
    untilDate,
    cursor: options.cursor,
  })
  return { formatted: formatOutput(result.items, format), tweets: result.items, nextCursor: result.nextCursor }
}

export interface RepliesResult {
  formatted: string
  tweets: TwitterTweet[]
  nextCursor: string | null
}

/**
 * Get replies to a tweet
 */
export async function getReplies(
  tweetId: string,
  options: { limit?: number; rankingMode?: 'Recency' | 'Relevance' | 'Likes'; cursor?: string | null } = {},
  format: OutputFormat = 'text'
): Promise<RepliesResult> {
  const client = new TwitterClient()
  const result = await client.getComments(
    tweetId,
    options.limit ?? 20,
    options.rankingMode ?? 'Relevance',
    options.cursor
  )
  return { formatted: formatOutput(result.items, format), tweets: result.items, nextCursor: result.nextCursor }
}
