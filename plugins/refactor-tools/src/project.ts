import { Project } from "ts-morph";

const projectCache = new Map<string, Project>();

export function getProject(rootDir: string): Project {
  const cached = projectCache.get(rootDir);
  if (cached) {
    return cached;
  }

  const project = new Project({
    tsConfigFilePath: `${rootDir}/tsconfig.json`,
    skipAddingFilesFromTsConfig: true,
  });

  // Add source files, excluding node_modules
  project.addSourceFilesAtPaths([
    `${rootDir}/**/*.ts`,
    `${rootDir}/**/*.tsx`,
    `${rootDir}/**/*.js`,
    `${rootDir}/**/*.jsx`,
    `!${rootDir}/**/node_modules/**`,
    `!${rootDir}/**/dist/**`,
    `!${rootDir}/**/build/**`,
  ]);

  projectCache.set(rootDir, project);
  return project;
}

export function clearProjectCache(rootDir?: string): void {
  if (rootDir) {
    projectCache.delete(rootDir);
  } else {
    projectCache.clear();
  }
}
