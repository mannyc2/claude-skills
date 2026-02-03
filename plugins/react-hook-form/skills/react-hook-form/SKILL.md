---
name: react-hook-form
description: Build accessible forms using React Hook Form with shadcn/ui Field components. Use when creating forms with validation, error handling, field arrays, or complex layouts. Covers useForm, register, Controller, useFieldArray, validation with Zod/Yup, and integration with Field, FieldLabel, FieldError, FieldSet components.
---

# React Hook Form + shadcn Field Integration

## Quick Decision Tree

| Need | Approach | Reference |
|------|----------|-----------|
| Setup form | `useForm` with Zod resolver | [useForm.md](references/useForm.md) |
| Native inputs (`<input>`, `<textarea>`) | `register()` | [register.md](references/register.md) |
| Controlled components (Select, Switch, Slider) | `Controller` / `useController` | [controller.md](references/controller.md) |
| Dynamic lists (add/remove items) | `useFieldArray` | [field-array.md](references/field-array.md) |
| Show validation errors | `FieldError` + `formState.errors` | [errors.md](references/errors.md) |
| Watch field values | `watch` (root) or `useWatch` (isolated) | [watching.md](references/watching.md) |
| Programmatic updates | `setValue`, `reset`, `trigger` | [methods.md](references/methods.md) |
| Share form across components | `FormProvider` + `useFormContext` | [context.md](references/context.md) |
| Layout fields | `Field`, `FieldSet`, `FieldGroup` | [field-components.md](references/field-components.md) |

## Core Integration Pattern

```tsx
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Field, FieldLabel, FieldError, FieldGroup } from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

const schema = z.object({
  email: z.string().email("Invalid email"),
  name: z.string().min(2, "Name required"),
})

type FormData = z.infer<typeof schema>

export function MyForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  return (
    <form onSubmit={handleSubmit((data) => console.log(data))}>
      <FieldGroup>
        <Field data-invalid={!!errors.email}>
          <FieldLabel htmlFor="email">Email</FieldLabel>
          <Input id="email" {...register("email")} aria-invalid={!!errors.email} />
          <FieldError>{errors.email?.message}</FieldError>
        </Field>

        <Field data-invalid={!!errors.name}>
          <FieldLabel htmlFor="name">Name</FieldLabel>
          <Input id="name" {...register("name")} aria-invalid={!!errors.name} />
          <FieldError>{errors.name?.message}</FieldError>
        </Field>

        <Button type="submit">Submit</Button>
      </FieldGroup>
    </form>
  )
}
```

## Controller Pattern (Select, Switch, Checkbox)

Use `Controller` for components that don't expose a native ref:

```tsx
import { Controller, useForm } from "react-hook-form"
import { Field, FieldLabel, FieldError, FieldContent, FieldDescription } from "@/components/ui/field"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"

export function ControlledForm() {
  const { control, handleSubmit, formState: { errors } } = useForm({
    defaultValues: { department: "", notifications: false }
  })

  return (
    <form onSubmit={handleSubmit(console.log)}>
      <FieldGroup>
        {/* Select */}
        <Field data-invalid={!!errors.department}>
          <FieldLabel>Department</FieldLabel>
          <Controller
            name="department"
            control={control}
            rules={{ required: "Select a department" }}
            render={({ field }) => (
              <Select onValueChange={field.onChange} value={field.value}>
                <SelectTrigger><SelectValue placeholder="Choose..." /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="eng">Engineering</SelectItem>
                  <SelectItem value="design">Design</SelectItem>
                </SelectContent>
              </Select>
            )}
          />
          <FieldError>{errors.department?.message}</FieldError>
        </Field>

        {/* Switch */}
        <Field orientation="horizontal">
          <Controller
            name="notifications"
            control={control}
            render={({ field }) => (
              <Switch checked={field.value} onCheckedChange={field.onChange} id="notifications" />
            )}
          />
          <FieldContent>
            <FieldLabel htmlFor="notifications">Notifications</FieldLabel>
            <FieldDescription>Receive email updates</FieldDescription>
          </FieldContent>
        </Field>
      </FieldGroup>
    </form>
  )
}
```

## Common Patterns

### Simple POST Form

For basic submission, you don't need `watch` or `useWatch`—`handleSubmit` provides all values:

```tsx
export function ContactForm() {
  const { register, handleSubmit, formState: { errors, isSubmitting }, reset } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  const onSubmit = async (data: FormData) => {
    const res = await fetch('/api/contact', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    if (res.ok) reset()
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <FieldGroup>
        <Field data-invalid={!!errors.email}>
          <FieldLabel htmlFor="email">Email</FieldLabel>
          <Input id="email" {...register("email")} aria-invalid={!!errors.email} />
          <FieldError>{errors.email?.message}</FieldError>
        </Field>
        
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Sending..." : "Submit"}
        </Button>
      </FieldGroup>
    </form>
  )
}
```

### Conditional Fields (when you need watch)

Only use `watch`/`useWatch` when UI depends on field values:

```tsx
const { register, watch } = useForm()
const accountType = watch("accountType")  // Re-renders form on change

return (
  <>
    <select {...register("accountType")}>
      <option value="personal">Personal</option>
      <option value="business">Business</option>
    </select>
    
    {accountType === "business" && (
      <input {...register("companyName", { required: "Required for business" })} />
    )}
  </>
)
```

### watch vs useWatch

| | `watch` | `useWatch` |
|---|---------|------------|
| Re-renders | Entire form component | Only component calling it |
| Use when | Simple forms, watching in same component | Large forms, watching in child components |

```tsx
// useWatch: isolates re-renders to child
function PriceDisplay({ control }) {
  const [qty, price] = useWatch({ control, name: ["qty", "price"] })
  return <p>Total: ${qty * price}</p>  // Only this component re-renders
}
```

### Destructuring Requirements

**formState subscription** — must destructure to subscribe:
```tsx
// ✅ Subscribes to errors and isSubmitting
const { formState: { errors, isSubmitting } } = useForm()

// ❌ Does NOT update on changes
const { formState } = useForm()
return <div>{formState.errors.name}</div>
```

**useEffect dependencies** — destructure to avoid infinite loops:
```tsx
// ✅ Correct
const { reset } = useForm()
useEffect(() => { reset(serverData) }, [reset, serverData])

// ❌ Infinite loop
const methods = useForm()
useEffect(() => { methods.reset(serverData) }, [methods])
```

## Critical Rules

- **Always use `data-invalid` on Field** for error styling
- **Always use `aria-invalid` on inputs** for accessibility  
- **Use Controller for Select, Switch, Slider** - they don't expose refs
- **Match `htmlFor` to input `id`** for label clicking
- **Use Zod resolver** - best TypeScript integration
- **Destructure `formState`** to subscribe: `const { errors } = formState` not `formState.errors`
- **Use `field.id` as key** in useFieldArray, never index
