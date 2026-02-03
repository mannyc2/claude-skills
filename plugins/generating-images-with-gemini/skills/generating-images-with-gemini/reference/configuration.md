# Configuration Options Reference

Complete reference for configuring Gemini image generation requests.

## Table of Contents

- Configuration Structure
- Response Modalities
- Image Configuration (Aspect Ratios, Image Sizes)
- System Instructions
- Thinking Configuration
- Generation Parameters (Temperature, Top-K, Top-P)
- Tools Configuration (Google Search, Code Execution)
- Configuration Cheat Sheet
- Default Values Reference

---

## Configuration Structure

```python
from google.genai import types

config = types.GenerateContentConfig(
    response_modalities=['TEXT', 'IMAGE'],  # Or just ['IMAGE']
    image_config=types.ImageConfig(
        aspect_ratio="16:9",
        image_size="2K"  # Gemini 3 Pro only
    ),
    system_instruction="You are a professional designer...",
    thinking_config=types.ThinkingConfig(
        include_thoughts=True,
        thinking_budget=1024  # For 2.5 models
    ),
    temperature=1.0,
    top_k=40,
    top_p=0.95,
    max_output_tokens=8192,
    tools=[{"google_search": {}}]  # Gemini 3 Pro only
)
```

---

## Response Modalities

Controls what the model returns (text, images, or both).

### Options

```python
response_modalities=['TEXT', 'IMAGE']  # Default: text + image (both)
response_modalities=['IMAGE']          # Image only, no text
```

**Use cases**:
- `['TEXT', 'IMAGE']`: When you want explanations along with images
- `['IMAGE']`: When you only need the visual output (faster, no unnecessary text)

⚠️ **Note**: Cannot request text-only for image generation models.

### Example

```python
# Image-only response (no text)
config = types.GenerateContentConfig(
    response_modalities=['IMAGE']
)

response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents="A mountain landscape",
    config=config
)
```

---

## Image Configuration

### Aspect Ratios

**Supported aspect ratios** (both models):

| Ratio | Description | Use Case |
|-------|-------------|----------|
| `1:1` | Square | Tile-based imagery (patterns, textures, spritesheets), social media, avatars, logos |
| `16:9` | Wide landscape | Presentations, YouTube, desktop wallpapers |
| `9:16` | Tall portrait | Mobile screens, stories |
| `4:3` | Standard landscape | Traditional photos, slideshows |
| `3:4` | Standard portrait | Portraits, book covers |
| `4:5` | Instagram portrait | Instagram posts |
| `5:4` | Slightly wide | Prints, frames |
| `2:3` | Classic portrait | Standard photo prints |
| `3:2` | Classic landscape | DSLR photos, prints |
| `21:9` | Ultra-wide | Cinematic, panoramas |

### Image Sizes

**Gemini 2.5 Flash Image**:
- Fixed ~1024px (not configurable)
- All aspect ratios consume 1290 tokens

**Gemini 3 Pro Image Preview**:

| Size | Resolution Range | Tokens | Use Case |
|------|------------------|--------|----------|
| `"1K"` | ~1024-1584px | 1120 | Default, good balance |
| `"2K"` | ~1696-3168px | 1120 | High quality, same cost as 1K |
| `"4K"` | ~3072-6336px | 2000 | Maximum quality, premium |

⚠️ **CRITICAL**: Must use uppercase 'K' (`"2K"` not `"2k"`)

**Example resolutions** (Gemini 3 Pro):

| Aspect Ratio | 1K | 2K | 4K |
|--------------|----|----|---- |
| 1:1 | 1024x1024 | 2048x2048 | 4096x4096 |
| 16:9 | 1376x768 | 2752x1536 | 5504x3072 |
| 9:16 | 768x1376 | 1536x2752 | 3072x5504 |

*See [reference-tables.md](reference-tables.md) for complete table.*

### Image Config Example

```python
config = types.GenerateContentConfig(
    image_config=types.ImageConfig(
        aspect_ratio="16:9",
        image_size="2K"  # Gemini 3 Pro only
    )
)

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents="Create a wide landscape image",
    config=config
)
```

### Tile-Based Image Configuration

**Recommended configuration for tile-based imagery** (patterns, textures, spritesheets):

```python
config = types.GenerateContentConfig(
    image_config=types.ImageConfig(
        aspect_ratio="1:1",  # Square format repeats seamlessly in grids
        image_size="2K"      # Balances detail quality vs file size
    )
)
```

