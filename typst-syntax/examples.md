# Typst Examples Library

## Introduction

This document provides 20+ working Typst examples across diverse use cases. Each example includes:
- **Description**: What the example demonstrates
- **Complete code**: Full, working Typst code
- **Key techniques**: Important syntax or patterns used
- **Use cases**: When to use this pattern

**Categories**:
- [Basic Documents](#basic-documents)
- [Academic Documents](#academic-documents)
- [Cheat Sheets](#cheat-sheets)
- [Presentations](#presentations)
- [Technical Documentation](#technical-documentation)

---

## Basic Documents

### Example 1: Simple Article

**Description**: Basic article with headings, paragraphs, emphasis, and lists

**Code**:
```typst
= Introduction to Operating Systems

An *operating system* (OS) is _essential software_ that manages computer hardware and software resources.

== Key Functions

The operating system provides several critical functions:

- *Process Management*: Scheduling and managing running programs
- *Memory Management*: Allocating and deallocating memory
- *File System Management*: Organizing and accessing data on storage
- *I/O Device Management*: Coordinating communication with hardware

== Types of Operating Systems

+ *Batch Systems*: Process jobs in batches without user interaction
+ *Time-Sharing Systems*: Multiple users share CPU time
+ *Real-Time Systems*: Guarantee response within time constraints
+ *Distributed Systems*: Coordinate multiple computers

The OS acts as an _intermediary_ between applications and hardware, providing *abstraction* and *protection*.
```

**Key Techniques**:
- Heading levels with `=` and `==`
- Bold (`*bold*`) and italic (`_italic_`)
- Unordered lists with `-`
- Ordered lists with `+`

**Use Cases**: Blog posts, documentation, simple reports

---

### Example 2: Multi-Section Document

**Description**: Document with multiple sections, subsections, and paragraph formatting

**Code**:
```typst
#set page(paper: "us-letter", margin: 1in)
#set text(font: "Times New Roman", size: 12pt)
#set par(justify: true, first-line-indent: 0.5in)

= Chapter 1: Memory Management

== Introduction

Memory management is one of the most important functions of an operating system. The OS must keep track of which parts of memory are in use and which are free.

== Paging

Paging is a memory management scheme that eliminates the need for contiguous allocation of physical memory. The operating system divides physical memory into fixed-sized blocks called _frames_ and divides logical memory into blocks of the same size called _pages_.

When a program is executed, its pages are loaded into available memory frames. This approach has several advantages:

- Eliminates external fragmentation
- Allows programs larger than physical memory
- Enables sharing of memory between processes
- Simplifies memory allocation

== Segmentation

Segmentation is a memory management technique that divides memory into variable-sized segments based on the logical divisions of a program. Unlike paging, segmentation supports the user's view of memory.

#v(1em)

Common segments include:
+ Code segment
+ Data segment
+ Stack segment
+ Heap segment
```

**Key Techniques**:
- Document setup with `#set page()` and `#set text()`
- Justified paragraphs with first-line indent
- Vertical spacing with `#v()`
- Multiple heading levels

**Use Cases**: Essays, chapters, technical writing

---

### Example 3: Document with Links and References

**Description**: Document with internal references and external links

**Code**:
```typst
#set heading(numbering: "1.1")

= Introduction <intro>

This document discusses CPU scheduling algorithms. For more details, see the official documentation at https://typst.app/docs/

= Background <background>

As mentioned in @intro, CPU scheduling is critical for system performance.

== First-Come, First-Served <fcfs>

FCFS is the simplest scheduling algorithm.

== Shortest Job First <sjf>

SJF provides optimal average waiting time.

= Comparison

The FCFS algorithm (@fcfs) is simpler than SJF (@sjf), but SJF performs better.

For more information, visit #link("https://typst.app")[the Typst website].

= References

- See @background for context
- See @intro for overview
```

**Key Techniques**:
- Labels with `<label-name>`
- References with `@label-name`
- Automatic numbering with `#set heading(numbering: "1.1")`
- External links with `#link()`

**Use Cases**: Technical documents with cross-references, manuals

---

### Example 4: Document with Table of Contents

**Description**: Document with automatic table of contents

**Code**:
```typst
#set heading(numbering: "1.")
#set page(numbering: "1")

#align(center)[
  #text(size: 18pt, weight: "bold")[
    Operating Systems Concepts
  ]
]

#v(2em)

#outline(
  title: [Table of Contents],
  indent: auto
)

#pagebreak()

= Introduction

This document covers key operating system concepts.

= Process Management

== Process States

Processes can be in one of several states: new, ready, running, waiting, or terminated.

== Process Scheduling

The OS uses scheduling algorithms to determine which process runs next.

= Memory Management

== Paging

Paging divides memory into fixed-size frames.

== Segmentation

Segmentation uses variable-size memory segments.

= Conclusion

Understanding these concepts is essential for OS development.
```

**Key Techniques**:
- `#outline()` for automatic table of contents
- `#pagebreak()` to start new page
- `#align(center)` for centered title
- Automatic heading numbering

**Use Cases**: Reports, manuals, documentation with navigation

---

## Academic Documents

### Example 5: Research Paper with Abstract

**Description**: Academic paper format with title, authors, abstract, and two-column layout

**Code**:
```typst
#set page(paper: "us-letter", margin: 1in)
#set par(justify: true)

#align(center)[
  #text(size: 16pt, weight: "bold")[
    Efficient Page Replacement Algorithms: \
    A Comparative Study
  ]

  #v(0.5em)

  #text(size: 12pt)[
    Jane Smith#super[1], John Doe#super[2]
  ]

  #v(0.3em)

  #text(size: 10pt, style: "italic")[
    #super[1]Department of Computer Science, University A \
    #super[2]Department of Engineering, University B
  ]
]

#v(1em)

#align(center)[
  #text(weight: "bold")[Abstract]
]

#box(width: 100%, inset: (x: 1in))[
  This paper presents a comprehensive comparison of page replacement algorithms including FIFO, LRU, and Clock. We evaluate their performance across various workloads and demonstrate that LRU provides superior performance in most scenarios, with only 12% overhead compared to the optimal algorithm.
]

#v(1em)

#set heading(numbering: "1.")

#columns(2, gutter: 0.3in)[
  = Introduction

  Page replacement is a critical component of virtual memory systems. When physical memory is full, the operating system must select a page to evict.

  This paper compares three algorithms: First-In-First-Out (FIFO), Least Recently Used (LRU), and Clock.

  = Related Work

  Previous studies @belady1966 have established the theoretical foundations of page replacement. Our work builds on this foundation with modern workload analysis.

  = Methodology

  We implemented three algorithms and tested them with:
  - Database workloads
  - Web server traffic
  - Scientific computing applications

  Each workload was run for 1000 simulated seconds.

  = Results

  #figure(
    table(
      columns: 3,
      [*Algorithm*], [*Avg Faults*], [*Overhead*],
      [FIFO], [342], [Low],
      [LRU], [187], [Medium],
      [Clock], [215], [Low]
    ),
    caption: [Page fault comparison]
  )

  LRU achieved the lowest fault rate (187 faults) but required additional bookkeeping.

  = Conclusion

  Our results demonstrate that LRU provides the best performance for most workloads, justifying its overhead.

  Future work will explore adaptive algorithms that adjust based on workload characteristics.

  = References

  [1] Belady, L. A. (1966). A study of replacement algorithms for virtual storage.
]
```

**Key Techniques**:
- Centered title and authors with superscript affiliations
- Abstract in indented box
- Two-column layout with `#columns()`
- Figure with table
- Academic formatting

**Use Cases**: Research papers, conference submissions, academic articles

---

### Example 6: Lab Report

**Description**: Lab report with sections, data tables, and observations

**Code**:
```typst
#set page(paper: "us-letter", margin: 1in, numbering: "1")
#set par(justify: true, leading: 0.65em)
#set heading(numbering: "1.1")

#align(center)[
  #text(size: 16pt, weight: "bold")[
    Lab Report: CPU Scheduling Simulation
  ]
  #v(0.5em)
  Alice Johnson \
  CS 433 - Operating Systems \
  October 15, 2024
]

#v(2em)

= Objective

The objective of this lab is to implement and compare FCFS and SJF CPU scheduling algorithms.

= Materials and Methods

== Implementation

We implemented both algorithms in Python and simulated 5 processes with varying burst times.

== Test Data

#figure(
  table(
    columns: 3,
    stroke: 0.5pt,
    [*Process*], [*Arrival*], [*Burst Time*],
    [P1], [0], [6],
    [P2], [2], [8],
    [P3], [4], [7],
    [P4], [6], [3],
    [P5], [8], [4]
  ),
  caption: [Process characteristics]
)

= Results

== FCFS Results

Average waiting time: *13.2 ms* \
Average turnaround time: *18.8 ms*

== SJF Results

Average waiting time: *8.6 ms* \
Average turnaround time: *14.2 ms*

= Discussion

SJF achieved 35% lower average waiting time compared to FCFS. This aligns with theoretical predictions that SJF minimizes average waiting time.

However, SJF requires knowledge of burst times in advance, which is often unavailable in real systems.

= Conclusion

This lab demonstrated that SJF outperforms FCFS in terms of average waiting time, but has practical limitations. Future experiments should explore predictive models for burst time estimation.

= Code Appendix

```python
def fcfs_schedule(processes):
    time = 0
    for p in sorted(processes, key=lambda x: x.arrival):
        wait = max(0, time - p.arrival)
        time += p.burst
        yield (p.id, wait)
\```
```

**Key Techniques**:
- Title page with metadata
- Hierarchical numbering
- Data tables with borders
- Code appendix
- Academic lab format

**Use Cases**: Lab reports, experiment documentation, academic assignments

---

### Example 7: Homework Assignment

**Description**: Homework problem set with numbered questions and solutions

**Code**:
```typst
#set page(paper: "us-letter", margin: 1in)
#set par(justify: true)

#align(center)[
  #text(size: 14pt, weight: "bold")[
    CS 537: Homework 3 - Synchronization
  ]
  Student: Bob Chen \
  Due: October 20, 2024
]

#v(1em)

*Problem 1*: Explain the critical section problem.

_Solution_: The critical section problem involves designing a protocol to ensure that when one process is executing in its critical section, no other process can enter its critical section. A solution must satisfy:
- Mutual exclusion
- Progress
- Bounded waiting

#v(0.5em)

*Problem 2*: Implement Peterson's solution for two processes.

_Solution_:

```c
// Shared variables
int turn;
bool flag[2];

// Process i
flag[i] = true;
turn = j;
while (flag[j] && turn == j);
// Critical section
flag[i] = false;
\```

This solution meets all three requirements. Mutual exclusion is ensured because both processes cannot be in their critical sections simultaneously when both flags are true.

#v(0.5em)

*Problem 3*: Given processes with the following semaphore operations, determine if deadlock is possible:

#table(
  columns: 2,
  stroke: 0.5pt,
  [*Process A*], [*Process B*],
  [`wait(S1)`], [`wait(S2)`],
  [`wait(S2)`], [`wait(S1)`],
  [`signal(S2)`], [`signal(S1)`],
  [`signal(S1)`], [`signal(S2)`]
)

_Solution_: Yes, deadlock is possible. If Process A acquires S1 and Process B acquires S2 simultaneously, both will be blocked waiting for each other's semaphore.

*Deadlock condition*: A holds S1, waits for S2; B holds S2, waits for S1.

*Prevention*: Impose ordering on semaphore acquisition (both acquire S1 before S2).
```

**Key Techniques**:
- Numbered problems with solutions
- Code blocks for algorithms
- Tables for data
- Math and logic notation

**Use Cases**: Homework submissions, problem sets, exercise solutions

---

## Cheat Sheets

### Example 8: Single-Column Compact Cheat Sheet

**Description**: Dense single-column reference for quick lookup

**Code**:
```typst
#set page(paper: "us-letter", margin: 0.4in)
#set text(size: 8pt)
#set par(leading: 0.4em, justify: true)
#set heading(numbering: none)

#show heading.where(level: 1): set text(size: 10pt, weight: "bold")
#show heading.where(level: 2): set text(size: 9pt, weight: "bold")

= CPU Scheduling Algorithms

== FCFS (First-Come, First-Served)
*Order*: Arrival time | *Preemptive*: No | *Starvation*: No | *Convoy Effect*: Yes

== SJF (Shortest Job First)
*Order*: Burst time (shortest first) | *Preemptive*: No | *Optimal*: Yes (min avg wait) | *Starvation*: Possible (long jobs)

== SRTF (Shortest Remaining Time First)
*Order*: Remaining time | *Preemptive*: Yes | *Optimal*: Yes | *Overhead*: High (context switches)

== Round Robin
*Order*: FCFS with time quantum | *Preemptive*: Yes | *Fair*: Yes | *Time Quantum*: Critical parameter

== Priority Scheduling
*Order*: Priority value | *Preemptive*: Can be | *Starvation*: Yes (low priority) | *Solution*: Aging

= Memory Management

== Paging
*Size*: Fixed (pages/frames) | *Fragmentation*: Internal only | *Address*: Page table lookup

== Segmentation
*Size*: Variable (segments) | *Fragmentation*: External | *Logical*: Matches program structure

== TLB (Translation Lookaside Buffer)
*Purpose*: Cache page table entries | *Hit Ratio*: $alpha$ | *EAT*: $alpha times (t + m) + (1-alpha) times (t + 2m)$

= Synchronization

== Mutex Lock
*Type*: Binary | *Busy Wait*: Yes | *Use*: Simple mutual exclusion

== Semaphore
*Type*: Counting | *Operations*: wait(), signal() | *Use*: Resource counting

== Monitor
*Type*: High-level | *Condition Vars*: wait(), signal() | *Use*: Complex synchronization
```

**Key Techniques**:
- Minimal margins and text size
- Tight line spacing
- Inline attribute format (key: value)
- Math notation in text

**Use Cases**: Exam prep, quick reference cards, formula sheets

---

### Example 9: Two-Column Cheat Sheet

**Description**: Two-column layout for balanced reference

**Code**:
```typst
#set page(paper: "us-letter", margin: 0.5in)
#set text(size: 9pt)
#set par(leading: 0.5em)
#set heading(numbering: none)

#columns(2, gutter: 0.4in)[

= Page Replacement

== FIFO
*Principle*: Replace oldest page

*Belady's Anomaly*: More frames may increase faults

*Complexity*: $O(1)$

== LRU (Least Recently Used)
*Principle*: Replace least recently used

*Implementation*:
- Counter method
- Stack method

*No Belady's Anomaly*

== Clock Algorithm
*Principle*: Second chance FIFO

*Reference Bit*: 0 = replace, 1 = second chance

*Approximates LRU*

#colbreak()

= Disk Scheduling

== FCFS
*Order*: Request order

*Fair*: Yes

*Seek Time*: High variance

== SSTF (Shortest Seek Time First)
*Order*: Closest track

*Starvation*: Possible

== SCAN (Elevator)
*Direction*: One direction, then reverse

*Fair*: More balanced

== C-SCAN (Circular SCAN)
*Direction*: One direction, jump back

*More Uniform Wait Time*

= Deadlock

== Necessary Conditions
+ *Mutual Exclusion*
+ *Hold and Wait*
+ *No Preemption*
+ *Circular Wait*

*All four must hold*

== Prevention
Break one condition

== Detection
Resource allocation graph

]
```

**Key Techniques**:
- Two-column layout with `#columns()`
- Manual column break with `#colbreak()`
- Compact hierarchical organization
- Mixed lists and definitions

**Use Cases**: Study guides, exam cheat sheets, quick references

---

### Example 10: Three-Column Dense Cheat Sheet

**Description**: Maximum information density with three columns

**Code**:
```typst
#set page(paper: "us-letter", margin: 0.3in)
#set text(size: 8pt)
#set par(leading: 0.4em)

#show heading.where(level: 1): set text(size: 9pt, weight: "bold")
#show heading.where(level: 2): set text(size: 8pt, weight: "bold", style: "italic")

#columns(3, gutter: 0.25in)[

= Processes

== States
New → Ready → Running → Waiting → Terminated

== PCB
PID, state, PC, registers, memory limits, files

== Context Switch
Save state, load state, overhead

#colbreak()

= Threads

== Benefits
Responsiveness, resource sharing, economy, scalability

== Types
*User*: Library-managed
*Kernel*: OS-managed

== Models
Many-to-one, one-to-one, many-to-many

#colbreak()

= Scheduling

== Metrics
- CPU utilization
- Throughput
- Turnaround time
- Waiting time
- Response time

== Gantt Chart
Visual timeline

]
```

**Key Techniques**:
- Three-column maximum density
- Minimal spacing
- Abbreviated content
- Visual separators

**Use Cases**: One-page references, formula sheets, condensed study aids

---

## Presentations

### Example 11: Slide Template

**Description**: Presentation slide with title and content

**Code**:
```typst
#set page(
  paper: "presentation-16-9",
  margin: (x: 1in, y: 0.5in)
)
#set text(size: 20pt)

#align(horizon + center)[
  #text(size: 36pt, weight: "bold")[
    Operating Systems Security
  ]

  #v(1em)

  #text(size: 24pt)[
    Alice Johnson
  ]

  #v(0.5em)

  October 2024
]

#pagebreak()

#block(above: 0em)[
  #text(size: 28pt, weight: "bold")[Access Control]
]

#v(1em)

#text(size: 20pt)[
  *Three Models*:

  + *Discretionary Access Control (DAC)*
    - Users control access to their resources
    - Example: File permissions in Unix

  + *Mandatory Access Control (MAC)*
    - System enforces access policy
    - Example: SELinux

  + *Role-Based Access Control (RBAC)*
    - Permissions assigned to roles
    - Example: Database user roles
]

#pagebreak()

#block(above: 0em)[
  #text(size: 28pt, weight: "bold")[Authentication Methods]
]

#v(1em)

#grid(
  columns: 2,
  gutter: 1in,
  [
    *Something You Know*
    - Password
    - PIN
    - Security questions

    *Something You Have*
    - Smart card
    - Security token
    - Phone (2FA)
  ],
  [
    *Something You Are*
    - Fingerprint
    - Facial recognition
    - Iris scan

    *Somewhere You Are*
    - IP address
    - GPS location
  ]
)
```

**Key Techniques**:
- `presentation-16-9` paper size
- Large text (20-36pt)
- Centered title slide
- Minimal bullet points per slide
- Grid layout for side-by-side content

**Use Cases**: Presentations, lectures, talks

---

### Example 12: Slide with Diagram Placeholder

**Description**: Slide incorporating figures and captions

**Code**:
```typst
#set page(paper: "presentation-16-9", margin: 1in)
#set text(size: 18pt)

#block(above: 0em)[
  #text(size: 28pt, weight: "bold")[Process State Diagram]
]

#v(1em)

#align(center)[
  #box(
    width: 90%,
    height: 60%,
    fill: gray.lighten(80%),
    stroke: 1pt,
    radius: 4pt
  )[
    #align(horizon + center)[
      #text(size: 14pt, style: "italic")[
        [Process state diagram would go here]

        New → Ready → Running → {Waiting, Terminated}
      ]
    ]
  ]
]

#v(1em)

*Key Transitions*:
- Admitted: New → Ready
- Dispatch: Ready → Running
- I/O wait: Running → Waiting
- I/O complete: Waiting → Ready
```

**Key Techniques**:
- Placeholder box for diagram
- Large, clear typography
- Centered visuals
- Concise bullet points

**Use Cases**: Technical presentations with diagrams, flowcharts

---

## Technical Documentation

### Example 13: API Reference

**Description**: API documentation with function signatures and examples

**Code**:
```typst
#set page(margin: 1in)
#set text(size: 11pt)
#set heading(numbering: "1.1")

= Process Management API

== create_process()

*Purpose*: Create a new process

*Signature*:
```c
pid_t create_process(
    const char *program,
    char *const argv[],
    char *const envp[]
);
\```

*Parameters*:
- `program`: Path to executable
- `argv`: Argument array (NULL-terminated)
- `envp`: Environment variables (NULL-terminated)

*Returns*:
- Success: Process ID (PID) of child
- Error: -1 (check errno)

*Example*:
```c
char *args[] = {"/bin/ls", "-la", "/home", NULL};
char *env[] = {NULL};
pid_t pid = create_process("/bin/ls", args, env);
if (pid == -1) {
    perror("create_process failed");
}
\```

*Error Codes*:
- `ENOMEM`: Insufficient memory
- `ENOENT`: Program not found
- `EACCES`: Permission denied

---

== terminate_process()

*Purpose*: Terminate a process gracefully

*Signature*:
```c
int terminate_process(pid_t pid, int signal);
\```

*Parameters*:
- `pid`: Process ID to terminate
- `signal`: Signal to send (SIGTERM, SIGKILL)

*Returns*:
- 0 on success
- -1 on error

*Example*:
```c
if (terminate_process(1234, SIGTERM) == 0) {
    printf("Process terminated\n");
}
\```
```

**Key Techniques**:
- Consistent function documentation format
- Code examples for each function
- Parameter descriptions
- Error code tables

**Use Cases**: API documentation, library references, SDK guides

---

### Example 14: Algorithm Documentation

**Description**: Detailed algorithm explanation with pseudocode and analysis

**Code**:
```typst
#set page(margin: 1in)
#set par(justify: true)
#set heading(numbering: "1.")

= Banker's Algorithm

== Overview

The Banker's Algorithm is a deadlock avoidance algorithm that ensures the system never enters a deadlock state by checking resource allocation safety.

== Data Structures

*Available*: Vector of length $m$ (available resources) \
*Max*: $n times m$ matrix (maximum demand) \
*Allocation*: $n times m$ matrix (currently allocated) \
*Need*: $n times m$ matrix (remaining need)

where $n$ = number of processes, $m$ = number of resource types

*Relationship*: Need[i][j] = Max[i][j] - Allocation[i][j]

== Safety Algorithm

```
1. Initialize Work = Available, Finish[i] = false for all i
2. Find process i where:
   - Finish[i] == false
   - Need[i] <= Work
3. If found:
   - Work = Work + Allocation[i]
   - Finish[i] = true
   - Go to step 2
4. If Finish[i] == true for all i, system is safe
\```

== Example

*Initial State*:

#table(
  columns: 5,
  stroke: 0.5pt,
  [], [*A*], [*B*], [*C*], [],
  [*Available*], [3], [3], [2], [],
  [*P0 Alloc*], [0], [1], [0], [*Max: 7 5 3*],
  [*P1 Alloc*], [2], [0], [0], [*Max: 3 2 2*],
  [*P2 Alloc*], [3], [0], [2], [*Max: 9 0 2*]
)

*Safe Sequence*: P1 → P0 → P2

== Complexity Analysis

*Time*: $O(m times n^2)$ \
*Space*: $O(m times n)$

where checking each of $n$ processes requires $O(m times n)$ comparisons.

== Advantages and Disadvantages

*Advantages*:
- Guarantees deadlock avoidance
- Works for multiple resource types
- Can handle dynamic requests

*Disadvantages*:
- Requires advance knowledge of maximum needs
- High computational overhead
- Processes must declare maximum resource requirements upfront
```

**Key Techniques**:
- Pseudocode formatting
- Data structure diagrams with tables
- Complexity analysis
- Example walkthrough

**Use Cases**: Algorithm documentation, textbooks, research papers

---

### Example 15: Comparison Table Documentation

**Description**: Side-by-side comparison of approaches

**Code**:
```typst
#set page(margin: 1in)
#set text(size: 11pt)

= Memory Allocation Strategies Comparison

#figure(
  table(
    columns: (1.5fr, 1fr, 1fr, 1fr, 1.5fr),
    stroke: 0.5pt,
    align: (left, center, center, center, left),
    inset: 8pt,

    table.header(
      [*Strategy*], [*Speed*], [*Fragmentation*], [*Complexity*], [*Best Use Case*]
    ),

    [*First Fit*],
    [Fast],
    [High],
    [Low],
    [Quick allocation, memory abundant],

    [*Best Fit*],
    [Medium],
    [Medium],
    [Medium],
    [Minimize wasted space],

    [*Worst Fit*],
    [Medium],
    [High],
    [Medium],
    [Large requests expected],

    [*Next Fit*],
    [Fast],
    [Medium],
    [Low],
    [Sequential access patterns],

    [*Buddy System*],
    [Slow],
    [Medium],
    [High],
    [Variable-size with quick coalescing]
  ),
  caption: [Memory allocation strategy comparison]
)

== Detailed Analysis

=== First Fit
Allocates the first block large enough. *Advantage*: Fast. *Disadvantage*: Creates fragmentation at beginning of memory.

=== Best Fit
Searches for smallest block that fits. *Advantage*: Minimizes wasted space per allocation. *Disadvantage*: Slower search time, creates tiny unusable fragments.

=== Worst Fit
Allocates largest available block. *Advantage*: Leftover space more likely to be usable. *Disadvantage*: Quickly exhausts large blocks.

=== Next Fit
Like first fit, but starts search from last allocation. *Advantage*: Distributes allocations more evenly. *Disadvantage*: Can fragment end of memory.

=== Buddy System
Divides memory into power-of-2 blocks. *Advantage*: Fast coalescing of free blocks. *Disadvantage*: Internal fragmentation (rounding to power of 2).
```

**Key Techniques**:
- Complex table with headers
- Comparison matrix format
- Detailed explanations following table
- Advantage/disadvantage analysis

**Use Cases**: Technology comparisons, decision guides, evaluation documents

---

### Example 16: Configuration File Documentation

**Description**: Document configuration syntax with examples

**Code**:
```typst
#set page(margin: 1in)
#set heading(numbering: "1.")

= Scheduler Configuration Guide

== Overview

The scheduler configuration file (`/etc/scheduler.conf`) controls CPU scheduling behavior.

== Syntax

```
[section]
parameter = value
\```

== Sections

=== [Global]

*default_algorithm*: Scheduling algorithm to use
- Values: `fcfs`, `sjf`, `rr`, `priority`
- Default: `rr`

*time_quantum*: Time slice for Round Robin (ms)
- Range: 1-1000
- Default: 10

*priority_levels*: Number of priority levels
- Range: 1-10
- Default: 5

=== [RoundRobin]

*quantum*: Override time quantum
*aging_enabled*: Prevent starvation (`true`/`false`)

=== [Priority]

*preemptive*: Allow preemption (`true`/`false`)
*aging_rate*: Priority boost interval (ms)

== Example Configuration

```
[Global]
default_algorithm = rr
time_quantum = 20

[RoundRobin]
quantum = 15
aging_enabled = true

[Priority]
preemptive = true
aging_rate = 100
\```

== Validation

Run `scheduler --validate` to check configuration syntax.

*Common Errors*:
- Invalid algorithm name
- time_quantum out of range
- Missing required section
```

**Key Techniques**:
- Code blocks for config syntax
- Section-based organization
- Parameter descriptions with types and ranges
- Example configuration
- Validation instructions

**Use Cases**: Configuration guides, admin documentation, setup instructions

---

### Example 17: Troubleshooting Guide

**Description**: Problem-solution format documentation

**Code**:
```typst
#set page(margin: 1in)
#set heading(numbering: "1.")

= Deadlock Troubleshooting Guide

== Problem: System Hangs

*Symptoms*:
- Processes not making progress
- CPU utilization drops to near zero
- No I/O activity

*Diagnosis*:
```bash
# Check for deadlock
$ ps aux | grep D  # Check for processes in uninterruptible sleep
$ lsof | grep LOCK  # Check for file locks
\```

*Solutions*:

+ *Identify deadlocked processes*
  ```bash
  $ kill -9 <pid>  # Force kill one process to break cycle
  \```

+ *Analyze resource allocation graph*
  - Check for circular wait condition
  - Identify which resource is causing the cycle

+ *Prevent future occurrences*
  - Impose resource ordering
  - Use timeouts for lock acquisition

---

== Problem: High Context Switch Rate

*Symptoms*:
- `vmstat` shows high context switch count (>10000/sec)
- Poor application performance
- High system CPU usage

*Diagnosis*:
```bash
$ vmstat 1 10  # Monitor context switches
$ pidstat -w 1  # Identify processes causing switches
\```

*Solutions*:

+ Increase time quantum (Round Robin)
  ```
  echo 50 > /sys/kernel/sched_rr_timeslice_ms
  \```

+ Reduce number of running processes
+ Use CPU affinity to reduce migration

---

## Problem: Priority Inversion

*Symptoms*:
- High-priority task blocked by low-priority task
- Unpredictable latency
- Real-time deadlines missed

*Example Scenario*:
```
H (high priority) waits for lock held by L (low priority)
M (medium priority) preempts L
Result: H blocked indefinitely
\```

*Solutions*:

+ *Priority Inheritance*: L temporarily inherits H's priority
+ *Priority Ceiling*: Locks have priority ceiling equal to highest task that uses them
```

**Key Techniques**:
- Problem-symptom-solution structure
- Command-line examples
- Scenario descriptions
- Multiple solution paths

**Use Cases**: Troubleshooting guides, FAQ documentation, support resources

---

## Summary

This examples library provides working code for diverse Typst use cases. Key patterns:

**Documents**:
- Set page and text with `#set page()` and `#set text()`
- Use heading levels consistently
- Apply paragraph formatting with `#set par()`

**Layout**:
- Multi-column with `#columns()`
- Tables with `#table(columns: N)`
- Figures with captions

**Formatting**:
- Bold: `*text*`
- Italic: `_text_`
- Code: ` ```lang `
- Math: `$expression$`

**For more**:
- **Syntax details**: See syntax-reference.md
- **Document patterns**: See patterns.md
- **Templates**: See templates/ directory
