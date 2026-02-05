import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

import { dependencyGraphSchema, getDependencyGraph } from "./tools/dependency-graph.js";
import { unusedExportsSchema, findUnusedExports } from "./tools/unused-exports.js";
import { complexitySchema, getComplexityReport } from "./tools/complexity.js";
import { orphansSchema, checkOrphans } from "./tools/orphans.js";
import { fileDiffSchema, diffFileTree } from "./tools/file-diff.js";
import { duplicatesSchema, findDuplicates } from "./tools/duplicates.js";

const server = new McpServer({
  name: "refactor-tools",
  version: "1.0.0",
});

// Tool 1: Dependency Graph
server.tool(
  "get_dependency_graph",
  "Map imports and exports across the codebase. Returns a graph of file dependencies including nodes (files with their exports), edges (import relationships), and stats (circular dependencies, totals).",
  dependencyGraphSchema.shape,
  async (input) => {
    const result = await getDependencyGraph(dependencyGraphSchema.parse(input));
    return {
      content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
    };
  }
);

// Tool 2: Unused Exports
server.tool(
  "find_unused_exports",
  "Detect dead code by finding exports that are never imported anywhere. Returns a list of unused exports per file with their location and kind.",
  unusedExportsSchema.shape,
  async (input) => {
    const result = await findUnusedExports(unusedExportsSchema.parse(input));
    return {
      content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
    };
  }
);

// Tool 3: Complexity Report
server.tool(
  "get_complexity_report",
  "Analyze code complexity metrics including lines of code, nesting depth, function count, and parameter counts. Returns violations based on configurable thresholds.",
  complexitySchema.shape,
  async (input) => {
    const result = await getComplexityReport(complexitySchema.parse(input));
    return {
      content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
    };
  }
);

// Tool 4: Orphan Checker
server.tool(
  "check_orphans",
  "Find broken imports that reference files that don't exist. Useful after refactoring to ensure all imports still resolve correctly.",
  orphansSchema.shape,
  async (input) => {
    const result = await checkOrphans(orphansSchema.parse(input));
    return {
      content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
    };
  }
);

// Tool 5: File Diff
server.tool(
  "diff_file_tree",
  "Get git-based file tree diff showing added, deleted, modified, and renamed files. Useful for verifying refactoring changes match expectations.",
  fileDiffSchema.shape,
  async (input) => {
    const result = await diffFileTree(fileDiffSchema.parse(input));
    return {
      content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
    };
  }
);

// Tool 6: Find Duplicates
server.tool(
  "find_duplicates",
  "Detect duplicate code blocks across the codebase using normalized line hashing. Returns duplicate patterns with occurrence locations and potential LOC savings if deduplicated.",
  duplicatesSchema.shape,
  async (input) => {
    const result = await findDuplicates(duplicatesSchema.parse(input));
    return {
      content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
    };
  }
);

// Start the server
const transport = new StdioServerTransport();
await server.connect(transport);
