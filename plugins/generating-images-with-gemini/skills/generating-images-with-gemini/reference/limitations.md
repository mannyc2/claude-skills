# Limitations & Gotchas

This guide documents known limitations, common pitfalls, and important constraints when using Gemini image generation.

## Table of Contents

- Critical Warnings (Temperature, Case Sensitivity, Thought Signatures)
- Language Support
- Input Format Constraints
- Output Behavior
- Reference Image Limits
- File Size and Retention
- Text Generation for Images
- SynthID Watermarks
- Thinking Mode Constraints
- Google Search Grounding Limitations
- Resolution Constraints
- Common Pitfalls
- Model-Specific Limitations
- Troubleshooting Common Issues

---

## Critical Warnings

### ⚠️ Temperature Must Stay at 1.0 (Gemini 3)

**Problem**: Lowering temperature on Gemini 3 Pro Image causes loops and degraded performance.

```python
# ❌ BAD - Causes issues on Gemini 3
config = types.GenerateContentConfig(
    temperature=0.7  # DON'T DO THIS
)

# ✅ GOOD - Keep default
config = types.GenerateContentConfig(
    temperature=1.0  # Always use this for Gemini 3
)
```

**Why**: Gemini 3 models are optimized for temperature=1.0, especially for complex reasoning tasks.

**Applies to**: Gemini 3 Pro Image Preview only
**Safe to adjust**: Gemini 2.5 Flash Image

---

### ⚠️ Case Sensitivity in Parameters

**Problem**: Lowercase 'k' in image_size will be rejected.

```python
# ❌ FAILS
image_size="2k"  # Lowercase - rejected

# ✅ WORKS
image_size="2K"  # Uppercase - correct
```

**Other case-sensitive parameters**:
- Model names: Use exact case (`gemini-2.5-flash-image`)
- Aspect ratios: Use exact format (`"16:9"` not `"16-9"`)

---

### ⚠️ Thought Signatures Must Be Preserved (Gemini 3 Pro)

**Problem**: Multi-turn conversations break if thought signatures aren't preserved.

**Solution**: Use the official SDK's chat feature (handles automatically):

```python
# ✅ GOOD - SDK handles signatures
chat = client.chats.create(model="gemini-3-pro-image-preview")
chat.send_message("Create a logo")
chat.send_message("Make it bigger")  # Signatures preserved automatically
```

**If manually managing history** (advanced):
- All image parts have `thought_signature` field
- First text part after thoughts has signature
- Must pass signatures back exactly as received

---

## Language Support

### Best Performance Languages

✅ **Fully supported** (best quality):
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

⚠️ **Other languages**: May work but with reduced quality

---

## Input Format Constraints

### Supported Input Types

✅ **Supported**:
- Text prompts
- Images (PNG, JPEG, WEBP, HEIC, HEIF)

❌ **NOT Supported**:
- Audio files
- Video files
- PDFs (for image generation context)

**Workaround**: Extract frames from video or convert PDF to images first.

---

## Output Behavior

### Number of Images Generated

**Limitation**: Model typically generates 1 image per request, not more.

```python
# ❌ This will likely generate only 1 image
prompt = "Generate 5 different variations of a logo"

# ✅ Use multi-turn or batch API instead
chat = client.chats.create(model="gemini-2.5-flash-image")
for i in range(5):
    response = chat.send_message(f"Generate logo variation {i+1}")
    # Save each image
```

**Workaround**: Use batch API for multiple images efficiently.

---

## Reference Image Limits

### Gemini 2.5 Flash Image

- **Optimal**: Up to 3 reference images
- **Effect**: More images may reduce quality
- **Recommendation**: Keep to 3 or fewer for best results

### Gemini 3 Pro Image Preview

- **Maximum**: 14 total reference images
  - Up to 6 object images (high-fidelity)
  - Up to 5 human images (character consistency)
- **Effect**: Exceeding limits may fail or reduce quality

**Example**:

```python
# ✅ GOOD - Within limits
images = [Image.open(f"object{i}.jpg") for i in range(6)]
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=["Combine these objects", *images]
)

# ❌ RISKY - Too many images
images = [Image.open(f"img{i}.jpg") for i in range(20)]  # May fail
```

---

