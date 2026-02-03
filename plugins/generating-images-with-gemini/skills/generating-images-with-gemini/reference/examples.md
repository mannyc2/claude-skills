# Complete Code Examples

This page provides complete, runnable code examples for common use cases.

All examples use the new Google GenAI SDK (`google-genai` package).

## Table of Contents

- Installation
- Example 1: Basic Text-to-Image
- Example 2: High-Resolution Image (2K)
- Example 3: Image Editing (Add Elements)
- Example 4: Semantic Inpainting
- Example 5: Style Transfer
- Example 6: Multi-Image Composition
- Example 7: Multi-Turn Iterative Refinement
- Example 8: Google Search Grounding
- Example 9: Batch Generation
- Example 10: File Upload and Reuse
- Example 11: Character Consistency
- Example 12: Logo Creation with Text
- Example 13: Thought Inspection
- Example 14: Error Handling with Retry
- Example 15: Complete Workflow - Product Mockup

---

## Installation

```bash
pip install google-genai pillow
export GOOGLE_API_KEY="your-api-key"
```

---

## Example 1: Basic Text-to-Image

**Use case**: Generate a simple image from a text prompt.

```python
from google import genai

client = genai.Client()

prompt = "A serene Japanese garden with koi pond at sunset, cherry blossoms in bloom"

response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=prompt
)

# Save the generated image
for part in response.parts:
    if part.inline_data:
        image = part.as_image()
        image.save("japanese_garden.png")
        print("✓ Image saved as 'japanese_garden.png'")
```

---

## Example 2: High-Resolution Image (2K)

**Use case**: Generate a high-quality image for print or professional use.

```python
from google import genai
from google.genai import types

client = genai.Client()

prompt = """
Create a professional product photograph of a minimalist ceramic coffee mug
in matte black. Studio lighting with soft shadows. Clean white background.
Ultra-realistic with sharp focus on product details.
"""

config = types.GenerateContentConfig(
    image_config=types.ImageConfig(
        aspect_ratio="1:1",
        image_size="2K"  # High resolution (MUST use uppercase 'K')
    ),
    response_modalities=['IMAGE']  # Image only, no text
)

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=prompt,
    config=config
)

for part in response.parts:
    if part.inline_data:
        image = part.as_image()
        image.save("product_photo_2k.png")
        print("✓ High-res image saved (2K resolution)")
```

---

## Example 3: Image Editing (Add Elements)

**Use case**: Add new elements to an existing photo.

```python
from google import genai
from PIL import Image

client = genai.Client()

# Load your image
original = Image.open("cat_photo.jpg")

prompt = """
Add a small wizard hat on the cat's head. Make it look natural
and match the lighting of the photo.
"""

response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=[prompt, original]
)

# Save edited image
for part in response.parts:
    if part.inline_data:
        edited = part.as_image()
        edited.save("cat_with_hat.png")
        print("✓ Edited image saved")
```

---

## Example 4: Semantic Inpainting (Change Specific Elements)

**Use case**: Change only specific parts of an image without manual masking.

```python
from google import genai
from PIL import Image

client = genai.Client()

living_room = Image.open("living_room.jpg")

prompt = """
Change only the blue sofa to be a vintage brown leather chesterfield sofa.
Keep everything else exactly the same - the pillows, lighting, walls,
and overall composition.
"""

response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=[prompt, living_room]
)

for part in response.parts:
    if part.inline_data:
        edited = part.as_image()
        edited.save("living_room_new_sofa.png")
        print("✓ Semantically edited image saved")
```

---

## Example 5: Style Transfer

**Use case**: Apply artistic style to a photograph.

```python
from google import genai
from PIL import Image

client = genai.Client()

city_photo = Image.open("city_street.jpg")

prompt = """
Transform this photograph into the artistic style of Vincent van Gogh's
'Starry Night'. Preserve the original composition of buildings and cars,
but render everything with swirling impasto brushstrokes and a dramatic
palette of deep blues and bright yellows.
"""

response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=[prompt, city_photo]
)

for part in response.parts:
    if part.inline_data:
        stylized = part.as_image()
        stylized.save("city_vangogh_style.png")
        print("✓ Stylized image saved")
```

---

## Example 6: Multi-Image Composition

**Use case**: Combine elements from multiple source images.

