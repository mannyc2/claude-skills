import { z } from "zod";
import { getProject } from "../project.js";
import path from "path";
import crypto from "crypto";

export const duplicatesSchema = z.object({
  rootDir: z.string().describe("Root directory of the project to analyze"),
  minLines: z.number().optional().default(3).describe("Minimum block size to consider a duplicate (default 3)"),
  ignoreTests: z.boolean().optional().default(true).describe("Skip __tests__/ and *.test.* files"),
});

export type DuplicatesInput = z.infer<typeof duplicatesSchema>;

interface Occurrence {
  file: string;
  startLine: number;
  endLine: number;
  raw: string;
}

interface DuplicateBlock {
  pattern: string;
  lines: number;
  occurrences: Occurrence[];
  savings: number;
}

interface DuplicatesResult {
  duplicates: DuplicateBlock[];
  stats: {
    totalDuplicateBlocks: number;
    totalDuplicateLines: number;
    potentialSavings: number;
    filesWithDuplication: number;
  };
}

/** Normalize a line for comparison: strip whitespace, collapse string literals */
function normalizeLine(line: string): string {
  let s = line.trim();
  // Collapse string literals to a placeholder
  s = s.replace(/"[^"]*"/g, '""');
  s = s.replace(/'[^']*'/g, "''");
  s = s.replace(/`[^`]*`/g, "``");
  return s;
}

function hashBlock(normalizedLines: string[]): string {
  return crypto
    .createHash("sha256")
    .update(normalizedLines.join("\n"))
    .digest("hex");
}

export async function findDuplicates(input: DuplicatesInput): Promise<DuplicatesResult> {
  const project = getProject(input.rootDir);
  const sourceFiles = project.getSourceFiles();
  const minLines = input.minLines ?? 3;

  // Collect normalized lines per file
  const fileData: { relativePath: string; rawLines: string[]; normalizedLines: string[] }[] = [];

  for (const sf of sourceFiles) {
    const filePath = sf.getFilePath();
    const relativePath = path.relative(input.rootDir, filePath);

    // Skip test files if configured
    if (input.ignoreTests !== false) {
      if (
        relativePath.includes("__tests__") ||
        relativePath.includes(".test.") ||
        relativePath.includes(".spec.")
      ) {
        continue;
      }
    }

    const rawLines = sf.getFullText().split("\n");
    const normalizedLines = rawLines.map(normalizeLine);
    fileData.push({ relativePath, rawLines, normalizedLines });
  }

  // Sliding window: for each file, hash every window of size minLines..maxWindow
  // We cap max window to avoid combinatorial explosion
  const maxWindow = 50;
  const hashMap = new Map<string, Occurrence[]>();

  for (const { relativePath, rawLines, normalizedLines } of fileData) {
    for (let windowSize = minLines; windowSize <= Math.min(maxWindow, normalizedLines.length); windowSize++) {
      for (let start = 0; start <= normalizedLines.length - windowSize; start++) {
        const block = normalizedLines.slice(start, start + windowSize);

        // Skip blocks that are all empty/trivial (braces, imports only)
        const substantive = block.filter(
          (l) => l.length > 0 && l !== "{" && l !== "}" && l !== ");" && l !== ")"
        );
        if (substantive.length < minLines) continue;

        const h = hashBlock(block);
        const rawBlock = rawLines.slice(start, start + windowSize).join("\n");

        if (!hashMap.has(h)) {
          hashMap.set(h, []);
        }
        hashMap.get(h)!.push({
          file: relativePath,
          startLine: start + 1,
          endLine: start + windowSize,
          raw: rawBlock,
        });
      }
    }
  }

  // Filter to blocks that appear 2+ times, deduplicate overlaps
  const rawDuplicates: { hash: string; occurrences: Occurrence[]; lines: number }[] = [];

  for (const [hash, occurrences] of hashMap) {
    if (occurrences.length < 2) continue;

    // Deduplicate: if same file + overlapping range, keep the first
    const deduped: Occurrence[] = [];
    for (const occ of occurrences) {
      const overlaps = deduped.some(
        (d) =>
          d.file === occ.file &&
          occ.startLine <= d.endLine &&
          occ.endLine >= d.startLine
      );
      if (!overlaps) {
        deduped.push(occ);
      }
    }

    if (deduped.length >= 2) {
      rawDuplicates.push({
        hash,
        occurrences: deduped,
        lines: deduped[0].endLine - deduped[0].startLine + 1,
      });
    }
  }

  // Remove smaller blocks that are subsets of larger detected blocks
  // Sort by size descending so we process largest first
  rawDuplicates.sort((a, b) => b.lines - a.lines);

  const coveredRanges = new Map<string, { start: number; end: number }[]>();
  const filtered: typeof rawDuplicates = [];

  for (const dup of rawDuplicates) {
    // Check if ALL occurrences are already covered by a larger block
    const allCovered = dup.occurrences.every((occ) => {
      const ranges = coveredRanges.get(occ.file) || [];
      return ranges.some((r) => occ.startLine >= r.start && occ.endLine <= r.end);
    });

    if (allCovered) continue;

    filtered.push(dup);

    // Mark these ranges as covered
    for (const occ of dup.occurrences) {
      if (!coveredRanges.has(occ.file)) {
        coveredRanges.set(occ.file, []);
      }
      coveredRanges.get(occ.file)!.push({ start: occ.startLine, end: occ.endLine });
    }
  }

  // Build result
  const duplicates: DuplicateBlock[] = filtered.map((d) => ({
    pattern: d.occurrences[0].raw,
    lines: d.lines,
    occurrences: d.occurrences,
    savings: (d.occurrences.length - 1) * d.lines,
  }));

  // Compute stats
  const filesWithDups = new Set<string>();
  let totalDuplicateLines = 0;
  let potentialSavings = 0;

  for (const dup of duplicates) {
    potentialSavings += dup.savings;
    totalDuplicateLines += dup.lines * dup.occurrences.length;
    for (const occ of dup.occurrences) {
      filesWithDups.add(occ.file);
    }
  }

  return {
    duplicates,
    stats: {
      totalDuplicateBlocks: duplicates.length,
      totalDuplicateLines,
      potentialSavings,
      filesWithDuplication: filesWithDups.size,
    },
  };
}
