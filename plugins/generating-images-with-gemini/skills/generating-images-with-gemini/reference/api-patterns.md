# API Patterns & Code Structure

Complete reference for API usage patterns, code structure, and common workflows.

## Table of Contents

- Client Initialization
- Core Generation Patterns (Text-to-Image, Image-to-Image, Multi-Turn, Streaming, Batch, File Upload)
- Response Parsing Patterns
- Configuration Patterns
- Multi-Image Composition
- Error Handling
- Workflow Patterns
- Advanced Patterns
- Import Patterns

---

## Client Initialization

### Basic Setup

```python
from google import genai
from google.genai import types
from PIL import Image

# Initialize client (uses GOOGLE_API_KEY environment variable)
client = genai.Client()
```

### With Explicit API Key

```python
client = genai.Client(api_key="your-api-key-here")
```

---

## Core Generation Patterns

### 1. Basic Text-to-Image

**Pattern**: Single prompt → single image

```python
from google import genai

client = genai.Client()

prompt = "A serene Japanese garden with koi pond at sunset"

response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=prompt
)

# Extract and save image
for part in response.parts:
    if part.text:
        print(part.text)
    elif part.inline_data:
        image = part.as_image()
        image.save("output.png")
```

**Use when**: Simple one-shot generation

---

### 2. Image-to-Image Editing

**Pattern**: Image + prompt → edited image

```python
from google import genai
from PIL import Image

client = genai.Client()

# Load reference image
original = Image.open("photo.jpg")

prompt = "Add sunglasses to the person and change sky to sunset colors"

response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=[prompt, original]  # Note: prompt first recommended
)

# Save edited image
for part in response.parts:
    if part.inline_data:
        edited = part.as_image()
        edited.save("edited.png")
```

**Use when**: Modifying existing images

**Image placement**: Put image BEFORE text for better results:
```python
contents=[original, prompt]  # ✅ Better
# vs
contents=[prompt, original]  # ⚠️ Okay but not optimal
```

---

### 3. Multi-Turn Chat

**Pattern**: Iterative refinement through conversation

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

# Turn 1
response1 = chat.send_message("Create a minimalist logo for a coffee shop")
response1.parts[0].as_image().save("logo_v1.png")

# Turn 2
response2 = chat.send_message("Make it more modern and use brown tones")
response2.parts[0].as_image().save("logo_v2.png")

# Turn 3
response3 = chat.send_message("Add a coffee bean icon")
response3.parts[0].as_image().save("logo_final.png")
```

**Use when**: Iteratively refining images

**SDK handles**:
- Conversation history
- Thought signatures (Gemini 3 Pro)
- Context preservation

---

### 4. Streaming Generation

**Pattern**: Progressive output for UX feedback

```python
from google import genai

client = genai.Client()

print("Generating...")
for chunk in client.models.generate_content_stream(
    model="gemini-2.5-flash-image",
    contents="A futuristic city skyline"
):
    for part in chunk.candidates[0].content.parts:
        if part.text:
            print(part.text, end="")
```

**Use when**: Want to show progress to users

**Note**: Images arrive in final chunk, text streams incrementally

---

### 5. Batch Generation

**Pattern**: High-volume, non-urgent generation

```python
import json
from google import genai
from google.genai import types

client = genai.Client()

# Create JSONL file
requests = [
    {
        "key": f"request-{i}",
        "request": {
            "contents": [{"parts": [{"text": f"A {color} flower"}]}],
            "generation_config": {"responseModalities": ["IMAGE"]}
        }
    }
    for i, color in enumerate(["red", "blue", "yellow"])
]

with open("batch.jsonl", "w") as f:
    for req in requests:
        f.write(json.dumps(req) + "\n")

# Upload and submit
uploaded = client.files.upload(
    file="batch.jsonl",
    config=types.UploadFileConfig(mime_type='jsonl')
)

job = client.batches.create(
    model="gemini-2.5-flash-image",
    src=uploaded.name,
    config={'display_name': "flowers"}
)

# Monitor
import time
while True:
    job = client.batches.get(name=job.name)
    if job.state.name in ['JOB_STATE_SUCCEEDED', 'JOB_STATE_FAILED']:
        break
    time.sleep(30)

# Download results
if job.state.name == 'JOB_STATE_SUCCEEDED':
    results = client.files.download(file=job.dest.file_name)
    # Process JSONL results...
