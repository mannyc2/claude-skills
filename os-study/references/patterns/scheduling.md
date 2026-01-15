# CPU Scheduling Pattern Guide

Quick reference for CPU scheduling algorithms, criteria, and trade-offs.

## Algorithm Comparison Matrix

| Algorithm | Preemptive | Avg Wait Time | Starvation Risk | Context Switch Overhead | Best Use Case |
|-----------|------------|---------------|-----------------|------------------------|---------------|
| FCFS | No | High (convoy effect) | None | Low | Batch systems, predictable workloads |
| SJF (non-preemptive) | No | **Optimal** (minimum) | Yes (long jobs) | Low | Known burst times, batch processing |
| SRTF (preemptive SJF) | Yes | Near-optimal | Yes (long jobs) | Medium | Time-sharing with known bursts |
| Priority | Either | Variable | **Yes** (low priority) | Medium | Systems with importance levels |
| Round Robin | Yes | Fair | None | **High** (if small quantum) | Time-sharing, interactive systems |
| Multilevel Queue | Yes | Depends on queues | Possible | Medium | Mixed workload types |
| Multilevel Feedback | Yes | Adaptive | Rare (with aging) | Medium-High | General-purpose OS |
| Rate Monotonic | Yes | N/A | No (if schedulable) | Low | **Hard real-time** (shorter period = higher priority) |
| EDF | Yes | N/A | No (if schedulable) | Medium | **Hard real-time** (earliest deadline first) |

## Scheduling Criteria

**Optimization Goals:**
- **CPU Utilization**: Keep CPU busy (target: 40-90% depending on system)
- **Throughput**: Number of processes completed per time unit
- **Turnaround Time**: Total time from submission to completion
- **Waiting Time**: Time spent in ready queue
- **Response Time**: Time from request until first response (critical for interactive)

**Key Insight**: No single algorithm optimizes all criteria. Must choose based on system requirements.

## Key Concepts

### 1. Convoy Effect (FCFS Problem)
**What**: Short processes stuck behind long CPU-bound process
**Why it matters**: Destroys throughput and response time
**Example**: One CPU-bound process (100ms) ahead of 10 I/O-bound processes (1ms each)
**Result**: Average wait = (0 + 100 + 101 + ... + 109) / 11 ≈ 54.5ms instead of ~5ms with better scheduling

### 2. SJF Optimality
**Theorem**: SJF minimizes average waiting time for a given set of processes
**Proof sketch**: Any reordering that swaps shorter job later increases total wait
**Limitation**: Requires knowing future CPU burst times (use exponential averaging to predict)

### 3. Time Quantum Selection (Round Robin)
**Trade-off**:
- **Too large** → Degenerates to FCFS, poor response time
- **Too small** → Excessive context switching overhead dominates
- **Rule of thumb**: 80% of CPU bursts should be shorter than quantum
- **Typical values**: 10-100ms (context switch typically <10μs)

**Example**:
- Quantum = 1ms, context switch = 0.1ms → 9.1% overhead
- Quantum = 10ms, context switch = 0.1ms → 0.99% overhead

## Preemptive vs Non-Preemptive

| Aspect | Non-Preemptive | Preemptive |
|--------|----------------|------------|
| **Definition** | Process runs until blocks or terminates | Can be interrupted by scheduler |
| **When decisions happen** | Only at (1) termination or (2) waiting | Also at (3) ready→running, (4) waiting→ready |
| **Advantages** | Simpler, no race conditions | Better response time, fairness |
| **Disadvantages** | Poor response, monopolization | Shared data races, kernel issues |
| **Use cases** | Old batch systems | Modern multiprogrammed systems |

## Starvation and Aging

**Starvation Problem**: Low-priority/long processes may never execute
**Occurs in**: Priority scheduling, SJF/SRTF

**Aging Solution**: Gradually increase priority of waiting processes
**Implementation**: Priority = Base_Priority + (Wait_Time / Constant)

## Real-Time Scheduling

### Hard vs Soft Real-Time
- **Soft Real-Time**: No guarantees, best effort (e.g., video streaming)
- **Hard Real-Time**: Must meet deadlines or system fails (e.g., airbag controller)

### Periodic Task Parameters
- **Processing time** (t): CPU time needed
- **Deadline** (d): When task must complete
- **Period** (p): Time between task instances
- **Constraint**: 0 ≤ t ≤ d ≤ p

### Rate Monotonic vs EDF