**Why this configuration works well for tiles:**

- **1:1 aspect ratio**: Square format repeats seamlessly when arranged in grids
  - Natural for patterns that tile horizontally and vertically
  - No edge cases with different dimensions

- **2K resolution** (2048x2048): Optimal balance for tiled content
  - **Not 1K** (1024x1024): Too low resolution, tiles look pixelated when repeated
  - **Not 4K** (4096x4096): Overkill for tiles, creates unnecessarily large files
  - **2K sweet spot**: Enough detail for crisp repetition without bloating file sizes

**Example usage:**

```python
# Generate a seamless texture tile
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents="Create a seamless stone texture pattern that tiles horizontally and vertically",
    config=types.GenerateContentConfig(
        image_config=types.ImageConfig(
            aspect_ratio="1:1",
            image_size="2K"
        )
    )
)
```

**Use cases:**
- Pattern backgrounds (geometric, organic, abstract)
- Texture maps (stone, wood, fabric, metal)
- Game sprite sheets and tile sets
- Repeating wallpaper designs
- Seamless icons and UI elements

---

## System Instructions

Guide the model's behavior and persona.

### Basic Usage

```python
config = types.GenerateContentConfig(
    system_instruction="You are an expert minimalist designer. Always use clean lines, limited color palettes, and effective negative space."
)
```

### Use Cases

**For consistent style**:
```python
system_instruction="You are a professional product photographer. Create studio-quality photos with soft lighting and clean backgrounds."
```

**For specific domain**:
```python
system_instruction="You are a scientific illustrator specializing in educational diagrams for biology textbooks."
```

**For brand guidelines**:
```python
system_instruction="You are a brand designer for EcoTech. Always use earth tones (greens, browns), minimalist style, and incorporate subtle nature motifs."
```

---

## Thinking Configuration

Control how the model reasons about the task.

### Gemini 2.5 Flash Image

**Default**: Does NOT think

```python
# Enable thinking (for complex tasks)
thinking_config=types.ThinkingConfig(thinking_budget=1024)

# Disable thinking (default, faster)
thinking_config=types.ThinkingConfig(thinking_budget=0)
```

**Thinking budget**: Number of tokens allocated for reasoning (0-2048)

### Gemini 3 Pro Image Preview

**Default**: ALWAYS thinks (cannot disable)

```python
# Include thought summaries in response
thinking_config=types.ThinkingConfig(include_thoughts=True)
```

**How thinking works** (Gemini 3 Pro):
- Generates up to 2 interim images to test composition
- Last thought image is also the final rendered image
- Interim thought images NOT charged

### Example

```python
# Gemini 3 Pro with thoughts visible
config = types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(include_thoughts=True)
)

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents="Create a complex technical diagram",
    config=config
)

# Inspect thoughts
for part in response.parts:
    if part.thought:
        print("💭 Thought:", part.text)
    elif part.inline_data:
        print("✅ Final image")
```

---

## Generation Parameters

### Temperature

Controls randomness in generation.

⚠️ **CRITICAL for Gemini 3**: Must stay at 1.0

```python
# Gemini 3 models - DON'T CHANGE
temperature=1.0  # Default, keep this

# Gemini 2.5 models - safe to adjust
temperature=0.7  # More deterministic
temperature=1.0  # More creative (default)
```

**Why this matters**:
- Gemini 3 with temperature <1.0 → loops, degraded performance
- Gemini 2.5 safe to adjust for different creativity levels

### Top-K and Top-P

Sampling parameters for text generation (less critical for image generation).

```python
top_k=40      # Default: 40 (consider top 40 tokens)
top_p=0.95    # Default: 0.95 (nucleus sampling threshold)
```

Generally use defaults unless you have specific needs.

### Max Output Tokens

Limit response length.

```python
max_output_tokens=8192  # Default
max_output_tokens=100   # For concise responses
```

**Use case**: Reduce hallucinations by limiting text output length.

---

## Tools Configuration

### Google Search Grounding

**Only Gemini 3 Pro Image Preview** supports this.

```python
tools=[{"google_search": {}}]
```

**Returns**:
- `searchEntryPoint`: HTML/CSS for search suggestions
- `groundingChunks`: Top 3 web sources used

**Example**:

