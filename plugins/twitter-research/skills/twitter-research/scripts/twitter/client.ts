import type { TwitterUser, TwitterTweet } from './types'

const RAPIDAPI_HOST = 'twitter241.p.rapidapi.com'
const RAPIDAPI_URL = `https://${RAPIDAPI_HOST}`

export class TwitterClient {
  private apiKey: string

  constructor(apiKey?: string) {
    this.apiKey = apiKey || process.env.RAPIDAPI_KEY_241 || ''
    if (!this.apiKey) {
      throw new Error('RAPIDAPI_KEY_241 environment variable required')
    }
  }

  private async fetch(endpoint: string, params?: Record<string, string>): Promise<unknown> {
    let url = `${RAPIDAPI_URL}${endpoint}`
    if (params) {
      url += '?' + new URLSearchParams(params).toString()
    }

    const maxRetries = 5
    let lastError: Error | null = null

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      if (attempt > 0) {
        const delay = Math.min(1000 * Math.pow(2, attempt - 1), 16000)
        await new Promise((r) => setTimeout(r, delay))
      }

      try {
        const response = await global.fetch(url, {
          headers: {
            'X-RapidAPI-Key': this.apiKey,
            'X-RapidAPI-Host': RAPIDAPI_HOST,
          },
        })

        if (response.status === 429) {
          lastError = new Error('Rate limited')
          continue
        }

        if (!response.ok) {
          throw new Error(`API error: ${response.status} ${response.statusText}`)
        }

        return await response.json()
      } catch (e) {
        if (e instanceof Error && e.message === 'Rate limited') {
          lastError = e
          continue
        }
        throw e
      }
    }

