# useController

Hook for controlled components, exposing field props and state.

## Props

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `name` | `FieldPath` | **Required** | Field path/name. |
| `control` | `Control` | | From `useForm`. Optional with `FormProvider`. |
| `rules` | `RegisterOptions` | | Validation rules. |
| `shouldUnregister` | `boolean` | `false` | Remove on unmount. Avoid with `useFieldArray`. |
| `disabled` | `boolean` | `false` | Disable input, exclude from submission. |
| `defaultValue` | `unknown` | | Initial value. Cannot be `undefined`. Prefer `useForm` defaults. |

## Returns

### `field`

| Name | Type | Description |
|------|------|-------------|
| `onChange` | `(value) => void` | Update value. Assign to component. |
| `onBlur` | `() => void` | Mark touched. Assign to component. |
| `value` | `unknown` | Current value. |
| `name` | `string` | Input name. |
| `ref` | `React.Ref` | For focus-on-error. Assign to component. |
| `disabled` | `boolean` | Disabled state. |

### `fieldState`

| Name | Type | Description |
|------|------|-------------|
| `invalid` | `boolean` | Fails validation. |
| `isTouched` | `boolean` | Has been interacted with. |
| `isDirty` | `boolean` | Differs from default. |
| `error` | `FieldError` | Error for this field. |

### `formState`

Same as `useForm` formState.

## Pattern

```tsx
import { useController } from "react-hook-form"
import { TextField } from "@material-ui/core"

function ControlledInput({ control, name }) {
  const {
    field,
    fieldState: { invalid, error }
  } = useController({
    name,
    control,
    rules: { required: true },
    defaultValue: "",
  })

  return (
    <TextField
      {...field}
      inputRef={field.ref}
      error={invalid}
      helperText={error?.message}
    />
  )
}
```

## Notes

- **No Double Register**: Don't use `...field` AND `...register()` on same input.
- **Refs**: Always assign `field.ref` for focus-on-error.
- **Undefined**: `defaultValue` cannot be `undefined`.
- **Multiple Hooks**: Rename destructured props: `const { field: inputField } = useController(...)`.

---

# Controller

Component wrapper for `useController`.

```tsx
<Controller
  name="category"
  control={control}
  defaultValue=""
  rules={{ required: "Required" }}
  render={({ field, fieldState }) => (
    <Select
      value={field.value}
      onValueChange={field.onChange}
      onBlur={field.onBlur}
    />
  )}
/>
```

---

# control

Object from `useForm` for connecting controlled components.

## Usage

```tsx
const { control } = useForm()

<Controller name="firstName" control={control} render={...} />
```

## Notes

- **Internal Only**: Do not access properties inside `control` directly.
- **Required For**: `Controller`, `useController`, `useFieldArray`, `useWatch` (unless using `FormProvider`).
