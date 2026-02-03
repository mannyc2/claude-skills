import { TwitterClient } from '../client'
import { formatOutput } from '../formatter'
import type { TwitterUser, OutputFormat } from '../types'

export async function findCommand(
  name: string,
  format: OutputFormat = 'text'
): Promise<string> {
  const client = new TwitterClient()

  // Search for tweets mentioning the name to find users
  const query = `"${name}"`
  const tweets = await client.search(query, 50)

  // Extract unique users and fetch their profiles
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

  // Sort by followers
  const users = Array.from(usersMap.values())
    .sort((a, b) => b.followersCount - a.followersCount)
    .slice(0, 10)

  return formatOutput(users, format)
}