## File Size and Retention

### Files API Limits

- **Total per project**: 20GB
- **Max per file**: 2GB
- **Retention period**: 48 hours (automatic deletion)
- **Download**: Cannot download files (input only, not for storage)

### When to Use Files API

Use Files API when:
- Total request size >20MB (including text, images, system instructions)
- Reusing same image across multiple requests
- Individual image files are very large

```python
# ✅ Use Files API for large/reused images
uploaded = client.files.upload(file="large_reference.jpg")

# Use multiple times
for prompt in ["Edit 1", "Edit 2", "Edit 3"]:
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[uploaded, prompt]
    )
```

### File Retention

**CRITICAL**: Files are automatically deleted after 48 hours.

- ✅ Manual deletion: Use `client.files.delete(name=file.name)` anytime
- ❌ Cannot extend: 48-hour period cannot be renewed
- ⚠️ Plan accordingly: Re-upload if needed after expiration

---

## Text Generation for Images

### Generate Text First, Then Image

**Problem**: Asking for specific text in images works poorly if done in one step.

```python
# ❌ LESS EFFECTIVE
prompt = "Create an infographic with title 'Climate Change' and subtitle 'The Facts'"

# ✅ MORE EFFECTIVE
# Step 1: Generate text
text_response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Write a title and subtitle for a climate change infographic"
)

# Step 2: Use that text in image
image_response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=f"Create an infographic with this text: {text_response.text}"
)
```

**Why**: Separating text generation from image generation produces more accurate text rendering.

---

## SynthID Watermarks

### Always Present

- **All generated images** include SynthID watermark
- **Cannot be disabled**
- **Invisible** to human eye
- **Purpose**: Provenance tracking

**Impact**: None on image quality or usability

---

## Thinking Mode Constraints

### Gemini 3 Pro Image Preview

✅ **Always thinks** (cannot disable)
- Generates up to 2 interim thought images (not charged)
- Last thought image is the final rendered image
- Must preserve thought signatures in multi-turn

### Gemini 2.5 Flash Image

✅ **Thinking disabled by default**
- Can enable: `thinking_budget=1024`
- Can disable (default): `thinking_budget=0`

**When to enable thinking** (2.5 Flash):
- Complex compositions
- Technical diagrams
- Multi-step reasoning needed

**When to disable thinking**:
- Simple images
- Speed priority
- Cost optimization

---

## Google Search Grounding Limitations

### Only Gemini 3 Pro

❌ **Not available** on Gemini 2.5 Flash Image

### Image Search Excluded

When using Google Search grounding:
- ✅ Text-based search results included
- ❌ Image search results excluded from grounding
- Returns top 3 web sources in `groundingChunks`

```python
# Search grounding uses text sources only
config = types.GenerateContentConfig(
    tools=[{"google_search": {}}]  # Text sources only
)
```

---

## Resolution Constraints

### Gemini 2.5 Flash Image

- **Fixed**: ~1024px resolution
- **Not configurable**: All aspect ratios produce ~1024px equivalent
- **Token cost**: 1290 tokens (all ratios)

### Gemini 3 Pro Image Preview

- **Configurable**: 1K, 2K, 4K
- **Token cost**: 1K/2K = 1120 tokens, 4K = 2000 tokens
- **Quality trade-off**: Higher resolution = better quality but higher cost

---

## Common Pitfalls

### 1. Keyword Salad Prompts

**Problem**: Listing disconnected keywords produces poor results.

```python
# ❌ BAD
"sunset mountains lake trees clouds orange purple"

# ✅ GOOD
"A mountain landscape at sunset, where peaks are reflected in a calm alpine lake. The sky transitions from orange to purple."
```

**Solution**: Use narrative, descriptive paragraphs.

### 2. Negative Prompts

**Problem**: Saying what you DON'T want doesn't work well.

```python
# ❌ BAD
"no cars, no people, no buildings"

# ✅ GOOD
"pristine wilderness landscape with untouched nature"
```

**Solution**: Describe what you DO want (semantic positive prompts).

### 3. Conflicting Instructions

**Problem**: Contradictory requirements confuse the model.

```python
# ❌ BAD
"minimalist design that's very detailed and ornate"

# ✅ GOOD
"minimalist design with one ornate focal point"
```

