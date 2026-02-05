import { z } from "zod";
import { getProject } from "../project.js";
import path from "path";
import { Node, SyntaxKind, SourceFile } from "ts-morph";

export const complexitySchema = z.object({
  rootDir: z.string().describe("Root directory of the project"),
  files: z.array(z.string()).optional().describe("Specific files to analyze (analyzes all if not specified)"),
  thresholds: z.object({
    maxLoc: z.number().optional().default(300).describe("Maximum lines of code per file"),
    maxNesting: z.number().optional().default(4).describe("Maximum nesting depth"),
    maxFunctions: z.number().optional().default(20).describe("Maximum functions per file"),
    maxParameters: z.number().optional().default(5).describe("Maximum parameters per function"),
  }).optional().default({}),
});

export type ComplexityInput = z.infer<typeof complexitySchema>;

interface FunctionMetrics {
  name: string;
  line: number;
  parameters: number;
  maxNesting: number;
  loc: number;
}

interface FileMetrics {
  loc: number;
  locWithoutComments: number;
  functionCount: number;
  maxNesting: number;
  functions: FunctionMetrics[];
}

interface Violation {
  type: "loc" | "nesting" | "functions" | "parameters";
  message: string;
  line?: number;
  value: number;
  threshold: number;
}

interface FileReport {
  path: string;
  metrics: FileMetrics;
  violations: Violation[];
}

interface ComplexityResult {
  files: FileReport[];
  summary: {
    totalFiles: number;
    totalLoc: number;
    totalFunctions: number;
    filesWithViolations: number;
    violationsByType: Record<string, number>;
  };
}

function calculateNestingDepth(node: Node, currentDepth: number = 0): number {
  let maxDepth = currentDepth;

  const nestingKinds = [
    SyntaxKind.IfStatement,
    SyntaxKind.ForStatement,
    SyntaxKind.ForInStatement,
    SyntaxKind.ForOfStatement,
    SyntaxKind.WhileStatement,
    SyntaxKind.DoStatement,
    SyntaxKind.SwitchStatement,
    SyntaxKind.TryStatement,
    SyntaxKind.CatchClause,
    SyntaxKind.ConditionalExpression,
  ];

  node.forEachChild((child) => {
    const isNestingNode = nestingKinds.includes(child.getKind());
    const childDepth = calculateNestingDepth(child, isNestingNode ? currentDepth + 1 : currentDepth);
    maxDepth = Math.max(maxDepth, childDepth);
  });

  return maxDepth;
}

function analyzeFunctions(sourceFile: SourceFile): FunctionMetrics[] {
  const functions: FunctionMetrics[] = [];

  // Get all function-like declarations
  const functionDeclarations = sourceFile.getFunctions();
  const arrowFunctions = sourceFile.getDescendantsOfKind(SyntaxKind.ArrowFunction);
  const methodDeclarations = sourceFile.getDescendantsOfKind(SyntaxKind.MethodDeclaration);

  for (const func of functionDeclarations) {
    const name = func.getName() || "<anonymous>";
    functions.push({
      name,
      line: func.getStartLineNumber(),
      parameters: func.getParameters().length,
      maxNesting: calculateNestingDepth(func),
      loc: func.getEndLineNumber() - func.getStartLineNumber() + 1,
    });
  }

  for (const arrow of arrowFunctions) {
    // Skip arrow functions that are direct children of variable declarations (those get named)
    const parent = arrow.getParent();
    let name = "<arrow>";
    if (Node.isVariableDeclaration(parent)) {
      name = parent.getName();
    } else if (Node.isPropertyAssignment(parent)) {
      name = parent.getName();
    }

    functions.push({
      name,
      line: arrow.getStartLineNumber(),
      parameters: arrow.getParameters().length,
      maxNesting: calculateNestingDepth(arrow),
      loc: arrow.getEndLineNumber() - arrow.getStartLineNumber() + 1,
    });
  }

  for (const method of methodDeclarations) {
    functions.push({
      name: method.getName(),
      line: method.getStartLineNumber(),
      parameters: method.getParameters().length,
      maxNesting: calculateNestingDepth(method),
      loc: method.getEndLineNumber() - method.getStartLineNumber() + 1,
    });
  }

  return functions;
}

