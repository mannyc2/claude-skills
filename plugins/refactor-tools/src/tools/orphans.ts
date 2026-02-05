import { z } from "zod";
import { getProject } from "../project.js";
import path from "path";
import { SyntaxKind, CallExpression } from "ts-morph";

export const orphansSchema = z.object({
  rootDir: z.string().describe("Root directory of the project to analyze"),
  files: z.array(z.string()).optional().describe("Specific files to check (checks all if not specified)"),
});

export type OrphansInput = z.infer<typeof orphansSchema>;

interface OrphanedImport {
  file: string;
  line: number;
  importPath: string;
  reason: "not_found" | "ambiguous" | "type_only_runtime";
}

interface OrphansResult {
  orphanedImports: OrphanedImport[];
  stats: {
    totalImports: number;
    orphanedCount: number;
    validCount: number;
    filesChecked: number;
  };
}

export async function checkOrphans(input: OrphansInput): Promise<OrphansResult> {
  const project = getProject(input.rootDir);
  let sourceFiles = project.getSourceFiles();

  // Filter to specific files if provided
  if (input.files && input.files.length > 0) {
    const targetPaths = new Set(
      input.files.map((f) => (path.isAbsolute(f) ? f : path.join(input.rootDir, f)))
    );
    sourceFiles = sourceFiles.filter((sf) => targetPaths.has(sf.getFilePath()));
  }

  const orphanedImports: OrphanedImport[] = [];
  let totalImports = 0;

  for (const sourceFile of sourceFiles) {
    const filePath = sourceFile.getFilePath();
    const relativePath = path.relative(input.rootDir, filePath);

    const importDeclarations = sourceFile.getImportDeclarations();

    for (const imp of importDeclarations) {
      totalImports++;

      const moduleSpecifier = imp.getModuleSpecifierValue();

      // Skip node_modules imports - they're handled by the package manager
      if (!moduleSpecifier.startsWith(".") && !moduleSpecifier.startsWith("/")) {
        continue;
      }

      // Try to resolve the import
      const resolvedFile = imp.getModuleSpecifierSourceFile();

      if (!resolvedFile) {
        // Check if there's a declaration file (.d.ts) that might satisfy this
        const line = imp.getStartLineNumber();

        orphanedImports.push({
          file: relativePath,
          line,
          importPath: moduleSpecifier,
          reason: "not_found",
        });
      }
    }

    // Also check for dynamic imports
    const callExpressions = sourceFile.getDescendantsOfKind(SyntaxKind.CallExpression) as CallExpression[];
    for (const call of callExpressions) {
      const expression = call.getExpression();
      if (expression.getText() === "import") {
        totalImports++;
        const args = call.getArguments();
        if (args.length > 0) {
          const arg = args[0];
          const text = arg.getText();
          // Extract string literal value
          const match = text.match(/^['"`](.+)['"`]$/);
          if (match) {
            const importPath = match[1];
            // Skip non-relative imports
            if (importPath.startsWith(".") || importPath.startsWith("/")) {
              // For dynamic imports, we can't easily resolve them via ts-morph
              // Just check if the file exists
              try {
                const resolvedPath = path.resolve(path.dirname(filePath), importPath);
                const extensions = [".ts", ".tsx", ".js", ".jsx", ".json", ""];
                let found = false;
                for (const ext of extensions) {
                  const fullPath = resolvedPath + ext;
                  const matchingFile = project.getSourceFile(fullPath);
                  if (matchingFile) {
                    found = true;
                    break;
                  }
                  // Also check for index files
                  const indexPath = path.join(resolvedPath, `index${ext}`);
                  const indexFile = project.getSourceFile(indexPath);
                  if (indexFile) {
                    found = true;
                    break;
                  }
                }
                if (!found) {
                  orphanedImports.push({
                    file: relativePath,
                    line: call.getStartLineNumber(),
                    importPath,
                    reason: "not_found",
                  });
                }
              } catch {
                // If we can't resolve, mark as potentially orphaned
                orphanedImports.push({
                  file: relativePath,
                  line: call.getStartLineNumber(),
                  importPath,
                  reason: "ambiguous",
                });
              }
            }
          }
        }
      }
    }
  }

  const orphanedCount = orphanedImports.length;
  const validCount = totalImports - orphanedCount;

  return {
    orphanedImports,
    stats: {
      totalImports,
      orphanedCount,
      validCount,
      filesChecked: sourceFiles.length,
    },
  };
}
