import type { SearchOptions } from './types'

export function buildQuery(options: SearchOptions): string {
  const parts: string[] = []

  // Keywords with OR support
  if (options.keywords || options.or?.length) {
    const terms: string[] = []
    if (options.keywords) terms.push(options.keywords)
    if (options.or?.length) terms.push(...options.or)

    if (terms.length > 1) {
      parts.push(`(${terms.join(' OR ')})`)
    } else if (terms.length === 1) {
      parts.push(terms[0])
    }
  }

  // User filters
  if (options.from) parts.push(`from:${options.from}`)
  if (options.to) parts.push(`to:${options.to}`)
  if (options.mention) parts.push(`@${options.mention}`)

  // Hashtags
  if (options.hashtags?.length) {
    for (const tag of options.hashtags) {
      parts.push(`#${tag.replace(/^#/, '')}`)
    }
  }

  // Exclusions
  if (options.exclude?.length) {
    for (const word of options.exclude) {
      parts.push(`-${word}`)
    }
  }

  // Engagement filters
  if (options.minLikes && options.minLikes > 0) {
    parts.push(`min_faves:${options.minLikes}`)
  }
  if (options.minRetweets && options.minRetweets > 0) {
    parts.push(`min_retweets:${options.minRetweets}`)
  }
  if (options.minReplies && options.minReplies > 0) {
    parts.push(`min_replies:${options.minReplies}`)
  }

  // Date filters
  if (options.since) parts.push(`since:${options.since}`)
  if (options.until) parts.push(`until:${options.until}`)
  if (options.days && options.days > 0) {
    const since = new Date()
    since.setDate(since.getDate() - options.days)
    parts.push(`since:${since.toISOString().split('T')[0]}`)
  }

  // Type filters
  if (options.noRetweets) parts.push('-filter:retweets')
  if (options.noReplies) parts.push('-filter:replies')
  if (options.onlyReplies) parts.push('filter:replies')

  // Media filters
  if (options.hasMedia) parts.push('filter:media')
  if (options.hasImages) parts.push('filter:images')
  if (options.hasVideos) parts.push('filter:videos')
  if (options.hasLinks) parts.push('filter:links')
  if (options.url) parts.push(`url:${options.url}`)

  // Language
  if (options.lang) parts.push(`lang:${options.lang}`)

  return parts.join(' ')
}