export async function getComplexityReport(input: ComplexityInput): Promise<ComplexityResult> {
  const project = getProject(input.rootDir);
  let sourceFiles = project.getSourceFiles();

  // Filter to specific files if provided
  if (input.files && input.files.length > 0) {
    const targetPaths = new Set(
      input.files.map((f) => (path.isAbsolute(f) ? f : path.join(input.rootDir, f)))
    );
    sourceFiles = sourceFiles.filter((sf) => targetPaths.has(sf.getFilePath()));
  }

  const thresholds = {
    maxLoc: input.thresholds?.maxLoc ?? 300,
    maxNesting: input.thresholds?.maxNesting ?? 4,
    maxFunctions: input.thresholds?.maxFunctions ?? 20,
    maxParameters: input.thresholds?.maxParameters ?? 5,
  };

  const files: FileReport[] = [];
  const violationsByType: Record<string, number> = {
    loc: 0,
    nesting: 0,
    functions: 0,
    parameters: 0,
  };

  let totalLoc = 0;
  let totalFunctions = 0;
  let filesWithViolations = 0;

  for (const sourceFile of sourceFiles) {
    const filePath = sourceFile.getFilePath();
    const relativePath = path.relative(input.rootDir, filePath);
    const fullText = sourceFile.getFullText();
    const lines = fullText.split("\n");

    // Calculate LOC (excluding empty lines and comments - simplified)
    const loc = lines.length;
    const locWithoutComments = lines.filter((line) => {
      const trimmed = line.trim();
      return trimmed.length > 0 && !trimmed.startsWith("//") && !trimmed.startsWith("/*") && !trimmed.startsWith("*");
    }).length;

    const functions = analyzeFunctions(sourceFile);
    const functionCount = functions.length;
    const maxNesting = functions.reduce((max, f) => Math.max(max, f.maxNesting), 0);

    const violations: Violation[] = [];

    // Check file-level violations
    if (loc > thresholds.maxLoc) {
      violations.push({
        type: "loc",
        message: `File has ${loc} lines, exceeds threshold of ${thresholds.maxLoc}`,
        value: loc,
        threshold: thresholds.maxLoc,
      });
      violationsByType.loc++;
    }

    if (functionCount > thresholds.maxFunctions) {
      violations.push({
        type: "functions",
        message: `File has ${functionCount} functions, exceeds threshold of ${thresholds.maxFunctions}`,
        value: functionCount,
        threshold: thresholds.maxFunctions,
      });
      violationsByType.functions++;
    }

    // Check function-level violations
    for (const func of functions) {
      if (func.maxNesting > thresholds.maxNesting) {
        violations.push({
          type: "nesting",
          message: `Function "${func.name}" has nesting depth of ${func.maxNesting}, exceeds threshold of ${thresholds.maxNesting}`,
          line: func.line,
          value: func.maxNesting,
          threshold: thresholds.maxNesting,
        });
        violationsByType.nesting++;
      }

      if (func.parameters > thresholds.maxParameters) {
        violations.push({
          type: "parameters",
          message: `Function "${func.name}" has ${func.parameters} parameters, exceeds threshold of ${thresholds.maxParameters}`,
          line: func.line,
          value: func.parameters,
          threshold: thresholds.maxParameters,
        });
        violationsByType.parameters++;
      }
    }

    if (violations.length > 0) {
      filesWithViolations++;
    }

    totalLoc += loc;
    totalFunctions += functionCount;

    files.push({
      path: relativePath,
      metrics: {
        loc,
        locWithoutComments,
        functionCount,
        maxNesting,
        functions,
      },
      violations,
    });
  }

  return {
    files,
    summary: {
      totalFiles: files.length,
      totalLoc,
      totalFunctions,
      filesWithViolations,
      violationsByType,
    },
  };
}