```python
from google import genai
from PIL import Image

client = genai.Client()

# Load source images
dress = Image.open("blue_dress.jpg")
model = Image.open("fashion_model.jpg")

prompt = """
Create a professional e-commerce fashion photo. Take the blue floral dress
from the first image and place it on the woman from the second image.
Generate a realistic full-body shot with proper lighting and shadows matching
the outdoor environment.
"""

response = client.models.generate_content(
    model="gemini-2.5-flash-image",  # Works with up to 3 images
    contents=[dress, model, prompt]
)

for part in response.parts:
    if part.inline_data:
        composite = part.as_image()
        composite.save("fashion_composite.png")
        print("✓ Composite image saved")
```

---

## Example 7: Multi-Turn Iterative Refinement

**Use case**: Gradually improve an image through conversation.

```python
from google import genai
from google.genai import types

client = genai.Client()

# Create chat session
chat = client.chats.create(
    model="gemini-3-pro-image-preview",
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE']
    )
)

# Turn 1: Initial generation
print("Creating initial logo...")
r1 = chat.send_message("Create a minimalist logo for a coffee shop called 'Bean There'")
r1.parts[0].as_image().save("logo_v1.png")
print("✓ Saved logo_v1.png")

# Turn 2: First refinement
print("\nMaking it more minimalist...")
r2 = chat.send_message("Make it more minimalist and use brown tones")
r2.parts[0].as_image().save("logo_v2.png")
print("✓ Saved logo_v2.png")

# Turn 3: Final tweak
print("\nAdding coffee bean icon...")
r3 = chat.send_message("Add a small coffee bean icon in the design")
r3.parts[0].as_image().save("logo_final.png")
print("✓ Saved logo_final.png")

print("\n✓ Iterative refinement complete! Check logo_v1, v2, and final.")
```

---

## Example 8: Google Search Grounding (Real-Time Data)

**Use case**: Generate images based on current events or real-time data.

```python
from google import genai
from google.genai import types

client = genai.Client()

prompt = """
Visualize the current weather forecast for the next 5 days in San Francisco
as a clean, modern weather chart. Include temperatures, weather icons, and
day labels.
"""

config = types.GenerateContentConfig(
    response_modalities=['TEXT', 'IMAGE'],
    image_config=types.ImageConfig(aspect_ratio="16:9"),
    tools=[{"google_search": {}}]  # Enable Google Search grounding
)

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",  # Only 3 Pro supports grounding
    contents=prompt,
    config=config
)

# Display sources used
if response.candidates and response.candidates[0].grounding_metadata:
    print("📚 Sources consulted:")
    metadata = response.candidates[0].grounding_metadata
    if hasattr(metadata, 'grounding_chunks'):
        for chunk in metadata.grounding_chunks:
            if hasattr(chunk, 'web'):
                print(f"  - {chunk.web.title}")
                print(f"    {chunk.web.uri}")

# Save image
for part in response.parts:
    if part.inline_data:
        image = part.as_image()
        image.save("sf_weather_forecast.png")
        print("\n✓ Image saved with real-time data")
```

---

## Example 9: Batch Generation (High Volume)

**Use case**: Generate many images efficiently at 50% cost reduction.

