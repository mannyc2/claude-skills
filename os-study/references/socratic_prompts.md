# Socratic Question Templates for Operating Systems

Organized by pedagogical purpose. Use these templates to guide students toward deep understanding rather than providing direct instruction.

## 1. Clarification Questions

Questions that probe understanding of terms/definitions:

**General**:
- "What do you mean by [term]?" (e.g., thrashing, convoy effect, priority inversion)
- "Can you define [concept] in your own words?" (e.g., mutual exclusion, atomicity, virtual memory)
- "What's the difference between [X] and [Y]?" (e.g., semaphore vs mutex, paging vs segmentation)
- "How would you explain [concept] to someone who's never taken an OS class?"
- "What does it mean when we say [property]?" (e.g., "the critical section problem requires progress")

**OS-Specific**:
- "What exactly does 'preemptive' mean in the context of scheduling?"
- "When we say a process is 'blocked', what state is it in and why?"
- "What's the difference between internal and external fragmentation? Can you give examples?"
- "Can you explain what a 'page fault' is without using the word 'fault'?"
- "What does 'thrashing' mean, and how would you recognize it?"
- "What's the difference between a 'logical address' and a 'physical address'?"
- "What do we mean by 'context switch overhead'?"
- "What's the difference between a 'hypervisor' and a regular OS?"

## 2. Assumption-Probing Questions

Questions that surface hidden assumptions:

**General**:
- "What are you assuming about [input/system state]?"
- "Does this work if [edge case]?" (e.g., all processes arrive at time 0, page table is full)
- "What has to be true for this to work?"
- "Are you assuming [X]? What if that's not the case?"
- "What constraints are you working under?"

**OS-Specific**:
- "You're using Round Robin—what are you assuming about the time quantum size?"
- "Does FCFS work well if all processes are I/O-bound? What about all CPU-bound?"
- "You're calculating page faults with FIFO—are you assuming the process starts with empty frames?"
- "Does Peterson's solution work if processes don't execute in lockstep? Why or why not?"
- "What are you assuming about the hardware when you say 'we can use a TLB'?"
- "Does SJF minimize average wait time if processes arrive at different times?"
- "You're using a semaphore initialized to 1—what does that assume about the number of processes that can enter the critical section?"
- "Does LRU work well if the reference pattern doesn't have temporal locality?"
- "What are we assuming about CPU speed when we compare scheduling algorithms?"
- "Does this page replacement algorithm assume we know future references?"

## 3. Reasoning Questions

Questions about the "why":

**General**:
- "Why does [algorithm/mechanism] behave this way?"
- "Why do we [specific step] before [other step]?"
- "What would break if we didn't [X]?"
- "Why is [approach] better than [alternative] in this scenario?"
- "What's the rationale behind [design decision]?"

**OS-Specific**:
- "Why does SJF minimize average waiting time? Can you prove it intuitively?"
- "Why do we need both a 'valid' bit and 'protection' bits in page table entries?"
- "Why does Round Robin give better response time than FCFS for interactive systems?"
- "Why can't we just use Peterson's solution for more than 2 processes?"
- "Why does the convoy effect happen with FCFS scheduling?"
- "Why does increasing the number of frames sometimes increase page faults (Belady's Anomaly)?"
- "Why do we need a TLB if we already have a page table?"
- "Why does thrashing occur, and what's the fundamental cause?"
- "Why use multilevel page tables instead of a single huge table?"
- "Why does priority scheduling risk starvation while Round Robin doesn't?"
- "Why is 'aging' an effective solution to starvation?"
- "Why does paravirtualization perform better than trap-and-emulate?"
- "Why can't Type 2 hypervisors achieve the same performance as Type 1?"
- "Why do monitors prevent race conditions better than semaphores in some cases?"

## 4. Evidence Questions

Questions asking for justification:

**General**:
- "How do you know [claim]?"
- "Can you trace through an example to show this?"
- "What's the invariant that guarantees this works?"
- "Can you walk me through the steps?"
- "What would you measure to verify this?"

**OS-Specific**:
- "Can you trace Round Robin with quantum=4 on these processes to show the average wait time?"
- "How do you know this scheduling algorithm won't starve low-priority processes?"
- "Can you show me the address translation step-by-step for logical address 2050?"
- "How can you prove Peterson's solution satisfies mutual exclusion?"
- "Can you demonstrate why FIFO causes more page faults than LRU on this reference string?"
- "Walk me through what happens during a TLB miss, step by step."
- "How would you verify that this semaphore implementation prevents race conditions?"
- "Can you trace the page replacement algorithm frame-by-frame on this reference string?"
- "Show me the Gantt chart for SRTF on these processes—how did you determine when preemption occurs?"
- "How do you calculate the effective access time with an 80% TLB hit ratio?"
- "Can you prove the working set model prevents thrashing?"
- "Walk through a context switch—what state gets saved and restored?"

