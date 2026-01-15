---
description: Generate exam-focused algorithm pattern guides from lecture notes into references/patterns/
---

Read OS chapter files in docs/ and create pattern reference guides in .claude/skills/os-study/references/patterns/.

## Goal

Create **exam-focused** reference guides — not implementation templates. Optimize for:
- Quick comparison lookups
- "When would you use X over Y?" decisions
- Understanding *why* algorithms have their properties
- Trace examples for practice
- Common exam questions with answers

## Output Files

### references/patterns/scheduling.md
From docs/ch5.md (CPU Scheduling):

**Include:**
- Scheduling fundamentals (CPU burst, I/O burst, dispatcher)
- Scheduling criteria (CPU utilization, throughput, turnaround time, waiting time, response time)
- Algorithm comparison matrix (FCFS, SJF, SRTF, Priority, RR, Multilevel Queue)
- Preemptive vs non-preemptive scheduling
- Convoy effect and starvation issues
- Round Robin quantum selection trade-offs
- Real-time scheduling (Rate Monotonic, EDF)
- Common exam questions:
  - "Trace Round Robin with quantum=4 on processes: P1(24), P2(3), P3(3)"
  - "Calculate average wait time for FCFS vs SJF"
  - "Why does SJF minimize average waiting time?"
  - "When would Priority scheduling cause starvation?"

### references/patterns/synchronization.md
From docs/ch6.md and docs/ch7.md (Synchronization Tools and Examples):

**Include:**
- Synchronization mechanism comparison matrix (Mutex, Semaphore, Monitor, Condition Variables)
- Critical section problem requirements (mutual exclusion, progress, bounded waiting)
- Peterson's solution and correctness proof
- Hardware support (test_and_set, compare_and_swap)
- Semaphore types (binary vs counting) and use cases
- Monitor advantages over semaphores
- Classic problems (Producer-Consumer, Readers-Writers, Dining Philosophers)
- Common exam questions:
  - "Trace Peterson's solution with interleaved execution"
  - "When would you use a semaphore vs a mutex?"
  - "Why are monitors safer than semaphores?"
  - "Solve Producer-Consumer using semaphores"

### references/patterns/memory-management.md
From docs/ch9.md (Main Memory):

**Include:**
- Address binding timing (compile, load, execution time)
- Logical vs physical address space
- MMU and address translation
- Paging fundamentals (page size, frame allocation, page table)
- Address translation formula (page number, offset)
- TLB (Translation Lookaside Buffer) and performance impact
- Page table structures comparison (hierarchical, hashed, inverted)
- Segmentation vs paging trade-offs
- Common exam questions:
  - "Translate logical address 0x3A7C with 4KB pages"
  - "Calculate effective access time with TLB hit ratio"
  - "Why use multilevel page tables?"
  - "Compare internal vs external fragmentation"

### references/patterns/page-replacement.md
From docs/ch10.md (Virtual Memory):

**Include:**
- Page replacement algorithm comparison matrix (FIFO, Optimal, LRU, Clock, LRU Approximations)
- Page fault calculation methodology
- Belady's Anomaly explanation (occurs with FIFO, not LRU)
- LRU implementation approaches (counter, stack)
- Second-chance/Clock algorithm mechanics
- Working set model and thrashing prevention
- Frame allocation policies (equal, proportional, priority)
- Common exam questions:
  - "Trace FIFO page replacement on reference string 7,0,1,2,0,3,0,4,2,3,0,3,2"
  - "Trace LRU page replacement on same reference string"
  - "Demonstrate Belady's Anomaly with example"
  - "Calculate effective access time with page fault rate"
  - "Compare LRU vs Clock algorithm trade-offs"

### references/patterns/virtualization.md
From docs/ch18.md (Virtual Machines):

**Include:**
- Hypervisor types comparison table (Type 0, Type 1, Type 2)
- VMM implementation techniques (trap-and-emulate, binary translation, hardware assistance)
- Paravirtualization vs full virtualization
- Nested page tables (NPT) mechanism
- CPU virtualization (VCPU management)
- Memory virtualization techniques (ballooning, deduplication, double paging)
- Live migration process steps
- Common exam questions:
  - "Compare Type 1 vs Type 2 hypervisor trade-offs"
  - "When is binary translation needed?"
  - "How does trap-and-emulate work?"
  - "Explain the steps of live migration"
  - "What are the advantages of paravirtualization?"

## Format Guidelines

Each file should follow this structure:
```markdown
# [Topic] Pattern Guide

Quick reference for [topic] concepts, trade-offs, and common questions.

## [Comparison Matrix / Fundamentals]
(Table comparing key options)

## Key Concepts
(2-3 most important ideas with brief explanations)

## [Section per major subtopic]
(Conceptual explanation, NOT implementation steps)

## Common Exam Questions

### "[Specific question]?"
(Direct answer with explanation)

### "Trace [algorithm] on [input]"
(Worked example with step-by-step table)
```

## Style Rules

1. **Use tables liberally** — comparison matrices, trace tables, terminology references
2. **Exam questions section is mandatory** — this is the most valuable part
3. **Include trace examples** — step-by-step state tables for algorithms
4. **Explain "why" not "how"** — "Why does LRU approximate optimal?" not "How to implement LRU"
5. **Keep pseudocode minimal** — only where it clarifies a concept, never full implementations
6. **Connect concepts** — "Thrashing connects scheduling decisions to memory management performance"

## Instructions

1. Read each relevant chapter file in docs/ (ch5, ch6, ch7, ch9, ch10, ch18)
2. Extract concepts, trade-offs, and common exam questions
3. Organize around UNDERSTANDING and DECISION-MAKING, not implementation
4. Include worked trace examples for algorithms (scheduling traces, page replacement traces, address translation)
5. Create .claude/skills/os-study/references/patterns/ directory if it doesn't exist
6. Output one .md file per category (scheduling, synchronization, memory-management, page-replacement, virtualization)
7. Focus on "When to use X vs Y" comparisons and performance calculations