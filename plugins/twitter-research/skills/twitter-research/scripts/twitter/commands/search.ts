import { TwitterClient } from '../client'
import { buildQuery } from '../query-builder'
import { applyPreset } from '../presets'
import { formatOutput } from '../formatter'
import type { SearchOptions, OutputFormat } from '../types'

export async function searchCommand(
  options: SearchOptions,
  format: OutputFormat = 'text'
): Promise<string> {
  let finalOptions = options
  if (options.preset) {
    finalOptions = applyPreset(options, options.preset)
  }

  const query = buildQuery(finalOptions)

  if (!query.trim()) {
    return 'Error: No search query specified'
  }

  const client = new TwitterClient()
  const tweets = await client.search(query, finalOptions.limit || 20)

  return formatOutput(tweets, format, query)
}
