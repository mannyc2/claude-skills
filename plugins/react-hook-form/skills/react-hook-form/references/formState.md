# formState

Object containing form state (interaction, validation, submission). Wrapped in Proxy for render optimization.

## Properties

| Name | Type | Description |
|------|------|-------------|
| `isDirty` | `boolean` | Any input differs from `defaultValues`. Requires `defaultValues`. |
| `dirtyFields` | `object` | Fields modified by user. |
| `touchedFields` | `object` | Fields user has interacted with. |
| `defaultValues` | `object` | Current defaults from `useForm` or `reset`. |
| `isSubmitted` | `boolean` | Form submitted at least once. Resets via `reset()`. |
| `isSubmitSuccessful` | `boolean` | Submission completed without runtime error. |
| `isSubmitting` | `boolean` | Currently submitting. |
| `isLoading` | `boolean` | Async `defaultValues` loading. |
| `submitCount` | `number` | Times submitted. |
| `isValid` | `boolean` | No errors. `setError` does NOT affect this. |
| `isValidating` | `boolean` | During validation. |
| `validatingFields` | `object` | Fields in async validation. |
| `errors` | `FieldErrors` | Field errors object. |
| `disabled` | `boolean` | Form disabled via `useForm({ disabled: true })`. |
| `isReady` | `boolean` | Subscription ready. Useful for child init. |

## Subscription Pattern

**Must destructure to subscribe:**

```tsx
// ✅ Subscribes to errors, isDirty, isSubmitting
const { formState: { errors, isDirty, isSubmitting } } = useForm()

// ❌ Does NOT subscribe correctly
const { formState } = useForm()
return <button disabled={!formState.isDirty} />
```

## Patterns

### Basic
```tsx
const { register, formState: { errors, isDirty, isSubmitting } } = useForm()

return (
  <form>
    <input {...register("test")} />
    <button disabled={!isDirty || isSubmitting}>Submit</button>
    {errors.test && <span>Error</span>}
  </form>
)
```

### Async Default Values
```tsx
const { formState: { isLoading } } = useForm({
  defaultValues: async () => await fetch('/api')
})

if (isLoading) return <Spinner />
```

### useEffect Dependency
```tsx
const { formState } = useForm()

useEffect(() => {
  if (formState.errors.firstName) { /* ... */ }
}, [formState]) // ✅ Pass entire object, NOT formState.errors
```

## Notes

- **Proxy**: Only re-renders when subscribed property changes.
- **isDirty**: Requires `defaultValues`. Does not deep compare `File` or Class instances.
- **isValid**: Derived from validation, NOT affected by `setError`.

---

# useFormState

Subscribes to form state, isolating re-renders to the component level.

## Signature

```typescript
useFormState(props?: { control?, name?, disabled?, exact? }): FormState
```

## Options

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `control` | `Control` | | From `useForm`. Optional with `FormProvider`. |
| `name` | `string` \| `string[]` | | Specific field(s) to subscribe to. |
| `disabled` | `boolean` | `false` | Disable subscription. |
| `exact` | `boolean` | `false` | Exact name matching. |

## Returns

Same properties as `formState` above.

## Patterns

### Subscribe in Child Component
```tsx
function ChildInput({ control }: { control: Control }) {
  const { dirtyFields } = useFormState({ control, name: "firstName" })
  return dirtyFields.firstName ? <span>Modified</span> : null
}
```

### Global Form State
```tsx
function GlobalStatus() {
  const { isSubmitting, isValid } = useFormState()
  return <button disabled={isSubmitting || !isValid}>Submit</button>
}
```

## Notes

- **Proxy**: Must destructure to subscribe.
- **File Inputs**: `isDirty` doesn't work with `File`/`FileList` (browser limitation).
