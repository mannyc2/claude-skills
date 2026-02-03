---
name: typst-syntax
description: General-purpose Typst markup language reference with complete syntax documentation, examples, and templates. Use when creating Typst documents, cheat sheets, academic papers, presentations, or technical documentation. Provides anti-patterns to avoid common Markdown/LaTeX confusion.
allowed-tools: "Read,Write,Bash,Edit"
model: inherit
---

# Typst Markup Language Guide

## Overview

**Typst** is a modern, powerful markup language for typesetting documents. It's designed as a faster, more intuitive alternative to LaTeX while being more powerful than Markdown. Use this skill when creating .typ files, typesetting technical documents, academic papers, cheat sheets, or any professional documentation.

**When to invoke this skill**:
- Creating or editing `.typ` files
- Converting from Markdown or LaTeX to Typst
- Designing cheat sheets, academic papers, or presentations
- When user mentions Typst syntax, typesetting, or document layout

**Navigation**:
- For complete function reference: See `syntax-reference.md`
- For 20+ diverse examples: See `examples.md`
- For document patterns and templates: See `patterns.md`
- For ready-to-use templates: See `templates/` directory

---

## Critical Differences from Markdown and LaTeX

**IMPORTANT**: Claude is trained heavily on Markdown and LaTeX. Typst has different syntax conventions that you MUST follow to avoid errors.

| Element | Markdown | LaTeX | Typst | Critical Notes |
|---------|----------|-------|-------|----------------|
| **Bold** | `**text**` | `\textbf{text}` | `*text*` | ⚠️ Single asterisk, NOT double! |
| **Italic** | `*text*` or `_text_` | `\textit{text}` | `_text_` | ⚠️ Underscore only, NOT asterisk! |
| **Headings** | `# H1`, `## H2` | `\section{}`, `\subsection{}` | `= H1`, `== H2` | ⚠️ Equals signs, NOT hash! |
| **Code blocks** | ` ```lang ` | `\begin{verbatim}` | ` ```lang ` | Same as Markdown |
| **Math inline** | `$x$` (with extension) | `$x$` | `$x$` | Same as LaTeX |
| **Math block** | `$$x$$` | `\[x\]` or `$$x$$` | `$ x $` | ⚠️ Space-delimited, NOT double-dollar! |
| **Lists** | `- item` or `* item` | `\item` in enumerate | `- item` | Hyphen for unordered |
| **Functions** | N/A | `\command{}` | `#function()` | ⚠️ Hash prefix for code mode! |

**Common mistakes to avoid**:
- ❌ Using `**bold**` (Markdown) → ✅ Use `*bold*` (Typst)
- ❌ Using `#` for headings (Markdown) → ✅ Use `=` for headings (Typst)
- ❌ Using `\textbf{}` (LaTeX) → ✅ Use `*bold*` (Typst)
- ❌ Forgetting `columns:` parameter in tables → ✅ Always specify column count

---

## Core Syntax Reference

Typst has **three syntactical modes** that you must understand:

### 1. Markup Mode (Default)

This is the default mode for writing content. Special characters trigger formatting:

**Headings**:
```typst
= Heading Level 1
== Heading Level 2
=== Heading Level 3
==== Heading Level 4
```

**Emphasis**:
```typst
*bold text*
_italic text_
*_bold and italic_*
```

**Lists**:
```typst
- Unordered list item
- Another item
  - Nested item (2 spaces indent)
  - Another nested item

+ Ordered list item
+ Second item
+ Third item
```

**Links**:
```typst
https://example.com  // Auto-linked
#link("https://example.com")[Link text]
```

**Line breaks**:
```typst
Line one \
Line two

New paragraph (blank line above)
```

---

### 2. Code Mode (via `#` prefix)

Enter code mode by prefixing with `#`. This allows programming logic and function calls:

**Variables**:
```typst
#let x = 5
#let name = "Alice"
#let items = (1, 2, 3)
```

**Conditionals**:
```typst
#if x > 3 [Large] else [Small]
#if condition [
  Content when true
] else [
  Content when false
]
```

**Loops**:
```typst
#for item in array [#item, ]
#for i in range(5) [Number #i ]
```

**Function calls**:
```typst
#table(columns: 3, [A], [B], [C])
#columns(2)[content in two columns]
#figure(image("path.png"), caption: [Caption])
```