```python
import json
import time
from google import genai
from google.genai import types

client = genai.Client()

# Define prompts
prompts = [
    "A red apple on white background, studio lighting",
    "A blue butterfly on a flower, macro photography",
    "A yellow sunflower in a field, golden hour",
    "A purple galaxy swirl, space photography",
    "A green forest path in autumn, cinematic"
]

# Create JSONL file
jsonl_file = "batch_requests.jsonl"
with open(jsonl_file, "w") as f:
    for i, prompt in enumerate(prompts):
        request = {
            "key": f"request-{i}",
            "request": {
                "contents": [{"parts": [{"text": prompt}]}],
                "generation_config": {"responseModalities": ["IMAGE"]}
            }
        }
        f.write(json.dumps(request) + "\n")

print(f"✓ Created {jsonl_file} with {len(prompts)} requests")

# Upload JSONL
uploaded = client.files.upload(
    file=jsonl_file,
    config=types.UploadFileConfig(mime_type='jsonl')
)
print(f"✓ Uploaded batch file")

# Submit batch job
job = client.batches.create(
    model="gemini-2.5-flash-image",
    src=uploaded.name,
    config={'display_name': "color-themed-images"}
)
print(f"✓ Batch job created: {job.name}")
print(f"  Status: {job.state.name}")

# Monitor progress
print("\nMonitoring batch job (can take up to 24 hours)...")
while True:
    job = client.batches.get(name=job.name)
    print(f"  State: {job.state.name}")

    if job.state.name in ['JOB_STATE_SUCCEEDED', 'JOB_STATE_FAILED']:
        break

    time.sleep(30)  # Check every 30 seconds

# Download results
if job.state.name == 'JOB_STATE_SUCCEEDED':
    print("\n✓ Job completed! Downloading results...")

    # Download the output JSONL file
    result_bytes = client.files.download(file=job.dest.file_name)
    result_content = result_bytes.decode('utf-8')

    # Parse JSONL results
    import json
    import base64
    from PIL import Image
    import io

    results = []
    for line in result_content.strip().split('\n'):
        if line.strip():
            results.append(json.loads(line))

    # Save images
    output_dir = "batch_outputs"
    import os
    os.makedirs(output_dir, exist_ok=True)

    for result in results:
        key = result.get('key', 'unknown')
        response = result.get('response', {})
        candidates = response.get('candidates', [])

        if candidates:
            content = candidates[0].get('content', {})
            parts = content.get('parts', [])

            for part in parts:
                if 'inlineData' in part:
                    # Decode base64 image data
                    image_data = base64.b64decode(part['inlineData']['data'])
                    image = Image.open(io.BytesIO(image_data))

                    # Save image
                    image_path = f"{output_dir}/{key}.png"
                    image.save(image_path)
                    print(f"  ✓ Saved {image_path}")

    print("✓ Batch generation complete")
else:
    print(f"\n❌ Job failed: {job.state.name}")
```

---

## Example 10: File Upload and Reuse

**Use case**: Upload a large file once and use it multiple times.

```python
from google import genai
from google.genai import types

client = genai.Client()

# Upload file once (for reuse or files >20MB)
print("Uploading reference image...")
uploaded = client.files.upload(
    file="large_reference.jpg",
    config=types.UploadFileConfig(
        display_name='reference-photo',
        mime_type='image/jpeg'
    )
)
print(f"✓ Uploaded: {uploaded.name}")

# Use multiple times with different prompts
styles = ["vintage", "modern", "abstract", "watercolor"]

for style in styles:
    print(f"\nApplying {style} style...")
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[uploaded, f"Apply a {style} filter to this image"]
    )

    for part in response.parts:
        if part.inline_data:
            image = part.as_image()
            image.save(f"output_{style}.png")
            print(f"✓ Saved output_{style}.png")

# Cleanup
client.files.delete(name=uploaded.name)
print("\n✓ Cleaned up uploaded file")
```

---

## Example 11: Character Consistency (360 View)

**Use case**: Generate multiple angles of the same character/person.

```python
from google import genai
from PIL import Image

client = genai.Client()

# Load reference image
person_image = Image.open("person_portrait.jpg")

# Generate different angles
angles = [
    "A studio portrait of this person against white, looking forward",
    "A studio portrait of this person against white, in profile looking right",
    "A studio portrait of this person against white, in profile looking left",
    "A studio portrait of this person against white, from behind"
]

for i, prompt in enumerate(angles):
    print(f"\nGenerating angle {i+1}...")
    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=[prompt, person_image]
    )

    for part in response.parts:
        if part.inline_data:
            image = part.as_image()
            image.save(f"person_angle_{i+1}.png")
            print(f"✓ Saved person_angle_{i+1}.png")

print("\n✓ Generated all angles with character consistency")
```

---

## Example 12: Logo Creation with Text

**Use case**: Create a professional logo with specific text.

```python
from google import genai
from google.genai import types

client = genai.Client()

# Step 1: Generate text content first (for better accuracy)
text_response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Write a short, catchy tagline for a coffee shop called 'Bean There'"
)

tagline = text_response.text.strip()
print(f"Generated tagline: {tagline}")

# Step 2: Create logo with the text
logo_prompt = f"""
Create a modern, minimalist logo for a coffee shop called 'Bean There'.
Include the tagline: '{tagline}'
Use clean, bold sans-serif font. Black and white color scheme.
Incorporate a coffee bean icon in a clever way. Square format.
"""

config = types.GenerateContentConfig(
    image_config=types.ImageConfig(aspect_ratio="1:1")
)

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",  # Better for text rendering
    contents=logo_prompt,
    config=config
)

for part in response.parts:
    if part.inline_data:
        image = part.as_image()
        image.save("coffee_shop_logo.png")
        print("✓ Logo saved as 'coffee_shop_logo.png'")
```

