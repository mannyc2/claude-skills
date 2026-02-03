# Prompting Strategies & Templates

This guide provides proven prompt templates and best practices for Gemini image generation.

## Table of Contents

- Core Principle
- Text-to-Image Templates (Photorealistic, Illustrations, Text in Images, Products, Minimalist, Comics, Google Search)
- Image Editing Templates (Adding/Removing, Inpainting, Style Transfer, Multi-Image, Detail Preservation, Sketch to Photo, Character Consistency)
- Best Practices (Be Specific, Context, Iterate, Step-by-Step, Semantic Negatives, Camera Control, Describe First, Few-Shot, Image Placement)
- Common Pitfalls
- Quick Template Selector

---

## Core Principle

**Describe the scene, don't just list keywords.**

Narrative, descriptive paragraphs produce better, more coherent images than disconnected word lists.

❌ **Bad**: "sunset, mountains, lake, reflection, colorful"
✅ **Good**: "A serene mountain landscape at sunset, with snow-capped peaks reflected in a still alpine lake. The sky glows with warm oranges and purples."

---

## Text-to-Image Templates

### 1. Photorealistic Scenes

**Template**:
```
A photorealistic [shot type] of [subject], [action or expression], set in
[environment]. The scene is illuminated by [lighting description], creating
a [mood] atmosphere. Captured with a [camera/lens details], emphasizing
[key textures and details]. The image should be in a [aspect ratio] format.
```

**Example**:
```python
prompt = """
A photorealistic close-up portrait of an elderly Japanese ceramicist with
deep, sun-etched wrinkles and a warm, knowing smile. He is carefully
inspecting a freshly glazed tea bowl. The setting is his rustic,
sun-drenched workshop. The scene is illuminated by soft, golden hour light
streaming through a window, highlighting the fine texture of the clay.
Captured with an 85mm portrait lens, resulting in a soft, blurred background
(bokeh). The overall mood is serene and masterful. Vertical portrait
orientation.
"""

response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=prompt
)
```

**Key photography terms to use**:
- **Camera angles**: wide-angle, close-up, macro, low-angle, high-angle, bird's eye
- **Lens types**: 85mm portrait, wide-angle, macro, fisheye
- **Lighting**: golden hour, softbox, three-point, natural light, studio-lit, rim lighting
- **Effects**: bokeh, depth of field, soft focus, motion blur
- **Shot types**: portrait, landscape, aerial, establishing shot

### 2. Stylized Illustrations & Stickers

**Template**:
```
A [style] sticker of a [subject], featuring [key characteristics] and a
[color palette]. The design should have [line style] and [shading style].
The background must be [background color/transparent].
```

**Example**:
```python
prompt = """
A kawaii-style sticker of a happy red panda wearing a tiny bamboo hat. It's
munching on a green bamboo leaf. The design features bold, clean outlines,
simple cel-shading, and a vibrant color palette. The background must be white.
"""

response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=prompt
)
```

**Popular styles**:
- Kawaii, chibi, anime, cartoon
- Pixel art, 8-bit, retro
- Watercolor, oil painting, impressionist
- Line art, sketch, ink drawing
- Flat design, minimalist, geometric

### 3. Accurate Text in Images

**Template**:
```
Create a [image type] for [brand/concept] with the text "[text to render]"
in a [font style]. The design should be [style description], with a
[color scheme].
```

**Example**:
```python
prompt = """
Create a modern, minimalist logo for a coffee shop called 'The Daily Grind'.
The text should be in a clean, bold, sans-serif font. The color scheme is
black and white. Put the logo in a circle. Use a coffee bean in a clever way.
"""

# Use Gemini 3 Pro Image for professional asset production
config = types.GenerateContentConfig(
    image_config=types.ImageConfig(aspect_ratio="1:1")
)

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=prompt,
    config=config
)
```

⚠️ **BEST PRACTICE**: For complex text, generate the text content first, then ask for the image:

