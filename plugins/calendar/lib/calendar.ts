import { resolve, dirname } from "path";
import { existsSync } from "fs";

const SWIFT_DIR = resolve(dirname(import.meta.dir), "swift");
const TOOL_PATH = resolve(SWIFT_DIR, "calendar-tool");
const SOURCE_PATH = resolve(SWIFT_DIR, "calendar-tool.swift");

async function ensureBinary() {
  if (existsSync(TOOL_PATH)) return;

  console.error("calendar-tool binary not found, compiling...");
  const build = Bun.spawn(
    [
      "swiftc",
      "-parse-as-library",
      "-O",
      "-o",
      TOOL_PATH,
      SOURCE_PATH,
      "-framework",
      "EventKit",
      "-framework",
      "CoreLocation",
    ],
    { stdout: "pipe", stderr: "pipe" }
  );

  const [, stderr, exitCode] = await Promise.all([
    new Response(build.stdout).text(),
    new Response(build.stderr).text(),
    build.exited,
  ]);

  if (exitCode !== 0) {
    throw new Error(`Failed to compile calendar-tool:\n${stderr}`);
  }
  console.error("calendar-tool compiled successfully");
}

export async function run(args: string[]): Promise<any> {
  await ensureBinary();

  const proc = Bun.spawn([TOOL_PATH, ...args], {
    stdout: "pipe",
    stderr: "pipe",
  });

  const [stdout, stderr, exitCode] = await Promise.all([
    new Response(proc.stdout).text(),
    new Response(proc.stderr).text(),
    proc.exited,
  ]);

  if (exitCode !== 0) {
    // Try to parse JSON error from the tool
    try {
      const parsed = JSON.parse(stdout);
      if (parsed.error) throw new Error(parsed.message);
    } catch {
      // Fall through
    }
    throw new Error(stderr || `calendar-tool exited with code ${exitCode}`);
  }

  return JSON.parse(stdout);
}
