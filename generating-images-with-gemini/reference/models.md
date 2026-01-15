# Model Capabilities & Selection

This guide helps you choose between Gemini 2.5 Flash Image and Gemini 3 Pro Image Preview.

## Table of Contents

- Available Models (Gemini 2.5 Flash, Gemini 3 Pro)
- Model Selection Decision Tree
- When to Use Which Model
- Comparison with Imagen Models
- Resolution Support
- Reference Image Limits
- Google Search Grounding
- Thinking Mode
- Language Support
- Pricing Summary
- Quick Reference Table

---

## Available Models

### Gemini 2.5 Flash Image (Nano Banana)

**Model ID**: `gemini-2.5-flash-image`

**Best for**:
- Speed and efficiency
- High-volume, low-latency tasks
- Budget-constrained projects
- Simple to moderate complexity images

**Capabilities**:
- **Resolution**: Fixed 1024px (various aspect ratios)
- **Reference images**: Works best with up to 3 images
- **Thinking**: Optional (disabled by default, can enable with `thinking_budget`)
- **Cost**: ~$0.039 per image (1290 tokens)
- **Speed**: Fast generation

**Limitations**:
- No 2K/4K support
- No Google Search grounding
- Best with ≤3 reference images
- Fixed resolution only

### Gemini 3 Pro Image Preview (Nano Banana Pro)

**Model ID**: `gemini-3-pro-image-preview`

**Best for**:
- Professional asset production
- Complex multi-turn editing workflows
- High-resolution output requirements
- Advanced text rendering (infographics, menus, diagrams)

**Capabilities**:
- **Resolution**: 1K, 2K, 4K (configurable)
- **Reference images**: Up to 14 images
  - Up to 6 object images (high-fidelity)
  - Up to 5 human images (character consistency)
- **Thinking**: Always enabled (cannot disable)
- **Cost**: ~$0.134 per image (1K/2K), ~$0.24 per image (4K)
- **Advanced features**:
  - Advanced text rendering
  - Google Search grounding
  - Generates interim "thought images" (not charged)

**Important Notes**:
- ⚠️ Temperature MUST stay at 1.0 (lowering causes loops/degraded performance)
- ✅ Thought signatures automatically preserved in SDK chat mode
- ✅ Can use real-time data via Google Search

## Model Selection Decision Tree

```
START: Need to generate/edit images
│
├─ Q: Budget very constrained? Speed critical?
│  └─ YES → Gemini 2.5 Flash Image
│  └─ NO → Continue
│
├─ Q: Need resolution >1K (2K or 4K)?
│  └─ YES → Gemini 3 Pro Image Preview
│  └─ NO → Continue
│
├─ Q: Need Google Search grounding?
│  └─ YES → Gemini 3 Pro Image Preview
│  └─ NO → Continue
│
├─ Q: Using >3 reference images?
│  └─ YES → Gemini 3 Pro Image Preview (up to 14)
│  └─ NO → Continue
│
├─ Q: Complex multi-turn editing workflow?
│  └─ YES → Gemini 3 Pro Image Preview
│  └─ NO → Continue
│
├─ Q: Professional asset production (infographics, menus, marketing)?
│  └─ YES → Gemini 3 Pro Image Preview
│  └─ NO → Continue
│
└─ DEFAULT → Gemini 2.5 Flash Image (good balance)
```

## When to Use Which Model

### Use Gemini 2.5 Flash Image when:

✅ Speed is priority
✅ High volume generation needed
✅ Budget constrained
✅ Simple to moderate complexity
✅ Up to 3 reference images
✅ 1024px resolution is sufficient

**Example use cases**:
- Social media content
- Quick concept sketches
- Basic product mockups
- Simple illustrations
- Style variations of a reference image

### Use Gemini 3 Pro Image Preview when:

✅ Professional quality needed
✅ Complex multi-turn editing
✅ High-resolution output (2K/4K)
✅ Advanced text rendering required
✅ Grounding with Google Search needed
✅ Many reference images (up to 14)
✅ Complex reasoning required

**Example use cases**:
- Professional infographics with text
- High-res marketing materials
- Complex multi-image compositions
- Character consistency across multiple images
- Real-time data visualization (weather, sports, etc.)
- Professional logo/branding work

## Comparison with Imagen Models

| Attribute | Imagen 4 | Gemini Native Image |
|-----------|--------|---------------------|
| **Strengths** | Specialized image generation | **Default recommendation.** Unparalleled flexibility, contextual understanding, mask-free editing. Multi-turn conversational editing. |
| **Availability** | Generally available | Preview (Production usage allowed) |
| **Latency** | **Low**. Near-real-time | Higher. More computation for advanced capabilities |
| **Cost** | $0.02-$0.12/image | Token-based: $30/1M tokens for image output (~$0.039/image up to 1024x1024) |
| **Recommended tasks** | Image quality, photorealism, specific styles, branding, logos, advanced spelling/typography | Interleaved text and image generation, multi-image composition, specific edits, iterative work, style transfer |

### When to use Imagen:

