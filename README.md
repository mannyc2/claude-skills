# Claude Skills

A collection of custom Claude Code skills for personal use.

## Skills

### generating-images-with-gemini
Generate and edit images using Google's Gemini API. Supports text-to-image generation, image editing, style transfer, multi-image composition, and batch generation.

### os-study
Interactive OS concepts quiz and learning tool. Features progress tracking, knowledge assessment, and dynamic cheat-sheet generation based on topics most struggled with.

### smart-cli-wrapper
Universal CLI output optimizer that achieves 80-95% token reduction while preserving actionable information. Meta-optimization for compressing verbose CLI outputs (kubectl, aws, terraform, etc.).

### spritesheets
Generate tilemap spritesheets for 2D scene composition. Creates tileable terrain, placeable objects, and character sprites for game maps, visual novels, and illustrated dialogues.

### tempo-protocol
Browse and reference Tempo.xyz documentation. Built for a GitHub bounty project.

### typst-syntax
Typst syntax reference and patterns. Useful since Claude has limited native knowledge of Typst markup.

## Structure

Each skill follows the standard structure:
```
skill-name/
├── SKILL.md        # Skill definition and instructions
├── references/     # Reference documentation
├── scripts/        # Helper scripts (optional)
└── ...
```
