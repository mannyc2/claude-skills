import { searchCommand } from './commands/search'
import { userCommand } from './commands/user'
import { findCommand } from './commands/find'
import { profileCommand } from './commands/profile'
import { repliesCommand } from './commands/replies'
import {
  searchArgsSchema,
  userArgsSchema,
  findArgsSchema,
  profileArgsSchema,
  repliesArgsSchema,
  argsToSearchOptions,
} from './types'

// Re-export for programmatic use
export * as service from './service'
export { TwitterClient } from './client'
export { buildQuery } from './query-builder'
export { formatOutput, formatProfileOutput } from './formatter'
export type { SearchOptions, OutputFormat, TwitterUser, TwitterTweet } from './types'

const HELP = `
Twitter Research CLI

Usage:
  bun run cli research tw <command> [options]

Commands:
  search <keywords> [limit]   Search tweets
  user <username>             Get user profile
  profile <username> [limit]  User profile + recent tweets
  find <name>                 Find users by name
  replies <tweetId> [limit]   Get replies to a tweet

Search Options:
  --from USER         Tweets from user
  --to USER           Replies to user
  --mention USER      Tweets mentioning user
  --hashtag TAG       Include hashtag (repeatable)
  --exclude WORD      Exclude word (repeatable)
  --or KEYWORD        OR keyword (repeatable)
  --min-likes N       Minimum likes
  --min-retweets N    Minimum retweets
  --min-replies N     Minimum replies
  --since YYYY-MM-DD  After date
  --until YYYY-MM-DD  Before date
  --days N            Last N days
  --with-retweets     Include retweets (excluded by default)
  --no-replies        Exclude replies
  --only-replies      Only replies
  --has-media         Has media
  --has-images        Has images
  --has-videos        Has videos
  --has-links         Has links
  --url DOMAIN        Links to domain
  --lang CODE         Language code
  --limit N           Max results (default: 20)
  --preset NAME       Use preset (indie, viral, recent)
  --format FORMAT     Output format (text, json)

Examples:
  bun run cli research tw search "indie hacker" 50 --min-likes 100
  bun run cli research tw search "MRR" --or "revenue" --preset indie
  bun run cli research tw profile levelsio 30
  bun run cli research tw find "marc lou"
`

/**
 * Parse CLI args, handling repeatable flags and positional args
 */
function parseArgs(argv: string[]): {
  command: string
  positional: string
  positionalLimit: number | undefined
  raw: Record<string, string | string[]>
} {
  const command = argv[0] || ''
  let positional = ''
  let positionalLimit: number | undefined
  const raw: Record<string, string | string[]> = {}

  let i = 1
  while (i < argv.length) {
    const arg = argv[i]

    if (arg.startsWith('--')) {
      const key = arg.slice(2)
      const nextArg = argv[i + 1]

      // Boolean flags (no value needed)
      const booleanFlags = [
        'with-retweets',
        'no-replies',
        'only-replies',
        'has-media',
        'has-images',
        'has-videos',
        'has-links',
        'help',
      ]

      if (booleanFlags.includes(key)) {
        raw[key] = 'true'
        i += 1
      } else if (nextArg && !nextArg.startsWith('--')) {
        // Repeatable flags
        const repeatableFlags = ['hashtag', 'exclude', 'or']
        if (repeatableFlags.includes(key)) {
          const existing = raw[key]
          if (Array.isArray(existing)) {
            existing.push(nextArg)
          } else if (typeof existing === 'string') {
            raw[key] = [existing, nextArg]
          } else {
            raw[key] = nextArg
          }
        } else {
          raw[key] = nextArg
        }
        i += 2
      } else {
        raw[key] = 'true'
        i += 1
      }
    } else if (!positional) {
      // First positional: keywords/username
      positional = arg
      i += 1
    } else if (positionalLimit === undefined && /^\d+$/.test(arg)) {
      // Second positional (if numeric): limit
      positionalLimit = parseInt(arg, 10)
      i += 1
    } else {
      i += 1
    }
  }

  return { command, positional, positionalLimit, raw }
}

export async function main(argv = process.argv.slice(2)) {

  if (argv.length === 0 || argv[0] === '--help' || argv[0] === '-h') {
    console.log(HELP)
    process.exit(0)
  }

  const { command, positional, positionalLimit, raw } = parseArgs(argv)

  // Apply positional limit if no --limit flag was provided
  if (positionalLimit !== undefined && !raw.limit) {
    raw.limit = String(positionalLimit)
  }

  try {
    switch (command) {
      case 'search': {
        const result = searchArgsSchema.safeParse({ ...raw, keywords: positional })
        if (!result.success) {
          const errors = result.error.issues
            .map((i) => `  --${i.path.join('.')}: ${i.message}`)
            .join('\n')
          throw new Error(`Invalid arguments:\n${errors}`)
        }
        const options = argsToSearchOptions(result.data)
        const output = await searchCommand(options, result.data.format)
        console.log(output)
        break
      }

      case 'user': {
        const result = userArgsSchema.safeParse({ ...raw, username: positional })
        if (!result.success) {
          const errors = result.error.issues
            .map((i) => `  ${i.path.join('.')}: ${i.message}`)
            .join('\n')
          throw new Error(`Invalid arguments:\n${errors}`)
        }
        const output = await userCommand(result.data.username, result.data.format)
        console.log(output)
        break
      }

      case 'find': {
        const result = findArgsSchema.safeParse({ ...raw, name: positional })
        if (!result.success) {
          const errors = result.error.issues
            .map((i) => `  ${i.path.join('.')}: ${i.message}`)
            .join('\n')
          throw new Error(`Invalid arguments:\n${errors}`)
        }
        const output = await findCommand(result.data.name, result.data.format)
        console.log(output)
        break
      }

      case 'profile': {
        const result = profileArgsSchema.safeParse({ ...raw, username: positional })
        if (!result.success) {
          const errors = result.error.issues
            .map((i) => `  ${i.path.join('.')}: ${i.message}`)
            .join('\n')
          throw new Error(`Invalid arguments:\n${errors}`)
        }
        const output = await profileCommand(
          result.data.username,
          result.data.limit || 10,
          result.data.format
        )
        console.log(output)
        break
      }

      case 'replies': {
        const result = repliesArgsSchema.safeParse({ ...raw, tweetId: positional })
        if (!result.success) {
          const errors = result.error.issues
            .map((i) => `  ${i.path.join('.')}: ${i.message}`)
            .join('\n')
          throw new Error(`Invalid arguments:\n${errors}`)
        }
        const output = await repliesCommand(
          result.data.tweetId,
          { limit: result.data.limit, rankingMode: result.data.rankingMode },
          result.data.format
        )
        console.log(output)
        break
      }

      default:
        console.error(`Unknown command: ${command}`)
        console.log(HELP)
        process.exit(1)
    }
  } catch (error) {
    console.error(`Error: ${error instanceof Error ? error.message : String(error)}`)
    process.exit(1)
  }
}

if (import.meta.main) {
  void main()
}
