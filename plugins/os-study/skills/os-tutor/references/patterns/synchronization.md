# Synchronization Tools Pattern Guide

Quick reference for process synchronization mechanisms, critical section solutions, and classic problems.

## Synchronization Mechanism Comparison

| Mechanism | Complexity | Busy Wait | User/Kernel | Use Case | Deadlock Risk |
|-----------|------------|-----------|-------------|----------|---------------|
| **Peterson's Solution** | High (software) | Yes | User | 2-process only, educational | None |
| **test_and_set** | Medium (hardware) | Yes (spinlock) | Kernel | Short critical sections | Low |
| **compare_and_swap** | Medium (hardware) | Yes (spinlock) | Kernel | Short critical sections, lock-free | Low |
| **Mutex Lock** | Low (API) | Yes (spinlock) | Both | Basic mutual exclusion | Low |
| **Semaphore (Binary)** | Low (API) | No (sleep/wakeup) | Both | Mutex + signaling | **Medium** |
| **Semaphore (Counting)** | Low (API) | No (sleep/wakeup) | Both | Resource counting | **Medium** |
| **Monitor** | Medium (language) | No | Language-level | Complex synchronization | Low |
| **Condition Variable** | Medium | No | Both | Waiting for events | Low (with monitor) |

## Critical Section Problem Requirements

**Three Requirements** (all must be satisfied):

### 1. Mutual Exclusion
**Definition**: If process Pi is executing in critical section, no other process can be in **its** critical section
**Why**: Prevents race conditions and data corruption
**Test**: Can two processes ever be in CS simultaneously?

### 2. Progress
**Definition**: If no process is in CS and some want to enter, selection of next process cannot be postponed indefinitely
**Why**: Prevents system from freezing due to poor coordination
**Violates**: If entry decision depends on process not in entry/CS section

### 3. Bounded Waiting
**Definition**: After process requests entry, there's a limit on how many times others can enter CS before it
**Why**: Prevents starvation
**Test**: Can a process be blocked forever while others repeatedly enter CS?

## Key Concepts

### 1. Race Condition
**Definition**: Multiple processes access shared data concurrently, and outcome depends on execution order

**Classic Example** (Producer-Consumer counter):
```c
// Producer                   // Consumer
counter++;                    counter--;

// Expands to:                // Expands to:
register1 = counter           register2 = counter
register1 = register1 + 1     register2 = register2 - 1
counter = register1           counter = register2
```

**Interleaving Problem**:
Initial counter = 5
1. Producer: register1 = 5
2. Producer: register1 = 6
3. Consumer: register2 = 5
4. Consumer: register2 = 4
5. Producer: counter = 6
6. Consumer: counter = 4  ← **Should be 5!**

### 2. Atomic Operations (Hardware Support)
**Definition**: Operation that completes without interruption

**test_and_set()**:
```c
boolean test_and_set(boolean *target) {
    boolean rv = *target;  // Read old value
    *target = TRUE;         // Set to TRUE
    return rv;              // Return old value
}
```
- **Atomicity**: All three steps execute as one indivisible operation
- **Returns**: Previous value (TRUE if locked, FALSE if available)
- **Usage**: Spin while test_and_set returns TRUE

**compare_and_swap()**:
```c
int compare_and_swap(int *value, int expected, int new_value) {
    int temp = *value;
    if (*value == expected)
        *value = new_value;
    return temp;
}
```
- **Atomicity**: Entire operation is indivisible
- **Conditional**: Only updates if current value matches expected
- **Usage**: Lock-free algorithms, optimistic concurrency

### 3. Busy Waiting (Spinlock) vs Sleep/Wakeup

| Aspect | Spinlock (Busy Wait) | Sleep/Wakeup |
|--------|----------------------|--------------|
| **CPU usage while waiting** | Wastes CPU cycles | Yields CPU to others |
| **Good for** | Very short wait times, multiprocessor | Longer waits, uniprocessor |
| **Context switch** | None | Two (sleep + wake) |
| **Implementation** | Hardware atomic ops | OS scheduler support |
| **Example** | Mutex lock | Semaphore with queue |

**When to use spinlock**: Critical section duration < 2 context switches

## Peterson's Solution (2-Process)

**Shared variables**:
```c
boolean flag[2];  // flag[i] = true means Pi ready to enter CS
int turn;         // Whose turn it is
```

**Process i code**:
```c
do {
    flag[i] = TRUE;        // I want to enter
    turn = j;               // Let other go first (courtesy)
    while (flag[j] && turn == j)
        ;                   // Busy wait

    /* Critical Section */

    flag[i] = FALSE;       // I'm leaving

    /* Remainder Section */
} while (TRUE);
```

