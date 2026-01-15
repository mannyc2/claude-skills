# Page Replacement Pattern Guide

Quick reference for virtual memory, demand paging, and page replacement algorithms.

## Page Replacement Algorithm Comparison

| Algorithm | Implementation | Performance | Belady's Anomaly | Use Case |
|-----------|----------------|-------------|------------------|----------|
| **FIFO** | Queue | Poor | **YES** ⚠️ | Educational only |
| **Optimal** | Future knowledge | Best (theoretical) | No | Benchmark for comparison |
| **LRU** | Counter or Stack | Very Good | No | General-purpose (if feasible) |
| **Second-Chance** | Circular queue + ref bit | Good | No | Practical LRU approximation |
| **Clock** | Same as Second-Chance | Good | No | Common in real OSes |
| **LFU** | Counter | Variable | No | Specific workloads |
| **MFU** | Counter | Variable | No | Rare use cases |

## Key Concepts

### 1. Demand Paging

**Principle**: Load pages only when needed (not entire program at start)

**Benefits**:
- Less I/O needed
- Less memory needed
- Faster program start
- More processes can fit in memory

**Implementation**:
- Valid/Invalid bit in page table
- Invalid = not in memory
- Access to invalid page → **Page Fault**

**Page Fault Handling Steps**:
1. Check page table → invalid bit set
2. Trap to OS (page fault handler)
3. Find free frame (or select victim page if none free)
4. Read desired page from disk into frame
5. Update page table (mark valid)
6. Restart instruction that caused fault

### 2. Effective Access Time with Page Faults

**Formula**: EAT = (1 - p) × memory_access + p × page_fault_time

Where:
- **p** = page fault rate (0 ≤ p ≤ 1)
- **memory_access** = time to access memory (e.g., 200ns)
- **page_fault_time** = time to service page fault (e.g., 8ms = 8,000,000ns)

**Example**:
- Memory access = 200ns
- Page fault service time = 8ms = 8,000,000ns
- Page fault rate = 0.001 (1 in 1000 accesses)

EAT = (0.999 × 200ns) + (0.001 × 8,000,000ns)
= 199.8ns + 8,000ns
= **8,199.8ns**

**Slowdown**: 8,200ns / 200ns = **41× slower** with just 0.1% fault rate!

**Key Insight**: Page fault rate must be very low for good performance

### 3. Belady's Anomaly

**Definition**: Increasing number of frames can actually **increase** page faults (counterintuitive!)

**Occurs in**: FIFO algorithm

**Does NOT occur in**: Stack algorithms (Optimal, LRU)

**Example**:

Reference string: `1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5`

**With 3 frames (FIFO)**: 9 page faults
```
1 | 1 | 1 | 4 | 4 | 4 | 5 | 5 | 5 | 3 | 3 | 3 |
  | 2 | 2 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 4 | 4 |
  |   | 3 | 3 | 3 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |
F | F | F | F | F | F | F |   |   | F | F | F |
```

**With 4 frames (FIFO)**: 10 page faults (worse!)
```
1 | 1 | 1 | 1 | 1 | 1 | 5 | 5 | 5 | 5 | 5 | 5 |
  | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 1 | 1 | 1 | 1 |
  |   | 3 | 3 | 3 | 3 | 3 | 3 | 2 | 2 | 2 | 2 |
  |   |   | 4 | 4 | 4 | 4 | 4 | 4 | 3 | 3 | 3 |
F | F | F | F |   |   | F | F | F | F | F |   |
```

**Why FIFO fails**: Doesn't consider page usage patterns (may evict frequently-used page)

## Page Replacement Algorithms

### FIFO (First-In, First-Out)

**Idea**: Replace oldest page in memory

**Implementation**: Queue of pages
- New page added to tail
- Victim selected from head

**Advantages**:
- Simple to implement
- Low overhead

**Disadvantages**:
- Poor performance (may replace heavily-used page)
- Belady's Anomaly

**Never use in practice!** (Educational only)

### Optimal Algorithm (OPT / MIN)

**Idea**: Replace page that won't be used for longest time in future

**Implementation**: Impossible (requires future knowledge!)

**Use**: Theoretical benchmark to compare other algorithms

**Performance**: **Best possible** (provably optimal)

**Why optimal**: Delaying eviction as long as possible minimizes page faults

### LRU (Least Recently Used)

**Idea**: Replace page that hasn't been used for longest time (past predicts future)

**Key Assumption**: Locality of reference (recently used pages likely to be used again soon)