```python
config = types.GenerateContentConfig(
    response_modalities=['TEXT', 'IMAGE'],
    tools=[{"google_search": {}}]
)

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents="Visualize yesterday's stock market performance",
    config=config
)

# Access grounding metadata
metadata = response.candidates[0].grounding_metadata
for chunk in metadata.grounding_chunks:
    print(f"Source: {chunk.web.title} - {chunk.web.uri}")
```

### Code Execution

If supported by model:

```python
tools=[types.Tool(code_execution=types.ToolCodeExecution)]
```

---

## Configuration Cheat Sheet

### Quick Generation (Speed Priority)

```python
config = types.GenerateContentConfig(
    response_modalities=['IMAGE'],  # No text overhead
    thinking_config=types.ThinkingConfig(thinking_budget=0)  # Flash only
)
```

### Professional Quality

```python
config = types.GenerateContentConfig(
    image_config=types.ImageConfig(
        aspect_ratio="16:9",
        image_size="2K"  # Or "4K" for max quality
    ),
    thinking_config=types.ThinkingConfig(include_thoughts=True)
)
```

### Multi-Turn Editing

```python
config = types.GenerateContentConfig(
    response_modalities=['TEXT', 'IMAGE'],
    system_instruction="You are a professional photo editor. Make subtle, realistic edits."
)
```

### Real-Time Data

```python
config = types.GenerateContentConfig(
    response_modalities=['TEXT', 'IMAGE'],
    tools=[{"google_search": {}}],  # Gemini 3 Pro only
    image_config=types.ImageConfig(aspect_ratio="16:9")
)
```

### Reduce Hallucinations

```python
config = types.GenerateContentConfig(
    temperature=0.7,  # For 2.5 models only
    max_output_tokens=100  # Shorter responses
)
```

---

## Default Values Reference

| Parameter | Gemini 2.5 Flash | Gemini 3 Pro |
|-----------|------------------|--------------|
| `response_modalities` | `['TEXT', 'IMAGE']` | `['TEXT', 'IMAGE']` |
| `aspect_ratio` | `"1:1"` | `"1:1"` |
| `image_size` | N/A (fixed ~1024px) | `"1K"` |
| `thinking_budget` | `0` (disabled) | N/A (always on) |
| `temperature` | `0.9` | `1.0` ⚠️ DON'T CHANGE |
| `top_k` | `40` | `40` |
| `top_p` | `0.95` | `0.95` |
| `max_output_tokens` | `8192` | `8192` |

---

## Model-Specific Requirements

### Gemini 3 Pro Image Preview

✅ **Must do**:
- Preserve thought signatures in multi-turn (SDK handles automatically)
- Keep temperature at 1.0
- Use uppercase 'K' for image_size

✅ **Can do**:
- Use Google Search grounding
- Generate 1K, 2K, or 4K images
- Include thought summaries

❌ **Cannot do**:
- Disable thinking mode
- Lower temperature below 1.0

### Gemini 2.5 Flash Image

✅ **Can do**:
- Adjust temperature
- Enable/disable thinking
- Use up to 3 reference images

❌ **Cannot do**:
- Configure image size (fixed ~1024px)
- Use Google Search grounding
- Generate 2K/4K images

---

## Complete Example

```python
from google import genai
from google.genai import types

client = genai.Client()

# Full configuration
config = types.GenerateContentConfig(
    # Output control
    response_modalities=['TEXT', 'IMAGE'],

    # Image settings
    image_config=types.ImageConfig(
        aspect_ratio="16:9",
        image_size="2K"
    ),

    # Behavior
    system_instruction="You are a professional data visualization expert.",

    # Thinking
    thinking_config=types.ThinkingConfig(
        include_thoughts=True
    ),

    # Generation parameters
    temperature=1.0,  # Keep at 1.0 for Gemini 3
    max_output_tokens=8192,

    # Tools
    tools=[{"google_search": {}}]  # Real-time data
)

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents="Create an infographic about recent climate data trends",
    config=config
)

# Process response
for part in response.parts:
    if part.text:
        print(f"Description: {part.text}")
    elif part.inline_data:
        image = part.as_image()
        image.save("climate_infographic.png")
```

---

## See Also

- [models.md](models.md) - Model capabilities and selection
- [prompt-templates.md](prompt-templates.md) - Effective prompting strategies
- [limitations.md](limitations.md) - Known limitations and workarounds
- [examples.md](examples.md) - Complete runnable examples