    throw lastError || new Error('Max retries exceeded')
  }

  async getUser(username: string): Promise<TwitterUser> {
    const data = (await this.fetch('/user', { username })) as {
      result?: {
        data?: {
          user?: {
            result?: {
              rest_id: string
              core: { screen_name: string; name: string }
              legacy: { followers_count: number; description?: string }
            }
          }
        }
      }
    }

    const user = data?.result?.data?.user?.result
    if (!user) {
      throw new Error(`User not found: @${username}`)
    }

    return {
      id: user.rest_id,
      username: user.core.screen_name,
      displayName: user.core.name,
      followersCount: user.legacy.followers_count,
      description: user.legacy.description || '',
    }
  }

  async getListTimeline(
    listId: string,
    options: { limit?: number; untilDate?: Date } = {}
  ): Promise<TwitterTweet[]> {
    const { limit = 50, untilDate } = options
    const allTweets: TwitterTweet[] = []
    let cursor: string | null = null
    let hitDateCutoff = false

    while (allTweets.length < limit && !hitDateCutoff) {
      const params: Record<string, string> = { listId }
      if (cursor) params.cursor = cursor

      const data = (await this.fetch('/list-timeline', params)) as {
        cursor?: { bottom?: string }
        result?: {
          timeline?: {
            instructions?: Array<{
              type?: string
              entries?: Array<{
                entryId?: string
                content?: {
                  value?: string
                  __typename?: string
                  itemContent?: {
                    tweet_results?: {
                      result?: {
                        legacy?: Record<string, unknown>
                        core?: { user_results?: { result?: Record<string, unknown> } }
                        views?: { count?: string }
                      }
                    }
                  }
                }
              }>
            }>
          }
        }
      }

      let nextCursor: string | null = null

      if (data.cursor?.bottom) {
        nextCursor = data.cursor.bottom
      }

      const instructions = data.result?.timeline?.instructions || []
      let foundTweets = 0

      for (const instruction of instructions) {
        if (instruction.type !== 'TimelineAddEntries') continue

        for (const entry of instruction.entries || []) {
          const entryId = entry.entryId || ''

          if (entryId.startsWith('cursor-bottom')) {
            nextCursor = entry.content?.value || null
            continue
          }

          const tweet = this.extractTweet(entry.content)
          if (tweet) {
            // Check date cutoff
            if (untilDate) {
              const tweetDate = new Date(tweet.createdAt)
              if (tweetDate < untilDate) {
                hitDateCutoff = true
                break
              }
            }
            allTweets.push(tweet)
            foundTweets++
          }
        }
      }

      if (foundTweets === 0 || !nextCursor || hitDateCutoff) break
      cursor = nextCursor

      // Rate limiting between pages
      if (allTweets.length < limit && !hitDateCutoff) {
        await new Promise((r) => setTimeout(r, 1000))
      }
    }

    return untilDate ? allTweets : allTweets.slice(0, limit)
  }

  async search(query: string, limit: number = 20): Promise<TwitterTweet[]> {
    const allTweets: TwitterTweet[] = []
    let cursor: string | null = null

    while (allTweets.length < limit) {
      const params: Record<string, string> = { query, type: 'Latest' }
      if (cursor) params.cursor = cursor

      const data = (await this.fetch('/search', params)) as {
        cursor?: { bottom?: string }
        result?: {
          timeline?: {
            instructions?: Array<{
              type?: string
              entries?: Array<{
                entryId?: string
                content?: {
                  value?: string
                  __typename?: string
                  itemContent?: {
                    tweet_results?: {
                      result?: {
                        legacy?: Record<string, unknown>
                        core?: { user_results?: { result?: Record<string, unknown> } }
                        views?: { count?: string }
                      }
                    }
                  }
                }
              }>
            }>
          }
        }
      }

      let nextCursor: string | null = null

      if (data.cursor?.bottom) {
        nextCursor = data.cursor.bottom
      }

      const instructions = data.result?.timeline?.instructions || []
      let foundTweets = 0

      for (const instruction of instructions) {
        if (instruction.type !== 'TimelineAddEntries') continue

        for (const entry of instruction.entries || []) {
          const entryId = entry.entryId || ''

          if (entryId.startsWith('cursor-bottom')) {
            nextCursor = entry.content?.value || null
            continue
          }

          const tweet = this.extractTweet(entry.content)
          if (tweet) {
            allTweets.push(tweet)
            foundTweets++
          }
        }
      }

      if (foundTweets === 0 || !nextCursor) break
      cursor = nextCursor

      // Rate limiting between pages
      if (allTweets.length < limit) {
        await new Promise((r) => setTimeout(r, 1000))
      }
    }

    return allTweets.slice(0, limit)
  }

  async getComments(
    tweetId: string,
    limit: number = 20,
    rankingMode: 'Recency' | 'Relevance' | 'Likes' = 'Relevance'
  ): Promise<TwitterTweet[]> {
    const allTweets: TwitterTweet[] = []
    let cursor: string | null = null

    while (allTweets.length < limit) {
      const params: Record<string, string> = {
        pid: tweetId,
        count: String(Math.min(limit - allTweets.length, 20)),
        rankingMode,
      }
      if (cursor) params.cursor = cursor

      const data = (await this.fetch('/comments-v2', params)) as {
        cursor?: { bottom?: string }
        result?: {
          instructions?: Array<{
            type?: string
            entries?: Array<{
              entryId?: string
              content?: {
                __typename?: string
                items?: Array<{
                  item?: {
                    itemContent?: {
                      tweet_results?: {
                        result?: {
                          rest_id?: string
                          legacy?: {
                            id_str: string
                            full_text: string
                            created_at: string
                            favorite_count?: number
                            retweet_count?: number
                            reply_count?: number
                            is_quote_status?: boolean
                          }
                          core?: {
                            user_results?: {
                              result?: {
                                core?: { screen_name?: string; name?: string }
                                legacy?: { screen_name?: string; name?: string }
                              }
                            }
                          }
                          views?: { count?: string }
                        }
                      }
                    }
                  }
                }>
              }
            }>
          }>
        }
      }

      let nextCursor: string | null = null

      if (data.cursor?.bottom) {
        nextCursor = data.cursor.bottom
      }

      const instructions = data.result?.instructions || []
      let foundTweets = 0

      for (const instruction of instructions) {
        if (instruction.type !== 'TimelineAddEntries') continue

        for (const entry of instruction.entries || []) {
          // Skip non-conversation entries (parent tweet, cursors)
          if (!entry.entryId?.startsWith('conversationthread-')) continue

          // Extract replies from conversation thread items
          const items = entry.content?.items || []
          for (const item of items) {
            const tweet = item.item?.itemContent?.tweet_results?.result
            if (!tweet?.legacy) continue

            const legacy = tweet.legacy
            const userResult = tweet.core?.user_results?.result
            const userCore = userResult?.core || {}
            const userLegacy = userResult?.legacy || {}

            let viewCount: number | null = null
            if (tweet.views?.count) {
              viewCount = parseInt(tweet.views.count, 10) || null
            }

            allTweets.push({
              id: legacy.id_str,
              text: legacy.full_text,
              createdAt: legacy.created_at,
              username: userCore.screen_name || userLegacy.screen_name || 'unknown',
              displayName: userCore.name || userLegacy.name || 'Unknown',
              likeCount: legacy.favorite_count || 0,
              retweetCount: legacy.retweet_count || 0,
              replyCount: legacy.reply_count || 0,
              viewCount,
              isRetweet: false,
              isReply: true,
              isQuote: legacy.is_quote_status || false,
              mediaUrls: [],
            })
            foundTweets++
          }
        }
      }

      if (foundTweets === 0 || !nextCursor) break
      cursor = nextCursor

      // Rate limiting between pages
      if (allTweets.length < limit) {
        await new Promise((r) => setTimeout(r, 1000))
      }
    }

    return allTweets.slice(0, limit)
  }

  private extractTweet(content: unknown): TwitterTweet | null {
    try {
      const c = content as {
        __typename?: string
        itemContent?: {
          tweet_results?: {
            result?: {
              legacy?: {
                id_str: string
                full_text: string
                created_at: string
                favorite_count?: number
                retweet_count?: number
                reply_count?: number
                in_reply_to_status_id_str?: string
                is_quote_status?: boolean
                extended_entities?: { media?: Array<{ type?: string; media_url_https?: string }> }
                entities?: { media?: Array<{ type?: string; media_url_https?: string }> }
              }
              core?: {
                user_results?: {
                  result?: {
                    core?: { screen_name?: string; name?: string }
                    legacy?: { screen_name?: string; name?: string }
                  }
                }
              }
              views?: { count?: string }
            }
          }
        }
      }

      if (c?.__typename !== 'TimelineTimelineItem') return null

      const tweetResult = c.itemContent?.tweet_results?.result
      if (!tweetResult?.legacy) return null

      const legacy = tweetResult.legacy
      const userResult = tweetResult.core?.user_results?.result
      const userCore = userResult?.core || {}
      const userLegacy = userResult?.legacy || {}

      let viewCount: number | null = null
      if (tweetResult.views?.count) {
        viewCount = parseInt(tweetResult.views.count, 10) || null
      }

      const mediaUrls: string[] = []
      const entities = legacy.extended_entities || legacy.entities || {}
      for (const media of entities.media || []) {
        if (media.type === 'photo' && media.media_url_https) {
          mediaUrls.push(media.media_url_https)
        }
      }

      return {
        id: legacy.id_str,
        text: legacy.full_text,
        createdAt: legacy.created_at,
        username: userCore.screen_name || userLegacy.screen_name || 'unknown',
        displayName: userCore.name || userLegacy.name || 'Unknown',
        likeCount: legacy.favorite_count || 0,
        retweetCount: legacy.retweet_count || 0,
        replyCount: legacy.reply_count || 0,
        viewCount,
        isRetweet: legacy.full_text.startsWith('RT @'),
        isReply: Boolean(legacy.in_reply_to_status_id_str),
        isQuote: legacy.is_quote_status || false,
        mediaUrls,
      }
    } catch {
      return null
    }
  }
}