**Implementation Options**:

#### Counter Method:
- Each page has counter (timestamp of last use)
- On access: Update counter to current time
- On fault: Search for page with smallest counter
- **Problem**: Search overhead, large counters

#### Stack Method:
- Maintain stack of page numbers
- On access: Move page to top of stack
- On fault: Victim = bottom of stack
- **Problem**: Expensive to maintain (need doubly-linked list)

**Advantages**:
- Excellent performance
- No Belady's Anomaly
- Approximates optimal well in practice

**Disadvantages**:
- Expensive to implement exactly
- High overhead

**Real OSes**: Use LRU approximations instead

### Second-Chance (Clock) Algorithm

**Idea**: Approximate LRU using reference bit

**Data Structure**: Circular queue + reference bit per page

**Algorithm**:
1. On page access: Set reference bit = 1
2. On page fault:
   - Start from current pointer position
   - If reference bit = 0 → **Replace this page**
   - If reference bit = 1 → Set to 0, advance pointer, repeat
3. Update pointer to next position

**Visualization** (Clock hand):
```
        Page 3 (ref=1)
             ↑
    Page 4 ← ● → Page 2 (ref=0)  ← Victim!
             ↓
        Page 1 (ref=1)
```

**Advantages**:
- Much simpler than LRU
- Reasonable approximation
- Low overhead

**Disadvantage**:
- Not as good as true LRU
- Worst case: scan all pages

**Enhanced Second-Chance**:
- Uses **(reference bit, modify bit)** pairs
- Priority: (0,0) > (0,1) > (1,0) > (1,1)
- Prefer clean pages (no write-back needed)

### LFU (Least Frequently Used)

**Idea**: Replace page with smallest access count

**Implementation**: Counter per page, increment on each access

**Problem**: Page used heavily in past but not now still has high count

**Solution**: Shift counts right periodically (aging)

### MFU (Most Frequently Used)

**Idea**: Page with smallest count probably just brought in, will be used more

**Rarely used** in practice (poor performance)

## Thrashing

**Definition**: System spends more time paging than executing

**Cause**: Process doesn't have enough frames for its working set

**Symptoms**:
- CPU utilization drops dramatically
- High disk I/O activity
- Processes make little progress

**Example Timeline**:
1. OS increases degree of multiprogramming
2. Total memory demand exceeds available memory
3. Processes start paging excessively
4. CPU idle waiting for page I/O
5. OS adds more processes (CPU idle!) → worse thrashing

**Solutions**:

### 1. Working Set Model

**Working Set (WS)**: Set of pages process is actively using

**Working Set Window** (Δ): Look-back time window
- WS(Δ) = set of pages referenced in last Δ time units

**Policy**: Grant process enough frames to hold its working set
- If total WSS > available frames → suspend processes (decrease MPL)

**Example**:
```
Reference string: ...2 6 1 5 7 7 7 7 5 1 6 2 3 4 1 2 3 4 4 4 3 4 3 4 4 4 1 3 2 3 4 4 4 3 4...
                              ↑
                          Current time

Δ = 10: WS = {1, 2, 5, 6, 7}  (5 pages)
Δ = 5:  WS = {1, 5, 7}        (3 pages)
```

### 2. Page-Fault Frequency (PFF)

**Idea**: Monitor page fault rate, adjust frame allocation

**Policy**:
- PFF too high → allocate more frames
- PFF too low → take away frames (process not using them)

**Thresholds**:
```
                    Upper Threshold
        ─────────────────────────────
                   Increase frames

        Acceptable Range

        ───────────────────────────── Lower Threshold
                   Decrease frames
```

**Advantage**: Simpler than working set, more responsive

## Common Exam Questions

### "Trace FIFO page replacement on reference string 7,0,1,2,0,3,0,4,2,3,0,3,2,1,2,0,1,7,0,1"

**Given**: 3 frames, initially empty

**Trace**:
```
Ref: 7  0  1  2  0  3  0  4  2  3  0  3  2  1  2  0  1  7  0  1
───────────────────────────────────────────────────────────────
F1:  7  7  7  2  2  2  2  4  4  4  0  0  0  1  1  1  1  7  7  7
F2:     0  0  0  0  0  0  0  2  2  2  2  2  2  2  0  0  0  0  0
F3:        1  1  1  3  3  3  3  3  3  3  3  3  3  3  1  1  1  1
───────────────────────────────────────────────────────────────
PF:  F  F  F  F  -  F  -  F  F  F  F  -  -  F  -  F  F  F  F  -
```