```

**Use when**:
- Generating 10+ images
- Can wait up to 24 hours
- Want 50% cost reduction

---

### 6. File Upload Pattern

**Pattern**: Reusable or large file handling

```python
from google import genai
from google.genai import types

client = genai.Client()

# Upload once
uploaded = client.files.upload(
    file="large_reference.jpg",
    config=types.UploadFileConfig(
        display_name='reference-photo',
        mime_type='image/jpeg'
    )
)

# Use multiple times
for prompt in ["Make it vintage", "Make it modern", "Make it abstract"]:
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[uploaded, prompt]
    )
    # Save result...

# Cleanup
client.files.delete(name=uploaded.name)
```

**Use when**:
- File >20MB
- Reusing same file across requests
- Managing file lifecycle explicitly

---

## Response Parsing Patterns

### Standard Response Structure

```python
response = client.models.generate_content(...)

# Response structure:
# response.candidates[0].content.parts[]
#   - Each part is either text or inline_data (image)

for part in response.parts:
    # Text content
    if part.text:
        print(f"Text: {part.text}")

    # Image content
    elif part.inline_data:
        image = part.as_image()
        image.save("output.png")
        # Or access raw data:
        # data = part.inline_data.data
        # mime_type = part.inline_data.mime_type

    # Thought (Gemini 3 Pro with thinking enabled)
    if hasattr(part, 'thought') and part.thought:
        print(f"Thought: {part.text}")

    # Thought signature (Gemini 3 Pro)
    if hasattr(part, 'thought_signature') and part.thought_signature:
        signature = part.thought_signature
        # Preserve for multi-turn
```

### Checking for Success

```python
response = client.models.generate_content(...)

if response.candidates:
    # Success - process parts
    for part in response.candidates[0].content.parts:
        if part.inline_data:
            image = part.as_image()
            image.save("output.png")
else:
    # No candidates - generation failed
    print("No candidates in response")
```

### Extracting Grounding Metadata

```python
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=prompt,
    config=types.GenerateContentConfig(
        tools=[{"google_search": {}}]
    )
)

if response.candidates and response.candidates[0].grounding_metadata:
    metadata = response.candidates[0].grounding_metadata

    # Search entry point
    if hasattr(metadata, 'search_entry_point'):
        print(metadata.search_entry_point)

    # Grounding chunks (sources)
    if hasattr(metadata, 'grounding_chunks'):
        for chunk in metadata.grounding_chunks:
            if hasattr(chunk, 'web'):
                print(f"{chunk.web.title} - {chunk.web.uri}")
```

---

## Configuration Patterns

### Minimal Configuration

```python
# Just the prompt
response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents="A sunset landscape"
)
```

### Standard Configuration

```python
config = types.GenerateContentConfig(
    image_config=types.ImageConfig(
        aspect_ratio="16:9"
    ),
    response_modalities=['IMAGE']  # Image only
)

response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=prompt,
    config=config
)
```

### Advanced Configuration

```python
config = types.GenerateContentConfig(
    response_modalities=['TEXT', 'IMAGE'],
    image_config=types.ImageConfig(
        aspect_ratio="16:9",
        image_size="2K"
    ),
    system_instruction="You are a professional designer",
    thinking_config=types.ThinkingConfig(
        include_thoughts=True
    ),
    temperature=1.0,
    tools=[{"google_search": {}}]
)

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=prompt,
    config=config
)
```

---

## Multi-Image Composition Pattern

```python
from google import genai
from PIL import Image

client = genai.Client()

# Load multiple images
background = Image.open("background.jpg")
person = Image.open("person.png")
logo = Image.open("logo.png")

# Compose
prompt = """
Create a professional photo: place the person from image 2 in front of
the background from image 1, and add the logo from image 3 in the top right.
"""

response = client.models.generate_content(
    model="gemini-2.5-flash-image",  # Best with up to 3 images
    contents=[background, person, logo, prompt]
)

composite = response.parts[0].as_image()
composite.save("composite.png")
```

**Image limits**:
- Gemini 2.5 Flash: Best with ≤3 images
- Gemini 3 Pro: Up to 14 images (6 objects + 5 humans)

---

## Error Handling Pattern

```python
from google import genai
from google.genai import types
import time

client = genai.Client()

