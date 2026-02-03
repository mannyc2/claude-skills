# watch

Subscribes to input changes; triggers re-render at hook level.

## Signatures

```typescript
watch(): Record<string, unknown>              // All values
watch(name: string, defaultValue?): T         // Single field
watch(names: string[], defaultValue?): T[]    // Multiple fields
```

## Patterns

```tsx
const { register, watch } = useForm({
  defaultValues: { name: "Alice", showAge: false }
})

// Single field
const showAge = watch("showAge", false)

// Multiple fields
const [name, age] = watch(["name", "age"])

// All values
const allValues = watch()

// Conditional rendering
return (
  <form>
    <input type="checkbox" {...register("showAge")} />
    {showAge && <input type="number" {...register("age")} />}
  </form>
)
```

## Notes

- **Initial Render**: Returns `undefined` before `register` unless `defaultValue` provided.
- **Precedence**: Inline `defaultValue` overrides `useForm` defaults.
- **Performance**: Re-renders at root. For isolated re-renders, use `useWatch`.
- **Effects**: Avoid in `useEffect` deps; use custom hook for comparison.

---

# useWatch

Subscribes to input changes, isolating re-renders to component level.

## Options

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `name` | `string` \| `string[]` | | Field(s) to watch. `undefined` = all. |
| `control` | `Control` | | From `useForm`. Optional with `FormProvider`. |
| `defaultValue` | `unknown` | | Value before initial render/SSR. |
| `disabled` | `boolean` | `false` | Pause subscription. |
| `exact` | `boolean` | `false` | Exact name matching. |
| `compute` | `(data) => any` | | Transform/select specific data. |

## Returns

| `name` | Return Type |
|--------|-------------|
| `string` | Single value |
| `string[]` | Array of values |
| `undefined` | All form values |

## Patterns

```tsx
function Watcher({ control }) {
  // Single
  const firstName = useWatch({ control, name: "firstName" })
  
  // Multiple
  const [first, last] = useWatch({ control, name: ["firstName", "lastName"] })
  
  // All
  const allData = useWatch({ control })
  
  // With compute
  const computed = useWatch({
    control,
    compute: (data) => data.items?.length || 0
  })
  
  return <div>{firstName}</div>
}
```

## Notes

- **Isolation**: Only re-renders the component calling it, not root.
- **Order**: `setValue` before `useWatch` subscribes is ignored.
- **Initial**: First render returns `defaultValue` or `useForm` defaults.

---

# subscribe

Subscribes to formState changes without triggering re-renders.

## Signature

```typescript
subscribe(options: {
  callback: (state) => void;
  name?: string | string[];
  exact?: boolean;
  formState?: { values?, isDirty?, errors?, ... };
}): () => void  // unsubscribe
```

## Options

| Name | Type | Description |
|------|------|-------------|
| `callback` | `Function` | **Required**. Handler for state updates. |
| `formState` | `object` | Whitelist properties: `{ values: true, isDirty: true }`. |
| `name` | `string` \| `string[]` | Specific field(s) to monitor. |
| `exact` | `boolean` | Exact name matching. |

## Pattern

```tsx
const { subscribe } = useForm()

useEffect(() => {
  const unsubscribe = subscribe({
    formState: { values: true, isDirty: true },
    callback: ({ values, isDirty }) => {
      console.log(values, isDirty)
    },
  })
  return () => unsubscribe()
}, [subscribe])
```

### Specific Fields

```tsx
subscribe({
  name: ['firstName', 'lastName'],
  formState: { values: true },
  callback: ({ values }) => { /* ... */ }
})
```

## Notes

- **Cleanup**: Returns unsubscribe function. Must call for cleanup.
- **No State Updates**: Do not call `setValue`, `reset` inside callback.
- **Use Case**: Logging, analytics, external sync without renders.