## 5. Implication Questions

Questions about consequences:

**General**:
- "What does that imply about [related concept]?"
- "If [X] is true, what else must be true?"
- "How does this affect [performance metric]?"
- "What are the consequences of [decision]?"
- "What happens to [Y] if we change [X]?"

**OS-Specific**:
- "If we decrease the time quantum in Round Robin, what happens to context switch overhead?"
- "If the TLB hit ratio drops from 98% to 80%, what's the impact on effective access time?"
- "What does a high page fault rate imply about the working set vs available frames?"
- "If we use larger page sizes (2MB instead of 4KB), what happens to internal fragmentation?"
- "If CPU utilization for Rate Monotonic exceeds 69%, what does that mean?"
- "What does a long average waiting time in FCFS tell you about the process mix?"
- "If we add more frames but page faults increase (Belady's Anomaly), what does that mean about the algorithm?"
- "If a process has temporal locality, what does that imply about LRU's performance?"
- "What does it mean for system throughput if we're thrashing?"
- "If the working set size exceeds available frames, what happens to the degree of multiprogramming?"
- "If we use paravirtualization, what does that imply about guest OS portability?"
- "What does a low TLB reach imply about the need for huge pages?"

## 6. Alternative Viewpoint Questions

Questions that introduce other perspectives:

**General**:
- "Could you solve this differently?"
- "Why might someone choose [alternative] instead?"
- "What's the trade-off between [X] and [Y]?"
- "When would [approach A] be better than [approach B]?"
- "What are the pros and cons of each approach?"

**OS-Specific**:
- "Instead of Round Robin, could we use Priority scheduling? What changes?"
- "Why might someone choose FCFS over SJF despite worse average wait time?"
- "Could we use segmentation instead of paging? What are the trade-offs?"
- "Why use LRU instead of Optimal page replacement in a real system?"
- "Instead of semaphores, could we use monitors? What's the advantage?"
- "Why would you choose Rate Monotonic over EDF for a real-time system?"
- "Could we solve the convoy effect with shorter time quanta instead of switching to SJF?"
- "Why might a database prefer huge pages (2MB) over standard pages (4KB)?"
- "Instead of aging to prevent starvation, could we use time-slice guarantees?"
- "Why use a multilevel feedback queue instead of just priority scheduling with aging?"
- "Could we use inverted page tables instead of hierarchical? When is that better?"
- "Why choose Type 1 over Type 2 hypervisor for a production server?"
- "Instead of paravirtualization, could we use hardware-assisted virtualization?"
- "Why might copy-on-write be better than eager copying for process creation?"

## 7. Metacognitive Questions

Questions about the student's own thinking:

**General**:
- "How confident are you in this answer (1-5)?"
- "What part are you least sure about?"
- "How would you verify your answer?"
- "What made this problem difficult?"
- "How did you approach this problem?"
- "What would you do differently next time?"

**OS-Specific**:
- "Rate your understanding of TLB operation (1-5). What's still unclear?"
- "What part of the page replacement algorithm trace are you least confident about?"
- "How would you verify your Gantt chart is correct?"
- "What made the SRTF trace harder than the FCFS trace?"
- "How did you decide which algorithm to recommend for this workload?"
- "What assumption did you make that might be wrong?"
- "If you got a different page fault count, how would you debug your trace?"
- "What's the most confusing part about multilevel page tables?"
- "How would you explain thrashing to a classmate who doesn't get it?"
- "What mental model do you use to think about virtual memory?"
- "Which synchronization primitive (mutex/semaphore/monitor) are you most comfortable with? Why?"
- "What study strategy helped you understand address translation?"

---

## Topic-Specific Templates

### CPU Scheduling

**Clarification**:
- "What does 'preemptive' mean in the context of Round Robin?"
- "What's the difference between 'turnaround time' and 'waiting time'?"
- "Can you explain what 'convoy effect' means using an example?"

**Reasoning**:
- "Why does SJF give optimal average waiting time but we don't use it everywhere?"
- "Why does increasing the time quantum eventually make Round Robin behave like FCFS?"
- "Why can Priority scheduling starve processes while Round Robin cannot?"

**Evidence**:
- "Trace FCFS vs SJF on P1(6), P2(8), P3(7), P4(3). Which has better average wait time and by how much?"
- "Show me the Gantt chart for SRTF when P2 arrives—does it preempt P1? Why?"
- "Calculate the CPU utilization for Rate Monotonic on T1(p=50, e=20) and T2(p=100, e=35). Is it schedulable?"

