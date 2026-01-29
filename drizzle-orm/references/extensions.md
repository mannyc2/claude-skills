# Extensions Reference

Drizzle ORM extensions for validation, type generation, and integrations.

## Table of Contents
1. [drizzle-zod](#drizzle-zod)
2. [drizzle-typebox](#drizzle-typebox)
3. [drizzle-valibot](#drizzle-valibot)

---

## drizzle-zod

Generate Zod schemas from Drizzle table definitions.

### Installation

```bash
npm install drizzle-zod
# or
bun add drizzle-zod
```

**Requirements:** drizzle-orm v0.36.0+, zod v3.25.1+

### Schema Generation

```typescript
import { pgTable, text, integer } from 'drizzle-orm/pg-core';
import { createSelectSchema, createInsertSchema, createUpdateSchema } from 'drizzle-zod';

const users = pgTable('users', {
  id: integer().generatedAlwaysAsIdentity().primaryKey(),
  name: text().notNull(),
  age: integer().notNull(),
  bio: text(),
});

// Select schema - for query results
const userSelectSchema = createSelectSchema(users);
// { id: number; name: string; age: number; bio: string | null }

// Insert schema - excludes generated columns, handles optionals
const userInsertSchema = createInsertSchema(users);
// { name: string; age: number; bio?: string | null }

// Update schema - all fields optional for partial updates
const userUpdateSchema = createUpdateSchema(users);
// { name?: string; age?: number; bio?: string | null }
```

### Usage with Queries

```typescript
// Validate API input before insert
const userInsertSchema = createInsertSchema(users);

async function createUser(input: unknown) {
  const parsed = userInsertSchema.parse(input);
  return db.insert(users).values(parsed);
}

// Validate query results
const userSelectSchema = createSelectSchema(users);

async function getUser(id: number) {
  const [row] = await db.select().from(users).where(eq(users.id, id));
  return userSelectSchema.parse(row);
}

// Partial updates
const userUpdateSchema = createUpdateSchema(users);

async function updateUser(id: number, input: unknown) {
  const parsed = userUpdateSchema.parse(input);
  return db.update(users).set(parsed).where(eq(users.id, id));
}
```

### Refining Schemas

Extend or overwrite fields:

```typescript
import { z } from 'zod';
import { createSelectSchema, createInsertSchema } from 'drizzle-zod';

const users = pgTable('users', {
  id: integer().primaryKey(),
  name: text().notNull(),
  email: text().notNull(),
  bio: text(),
  preferences: json(),
});

const userInsertSchema = createInsertSchema(users, {
  // Extend: add validation to generated schema
  name: (schema) => schema.min(2).max(50),
  
  // Extend: add email validation
  email: (schema) => schema.email(),
  
  // Extend: add length limit
  bio: (schema) => schema.max(1000),
  
  // Overwrite: replace json with specific schema
  preferences: z.object({
    theme: z.enum(['light', 'dark']),
    notifications: z.boolean(),
  }),
});
```

### Extended Zod Instances

Use with libraries that extend Zod (e.g., @hono/zod-openapi):

```typescript
import { createSchemaFactory } from 'drizzle-zod';
import { z } from '@hono/zod-openapi';

const { createInsertSchema, createSelectSchema } = createSchemaFactory({
  zodInstance: z,
});

const userInsertSchema = createInsertSchema(users, {
  name: (schema) => schema.openapi({ example: 'John Doe' }),
  email: (schema) => schema.email().openapi({ example: 'john@example.com' }),
});
```

### Type Coercion

Auto-coerce strings to dates, numbers, etc:

```typescript
import { createSchemaFactory } from 'drizzle-zod';

const { createInsertSchema } = createSchemaFactory({
  coerce: {
    date: true,  // z.coerce.date() for timestamp/date columns
  },
  // Or coerce all supported types:
  // coerce: true,
});

const users = pgTable('users', {
  createdAt: timestamp().notNull(),
});

const schema = createInsertSchema(users);
// createdAt accepts string input, coerces to Date
```

### Views & Enums

```typescript
import { pgEnum, pgView } from 'drizzle-orm/pg-core';
import { createSelectSchema } from 'drizzle-zod';

// Enum
const roleEnum = pgEnum('role', ['admin', 'user', 'guest']);
const roleSchema = createSelectSchema(roleEnum);
// z.enum(['admin', 'user', 'guest'])

// View
const activeUsers = pgView('active_users').as((qb) =>
  qb.select().from(users).where(eq(users.active, true))
);
const activeUserSchema = createSelectSchema(activeUsers);
```

### Type Mappings

| Drizzle Type | Zod Schema |
|--------------|------------|
| `boolean` | `z.boolean()` |
| `text`, `varchar`, `char` | `z.string()` |
| `uuid` | `z.string().uuid()` |
| `integer`, `serial` | `z.number().int()` |
| `bigint({ mode: 'number' })` | `z.number().int()` |
| `bigint({ mode: 'bigint' })` | `z.bigint()` |
| `real`, `float`, `double` | `z.number()` |
| `numeric`, `decimal` | `z.string()` |
| `timestamp` (mode: date) | `z.date()` |
| `timestamp` (mode: string) | `z.string()` |
| `json`, `jsonb` | `z.unknown()` |
| `array(...)` | `z.array(baseSchema)` |

---

## drizzle-typebox

Generate TypeBox schemas from Drizzle tables.

### Installation

```bash
npm install drizzle-typebox @sinclair/typebox
```

### Usage

```typescript
import { pgTable, text, integer } from 'drizzle-orm/pg-core';
import { createSelectSchema, createInsertSchema } from 'drizzle-typebox';

const users = pgTable('users', {
  id: integer().primaryKey(),
  name: text().notNull(),
});

const userSelectSchema = createSelectSchema(users);
const userInsertSchema = createInsertSchema(users);

// Use with TypeBox validation
import { Value } from '@sinclair/typebox/value';

const isValid = Value.Check(userInsertSchema, { name: 'John' });
```

### Refining Schemas

```typescript
import { Type } from '@sinclair/typebox';
import { createInsertSchema } from 'drizzle-typebox';

const userInsertSchema = createInsertSchema(users, {
  name: (schema) => Type.String({ ...schema, minLength: 2, maxLength: 50 }),
  email: Type.String({ format: 'email' }),
});
```

---

## drizzle-valibot

Generate Valibot schemas from Drizzle tables.

### Installation

```bash
npm install drizzle-valibot valibot
```

### Usage

```typescript
import { pgTable, text, integer } from 'drizzle-orm/pg-core';
import { createSelectSchema, createInsertSchema } from 'drizzle-valibot';
import * as v from 'valibot';

const users = pgTable('users', {
  id: integer().primaryKey(),
  name: text().notNull(),
  email: text().notNull(),
});

const userSelectSchema = createSelectSchema(users);
const userInsertSchema = createInsertSchema(users);

// Validate
const result = v.safeParse(userInsertSchema, { name: 'John', email: 'john@example.com' });
```

### Refining Schemas

```typescript
import * as v from 'valibot';
import { createInsertSchema } from 'drizzle-valibot';

const userInsertSchema = createInsertSchema(users, {
  name: (schema) => v.pipe(schema, v.minLength(2), v.maxLength(50)),
  email: v.pipe(v.string(), v.email()),
});
```

---

## Common Patterns

### API Validation Layer

```typescript
import { createInsertSchema, createUpdateSchema } from 'drizzle-zod';
import { z } from 'zod';

const users = pgTable('users', {
  id: integer().primaryKey().generatedAlwaysAsIdentity(),
  name: text().notNull(),
  email: text().notNull(),
});

// Strict insert schema with custom validations
export const createUserSchema = createInsertSchema(users, {
  name: (s) => s.min(1).max(100),
  email: (s) => s.email(),
});

// Update schema (all optional)
export const updateUserSchema = createUpdateSchema(users, {
  name: (s) => s.min(1).max(100),
  email: (s) => s.email(),
});

// API route handler
app.post('/users', async (req, res) => {
  const parsed = createUserSchema.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json({ errors: parsed.error.flatten() });
  }
  const user = await db.insert(users).values(parsed.data).returning();
  return res.json(user);
});
```

### Form Validation

```typescript
import { createInsertSchema } from 'drizzle-zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

const userFormSchema = createInsertSchema(users, {
  name: (s) => s.min(2, 'Name must be at least 2 characters'),
  email: (s) => s.email('Invalid email address'),
});

type UserFormData = z.infer<typeof userFormSchema>;

function UserForm() {
  const form = useForm<UserFormData>({
    resolver: zodResolver(userFormSchema),
  });
  
  // ...
}
```

### OpenAPI Integration

```typescript
import { createSchemaFactory } from 'drizzle-zod';
import { z } from '@hono/zod-openapi';

const { createSelectSchema, createInsertSchema } = createSchemaFactory({
  zodInstance: z,
});

export const UserSchema = createSelectSchema(users).openapi('User');

export const CreateUserSchema = createInsertSchema(users, {
  name: (s) => s.openapi({ example: 'John Doe' }),
  email: (s) => s.email().openapi({ example: 'john@example.com' }),
}).openapi('CreateUser');
```