```python
# Step 1: Generate text
text_response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Write a catchy title and subtitle for a climate change infographic"
)

# Step 2: Use that text in image generation
image_response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=f"Create an infographic with this text: {text_response.text}"
)
```

### 4. Product Mockups & Commercial Photography

**Template**:
```
A high-resolution, studio-lit product photograph of a [product description]
on a [background surface/description]. The lighting is a [lighting setup,
e.g., three-point softbox setup] to [lighting purpose]. The camera angle is
a [angle type] to showcase [specific feature]. Ultra-realistic, with sharp
focus on [key detail]. [Aspect ratio].
```

**Example**:
```python
prompt = """
A high-resolution, studio-lit product photograph of a minimalist ceramic
coffee mug in matte black, presented on a polished concrete surface. The
lighting is a three-point softbox setup designed to create soft, diffused
highlights and eliminate harsh shadows. The camera angle is a slightly
elevated 45-degree shot to showcase its clean lines. Ultra-realistic, with
sharp focus on the steam rising from the coffee. Square image.
"""

config = types.GenerateContentConfig(
    image_config=types.ImageConfig(aspect_ratio="1:1")
)

response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=prompt,
    config=config
)
```

### 5. Minimalist Design & Negative Space

**Template**:
```
A minimalist composition featuring a single [subject] positioned in the
[bottom-right/top-left/etc.] of the frame. The background is a vast, empty
[color] canvas, creating significant negative space. Soft, subtle lighting.
[Aspect ratio].
```

**Example**:
```python
prompt = """
A minimalist composition featuring a single, delicate red maple leaf
positioned in the bottom-right of the frame. The background is a vast, empty
off-white canvas, creating significant negative space for text. Soft,
diffused lighting from the top left. Square image.
"""

response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=prompt
)
```

**Use case**: Backgrounds for websites, presentations, marketing with text overlays

### 6. Sequential Art (Comics/Storyboards)

**Template**:
```
Make a [number] panel comic in a [style]. Put the character in a [type of scene].
```

**Example**:
```python
from PIL import Image

character_image = Image.open('/path/to/character.jpg')
text_input = """
Make a 3 panel comic in a gritty, noir art style with high-contrast black
and white inks. Put the character in a humorous scene at a coffee shop.
"""

# Use Gemini 3 Pro Image for text accuracy and storytelling
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=[text_input, character_image],
)
```

### 7. Grounding with Google Search

**Template**: Reference current events, weather, sports, etc.

**Example**:
```python
prompt = """
Make a simple but stylish graphic of last night's Arsenal game in the
Champion's League
"""

config = types.GenerateContentConfig(
    response_modalities=['Text', 'Image'],
    image_config=types.ImageConfig(aspect_ratio="16:9"),
    tools=[{"google_search": {}}]
)

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",  # Only 3 Pro supports grounding
    contents=prompt,
    config=config
)

# Response includes grounding metadata
print("Sources:", response.candidates[0].grounding_metadata.grounding_chunks)
```

**Other examples**:
- "Visualize the current weather forecast for the next 5 days in San Francisco"
- "Create a chart showing yesterday's stock market performance"
- "Design an infographic about recent climate data"

---

## Image Editing Templates

### 1. Adding and Removing Elements

**Template**:
```
Using the provided image of [subject], please [add/remove/modify] [element]
to/from the scene. Ensure the change is [description of how the change should
integrate].
```

**Example**:
```python
from PIL import Image

image_input = Image.open('/path/to/cat_photo.png')
text_input = """
Using the provided image of my cat, please add a small, knitted wizard hat
on its head. Make it look like it's sitting comfortably and matches the soft
lighting of the photo.
"""

response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=[text_input, image_input],
)
```

### 2. Inpainting (Semantic Masking)

**Template**:
```
Using the provided image, change only the [specific element] to [new
element/description]. Keep everything else in the image exactly the same,
preserving the original style, lighting, and composition.
```