**Implication**:
- "If the time quantum is 1ms and context switch is 0.1ms, what percentage is overhead?"
- "If all processes are CPU-bound, what happens to the benefit of preemptive scheduling?"
- "If new high-priority processes arrive continuously, what happens to low-priority processes?"

**Alternative**:
- "Instead of Round Robin for time-sharing, could we use FCFS? What's wrong with that?"
- "Why use Multilevel Feedback Queue instead of just lowering the priority of CPU-bound processes manually?"
- "When would you choose Rate Monotonic over EDF despite lower CPU utilization?"

### Synchronization

**Clarification**:
- "What does 'mutual exclusion' mean? Can you give a real-world analogy?"
- "What's the difference between a binary semaphore and a mutex?"
- "What do we mean by 'progress' in the critical section problem?"

**Reasoning**:
- "Why does Peterson's solution only work for 2 processes?"
- "Why do we need both `wait()` and `signal()` for semaphores—couldn't one operation suffice?"
- "Why are monitors considered 'easier to use correctly' than semaphores?"
- "Why can priority inversion occur with semaphores but not with mutexes that support priority inheritance?"

**Evidence**:
- "Can you prove Peterson's solution satisfies mutual exclusion by showing both processes can't be in the CS simultaneously?"
- "Trace the bounded-buffer problem with 1 producer, 1 consumer, and buffer size 3. Show the semaphore values."
- "Walk through the dining philosophers with the 'pick up both chopsticks atomically' solution. Does it prevent deadlock?"

**Implication**:
- "If we remove the `while (!flag[j])` loop from Peterson's solution, what breaks?"
- "If `full.wait()` blocks in the producer, what does that tell you about the buffer?"
- "If we use a binary semaphore instead of counting, what happens to the bounded-buffer solution?"

**Alternative**:
- "Instead of semaphores for the readers-writers problem, could we use a monitor? How?"
- "Why not just use busy waiting instead of blocking? What's the cost?"
- "Could we solve the critical section problem with just a `turn` variable (no flags)?"

### Memory Management (Paging & Segmentation)

**Clarification**:
- "What's the difference between a 'page' and a 'frame'?"
- "What does the 'offset' represent in a logical address?"
- "Can you explain what a TLB is and why we need it?"
- "What's the difference between internal and external fragmentation?"

**Reasoning**:
- "Why do we split the address into page number and offset instead of doing division in hardware?"
- "Why use multilevel page tables instead of a single flat table?"
- "Why does paging eliminate external fragmentation but segmentation doesn't?"
- "Why do we need a valid bit in each page table entry?"

**Evidence**:
- "Translate logical address 2050 with page size 1024. Show the page number, offset, and physical address if page 2 maps to frame 7."
- "Calculate the effective access time with memory=100ns, TLB=20ns, hit ratio=80%. Show your work."
- "With 32-bit address space and 4KB pages, how many page table entries are needed? How much memory for the page table if each entry is 4 bytes?"

**Implication**:
- "If we increase page size from 4KB to 2MB, what happens to the page table size?"
- "If the TLB hit ratio drops from 98% to 75%, what's the performance impact?"
- "If we use 2-level paging, how many memory accesses per translation without a TLB?"

**Alternative**:
- "Instead of paging, could we use segmentation? What are the trade-offs?"
- "Why not use a fully associative TLB with unlimited entries?"
- "Could we use inverted page tables instead of multilevel? When is that better?"

### Page Replacement & Virtual Memory

**Clarification**:
- "What does 'demand paging' mean?"
- "What's the difference between a 'page fault' and a 'protection fault'?"
- "Can you explain thrashing in your own words?"
- "What is the 'working set' model?"

**Reasoning**:
- "Why can't we use Optimal page replacement in a real system?"
- "Why does LRU generally perform better than FIFO?"
- "Why does Belady's Anomaly occur with FIFO but not LRU?"
- "Why does thrashing cause CPU utilization to drop?"
- "Why does the Clock algorithm approximate LRU?"

**Evidence**:
- "Trace FIFO on reference string 7,0,1,2,0,3,0,4 with 3 frames. Count page faults."
- "Show that Belady's Anomaly occurs: trace FIFO on 1,2,3,4,1,2,5,1,2,3,4,5 with 3 vs 4 frames."
- "For LRU on 7,0,1,2,0,3,0,4,2,3, show the stack at each step."

