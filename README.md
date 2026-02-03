# Claude Skills Marketplace

A plugin marketplace for Claude Code with 13 plugins covering development, learning, and productivity.

## Installation

```bash
# Add the marketplace
/plugin marketplace add cjpher/claude-skills

# Install a specific plugin
/plugin install drizzle-orm@cjpher-skills
```

Or install directly from a local clone:

```bash
/plugin marketplace add ./
/plugin install drizzle-orm@cjpher-skills
```

## Plugins

| Plugin | Description |
|--------|-------------|
| **drizzle-orm** | TypeScript ORM for SQL databases with type-safe queries, relations, and migrations |
| **generating-images-with-gemini** | Generate and edit images using Google's Gemini API |
| **neon-cli** | Reference for the Neon CLI to manage serverless Postgres |
| **os-study** | Adaptive OS study companion with spaced repetition and Socratic method |
| **react-hook-form** | Build accessible forms using React Hook Form with shadcn/ui |
| **remotion-video** | Create well-paced, narrative-driven videos using Remotion |
| **smart-cli-wrapper** | Universal CLI output optimizer achieving 80-95% token reduction |
| **spritesheets** | Generate tilemap spritesheets for 2D scene composition |
| **swiftui** | Expert guidance for SwiftUI development on Apple platforms |
| **tempo-protocol** | Tempo blockchain protocol knowledge and documentation access |
| **twitter-research** | Research and analyze Twitter/X content |
| **typst-syntax** | Typst markup language reference with complete syntax documentation |
| **z-image-prompts** | Transform requests into detailed visual prompts for text-to-image models |

## Structure

```
claude-skills/
├── .claude-plugin/
│   └── marketplace.json      # Marketplace catalog
├── plugins/
│   └── <plugin-name>/
│       ├── .claude-plugin/
│       │   └── plugin.json   # Plugin manifest
│       ├── skills/           # Skill definitions
│       ├── agents/           # Agent definitions (optional)
│       └── mcp_server.py     # MCP server (optional)
└── README.md
```

Each plugin follows the standard Claude Code plugin structure with auto-discovery of skills, agents, and commands.