**Why it works**:
- **Mutual Exclusion**: Pi enters only if `flag[j]==FALSE` OR `turn==i`
  - If both want to enter, `turn` can only be i OR j (not both)
- **Progress**: If Pj not interested (`flag[j]==FALSE`), Pi enters immediately
- **Bounded Waiting**: After Pi sets `turn=j`, if Pj enters and exits, it sets `flag[j]=FALSE`, allowing Pi to enter next

**Limitation**: Only works for exactly 2 processes

## Semaphores

**Definition**: Integer variable accessed only through atomic `wait()` and `signal()` operations

### Binary Semaphore (Mutex)
- Value: 0 or 1
- **Use**: Mutual exclusion

### Counting Semaphore
- Value: 0 to N
- **Use**: Resource counting (e.g., available buffers)

**Operations**:
```c
wait(S) {          // Also called P() or down()
    while (S <= 0)
        ;  // Busy wait (or block process)
    S--;
}

signal(S) {        // Also called V() or up()
    S++;
}
```

**With sleep/wakeup (no busy waiting)**:
```c
typedef struct {
    int value;
    struct process *list;  // Waiting queue
} semaphore;

wait(semaphore *S) {
    S->value--;
    if (S->value < 0) {
        add this process to S->list;
        block();  // Sleep
    }
}

signal(semaphore *S) {
    S->value++;
    if (S->value <= 0) {  // Processes waiting
        remove a process P from S->list;
        wakeup(P);
    }
}
```

### Deadlock with Semaphores

**Scenario**: Two semaphores S and Q

```c
// Process P0              // Process P1
wait(S);                   wait(Q);
wait(Q);                   wait(S);
...                        ...
signal(S);                 signal(Q);
signal(Q);                 signal(S);
```

**Deadlock**: P0 holds S, wants Q; P1 holds Q, wants S → **Both blocked forever**

**Solution**: Enforce ordering — always acquire S before Q

## Monitors

**Definition**: High-level synchronization construct
- Abstract data type with:
  - Shared data variables (private)
  - Procedures that operate on data
  - Initialization code
- **Key property**: Only one process can be active in monitor at a time (automatic mutual exclusion)

**Syntax**:
```c
monitor MonitorName {
    // Shared variable declarations
    int data;

    procedure P1(...) {
        // Operations on shared data
    }

    procedure Pn(...) {
        // Operations on shared data
    }

    initialization_code() {
        // Initialize shared variables
    }
}
```

