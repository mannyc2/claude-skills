---
name: tilemap-spritesheet
description: Generate tilemap spritesheets for 2D scene composition. Use when creating visual assets that will be combined via code — game maps, visual novels, illustrated dialogues. Outputs tileable terrain, placeable objects, and character sprites with chroma key backgrounds.
---

# Tilemap Spritesheet Generator

Generate spritesheets for code-based composition.

## Core Concept

**Image model composition** (Gemini, etc): Generates new pixels. Costs ~$0.13 per scene.

**LLM-written code composition** (Claude Code): Writes code that rearranges existing pixels. Code costs ~$0.01 to write, then runs unlimited times for free.

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Image Model    │ ──► │  LLM writes     │ ──► │  Code runs      │
│  (Gemini)       │     │  compositor     │     │                 │
│                 │     │  (Claude Code)  │     │  Scene 1 ($0)   │
│  Spritesheet    │     │                 │     │  Scene 2 ($0)   │
│  $0.13 once     │     │  ~$0.01 once    │     │  Scene N ($0)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

**The rule:** Generate pixels once. Rearrange them forever.

## Tile Types

| Type | Purpose | Requirements |
|------|---------|--------------|
| Terrain | Background tilemap | Seamless edges, tileable |
| Objects | Trees, buildings, props | Transparent, placeable on terrain |
| Characters | People, creatures | Transparent, multiple poses/expressions |
| UI | Dialogue boxes, icons | Transparent, flat |

## Spritesheet Spec

**Resolution:** 2K (2048×2048) at 1:1 aspect ratio
**Tile size:** 256px or 512px per tile
**Background:** Solid #FF00FF magenta (chroma key removal)
**Cost:** ~$0.13 per sheet, ~$0.002 per tile (64 tiles)

## Prompt Template

```
A [GRID]x[GRID] tilemap spritesheet. [TOTAL_SIZE] total, [TILE_SIZE]px per tile.
Strict grid layout, no overlap between tiles.

Row 1 - Terrain tiles (seamless edges, tileable):
[list tiles with connectivity notes]

Row 2 - Object tiles (transparent, placeable):
[list objects]

Row 3 - [Character name] sprites (transparent):
[list poses/expressions]

Row 4 - [Character name] sprites (transparent):
[list poses/expressions]

Style: [style description]

CRITICAL: Solid #FF00FF magenta background on every tile. No gradients.
```

## Terrain Tile Connectivity

For seamless tiling, specify edge connections:

```
Grass tiles:
1. grass-full (all edges grass)
2. grass-path-right (grass with path connecting right edge)
3. grass-path-down (grass with path connecting bottom edge)
4. grass-path-corner (path turns from right to down)
5. grass-water-right (grass with water on right edge)
...
```

## Example: Pastoral Scene (Phaedrus)

```
A 8x8 tilemap spritesheet. 2048x2048 total, 256px per tile.

Row 1 - Terrain base (seamless, tileable):
1. grass plain  2. grass with flowers  3. dirt path horizontal  4. dirt path vertical
5. dirt path corner NE  6. dirt path corner SE  7. water  8. water edge grass

Row 2 - Terrain transitions:
1. grass-to-path left  2. grass-to-path right  3. grass-to-water top  4. grass-to-water bottom
5. riverbank left  6. riverbank right  7. shallow water  8. rocks in water

Row 3 - Objects (transparent, place on terrain):
1. plane tree large  2. olive tree  3. bush small  4. bush large
5. reeds  6. rocks cluster  7. flowers patch  8. fallen branch

Row 4 - Structures (transparent):
1. stone gate left  2. stone gate right  3. stone wall segment  4. wall corner
5. milestone  6. wooden bench  7. altar small  8. column broken

Row 5 - Socrates sprites (elderly, bald, white beard, white robes, transparent):
1. standing front  2. standing side  3. walking  4. sitting
5. lying down  6. gesturing talk  7. thinking  8. pointing

Row 6 - Phaedrus sprites (young, wavy brown hair, blue robes, transparent):
1. standing front  2. standing side  3. walking  4. sitting cross-legged
5. holding scroll  6. reading scroll  7. excited gesture  8. sheepish

Row 7 - Props (transparent, small):
1. scroll rolled  2. scroll open  3. sandals pair  4. water ripple
5. cicada  6. flower single  7. leaf  8. feather

Row 8 - UI elements (flat, transparent):
1. dialogue box  2. name plate  3. arrow right  4. arrow left
5. continue indicator  6. chapter marker  7. quote marks open  8. quote marks close

Style: warm pastoral illustration, golden summer afternoon light, soft painterly, ancient Greek countryside.

CRITICAL: Solid #FF00FF magenta background. No gradients, pure magenta behind every element.
```

## Post-Processing

Remove magenta background:
```bash
convert spritesheet.png -fuzz 10% -transparent "#FF00FF" output.png
```

Slice into individual tiles:
```bash
convert spritesheet.png -crop 256x256 +repage tiles/tile_%02d.png
```

## Composition (Code-based)

The tilemap is composed by code, not by generating new images:

```javascript
// Define map
const map = [
  [0, 0, 2, 0, 0],  // grass, grass, path, grass, grass
  [0, 1, 2, 6, 6],  // grass, flowers, path, water, water
  [0, 0, 2, 4, 6],  // grass, grass, path, bank, water
];

// Place characters
const characters = [
  { sprite: 'socrates_sitting', x: 2, y: 2 },
  { sprite: 'phaedrus_reading', x: 3, y: 2 },
];

// Render layers: terrain → objects → characters → UI
// This code runs unlimited times for $0
```

Claude Code writes this compositor once. It then generates unlimited scenes from the spritesheet.

## Open Problems

1. **Seamless tiling** — Current image models struggle with precise edge matching
2. **Consistent style across tiles** — Some tiles may drift in style
3. **Character scale vs terrain scale** — May need separate sheets at different scales

## Testing Checklist

- [ ] Do terrain tiles actually tile seamlessly?
- [ ] Do object/character tiles have clean magenta removal?
- [ ] Is style consistent across all tiles?
- [ ] Are character proportions correct relative to terrain?