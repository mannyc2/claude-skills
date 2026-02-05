import { z } from "zod";
import { getProject } from "../project.js";
import path from "path";
import { Node } from "ts-morph";

export const unusedExportsSchema = z.object({
  rootDir: z.string().describe("Root directory of the project to analyze"),
  entryPoints: z.array(z.string()).optional().describe("Entry point files (exports from these are considered used)"),
  ignorePatterns: z.array(z.string()).optional().default([]).describe("Glob patterns to ignore"),
});

export type UnusedExportsInput = z.infer<typeof unusedExportsSchema>;

interface UnusedExport {
  name: string;
  line: number;
  col: number;
  kind: string;
}

interface FileUnusedExports {
  file: string;
  exports: UnusedExport[];
}

interface UnusedExportsResult {
  unusedExports: FileUnusedExports[];
  stats: {
    totalExports: number;
    unusedCount: number;
    usedCount: number;
    unusedPercentage: number;
  };
}

export async function findUnusedExports(input: UnusedExportsInput): Promise<UnusedExportsResult> {
  const project = getProject(input.rootDir);
  const sourceFiles = project.getSourceFiles();

  // Normalize entry points to absolute paths
  const entryPointSet = new Set<string>();
  if (input.entryPoints) {
    for (const entry of input.entryPoints) {
      const absolute = path.isAbsolute(entry) ? entry : path.join(input.rootDir, entry);
      entryPointSet.add(absolute);
    }
  }

  const unusedExports: FileUnusedExports[] = [];
  let totalExports = 0;
  let unusedCount = 0;

  for (const file of sourceFiles) {
    const filePath = file.getFilePath();
    const relativePath = path.relative(input.rootDir, filePath);

    // Skip files matching ignore patterns
    if (input.ignorePatterns?.some(pattern => relativePath.includes(pattern))) {
      continue;
    }

    // Entry points - their exports are considered "used"
    const isEntryPoint = entryPointSet.has(filePath);

    const exportedDeclarations = file.getExportedDeclarations();
    const fileUnused: UnusedExport[] = [];

    for (const [name, declarations] of exportedDeclarations) {
      totalExports++;

      // Entry point exports are always considered used
      if (isEntryPoint) {
        continue;
      }

      // Check if this export is used anywhere
      const decl = declarations[0];
      if (!decl) continue;

      // Find references to this declaration
      let isUsed = false;

      try {
        // For named exports, find references
        if (Node.isReferenceFindable(decl)) {
          const references = decl.findReferences();
          for (const ref of references) {
            const refDefs = ref.getReferences();
            for (const refDef of refDefs) {
              const refFile = refDef.getSourceFile().getFilePath();
              // If referenced in a different file, it's used
              if (refFile !== filePath) {
                isUsed = true;
                break;
              }
              // Check if the reference is not just the definition itself
              const refNode = refDef.getNode();
              const declStartLine = decl.getStartLineNumber();
              const refStartLine = refNode.getStartLineNumber();
              if (refStartLine !== declStartLine) {
                isUsed = true;
                break;
              }
            }
            if (isUsed) break;
          }
        }
      } catch {
        // If we can't find references, assume it might be used
        isUsed = true;
      }

      if (!isUsed) {
        unusedCount++;
        const startPos = decl.getStart();
        const { line, column } = file.getLineAndColumnAtPos(startPos);

        fileUnused.push({
          name,
          line,
          col: column,
          kind: decl.getKindName(),
        });
      }
    }

    if (fileUnused.length > 0) {
      unusedExports.push({
        file: relativePath,
        exports: fileUnused,
      });
    }
  }

  const usedCount = totalExports - unusedCount;
  const unusedPercentage = totalExports > 0 ? Math.round((unusedCount / totalExports) * 100) : 0;

  return {
    unusedExports,
    stats: {
      totalExports,
      unusedCount,
      usedCount,
      unusedPercentage,
    },
  };
}
