# shadcn Field Components

Layout components for composing accessible forms.

## Import

```tsx
import {
  Field,
  FieldContent,
  FieldDescription,
  FieldError,
  FieldGroup,
  FieldLabel,
  FieldLegend,
  FieldSeparator,
  FieldSet,
  FieldTitle,
} from "@/components/ui/field"
```

## Component Hierarchy

```
FieldSet (semantic fieldset)
├── FieldLegend (section title)
├── FieldDescription (section helper)
└── FieldGroup (stacks fields)
    ├── Field (single field wrapper)
    │   ├── FieldLabel
    │   ├── [Input/Select/Switch]
    │   ├── FieldDescription
    │   └── FieldError
    └── FieldSeparator
```

## Components

### Field

Core wrapper for single form control.

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `orientation` | `"vertical"` \| `"horizontal"` \| `"responsive"` | `"vertical"` | Layout direction. |
| `data-invalid` | `boolean` | | Error state styling. |

```tsx
// Vertical (default)
<Field>
  <FieldLabel htmlFor="email">Email</FieldLabel>
  <Input id="email" />
</Field>

// Horizontal (checkboxes, switches)
<Field orientation="horizontal">
  <Checkbox id="terms" />
  <FieldLabel htmlFor="terms">Accept terms</FieldLabel>
</Field>

// With error
<Field data-invalid={!!errors.email}>
  <Input aria-invalid={!!errors.email} />
  <FieldError>{errors.email?.message}</FieldError>
</Field>
```

### FieldContent

Groups label + description beside control (horizontal layouts).

```tsx
<Field orientation="horizontal">
  <Switch id="notifications" />
  <FieldContent>
    <FieldLabel htmlFor="notifications">Notifications</FieldLabel>
    <FieldDescription>Receive email updates</FieldDescription>
  </FieldContent>
</Field>
```

### FieldLabel

Label element. Match `htmlFor` to input `id`.

```tsx
<FieldLabel htmlFor="email">Email address</FieldLabel>
<Input id="email" />

// Lighter weight for checkboxes/radios
<FieldLabel className="font-normal">Option</FieldLabel>
```

### FieldTitle

Non-label title inside FieldContent (choice cards).

```tsx
<FieldContent>
  <FieldTitle>Premium Plan</FieldTitle>
  <FieldDescription>Best for teams</FieldDescription>
</FieldContent>
```

### FieldDescription

Helper text.

```tsx
<FieldDescription>We'll never share your email.</FieldDescription>
```

### FieldError

Validation message.

```tsx
// Single message
<FieldError>Email is required</FieldError>

// From RHF errors
<FieldError>{errors.email?.message}</FieldError>

// Array format
<FieldError errors={[errors.email]} />
```

### FieldSet

Semantic `<fieldset>` for grouping related fields.

```tsx
<FieldSet>
  <FieldLegend>Personal Information</FieldLegend>
  <FieldGroup>
    <Field>...</Field>
  </FieldGroup>
</FieldSet>
```

### FieldLegend

Legend for FieldSet.

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `variant` | `"legend"` \| `"label"` | `"legend"` | Size variant. |

```tsx
<FieldLegend>Section Title</FieldLegend>
<FieldLegend variant="label">Nested Section</FieldLegend>
```

### FieldGroup

Stacks Field components.

```tsx
<FieldGroup>
  <Field>...</Field>
  <Field>...</Field>
</FieldGroup>
```

### FieldSeparator

Divider between groups.

```tsx
<FieldSeparator />
<FieldSeparator>Or continue with</FieldSeparator>
```

## Layout Patterns

### Standard Vertical

```tsx
<Field>
  <FieldLabel htmlFor="email">Email</FieldLabel>
  <Input id="email" {...register("email")} />
  <FieldDescription>Your primary email</FieldDescription>
  <FieldError>{errors.email?.message}</FieldError>
</Field>
```

### Horizontal Checkbox

```tsx
<Field orientation="horizontal">
  <Checkbox id="terms" {...register("terms")} />
  <FieldLabel htmlFor="terms" className="font-normal">
    Accept terms
  </FieldLabel>
</Field>
```

### Grid Layout

```tsx
<div className="grid grid-cols-2 gap-4">
  <Field>
    <FieldLabel htmlFor="first">First</FieldLabel>
    <Input id="first" {...register("first")} />
  </Field>
  <Field>
    <FieldLabel htmlFor="last">Last</FieldLabel>
    <Input id="last" {...register("last")} />
  </Field>
</div>
```

### Choice Cards

Wrap Field inside FieldLabel:

```tsx
<RadioGroup>
  <FieldLabel htmlFor="premium">
    <Field orientation="horizontal">
      <FieldContent>
        <FieldTitle>Premium</FieldTitle>
        <FieldDescription>Full features</FieldDescription>
      </FieldContent>
      <RadioGroupItem value="premium" id="premium" />
    </Field>
  </FieldLabel>
</RadioGroup>
```

### Responsive

```tsx
<Field orientation="responsive">
  <FieldContent>
    <FieldLabel htmlFor="name">Name</FieldLabel>
    <FieldDescription>Your full name</FieldDescription>
  </FieldContent>
  <Input id="name" {...register("name")} />
</Field>
```
