import { z } from 'zod'

// Response types

export interface TwitterUser {
  id: string
  username: string
  displayName: string
  followersCount: number
  description: string
}

export interface TwitterTweet {
  id: string
  text: string
  createdAt: string
  username: string
  displayName: string
  likeCount: number
  retweetCount: number
  replyCount: number
  viewCount: number | null
  isRetweet: boolean
  isReply: boolean
  isQuote: boolean
  mediaUrls: string[]
}

export interface SearchSummary {
  query: string
  total: number
  uniqueAuthors: number
  totalLikes: number
  totalRetweets: number
  topAuthors: Array<{ username: string; count: number; likes: number }>
}

// Zod schemas for CLI args

const optionalInt = z
  .string()
  .optional()
  .transform((val, ctx) => {
    if (val === undefined) return undefined
    const parsed = parseInt(val, 10)
    if (isNaN(parsed)) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'Expected number' })
      return z.NEVER
    }
    return parsed
  })

const stringToBoolean = z
  .string()
  .optional()
  .transform((val) => val === 'true')

const stringArray = z
  .union([z.string(), z.array(z.string())])
  .optional()
  .transform((val) => {
    if (val === undefined) return undefined
    return Array.isArray(val) ? val : [val]
  })

export const searchArgsSchema = z.object({
  keywords: z.string().optional(),
  from: z.string().optional(),
  to: z.string().optional(),
  mention: z.string().optional(),
  hashtag: stringArray,
  exclude: stringArray,
  or: stringArray,
  'min-likes': optionalInt,
  'min-retweets': optionalInt,
  'min-replies': optionalInt,
  since: z.string().optional(),
  until: z.string().optional(),
  days: optionalInt,
  'with-retweets': stringToBoolean, // default excludes retweets
  'no-replies': stringToBoolean,
  'only-replies': stringToBoolean,
  'has-media': stringToBoolean,
  'has-images': stringToBoolean,
  'has-videos': stringToBoolean,
  'has-links': stringToBoolean,
  url: z.string().optional(),
  lang: z.string().optional(),
  limit: optionalInt,
  preset: z.string().optional(),
  format: z.enum(['text', 'json']).optional().default('text'),
})

export type SearchArgs = z.infer<typeof searchArgsSchema>

export const userArgsSchema = z.object({
  username: z.string({ required_error: 'Username required' }),
  format: z.enum(['text', 'json']).optional().default('text'),
})

export type UserArgs = z.infer<typeof userArgsSchema>

export const tweetsArgsSchema = z.object({
  username: z.string({ required_error: 'Username required' }),
  'with-retweets': stringToBoolean, // default excludes retweets
  'no-replies': stringToBoolean,
  'only-replies': stringToBoolean,
  since: z.string().optional(),
  until: z.string().optional(),
  days: optionalInt,
  limit: optionalInt,
  format: z.enum(['text', 'json']).optional().default('text'),
})

export type TweetsArgs = z.infer<typeof tweetsArgsSchema>

export const findArgsSchema = z.object({
  name: z.string({ required_error: 'Name/keyword required' }),
  format: z.enum(['text', 'json']).optional().default('text'),
})

export type FindArgs = z.infer<typeof findArgsSchema>

export const profileArgsSchema = z.object({
  username: z.string({ required_error: 'Username required' }),
  limit: optionalInt,
  format: z.enum(['text', 'json']).optional().default('text'),
})

export type ProfileArgs = z.infer<typeof profileArgsSchema>

export const repliesArgsSchema = z.object({
  tweetId: z.string({ required_error: 'Tweet ID required' }),
  limit: optionalInt,
  rankingMode: z.enum(['Recency', 'Relevance', 'Likes']).optional().default('Relevance'),
  format: z.enum(['text', 'json']).optional().default('text'),
})

export type RepliesArgs = z.infer<typeof repliesArgsSchema>

// Normalized options for internal use

export interface SearchOptions {
  keywords?: string
  from?: string
  to?: string
  mention?: string
  hashtags?: string[]
  exclude?: string[]
  or?: string[]
  minLikes?: number
  minRetweets?: number
  minReplies?: number
  since?: string
  until?: string
  days?: number
  noRetweets?: boolean
  noReplies?: boolean
  onlyReplies?: boolean
  hasMedia?: boolean
  hasImages?: boolean
  hasVideos?: boolean
  hasLinks?: boolean
  url?: string
  lang?: string
  limit?: number
  preset?: string
}

export type OutputFormat = 'text' | 'json'

// Convert CLI args to internal options

export function argsToSearchOptions(args: SearchArgs): SearchOptions {
  return {
    keywords: args.keywords,
    from: args.from,
    to: args.to,
    mention: args.mention,
    hashtags: args.hashtag,
    exclude: args.exclude,
    or: args.or,
    minLikes: args['min-likes'],
    minRetweets: args['min-retweets'],
    minReplies: args['min-replies'],
    since: args.since,
    until: args.until,
    days: args.days,
    noRetweets: !args['with-retweets'], // default true (exclude retweets)
    noReplies: args['no-replies'],
    onlyReplies: args['only-replies'],
    hasMedia: args['has-media'],
    hasImages: args['has-images'],
    hasVideos: args['has-videos'],
    hasLinks: args['has-links'],
    url: args.url,
    lang: args.lang,
    limit: args.limit,
    preset: args.preset,
  }
}

export function argsToTweetsOptions(
  args: TweetsArgs
): Omit<SearchOptions, 'keywords' | 'from'> {
  return {
    noRetweets: !args['with-retweets'], // default true (exclude retweets)
    noReplies: args['no-replies'],
    onlyReplies: args['only-replies'],
    since: args.since,
    until: args.until,
    days: args.days,
    limit: args.limit,
  }
}
