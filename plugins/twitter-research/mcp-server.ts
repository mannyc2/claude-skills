import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js'
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'
import { z } from 'zod'
import {
  search,
  getUser,
  getUserTweets,
  getProfile,
  findUsers,
  getListTimeline,
  getReplies,
} from './skills/twitter-research/scripts/twitter/service'
import type { SearchOptions } from './skills/twitter-research/scripts/twitter/types'

const server = new McpServer({
  name: 'twitter-research',
  version: '1.0.0',
})

server.tool(
  'search_tweets',
  'Search Twitter/X for tweets matching keywords with optional filters for engagement, date, media, and users. Returns formatted results optimized for analysis.',
  {
    keywords: z.string().optional().describe('Search keywords'),
    from: z.string().optional().describe('Tweets from this user'),
    to: z.string().optional().describe('Replies to this user'),
    mention: z.string().optional().describe('Tweets mentioning this user'),
    hashtags: z.array(z.string()).optional().describe('Include hashtags'),
    exclude: z.array(z.string()).optional().describe('Exclude words'),
    or: z.array(z.string()).optional().describe('OR keywords'),
    minLikes: z.number().optional().describe('Minimum likes'),
    minRetweets: z.number().optional().describe('Minimum retweets'),
    minReplies: z.number().optional().describe('Minimum replies'),
    since: z.string().optional().describe('After date (YYYY-MM-DD)'),
    until: z.string().optional().describe('Before date (YYYY-MM-DD)'),
    days: z.number().optional().describe('Tweets from last N days'),
    noRetweets: z.boolean().optional().describe('Exclude retweets (default: true)'),
    noReplies: z.boolean().optional().describe('Exclude replies'),
    onlyReplies: z.boolean().optional().describe('Only show replies'),
    hasMedia: z.boolean().optional().describe('Has any media'),
    hasImages: z.boolean().optional().describe('Has images'),
    hasVideos: z.boolean().optional().describe('Has videos'),
    hasLinks: z.boolean().optional().describe('Has links'),
    url: z.string().optional().describe('Links to specific domain'),
    lang: z.string().optional().describe('Language code (en, es, ja, etc.)'),
    limit: z.number().optional().describe('Max results (default: 20)'),
    preset: z.string().optional().describe('Use preset: indie, viral, recent'),
  },
  async (params) => {
    const options: SearchOptions = {
      ...params,
      noRetweets: params.noRetweets ?? true,
    }
    const result = await search(options)
    return {
      content: [
        { type: 'text' as const, text: result.formatted },
        { type: 'text' as const, text: `\n\n<structured_data>\n${JSON.stringify(result.tweets, null, 2)}\n</structured_data>` },
      ],
    }
  }
)

server.tool(
  'get_user',
  'Get a Twitter/X user profile by username. Returns display name, follower count, bio, and ID.',
  {
    username: z.string().describe('Twitter username (with or without @)'),
  },
  async ({ username }) => {
    const result = await getUser(username)
    return {
      content: [
        { type: 'text' as const, text: result.formatted },
        { type: 'text' as const, text: `\n\n<structured_data>\n${JSON.stringify(result.user, null, 2)}\n</structured_data>` },
      ],
    }
  }
)

server.tool(
  'get_user_tweets',
  "Get a user's recent tweets with optional filters. Excludes retweets by default.",
  {
    username: z.string().describe('Twitter username'),
    limit: z.number().optional().describe('Max results (default: 20)'),
    noRetweets: z.boolean().optional().describe('Exclude retweets (default: true)'),
    noReplies: z.boolean().optional().describe('Exclude replies'),
    onlyReplies: z.boolean().optional().describe('Only show replies'),
    since: z.string().optional().describe('After date (YYYY-MM-DD)'),
    until: z.string().optional().describe('Before date (YYYY-MM-DD)'),
    days: z.number().optional().describe('Tweets from last N days'),
  },
  async ({ username, ...options }) => {
    const result = await getUserTweets(username, options)
    return {
      content: [
        { type: 'text' as const, text: result.formatted },
        { type: 'text' as const, text: `\n\n<structured_data>\n${JSON.stringify(result.tweets, null, 2)}\n</structured_data>` },
      ],
    }
  }
)

server.tool(
  'get_profile',
  "Get a user's full profile with their recent original tweets. Combines user info and timeline in one call.",
  {
    username: z.string().describe('Twitter username'),
    limit: z.number().optional().describe('Number of recent tweets (default: 10)'),
  },
  async ({ username, limit }) => {
    const result = await getProfile(username, limit ?? 10)
    return {
      content: [
        { type: 'text' as const, text: result.formatted },
        {
          type: 'text' as const,
          text: `\n\n<structured_data>\n${JSON.stringify({ user: result.user, tweets: result.tweets }, null, 2)}\n</structured_data>`,
        },
      ],
    }
  }
)

server.tool(
  'find_users',
  'Find Twitter/X users by name or keyword. Searches tweets and resolves unique authors, sorted by follower count.',
  {
    name: z.string().describe('Name or keyword to search for'),
  },
  async ({ name }) => {
    const result = await findUsers(name)
    return {
      content: [
        { type: 'text' as const, text: result.formatted },
        { type: 'text' as const, text: `\n\n<structured_data>\n${JSON.stringify(result.users, null, 2)}\n</structured_data>` },
      ],
    }
  }
)

server.tool(
  'get_replies',
  'Get replies/comments on a specific tweet by tweet ID.',
  {
    tweetId: z.string().describe('Tweet ID to get replies for'),
    limit: z.number().optional().describe('Max replies (default: 20)'),
    rankingMode: z.enum(['Recency', 'Relevance', 'Likes']).optional().describe('Sort order (default: Relevance)'),
  },
  async ({ tweetId, limit, rankingMode }) => {
    const result = await getReplies(tweetId, { limit, rankingMode })
    return {
      content: [
        { type: 'text' as const, text: result.formatted },
        { type: 'text' as const, text: `\n\n<structured_data>\n${JSON.stringify(result.tweets, null, 2)}\n</structured_data>` },
      ],
    }
  }
)

server.tool(
  'get_list_timeline',
  'Get recent tweets from a Twitter/X list by list ID.',
  {
    listId: z.string().describe('Twitter list ID'),
    limit: z.number().optional().describe('Max tweets (default: 50)'),
    days: z.number().optional().describe('Only tweets from last N days'),
  },
  async ({ listId, limit, days }) => {
    const result = await getListTimeline(listId, { limit, days })
    return {
      content: [
        { type: 'text' as const, text: result.formatted },
        { type: 'text' as const, text: `\n\n<structured_data>\n${JSON.stringify(result.tweets, null, 2)}\n</structured_data>` },
      ],
    }
  }
)

async function main() {
  const transport = new StdioServerTransport()
  await server.connect(transport)
}

main().catch((error) => {
  console.error('Server error:', error)
  process.exit(1)
})
