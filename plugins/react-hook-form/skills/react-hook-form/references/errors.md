# handleSubmit

Validates form data before invoking callbacks.

## Signature

```typescript
handleSubmit(
  onValid: (data, event?) => Promise<void>,
  onInvalid?: (errors, event?) => void
) => (e?) => Promise<void>
```

## Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `onValid` | `(data, e?) => Promise<void>` | Yes | Called when validation passes. |
| `onInvalid` | `(errors, e?) => void` | No | Called when validation fails. |

## Pattern

```tsx
const { register, handleSubmit } = useForm<FormValues>()

const onSubmit = async (data) => {
  try {
    await saveAPI(data)
  } catch (e) {
    console.error(e)
  }
}

const onError = (errors) => console.log(errors)

return (
  <form onSubmit={handleSubmit(onSubmit, onError)}>
    <input {...register("firstName")} />
    <button type="submit">Submit</button>
  </form>
)
```

## Notes

- **Disabled Inputs**: Appear as `undefined` in data. Use `readOnly` to retain values.
- **Error Handling**: Does NOT catch errors in `onValid`. Use try/catch.
- **Async**: Both callbacks can be async.

---

# setError

Manually sets field or global errors.

## Signature

```typescript
setError(
  name: string,
  error: { type: string; message?: string; types?: Record<string, string> },
  config?: { shouldFocus?: boolean }
) => void
```

## Parameters

| Name | Type | Description |
|------|------|-------------|
| `name` | `string` | Field name or root key (e.g., `"root.serverError"`). |
| `error` | `ErrorOption` | Must include `type`. |
| `config.shouldFocus` | `boolean` | Focus input if `true` and ref available. |

## Patterns

### Field Error
```tsx
setError("username", { type: "manual", message: "Username taken" }, { shouldFocus: true })
```

### Multiple Errors (requires `criteriaMode: "all"`)
```tsx
setError("password", {
  types: {
    minLength: "Too short",
    uppercase: "Needs uppercase"
  }
})
```

### Server/Root Errors
```tsx
setError("root.serverSide", { type: "500", message: "Server unreachable" })

// Access
{errors.root?.serverSide && <p>{errors.root.serverSide.message}</p>}
```

## Notes

- **Persistence**: Errors on registered inputs clear on next validation pass. Unregistered persist until `clearErrors`.
- **Root Errors**: Don't persist across submissions.
- **isValid**: `setError` does NOT update `isValid` (derived from validation rules only).

---

# clearErrors

Manually clears errors.

## Signature

```typescript
clearErrors(name?: string | string[]): void
```

## Patterns

```tsx
clearErrors()                        // Clear all
clearErrors("firstName")             // Clear single
clearErrors(["firstName", "lastName"]) // Clear multiple
clearErrors("user")                  // Clear nested (user.first, user.last)
```

## Notes

- Does NOT affect validation rules.
- Does NOT update `isValid`.
- Clearing parent clears all child fields.