### 4. Inline Data Size Limit

**Problem**: Requests >20MB fail.

```python
# ❌ MAY FAIL - Large inline images
response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=[large_image_30mb, "Edit this"]  # Too large
)

# ✅ WORKS - Use Files API
uploaded = client.files.upload(file="large_image_30mb.jpg")
response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=[uploaded, "Edit this"]
)
```

### 5. Unrealistic Batch Expectations

**Problem**: Expecting instant results from batch API.

- ⏱️ Batch jobs target 24-hour turnaround
- Often faster, but not guaranteed
- Not suitable for real-time needs

**Solution**: Use batch for non-urgent, high-volume generation.

---

## Model-Specific Limitations

### Gemini 2.5 Flash Image

❌ **Cannot**:
- Generate 2K/4K images
- Use Google Search grounding
- Handle >3 reference images optimally

✅ **Can**:
- Adjust temperature
- Enable/disable thinking
- Fast, cost-effective generation

### Gemini 3 Pro Image Preview

❌ **Cannot**:
- Disable thinking mode
- Lower temperature below 1.0
- Use on budget-constrained projects

✅ **Can**:
- Generate 2K/4K images
- Use Google Search grounding
- Handle up to 14 reference images
- Advanced text rendering

---

## Troubleshooting Common Issues

### Generic Output

**Problem**: Model generates generic images not tailored to prompt.

**Solutions**:
1. Ask model to describe first:
   ```python
   "First describe what you see, then create a stylized version"
   ```
2. Be more specific in prompt
3. Use few-shot examples (2-3 example pairs)

### Hallucinations

**Problem**: Model invents incorrect details.

**Solutions**:
1. Lower temperature (Gemini 2.5 only)
2. Ask for shorter descriptions: `max_output_tokens=100`
3. Be more specific: "Only include X, Y, Z"
4. Use step-by-step instructions

### Wrong Element Focus

**Problem**: Model focuses on wrong part of image.

**Solutions**:
1. Explicitly mention focus: "Focus on the person in red shirt"
2. Use semantic masking: "Change only the [element]"
3. Provide informal bounding hints: "The object in top-right corner"
4. Multi-turn refinement

### Quality Issues

**Problem**: Output quality lower than expected.

**Solutions**:
1. Use Gemini 3 Pro for professional quality
2. Enable higher resolution (2K/4K)
3. Improve prompt specificity
4. Reduce number of reference images (if >3 for Flash, >14 for Pro)

---

## Rate Limits and Quotas

**Note**: Rate limits vary by project and API tier.

### Batch API vs Standard API

- **Batch API**: Higher rate limits, 50% cost reduction
- **Standard API**: Lower limits but real-time

### When You Hit Limits

1. Use batch API for high-volume
2. Implement exponential backoff retry logic
3. Distribute requests over time
4. Consider upgrading API tier

---

## Error Handling Best Practices

```python
from google import genai
from google.genai import types

client = genai.Client()

try:
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents="Generate an image"
    )

    # Check for successful response
    if response.candidates:
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                image = part.as_image()
                image.save("output.png")
    else:
        print("No candidates in response")

except Exception as e:
    print(f"Error: {e}")

    # Common retry strategies:
    # - Use Files API if inline data >20MB
    # - Check model availability
    # - Verify API key and quotas
    # - Implement exponential backoff
```

---

## Known Issues and Workarounds

### Issue: Batch Job Stuck in Pending

**Workaround**: Jobs can take up to 24 hours. Check back periodically.

```python
batch_job = client.batches.get(name=job_name)
print(f"State: {batch_job.state.name}")
```

### Issue: File Upload Fails

**Workaround**: Check file size (<2GB), MIME type, and project quota.

### Issue: Thought Signatures Error

**Workaround**: Use SDK chat feature instead of manual history management.

```python
# ✅ Let SDK handle it
chat = client.chats.create(model="gemini-3-pro-image-preview")
```

---

## See Also

- [configuration.md](configuration.md) - Proper configuration to avoid issues
- [models.md](models.md) - Choose the right model for your needs
- [prompt-templates.md](prompt-templates.md) - Effective prompting strategies
- [examples.md](examples.md) - Working code examples
