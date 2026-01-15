---
name: generating-images-with-gemini
description: Generate and edit images using Google's Gemini API. Use for text-to-image generation, image editing, style transfer, multi-image composition, batch generation, or when user mentions Gemini image generation, creating images, editing photos, infographics, logos, or product mockups.
---

# Generating Gemini Images

Generate and edit images using Gemini's native image generation models. Supports text-to-image, image editing, multi-image composition, and batch generation.

## Quick start

### Basic text-to-image generation

```python
from google import genai

client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents="A serene Japanese garden with koi pond at sunset",
)

for part in response.parts:
    if part.inline_data:
        image = part.as_image()
        image.save("garden.png")
```

### Image editing

```python
from google import genai
from PIL import Image

client = genai.Client()

original = Image.open("photo.jpg")

response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=[
        "Add sunglasses to the person and change the sky to sunset colors",
        original
    ]
)

edited = response.parts[0].as_image()
edited.save("edited_photo.png")
```

### Multi-turn refinement

```python
from google import genai
from google.genai import types

client = genai.Client()

chat = client.chats.create(
    model="gemini-3-pro-image-preview",
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE']
    )
)

# Initial generation
r1 = chat.send_message("Create a minimalist logo for a coffee shop")
r1.parts[0].as_image().save("logo_v1.png")

# Refine
r2 = chat.send_message("Make it more modern and use brown tones")
r2.parts[0].as_image().save("logo_v2.png")

# Final tweak
r3 = chat.send_message("Add a coffee bean icon")
r3.parts[0].as_image().save("logo_final.png")
```

## Model selection

### Gemini 2.5 Flash Image
**Use when**: Speed and cost are priorities
- Fixed 1024px resolution
- Best with up to 3 reference images
- Fast, cost-effective generation
- Good for high-volume generation

### Gemini 3 Pro Image Preview
**Use when**: Professional quality is required
- 1K, 2K, 4K resolution support
- Up to 14 reference images
- Advanced text rendering
- Google Search grounding
- Complex multi-turn editing

**Quick decision**: Need 2K/4K or >3 reference images → Use Gemini 3 Pro. Otherwise → Use 2.5 Flash.

## Key capabilities

**Prompt templates**: [reference/prompt-templates.md](reference/prompt-templates.md) - Proven templates for common use cases

**Configuration**: [reference/configuration.md](reference/configuration.md) - Aspect ratios, resolutions, parameters

**Batch generation**: Run `python templates/batch-generation.py` or see code for batch API patterns - 50% cost reduction

**File management**: [reference/files-api.md](reference/files-api.md) - Upload/reuse large files

**CLI tool**: Run `python cli.py --help` for standalone command-line interface to all templates

## Critical notes

⚠️ **Important gotchas:**

1. **Temperature must stay at 1.0** for Gemini 3 Pro (lowering causes loops)
2. **Use uppercase 'K'** for image sizes ("2K" not "2k")
3. **Describe scenes narratively**, not as keyword lists

See [reference/limitations.md](reference/limitations.md) for complete details.

## Reference documentation

- **Model capabilities**: [reference/models.md](reference/models.md)
- **Prompting strategies**: [reference/prompt-templates.md](reference/prompt-templates.md)
- **API patterns**: [reference/api-patterns.md](reference/api-patterns.md)
- **Configuration options**: [reference/configuration.md](reference/configuration.md)
- **Complete examples**: [reference/examples.md](reference/examples.md)
- **Decision trees & tables**: [reference/reference-tables.md](reference/reference-tables.md)
