# useFieldArray

Manages dynamic form lists with append, prepend, remove, and reorder operations.

## Props

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `name` | `string` | **Required** | Field array path (e.g., `"users"`, `"cart.items"`). |
| `control` | `Control` | | From `useForm`. Optional with `FormProvider`. |
| `rules` | `object` | | Validation: `required`, `minLength`, `maxLength`, `validate`. Errors in `errors.name.root`. |
| `shouldUnregister` | `boolean` | | Unregister on unmount. |

## Returns

| Name | Type | Description |
|------|------|-------------|
| `fields` | `(T & { id: string })[]` | Iterable fields. **Must use `field.id` as React key**. |
| `append` | `(data, options?) => void` | Add to end. Data must be complete object. |
| `prepend` | `(data, options?) => void` | Add to start. |
| `insert` | `(index, data, options?) => void` | Insert at index. |
| `swap` | `(from, to) => void` | Swap two items. |
| `move` | `(from, to) => void` | Move item to new index. |
| `replace` | `(data[]) => void` | Replace entire array. |
| `remove` | `(index?) => void` | Remove at index. No index = remove all. |
| `update` | `(index, data) => void` | Update at index. **Causes remount**. Use `setValue` to preserve state. |

## Pattern

```tsx
import { useForm, useFieldArray } from "react-hook-form"

type FormValues = {
  items: { name: string; qty: number }[]
}

function ItemList() {
  const { control, register, formState: { errors } } = useForm<FormValues>({
    defaultValues: { items: [{ name: "", qty: 1 }] }
  })
  
  const { fields, append, remove } = useFieldArray({
    control,
    name: "items",
    rules: { minLength: 1 }
  })

  return (
    <form>
      {fields.map((field, index) => (
        // ✅ ALWAYS use field.id as key, NEVER index
        <div key={field.id}>
          <input {...register(`items.${index}.name` as const)} />
          <input type="number" {...register(`items.${index}.qty` as const, { valueAsNumber: true })} />
          <button type="button" onClick={() => remove(index)}>Delete</button>
        </div>
      ))}
      
      {/* Root validation error */}
      {errors.items?.root && <p>{errors.items.root.message}</p>}
      
      {/* Must provide complete object */}
      <button type="button" onClick={() => append({ name: "", qty: 1 })}>
        Add Item
      </button>
    </form>
  )
}
```

## Watching Field Array Values

```tsx
const { fields } = useFieldArray({ control, name: "items" })
const watchedItems = watch("items")

// Merge for real-time values
const controlledFields = fields.map((field, i) => ({
  ...field,
  ...watchedItems[i]
}))
```

## Notes

- **Keys**: Always use `field.id`, never `index`. Using index breaks sorting/removal.
- **Async Actions**: `append`, `remove`, etc. are async. Don't chain synchronously.
- **Data Shape**: Flat arrays (`['a', 'b']`) NOT supported. Must be objects (`[{ value: 'a' }]`).
- **Complete Data**: `append`/`insert`/`update` require complete objects, not partials.
- **Update vs setValue**: `update()` remounts. Use `setValue('items.0.name', val)` to preserve focus/state.
- **TypeScript**: Use `as const` for template literal paths.
- **Uniqueness**: Don't use multiple `useFieldArray` with same `name`.
