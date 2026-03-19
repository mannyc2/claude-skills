/**
 * Minimal TOON (Token-Oriented Object Notation) encoder for uniform arrays
 * of objects and simple key-value objects. Implements the subset of TOON spec
 * v3.0 needed for tweet/user data output.
 *
 * @see https://github.com/toon-format/spec
 */

type Primitive = string | number | boolean | null

/** Encode a value as TOON. Supports primitives, flat objects, and uniform arrays of flat objects. */
export function encodeToon(value: unknown): string {
  if (value === null || value === undefined) return 'null'
  if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
    return encodePrimitive(value)
  }
  if (Array.isArray(value)) {
    if (value.length === 0) return '[0]:'
    if (isUniformObjectArray(value)) {
      return encodeTabularArray(value)
    }
    // Fallback: array of primitives
    if (value.every(isPrimitive)) {
      return `[${value.length}]: ${value.map(v => encodePrimitive(v)).join(',')}`
    }
  }
  if (typeof value === 'object') {
    return encodeObject(value as Record<string, unknown>)
  }
  return String(value)
}

function encodePrimitive(value: Primitive): string {
  if (value === null) return 'null'
  if (typeof value === 'boolean') return String(value)
  if (typeof value === 'number') return String(value)
  return encodeString(value)
}

function encodeString(value: string): string {
  if (isSafeUnquoted(value)) return value
  return `"${escapeString(value)}"`
}

/** A string is safe unquoted if it's non-empty and contains no characters that need quoting. */
function isSafeUnquoted(value: string): boolean {
  if (value.length === 0) return false
  // Must not look like null/true/false
  if (value === 'null' || value === 'true' || value === 'false') return false
  // Must not start/end with whitespace
  if (value[0] === ' ' || value[value.length - 1] === ' ') return false
  // Must not contain structural characters
  for (const ch of value) {
    if (ch === ',' || ch === '"' || ch === '\n' || ch === '\r' || ch === '\t') return false
  }
  // Must not look like a number
  if (/^-?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$/.test(value)) return false
  return true
}

function escapeString(value: string): string {
  let result = ''
  for (const ch of value) {
    switch (ch) {
      case '"': result += '\\"'; break
      case '\\': result += '\\\\'; break
      case '\n': result += '\\n'; break
      case '\r': result += '\\r'; break
      case '\t': result += '\\t'; break
      default: result += ch
    }
  }
  return result
}

function isPrimitive(value: unknown): value is Primitive {
  return value === null || typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean'
}

/** Check if all items are objects with the same keys and all-primitive values. */
function isUniformObjectArray(arr: unknown[]): arr is Record<string, Primitive>[] {
  if (arr.length === 0) return false
  const first = arr[0]
  if (first === null || typeof first !== 'object' || Array.isArray(first)) return false
  const keys = Object.keys(first)
  if (keys.length === 0) return false
  for (const item of arr) {
    if (item === null || typeof item !== 'object' || Array.isArray(item)) return false
    const obj = item as Record<string, unknown>
    const itemKeys = Object.keys(obj)
    if (itemKeys.length !== keys.length) return false
    for (const key of keys) {
      if (!(key in obj) || !isPrimitive(obj[key])) return false
    }
  }
  return true
}

/** Encode a uniform array of objects as TOON tabular format. */
function encodeTabularArray(rows: Record<string, Primitive>[]): string {
  const fields = Object.keys(rows[0]!)
  const header = `[${rows.length}]{${fields.join(',')}}:`
  const lines = [header]
  for (const row of rows) {
    const values = fields.map(f => encodePrimitive(row[f]!))
    lines.push(`  ${values.join(',')}`)
  }
  return lines.join('\n')
}

/** Encode a flat object as TOON key-value pairs. */
function encodeObject(obj: Record<string, unknown>): string {
  const lines: string[] = []
  for (const [key, value] of Object.entries(obj)) {
    if (value === undefined) continue
    if (isPrimitive(value)) {
      lines.push(`${key}: ${encodePrimitive(value)}`)
    } else if (Array.isArray(value)) {
      if (value.length === 0) {
        lines.push(`${key}[0]:`)
      } else if (value.every(isPrimitive)) {
        lines.push(`${key}[${value.length}]: ${value.map(v => encodePrimitive(v as Primitive)).join(',')}`)
      } else if (isUniformObjectArray(value)) {
        lines.push(`${key}${encodeTabularArray(value)}`)
      } else {
        // Fallback for mixed arrays — inline JSON
        lines.push(`${key}: ${JSON.stringify(value)}`)
      }
    } else if (typeof value === 'object' && value !== null) {
      lines.push(`${key}:`)
      const subLines = encodeObject(value as Record<string, unknown>)
      for (const line of subLines.split('\n')) {
        lines.push(`  ${line}`)
      }
    }
  }
  return lines.join('\n')
}
