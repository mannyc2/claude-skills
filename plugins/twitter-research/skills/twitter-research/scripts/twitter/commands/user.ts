import { TwitterClient } from '../client'
import { formatOutput } from '../formatter'
import type { OutputFormat } from '../types'

export async function userCommand(
  username: string,
  format: OutputFormat = 'text'
): Promise<string> {
  const client = new TwitterClient()
  const user = await client.getUser(username.replace(/^@/, ''))

  return formatOutput(user, format)
}