✅ Image quality, photorealism, artistic detail are top priority
✅ Specific styles needed (impressionism, anime, etc.)
✅ Branding, style infusion, logos, product designs
✅ Advanced spelling or typography

### When to use Gemini:

✅ Interleaved text and image generation
✅ Combining elements from multiple images
✅ Highly specific edits with simple language
✅ Iterative work on an image
✅ Applying design/texture while preserving form

## Resolution Support

### Gemini 2.5 Flash Image

- **Fixed**: 1024x1024 equivalent at various aspect ratios
- **Tokens**: All consume 1290 tokens regardless of aspect ratio
- **Quality**: Optimized for speed and efficiency

### Gemini 3 Pro Image Preview

- **1K** (default): Lower token cost (1120 tokens)
- **2K**: Medium quality/cost (1120 tokens)
- **4K**: Highest quality, higher tokens (2000 tokens)

⚠️ **CRITICAL**: Must use uppercase 'K' (e.g., `"2K"` not `"2k"`)

**Resolution table** (Gemini 3 Pro):

| Aspect Ratio | 1K Resolution | 2K Resolution | 4K Resolution |
|--------------|---------------|---------------|---------------|
| 1:1          | 1024x1024     | 2048x2048     | 4096x4096     |
| 16:9         | 1376x768      | 2752x1536     | 5504x3072     |
| 9:16         | 768x1376      | 1536x2752     | 3072x5504     |
| 4:3          | 1200x896      | 2400x1792     | 4800x3584     |
| 3:4          | 896x1200      | 1792x2400     | 3584x4800     |

*See [reference-tables.md](reference-tables.md) for complete resolution/token tables.*

## Reference Image Limits

### Gemini 2.5 Flash Image

- **Best with**: Up to 3 reference images
- **Quality impact**: More images may reduce quality

### Gemini 3 Pro Image Preview

- **Up to 14 total reference images**:
  - Up to **6 object images** (high-fidelity composition)
  - Up to **5 human images** (character consistency)
- Exceeding limits may fail or reduce quality

## Google Search Grounding

**Only Gemini 3 Pro Image Preview** supports this feature.

```python
from google.genai import types

config = types.GenerateContentConfig(
    response_modalities=['Text', 'Image'],
    tools=[{"google_search": {}}]
)
```

**Returns in response**:
- `searchEntryPoint`: HTML/CSS for required search suggestions
- `groundingChunks`: Top 3 web sources used
- **Note**: Image search results excluded from grounding

**Example use cases**:
- "Visualize the current weather forecast for Tokyo"
- "Create a chart showing yesterday's stock market performance"
- "Design an infographic about last night's sports game"

## Thinking Mode

### Gemini 2.5 Flash Image

- **Default**: Does NOT think
- **Can enable**: `thinking_config=types.ThinkingConfig(thinking_budget=1024)`
- **Can disable** (default): `thinking_budget=0`

### Gemini 3 Pro Image Preview

- **Default**: ALWAYS thinks (cannot disable)
- **Thinking process**:
  - Generates up to 2 interim images to test composition
  - Last image in thinking is also the final rendered image
  - Interim thought images NOT charged for tokens

**Include thought summaries**:
```python
thinking_config=types.ThinkingConfig(include_thoughts=True)
```

## Language Support

**Best-performing languages** (complete list):

- EN (English)
- ar-EG (Arabic - Egypt)
- de-DE (German)
- es-MX (Spanish - Mexico)
- fr-FR (French)
- hi-IN (Hindi)
- id-ID (Indonesian)
- it-IT (Italian)
- ja-JP (Japanese)
- ko-KR (Korean)
- pt-BR (Portuguese - Brazil)
- ru-RU (Russian)
- ua-UA (Ukrainian)
- vi-VN (Vietnamese)
- zh-CN (Chinese)

Other languages may work but with reduced quality.

## Pricing Summary

### Gemini 2.5 Flash Image

**Standard**:
- Input: $0.30/1M tokens
- Output: ~$0.039 per image (1290 tokens)

**Batch** (50% discount):
- Input: $0.15/1M tokens
- Output: ~$0.0195 per image

### Gemini 3 Pro Image Preview

**Standard**:
- Input: $2.00/1M tokens
- Output: ~$0.134 per 1K/2K image, ~$0.24 per 4K image

**Batch** (50% discount):
- Input: $1.00/1M tokens
- Output: ~$0.067 per 1K/2K image, ~$0.12 per 4K image

## Quick Reference

| Feature | Gemini 2.5 Flash | Gemini 3 Pro |
|---------|------------------|--------------|
| **Resolution** | Fixed 1024px | 1K, 2K, 4K |
| **Cost per image** | ~$0.039 | ~$0.134-$0.24 |
| **Reference images** | Up to 3 | Up to 14 |
| **Google Search** | ❌ No | ✅ Yes |
| **Thinking** | Optional (off by default) | Always on |
| **Speed** | Fast | Slower (more computation) |
| **Best for** | Volume, speed, cost | Quality, complexity |

## Getting Started

See [examples.md](examples.md) for code examples using each model.