---

### 3. Math Mode (via `$` delimiters)

Math mode for equations and mathematical notation:

**Inline math**:
```typst
The formula $a^2 + b^2 = c^2$ is the Pythagorean theorem.
```

**Block math** (space-delimited):
```typst
$ E = m c^2 $

$ sum_(i=1)^n i = (n(n+1))/2 $
```

**Common symbols**:
```typst
$alpha$, $beta$, $gamma$  // Greek letters
$sum$, $integral$, $product$  // Operators
$<=$ $>=$ $!=$ $equiv$  // Relations
$a/b$ or $frac(a, b)$  // Fractions
$x_i^2$  // Subscripts and superscripts
```

---

## Essential Functions

### Page Setup

```typst
// Set page dimensions and margins
#set page(width: 8.5in, height: 11in, margin: 1in)

// Or use standard paper sizes
#set page(paper: "us-letter", margin: 0.5in)
#set page(paper: "a4", margin: (x: 1in, y: 1.5in))
```

### Typography

```typst
// Set default text properties
#set text(font: "Arial", size: 11pt)
#set text(font: "Times New Roman", size: 12pt, fill: black)

// Paragraph settings
#set par(justify: true, leading: 0.65em)
#set par(first-line-indent: 0.5in)
```

### Layout Functions

```typst
// Multi-column layout
#columns(2)[
  Content in two columns
]

#columns(3, gutter: 0.5in)[
  Content in three columns with custom gutter
]

// Grid layout
#grid(
  columns: (1fr, 2fr),
  [Column 1], [Column 2]
)

// Manual column break
#colbreak()
```

### Tables

**CRITICAL**: The `columns` parameter is REQUIRED. This is the most common error.

```typst
// Basic table
#table(
  columns: 3,
  [Header 1], [Header 2], [Header 3],
  [Row 1 Col 1], [Row 1 Col 2], [Row 1 Col 3],
  [Row 2 Col 1], [Row 2 Col 2], [Row 2 Col 3]
)

// Styled table
#table(
  columns: (1.5fr, 1fr, 1fr),  // Fractional widths
  stroke: 0.5pt,  // Border width
  align: (left, center, center),  // Per-column alignment
  [*Name*], [*Time*], [*Space*],
  [Quick Sort], [O(n log n)], [O(log n)],
  [Merge Sort], [O(n log n)], [O(n)]
)
```

### Code Blocks

```typst
// Code block with syntax highlighting
```c
int main() {
    printf("Hello, World!");
    return 0;
}
\```  // Note: escaped for display

// Inline code
This is `inline code` within text.
```

### Figures and Images

```typst
#figure(
  image("diagram.png", width: 80%),
  caption: [System architecture diagram]
)

#figure(
  table(columns: 2, [A], [B], [1], [2]),
  caption: [Comparison table]
)
```

---

## Set and Show Rules (Global Styling)

**Set rules** apply settings globally to all future instances:

```typst
// Automatically number all headings
#set heading(numbering: "1.1")

// Set default paragraph justification
#set par(justify: true)

// Set heading appearance
#set heading(supplement: "Section")
```

**Show rules** transform how elements appear:

```typst
// Style all level 1 headings
#show heading.where(level: 1): it => [
  #set text(size: 18pt, weight: "bold")
  #block(above: 1em, below: 0.5em)[#it.body]
]

// Style all level 2 headings
#show heading.where(level: 2): it => [
  #set text(size: 14pt, weight: "bold", fill: blue)
  #it.body
]

// Add emphasis to specific terms
#show "IMPORTANT": set text(weight: "bold", fill: red)
```

---

## Examples

### Example 1: Basic Document

<example>
<description>Simple document with headings, emphasis, and lists</description>
<input>Create a Typst document about operating systems with a heading, some bold text, and a bulleted list</input>
<output>
```typst
= Operating Systems

An *operating system* is a _critical_ software layer that manages hardware resources.

Key functions:
- Process management
- Memory management
- File system management
- I/O device management

The OS provides *abstraction* and *protection* for applications.
```
</output>
</example>

---

### Example 2: Multi-Column Cheat Sheet