def generate_with_retry(prompt, max_retries=3):
    """Generate with exponential backoff retry."""

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=prompt
            )

            if response.candidates:
                return response
            else:
                print(f"No candidates (attempt {attempt + 1})")

        except Exception as e:
            print(f"Error (attempt {attempt + 1}): {e}")

            if attempt < max_retries - 1:
                wait = 2 ** attempt  # Exponential backoff
                print(f"Retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise

    return None

# Usage
response = generate_with_retry("A sunset landscape")
```

---

## Workflow Patterns

### Pattern 1: Single-Shot Generation

```
User Input → Generate → Save → Done
```

**Code**:
```python
response = client.models.generate_content(model, contents=prompt)
image = response.parts[0].as_image()
image.save("output.png")
```

**Best for**: One-off images

---

### Pattern 2: Iterative Refinement

```
Generate → Review → Refine → Review → Refine → Done
```

**Code**:
```python
chat = client.chats.create(model="gemini-3-pro-image-preview")

# Initial
r1 = chat.send_message("Create a logo")
r1.parts[0].as_image().save("v1.png")

# Refine
r2 = chat.send_message("Make it more minimalist")
r2.parts[0].as_image().save("v2.png")

# Final
r3 = chat.send_message("Add brand colors")
r3.parts[0].as_image().save("final.png")
```

**Best for**: Professional assets requiring feedback

---

### Pattern 3: Batch Production

```
Define Requests → Upload → Submit → Monitor → Download → Process
```

**Code**: See "Batch Generation" pattern above

**Best for**: High-volume, non-urgent generation

---

### Pattern 4: Image Editing Pipeline

```
Load Image → Edit 1 → Edit 2 → Edit 3 → Save
```

**Code**:
```python
image = Image.open("original.jpg")

# Edit 1: Style transfer
r1 = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=[image, "Make it look like a painting"]
)
edited1 = r1.parts[0].as_image()

# Edit 2: Add element
r2 = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=[edited1, "Add a moon in the sky"]
)
edited2 = r2.parts[0].as_image()

edited2.save("final.png")
```

**Best for**: Complex multi-step edits

---

### Pattern 5: A/B Testing Variations

```
Define Variations → Generate All → Compare → Select Best
```

**Code**:
```python
variations = [
    "minimalist logo with blue tones",
    "minimalist logo with green tones",
    "minimalist logo with purple tones"
]

for i, prompt in enumerate(variations):
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=prompt
    )
    response.parts[0].as_image().save(f"variation_{i}.png")
```

**Best for**: Exploring design options

---

## Advanced Patterns

### Thought Inspection (Gemini 3 Pro)

```python
config = types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(include_thoughts=True)
)

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents="Create a complex infographic",
    config=config
)

# Separate thoughts from output
thoughts = []
outputs = []

for part in response.parts:
    if part.thought:
        thoughts.append(part)
    else:
        outputs.append(part)

print(f"Model generated {len(thoughts)} thoughts")
print(f"Final output has {len(outputs)} parts")
```

### Conversation History Access

```python
chat = client.chats.create(model="gemini-3-pro-image-preview")

# Have conversation
chat.send_message("Create a logo")
chat.send_message("Make it bigger")
chat.send_message("Change color to blue")

# Review history
for message in chat.get_history():
    print(f"{message.role}:")
    for part in message.parts:
        if part.text:
            print(f"  Text: {part.text[:50]}...")
        elif hasattr(part, 'inline_data') and part.inline_data:
            print(f"  Image: {part.inline_data.mime_type}")
```

### Custom System Instructions

```python
config = types.GenerateContentConfig(
    system_instruction="""
    You are a professional product photographer specializing in e-commerce.

    Guidelines:
    - Always use soft, diffused lighting
    - Create clean, white backgrounds
    - Emphasize product details and textures
    - Maintain consistent style across all images
    """
)

response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents="Product photo of a ceramic mug",
    config=config
)
```

---

## Import Patterns

### Minimal Imports

```python
from google import genai

client = genai.Client()
```

### Standard Imports

```python
from google import genai
from google.genai import types
from PIL import Image
```

### Full Imports

```python
from google import genai
from google.genai import types
from PIL import Image
import json
import time
```

---

## See Also

- [configuration.md](configuration.md) - Detailed configuration options
- [examples.md](examples.md) - Complete runnable examples
- [limitations.md](limitations.md) - Known limitations and workarounds
- [files-api.md](files-api.md) - File upload and management patterns
