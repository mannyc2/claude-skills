# useForm

React hook for managing form state and validation.

## Options

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `mode` | `'onSubmit'` \| `'onBlur'` \| `'onChange'` \| `'onTouched'` \| `'all'` | `'onSubmit'` | Validation trigger strategy. `onChange` impacts performance. |
| `reValidateMode` | `'onChange'` \| `'onBlur'` \| `'onSubmit'` | `'onChange'` | Re-validation strategy after submission errors. |
| `defaultValues` | `FieldValues` \| `() => Promise<FieldValues>` | | Initial values. Cached. Avoid `undefined` or prototype methods. |
| `values` | `FieldValues` | | Reactive values that update form (overwrites `defaultValues`). |
| `errors` | `FieldErrors` | | Server errors. Keep reference stable to avoid infinite re-renders. |
| `resetOptions` | `KeepStateOptions` | | Config for internal reset when `values`/`defaultValues` update. |
| `criteriaMode` | `'firstError'` \| `'all'` | `'firstError'` | Gather first error per field or all. |
| `shouldFocusError` | `boolean` | `true` | Focus first error field on submit. Requires registered ref. |
| `delayError` | `number` (ms) | `0` | Delay error appearance. Removed instantly on fix. |
| `shouldUnregister` | `boolean` | `false` | Remove input value when unmounted. |
| `shouldUseNativeValidation` | `boolean` | `false` | Enable browser native validation (`:valid` selectors). |
| `disabled` | `boolean` | `false` | Disable entire form and inputs. |
| `resolver` | `Resolver` | | External validation (Zod, Yup, Joi). |
| `context` | `object` | | Mutable context passed to resolver. |

## Returns

```typescript
{
  register,       // Register inputs
  unregister,     // Unregister inputs
  formState,      // State: isDirty, isSubmitting, errors, etc.
  watch,          // Subscribe to changes
  handleSubmit,   // Submit handler
  reset,          // Reset form
  resetField,     // Reset specific field
  setError,       // Manually set error
  clearErrors,    // Manually clear errors
  setValue,       // Manually set value
  setFocus,       // Manually focus
  getValues,      // Get values
  getFieldState,  // Get field state
  trigger,        // Trigger validation
  control,        // Control object for Controller
}
```

## Patterns

### Basic Setup
```tsx
const { register, handleSubmit, formState: { errors } } = useForm({
  defaultValues: { firstName: '', lastName: '' }
})
```

### Async Default Values
```tsx
useForm({
  defaultValues: async () => await fetch('/api/user').then(r => r.json())
})
```

### External Validation (Zod)
```tsx
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"

const schema = z.object({
  email: z.string().email(),
  age: z.number().min(18),
})

useForm({
  resolver: zodResolver(schema),
})
```

### Reactive Values (External State)
```tsx
useForm({
  values: externalData,
  resetOptions: {
    keepDirtyValues: true,
    keepErrors: true,
  },
})
```

## Notes

- **Performance**: `mode: 'onChange'` triggers re-renders on every keystroke. Prefer `onSubmit` or `onBlur`.
- **Dependencies**: Do not add entire `useForm` return to `useEffect` deps; destructure specific methods.
- **Resolver Errors**: Must return hierarchically: `{ participants: [null, { name: err }] }`, not flat keys.
- **Server Errors**: Keep `errors` prop reference-stable to avoid infinite re-renders.