<example>
<description>Compact cheat sheet with two-column layout</description>
<input>Create a two-column cheat sheet format for exam reference</input>
<output>
```typst
#set page(margin: 0.5in)
#set text(size: 9pt)
#set par(leading: 0.5em)

#columns(2)[
  = CPU Scheduling

  == FCFS
  *Definition*: First-Come, First-Served

  *Pros*: Simple, fair

  *Cons*: Convoy effect

  == SJF
  *Definition*: Shortest Job First

  *Pros*: Minimum average wait time

  *Cons*: Starvation possible

  #colbreak()

  = Memory Management

  == Paging
  *Definition*: Fixed-size memory chunks

  *Pros*: No external fragmentation

  *Cons*: Internal fragmentation
]
```
</output>
</example>

---

### Example 3: Table with Comparison

<example>
<description>Comparison table with synchronization mechanisms</description>
<input>Create a table comparing synchronization mechanisms</input>
<output>
```typst
#table(
  columns: (1.5fr, 1fr, 1fr, 2fr),
  stroke: 0.5pt,
  align: (left, center, center, left),

  [*Mechanism*], [*Busy Wait*], [*Complexity*], [*Use Case*],
  [Peterson's], [Yes], [High], [Educational only],
  [Mutex Lock], [Yes], [Low], [Simple mutual exclusion],
  [Semaphore], [No], [Low], [Resource counting],
  [Monitor], [No], [Medium], [Complex synchronization]
)
```
</output>
</example>

---

### Example 4: Code Block with Algorithm

<example>
<description>Algorithm documentation with code and explanation</description>
<input>Show Peterson's solution algorithm in a Typst document</input>
<output>
```typst
= Peterson's Solution

*Algorithm for Process i*:

```c
do {
    flag[i] = true;
    turn = j;
    while (flag[j] && turn == j);

    /* Critical Section */

    flag[i] = false;

    /* Remainder Section */
} while (true);
\```

*Properties*:
- Meets *mutual exclusion* requirement
- Ensures *progress* (no indefinite postponement)
- Provides *bounded waiting* guarantee
```
</output>
</example>

---

### Example 5: Math Equations

<example>
<description>Mathematical formulas with proper notation</description>
<input>Document the effective access time formula for TLB</input>
<output>
```typst
= Effective Access Time (EAT)

The effective access time with TLB is calculated as:

$ "EAT" = alpha times ("TLB access time" + "memory access time") \
  + (1 - alpha) times ("TLB access time" + 2 times "memory access time") $

where $alpha$ is the TLB hit ratio.

*Example calculation*:

Given:
- TLB hit ratio: $alpha = 0.98$
- TLB access time: 1 ns
- Memory access time: 100 ns

$ "EAT" = 0.98 times (1 + 100) + 0.02 times (1 + 200) = 103 "ns" $
```
</output>
</example>

---

## Anti-Examples (Common Mistakes)

### Anti-Example 1: Bold and Italic Syntax

<incorrect_example>
<wrong>
```typst
**Bold text** and *italic text*
```
</wrong>
<why_wrong>This uses Markdown syntax. Typst uses single asterisk for bold and underscore for italic (opposite of common Markdown conventions)</why_wrong>
<correct>
```typst
*Bold text* and _italic text_
```
</correct>
</incorrect_example>

---

### Anti-Example 2: Heading Syntax