**Page Faults**: 15 out of 20 references

**Explanation**:
- 7: Cold start → Fault, load into F1
- 0: Not in memory → Fault, load into F2
- 1: Not in memory → Fault, load into F3
- 2: Not in memory → Fault, replace 7 (oldest) in F1
- 0: Already in F2 → Hit
- 3: Not in memory → Fault, replace 0 (oldest) in F2
- etc.

### "Trace LRU page replacement on same reference string"

**Reference string**: 7,0,1,2,0,3,0,4,2,3,0,3,2,1,2,0,1,7,0,1

**Trace** (with LRU ordering):
```
Ref: 7  0  1  2  0  3  0  4  2  3  0  3  2  1  2  0  1  7  0  1
───────────────────────────────────────────────────────────────
F1:  7  7  7  2  2  2  2  4  4  4  4  4  4  1  1  1  1  1  1  1
F2:     0  0  0  0  0  0  0  2  2  2  2  2  2  2  0  0  0  0  0
F3:        1  1  1  3  3  3  3  3  0  0  0  0  0  0  7  7  7  7
───────────────────────────────────────────────────────────────
LRU: 7  0  1  1  2  2  3  2  4  3  3  0  2  0  1  1  7  0  1  (which is LRU at time of fault)
PF:  F  F  F  F  -  F  -  F  F  F  F  -  -  F  -  F  -  F  -  -
```

**Page Faults**: 12 out of 20 references

**Improvement**: LRU (12 faults) vs FIFO (15 faults) = **20% better**

**Explanation** (key differences):
- At reference 4: FIFO replaces 0 (oldest), LRU replaces 7 (least recently used)
- At reference 0 (position 11): LRU has 0 already (hit!), FIFO had replaced it (fault)

### "Demonstrate Belady's Anomaly with example"

**Reference string**: 1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5

**3 Frames (FIFO)**:
```
Ref: 1  2  3  4  1  2  5  1  2  3  4  5
───────────────────────────────────────
F1:  1  1  1  4  4  4  5  5  5  3  3  3
F2:     2  2  2  1  1  1  1  1  1  4  4
F3:        3  3  3  2  2  2  2  2  2  2
───────────────────────────────────────
PF:  F  F  F  F  F  F  F  -  -  F  F  F
```
**Page Faults = 9**

**4 Frames (FIFO)**:
```
Ref: 1  2  3  4  1  2  5  1  2  3  4  5
───────────────────────────────────────
F1:  1  1  1  1  1  1  5  5  5  5  5  5
F2:     2  2  2  2  2  2  1  1  1  1  1
F3:        3  3  3  3  3  3  2  2  2  2
F4:           4  4  4  4  4  4  3  3  3
───────────────────────────────────────
PF:  F  F  F  F  -  -  F  F  F  F  F  -
```
**Page Faults = 10**  ← **More frames, MORE faults!**

**Why**: FIFO doesn't respect locality
- With 3 frames: Some lucky hits
- With 4 frames: Different eviction pattern, unlucky misses

**Lesson**: Adding memory shouldn't hurt performance! (LRU doesn't have this problem)

### "Calculate effective access time with page fault rate"

**Given**:
- Memory access time = 100ns
- Page fault service time = 25ms = 25,000,000ns
- Page fault rate = 1 / 10,000 = 0.0001

**Formula**: EAT = (1 - p) × memory + p × fault_time

**Calculation**:
EAT = (0.9999 × 100ns) + (0.0001 × 25,000,000ns)
= 99.99ns + 2,500ns
= **2,599.99ns**

**Slowdown**: 2,600ns / 100ns = **26× slower**

**To keep slowdown under 10%** (EAT < 110ns):
- Need: (1 - p) × 100 + p × 25,000,000 < 110
- Solve: p < 0.0000004 = 1 fault per 2,500,000 accesses

**Key Insight**: Even tiny page fault rates cause huge slowdowns!

### "Compare LRU vs Clock algorithm trade-offs"

| Aspect | LRU | Clock (Second-Chance) |
|--------|-----|----------------------|
| **Performance** | Near-optimal | Very good (close to LRU) |
| **Implementation** | Complex (counter/stack) | Simple (circular queue + ref bit) |
| **Overhead** | High (update on every access) | Low (ref bit set in hardware) |
| **Page fault rate** | Lower | Slightly higher |
| **Practicality** | Often too expensive | **Widely used in real OSes** |
| **HW support needed** | Full timestamp | Just reference bit |