**Example**:
```python
living_room_image = Image.open('/path/to/living_room.png')
text_input = """
Using the provided image of a living room, change only the blue sofa to be
a vintage, brown leather chesterfield sofa. Keep the rest of the room,
including the pillows on the sofa and the lighting, unchanged.
"""

response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=[text_input, living_room_image],
)
```

**No masks needed** - Gemini uses semantic understanding to identify and modify specific elements.

### 3. Style Transfer

**Template**:
```
Transform the provided photograph of [subject] into the artistic style of
[artist/art style]. Preserve the original composition but render it with
[description of stylistic elements].
```

**Example**:
```python
city_image = Image.open('/path/to/city.png')
text_input = """
Transform the provided photograph of a modern city street at night into the
artistic style of Vincent van Gogh's 'Starry Night'. Preserve the original
composition of buildings and cars, but render all elements with swirling,
impasto brushstrokes and a dramatic palette of deep blues and bright yellows.
"""

response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=[text_input, city_image],
)
```

### 4. Multi-Image Composition

**Template**:
```
Create a new image by combining the elements from the provided images. Take
the [element from image 1] and place it with/on the [element from image 2].
The final image should be a [description of the final scene].
```

**Example**:
```python
dress_image = Image.open('/path/to/dress.png')
model_image = Image.open('/path/to/model.png')

text_input = """
Create a professional e-commerce fashion photo. Take the blue floral dress
from the first image and let the woman from the second image wear it.
Generate a realistic, full-body shot of the woman wearing the dress, with
the lighting and shadows adjusted to match the outdoor environment.
"""

response = client.models.generate_content(
    model="gemini-2.5-flash-image",  # Works with up to 3 images
    contents=[dress_image, model_image, text_input],
)
```

### 5. High-Fidelity Detail Preservation

**Template**:
```
Using the provided images, place [element from image 2] onto [element from
image 1]. Ensure that the features of [element from image 1] remain
completely unchanged. The added element should [description of how the
element should integrate].
```

**Example**:
```python
woman_image = Image.open('/path/to/woman.png')
logo_image = Image.open('/path/to/logo.png')
text_input = """
Take the first image of the woman with brown hair, blue eyes, and a neutral
expression. Add the logo from the second image onto her black t-shirt.
Ensure the woman's face and features remain completely unchanged. The logo
should look like it's naturally printed on the fabric, following the folds
of the shirt.
"""

response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=[woman_image, logo_image, text_input],
)
```

### 6. Bring Something to Life (Sketch to Photo)

**Template**:
```
Turn this rough [medium] sketch of a [subject] into a [style description]
photo. Keep the [specific features] from the sketch but add [new details/materials].
```

**Example**:
```python
sketch_image = Image.open('/path/to/car_sketch.png')
text_input = """
Turn this rough pencil sketch of a futuristic car into a polished photo of
the finished concept car in a showroom. Keep the sleek lines and low profile
from the sketch but add metallic blue paint and neon rim lighting.
"""

# Use Gemini 3 Pro Image for better rendering quality
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=[sketch_image, text_input],
)
```

### 7. Character Consistency (360 View)

**Template**:
```
A studio portrait of [person] against [background], [looking forward/in profile looking right/etc.]
```

**Example**:
```python
image_input = Image.open('/path/to/person.jpg')

# First angle
text_input = "A studio portrait of this man against white, in profile looking right"
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=[text_input, image_input],
)

# Save and use in next prompt for consistency
# Include previously generated images in subsequent prompts
```

---

## Best Practices

### 1. Be Hyper-Specific

❌ **Bad**: "fantasy armor"
✅ **Good**: "ornate elven plate armor, etched with silver leaf patterns, with a high collar and pauldrons shaped like falcon wings"

The more specific your description, the better the result.

### 2. Provide Context and Intent

Explain the *purpose* of the image:

```python
prompt = "Create a logo for a high-end, minimalist skincare brand targeting millennials"
# Better than: "Create a logo"
```

### 3. Iterate and Refine

Use multi-turn chat for incremental improvements:

