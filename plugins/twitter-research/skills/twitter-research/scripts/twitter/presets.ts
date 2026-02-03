import type { SearchOptions } from './types'

export const PRESETS: Record<string, Partial<SearchOptions>> = {
  indie: {
    minLikes: 100,
    noRetweets: true,
    lang: 'en',
  },
  viral: {
    minLikes: 1000,
    noRetweets: true,
  },
  recent: {
    days: 7,
    noRetweets: true,
  },
}

export function applyPreset(
  options: SearchOptions,
  presetName: string
): SearchOptions {
  const preset = PRESETS[presetName]
  if (!preset) {
    throw new Error(
      `Unknown preset: ${presetName}. Available: ${Object.keys(PRESETS).join(', ')}`
    )
  }
  // Filter out undefined values from options so they don't override preset
  const definedOptions: Partial<SearchOptions> = {}
  for (const [key, value] of Object.entries(options)) {
    if (value !== undefined) {
      definedOptions[key as keyof SearchOptions] = value as never
    }
  }
  // Preset values are defaults, explicit options override
  return { ...preset, ...definedOptions }
}
