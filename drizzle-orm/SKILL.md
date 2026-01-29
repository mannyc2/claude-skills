---
name: drizzle-orm
description: "TypeScript ORM for SQL databases. Use when building database schemas, writing type-safe queries, setting up relations, or managing migrations with Drizzle ORM. Triggers on drizzle schema definition, drizzle queries, drizzle relations, drizzle migrations, drizzle-kit, type-safe SQL, PostgreSQL/MySQL/SQLite with TypeScript. Also use when user mentions drizzle in database context or asks about TypeScript ORMs."
---

# Drizzle ORM Skill

Type-safe TypeScript ORM with SQL-like syntax. Schema acts as single source of truth for queries and migrations.

## Quick Start

```typescript
import { pgTable, serial, text, integer, timestamp } from 'drizzle-orm/pg-core';
import { drizzle } from 'drizzle-orm/node-postgres';
import { Pool } from 'pg';
import { eq } from 'drizzle-orm';

// 1. Define schema
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  email: text('email').notNull().unique(),
  createdAt: timestamp('created_at').defaultNow(),
});

// 2. Connect
const pool = new Pool({ connectionString: process.env.DATABASE_URL });
const db = drizzle(pool);

// 3. Query
const allUsers = await db.select().from(users);
const user = await db.select().from(users).where(eq(users.id, 1));
await db.insert(users).values({ name: 'John', email: 'john@example.com' });
```

## Database Drivers

| Database | Package | Table Function |
|----------|---------|----------------|
| PostgreSQL | `drizzle-orm/pg-core` | `pgTable` |
| MySQL | `drizzle-orm/mysql-core` | `mysqlTable` |
| SQLite | `drizzle-orm/sqlite-core` | `sqliteTable` |

## Core Operations

```typescript
import { eq, and, gt, like, isNull, inArray } from 'drizzle-orm';

// SELECT
db.select().from(users);
db.select({ name: users.name }).from(users);
db.select().from(users).where(eq(users.id, 1));
db.select().from(users).where(and(gt(users.id, 10), like(users.email, '%@gmail.com')));

// INSERT
await db.insert(users).values({ name: 'John', email: 'john@example.com' });
await db.insert(users).values([{ name: 'A' }, { name: 'B' }]);
const [newUser] = await db.insert(users).values({ name: 'New' }).returning();

// UPDATE
await db.update(users).set({ name: 'Updated' }).where(eq(users.id, 1));

// DELETE
await db.delete(users).where(eq(users.id, 1));

// JOIN
db.select().from(posts).innerJoin(users, eq(posts.authorId, users.id));
db.select().from(users).leftJoin(posts, eq(users.id, posts.authorId));
```

## Migrations (drizzle-kit)

```typescript
// drizzle.config.ts
import { defineConfig } from 'drizzle-kit';

export default defineConfig({
  dialect: 'postgresql',
  schema: './src/db/schema.ts',
  out: './drizzle',
  dbCredentials: { url: process.env.DATABASE_URL! },
});
```

```bash
npx drizzle-kit generate  # Generate SQL from schema diff
npx drizzle-kit migrate   # Apply migrations
npx drizzle-kit push      # Push schema directly (dev)
npx drizzle-kit pull      # Introspect DB to schema
npx drizzle-kit studio    # GUI browser
```

## Common Patterns

```typescript
// Reusable timestamps
const timestamps = {
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').$onUpdate(() => new Date()),
};

export const posts = pgTable('posts', {
  id: serial('id').primaryKey(),
  title: text('title').notNull(),
  ...timestamps,
});

// Transactions
await db.transaction(async (tx) => {
  const [user] = await tx.insert(users).values({ name: 'A' }).returning();
  await tx.insert(posts).values({ title: 'Post', authorId: user.id });
});

// Type inference
import { InferSelectModel, InferInsertModel } from 'drizzle-orm';
type User = InferSelectModel<typeof users>;
type NewUser = InferInsertModel<typeof users>;
```

## References

- **[schema.md](references/schema.md)** - Column types, modifiers, constraints, indexes, custom types, generated columns
- **[relations.md](references/relations.md)** - defineRelations, one/many, through tables, aliases, indexing strategies
- **[queries.md](references/queries.md)** - Filters/operators, relational queries, CTEs, subqueries, extras, iterators
- **[advanced.md](references/advanced.md)** - Set operations, batch API, caching, read replicas, dynamic queries
- **[migrations.md](references/migrations.md)** - drizzle-kit workflows, custom migrations, runtime migrations
- **[extensions.md](references/extensions.md)** - drizzle-zod, drizzle-typebox, drizzle-valibot validation
- **[seeding.md](references/seeding.md)** - drizzle-seed generators, refinements, weighted random, test data