<incorrect_example>
<wrong>
```typst
# Heading 1
## Heading 2
### Heading 3
```
</wrong>
<why_wrong>Hash symbols (#) are for code mode in Typst, not headings. This is Markdown syntax</why_wrong>
<correct>
```typst
= Heading 1
== Heading 2
=== Heading 3
```
</correct>
</incorrect_example>

---

### Anti-Example 3: Table Column Count

<incorrect_example>
<wrong>
```typst
#table([A], [B], [C], [1], [2], [3])
```
</wrong>
<why_wrong>Missing the required `columns:` parameter. Typst cannot infer column count</why_wrong>
<correct>
```typst
#table(
  columns: 3,
  [A], [B], [C],
  [1], [2], [3]
)
```
</correct>
</incorrect_example>

---

## Verification Checklist

**Before generating or outputting Typst code, verify the following**:

### 1. Syntax Mode Correctness
- [ ] Headings use `=` symbols, NOT `#`
- [ ] Bold uses `*text*`, NOT `**text**`
- [ ] Italic uses `_text_`, NOT `*text*`
- [ ] Code mode uses `#` prefix for functions
- [ ] Math mode uses `$` delimiters with proper spacing

### 2. Function Signatures
- [ ] `#table()` has explicit `columns:` parameter (REQUIRED)
- [ ] `#columns()` wraps content in `[...]` brackets
- [ ] Set rules use `#set element(parameter: value)` format
- [ ] Show rules use `#show selector: transformation` format
- [ ] No LaTeX commands (no `\textbf`, `\section`, `\begin{}`, etc.)

### 3. Layout and Spacing
- [ ] Page settings use correct units (in, cm, pt, %)
- [ ] Text size specified with `pt` suffix (e.g., `11pt`)
- [ ] Margins set via `#set page(margin: ...)`
- [ ] Column layouts use `#columns(N)[content]` syntax

### 4. Content Formatting
- [ ] Code blocks use triple backticks with language identifier
- [ ] Tables have consistent column counts per row
- [ ] Math symbols use Typst notation, not LaTeX (e.g., `sum` not `\sum`)
- [ ] Lists use `-` for unordered, `+` for ordered

### 5. Common Mistakes to Avoid
- [ ] NOT using Markdown double asterisks `**bold**`
- [ ] NOT using hash for headings `# Heading`
- [ ] NOT forgetting `columns:` parameter in tables
- [ ] NOT mixing LaTeX syntax with Typst

**If uncertain about syntax**:
- Consult `syntax-reference.md` for complete function signatures
- Check `examples.md` for similar use cases
- Review `templates/` for working patterns

---

## Extended Resources

### Complete Reference Documentation

**Comprehensive function reference**: See `syntax-reference.md`
- Detailed function signatures with all parameters
- Text formatting: `#text()`, `#emph()`, `#strong()`
- Layout functions: `#page()`, `#columns()`, `#grid()`, `#block()`
- Tables and figures: `#table()`, `#figure()`, `#image()`
- Math mode: symbols, operators, fractions, matrices
- Set and show rules: selectors, transformations
- Scripting: variables, conditionals, loops, functions

**Extended examples library**: See `examples.md`
- 20+ diverse, working examples
- Categories: basic documents, academic papers, cheat sheets, presentations, technical docs
- Each example includes description, complete code, and key techniques

**Document patterns and templates**: See `patterns.md`
- Reusable templates with design rationale
- Academic paper pattern
- Cheat sheet pattern (dense multi-column)
- Resume/CV pattern
- Presentation slides pattern
- Technical report pattern

### Ready-to-Use Templates

**Blank cheat sheet template**: `templates/cheatsheet-basic.typ`
- Multi-column layout for compact reference sheets
- Minimal margins, small text, tight spacing
- Examples of tables, code blocks, lists, math
- Ready to customize with your content

**OS synchronization example**: `templates/cheatsheet-os-example.typ`
- Real-world example using Ch6 lecture content
- Demonstrates: code blocks, tables, algorithms, definitions
- Shows how to create dense, information-rich cheat sheets

### Online Resources

**Official Typst documentation**:
- Main docs: https://typst.app/docs/
- Syntax reference: https://typst.app/docs/reference/syntax/
- Tutorial: https://typst.app/docs/tutorial/
- Function reference: https://typst.app/docs/reference/

**Community resources**:
- Web app (for testing): https://typst.app/
- GitHub repository: https://github.com/typst/typst
- Discord community: https://discord.gg/2uDybryKPe

---

## Summary

Typst is a powerful, modern markup language that combines the simplicity of Markdown with the power of LaTeX. The key to success with Typst is remembering the critical syntax differences:

**Remember**:
- ✅ `*bold*` and `_italic_` (NOT Markdown's `**bold**` and `*italic*`)
- ✅ `= Heading` (NOT Markdown's `# Heading`)
- ✅ `#table(columns: 3, ...)` (columns parameter is REQUIRED)
- ✅ `#function()` for code mode (NOT LaTeX's `\command{}`)
- ✅ `$ math $` with spaces for block math

**When in doubt**:
1. Check the verification checklist above
2. Consult `syntax-reference.md` for function details
3. Look at `examples.md` for similar use cases
4. Review working templates in `templates/`

This skill provides everything needed to generate correct, idiomatic Typst code for any document type.
