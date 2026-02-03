# setValue

Dynamically sets field value with optional validation and state updates.

## Signature

```typescript
setValue(name: string, value: unknown, config?: SetValueConfig): void
```

## Config Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `shouldValidate` | `boolean` | `false` | Trigger validation, update `errors`/`isValid`. |
| `shouldDirty` | `boolean` | `false` | Compute dirty state, update `isDirty`/`dirtyFields`. |
| `shouldTouch` | `boolean` | `false` | Mark as touched, update `touchedFields`. |

## Patterns

```typescript
// Basic
setValue("firstName", "Bill")

// With state updates
setValue("lastName", "Luo", { shouldValidate: true, shouldDirty: true })

// Nested: prefer leaf path (performant)
setValue("user.firstName", "value")  // ✅
setValue("user", { firstName: "value" })  // ❌ More re-renders

// Field array: update specific item
setValue("items.0.name", "New Name")
```

## Notes

- **Re-renders**: Only if error triggered/resolved or dirty/touched changes.
- **Non-existent Fields**: Will NOT create fields. Must be registered.
- **Field Arrays**: Use `useFieldArray.replace()` for entire array, `setValue` for cells.

---

# getValues

Reads form values without re-renders or subscriptions.

## Signatures

```typescript
getValues(): FieldValues                    // All
getValues(field: string): any               // Single
getValues(fields: string[]): any[]          // Multiple
getValues(undefined, { dirtyFields?, touchedFields? }): FieldValues  // Filtered
```

## Patterns

```typescript
const all = getValues()
const single = getValues("firstName")
const multiple = getValues(["firstName", "lastName"])
const dirtyOnly = getValues(undefined, { dirtyFields: true })
```

## Notes

- **Initial Render**: Returns `defaultValues` before render.
- **No Re-renders**: Unlike `watch()`, doesn't trigger re-renders.

---

# getFieldState

Gets individual field state synchronously.

## Signature

```typescript
getFieldState(name: string, formState?): {
  isDirty: boolean;
  isTouched: boolean;
  invalid: boolean;
  error?: FieldError;
}
```

## Patterns

```tsx
// With subscription (destructured formState)
const { getFieldState, formState: { isDirty } } = useForm()
const { isDirty: fieldDirty } = getFieldState("firstName")

// Without subscription (pass formState)
const { getFieldState, formState } = useForm()
const { isDirty } = getFieldState("firstName", formState)
```

## Notes

- **Subscription Required**: Must destructure relevant `formState` property OR pass entire `formState`.

---

# reset

Resets entire form state and values.

## Signature

```typescript
reset(values?: T | ((values: T) => T), options?: KeepStateOptions): void
```

## KeepStateOptions

| Option | Type | Description |
|--------|------|-------------|
| `keepErrors` | `boolean` | Retain all errors. |
| `keepDirty` | `boolean` | Retain `dirtyFields`. |
| `keepDirtyValues` | `boolean` | Only non-dirty fields update. |
| `keepValues` | `boolean` | Retain current values. |
| `keepDefaultValues` | `boolean` | Retain original `defaultValues`. |
| `keepIsSubmitted` | `boolean` | Retain `isSubmitted`. |
| `keepTouched` | `boolean` | Retain `touchedFields`. |
| `keepIsValid` | `boolean` | Retain `isValid`. |
| `keepSubmitCount` | `boolean` | Retain `submitCount`. |

## Patterns

```tsx
reset()                                    // To original defaults
reset({ firstName: "New" })                // New values + defaults
reset(undefined, { keepDirtyValues: true }) // Keep user edits

// After successful submit
useEffect(() => {
  if (isSubmitSuccessful) reset()
}, [isSubmitSuccessful, reset])
```

## Notes

- **Controlled Components**: Requires `defaultValues` in `useForm` for `Controller`.
- **Timing**: Avoid before mount; use in `useEffect` or event handlers.
- **keepDirtyValues**: Requires `dirtyFields` subscription.

---

# resetField

Resets individual field state and value.

## Signature

```typescript
resetField(name: string, options?: {
  keepError?: boolean;
  keepDirty?: boolean;
  keepTouched?: boolean;
  defaultValue?: unknown;
}): void
```

## Patterns

```typescript
resetField("firstName")                              // To original default
resetField("firstName", { keepError: true })         // Keep error
resetField("firstName", { defaultValue: "New" })     // New baseline
```

---

# trigger

Manually triggers validation.

## Signature

```typescript
trigger(name?: string | string[], options?: { shouldFocus?: boolean }): Promise<boolean>
```

## Patterns

```typescript
await trigger()                              // All fields
await trigger("firstName")                   // Single (optimized render)
await trigger(["firstName", "lastName"])     // Multiple
trigger("email", { shouldFocus: true })      // Focus on error
```

## Notes

- **Render**: Single string = isolated render. Array/undefined = full re-render.
- **Focus**: Requires registered `ref`.

---

# setFocus

Programmatically focuses a field.

## Signature

```typescript
setFocus(name: string, options?: { shouldSelect?: boolean }): void
```

## Patterns

```tsx
useEffect(() => {
  setFocus("firstName")
}, [setFocus])

setFocus("age", { shouldSelect: true })  // Focus and select content
```

## Notes

- **Ref Required**: Field must have registered ref.
- **After Reset**: Avoid immediately after `reset()` (refs torn down).

---

# unregister

Removes field value, reference, and validation.

## Signature

```typescript
unregister(name: string | string[], options?: UnregisterOptions): void
```

## Options

| Option | Type | Description |
|--------|------|-------------|
| `keepDirty` | `boolean` | Preserve `dirtyFields`. |
| `keepTouched` | `boolean` | Preserve `touchedFields`. |
| `keepIsValid` | `boolean` | Preserve `isValid`. |
| `keepError` | `boolean` | Preserve errors. |
| `keepValue` | `boolean` | Preserve value. |
| `keepDefaultValue` | `boolean` | Preserve default. |

## Patterns

```typescript
unregister("firstName")
unregister(["firstName", "lastName"])
unregister("firstName", { keepValue: true, keepError: true })
```

## Notes

- **Re-registration**: If component stays mounted, field re-registers on render. Unmount the input.
- **Schema Validation**: Does NOT update schema. Adjust Zod/Yup manually for dynamic fields.
