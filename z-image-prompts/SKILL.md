---
name: z-image-prompts
description: Transform user requests into detailed visual prompts for Z-Image, Flux, Nano-Banana, and similar text-to-image models. Use when users ask to generate image prompts, create visual descriptions, or need help describing scenes for AI image generation. Triggers on requests like "create a prompt for", "describe this scene", "z-image prompt", "image prompt", or "visual description for".
---

# Z-Image Prompt Generator

Transform user requests into concrete, detailed visual descriptions optimized for text-to-image models.

## Workflow

### 0. Assess Completeness

Before generating, evaluate the request against these categories:

| Category | Priority | If Missing |
|----------|----------|------------|
| 📸 Medium (photo, painting, 3D) | Required | Ask if ambiguous between very different styles |
| 👤 Subject (who/what) | Required | Must ask — cannot proceed without |
| 🏃 Action/Pose | High | Ask if scene depends on it |
| 🌍🛌 Setting (indoor/outdoor) | Medium | Default based on context, or ask if mood-critical |
| 👕 Clothing | Medium | Default to contextually appropriate |
| 🎥 Camera (shot/angle) | Low | Default to medium shot, eye level |
| 💡 Lighting | Low | Default to soft natural light |
| 🎞️ Color Grading | Low | Default to neutral |

**Decision logic:**
- **Required missing** → Ask before proceeding
- **High priority ambiguous** → Ask if multiple valid interpretations would produce very different images
- **Medium/Low missing** → Make sensible defaults, proceed

**When asking**, batch related questions. Don't ask 10 separate questions:
```
Good: "A few quick details: Is this a photograph or illustration? And is she indoors or outdoors?"
Bad: "What medium?" [wait] "What setting?" [wait] "What lighting?" [wait]
```

**Don't ask when:**
- User says "surprise me" or "your choice"
- Request is already detailed
- Context strongly implies the answer
- It's a low-priority category with obvious defaults

### 1. Lock Core Elements

Extract and preserve unchanged:
- Subject (who/what)
- Quantity (how many)
- Action/State (doing what)
- Specified names, colors, text content

### 2. Generative Reasoning (if needed)

When the request isn't a direct scene (e.g., "design a logo", "show how X works", "what is Y"):
1. Conceptualize a specific, visualizable solution
2. This solution becomes the foundation for description

### 3. Inject Aesthetic Details

Add professional-grade specifics:
- **Composition**: Shot type, camera angle
- **Lighting**: Source, quality, direction
- **Atmosphere**: Time of day, weather, mood through environment
- **Materials**: Surface textures, fabric properties
- **Color palette**: Dominant tones, grading style
- **Spatial depth**: Foreground/midground/background layers

See `references/presets.md` for tested phrase options.

### 4. Handle Text Elements

For any text appearing in the image:
- Wrap exact text content in English double quotes: `"Hello World"`
- Describe position, size, font style, material (signage, screen, print)
- For design pieces (posters, menus, UI): describe ALL textual content with typography

## Output Rules

**DO:**
- Use objective, concrete language
- Describe observable visual properties
- Be specific about quantities, positions, materials

**DON'T:**
- Use metaphors or figurative language
- Include meta-tags (8K, masterpiece, best quality)
- Add drawing instructions or model parameters
- Include anything except the final prompt

## Examples: Ask vs. Proceed

**Proceed immediately:**
> "A samurai in golden armor standing in a bamboo forest at sunset"
> 
> Has: subject ✓, clothing ✓, setting ✓, lighting implied ✓

**Ask first:**
> "A woman looking mysterious"
> 
> Missing: medium (photo? painting?), setting, clothing — too many valid interpretations
> Ask: "Quick clarification: should this be a photograph or illustration? And any preference on setting—indoor, outdoor, abstract background?"

**Proceed with defaults:**
> "A cyberpunk hacker"
> 
> Missing: pose, exact setting, camera
> But: "cyberpunk" implies neon lighting, tech environment. Default the rest, proceed.

**Ask selectively:**
> "Portrait of my grandmother"
> 
> Has: subject type, implies medium (photo) and shot (portrait)
> Missing: her actual appearance
> Ask: "Could you describe her—age, hair, any distinctive features? Or should I create a generic elderly woman portrait?"

## Quick Reference

**Shot types**: extreme wide, wide, medium, close, detail
**Angles**: eye level, low angle, high angle, overhead, dutch
**Lighting**: golden hour, blue hour, neon, candlelight, rim light
**Color**: warm, cool, desaturated, vibrant, teal-orange

For full options: `references/presets.md`
For examples: `assets/examples.md`
