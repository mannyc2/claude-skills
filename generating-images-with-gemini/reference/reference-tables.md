# Reference Tables & Decision Trees

Quick reference tables and decision trees for Gemini image generation.

## Table of Contents

- Model Selection Decision Tree
- Resolution & Token Tables (Gemini 2.5 Flash, Gemini 3 Pro)
- Pricing Comparison Table
- Model Comparison Matrix
- Aspect Ratio Use Cases
- Troubleshooting Decision Trees
- Workflow Selection Matrix
- Configuration Quick Reference
- Default Values Reference
- Language Support Table
- MIME Type Reference
- Error Code Quick Reference
- Quick Template Selector

---

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

---

## Resolution & Token Tables

### Gemini 2.5 Flash Image - Complete Table

| Aspect Ratio | Resolution | Tokens |
|--------------|------------|--------|
| 1:1          | 1024x1024  | 1290   |
| 2:3          | 832x1248   | 1290   |
| 3:2          | 1248x832   | 1290   |
| 3:4          | 864x1184   | 1290   |
| 4:3          | 1184x864   | 1290   |
| 4:5          | 896x1152   | 1290   |
| 5:4          | 1152x896   | 1290   |
| 9:16         | 768x1344   | 1290   |
| 16:9         | 1344x768   | 1290   |
| 21:9         | 1536x672   | 1290   |

