# register

Registers an input to the form, applying validation rules and event listeners.

## Signature

```typescript
register(name: string, options?: RegisterOptions): { onChange, onBlur, ref, name }
```

## Options

| Name | Type | Default | Description |
|------|------|---------|-------------|
| **Validation** |
| `required` | `boolean` \| `string` | | Mandatory input. String = error message. |
| `maxLength` | `number` \| `{ value, message }` | | Maximum string length. |
| `minLength` | `number` \| `{ value, message }` | | Minimum string length. |
| `max` | `number` \| `{ value, message }` | | Maximum numerical value. |
| `min` | `number` \| `{ value, message }` | | Minimum numerical value. |
| `pattern` | `RegExp` \| `{ value, message }` | | Regex pattern. Avoid `/g` flag. |
| `validate` | `Function` \| `Record<string, Function>` | | Custom validator(s). Return `true`, error string, or `false`. |
| **Transformation** |
| `valueAsNumber` | `boolean` | `false` | Parse as Number (or NaN). Runs before validation. |
| `valueAsDate` | `boolean` | `false` | Parse as Date. Runs before validation. |
| `setValueAs` | `(value) => any` | | Custom transform. Ignored if `valueAs*` used. |
| **Lifecycle** |
| `disabled` | `boolean` | `false` | Disabled; value becomes `undefined`; validation skipped. |
| `deps` | `string` \| `string[]` | | Trigger validation for dependent fields. |
| `shouldUnregister` | `boolean` | | Remove value on unmount. Avoid with `useFieldArray`. |
| `onChange` | `(e) => void` | | Additional handler on change. |
| `onBlur` | `(e) => void` | | Additional handler on blur. |

## Returns

| Name | Type | Description |
|------|------|-------------|
| `name` | `string` | Field name |
| `onChange` | `ChangeHandler` | Bind to input's `onChange` |
| `onBlur` | `ChangeHandler` | Bind to input's `onBlur` |
| `ref` | `React.Ref` | Attach to element for focus-on-error |

## Patterns

### Basic
```tsx
<input {...register("firstName", { required: true })} />
<select {...register("category")}>...</select>
```

### Validation & Transform
```tsx
<input
  type="number"
  {...register("age", {
    valueAsNumber: true,
    min: { value: 18, message: "Must be 18+" },
    max: 99
  })}
/>
```

### Custom Async Validation
```tsx
<input {...register("username", {
  validate: {
    checkExists: async (v) => await api.checkUser(v) || "Taken",
    matchEmail: (v, formValues) => v === formValues.email || "Mismatch"
  }
})} />
```

### Nested & Array Fields
```tsx
register("user.details.firstName")  // dot syntax only
register("items.0.name")            // bracket syntax NOT supported
```

### Custom Components (innerRef)
```tsx
const { ref, name, onBlur, onChange } = register("customField")

<CustomInput
  name={name}
  onBlur={onBlur}
  onChange={onChange}
  inputRef={ref}
/>
```

## Notes

- **Syntax**: Use dot `test.0.prop` for arrays/nesting. Bracket `test[0]` NOT supported.
- **Disabled**: Returns `undefined` in values, skips validation.
- **Unique Names**: Must be unique, cannot start with numbers.
- **Reserved**: Avoid names `ref` or `_f`.
- **Unmounting**: Values persist unless `shouldUnregister: true`.