```python
chat = client.chats.create(model='gemini-3-pro-image-preview')

response = chat.send_message("Create a sunset landscape")
# Review image
response = chat.send_message("That's great, but can you make the lighting a bit warmer?")
response = chat.send_message("Perfect! Now add a small sailboat on the horizon")
```

### 4. Use Step-by-Step Instructions

For complex scenes, break it down:

```python
prompt = """
First, create a background of a serene, misty forest at dawn.
Then, in the foreground, add a moss-covered ancient stone altar.
Finally, place a single, glowing sword on top of the altar.
"""
```

### 5. Use "Semantic Negative Prompts"

Don't say what you DON'T want - describe what you DO want:

❌ **Bad**: "no cars, no people, no buildings"
✅ **Good**: "an empty, pristine wilderness landscape with untouched nature"

### 6. Control the Camera

Use photographic language:

- `wide-angle shot` - Broad view
- `macro shot` - Extreme close-up
- `low-angle perspective` - Looking up (makes subject powerful)
- `high-angle perspective` - Looking down (makes subject small)
- `bokeh` - Blurred background
- `shallow depth of field` - Sharp subject, blurred background
- `golden hour lighting` - Warm, soft morning/evening light
- `three-point lighting` - Professional studio setup

### 7. Ask Model to Describe Image First

When output seems generic or you want better tailoring:

```python
prompt = """
First, describe what you see in this image in detail.
Then, create a stylized cartoon version maintaining all the key elements you identified.
"""
```

This helps the model better understand context before generating.

### 8. Few-Shot Examples

Provide example image-text pairs to teach the pattern:

```python
contents = [
    "Example 1 - Input photo of sunset:",
    example_image_1,
    "Example 1 - Desired watercolor style output:",
    watercolor_example_1,
    "Example 2 - Input photo of mountain:",
    example_image_2,
    "Example 2 - Desired watercolor style output:",
    watercolor_example_2,
    "Now apply the same watercolor style to this image:",
    user_image,
]

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=contents
)
```

Typically 2-3 examples is effective.

### 9. Image Placement

**For single-image prompts**: Put image BEFORE text for better results

```python
contents = [image, "Caption this image"]  # ✅ Better
# vs
contents = ["Caption this image", image]  # ⚠️ Okay but not optimal
```

---

## Common Pitfalls

### ❌ Keyword Salad

**Bad**:
```
"sunset mountains lake trees clouds orange purple sky reflection water"
```

**Good**:
```
"A mountain landscape at sunset, where snow-capped peaks are reflected in a calm alpine lake. The sky transitions from deep orange near the horizon to soft purple overhead. Pine trees frame the scene."
```

### ❌ Vague Descriptions

**Bad**:
```
"A nice house"
```

**Good**:
```
"A charming Victorian-era house with white clapboard siding, forest green shutters, and a wraparound porch. The architecture features ornate gingerbread trim. Set in autumn with colorful leaves."
```

### ❌ Conflicting Instructions

**Bad**:
```
"Create a minimalist design that's also very detailed and ornate"
```

**Good**:
```
"Create a minimalist design with one ornate focal point element"
```

### ❌ Unrealistic Expectations

**Bad**:
```
"Generate 10 different images showing all angles"
```

(Model typically generates 1 image per request)

**Good**:
```
Use multi-turn chat for multiple iterations, or batch API for multiple variations
```

---

## Quick Template Selector

**I need to create...**

- **Product photo** → Template #4 (Product Mockups)
- **Logo/branding** → Template #3 (Accurate Text)
- **Social media graphic** → Template #5 (Minimalist Design) or #7 (Google Search)
- **Realistic photo** → Template #1 (Photorealistic Scenes)
- **Illustration/sticker** → Template #2 (Stylized Illustrations)
- **Comic/storyboard** → Template #6 (Sequential Art)
- **Edit existing image** → Image Editing Templates #1-7

---

## See Also

- [configuration.md](configuration.md) - Configure aspect ratios, resolutions, etc.
- [examples.md](examples.md) - Complete runnable code examples
- [limitations.md](limitations.md) - Known limitations and workarounds
