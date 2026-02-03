# Typst Document Patterns

## Introduction

This document provides reusable Typst templates for common document types. Each pattern includes:
- **Complete working code** ready to customize
- **Design rationale** explaining WHY specific choices were made
- **Customization points** for adapting to your needs
- **Common variations** for different use cases

**Patterns**:
1. [Academic Paper](#pattern-1-academic-paper)
2. [Cheat Sheet (Dense Multi-Column)](#pattern-2-cheat-sheet-dense-multi-column)
3. [Resume/CV](#pattern-3-resumecv)
4. [Presentation Slides](#pattern-4-presentation-slides)
5. [Technical Report](#pattern-5-technical-report)

---

## Pattern 1: Academic Paper

### Design Rationale

Academic papers require:
- **Two-column layout**: Maximizes text density while maintaining readability (industry standard for conferences)
- **Justified text**: Professional appearance, reduces ragged edges
- **Tight spacing**: Fits more content within page limits (conference papers typically 6-8 pages)
- **Numbered sections**: Easy cross-referencing
- **Abstract box**: Highlights paper summary for quick scanning
- **Figure captions**: Required for academic publishing

**WHY two-column?**
- Studies show 50-75 characters per line is optimal for readability
- Single-column would require narrow margins or result in overly long lines
- Two-column allows normal margins while keeping line length optimal

**WHY justify text?**
- Professional appearance (matches LaTeX output)
- More compact (fewer "rivers" of whitespace)
- Standard in academic publishing

**Trade-offs accepted**:
- Two-column can make tables awkward (use `table.cell(colspan: 2)` to span columns)
- Column breaks sometimes suboptimal (use `#colbreak()` for manual control)
- Harder to scan quickly compared to single-column (but accepted norm in academia)

### Complete Template

```typst
#set page(
  paper: "us-letter",
  margin: 1in
)

#set par(justify: true, leading: 0.65em)
#set heading(numbering: "1.")

// Title and Authors
#align(center)[
  #text(size: 16pt, weight: "bold")[
    Your Paper Title: \
    A Compelling Subtitle
  ]

  #v(0.5em)

  #text(size: 12pt)[
    Author One#super[1], Author Two#super[2], Author Three#super[1]
  ]

  #v(0.3em)

  #text(size: 10pt, style: "italic")[
    #super[1]Department of Computer Science, University A \
    #super[2]Department of Engineering, University B \
    {author1, author3}@university-a.edu, author2@university-b.edu
  ]
]

#v(1em)

// Abstract
#align(center)[
  #text(weight: "bold")[Abstract]
]

#box(width: 100%, inset: (x: 0.75in))[
  This paper presents [your contribution]. We demonstrate that [key result] achieving [performance metric]. Our evaluation shows [main findings]. These results have implications for [broader impact].

  *Keywords*: keyword1, keyword2, keyword3, keyword4
]

#v(1em)

// Two-column layout begins
#columns(2, gutter: 0.3in)[

  = Introduction

  The problem of [X] has received significant attention in recent years. However, existing approaches suffer from [limitations].

  This paper makes the following contributions:
  - Novel [technique/algorithm/approach]
  - Comprehensive evaluation on [workloads/datasets]
  - Demonstration of [X]% improvement over state-of-the-art

  The remainder of this paper is organized as follows. Section 2 reviews related work. Section 3 describes our approach. Section 4 presents evaluation results. Section 5 discusses limitations and future work. Section 6 concludes.

  = Background and Related Work

  == Background on [Topic]

  [Background paragraph explaining necessary concepts]

  == Related Work

  Previous work can be categorized into three approaches:

  *Category 1*: Methods like [cite] and [cite] focus on [approach]. However, they suffer from [limitation].

  *Category 2*: Recent work [cite] proposes [approach]. While promising, this approach [limitation].

  *Category 3*: Our work builds on [cite] but differs in [key difference].

  = System Design

  == Overview

  Our system consists of three main components (Figure 1):
  + [Component 1]: Responsible for [function]
  + [Component 2]: Handles [function]
  + [Component 3]: Manages [function]

  == Component 1: [Name]

  [Detailed description of first component]

  ```python
  def component1_algorithm(input):
      # Process input
      result = process(input)
      return result
  ```

  == Component 2: [Name]

  [Detailed description of second component]

  = Evaluation

  == Experimental Setup

  #figure(
    table(
      columns: (1fr, 2fr),
      stroke: 0.5pt,
      align: (left, left),
      [*Parameter*], [*Value*],
      [CPU], [Intel Xeon E5-2680 v4],
      [Memory], [128 GB DDR4],
      [OS], [Linux 5.15],
      [Workload], [YCSB, TPC-C]
    ),
    caption: [Experimental configuration]
  )

  We evaluate our system using:
  - *Workload A*: [Description]
  - *Workload B*: [Description]

  == Results

  #figure(
    // Placeholder for graph
    box(
      width: 100%,
      height: 150pt,
      fill: gray.lighten(90%),
      stroke: 0.5pt
    )[
      #align(horizon + center)[
        [Performance comparison graph]
      ]
    ],
    caption: [Throughput comparison]
  ) <fig-throughput>

  Figure @fig-throughput shows that our approach achieves 2.3× higher throughput than the baseline.

  = Discussion

  == Implications

  Our results demonstrate that [finding]. This has several implications:

  - *Implication 1*: [Discussion]
  - *Implication 2*: [Discussion]

  == Limitations

  Our work has the following limitations:

  + *Limitation 1*: [Description and impact]
  + *Limitation 2*: [Description and potential solution]

  = Related Work

  [Extended related work section if not already covered]

  = Conclusion

  This paper presented [contribution]. Our evaluation showed [results]. Future work includes [directions].

  Future directions include:
  - Extending to [scenario]
  - Optimizing for [metric]
  - Investigating [question]

  #v(1em)

  *Acknowledgments*: This work was supported by [grant/funding].

  // References
  = References

  [1] Author, A. et al. "Paper Title." Conference, Year.

  [2] Author, B. "Another Paper." Journal, Vol(Issue), Pages, Year.

  [3] Author, C. et al. "Related Work." Conference, Year.

] // End two-column layout
```

### Customization Points

**Conference-specific**:
- Page limit: Adjust content or margins
- Column count: Some use single-column (change `#columns(2)` to `#columns(1)`)
- Font: Some require specific fonts (add `#set text(font: "Times New Roman")`)

**Margin variations**:
```typst
#set page(margin: 0.75in)  // Tighter margins for page limits
#set page(margin: (x: 1in, y: 0.75in))  // Narrow top/bottom
```

**Font size variations**:
```typst
#set text(size: 10pt)  // Smaller for fitting more content
```

---

## Pattern 2: Cheat Sheet (Dense Multi-Column)

### Design Rationale

Cheat sheets optimize for **information density** over aesthetics:

- **Minimal margins (0.3-0.5in)**: Maximize usable space (standard 1in margins waste ~30% of page)
- **Small text (8-9pt)**: Fits 2-3× more content than standard 11-12pt
- **Tight line spacing (0.4-0.5em)**: Reduces vertical whitespace
- **Multiple columns (2-3)**: Prevents eye fatigue from scanning wide lines
- **No paragraph indents**: Saves space, maintains visual clarity with spacing instead
- **Abbreviated content**: Definitions, not full sentences
- **Tables over prose**: Structured data is more scannable

**WHY minimal margins?**
- Cheat sheets are typically not bound (no margin needed for binding)
- Used for quick reference, not extended reading (eye strain less of a concern)
- Single-page constraint makes every square inch valuable

**WHY small text?**
- Users zoom in or hold closer when needed
- Fits critical formulas that would otherwise wrap awkwardly
- Allows 3-column layout on letter size (2 columns only if text ≥10pt)

**WHY multiple columns?**
- 2 columns: 50-60 characters per line (optimal readability even at 9pt)
- 3 columns: More content, but requires 8pt font (harder to read)
- 1 column: Lines too long (90+ characters), harder to scan vertically

**Trade-offs accepted**:
- Hard to read for extended periods (intentional - quick reference only)
- Printing issues if printer can't handle small fonts (recommend PDF viewing)
- Not accessible for vision-impaired users (create separate accessible version if needed)

### Complete Template

```typst
// Dense cheat sheet optimized for maximum information per page
#set page(
  paper: "us-letter",
  margin: 0.4in  // Minimal margins
)

#set text(
  font: "Arial",  // Sans-serif more readable at small sizes
  size: 9pt  // Small but readable
)

#set par(
  leading: 0.45em,  // Tight line spacing
  justify: true,
  first-line-indent: 0pt  // No indents, save space
)

#set heading(numbering: none)  // Numbers waste space

// Heading styles
#show heading.where(level: 1): it => [
  #set text(size: 11pt, weight: "bold")
  #block(above: 0.7em, below: 0.4em, fill: gray.lighten(80%), inset: 3pt)[
    #upper(it.body)
  ]
]

#show heading.where(level: 2): it => [
  #set text(size: 10pt, weight: "bold")
  #block(above: 0.5em, below: 0.3em)[#it.body]
]

#show heading.where(level: 3): it => [
  #set text(size: 9pt, weight: "bold", style: "italic")
  #block(above: 0.3em, below: 0.2em)[#it.body]
]

// Three-column layout for maximum density
#columns(3, gutter: 0.3in)[

  = Section 1

  == Subsection 1.1

  *Term*: Brief definition

  *Formula*: $ f(x) = x^2 $

  *Properties*:
  - Prop 1
  - Prop 2

  === Sub-subsection

  More detail in smaller section.

  #table(
    columns: 2,
    stroke: 0.5pt,
    align: left,
    inset: 3pt,
    [*Key*], [*Value*],
    [A], [Fast],
    [B], [Slow]
  )

  #colbreak()  // Manual column break for control

  = Section 2

  == Subsection 2.1

  *Comparison*:

  #table(
    columns: (1fr, 1fr, 1fr),
    stroke: 0.5pt,
    align: center,
    inset: 3pt,
    [*Method*], [*Time*], [*Space*],
    [M1], [O(n)], [O(1)],
    [M2], [O(n²)], [O(n)]
  )

  *Key Points*:
  - Point 1: Detail
  - Point 2: Detail

  == Subsection 2.2

  ```
  Algorithm:
  1. Step one
  2. Step two
  3. Return result
  ```

  *Complexity*: $O(n log n)$

  #colbreak()

  = Section 3

  == Quick Reference

  *Important formulas*:

  $ a^2 + b^2 = c^2 $

  $ E = m c^2 $

  $ F = m a $

  *Constants*:
  - $pi approx 3.14159$
  - $e approx 2.71828$

  == Symbols

  #table(
    columns: 2,
    stroke: 0.5pt,
    inset: 2pt,
    [$alpha$], [Alpha],
    [$beta$], [Beta],
    [$gamma$], [Gamma],
    [$delta$], [Delta]
  )

] // End columns
```

### Customization Points

**For even more density (exam with formulas)**:
```typst
#set page(margin: 0.25in)
#set text(size: 8pt)
#set par(leading: 0.35em)
#columns(4, gutter: 0.2in)  // Four columns!
```

**For better readability (study guide)**:
```typst
#set page(margin: 0.5in)
#set text(size: 10pt)
#set par(leading: 0.55em)
#columns(2, gutter: 0.5in)  // Two columns
```

**Color coding sections** (if printing in color):
```typst
#show heading.where(level: 1): it => [
  #block(
    fill: blue.lighten(85%),
    inset: 3pt,
    width: 100%
  )[
    #text(fill: blue.darken(40%))[*#it.body*]
  ]
]
```

---

## Pattern 3: Resume/CV

### Design Rationale

Resumes optimize for **scannability** by recruiters (6-second initial scan):

- **Clean, minimal design**: No distractions from content
- **Clear section headers**: Bold, larger text for rapid navigation
- **Consistent formatting**: Same pattern for all entries (Title • Company • Date)
- **Bullet points over paragraphs**: Easier to scan vertically
- **Action verbs**: "Implemented" not "Was responsible for implementing"
- **Quantified achievements**: Numbers stand out in scanning
- **No photos/graphics**: ATS (Applicant Tracking Systems) can't parse them
- **Standard fonts**: Arial, Calibri, Times (ATS compatibility)

**WHY single column?**
- Two-column can confuse ATS parsing order
- Recruiters scan top-to-bottom, left-to-right (single column is natural)
- Easier to extract sections programmatically

**WHY minimal styling?**
- Fancy designs reduce ATS parsing accuracy
- Content matters more than aesthetics
- Printing/PDF conversion issues with complex layouts

**WHY reverse chronological?**
- Most recent = most relevant (industry standard)
- Recruiters expect this format
- Shows career progression

**Trade-offs accepted**:
- Less visually distinctive (but safer for ATS)
- Less space efficient than two-column (but more important to parse correctly)
- Repetitive structure (but consistency aids scanning)

### Complete Template

```typst
#set page(
  paper: "us-letter",
  margin: (x: 0.75in, y: 0.75in)
)

#set text(
  font: "Arial",
  size: 11pt
)

#set par(justify: false)  // Left-aligned for scannability

// Helper function for job entries
#let job(title, company, location, dates, items) = {
  block(above: 0.8em, below: 0.5em)[
    #grid(
      columns: (1fr, auto),
      [*#title* #h(0.5em) • #h(0.5em) _#company_],
      [#dates]
    )
    #text(size: 10pt, style: "italic")[#location]

    #for item in items [
      - #item
    ]
  ]
}

// Header
#align(center)[
  #text(size: 20pt, weight: "bold")[Your Name]

  #v(0.3em)

  #text(size: 10pt)[
    your.email@example.com • (555) 123-4567 • linkedin.com/in/yourprofile • github.com/yourusername
  ]

  #v(0.2em)

  #text(size: 10pt)[
    City, State • Available for relocation
  ]
]

#v(0.5em)
#line(length: 100%, stroke: 1pt)

// Education
#v(0.5em)
#text(size: 13pt, weight: "bold")[EDUCATION]
#v(0.3em)

#grid(
  columns: (1fr, auto),
  [*Bachelor of Science in Computer Science*],
  [Expected May 2025]
)
_University Name_, City, State
- GPA: 3.85/4.0
- Relevant Coursework: Operating Systems, Algorithms, Database Systems, Computer Networks
- Honors: Dean's List (Fall 2023, Spring 2024)

// Experience
#v(0.5em)
#line(length: 100%, stroke: 0.5pt)
#v(0.5em)
#text(size: 13pt, weight: "bold")[EXPERIENCE]
#v(0.3em)

#job(
  "Software Engineering Intern",
  "Tech Company Inc.",
  "San Francisco, CA",
  "June 2024 - Aug 2024",
  (
    [Developed RESTful API endpoints serving 10M+ requests/day using Python and FastAPI, reducing average response time by 35%],
    [Implemented caching layer with Redis, improving cache hit ratio from 45% to 82%],
    [Collaborated with 5-person team using Agit, conducting code reviews and pair programming sessions],
    [Wrote comprehensive unit tests achieving 95% code coverage using pytest]
  )
)

#job(
  "Research Assistant",
  "University CS Department",
  "City, State",
  "Jan 2024 - Present",
  (
    [Analyzing CPU scheduling algorithms for real-time systems under Professor Smith],
    [Developed simulation framework in C++ to evaluate FCFS, SJF, and Round Robin algorithms],
    [Presented findings at Undergraduate Research Symposium (April 2024)],
    [Co-authoring paper on adaptive scheduling for submission to RTAS conference]
  )
)

#job(
  "Teaching Assistant - CS 537: Operating Systems",
  "University Name",
  "City, State",
  "Sep 2023 - Dec 2023",
  (
    [Held weekly office hours helping 30+ students with concepts in process management, memory allocation, and synchronization],
    [Graded assignments and exams for class of 150 students],
    [Created supplemental tutorial materials on deadlock prevention algorithms]
  )
)

// Projects
#v(0.5em)
#line(length: 100%, stroke: 0.5pt)
#v(0.5em)
#text(size: 13pt, weight: "bold")[PROJECTS]
#v(0.3em)

*Custom Shell Implementation* • C, Linux
- Built Unix-like shell supporting pipes, I/O redirection, and background processes
- Implemented job control (fg, bg, jobs commands) and signal handling
- Handled edge cases including zombie process prevention and proper signal propagation

*Distributed Key-Value Store* • Go, Docker
- Designed and implemented distributed KV store with consistent hashing and replication
- Achieved 50,000 reads/sec and 30,000 writes/sec in benchmarks
- Implemented Raft consensus algorithm for leader election and log replication

*Thread-Safe Memory Allocator* • C
- Developed custom malloc/free implementation with thread safety using mutexes
- Reduced fragmentation by 40% compared to baseline using best-fit allocation
- Optimized for multi-threaded workloads with per-thread caching

// Skills
#v(0.5em)
#line(length: 100%, stroke: 0.5pt)
#v(0.5em)
#text(size: 13pt, weight: "bold")[SKILLS]
#v(0.3em)

*Languages*: C, C++, Python, Go, Java, SQL, Bash \
*Technologies*: Linux, Git, Docker, Kubernetes, Redis, PostgreSQL, FastAPI \
*Concepts*: Operating Systems, Algorithms, Distributed Systems, Concurrency, Networking
```

### Customization Points

**For experienced professionals** (more work experience, less education):
```typst
// Move Education to bottom
// Add more job entries
// Remove GPA if >3 years out of school
```

**For international positions**:
```typst
// Replace "City, State" with "City, Country"
// Add work authorization status
// Include languages spoken
```

**For academic CV** (research-focused):
```typst
// Add Publications section
// Add Conferences section
// Expand Research Experience
// Include Academic Honors/Awards
```

---

## Pattern 4: Presentation Slides

### Design Rationale

Presentation slides prioritize **visual clarity** for projection:

- **Large text (18-36pt)**: Readable from back of room (rule: 1pt per foot of distance)
- **Minimal bullet points**: 3-5 per slide maximum (audience can't read and listen simultaneously)
- **High contrast**: Black on white or white on black (avoid color combinations like red/green)
- **Generous whitespace**: Reduces cognitive load, focuses attention
- **One idea per slide**: Better than cramming multiple topics
- **Visual hierarchy**: Title >> main points >> supporting details

**WHY large text?**
- Projectors reduce apparent size by 30-50%
- Audience distance: 10-30 feet typical (requires 18pt minimum)
- Older audience may have reduced vision (play it safe)

**WHY minimal text?**
- Slides are prompts, not documentation
- Audience reads faster than you speak (creates awkward silence or reading while you're talking)
- Details belong in handouts, not slides

**WHY high contrast?**
- Projectors have lower contrast than monitors
- Room lighting reduces effective contrast further
- Color blindness affects 8% of men, 0.5% of women

**Trade-offs accepted**:
- Less information per slide (requires more slides, but better retention)
- Not useful as standalone document (create separate handout)
- Requires more preparation (can't just read bullet points)

### Complete Template

```typst
#set page(
  paper: "presentation-16-9",  // Widescreen (standard for modern projectors)
  margin: (x: 1in, y: 0.75in)
)

#set text(
  size: 20pt,  // Base text size
  font: "Arial"
)

// Title Slide
#align(horizon + center)[
  #text(size: 44pt, weight: "bold")[
    Your Presentation Title
  ]

  #v(1em)

  #text(size: 28pt)[
    Subtitle or Context
  ]

  #v(2em)

  #text(size: 24pt)[
    Your Name
  ]

  #v(0.5em)

  #text(size: 20pt)[
    Organization • Event • Date
  ]
]

#pagebreak()

// Agenda Slide
#block(above: 0em)[
  #text(size: 32pt, weight: "bold")[Agenda]
]

#v(1.5em)

#text(size: 24pt)[
  + Introduction and Motivation
  + Background
  + Our Approach
  + Evaluation Results
  + Conclusion and Future Work
]

#pagebreak()

// Content Slide - Bullet Points
#block(above: 0em)[
  #text(size: 32pt, weight: "bold")[Problem Statement]
]

#v(1.5em)

#text(size: 22pt)[
  Current systems face three key challenges:

  #v(0.8em)

  + *Scalability*: Cannot handle >10,000 requests/sec
    #v(0.3em)
  + *Latency*: Average response time >500ms
    #v(0.3em)
  + *Cost*: Hardware costs exceed \$100K/year

  #v(1em)

  → Need better approach
]

#pagebreak()

// Content Slide - Two Column
#block(above: 0em)[
  #text(size: 32pt, weight: "bold")[Comparison: Before vs. After]
]

#v(1em)

#grid(
  columns: (1fr, 1fr),
  gutter: 1in,
  [
    #align(center)[
      #text(size: 26pt, fill: red.darken(20%), weight: "bold")[
        Before
      ]
    ]

    #v(0.5em)

    #text(size: 20pt)[
      - Manual configuration
      - Hours of setup time
      - Error-prone
      - Not reproducible
    ]
  ],
  [
    #align(center)[
      #text(size: 26pt, fill: green.darken(20%), weight: "bold")[
        After
      ]
    ]

    #v(0.5em)

    #text(size: 20pt)[
      - Automated deployment
      - Minutes to deploy
      - Validated configs
      - Version controlled
    ]
  ]
)

#pagebreak()

// Content Slide - Image Placeholder
#block(above: 0em)[
  #text(size: 32pt, weight: "bold")[System Architecture]
]

#v(0.5em)

#align(center)[
  #box(
    width: 90%,
    height: 65%,
    fill: gray.lighten(90%),
    stroke: 1pt,
    radius: 4pt
  )[
    #align(horizon + center)[
      #text(size: 18pt, style: "italic")[
        [Architecture diagram would go here]

        #v(0.5em)

        Client → Load Balancer → Servers → Database
      ]
    ]
  ]
]

#pagebreak()

// Results Slide - Big Number
#block(above: 0em)[
  #text(size: 32pt, weight: "bold")[Key Result]
]

#v(2em)

#align(center)[
  #text(size: 72pt, weight: "bold", fill: blue.darken(20%))[
    3.2×
  ]

  #v(0.5em)

  #text(size: 28pt)[
    Faster than baseline
  ]

  #v(1em)

  #text(size: 20pt, style: "italic")[
    (measured across 10,000 requests)
  ]
]

#pagebreak()

// Table Slide
#block(above: 0em)[
  #text(size: 32pt, weight: "bold")[Performance Comparison]
]

#v(1em)

#align(center)[
  #table(
    columns: (1.5fr, 1fr, 1fr, 1fr),
    stroke: 1pt,
    align: (left, center, center, center),
    inset: 10pt,

    table.header(
      [*System*],
      [*Throughput*],
      [*Latency*],
      [*Cost*]
    ),

    [Baseline], [10K/s], [500ms], [\$100K],
    [Approach A], [25K/s], [200ms], [\$80K],
    [*Our Approach*], [*32K/s*], [*150ms*], [*\$60K*]
  )
]

#v(0.5em)

#text(size: 18pt, style: "italic")[
  * Bold = best in category
]

#pagebreak()

// Conclusion Slide
#block(above: 0em)[
  #text(size: 32pt, weight: "bold")[Conclusion]
]

#v(1.5em)

#text(size: 24pt)[
  *Key Takeaways*:

  #v(1em)

  + Achieved 3.2× performance improvement
  + Reduced costs by 40%
  + Demonstrated scalability to 100K+ requests/sec

  #v(2em)

  *Future Work*: Extend to distributed scenarios
]

#pagebreak()

// Questions Slide
#align(horizon + center)[
  #text(size: 52pt, weight: "bold")[
    Questions?
  ]

  #v(2em)

  #text(size: 24pt)[
    your.email@example.com \
    github.com/yourusername
  ]
]
```

### Customization Points

**For dark background** (better for dark rooms):
```typst
#set page(fill: black)
#set text(fill: white)
```

**For 4:3 aspect ratio** (older projectors):
```typst
#set page(paper: "presentation-4-3")
```

**For accessibility** (high contrast):
```typst
#set page(fill: black)
#set text(fill: white, size: 24pt)  // Larger base size
```

---

## Pattern 5: Technical Report

### Design Rationale

Technical reports balance **professional appearance** with **detailed content**:

- **Single column**: Easier to read tables, code, and detailed text
- **Numbered sections**: Required for referencing ("see Section 3.2")
- **Page numbers**: Essential for multi-page documents
- **Headers/footers**: Context on every page (document title, section)
- **Generous margins**: Allows binding, annotations
- **Figures and tables**: Numbered for cross-referencing
- **Table of contents**: Navigation for long documents (>10 pages)

**WHY single column?**
- Technical details (code, complex tables) don't fit well in narrow columns
- Reports are read sequentially, not scanned (unlike cheat sheets)
- Standard for industry/government reports (reader expectation)

**WHY numbered sections?**
- Enables precise references ("Section 3.2.1 describes the algorithm")
- Required for formal documents (RFPs, specifications, standards)
- Easier to discuss in meetings ("Let's review Section 4")

**WHY table of contents?**
- Long documents (20+ pages) need navigation
- Helps readers skip to relevant sections
- Professional appearance (matches LaTeX/Word conventions)

**Trade-offs accepted**:
- Less space-efficient than two-column (but readability is priority)
- More pages (but comprehensiveness is valued)
- Slower to scan than cheat sheet (but not designed for quick reference)

### Complete Template

```typst
#set page(
  paper: "us-letter",
  margin: (left: 1.25in, right: 1in, top: 1in, bottom: 1in),
  numbering: "1",
  number-align: center,
  header: locate(loc => {
    if counter(page).at(loc).first() > 1 [
      #set text(size: 10pt, style: "italic")
      Technical Report: System Design Document
      #h(1fr)
      #datetime.today().display()
    ]
  }),
  footer: locate(loc => {
    if counter(page).at(loc).first() > 1 [
      #line(length: 100%, stroke: 0.5pt)
      #set text(size: 10pt)
      #h(1fr)
      Confidential - Internal Use Only
      #h(1fr)
    ]
  })
)

#set text(
  font: "Arial",
  size: 11pt
)

#set par(
  justify: true,
  leading: 0.65em,
  first-line-indent: 0pt
)

#set heading(numbering: "1.1")

// Title Page
#align(center + horizon)[
  #text(size: 24pt, weight: "bold")[
    System Design Document: \
    Distributed Task Scheduler
  ]

  #v(2em)

  #text(size: 14pt)[
    Version 1.0
  ]

  #v(1em)

  #text(size: 12pt)[
    Prepared by: Engineering Team \
    Date: #datetime.today().display() \
    Status: Draft for Review
  ]

  #v(3em)

  #text(size: 10pt, style: "italic")[
    CONFIDENTIAL \
    Internal Use Only
  ]
]

#pagebreak()

// Table of Contents
#outline(
  title: [Table of Contents],
  indent: auto
)

#pagebreak()

// Executive Summary
= Executive Summary

This document describes the design of a distributed task scheduler capable of handling 100,000+ tasks per second with high availability guarantees.

*Key Features*:
- Horizontal scalability via consistent hashing
- Fault tolerance through replication
- Priority-based scheduling
- Real-time monitoring and alerting

*Target Performance*:
- Throughput: >100K tasks/sec
- Latency: P99 < 100ms
- Availability: 99.99% uptime

#pagebreak()

= Introduction

== Background

Current task scheduling systems face scalability limitations beyond 10,000 tasks/sec. This design addresses these limitations through distributed architecture.

== Scope

This document covers:
- System architecture and components
- Data models and APIs
- Scalability and fault tolerance mechanisms
- Deployment and operational considerations

Out of scope:
- Implementation details (see separate implementation spec)
- Detailed performance tuning
- Client SDK design

== Definitions

#table(
  columns: (1fr, 3fr),
  stroke: 0.5pt,
  align: (left, left),
  inset: 8pt,
  [*Term*], [*Definition*],
  [Task], [Unit of work to be scheduled and executed],
  [Worker], [Process that executes tasks],
  [Scheduler], [Component that assigns tasks to workers],
  [Queue], [Ordered collection of pending tasks]
)

= System Architecture

== Overview

The system consists of four main components (Figure 1):

#figure(
  box(
    width: 100%,
    height: 200pt,
    fill: gray.lighten(95%),
    stroke: 1pt,
    radius: 2pt
  )[
    #align(horizon + center)[
      #text(size: 10pt, style: "italic")[
        [System architecture diagram: API Gateway → Scheduler → Workers → Storage]
      ]
    ]
  ],
  caption: [High-level system architecture]
) <fig-architecture>

As shown in @fig-architecture, requests flow from the API Gateway through the Scheduler to available Workers.

== Components

=== API Gateway

*Responsibility*: Accept task submissions and queries

*Key Features*:
- REST API for task submission
- Authentication and authorization
- Rate limiting (per-user quotas)
- Request validation

*Technology*: Go, gRPC

=== Scheduler

*Responsibility*: Assign tasks to workers based on priority and capacity

*Algorithm*:
```
1. Receive task from queue
2. Check worker capacity
3. If capacity available:
     Assign task to worker
     Update worker state
   Else:
     Re-queue task with backoff
4. Monitor task progress
5. Handle task completion or failure
```

*Scaling*: Horizontal via consistent hashing on task ID

=== Worker Pool

*Responsibility*: Execute assigned tasks

*Characteristics*:
- Stateless (can scale horizontally)
- Heartbeat to scheduler every 5 seconds
- Graceful shutdown (finish in-progress tasks)

=== Storage Layer

*Responsibility*: Persist task metadata and results

*Components*:
- PostgreSQL: Task metadata, scheduling state
- Redis: Task queue, worker registry
- S3: Large task artifacts

= Data Models

== Task Schema

#figure(
  table(
    columns: (1fr, 1fr, 2fr),
    stroke: 0.5pt,
    align: (left, left, left),
    inset: 6pt,
    [*Field*], [*Type*], [*Description*],
    [task_id], [UUID], [Unique identifier],
    [priority], [int], [1-10, higher = more urgent],
    [created_at], [timestamp], [Submission time],
    [scheduled_at], [timestamp], [Scheduled execution time],
    [status], [enum], [pending, running, completed, failed],
    [payload], [json], [Task-specific data],
    [result], [json], [Execution result (when complete)]
  ),
  caption: [Task table schema]
)

= Performance Analysis

== Scalability

#figure(
  table(
    columns: (1fr, 1fr, 1fr, 1fr),
    stroke: 0.5pt,
    align: (left, center, center, center),
    inset: 8pt,
    [*Configuration*], [*Workers*], [*Throughput*], [*P99 Latency*],
    [Small], [10], [25K/s], [80ms],
    [Medium], [50], [100K/s], [95ms],
    [Large], [200], [350K/s], [105ms]
  ),
  caption: [Scalability test results]
)

The system scales near-linearly up to 200 workers. Beyond this point, scheduler becomes bottleneck (requires sharding).

= Deployment

== Infrastructure Requirements

*Production Environment*:
- 3× Scheduler instances (m5.xlarge)
- 50× Worker instances (c5.2xlarge)
- 1× PostgreSQL RDS (db.r5.2xlarge, Multi-AZ)
- Redis cluster (3 nodes, r5.xlarge)

*Estimated Monthly Cost*: \$15,000

= Conclusion

This design provides a scalable, fault-tolerant task scheduler meeting performance requirements. Next steps include prototype implementation and load testing.

= Appendix A: API Reference

== Submit Task

*Endpoint*: `POST /api/v1/tasks`

*Request Body*:
```json
{
  "priority": 5,
  "scheduled_at": "2024-10-20T10:00:00Z",
  "payload": { ... }
}
```

*Response*:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending"
}
```
```

### Customization Points

**For internal docs** (less formal):
```typst
// Remove headers/footers
// Remove "Confidential" markings
// Reduce margin formality
```

**For external deliverables** (more formal):
```typst
// Add company logo to title page
// Add approval/signature section
// Add revision history table
```

**For standards documents**:
```typst
// Deeper section numbering (1.1.1.1)
// More rigid structure (must-have sections)
// Normative language (SHALL, SHOULD, MAY)
```

---

## Summary

These patterns provide starting points for common document types. Key principles across all patterns:

**Design Decisions Should Be Intentional**:
- Every margin, font size, and spacing choice serves a purpose
- Trade-offs are explicitly acknowledged
- Rationale documented for future reference

**Context Determines Design**:
- Cheat sheet optimizes for density (exam constraints)
- Resume optimizes for scannability (recruiter behavior)
- Slides optimize for projection (room size, lighting)
- Reports optimize for comprehensiveness (reference use)

**Customize Based on Requirements**:
- Page limits → adjust margins/font size
- ATS compatibility → simplify formatting
- Accessibility → increase contrast/size
- Printing → avoid small fonts/low contrast

For more examples, see examples.md. For syntax details, see syntax-reference.md.
