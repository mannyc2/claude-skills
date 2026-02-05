import { z } from "zod";
import { getProject } from "../project.js";
import path from "path";

export const dependencyGraphSchema = z.object({
  rootDir: z.string().describe("Root directory of the project to analyze"),
  entryFiles: z.array(z.string()).optional().describe("Entry point files to start from (analyzes all if not specified)"),
  depth: z.number().optional().default(Infinity).describe("Maximum depth of dependencies to traverse"),
  includeNodeModules: z.boolean().optional().default(false).describe("Include node_modules dependencies"),
});

export type DependencyGraphInput = z.infer<typeof dependencyGraphSchema>;

interface GraphNode {
  id: string;
  path: string;
  exports: string[];
}

interface GraphEdge {
  from: string;
  to: string;
  imports: string[];
}

interface DependencyGraphResult {
  nodes: GraphNode[];
  edges: GraphEdge[];
  stats: {
    totalFiles: number;
    totalExports: number;
    totalImports: number;
    circularDeps: string[][];
  };
}

export async function getDependencyGraph(input: DependencyGraphInput): Promise<DependencyGraphResult> {
  const project = getProject(input.rootDir);
  const sourceFiles = project.getSourceFiles();

  const nodes: GraphNode[] = [];
  const edges: GraphEdge[] = [];
  const fileToId = new Map<string, string>();

  // Build nodes from source files
  for (const file of sourceFiles) {
    const filePath = file.getFilePath();
    const relativePath = path.relative(input.rootDir, filePath);
    const id = relativePath;

    fileToId.set(filePath, id);

    const exports: string[] = [];
    const exportedDeclarations = file.getExportedDeclarations();
    for (const [name] of exportedDeclarations) {
      exports.push(name);
    }

    nodes.push({
      id,
      path: relativePath,
      exports,
    });
  }

  // Build edges from imports
  const adjacencyList = new Map<string, Set<string>>();

  for (const file of sourceFiles) {
    const filePath = file.getFilePath();
    const fromId = fileToId.get(filePath);
    if (!fromId) continue;

    adjacencyList.set(fromId, new Set());

    const importDeclarations = file.getImportDeclarations();
    for (const imp of importDeclarations) {
      const moduleSpecifier = imp.getModuleSpecifierValue();

      // Skip node_modules unless explicitly included
      if (!input.includeNodeModules && !moduleSpecifier.startsWith(".") && !moduleSpecifier.startsWith("/")) {
        continue;
      }

      const resolvedFile = imp.getModuleSpecifierSourceFile();
      if (!resolvedFile) continue;

      const toPath = resolvedFile.getFilePath();
      const toId = fileToId.get(toPath);
      if (!toId) continue;

      adjacencyList.get(fromId)?.add(toId);

      const imports: string[] = [];
      const namedImports = imp.getNamedImports();
      for (const named of namedImports) {
        imports.push(named.getName());
      }
      const defaultImport = imp.getDefaultImport();
      if (defaultImport) {
        imports.push("default");
      }
      const namespaceImport = imp.getNamespaceImport();
      if (namespaceImport) {
        imports.push("* as " + namespaceImport.getText());
      }

      edges.push({
        from: fromId,
        to: toId,
        imports,
      });
    }
  }

  // Detect circular dependencies using DFS
  const circularDeps: string[][] = [];
  const visited = new Set<string>();
  const recursionStack = new Set<string>();
  const currentPath: string[] = [];

  function detectCycles(nodeId: string): void {
    visited.add(nodeId);
    recursionStack.add(nodeId);
    currentPath.push(nodeId);

    const neighbors = adjacencyList.get(nodeId) || new Set();
    for (const neighbor of neighbors) {
      if (!visited.has(neighbor)) {
        detectCycles(neighbor);
      } else if (recursionStack.has(neighbor)) {
        // Found a cycle
        const cycleStart = currentPath.indexOf(neighbor);
        const cycle = currentPath.slice(cycleStart);
        cycle.push(neighbor); // Complete the cycle
        circularDeps.push(cycle);
      }
    }

    currentPath.pop();
    recursionStack.delete(nodeId);
  }

  for (const nodeId of adjacencyList.keys()) {
    if (!visited.has(nodeId)) {
      detectCycles(nodeId);
    }
  }

  // Calculate stats
  const totalExports = nodes.reduce((sum, node) => sum + node.exports.length, 0);
  const totalImports = edges.reduce((sum, edge) => sum + edge.imports.length, 0);

  return {
    nodes,
    edges,
    stats: {
      totalFiles: nodes.length,
      totalExports,
      totalImports,
      circularDeps,
    },
  };
}