---

## Example 13: Thought Inspection (Debugging)

**Use case**: Understand the model's reasoning process.

```python
from google import genai
from google.genai import types

client = genai.Client()

prompt = "Create a detailed infographic about the solar system with accurate planetary sizes"

config = types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(include_thoughts=True)
)

print("Generating with thinking enabled...\n")
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=prompt,
    config=config
)

# Separate thoughts from final output
thoughts = []
outputs = []

for part in response.parts:
    if part.thought:
        thoughts.append(part)
    else:
        outputs.append(part)

print(f"💭 Model generated {len(thoughts)} thoughts")
for i, thought in enumerate(thoughts, 1):
    if thought.text:
        print(f"\nThought {i}: {thought.text[:100]}...")

print(f"\n✅ Final output has {len(outputs)} parts")
for part in outputs:
    if part.inline_data:
        image = part.as_image()
        image.save("solar_system.png")
        print("✓ Final image saved as 'solar_system.png'")
```

---

## Example 14: Error Handling with Retry

**Use case**: Robust generation with automatic retry.

```python
from google import genai
import time

client = genai.Client()

def generate_with_retry(prompt, model="gemini-2.5-flash-image", max_retries=3):
    """Generate with exponential backoff retry."""

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            if response.candidates:
                return response
            else:
                print(f"No candidates (attempt {attempt + 1})")

        except Exception as e:
            print(f"Error (attempt {attempt + 1}): {e}")

            if attempt < max_retries - 1:
                wait = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                print(f"Retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise

    return None

# Usage
prompt = "A sunset over mountains"
response = generate_with_retry(prompt)

if response:
    for part in response.parts:
        if part.inline_data:
            image = part.as_image()
            image.save("sunset.png")
            print("✓ Image saved successfully")
else:
    print("❌ Failed to generate after retries")
```

---

## Example 15: Complete Workflow - Product Mockup

**Use case**: End-to-end workflow for creating a product mockup.

```python
from google import genai
from google.genai import types

client = genai.Client()

# Create chat for iterative refinement
chat = client.chats.create(
    model="gemini-3-pro-image-preview",
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
        system_instruction="You are a professional product designer specializing in mobile app mockups."
    )
)

print("Step 1: Creating initial mockup...")
r1 = chat.send_message(
    "Create a smartphone mockup displaying a weather app. Modern, clean design with temperature and forecast."
)
r1.parts[0].as_image().save("mockup_v1.png")
print("✓ Saved mockup_v1.png")

print("\nStep 2: Adjusting theme...")
r2 = chat.send_message(
    "Change to dark mode theme with blue accents"
)
r2.parts[0].as_image().save("mockup_v2.png")
print("✓ Saved mockup_v2.png")

print("\nStep 3: Adding realism...")
r3 = chat.send_message(
    "Add a hand holding the phone. Natural skin tone, casual setting."
)
r3.parts[0].as_image().save("mockup_v3.png")
print("✓ Saved mockup_v3.png")

print("\nStep 4: Final polish...")
config_final = types.GenerateContentConfig(
    image_config=types.ImageConfig(
        aspect_ratio="9:16",
        image_size="2K"  # High res for final
    )
)
r4 = chat.send_message(
    "Add professional lighting and shadows for a polished product photo look",
    config=config_final
)
r4.parts[0].as_image().save("mockup_final_2k.png")
print("✓ Saved mockup_final_2k.png (high resolution)")

print("\n✓ Complete workflow finished!")
print("Generated: mockup_v1.png, mockup_v2.png, mockup_v3.png, mockup_final_2k.png")
```

---

## See Also

- [api-patterns.md](api-patterns.md) - API usage patterns
- [prompt-templates.md](prompt-templates.md) - Effective prompting strategies
- [configuration.md](configuration.md) - Configuration options
- [limitations.md](limitations.md) - Known limitations