| Property | Rate Monotonic (RM) | Earliest Deadline First (EDF) |
|----------|---------------------|-------------------------------|
| **Priority assignment** | Static (shorter period = higher priority) | Dynamic (earliest deadline = higher priority) |
| **Preemptive** | Yes | Yes |
| **Optimality** | Optimal among static priority | Optimal among all algorithms |
| **CPU Utilization bound** | ≤ n(2^(1/n) - 1) ≈ 69% for many tasks | ≤ 100% |
| **Complexity** | Simple, predictable | More complex overhead |
| **When it fails** | Misses deadlines even when schedulable by EDF | Only fails when truly unschedulable |

## Common Exam Questions

### "Trace Round Robin with quantum=4 on processes: P1(24), P2(3), P3(3)"

**Arrival order**: P1, P2, P3 (all arrive at t=0)
**Burst times**: P1=24, P2=3, P3=3

**Gantt Chart**:
```
| P1  | P2  | P3  | P1  | P1  | P1  | P1  | P1  |
0     4     7    10    14    18    22    26    30
```

**Calculations**:
- **P1**: Waiting time = (10-4) + (14-10) + (18-14) + (22-18) + (26-22) = 16ms
  - Runs at: 0-4, 10-14, 14-18, 18-22, 22-26, 26-30
  - Waits during: 4-10 (P2 and P3), then runs continuously
- **P2**: Waiting time = 4ms (waits 0-4 while P1 runs)
- **P3**: Waiting time = 7ms (waits 0-4 for P1, 4-7 for P2)

**Average waiting time** = (16 + 4 + 7) / 3 = **9ms**

**Note**: Same processes with FCFS = (0 + 24 + 27) / 3 = 17ms (much worse!)

### "Calculate average wait time for FCFS vs SJF"

**Given**: P1(6), P2(8), P3(7), P4(3) — all arrive at t=0

**FCFS (First-Come, First-Served)** — order: P1, P2, P3, P4
```
| P1 | P2 | P3 | P4 |
0    6    14   21   24
```
- Waiting: P1=0, P2=6, P3=14, P4=21
- **Average = (0+6+14+21)/4 = 10.25ms**

**SJF (Shortest-Job-First)** — order: P4, P1, P3, P2
```
| P4 | P1 | P3 | P2 |
0    3    9    16   24
```
- Waiting: P4=0, P1=3, P3=9, P2=16
- **Average = (0+3+9+16)/4 = 7ms**

**Improvement**: SJF reduces average wait time by 32%

### "Why does SJF minimize average waiting time?"

**Intuitive Proof**:
Consider two jobs J1 (short) and J2 (long) where t1 < t2.

**Order 1** (J1 then J2):
- Wait times: W1=0, W2=t1
- Total wait = 0 + t1 = t1

**Order 2** (J2 then J1):
- Wait times: W1=t2, W2=0
- Total wait = t2 + 0 = t2

Since t1 < t2, Order 1 (shorter job first) produces less total waiting time.

**Extension**: This applies to any set of jobs — always putting shorter jobs first minimizes sum (and therefore average) of waiting times.

### "When would Priority scheduling cause starvation?"

**Starvation occurs when**: Continuous stream of high-priority processes prevents low-priority processes from ever executing.

**Example**:
- Process P1: Priority 1 (highest), burst 100ms
- Process P2: Priority 5 (lowest), burst 10ms
- New high-priority processes arrive every 50ms

Result: P2 never runs because CPU always busy with priority 1-4 processes.

**Solutions**:
1. **Aging**: Increase priority as wait time increases
   - Example: Priority(t) = Base_Priority - (Wait_Time / 100ms)
2. **Multilevel Feedback Queue**: Automatically boost priority of long-waiting processes
3. **Time-slice guarantees**: Reserve minimum CPU percentage for each priority level

### "Trace SRTF (Shortest Remaining Time First)"

**Given**:

| Process | Arrival Time | Burst Time |
|---------|--------------|------------|
| P1 | 0 | 8 |
| P2 | 1 | 4 |
| P3 | 2 | 9 |
| P4 | 3 | 5 |

**Execution Timeline**:
- **t=0**: Only P1 available, remaining=8 → **Run P1**
- **t=1**: P2 arrives (remaining=4), P1 (remaining=7) → **Preempt to P2** (4 < 7)
- **t=2**: P3 arrives (remaining=9), P2 (remaining=3) → **Continue P2** (3 < 9)
- **t=3**: P4 arrives (remaining=5), P2 (remaining=2) → **Continue P2** (2 < 5)
- **t=5**: P2 completes, compare P1(7), P3(9), P4(5) → **Run P4**
- **t=10**: P4 completes, compare P1(7), P3(9) → **Run P1**
- **t=17**: P1 completes → **Run P3**
- **t=26**: P3 completes