**Note**: All aspect ratios consume flat 1290 tokens for Gemini 2.5 Flash Image. See [ai.google.dev/pricing](https://ai.google.dev/pricing) for current costs.

### Gemini 3 Pro Image Preview - Complete Table

| Aspect Ratio | 1K Resolution | 1K Tokens | 2K Resolution | 2K Tokens | 4K Resolution | 4K Tokens |
|--------------|---------------|-----------|---------------|-----------|---------------|-----------|
| **1:1**      | 1024x1024     | 1120      | 2048x2048     | 1120      | 4096x4096     | 2000      |
| **2:3**      | 848x1264      | 1120      | 1696x2528     | 1120      | 3392x5056     | 2000      |
| **3:2**      | 1264x848      | 1120      | 2528x1696     | 1120      | 5056x3392     | 2000      |
| **3:4**      | 896x1200      | 1120      | 1792x2400     | 1120      | 3584x4800     | 2000      |
| **4:3**      | 1200x896      | 1120      | 2400x1792     | 1120      | 4800x3584     | 2000      |
| **4:5**      | 928x1152      | 1120      | 1856x2304     | 1120      | 3712x4608     | 2000      |
| **5:4**      | 1152x928      | 1120      | 2304x1856     | 1120      | 4608x3712     | 2000      |
| **9:16**     | 768x1376      | 1120      | 1536x2752     | 1120      | 3072x5504     | 2000      |
| **16:9**     | 1376x768      | 1120      | 2752x1536     | 1120      | 5504x3072     | 2000      |
| **21:9**     | 1584x672      | 1120      | 3168x1344     | 1120      | 6336x2688     | 2000      |

**Notes**:
- 1K and 2K have same token cost (1120)
- 4K costs more (2000 tokens)
- Choose resolution based on quality needs vs cost

---

## Pricing Comparison

**For current pricing**, see Google's official pricing page: [ai.google.dev/pricing](https://ai.google.dev/pricing)

**Key pricing notes:**
- **Gemini 2.5 Flash Image**: Most cost-effective option, fixed ~1024px resolution
- **Gemini 3 Pro Image Preview**: Higher cost but supports 1K/2K/4K resolutions
- **Batch API**: Offers 50% cost reduction for non-urgent, high-volume generation
- **Resolution impact**: 4K images cost more than 1K/2K (which have equal pricing)

---

## Model Comparison Matrix

| Feature | Gemini 2.5 Flash Image | Gemini 3 Pro Image Preview |
|---------|------------------------|----------------------------|
| **Model ID** | `gemini-2.5-flash-image` | `gemini-3-pro-image-preview` |
| **Resolution** | Fixed ~1024px | 1K, 2K, 4K configurable |
| **Reference Images** | Best with ≤3 | Up to 14 (6 objects + 5 humans) |
| **Google Search** | ❌ No | ✅ Yes |
| **Thinking** | Optional (off by default) | Always on (cannot disable) |
| **Temperature** | Adjustable | Must stay at 1.0 |
| **Relative Cost** | Lower | Higher |
| **Speed** | Fast | Slower (more computation) |
| **Text Rendering** | Standard | Advanced (infographics, menus) |
| **Best for** | Volume, speed, cost | Quality, complexity, professional |

---

## Aspect Ratio Use Cases

| Aspect Ratio | Description | Best Use Cases |
|--------------|-------------|----------------|
| **1:1** | Square | Tile-based imagery (patterns, textures, spritesheets), social media posts, avatars, profile pictures, logos |
| **16:9** | Wide landscape | Presentations, YouTube thumbnails, desktop wallpapers, TV displays |
| **9:16** | Tall portrait | Mobile screens, Instagram/TikTok stories, phone wallpapers |
| **4:3** | Standard landscape | Traditional photos, slideshows, older displays |
| **3:4** | Standard portrait | Portraits, book covers, magazine layouts |
| **4:5** | Instagram portrait | Instagram feed posts |
| **5:4** | Slightly wide | Photo prints, framed artwork |
| **2:3** | Classic portrait | Standard photo prints (4x6) |
| **3:2** | Classic landscape | DSLR photos, prints |
| **21:9** | Ultra-wide | Cinematic images, panoramas, ultrawide monitors |

---

## Troubleshooting Decision Trees

### Generic Output → How to Fix

```
Problem: Output is too generic, not tailored to input
│
├─ Solution 1: Ask model to describe image/scene first
│  └─ "First describe what you see in detail, then [task]"
│
├─ Solution 2: Be more specific about which elements to focus on
│  └─ "Focus on the wooden objects in the foreground"
│
├─ Solution 3: Use few-shot examples
│  └─ Provide 2-3 example input-output pairs
│
└─ Solution 4: Add context and intent
   └─ Explain the purpose: "for a product catalog"
```

### Hallucinations → Remediation Steps

```
Problem: Model generating incorrect or made-up details
│
├─ Solution 1: Lower temperature (2.5 Flash only, NOT 3 Pro)
│  └─ temperature=0.7 or lower
│
├─ Solution 2: Reduce output length
│  └─ max_output_tokens=100 (less opportunity to extrapolate)
│
├─ Solution 3: Be more specific and constrained
│  └─ "Only include X, Y, Z. No other elements."
│
└─ Solution 4: Use step-by-step instructions
   └─ Break complex task into smaller, clear steps
```

### Wrong Element Focus → Correction Strategies

```
Problem: Model focusing on wrong part of image/prompt
│
├─ Solution 1: Explicitly state what to focus on
│  └─ "Focus on the person wearing the red shirt"
│
├─ Solution 2: Use semantic masking
│  └─ "Change only the [specific element], keep everything else"
│
├─ Solution 3: Provide informal spatial hints
│  └─ "The object in the top-right corner of the image"
│
└─ Solution 4: Multi-turn refinement
   └─ Generate, then "adjust the focus to [element]"
```

### Quality Issues → Resolution Steps

```
Problem: Output quality lower than expected
│
├─ Solution 1: Use higher-quality model
│  └─ Switch to Gemini 3 Pro Image Preview
│
├─ Solution 2: Increase resolution
│  └─ Use 2K or 4K (Gemini 3 Pro only)
│
├─ Solution 3: Improve prompt specificity
│  └─ Add detail about style, lighting, composition
│
├─ Solution 4: Reduce reference images
│  └─ Use ≤3 for Flash, ≤14 for Pro
│
└─ Solution 5: Enable thinking (for complex tasks)
   └─ thinking_budget=1024 (Flash) or always on (Pro)
```

---

## Workflow Selection Matrix

| Task Type | Recommended Workflow | Model | Pattern |
|-----------|---------------------|-------|---------|
| **Simple one-shot image** | Single-shot generation | 2.5 Flash | Basic text-to-image |
| **Professional asset** | Iterative refinement | 3 Pro | Multi-turn chat |
| **Bulk generation (10+)** | Batch production | 2.5 Flash | Batch API |
| **Image editing** | Image-to-image | 2.5 Flash | Image editing pattern |
| **Style transfer** | Image-to-image | 2.5 Flash | Style transfer pattern |
| **Multi-image composition** | Multi-image | 2.5 Flash/3 Pro | Multi-image pattern |
| **Real-time data** | Grounded generation | 3 Pro | Google Search pattern |
| **High-res output** | Professional generation | 3 Pro | 2K/4K configuration |
| **Character consistency** | Multi-view generation | 3 Pro | Character consistency pattern |
| **A/B testing** | Variation generation | 2.5 Flash | Batch or multi-turn |

---

## Configuration Quick Reference

### Speed Priority

```python
config = types.GenerateContentConfig(
    response_modalities=['IMAGE'],  # No text
    thinking_config=types.ThinkingConfig(thinking_budget=0)  # Flash only
)
```

### Quality Priority

```python
config = types.GenerateContentConfig(
    image_config=types.ImageConfig(
        aspect_ratio="16:9",
        image_size="4K"
    ),
    thinking_config=types.ThinkingConfig(include_thoughts=True)
)
```

### Cost Priority

```python
# Use Gemini 2.5 Flash with batch API
config = types.GenerateContentConfig(
    response_modalities=['IMAGE']
)
# + Batch API for 50% discount
```

### Professional Asset

```python
config = types.GenerateContentConfig(
    response_modalities=['TEXT', 'IMAGE'],
    image_config=types.ImageConfig(
        aspect_ratio="1:1",
        image_size="2K"
    ),
    system_instruction="You are a professional graphic designer."
)
```

---

## Default Values Reference

| Parameter | Gemini 2.5 Flash Image | Gemini 3 Pro Image Preview |
|-----------|------------------------|----------------------------|
| `response_modalities` | `['TEXT', 'IMAGE']` | `['TEXT', 'IMAGE']` |
| `aspect_ratio` | `"1:1"` | `"1:1"` |
| `image_size` | N/A (fixed ~1024px) | `"1K"` |
| `thinking_budget` | `0` (disabled) | N/A (always enabled) |
| `temperature` | `0.9` | `1.0` ⚠️ DON'T CHANGE |
| `top_k` | `40` | `40` |
| `top_p` | `0.95` | `0.95` |
| `max_output_tokens` | `8192` | `8192` |

---

## Language Support Table

| Language | Code | Support Level |
|----------|------|---------------|
| English | EN | ✅ Full |
| Arabic (Egypt) | ar-EG | ✅ Full |
| German | de-DE | ✅ Full |
| Spanish (Mexico) | es-MX | ✅ Full |
| French | fr-FR | ✅ Full |
| Hindi | hi-IN | ✅ Full |
| Indonesian | id-ID | ✅ Full |
| Italian | it-IT | ✅ Full |
| Japanese | ja-JP | ✅ Full |
| Korean | ko-KR | ✅ Full |
| Portuguese (Brazil) | pt-BR | ✅ Full |
| Russian | ru-RU | ✅ Full |
| Ukrainian | ua-UA | ✅ Full |
| Vietnamese | vi-VN | ✅ Full |
| Chinese | zh-CN | ✅ Full |
| Other languages | - | ⚠️ Reduced quality |

---

## MIME Type Reference

| MIME Type | Extension | Use Case |
|-----------|-----------|----------|
| `image/png` | .png | Graphics, transparency, logos |
| `image/jpeg` | .jpg, .jpeg | Photos, general images |
| `image/webp` | .webp | Modern web format |
| `image/heic` | .heic | Apple photos |
| `image/heif` | .heif | Apple photos |

---

## Error Code Quick Reference

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| **File too large** | >2GB per file or >20MB inline | Use Files API |
| **Quota exceeded** | >20GB total storage | Delete old files |
| **Invalid parameter** | Lowercase 'k' in image_size | Use uppercase: "2K" |
| **No candidates** | Generation failed | Check prompt, retry with backoff |
| **Temperature error** | Temperature <1.0 on Gemini 3 | Set temperature=1.0 |
| **File not found** | File expired (>48h) | Re-upload file |
| **Too many images** | >3 for Flash, >14 for Pro | Reduce reference images |

---

## Quick Template Selector

**I want to create...**

| Output Type | Recommended Template | Model |
|-------------|---------------------|--------|
| **Product photo** | Product mockup template | 2.5 Flash or 3 Pro |
| **Logo/branding** | Accurate text template | 3 Pro |
| **Social media graphic** | Minimalist design template | 2.5 Flash |
| **Realistic photo** | Photorealistic template | 2.5 Flash or 3 Pro |
| **Illustration/sticker** | Stylized illustration template | 2.5 Flash |
| **Comic/storyboard** | Sequential art template | 3 Pro |
| **Infographic** | Text + grounding template | 3 Pro |
| **Edit existing image** | Image editing template | 2.5 Flash |
| **Multiple variations** | Batch generation | 2.5 Flash |
| **High-res asset** | 2K/4K template | 3 Pro |

---

## See Also

- [models.md](models.md) - Detailed model capabilities
- [configuration.md](configuration.md) - Configuration options explained
- [limitations.md](limitations.md) - Known limitations
- [examples.md](examples.md) - Complete runnable examples
