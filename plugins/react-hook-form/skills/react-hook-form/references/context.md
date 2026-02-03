# FormProvider / useFormContext

Access `useForm` methods in nested components via React Context.

## FormProvider

```tsx
import { useForm, FormProvider } from "react-hook-form"

function App() {
  const methods = useForm()
  
  return (
    <FormProvider {...methods}>
      <form onSubmit={methods.handleSubmit(console.log)}>
        <NestedInput />
      </form>
    </FormProvider>
  )
}
```

## useFormContext

```tsx
import { useFormContext } from "react-hook-form"

function NestedInput() {
  const { register } = useFormContext()
  return <input {...register("nested")} />
}
```

## Returns

Same as `useForm()`: `register`, `formState`, `watch`, `handleSubmit`, `reset`, `setValue`, `getValues`, `control`, etc.

## Notes

- **Provider Required**: `useFormContext` only works inside `<FormProvider />`.
- **Dependencies**: Don't add entire `methods` to `useEffect` deps; destructure specific methods.
- **Types**: Pass generic for strict typing: `useFormContext<FormType>()`.

---

# createFormControl

Creates standalone form state without React Context or component rendering.

## Signature

```typescript
createFormControl<T>(props?: UseFormProps<T>): {
  control: Control;
  formControl: FormControl;
  subscribe: Function;
  ...methods: UseFormReturn;
}
```

## Pattern

```tsx
import { createFormControl, useForm, useFormState } from 'react-hook-form'

// Initialize outside or inside component
const { formControl, control, handleSubmit, register } = createFormControl({
  mode: 'onChange',
  defaultValues: { firstName: 'Bill' }
})

function App() {
  // Bind to React lifecycle
  useForm({ formControl })
  
  return (
    <form onSubmit={handleSubmit(console.log)}>
      <input {...register('firstName')} />
      <ChildComponent control={control} />
    </form>
  )
}

function ChildComponent({ control }) {
  const { isDirty } = useFormState({ control })
  return <p>Dirty: {isDirty}</p>
}
```

## Notes

- **Mutually Exclusive**: Don't use with `<FormProvider />`.
- **Version**: Available from v7.55.0.
- **Binding**: Must pass `formControl` to `useForm` to bind lifecycle.
- **Performance**: `subscribe` monitors state without React re-renders.