**Gantt Chart**:
```
| P1 | P2 | P4 | P1 | P3 |
0    1    5   10   17   26
```

**Waiting Times**:
- P1: (10-1) = 9ms (interrupted at t=1, resumes at t=10)
- P2: (1-1) = 0ms (runs immediately when arrives)
- P3: (17-2) = 15ms (arrives at 2, starts at 17)
- P4: (5-3) = 2ms (arrives at 3, starts at 5)

**Average wait = (9+0+15+2)/4 = 6.5ms**

### "Compare Rate Monotonic vs EDF for real-time tasks"

**Scenario**: Two periodic tasks
- Task T1: period=50ms, execution=20ms
- Task T2: period=100ms, execution=35ms

**CPU Utilization**: U = (20/50) + (35/100) = 0.4 + 0.35 = 0.75 = 75%

**Rate Monotonic**:
- Assigns priorities: T1 (higher, shorter period) > T2
- Schedulability test: U ≤ 2(2^(1/2) - 1) ≈ 0.828
- Result: **Schedulable** (0.75 < 0.828)

**EDF**:
- Assigns priorities dynamically based on deadlines
- Schedulability test: U ≤ 1.0
- Result: **Schedulable** (0.75 < 1.0)

**When Rate Monotonic Fails but EDF Succeeds**:
- Task T1: period=50ms, execution=25ms
- Task T2: period=75ms, execution=30ms
- U = (25/50) + (30/75) = 0.5 + 0.4 = 0.9 = 90%

Rate Monotonic: 0.9 > 0.828 → **May fail** (actually does fail for this example)
EDF: 0.9 < 1.0 → **Schedulable**

**Trade-off**: EDF achieves higher CPU utilization but has more runtime overhead for priority recalculation.

## Advanced Concepts

### Multilevel Feedback Queue (MLFQ)

**Idea**: Automatically adjust priority based on behavior
**Mechanism**: Multiple queues with different priorities and time quantums
- New processes enter highest priority queue (short quantum)
- If process uses full quantum → demote to lower priority queue
- If process blocks before quantum expires → keep or boost priority

**Advantage**: Approximates SJF without knowing burst times
**Prevents starvation**: Aging gradually boosts long-waiting processes

### Linux CFS (Completely Fair Scheduler)

**Core Concept**: Give each process fair share of CPU proportional to its priority (nice value)

**Virtual Runtime (vruntime)**:
- Tracks how much CPU time process has received, weighted by priority
- Lower priority processes accumulate vruntime faster
- Scheduler always picks process with **lowest vruntime**

**Data Structure**: Red-black tree (O(log n) selection)
- Leftmost node = process with smallest vruntime = next to run

**Advantage**: Provides fairness while handling different priorities elegantly

## Decision Guide

**Choose FCFS when**:
- Batch system with predictable, similar-length jobs
- Simplicity more important than performance
- Minimal context switching overhead required

**Choose SJF/SRTF when**:
- Can estimate/know CPU burst times
- Minimizing average wait time is critical
- Acceptable to potentially starve long jobs

**Choose Priority when**:
- Jobs have inherent importance levels
- Can implement aging to prevent starvation
- Real-time requirements with static priorities

**Choose Round Robin when**:
- Interactive/time-sharing system
- Fairness and response time critical
- Can tolerate context switch overhead

**Choose Multilevel Feedback Queue when**:
- General-purpose operating system
- Mixed workload (CPU-bound and I/O-bound)
- Want automatic adaptation without manual tuning

**Choose Rate Monotonic when**:
- Hard real-time system
- Static priority assignment acceptable
- Tasks have predictable periods
- CPU utilization < 69-83%

**Choose EDF when**:
- Hard real-time system
- Need maximum CPU utilization (up to 100%)
- Can handle dynamic priority overhead
- Tasks have varying deadlines

## Performance Calculation Tips

### Gantt Chart Construction
1. Draw timeline starting at t=0
2. For preemptive: Check for arrivals/preemptions at each time unit
3. For non-preemptive: Process runs to completion before next selection
4. Mark all process execution intervals

### Waiting Time Calculation
**Formula**: Waiting Time = (Start Time - Arrival Time) + (Sum of interrupt durations)

**For each process**:
1. Identify all time intervals when process is ready but not running
2. Sum those intervals
3. Or: (Turnaround Time) - (Burst Time)

### Average Metrics
- Average Waiting Time = (Sum of all wait times) / (Number of processes)
- Average Turnaround Time = (Sum of all turnaround times) / (Number of processes)
- Throughput = (Number of processes completed) / (Total time elapsed)
