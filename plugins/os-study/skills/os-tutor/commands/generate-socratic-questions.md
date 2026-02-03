---
description: Generate Socratic question templates for OS tutoring
---

Create ${CLAUDE_PLUGIN_ROOT}/skills/os-tutor/references/socratic_prompts.md with question templates organized by pedagogical purpose.

## Output Structure

### 1. Clarification Questions
Questions that probe understanding of terms/definitions:
- "What do you mean by [term]?"
- "Can you define [concept] in your own words?"
- "What's the difference between [X] and [Y]?"

### 2. Assumption-Probing Questions  
Questions that surface hidden assumptions:
- "What are you assuming about the input?"
- "Does this work if [edge case]?"
- "What has to be true for this to work?"

### 3. Reasoning Questions
Questions about the "why":
- "Why does [operation] take O(log n)?"
- "Why do we [specific step] before [other step]?"
- "What would break if we didn't [X]?"

### 4. Evidence Questions
Questions asking for justification:
- "How do you know [claim]?"
- "Can you trace through an example?"
- "What's the invariant that guarantees this?"

### 5. Implication Questions
Questions about consequences:
- "What does that imply about [related concept]?"
- "If [X] is true, what else must be true?"
- "How does this affect the time complexity?"

### 6. Alternative Viewpoint Questions
Questions that introduce other perspectives:
- "Could you solve this differently?"
- "Why might someone choose [alternative] instead?"
- "What's the trade-off?"

### 7. Metacognitive Questions
Questions about the student's own thinking:
- "How confident are you (1-5)?"
- "What part are you least sure about?"
- "How would you verify your answer?"

## Topic-Specific Templates

Generate 3-5 Socratic questions for each major topic cluster:

### CPU Scheduling
- "Why does SJF minimize average waiting time?"
- "If we increase the time quantum in Round Robin, what happens to response time? Throughput?"
- "When would Priority scheduling cause starvation? How can we prevent it?"
- ...

### Synchronization
- "What does 'thrashing' mean in the context of virtual memory?"
- "Why does the working set model help prevent thrashing?"
- "What would break if we didn't satisfy the 'progress' requirement?"
- "Instead of semaphores, could we use monitors? What changes?"
- ...

### Memory Management
- "How does the TLB improve performance? What's the trade-off?"
- "Why use multilevel page tables instead of a single large table?"
- "If the page size doubles, what happens to internal fragmentation?"
- ...

### Page Replacement
- "What evidence shows that LRU approximates the optimal algorithm?"
- "If we use FIFO page replacement, what could happen as we add more frames?"
- "Why doesn't Belady's Anomaly occur with LRU?"
- ...

### Virtualization
- "When would you choose Type 1 vs Type 2 hypervisor?"
- "How does trap-and-emulate enable virtualization?"
- "What advantage does paravirtualization provide over full virtualization?"
- ...

## Instructions

1. Read the topic_graph.md to understand what OS concepts exist
2. For each difficulty 3+ topic, generate at least 2 Socratic questions
3. Questions should force explanation, not just yes/no answers
4. Include questions that connect across topics (e.g., scheduling affects memory management)
5. Focus on conceptual understanding and design trade-offs
6. Output to ${CLAUDE_PLUGIN_ROOT}/skills/os-tutor/references/socratic_prompts.md