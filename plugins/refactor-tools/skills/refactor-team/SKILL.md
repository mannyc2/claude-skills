---
name: refactor-team
description: LOC-reducing refactoring for codebases. Finds dead code, duplicate blocks, and structural issues — then eliminates lines instead of shuffling them around. Spawns analyst and implementer agents for parallel work.
allowed-tools: mcp__refactor-tools__get_dependency_graph, mcp__refactor-tools__find_unused_exports, mcp__refactor-tools__get_complexity_report, mcp__refactor-tools__check_orphans, mcp__refactor-tools__diff_file_tree, mcp__refactor-tools__find_duplicates
---

# LOC-Reducing Refactoring Workflow

You are the lead orchestrator of a refactoring workflow focused on **reducing lines of code**. Every refactoring action must justify itself by eliminating more lines than it adds. Do not extract helpers that merely move code around.

**Prerequisite:** This workflow requires agent teams. Ensure `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` is set.

## Phase 1: PARALLEL SCAN

Spawn two analyst teammates to run simultaneously:

1. **analyst-structure** -- Send it the rootDir. It will run `get_dependency_graph` and `check_orphans`, then return a Structure Report.
2. **analyst-quality** -- Send it the rootDir. It will run `find_unused_exports`, `get_complexity_report`, and `find_duplicates`, then return a Quality Report including duplicate code blocks and LOC savings estimates.

Both agents work in parallel. Wait for both to complete before proceeding.

## Phase 2: SYNTHESIZE

Read both analyst reports and produce a unified analysis. Apply this **priority order** — higher-priority items yield guaranteed LOC reduction:

### Priority 1: Dead Code (guaranteed LOC reduction)
- Unused exports from `find_unused_exports`
- Every deletion is pure LOC savings
- Estimate: `-N` lines per unused export removed

### Priority 2: Duplicate Code (high-confidence LOC reduction)
- Duplicate blocks from `find_duplicates`
- Extract shared helper, replace N occurrences → net savings = `(N-1) × block_size - helper_overhead`
- Only recommend extraction if net savings > 0

### Priority 3: Structural Issues (health, not LOC)
- Circular dependencies, orphaned imports, poor module boundaries
- Fix for codebase health — no LOC claim

### Priority 4: Complexity (investigation only)
- Long or deeply-nested functions from `get_complexity_report`
- Do NOT automatically extract helpers. Instead, categorize the **cause**:
  - **Duplication within the function** → already covered by Priority 2
  - **Unnecessary branching / over-defensive code** → simplify in place
  - **Inherently complex domain logic** → leave it alone
- Only flag complexity for action if there's a concrete simplification

Present the synthesis to the user as a summary with estimated LOC impact per category.

## Phase 3: PLAN + PARTITION

### Create Refactoring Manifest

Based on the synthesized analysis, create a manifest where every change has a LOC estimate:

| Change | Files | LOC Impact |
|--------|-------|------------|
| Delete unused export `foo` | `src/bar.ts` | -12 |
| Extract duplicate block to shared helper | `a.ts`, `b.ts`, `c.ts` | +8 / -24 / net -16 |
| ... | ... | ... |

**Bottom line: estimated net LOC change = sum of all impacts.**

**Rule: Refuse any change that is net-positive in LOC** unless it fixes a correctness or structural issue (Priority 3). "Extract helper" refactors that are net-positive are banned.

### Partition into Independent Groups

Use the dependency graph to partition implementation into groups that can run in parallel:

- **Files that import each other go in the same group** -- No two implementers should share files
- **Foundation group** (if needed) -- Shared types, utilities, or new modules that other groups depend on. This group runs first.
- **Remaining groups** -- Roughly equal work volume per group, no cross-group file dependencies

### Get Approval

Present the full plan to the user with AskUserQuestion:
- Summary of all changes with LOC estimates
- **Expected net LOC change** (must be negative or zero)
- The parallel groups with file assignments
- Risk assessment
- Foundation group (runs first) vs parallel groups (run after)

**Do not proceed without explicit user approval.**

## Phase 4: PARALLEL IMPLEMENTATION

After approval, spawn refactor-implementer teammates:

### Foundation Group (if any)
Spawn a single implementer for the foundation group. This runs first and must complete before other groups start. Send it:
- Exact file list
- Specific changes from the approved plan
- Context about why these are foundation changes

### Parallel Groups
After the foundation group completes (or immediately if no foundation group), spawn implementers for remaining groups in parallel. Each gets:
- Exact file list (no overlap with other groups)
- Specific changes from the approved plan
- Instruction to report any out-of-scope dependencies

Wait for all implementers to complete.

## Phase 5: VERIFY

Run verification after all implementers finish:

1. **check_orphans** on the full rootDir -- must return 0 orphaned imports
2. **diff_file_tree** -- confirm changes match the manifest
3. **LOC audit** -- count insertions and deletions from `diff_file_tree`. Compute net LOC change. **Flag if net-positive** — this means the refactoring added more code than it removed, which violates the workflow's goal.
4. **`bun tsc --noEmit`** -- type checking must pass
5. **Run tests** if available (look for test scripts in package.json)

### If Verification Fails

- Identify the specific failure(s)
- Spawn a single refactor-implementer with the fix instructions
- Re-run verification after the fix
- Repeat until clean

Output a **VERIFICATION REPORT**:
- Orphaned imports: count (must be 0)
- File changes vs manifest: match status
- **Net LOC change: +N / -N** (target: negative)
- Type check: pass/fail
- Tests: pass/fail/skipped

---

## File Conflict Avoidance

The parallel implementation is safe because:

1. **Pre-partitioned by lead** -- Dependency graph ensures no two implementers share files
2. **Foundation-first ordering** -- Shared module creation completes before consumers start
3. **Implementers cannot touch out-of-scope files** -- They report cross-group needs to the lead
4. **Lead resolves conflicts** in the verification phase if any arise
