import { TwitterClient } from '../client'
import { formatOutput } from '../formatter'
import type { OutputFormat } from '../types'

export async function repliesCommand(
  tweetId: string,
  options: { limit?: number; rankingMode?: 'Recency' | 'Relevance' | 'Likes' } = {},
  format: OutputFormat = 'text'
): Promise<string> {
  const client = new TwitterClient()
  const tweets = await client.getComments(
    tweetId,
    options.limit || 20,
    options.rankingMode || 'Relevance'
  )

  return formatOutput(tweets, format, `replies:${tweetId}`)
}