**Advantages over Semaphores**:
1. **Safer**: Mutual exclusion automatic (can't forget to acquire lock)
2. **Clearer**: Structure makes intent obvious
3. **Compiler-checked**: Syntax errors caught at compile time

**Disadvantage**: Not powerful enough alone — need condition variables for complex synchronization

### Condition Variables

**Purpose**: Allow process to wait for condition to become true

**Operations**:
```c
x.wait()    // Suspend calling process until x.signal()
x.signal()  // Resume one process waiting on x (if any)
```

**Signal-and-Wait vs Signal-and-Continue**:
- **Signal-and-Wait**: Signaling process waits, signaled process runs
- **Signal-and-Continue**: Signaling process continues, signaled waits

**Choice depends on language/implementation** (Mesa uses signal-and-continue)

## Classic Synchronization Problems

### 1. Bounded-Buffer (Producer-Consumer)

**Setup**: n buffers, mutex for CS, counting semaphores for full/empty tracking

**Shared Resources**:
```c
semaphore mutex = 1;    // Mutex for buffer access
semaphore full = 0;     // Count of full buffers
semaphore empty = n;    // Count of empty buffers
```

**Producer**:
```c
do {
    // Produce item
    wait(empty);        // Wait for empty slot
    wait(mutex);        // Enter critical section
    // Add item to buffer
    signal(mutex);      // Leave critical section
    signal(full);       // Increment full count
} while (TRUE);
```

**Consumer**:
```c
do {
    wait(full);         // Wait for full slot
    wait(mutex);        // Enter critical section
    // Remove item from buffer
    signal(mutex);      // Leave critical section
    signal(empty);      // Increment empty count
    // Consume item
} while (TRUE);
```

**Key Insight**: `wait(empty)` and `wait(full)` MUST come before `wait(mutex)` to avoid deadlock!

### 2. Readers-Writers Problem

**Constraint**:
- Multiple readers can read simultaneously
- Only one writer can write (exclusive access)
- No readers when writer is writing

**Shared Resources**:
```c
semaphore rw_mutex = 1;  // Mutex for writers
semaphore mutex = 1;     // Mutex for read_count
int read_count = 0;      // Number of active readers
```

**Writer**:
```c
wait(rw_mutex);
// Writing performed
signal(rw_mutex);
```

**Reader**:
```c
wait(mutex);
read_count++;
if (read_count == 1)     // First reader
    wait(rw_mutex);       // Lock out writers
signal(mutex);

// Reading performed

wait(mutex);
read_count--;
if (read_count == 0)     // Last reader
    signal(rw_mutex);     // Allow writers
signal(mutex);
```

**Starvation Issues**:
- **First variation** (above): Writers may starve if readers keep arriving
- **Second variation**: Readers may starve if writers prioritized

### 3. Dining Philosophers Problem

**Setup**: 5 philosophers, 5 chopsticks (one between each pair)
**Rule**: Need **both** adjacent chopsticks to eat

**Naive Solution (DEADLOCKS)**:
```c
do {
    wait(chopstick[i]);
    wait(chopstick[(i+1) % 5]);

    // Eat

    signal(chopstick[i]);
    signal(chopstick[(i+1) % 5]);

    // Think
} while (TRUE);
```

**Deadlock**: All 5 philosophers pick up left chopstick → all wait for right → **deadlock!**

**Monitor Solution** (prevents deadlock):
```c
monitor DiningPhilosophers {
    enum {THINKING, HUNGRY, EATING} state[5];
    condition self[5];

    void pickup(int i) {
        state[i] = HUNGRY;
        test(i);  // Try to get both chopsticks
        if (state[i] != EATING)
            self[i].wait();
    }

    void putdown(int i) {
        state[i] = THINKING;
        test((i+4) % 5);  // Check left neighbor
        test((i+1) % 5);  // Check right neighbor
    }

    void test(int i) {
        if (state[(i+4) % 5] != EATING &&
            state[i] == HUNGRY &&
            state[(i+1) % 5] != EATING) {
            state[i] = EATING;
            self[i].signal();
        }
    }
}
```

**Why no deadlock**: `test()` only sets EATING if **both** neighbors not eating (atomic check)

## Common Exam Questions

### "Trace Peterson's solution with interleaved execution"

**Initial**: `flag[0]=FALSE, flag[1]=FALSE, turn=?`

**Scenario**: Both P0 and P1 want to enter CS

| Time | P0 Action | P1 Action | flag[0] | flag[1] | turn | Result |
|------|-----------|-----------|---------|---------|------|--------|
| t0 | `flag[0]=TRUE` | - | TRUE | FALSE | ? | - |
| t1 | `turn=1` | - | TRUE | FALSE | 1 | - |
| t2 | Check: `flag[1] && turn==1` → FALSE | - | TRUE | FALSE | 1 | **P0 enters CS** |
| t3 | (In CS) | `flag[1]=TRUE` | TRUE | TRUE | 1 | - |
| t4 | (In CS) | `turn=0` | TRUE | TRUE | 0 | - |
| t5 | (In CS) | Check: `flag[0] && turn==0` → TRUE | TRUE | TRUE | 0 | **P1 waits** |
| t6 | Exit CS, `flag[0]=FALSE` | (Waiting) | FALSE | TRUE | 0 | - |
| t7 | - | Check now FALSE | FALSE | TRUE | 0 | **P1 enters CS** |

**Mutual Exclusion holds**: When both want CS, `turn` breaks tie

### "When would you use a semaphore vs a mutex?"

| Use Case | Choose |Reason |
|----------|--------|-------|
| Simple lock (one resource) | **Mutex** | Simpler, clearer intent |
| Signaling between processes | **Semaphore** | Can signal without holding lock |
| Resource pool (n instances) | **Counting Semaphore** | Tracks available count |
| Very short critical section (multiprocessor) | **Spinlock** | Avoid context switch overhead |
| Long critical section | **Semaphore (blocking)** | Yield CPU instead of spin |
| Complex synchronization logic | **Monitor + Condition Variables** | Safer, more structured |

**Example: Signaling with Semaphore**:
```c
semaphore synch = 0;  // Initially 0

// Process P1
S1;
signal(synch);  // Signal completion

// Process P2
wait(synch);   // Wait for P1's signal
S2;            // Execute after S1
```
*This pattern impossible with simple mutex!*

### "Why are monitors safer than semaphores?"

**Semaphore Problems**:
1. **Easy to forget**: Omitting `wait()` or `signal()` causes race conditions
2. **Wrong order**: `signal()` before `wait()` breaks synchronization
3. **Deadlock**: Wrong order of multiple semaphores causes deadlock
4. **No compiler help**: Errors only appear at runtime

**Example of Bad Semaphore Code**:
```c
// Mistake 1: signal before wait
signal(mutex);
critical_section();
wait(mutex);  // ← Wrong order!

// Mistake 2: Double wait
wait(mutex);
wait(mutex);  // ← Deadlock!
critical_section();

// Mistake 3: Forgot wait
critical_section();  // ← No protection!
signal(mutex);
```

**Monitor Advantages**:
1. **Automatic mutual exclusion**: Can't forget to lock
2. **Structured**: Clear entry/exit points
3. **Compiler-enforced**: Syntax errors caught early
4. **Intent clear**: Structure shows synchronization purpose

### "Solve Producer-Consumer using semaphores"

**Given**: Buffer of size 5

**Solution**:
```c
#define N 5
semaphore mutex = 1;    // Protects buffer access
semaphore empty = N;    // Count of empty slots (initially N)
semaphore full = 0;     // Count of full slots (initially 0)

void producer() {
    while (TRUE) {
        item = produce_item();

        wait(empty);     // Decrement empty count (may block)
        wait(mutex);     // Lock buffer
        insert_item(item);
        signal(mutex);   // Unlock buffer
        signal(full);    // Increment full count
    }
}

void consumer() {
    while (TRUE) {
        wait(full);      // Decrement full count (may block)
        wait(mutex);     // Lock buffer
        item = remove_item();
        signal(mutex);   // Unlock buffer
        signal(empty);   // Increment empty count

        consume_item(item);
    }
}
```

**Why this order?**:
- `wait(empty/full)` BEFORE `wait(mutex)`: Prevents holding mutex while blocked
- If reversed: Producer holds mutex while waiting for empty → Consumer can't remove items → **Deadlock**

**Trace Example** (N=2, initially empty):

| Step | Action | empty | full | mutex | Buffer Count |
|------|--------|-------|------|-------|--------------|
| 1 | Producer: wait(empty) | 1 | 0 | 1 | 0 |
| 2 | Producer: wait(mutex) | 1 | 0 | 0 | 0 |
| 3 | Producer: insert | 1 | 0 | 0 | 1 |
| 4 | Producer: signal(mutex) | 1 | 0 | 1 | 1 |
| 5 | Producer: signal(full) | 1 | 1 | 1 | 1 |
| 6 | Consumer: wait(full) | 1 | 0 | 1 | 1 |
| 7 | Consumer: wait(mutex) | 1 | 0 | 0 | 1 |
| 8 | Consumer: remove | 1 | 0 | 0 | 0 |
| 9 | Consumer: signal(mutex) | 1 | 0 | 1 | 0 |
| 10 | Consumer: signal(empty) | 2 | 0 | 1 | 0 |

### "Explain priority inversion and the solution"

**Priority Inversion Problem**:
1. Low-priority process L holds lock
2. High-priority process H needs same lock
3. Medium-priority process M preempts L
4. Result: H blocked by M (indirectly), even though H has higher priority!

**Example Timeline**:
```
t0: L acquires lock
t1: H arrives, blocks on lock (waiting for L)
t2: M arrives, preempts L (M has higher priority than L)
t3: M runs while H waits (INVERSION: Medium priority blocking High)
t4: M completes
t5: L resumes, eventually releases lock
t6: H finally acquires lock
```

**Solution: Priority Inheritance Protocol**:
- When H blocks on lock held by L, temporarily boost L's priority to H's priority
- L runs at high priority until it releases lock
- Prevents M from preempting L
- After release, L returns to original priority

**Mars Pathfinder** (real incident):
- High-priority task blocked by low-priority task
- Medium-priority tasks kept interrupting
- System watchdog timer reset spacecraft!
- Fixed by enabling priority inheritance

## Advanced Concepts

### Adaptive Mutex (Solaris)
**Idea**: Choose spin vs sleep based on lock holder state
- If holder running on another CPU → **Spin** (likely releases soon)
- If holder not running → **Sleep** (will take time to schedule)

**Advantage**: Gets benefits of both spinlock (low latency) and blocking (CPU efficiency)

### Transactional Memory
**Concept**: Execute critical section as transaction
- If conflicts detected → rollback and retry
- If no conflicts → commit atomically

**Advantage**: No manual locking, better composability
**Disadvantage**: Not all operations can be rolled back (I/O)

### Read-Write Locks
**Optimization** for readers-writers:
- Shared mode: Multiple readers allowed
- Exclusive mode: Single writer only

**Advantage**: Better performance when reads dominate

## Decision Guide

**Use Peterson's Solution**: Never (educational only, doesn't scale beyond 2 processes)

**Use test_and_set/compare_and_swap**: When implementing low-level synchronization primitives

**Use Mutex**: Simple mutual exclusion, short critical sections

**Use Binary Semaphore**: Signaling between processes, synchronization beyond simple locks

**Use Counting Semaphore**: Managing pool of identical resources

**Use Monitor**: Complex synchronization logic, multiple condition variables, language supports it

**Use Condition Variables**: Waiting for specific conditions, event notification

**Use Read-Write Locks**: Read-heavy workloads (many readers, few writers)
