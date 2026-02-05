import { z } from "zod";
import { $ } from "bun";

export const fileDiffSchema = z.object({
  rootDir: z.string().describe("Root directory of the project"),
  compareRef: z.string().optional().default("HEAD").describe("Git ref to compare against (default: HEAD)"),
  pathPrefix: z.string().optional().describe("Filter to files under this path prefix"),
});

export type FileDiffInput = z.infer<typeof fileDiffSchema>;

interface FileChange {
  path: string;
  status: "added" | "deleted" | "modified" | "renamed";
  oldPath?: string; // For renames
}

interface FileDiffResult {
  changes: {
    added: string[];
    deleted: string[];
    modified: string[];
    renamed: Array<{ from: string; to: string }>;
  };
  stats: {
    totalChanges: number;
    addedCount: number;
    deletedCount: number;
    modifiedCount: number;
    renamedCount: number;
  };
}

export async function diffFileTree(input: FileDiffInput): Promise<FileDiffResult> {
  const changes: FileChange[] = [];

  try {
    // Get staged and unstaged changes
    const stagedResult = await $`cd ${input.rootDir} && git diff --name-status --cached ${input.compareRef}`.text();
    const unstagedResult = await $`cd ${input.rootDir} && git diff --name-status`.text();

    // Also get untracked files
    const untrackedResult = await $`cd ${input.rootDir} && git ls-files --others --exclude-standard`.text();

    const processedPaths = new Set<string>();

    // Parse staged changes
    for (const line of stagedResult.split("\n").filter(Boolean)) {
      const parts = line.split("\t");
      if (parts.length < 2) continue;

      const status = parts[0];
      const filePath = parts[1];

      if (input.pathPrefix && !filePath.startsWith(input.pathPrefix)) {
        continue;
      }

      processedPaths.add(filePath);

      if (status === "A") {
        changes.push({ path: filePath, status: "added" });
      } else if (status === "D") {
        changes.push({ path: filePath, status: "deleted" });
      } else if (status === "M") {
        changes.push({ path: filePath, status: "modified" });
      } else if (status.startsWith("R")) {
        const oldPath = parts[1];
        const newPath = parts[2];
        changes.push({ path: newPath, status: "renamed", oldPath });
        processedPaths.add(newPath);
      }
    }

    // Parse unstaged changes (only add if not already processed)
    for (const line of unstagedResult.split("\n").filter(Boolean)) {
      const parts = line.split("\t");
      if (parts.length < 2) continue;

      const status = parts[0];
      const filePath = parts[1];

      if (processedPaths.has(filePath)) continue;
      if (input.pathPrefix && !filePath.startsWith(input.pathPrefix)) {
        continue;
      }

      processedPaths.add(filePath);

      if (status === "A") {
        changes.push({ path: filePath, status: "added" });
      } else if (status === "D") {
        changes.push({ path: filePath, status: "deleted" });
      } else if (status === "M") {
        changes.push({ path: filePath, status: "modified" });
      } else if (status.startsWith("R")) {
        const oldPath = parts[1];
        const newPath = parts[2];
        changes.push({ path: newPath, status: "renamed", oldPath });
      }
    }

    // Parse untracked files
    for (const line of untrackedResult.split("\n").filter(Boolean)) {
      const filePath = line.trim();
      if (processedPaths.has(filePath)) continue;
      if (input.pathPrefix && !filePath.startsWith(input.pathPrefix)) {
        continue;
      }

      changes.push({ path: filePath, status: "added" });
    }
  } catch (error) {
    // If git commands fail (not a git repo, etc.), return empty result
    return {
      changes: {
        added: [],
        deleted: [],
        modified: [],
        renamed: [],
      },
      stats: {
        totalChanges: 0,
        addedCount: 0,
        deletedCount: 0,
        modifiedCount: 0,
        renamedCount: 0,
      },
    };
  }

  // Organize by change type
  const added: string[] = [];
  const deleted: string[] = [];
  const modified: string[] = [];
  const renamed: Array<{ from: string; to: string }> = [];

  for (const change of changes) {
    switch (change.status) {
      case "added":
        added.push(change.path);
        break;
      case "deleted":
        deleted.push(change.path);
        break;
      case "modified":
        modified.push(change.path);
        break;
      case "renamed":
        renamed.push({ from: change.oldPath!, to: change.path });
        break;
    }
  }

  return {
    changes: {
      added: added.sort(),
      deleted: deleted.sort(),
      modified: modified.sort(),
      renamed: renamed.sort((a, b) => a.to.localeCompare(b.to)),
    },
    stats: {
      totalChanges: changes.length,
      addedCount: added.length,
      deletedCount: deleted.length,
      modifiedCount: modified.length,
      renamedCount: renamed.length,
    },
  };
}