**Decision**:
- **Theoretical/Small systems**: LRU (if can afford overhead)
- **Real OS Implementation**: Clock (best trade-off)

**Example**: Linux uses a variant of Clock (2-handed clock algorithm)

### "Explain working set and how it prevents thrashing"

**Working Set Definition**: Set of pages process actively uses over time window Δ

**Example Process Behavior**:
```
Time:  0────10────20────30────40────50────60
Phase:   Startup   Loop A    Loop B    Finish
WS:    {1,2,3,4} {5,6,7}   {8,9,10}  {11,12}
Size:     4         3          3         2
```

**Working Set Model**:
1. Measure each process's WSS (working set size)
2. Total demand = Σ WSS for all processes
3. If total demand > available frames → **Thrashing risk**

**Prevention Strategy**:
- **Policy**: Only run process if can allocate its full WSS
- **If Σ WSS > available memory**:
  - Suspend some processes (reduce MPL)
  - Swap them out completely
  - Give remaining processes enough frames

**Example Scenario**:
- Memory = 100 frames
- Process A: WSS = 30
- Process B: WSS = 35
- Process C: WSS = 40
- Total demand = 105 frames > 100 available

**Solution**: Suspend Process C
- Now only need 65 frames
- A and B run without thrashing
- C swapped out temporarily

**Advantage**: Better to run 2 processes well than 3 processes poorly (thrashing)

## Advanced Concepts

### Copy-on-Write (COW)

**Scenario**: `fork()` creates child process

**Naive approach**: Copy all parent pages → slow, wasteful

**COW approach**:
1. Initially share all pages (mark read-only)
2. On write attempt → **Copy page at that moment**
3. Only copy pages that are actually modified

**Advantages**:
- Faster process creation
- Less memory usage
- Many pages never modified (stay shared)

**Common use**: Fork + exec pattern
- Child often execs immediately → no point copying!
- COW makes fork nearly free

### Memory-Mapped Files

**Concept**: Map file into virtual address space

**Benefits**:
- File I/O through memory access (simpler)
- Shared memory between processes (map same file)
- Paging system handles actual I/O

**Example**:
```c
void *addr = mmap(NULL, filesize, PROT_READ|PROT_WRITE,
                  MAP_SHARED, fd, 0);
// Now access file via addr[offset]
```

### Kernel Memory Allocation

**Problem**: Kernel needs physically contiguous memory for DMA, buffers

**Solutions**:

#### 1. Buddy System
- Allocate memory in powers of 2
- Split/merge blocks as needed
- **Advantage**: Fast allocation/deallocation, low external fragmentation
- **Disadvantage**: Internal fragmentation (need 65KB? Get 128KB!)

#### 2. Slab Allocator
- Pre-allocate pools of commonly-used structures
- **Slab** = one or more contiguous pages
- **Cache** = collection of slabs for one object type
- **Advantage**: Very fast (no allocation overhead), no fragmentation
- **Used by**: Linux kernel for task_struct, inode, dentry, etc.

## Decision Guide

**Use FIFO**: Never (educational only)

**Use Optimal**: As benchmark to compare other algorithms

**Use LRU**: When can afford overhead and want best performance

**Use Second-Chance/Clock**: For real OS implementation (best trade-off)

**Use Enhanced Second-Chance**: When want to prefer clean pages (avoid write-back)

**Use Working Set Model**: To prevent thrashing in multiprogrammed systems

**Use PFF**: For simpler, more responsive thrashing prevention

**Use COW**: For fork(), shared libraries, memory-efficient sharing

**Use Memory-Mapped Files**: For shared memory IPC, file I/O convenience

## Performance Tips

### Minimizing Page Faults
1. **Increase locality**: Access data sequentially, keep related data together
2. **Adequate frames**: Working set should fit in allocated frames
3. **Prepaging**: Load predicted pages before needed
4. **Page size**: Balance internal fragmentation vs page fault overhead

### Optimizing Page Replacement
1. Use LRU approximation (Clock) for good performance with low overhead
2. Prefer clean pages (avoid disk writes on eviction)
3. Consider page usage patterns (frequent vs infrequent access)
4. Implement page buffering (keep recently freed pages in pool)

### Preventing Thrashing
1. Monitor page fault frequency
2. Adjust degree of multiprogramming dynamically
3. Ensure each process gets its working set
4. Use suspension (swapping) when total demand exceeds capacity
5. Prioritize interactive processes for better UX