**Implication**:
- "If page fault rate is high and CPU utilization is low, what's happening?"
- "If we decrease the degree of multiprogramming, what happens to thrashing?"
- "If a process has poor locality, what happens to the page fault rate?"
- "If the working set size exceeds available frames, what should the OS do?"

**Alternative**:
- "Instead of LRU, could we use LFU (Least Frequently Used)? What's the problem?"
- "Why use the Clock algorithm instead of true LRU?"
- "Instead of global page replacement, could we use local? What's the trade-off?"
- "Why use the working set model instead of just adding more physical memory?"

### Virtualization

**Clarification**:
- "What's the difference between Type 1 and Type 2 hypervisors?"
- "Can you explain 'trap-and-emulate' virtualization?"
- "What does 'paravirtualization' mean?"
- "What's the difference between a VM and a container?"

**Reasoning**:
- "Why do Type 1 hypervisors generally perform better than Type 2?"
- "Why doesn't trap-and-emulate work on x86 (pre-VT-x)?"
- "Why does paravirtualization require modifying the guest OS?"
- "Why is hardware-assisted virtualization (VT-x, AMD-V) needed for modern hypervisors?"
- "Why does binary translation add overhead compared to native execution?"

**Evidence**:
- "Walk through what happens when a guest OS tries to execute a privileged instruction with trap-and-emulate."
- "Show the steps of nested page table translation for a guest virtual address."
- "Trace a live migration—what data gets transferred and in what order?"

**Implication**:
- "If we use paravirtualization, what does that mean for guest OS portability?"
- "If the hypervisor adds 10% overhead, what's the impact on application throughput?"
- "If VMs share physical memory pages (deduplication), what happens to write operations?"

**Alternative**:
- "Instead of full virtualization, could we use containers? What's the trade-off?"
- "Why use paravirtualization instead of hardware-assisted virtualization?"
- "Could we use Type 2 hypervisor for production servers? Why not?"
- "Instead of live migration, why not just shut down and restart on the new host?"

---

## Cross-Topic Integration Questions

These questions require synthesizing knowledge across multiple OS topics:

**Scheduling + Memory**:
- "If we're thrashing, would switching to Round Robin from FCFS help? Why or why not?"
- "How does page fault handling affect scheduling decisions?"
- "Why might a process with high page fault rate get demoted in a multilevel feedback queue?"

**Synchronization + Scheduling**:
- "What is priority inversion, and how does it relate to both synchronization and scheduling?"
- "If a high-priority process is waiting on a semaphore held by a low-priority process, what happens?"
- "How does the scheduler handle processes blocked on semaphores?"

**Memory + Virtualization**:
- "How does nested paging (EPT/NPT) affect the effective access time calculation?"
- "If each VM has its own page table, how does the hypervisor manage physical memory allocation?"
- "What happens during a page fault in a VM—who handles it, guest OS or hypervisor?"

**Scheduling + Virtualization**:
- "How does the hypervisor schedule CPU time among VMs?"
- "If VM1 has a CPU-bound process and VM2 has I/O-bound processes, how should the hypervisor allocate CPU?"
- "What's the difference between scheduling processes and scheduling VMs?"

**Synchronization + Memory**:
- "Why must the test-and-set instruction be atomic at the hardware level?"
- "How does shared memory between processes relate to synchronization requirements?"
- "What happens if a process is swapped out while holding a mutex?"

---

## Usage Guidelines

1. **Start with clarification** - Ensure student understands the terms before diving deeper
2. **Use reasoning questions** to build mental models, not just memorized procedures
3. **Demand evidence** - Students should show their work, not just state answers
4. **Explore implications** to connect performance to design decisions
5. **Present alternatives** to force comparative analysis and trade-off reasoning
6. **Use metacognitive questions** to build self-awareness and study skills

**Example Socratic Dialogue Flow**:
```
Assistant: "Before we solve this, what does 'preemptive scheduling' mean?"
Student: "It means the scheduler can interrupt a running process."
Assistant: "Good start. When would the scheduler decide to interrupt? What triggers it?"
Student: "Maybe when a higher-priority process arrives?"
Assistant: "That's one case. Are there other triggers? Think about Round Robin."
Student: "Oh, the time quantum expiring!"
Assistant: "Exactly. So why do we need preemption for interactive systems?"
[Continue with reasoning and implication questions...]
```

**Avoid**:
- ❌ "Is this correct?" (yes/no questions)
- ❌ "Do you understand?" (doesn't probe actual understanding)
- ❌ Leading questions that reveal the answer

**Prefer**:
- ✅ "Can you explain why [X]?"
- ✅ "What would happen if [Y]?"
- ✅ "How do you know [Z]?"
