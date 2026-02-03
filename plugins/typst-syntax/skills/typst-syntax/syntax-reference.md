# Typst Complete Syntax Reference

## Introduction

This document provides a comprehensive reference for Typst syntax, functions, and parameters. Use this as a lookup resource when you need detailed information about specific language features.

**Organization**:
- [Markup Mode](#markup-mode) - Text formatting with special characters
- [Code Mode](#code-mode) - Scripting and function calls
- [Math Mode](#math-mode) - Mathematical notation
- [Text Formatting Functions](#text-formatting-functions)
- [Layout Functions](#layout-functions)
- [Document Setup](#document-setup)
- [Tables and Figures](#tables-and-figures)
- [Code Blocks](#code-blocks)
- [Set and Show Rules](#set-and-show-rules)
- [Scripting](#scripting)
- [Data Types](#data-types)

**Cross-references**:
- For quick syntax overview: See SKILL.md
- For working examples: See examples.md
- For document templates: See patterns.md

---

## Markup Mode

Typst documents start in markup mode, where text is written naturally with special syntax for formatting.

### Headings

Create headings by starting a line with one or more equals signs followed by a space:

```typst
= Level 1 Heading
== Level 2 Heading
=== Level 3 Heading
==== Level 4 Heading
```

**Common Pitfalls**:
- ❌ `# Heading` — This is Markdown, not Typst
- ✅ `= Heading` — Correct Typst syntax

### Text Emphasis

**Bold text** uses single asterisks at word boundaries:

```typst
*This is bold text*
```

**Italic text** uses underscores at word boundaries:

```typst
_This is italic text_
```

**Combined emphasis**:
```typst
*_Bold and italic_*
```

**⚠️ CRITICAL**: This is the most common LLM error with Typst:
- ❌ `**bold**` — This is Markdown, NOT Typst
- ❌ `\textbf{bold}` — This is LaTeX, NOT Typst
- ✅ `*bold*` — Correct Typst syntax (single asterisks)

For mid-word formatting, use functions: `un#strong[bold]ed` or `un#emph[italic]ed`.

### Lists

**Bullet lists** start lines with a hyphen:

```typst
- First item
- Second item
  - Nested item (indented with 2 spaces)
- Third item
```

**Numbered lists** use `+` for automatic numbering:

```typst
+ First item
+ Second item
+ Third item
```

Or explicit numbers:
```typst
1. First item
2. Second item
3. Third item
```

**Term lists** (definitions) use `/` syntax:

```typst
/ Term: Definition goes here
/ Ligature: A merged glyph combining multiple characters.
```

**Common Pitfalls**:
- ❌ `* item` — Asterisk creates bold text, not list items
- ✅ `- item` — Hyphen creates list items

### Links and References

URLs are automatically detected and linked:

```typst
Visit https://typst.app/ for more.
```

Explicit links use the function:

```typst
#link("https://typst.app/")[Click here]
```

**Labels and references** connect document elements:

```typst
= Introduction <intro>

See @intro for details.
As discussed in @intro[the introduction].
```

Labels attach to any element with `<labelname>` immediately after. Reference with `@labelname`.

### Raw Text and Code

**Inline code** uses single backticks:

```typst
Use `print(1)` to output.
```

**Code blocks** use triple backticks with optional language tag:

````typst
```python
def hello():
    return "world"
```
````

### Comments

```typst
// Single line comment

/* Multi-line
   block comment */
```

### Line Breaks and Paragraphs

**Line break** within a paragraph uses backslash:

```typst
Line one \
Line two
```

**Paragraph break** requires a blank line between paragraphs.

### Smart Typography

Typst automatically converts certain character sequences:

| Input | Output | Description |
|-------|--------|-------------|
| `~` | Non-breaking space | Keeps words together |
| `---` | — (em dash) | Long dash |
| `--` | – (en dash) | Medium dash for ranges |
| `-?` | Soft hyphen | Optional line break point |
| `...` | … (ellipsis) | Three dots |

### Escape Sequences

```typst
\*literal asterisks\*
\_literal underscores\_
\#literal hash
\@literal at sign
\\literal backslash
\u{1f600}  // Unicode codepoint (emoji 😀)
```

---

## Code Mode

The hash (`#`) prefix switches from markup mode to code mode for expressions, function calls, and scripting.

### The # Prefix

```typst
#emph[Hello]
#"hello".len()
#(1 + 2)
```

### Mode Switching

| From | To | Syntax |
|------|-----|--------|
| Markup | Code | `#expression` |
| Markup | Math | `$...$` |
| Code | Markup | `[content]` |
| Code | Math | `$...$` |

### Function Call Syntax

**Basic syntax**:
```typst
#function-name(arg1, arg2)
```

**Named arguments** use `name: value`:
```typst
#rect(width: 2cm, height: 1cm, fill: red)
```

**Content blocks** with `[]` are trailing arguments:
```typst
#list[A][B][C]
#text(size: 14pt)[Large text]
```

**Common Pitfalls**:
- ❌ `#text{content}` — Braces are for code blocks, not content
- ✅ `#text[content]` — Square brackets for content arguments

---

## Text Formatting Functions

### #text()

**Purpose**: Style text appearance with custom font, size, weight, and color

**Signature**:
```typst
#text(
  font: string | array,
  size: length,
  weight: string | int,
  style: string,
  fill: color,
  tracking: length,
  spacing: length,
  baseline: length,
  lang: string,
  region: string,
  body: content
)
```

**Key Parameters**:
- `font`: Font family name or array for fallbacks
  - `"Arial"`, `"Times New Roman"`, `"Courier New"`
  - `("Helvetica", "Arial", sans-serif)` — fallback chain
- `size`: Font size with unit (`11pt`, `1.2em`, `14px`)
- `weight`: Font weight
  - String: "thin", "extralight", "light", "regular", "medium", "semibold", "bold", "extrabold", "black"
  - Numeric: 100-900 (400=regular, 700=bold)
- `style`: "normal" or "italic"
- `fill`: Text color (`red`, `rgb(255, 0, 0)`, `#FF0000`)
- `tracking`: Letter spacing
- `lang`: Language code for hyphenation ("en", "de", "fr")

**Examples**:

```typst
#text(size: 14pt, weight: "bold")[Important Text]
#text(font: "Courier New", fill: blue)[Code snippet]

#text(
  font: "Times New Roman",
  size: 12pt,
  weight: "bold",
  style: "italic",
  fill: rgb(200, 0, 0)
)[Emphasized heading]
```

**Common Pitfalls**:
- ❌ `size: 12` — Missing unit
- ✅ `size: 12pt` — Include unit
- ❌ `\textbf{}` — LaTeX syntax doesn't work
- ✅ `weight: "bold"` — Use named parameter

---

### #emph()

**Purpose**: Emphasize text (typically renders as italic)

**Signature**:
```typst
#emph(body: content)
```

**Examples**:
```typst
This is #emph[emphasized] text.
```

**Note**: Prefer `_italic_` markup for simple cases. Use `#emph()` when emphasis might be styled differently via show rules.

---

### #strong()

**Purpose**: Strong emphasis (typically renders as bold)

**Signature**:
```typst
#strong(body: content)
```

**Examples**:
```typst
This is #strong[important] text.
```

**Note**: Prefer `*bold*` markup for simple cases. Use `#strong()` for programmatic control.

---

### #strike()

**Purpose**: Strikethrough text (no markup shorthand exists)

**Signature**:
```typst
#strike(stroke: stroke, offset: length, extent: length, body: content)
```

**Examples**:
```typst
#strike[Deleted text]
#strike(stroke: 1.5pt + red)[Red strikethrough]
```

---

### #underline()

**Purpose**: Underline text

**Signature**:
```typst
#underline(stroke: stroke, offset: length, extent: length, body: content)
```

**Examples**:
```typst
#underline[Underlined text]
#underline(stroke: 2pt + blue)[Blue underline]
```

---

### #highlight()

**Purpose**: Highlight text with background color

**Signature**:
```typst
#highlight(fill: color, top-edge: string, bottom-edge: string, body: content)
```

**Examples**:
```typst
#highlight[Highlighted text]
#highlight(fill: yellow)[Yellow highlight]
```

---

### #smallcaps()

**Purpose**: Render text in small capitals

**Examples**:
```typst
#smallcaps[Small Capitals]
```

---

### #upper() and #lower()

**Purpose**: Convert text case

**Examples**:
```typst
#upper("hello")  // "HELLO"
#lower("HELLO")  // "hello"
```

---

### #link()

**Purpose**: Create hyperlinks

**Signature**:
```typst
#link(dest: string | label, body: content)
```

**Parameters**:
- `dest`: URL string or label reference
- `body`: Link text (optional — uses URL if omitted)

**Examples**:
```typst
#link("https://typst.app")[Typst Website]
#link(<intro>)[Go to introduction]
```

---

## Layout Functions

### #page()

**Purpose**: Set page dimensions, margins, headers, and footers

**Signature**:
```typst
#set page(
  paper: string,
  width: length,
  height: length,
  margin: length | dictionary,
  columns: int,
  fill: color,
  numbering: string,
  number-align: alignment,
  header: content,
  footer: content,
  header-ascent: length,
  footer-descent: length
)
```

**Key Parameters**:
- `paper`: Standard paper size
  - `"a4"`, `"a5"`, `"a3"` (A-series)
  - `"us-letter"`, `"us-legal"`, `"us-tabloid"`
- `width`, `height`: Custom dimensions (`8.5in`, `21cm`)
- `margin`: Margins
  - Single value: `1in` (all sides)
  - Dictionary: `(x: 1in, y: 1.5in)` or `(left: 1in, right: 1in, top: 1.5in, bottom: 1.5in)`
- `columns`: Number of columns
- `numbering`: Page numbering format (`"1"`, `"i"`, `"I"`, `"a"`, `"1 of 1"`)

**Examples**:

```typst
// Standard letter size
#set page(paper: "us-letter", margin: 1in)

// Custom dimensions
#set page(width: 8.5in, height: 11in, margin: 0.5in)

// Asymmetric margins
#set page(
  paper: "a4",
  margin: (left: 1.5in, right: 1in, top: 1in, bottom: 1in)
)

// With headers and footers
#set page(
  paper: "us-letter",
  margin: 1in,
  header: [Document Title #h(1fr) Chapter 1],
  footer: context [Page #counter(page).display("1 of 1", both: true)],
  numbering: "1"
)
```

---

### #columns()

**Purpose**: Create multi-column layout

**Signature**:
```typst
#columns(count: int, gutter: length, body: content)
```

**Parameters**:
- `count`: Number of columns (2, 3, 4, etc.)
- `gutter`: Space between columns (default: auto)
- `body`: Content to lay out

**Examples**:

```typst
// Two-column layout
#columns(2)[
  Content flows across two columns automatically.
]

// Three columns with custom gutter
#columns(3, gutter: 0.5in)[
  Content in three columns.
]

// Manual column break
#columns(2)[
  Content in first column.
  #colbreak()
  Content in second column.
]
```

---

### #grid()

**Purpose**: Create precise grid layouts with custom column widths

**Signature**:
```typst
#grid(
  columns: int | array,
  rows: int | array,
  gutter: length,
  column-gutter: length,
  row-gutter: length,
  align: alignment | array,
  ...cells: content
)
```

**Parameters**:
- `columns`: Column specifications
  - Integer: Equal-width columns (`3`)
  - Array: Custom widths (`(1fr, 2fr, 1fr)`, `(100pt, auto, 1fr)`)
- `rows`: Row specifications (same format)
- `gutter`: Spacing between all cells
- `column-gutter`, `row-gutter`: Directional spacing

**Examples**:

```typst
// Two-column grid with custom widths
#grid(
  columns: (1fr, 2fr),
  [Narrow], [Wide]
)

// Complex grid
#grid(
  columns: (100pt, auto, 1fr),
  rows: (auto, 50pt),
  gutter: 10pt,
  [Fixed], [Auto], [Flexible],
  [Cell 1], [Cell 2], [Cell 3]
)
```

---

### #block()

**Purpose**: Create block-level container with spacing and styling

**Signature**:
```typst
#block(
  width: length,
  height: length,
  breakable: bool,
  fill: color,
  stroke: stroke,
  radius: length,
  inset: length | dictionary,
  outset: length | dictionary,
  above: length,
  below: length,
  body: content
)
```

**Examples**:

```typst
// Highlighted box
#block(
  fill: rgb(240, 240, 255),
  stroke: 1pt + blue,
  radius: 4pt,
  inset: 10pt
)[
  Important note: This is highlighted content.
]

// Spacing control
#block(above: 2em, below: 1em)[
  Content with custom spacing.
]
```

---

### #box()

**Purpose**: Create inline container

**Signature**:
```typst
#box(
  width: length,
  height: length,
  baseline: length,
  fill: color,
  stroke: stroke,
  radius: length,
  inset: length | dictionary,
  outset: length | dictionary,
  body: content
)
```

**Examples**:
```typst
#box(fill: aqua, inset: 4pt)[Boxed]
#box(width: 50pt, height: 30pt, fill: yellow)[Fixed size]
```

---

### #align()

**Purpose**: Align content horizontally or vertically

**Signature**:
```typst
#align(alignment: alignment, body: content)
```

**Alignment Values**:
- Horizontal: `left`, `center`, `right`
- Vertical: `top`, `horizon`, `bottom`
- Combined: `top + left`, `center + horizon`

**Examples**:
```typst
#align(center)[Centered text]
#align(right)[Right-aligned]
#align(center + horizon)[Centered both ways]
```

---

### #pad()

**Purpose**: Add padding around content

**Signature**:
```typst
#pad(
  left: length,
  right: length,
  top: length,
  bottom: length,
  x: length,
  y: length,
  rest: length,
  body: content
)
```

**Examples**:
```typst
#pad(10pt)[Padding on all sides]
#pad(x: 20pt, y: 10pt)[Horizontal and vertical]
#pad(left: 30pt)[Left padding only]
```

---

### #stack()

**Purpose**: Stack content vertically or horizontally

**Signature**:
```typst
#stack(dir: direction, spacing: length, ...children: content)
```

**Parameters**:
- `dir`: Direction — `ttb` (top-to-bottom), `btt`, `ltr`, `rtl`
- `spacing`: Space between items

**Examples**:
```typst
#stack(
  dir: ttb,
  spacing: 5pt,
  rect[First],
  rect[Second],
  rect[Third]
)
```

---

### #h() and #v()

**Purpose**: Insert horizontal or vertical space

**Examples**:
```typst
Left #h(1fr) Right  // Push apart with flexible space
Left #h(2cm) Right  // Fixed 2cm space

Above
#v(1em)
Below
```

---

### #pagebreak()

**Purpose**: Insert page break

**Signature**:
```typst
#pagebreak(weak: bool, to: string)
```

**Parameters**:
- `weak`: Only break if needed (`true`/`false`)
- `to`: Skip to specific page (`"odd"`, `"even"`)

**Examples**:
```typst
#pagebreak()
#pagebreak(weak: true)
#pagebreak(to: "odd")
```

---

### #colbreak()

**Purpose**: Insert column break (within `#columns()`)

**Examples**:
```typst
#columns(2)[
  First column content.
  #colbreak()
  Second column content.
]
```

---

## Document Setup

### #set text()

**Purpose**: Set default text properties for the document

**Examples**:
```typst
#set text(font: "Times New Roman", size: 12pt)
#set text(font: ("Helvetica Neue", "Arial", sans-serif))
#set text(font: "Georgia", size: 11pt, fill: rgb(40, 40, 40))
```

---

### #set par()

**Purpose**: Set default paragraph properties

**Signature**:
```typst
#set par(
  justify: bool,
  leading: length,
  spacing: length,
  first-line-indent: length,
  hanging-indent: length,
  linebreaks: string
)
```

**Parameters**:
- `justify`: Justify text (`true`/`false`)
- `leading`: Line spacing (`0.65em`, `1.5em`)
- `spacing`: Space between paragraphs
- `first-line-indent`: Indent first line
- `hanging-indent`: Indent all but first line
- `linebreaks`: `"simple"` or `"optimized"`

**Examples**:
```typst
// Justified with normal spacing
#set par(justify: true, leading: 0.65em)

// Traditional book style
#set par(first-line-indent: 0.5in, spacing: 0em)

// Bibliography style
#set par(hanging-indent: 0.5in)
```

---

### #set heading()

**Purpose**: Configure heading appearance and numbering

**Signature**:
```typst
#set heading(
  numbering: string | function,
  supplement: string,
  outlined: bool,
  bookmarked: bool
)
```

**Parameters**:
- `numbering`: Numbering pattern
  - `"1"` — Arabic (1, 2, 3)
  - `"1.1"` — Hierarchical (1, 1.1, 1.1.1)
  - `"I"` — Roman (I, II, III)
  - `"A"` — Letters (A, B, C)
- `supplement`: Text before number ("Chapter", "Section")
- `outlined`: Include in outline/TOC
- `bookmarked`: Create PDF bookmarks

**Examples**:
```typst
#set heading(numbering: "1.1")
#set heading(numbering: "1", supplement: "Chapter")
```

---

### #outline()

**Purpose**: Generate table of contents

**Signature**:
```typst
#outline(
  title: content,
  target: selector,
  depth: int,
  indent: length | bool
)
```

**Examples**:
```typst
#outline()
#outline(title: [Table of Contents])
#outline(depth: 2)
#outline(indent: 2em)

// List of figures
#outline(
  title: [List of Figures],
  target: figure.where(kind: image)
)

// List of tables
#outline(
  title: [List of Tables],
  target: figure.where(kind: table)
)
```

---

## Tables and Figures

### #table()

**Purpose**: Create tables with rows and columns

**⚠️ CRITICAL**: The `columns` parameter is **REQUIRED**. This is the most common error.

**Signature**:
```typst
#table(
  columns: int | array,        // REQUIRED!
  rows: int | array,
  gutter: length,
  column-gutter: length,
  row-gutter: length,
  fill: color | function,
  align: alignment | array | function,
  stroke: none | length | color | stroke | function,
  inset: length | dictionary | function,
  ...cells: content
)
```

**Key Parameters**:
- `columns`: **REQUIRED**. Column count or widths
  - Integer: `3` (three equal columns)
  - Array: `(1fr, 2fr, 1fr)` (fractional), `(100pt, auto, 1fr)` (mixed)
- `rows`: Row specifications (optional)
- `fill`: Background color
  - Single: `rgb(240, 240, 240)`
  - Function: `(col, row) => if calc.even(row) { gray }` (zebra striping)
- `align`: Cell alignment
  - Single: `center` (all cells)
  - Per-column: `(left, center, right)`
  - Function: `(col, row) => if col == 0 { left } else { right }`
- `stroke`: Border styling
  - `none` — No borders
  - `0.5pt` — Uniform border
  - `1pt + blue` — Colored border
  - `(x: 0pt, y: 0.5pt)` — Horizontal lines only
- `inset`: Cell padding
  - Single: `5pt` (all sides)
  - Dictionary: `(x: 8pt, y: 4pt)`

**Examples**:

*Basic table*:
```typst
#table(
  columns: 3,
  [Header 1], [Header 2], [Header 3],
  [Row 1 Col 1], [Row 1 Col 2], [Row 1 Col 3],
  [Row 2 Col 1], [Row 2 Col 2], [Row 2 Col 3]
)
```

*Styled table with custom widths*:
```typst
#table(
  columns: (1.5fr, 1fr, 1fr),
  stroke: 0.5pt,
  align: (left, center, center),
  inset: 8pt,
  [*Name*], [*Time*], [*Space*],
  [Quick Sort], [O(n log n)], [O(log n)],
  [Merge Sort], [O(n log n)], [O(n)]
)
```

*Zebra striping*:
```typst
#table(
  columns: 3,
  fill: (col, row) => if calc.even(row) { rgb(240, 240, 240) },
  [Header 1], [Header 2], [Header 3],
  [Data 1], [Data 2], [Data 3],
  [Data 4], [Data 5], [Data 6]
)
```

*Header row styling*:
```typst
#table(
  columns: 4,
  fill: (col, row) => if row == 0 { blue } else if calc.even(row) { silver },
  align: (col, row) => if row == 0 { center } else { left },
  stroke: 1pt,
  inset: 6pt,
  table.header([*Col 1*], [*Col 2*], [*Col 3*], [*Col 4*]),
  [Data], [Data], [Data], [Data]
)
```

*Horizontal lines only*:
```typst
#table(
  columns: 3,
  stroke: (x: 0pt, y: 0.5pt),
  [A], [B], [C],
  [1], [2], [3]
)
```

**Common Mistakes**:
- ❌ `#table([A], [B], [C])` — Missing `columns:` parameter
- ✅ `#table(columns: 3, [A], [B], [C])` — Explicit column count
- ❌ Mismatched cells per row
- ✅ Ensure each row has exactly `columns` cells

---

### #figure()

**Purpose**: Create numbered figures with captions

**Signature**:
```typst
#figure(
  body: content,
  caption: content,
  kind: string,
  supplement: string,
  numbering: string,
  gap: length,
  outlined: bool,
  placement: alignment
)
```

**Parameters**:
- `body`: Figure content (image, table, code)
- `caption`: Caption text
- `kind`: Figure type (`"figure"`, `"table"`, `"listing"`, custom)
- `supplement`: Label prefix ("Figure", "Table")
- `placement`: `auto`, `top`, `bottom`

**Examples**:

*Figure with image*:
```typst
#figure(
  image("diagram.png", width: 80%),
  caption: [System architecture overview]
) <fig-arch>

See @fig-arch for details.
```

*Figure with table*:
```typst
#figure(
  table(
    columns: 2,
    [*Property*], [*Value*],
    [Speed], [Fast],
    [Memory], [Low]
  ),
  caption: [Performance comparison],
  kind: "table",
  supplement: "Table"
)
```

*Figure with code*:
```typst
#figure(
  ```python
  def hello():
      print("Hello, World!")
  ```,
  caption: [Hello World in Python],
  kind: "listing",
  supplement: "Listing"
)
```

---

### #image()

**Purpose**: Insert images

**Signature**:
```typst
#image(
  path: string,
  format: string,
  width: length,
  height: length,
  alt: string,
  fit: string
)
```

**Parameters**:
- `path`: File path (relative or absolute)
- `format`: `"png"`, `"jpg"`, `"gif"`, `"svg"` (usually auto-detected)
- `width`, `height`: Dimensions
- `alt`: Alternative text for accessibility
- `fit`: `"cover"`, `"contain"`, `"stretch"`

**Examples**:
```typst
#image("photo.png")
#image("diagram.png", width: 60%)
#image("logo.png", width: 100pt, height: 50pt)
#image("chart.svg", width: 80%, alt: "Sales chart for Q4")
```

---

## Code Blocks

### Triple Backtick Syntax

**Purpose**: Insert code blocks with syntax highlighting

````typst
```language
code here
```
````

**Supported Languages**: `c`, `cpp`, `python`, `java`, `javascript`, `typescript`, `rust`, `go`, `bash`, `sql`, `html`, `css`, `json`, `yaml`, `xml`, `markdown`, `typst`, `typ` (Typst markup), `typc` (Typst code)

**Examples**:

````typst
```python
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```

```c
int main() {
    printf("Hello, World!\n");
    return 0;
}
```
````

---

### #raw()

**Purpose**: Inline or block code with programmatic control

**Signature**:
```typst
#raw(text: string, lang: string, block: bool, align: alignment)
```

**Examples**:
```typst
This is #raw("inline code", lang: "python") within text.

#raw(
  "int x = 5;",
  lang: "c",
  block: true
)
```

---

## Math Mode

### Inline vs Block Math

**Inline math** — no spaces adjacent to `$`:
```typst
The formula $a^2 + b^2 = c^2$ is the Pythagorean theorem.
```

**Block math** — spaces or newlines after opening `$` and before closing `$`:
```typst
$ E = m c^2 $

$ sum_(i=1)^n i = (n(n+1))/2 $
```

---

### Fractions, Exponents, Subscripts

```typst
// Fractions
$a/b$                    // Slash syntax
$frac(a, b)$             // Function syntax
$(x+1)/(y-2)$            // Complex fraction

// Exponents and subscripts
$x^2$                    // Superscript
$x_i$                    // Subscript
$x^2_i$                  // Both
$x_(a + b)$              // Multi-character subscript
$x^(a + b)$              // Multi-character superscript
```

---

### Greek Letters

| Lowercase | Uppercase | Lowercase | Uppercase |
|-----------|-----------|-----------|-----------|
| `alpha` α | `Alpha` Α | `nu` ν | `Nu` Ν |
| `beta` β | `Beta` Β | `xi` ξ | `Xi` Ξ |
| `gamma` γ | `Gamma` Γ | `omicron` ο | `Omicron` Ο |
| `delta` δ | `Delta` Δ | `pi` π | `Pi` Π |
| `epsilon` ε | `Epsilon` Ε | `rho` ρ | `Rho` Ρ |
| `zeta` ζ | `Zeta` Ζ | `sigma` σ | `Sigma` Σ |
| `eta` η | `Eta` Η | `tau` τ | `Tau` Τ |
| `theta` θ | `Theta` Θ | `upsilon` υ | `Upsilon` Υ |
| `iota` ι | `Iota` Ι | `phi` φ | `Phi` Φ |
| `kappa` κ | `Kappa` Κ | `chi` χ | `Chi` Χ |
| `lambda` λ | `Lambda` Λ | `psi` ψ | `Psi` Ψ |
| `mu` μ | `Mu` Μ | `omega` ω | `Omega` Ω |

**Variants**: `epsilon.alt` (ϵ), `theta.alt` (ϑ), `phi.alt` (ϕ), `pi.alt` (ϖ), `sigma.alt` (ς)

---

### Mathematical Symbols

**Operators**:
```typst
$+$, $-$, $times$, $div$, $plus.minus$
$sum$, $product$, $integral$
$union$, $inter$ (intersection)
$subset$, $supset$, $in$, $notin$
```

**Relations**:
```typst
$=$, $!=$, $equiv$, $approx$, $sim$
$<$, $>$, $<=$, $>=$
$subset$, $supset$, $subseteq$, $supseteq$
```

**Arrows**:
```typst
$->$, $<-$, $<->$           // Single arrows
$=>$, $<=$, $<=>$           // Double arrows
$arrow.r$, $arrow.l$        // Explicit naming
$arrow.r.long$              // Long arrow
```

**Miscellaneous**:
```typst
$infinity$, $partial$, $nabla$
$forall$, $exists$
$...$ (ellipsis), $dots.v$ (vertical), $dots.c$ (centered)
```

**Number Sets**: `NN` (ℕ), `ZZ` (ℤ), `QQ` (ℚ), `RR` (ℝ), `CC` (ℂ)

---

### Math Functions

**Built-in operators** (with proper spacing):
```typst
$sin(x)$, $cos(x)$, $tan(x)$
$arcsin(x)$, $arccos(x)$, $arctan(x)$
$log(x)$, $ln(x)$, $exp(x)$
$lim_(x -> 0) f(x)$
$max$, $min$, $sup$, $inf$
$det(A)$, $dim$, $ker$
$gcd$, $lcm$, $mod$
```

**Sums, Products, Integrals**:
```typst
$sum_(i=0)^n i$
$product_(i=1)^n i$
$integral_0^1 f(x) dif x$
$integral.double$, $integral.triple$
$integral.cont$ (contour)
```

**Roots**:
```typst
$sqrt(x)$
$root(3, x)$    // Cube root
$root(n, x)$    // n-th root
```

**Matrices**:
```typst
$mat(a, b; c, d)$                    // 2x2 matrix
$mat(1, 0, 0; 0, 1, 0; 0, 0, 1)$     // 3x3 identity

$vec(x, y, z)$                        // Column vector
$mat(delim: "[", a, b; c, d)$         // Square brackets
$mat(delim: "|", a, b; c, d)$         // Determinant
```

**Cases**:
```typst
$ f(x) := cases(
  1 "if" x > 0,
  0 "if" x = 0,
  -1 "if" x < 0
) $
```

**Accents**:
```typst
$hat(x)$, $tilde(x)$, $bar(x)$
$vec(x)$, $arrow(x)$
$dot(x)$, $dot.double(x)$
$overline(x + y)$, $underline(x)$
```

**Special Functions**:
```typst
$binom(n, k)$       // Binomial coefficient
$abs(x)$            // Absolute value
$norm(x)$           // Norm
$floor(x)$          // Floor
$ceil(x)$           // Ceiling
$cancel(x)$         // Strikethrough
```

---

### Multi-line Equations

Use `\` for line breaks and `&` for alignment points:
```typst
$ sum_(k=0)^n k
    &= 1 + ... + n \
    &= (n(n+1)) / 2 $
```

---

### Equation Numbering

```typst
#set math.equation(numbering: "(1)")

$ phi.alt := (1 + sqrt(5)) / 2 $ <ratio>

See @ratio for the golden ratio.
```

---

### Math Styles

```typst
$cal(A)$      // Calligraphic 𝒜
$bb(R)$       // Blackboard bold ℝ
$frak(A)$     // Fraktur 𝔄
$mono(x)$     // Monospace
$sans(x)$     // Sans-serif
$bold(x)$     // Bold
$italic(x)$   // Italic
$upright(x)$  // Upright
```

---

### Text in Math Mode

Use quotes for regular text:
```typst
$ "area" = pi dot "radius"^2 $
$ f(x) = 1 "if" x > 0 $
```

Access code variables with `#`:
```typst
#let x = 5
$ #x < 17 $
```

---

## Set and Show Rules

### #set

**Purpose**: Apply default settings to all future instances of an element

**Syntax**:
```typst
#set element(parameter: value, ...)
```

**Common Set Rules**:
```typst
#set text(font: "Arial", size: 11pt)
#set par(justify: true, leading: 0.65em)
#set heading(numbering: "1.1")
#set page(paper: "us-letter", margin: 1in)
#set list(marker: [--])
#set enum(numbering: "1.a)")
#set raw(theme: "dark")
#set math.equation(numbering: "(1)")
```

**Scoping** with braces:
```typst
#set text(size: 11pt)

{
  #set text(size: 14pt)
  This is larger text.
}

This is back to 11pt.
```

**Scoping** with brackets:
```typst
#[
  #set text(fill: blue)
  This is blue.
]

This is not blue.
```

---

### #show

**Purpose**: Transform how elements are displayed

**Syntax**:
```typst
#show selector: transformation
```

**Selector Types**:

1. **Element type**:
```typst
#show heading: set text(blue)
#show table: set align(center)
```

2. **String matching**:
```typst
#show "TODO": set text(red, weight: "bold")
#show "FIXME": box(fill: yellow, inset: 2pt)
```

3. **Regex pattern**:
```typst
#show regex("[A-Z]{3,}"): set text(font: "Courier New")
```

4. **Filtered selector** with `.where()`:
```typst
#show heading.where(level: 1): set text(size: 20pt)
#show heading.where(level: 2): set text(size: 16pt)
```

5. **Label selector**:
```typst
#show <important>: set text(red)
This is important. <important>
```

**Transformation Types**:

*Set properties*:
```typst
#show heading: set text(blue)
```

*Custom function*:
```typst
#show heading: it => [
  #set text(size: 18pt, weight: "bold")
  #block(above: 1em, below: 0.5em)[#it.body]
]
```

*Complex transformation*:
```typst
#show heading.where(level: 1): it => {
  set text(size: 20pt, weight: "bold")
  set align(center)
  block(
    width: 100%,
    fill: blue.lighten(80%),
    inset: 10pt,
    radius: 4pt
  )[#it.body]
}
```

**Element Fields** accessible in show rules:

```typst
// Heading fields
#show heading: it => {
  it.body      // Content
  it.level     // Nesting level (1, 2, ...)
  it.numbering // Numbering pattern
}

// Figure fields
#show figure: it => {
  it.body      // Figure content
  it.caption   // Caption
  it.kind      // "image", "table", etc.
}
```

**Common Patterns**:

*Underline headings*:
```typst
#show heading: it => [
  #it
  #v(-0.5em)
  #line(length: 100%, stroke: 0.5pt)
]
```

*Style inline code*:
```typst
#show raw.where(block: false): box.with(
  fill: luma(240),
  inset: (x: 3pt, y: 0pt),
  outset: (y: 3pt),
  radius: 2pt
)
```

*Style block code*:
```typst
#show raw.where(block: true): block.with(
  fill: luma(240),
  inset: 10pt,
  radius: 4pt,
  width: 100%
)
```

*Style links*:
```typst
#show link: set text(fill: blue)
#show link: underline
```

---

## Scripting

### Variables

**Declaration**:
```typst
#let x = 5
#let name = "Alice"
#let items = (1, 2, 3, 4, 5)
#let dict = (name: "Bob", age: 30)
```

**Destructuring**:
```typst
#let (x, y) = (1, 2)
#let (a, .., b) = (1, 2, 3, 4)  // a=1, b=4
#let (_, y, _) = (1, 2, 3)      // Discard with _
```

---

### Conditionals

```typst
#if condition [Content when true] else [Content when false]

#if x > 5 [Large] else [Small]

#if x > 10 [
  Very large
] else if x > 5 [
  Medium
] else [
  Small
]
```

---

### Loops

**For loop**:
```typst
#for item in array [#item, ]

#for i in range(5) [Number #i ]

#for (key, value) in dictionary [
  #key: #value
]
```

**While loop**:
```typst
#let i = 0
#while i < 5 {
  [Item #i ]
  i = i + 1
}
```

**Loop control**: `break`, `continue`

---

### Functions

**Definition**:
```typst
#let greet(name) = [Hello, #name!]
#let add(a, b) = a + b
```

**With default parameters**:
```typst
#let greet(name, greeting: "Hello") = [#greeting, #name!]

#greet("World")                    // Hello, World!
#greet("World", greeting: "Hi")    // Hi, World!
```

**Multi-line function with code block**:
```typst
#let alert(body, fill: red) = {
  set text(white)
  set align(center)
  rect(fill: fill, inset: 8pt, radius: 4pt)[*Warning:* #body]
}
```

---

### Imports

```typst
#import "path/to/file.typ"           // Entire module
#import "file.typ" as mod            // With rename
#import "file.typ": func1, func2     // Specific items
#import "file.typ": *                // All items

#include "chapter.typ"               // Include content directly
```

**Package imports**:
```typst
#import "@preview/package-name:0.1.0": function
```

---

### Context

**Purpose**: Access layout-dependent values (page number, element position)

```typst
#context counter(page).display()
#context counter(page).display("1 of 1", both: true)
#context counter(heading).display()
```

---

### Counter

**Purpose**: Track and display counters

```typst
#counter(page).display()           // Current page
#counter(page).display("i")        // Roman numerals
#counter(page).update(1)           // Reset to 1

#counter(heading).display()        // Current heading number
```

---

## Data Types

### Primitive Types

**Strings**:
```typst
#"hello world!"
#"\"hello\n  world\"!"

// Methods
#"hello".len()              // 5
#"hello".first()            // "h"
#"hello".slice(1, 4)        // "ell"
#"hello world".split(" ")   // ("hello", "world")
#"  hello  ".trim()         // "hello"
#"hello".replace("l", "L")  // "heLLo"
#"hello".contains("ell")    // true
#"hello".starts-with("he")  // true
#"hello".upper()            // "HELLO"
```

Escape sequences: `\\`, `\"`, `\n`, `\r`, `\t`, `\u{1f600}`

**Integers**:
```typst
#42               // Decimal
#0xff             // Hexadecimal (255)
#0o10             // Octal (8)
#0b1001           // Binary (9)
```

**Floats**:
```typst
#3.14
#1e8              // 100000000.0
#float.nan        // Not a Number
#float.inf        // Infinity
```

**Booleans**:
```typst
#true
#false
#(not false)        // true
#(true and false)   // false
#(true or false)    // true
```

---

### Collection Types

**Arrays**:
```typst
#(1, 2, 3)
#("a", "b", "c")
#(1,)                // Single-element (trailing comma required)
#()                  // Empty array

// Indexing
#array.at(0)         // First element
#array.at(-1)        // Last element

// Methods
#(1, 2, 3).len()                    // 3
#(1, 2, 3).first()                  // 1
#(1, 2, 3).last()                   // 3
#(1, 2, 3).push(4)                  // (1, 2, 3, 4)
#(1, 2, 3).pop()                    // (1, 2)
#(1, 2, 3).slice(1, 3)              // (2, 3)
#(1, 2, 3).map(x => x * 2)          // (2, 4, 6)
#(1, 2, 3).filter(x => x > 1)       // (2, 3)
#(1, 2, 3).fold(0, (a, b) => a + b) // 6
#(1, 2, 3).contains(2)              // true
#(3, 1, 2).sorted()                 // (1, 2, 3)
#(1, 2, 3).rev()                    // (3, 2, 1)
#("a", "b", "c").join(", ")         // "a, b, c"
#(1, 2, 3).sum()                    // 6
#(1, 2, 3).enumerate()              // ((0, 1), (1, 2), (2, 3))

// Range creation
#range(5)            // (0, 1, 2, 3, 4)
#range(1, 5)         // (1, 2, 3, 4)
#range(0, 10, 2)     // (0, 2, 4, 6, 8)
```

**Dictionaries**:
```typst
#let dict = (name: "Typst", born: 2019)
#dict.name           // Field access
#dict.at("name")     // Method access
#("name" in dict)    // Check key existence

// Methods
#dict.len()          // 2
#dict.keys()         // ("name", "born")
#dict.values()       // ("Typst", 2019)
#dict.pairs()        // (("name", "Typst"), ("born", 2019))
```

---

### Special Types

**Content**: Document content
```typst
#let greeting = [*Hello!*]
```

**None**: Absence of value
```typst
#none
#if val == none [Value is none]
```

**Auto**: Smart default
```typst
#set page(width: auto)
```

---

### Measurement Types

**Length units**:
```typst
72pt     // Points (1/72 inch)
254mm    // Millimeters
2.54cm   // Centimeters
1in      // Inches
2.5em    // Relative to font size
```

**Relative lengths**:
```typst
50%           // Percentage of container
50% + 2pt     // Combined
```

**Fractions** (for distributing space):
```typst
1fr
2fr
#grid(columns: (1fr, 2fr))  // 1:2 ratio
```

**Angles**:
```typst
90deg    // Degrees
1.57rad  // Radians
```

---

### Color Types

**Named colors**: `black`, `gray`, `silver`, `white`, `navy`, `blue`, `aqua`, `teal`, `eastern`, `purple`, `fuchsia`, `maroon`, `red`, `orange`, `yellow`, `olive`, `green`, `lime`

**Hex colors**:
```typst
#rgb("#ff0000")        // Red
#rgb("#ff000080")      // Red with 50% alpha
#rgb("#f00")           // Shorthand
```

**RGB**:
```typst
#rgb(255, 0, 0)              // Integers 0-255
#rgb(100%, 0%, 0%)           // Percentages
#rgb(255, 0, 0, 128)         // With alpha
```

**Other color spaces**:
```typst
#luma(128)                   // Grayscale
#cmyk(100%, 0%, 0%, 0%)      // CMYK
#color.hsl(30deg, 50%, 60%)  // HSL
#color.hsv(30deg, 50%, 60%)  // HSV
```

**Color methods**:
```typst
#red.lighten(50%)
#blue.darken(30%)
#green.saturate(20%)
#purple.desaturate(20%)
#red.negate()
#blue.transparentize(50%)
#color.mix(red, blue)
```

---

### Type Checking and Conversion

```typst
#type(12)              // int
#type("hello")         // str
#type([Hi])            // content

#int("42")             // 42
#float(42)             // 42.0
#str(10)               // "10"
```

---

## Quick Reference: Most Common Functions

| Function | Purpose | Critical Parameters |
|----------|---------|-------------------|
| `#set page()` | Page setup | `paper`, `margin`, `numbering` |
| `#set text()` | Typography | `font`, `size`, `fill` |
| `#table()` | Tables | **`columns` (REQUIRED)**, `stroke`, `fill` |
| `#columns()` | Multi-column | `count`, `gutter` |
| `#figure()` | Captioned figures | `caption`, `kind` |
| `#set heading()` | Heading config | `numbering` |
| `#show heading:` | Heading styling | — |
| `#set par()` | Paragraph settings | `justify`, `leading` |
| `#grid()` | Grid layout | `columns`, `rows`, `gutter` |
| `#block()` | Block container | `fill`, `stroke`, `inset` |
| `#image()` | Images | `path`, `width` |
| `#link()` | Hyperlinks | `dest`, `body` |

---

## Summary

**Remember**: Always verify syntax with the checklist in SKILL.md before generating code.

**Most common errors**:
1. Using `**bold**` instead of `*bold*`
2. Forgetting `columns:` parameter in `#table()`
3. Using `#` for headings instead of `=`
4. Using braces `{}` instead of brackets `[]` for content arguments
5. Missing units on lengths (`12` vs `12pt`)