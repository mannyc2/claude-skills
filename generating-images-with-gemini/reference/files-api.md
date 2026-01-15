# Files API Reference

Complete guide to uploading, managing, and using files with Gemini image generation.

## Table of Contents

- When to Use Files API
- Files API Limits
- Upload Patterns (Basic, Metadata, Multiple Files)
- Using Uploaded Files
- File Metadata
- Listing Files
- File Deletion
- File Retention Policies
- Supported MIME Types
- Advanced Patterns
- Batch API with Files
- Common Issues and Solutions
- Best Practices

---

## When to Use Files API

Use the Files API instead of inline data when:

✅ **File size >20MB** - Inline limit including all request content
✅ **Reusing files** - Upload once, use many times (more efficient)
✅ **Large image assets** - That you'll reference multiple times

**Benefits**:
- Avoid repeated uploads
- Handle files >20MB
- Better performance for large files
- Explicit lifecycle management

---

## Files API Limits

| Limit | Value |
|-------|-------|
| **Total storage per project** | 20GB |
| **Max file size** | 2GB |
| **Retention period** | 48 hours (auto-deletion) |
| **Can download** | ❌ No (input only) |

⚠️ **IMPORTANT**: Files are automatically deleted after 48 hours and cannot be renewed.

---

## Upload Patterns

### Basic Upload

```python
from google import genai
from google.genai import types

client = genai.Client()

# Simple upload (auto-detects MIME type)
my_file = client.files.upload(file='photo.jpg')

print(f"Uploaded: {my_file.name}")
print(f"URI: {my_file.uri}")
```

### Upload with Metadata

```python
my_file = client.files.upload(
    file='reference.jpg',
    config=types.UploadFileConfig(
        display_name='Product Reference Photo',
        mime_type='image/jpeg'
    )
)

print(f"Name: {my_file.name}")
print(f"Display Name: {my_file.display_name}")
```

### Multiple File Upload

```python
files = []
for path in ["img1.jpg", "img2.png", "img3.jpg"]:
    f = client.files.upload(file=path)
    files.append(f)
    print(f"Uploaded: {path}")

# Use all in one request
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=["Combine these images", *files]
)
```

---

## Using Uploaded Files

### Single Use

```python
# Upload
uploaded = client.files.upload(file='reference.jpg')

# Use immediately
response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=[uploaded, "Edit this image"]
)

# Save result
response.parts[0].as_image().save("edited.png")

# Clean up
client.files.delete(name=uploaded.name)
```

### Reuse Pattern

```python
# Upload once
uploaded = client.files.upload(file='reference.jpg')

# Use multiple times
styles = ["vintage", "modern", "abstract", "watercolor"]

for style in styles:
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[uploaded, f"Apply {style} style to this image"]
    )
    response.parts[0].as_image().save(f"output_{style}.png")
    print(f"✓ Created {style} version")

# Cleanup after all uses
client.files.delete(name=uploaded.name)
print("✓ Cleaned up uploaded file")
```

---

## File Metadata

### Retrieve Metadata

```python
# Upload file
my_file = client.files.upload(file='sample.jpg')

# Get metadata
file_info = client.files.get(name=my_file.name)

print(f"Name: {file_info.name}")
print(f"Display Name: {file_info.display_name}")
print(f"Size: {file_info.size_bytes} bytes")
print(f"MIME Type: {file_info.mime_type}")
print(f"State: {file_info.state}")
print(f"URI: {file_info.uri}")
```

### Metadata Fields

| Field | Description |
|-------|-------------|
| `name` | Unique identifier (use for operations) |
| `display_name` | Human-readable name |
| `size_bytes` | File size in bytes |
| `mime_type` | MIME type (e.g., image/jpeg) |
| `state` | Processing state |
| `uri` | Resource URI |
| `create_time` | Upload timestamp |
| `update_time` | Last update timestamp |

---

## Listing Files

### List All Files

```python
print("Uploaded files:")
for f in client.files.list():
    print(f"  - {f.name}")
    print(f"    Display: {f.display_name if hasattr(f, 'display_name') else 'N/A'}")
    print(f"    Size: {f.size_bytes} bytes")
    print()
```

### With Pagination

```python
# List is automatically paginated by SDK
all_files = list(client.files.list())
print(f"Total files: {len(all_files)}")

for f in all_files:
    print(f"{f.name} - {f.size_bytes} bytes")
```

### Filter by Pattern

```python
# Get all files and filter manually
all_files = list(client.files.list())

# Filter for JPEGs
jpegs = [f for f in all_files if f.mime_type == 'image/jpeg']
print(f"JPEG files: {len(jpegs)}")

# Filter by display name pattern
product_photos = [f for f in all_files if 'product' in f.display_name.lower()]
print(f"Product photos: {len(product_photos)}")
```

---

## File Deletion

### Manual Deletion

```python
# Upload
my_file = client.files.upload(file='temp.jpg')

# Use it
response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=[my_file, "Process this"]
)

# Clean up immediately (don't wait 48 hours)
client.files.delete(name=my_file.name)
print("✓ File deleted")
```

### Batch Deletion

```python
# Delete all uploaded files
all_files = list(client.files.list())

for f in all_files:
    client.files.delete(name=f.name)
    print(f"✓ Deleted {f.name}")

print(f"✓ Deleted {len(all_files)} files")
```

### Delete Old Files

```python
from datetime import datetime, timedelta

# Get all files
all_files = list(client.files.list())

# Delete files older than 1 hour
one_hour_ago = datetime.now() - timedelta(hours=1)

for f in all_files:
    if f.create_time < one_hour_ago:
        client.files.delete(name=f.name)
        print(f"✓ Deleted old file: {f.name}")
```

---

## File Retention Policies

### Automatic Deletion

- **48-hour retention**: All uploaded files automatically deleted after 48 hours
- **No extension**: Cannot extend the 48-hour period
- **Re-upload if needed**: Must re-upload files if needed after expiration

### Manual Deletion

```python
# Delete anytime before 48-hour expiration
client.files.delete(name=my_file.name)
```

### Retention Best Practices

```python
# Pattern 1: Upload → Use → Delete immediately
uploaded = client.files.upload(file='temp.jpg')
response = client.models.generate_content(...)
client.files.delete(name=uploaded.name)

# Pattern 2: Upload → Use multiple times → Delete when done
uploaded = client.files.upload(file='reference.jpg')
for prompt in prompts:
    response = client.models.generate_content(...)
client.files.delete(name=uploaded.name)

# Pattern 3: Let auto-deletion handle it (if not time-sensitive)
uploaded = client.files.upload(file='reference.jpg')
response = client.models.generate_content(...)
# Cleanup happens automatically after 48 hours
```

---

## Supported MIME Types

### Image Types

| MIME Type | Extension | Notes |
|-----------|-----------|-------|
| `image/png` | .png | Recommended for graphics |
| `image/jpeg` | .jpg, .jpeg | Recommended for photos |
| `image/webp` | .webp | Modern format |
| `image/heic` | .heic | Apple format |
| `image/heif` | .heif | Apple format |

### Auto-Detection vs Explicit

```python
# Auto-detect (recommended)
f = client.files.upload(file='photo.jpg')
# SDK automatically detects image/jpeg

# Explicit MIME type
f = client.files.upload(
    file='photo.jpg',
    config=types.UploadFileConfig(mime_type='image/jpeg')
)
```

---

## Advanced Patterns

### Upload with Error Handling

```python
def upload_with_retry(file_path, max_retries=3):
    """Upload file with retry logic."""

    for attempt in range(max_retries):
        try:
            uploaded = client.files.upload(file=file_path)
            print(f"✓ Uploaded: {uploaded.name}")
            return uploaded

        except Exception as e:
            print(f"Upload failed (attempt {attempt + 1}): {e}")

            if attempt < max_retries - 1:
                import time
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise

    return None

# Usage
file = upload_with_retry('large_image.jpg')
```

### Track File Usage

```python
class FileTracker:
    """Track uploaded files for cleanup."""

    def __init__(self, client):
        self.client = client
        self.uploaded_files = []

    def upload(self, file_path, **kwargs):
        """Upload and track file."""
        f = self.client.files.upload(file=file_path, **kwargs)
        self.uploaded_files.append(f)
        return f

    def cleanup_all(self):
        """Delete all tracked files."""
        for f in self.uploaded_files:
            self.client.files.delete(name=f.name)
            print(f"✓ Deleted {f.name}")
        self.uploaded_files = []

# Usage
tracker = FileTracker(client)

# Upload multiple files
file1 = tracker.upload('img1.jpg')
file2 = tracker.upload('img2.jpg')

# Use them...

# Clean up all at once
tracker.cleanup_all()
```

### File Size Validation

```python
import os

def upload_if_valid(file_path, max_size_mb=2000):
    """Upload file if within size limit."""

    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

    if file_size_mb > max_size_mb:
        print(f"❌ File too large: {file_size_mb:.2f}MB (max: {max_size_mb}MB)")
        return None

    print(f"✓ File size OK: {file_size_mb:.2f}MB")
    return client.files.upload(file=file_path)

# Usage
uploaded = upload_if_valid('large_image.jpg')
if uploaded:
    # Use file...
    pass
```

---

## Batch API with Files

### Upload JSONL for Batch

```python
import json

# Create JSONL file
requests = [
    {
        "key": f"request-{i}",
        "request": {
            "contents": [{"parts": [{"text": prompt}]}],
            "generation_config": {"responseModalities": ["IMAGE"]}
        }
    }
    for i, prompt in enumerate(["prompt1", "prompt2", "prompt3"])
]

with open("batch.jsonl", "w") as f:
    for req in requests:
        f.write(json.dumps(req) + "\n")

# Upload JSONL
uploaded_jsonl = client.files.upload(
    file="batch.jsonl",
    config=types.UploadFileConfig(
        display_name='my-batch-requests',
        mime_type='jsonl'
    )
)

# Create batch job
job = client.batches.create(
    model="gemini-2.5-flash-image",
    src=uploaded_jsonl.name,
    config={'display_name': "my-batch-job"}
)

print(f"✓ Batch job created: {job.name}")
```

---

## Common Issues and Solutions

### Issue: Upload Fails

**Causes**:
- File too large (>2GB)
- Invalid MIME type
- Project quota exceeded
- Network issues

**Solutions**:
```python
try:
    uploaded = client.files.upload(file='image.jpg')
except Exception as e:
    print(f"Upload failed: {e}")

    # Check file size
    import os
    size_mb = os.path.getsize('image.jpg') / (1024 * 1024)
    print(f"File size: {size_mb:.2f}MB")

    # Check quota
    all_files = list(client.files.list())
    total_size = sum(f.size_bytes for f in all_files)
    print(f"Current usage: {total_size / (1024**3):.2f}GB / 20GB")
```

### Issue: File Not Found

**Cause**: File expired (>48 hours) or was deleted

**Solution**:
```python
try:
    file_info = client.files.get(name=file_name)
except Exception as e:
    print(f"File not found: {e}")
    print("File may have expired or been deleted")
    # Re-upload if needed
    uploaded = client.files.upload(file='image.jpg')
```

### Issue: Quota Exceeded

**Cause**: >20GB total storage used

**Solution**:
```python
# List all files
all_files = list(client.files.list())

# Calculate usage
total_bytes = sum(f.size_bytes for f in all_files)
total_gb = total_bytes / (1024**3)

print(f"Storage used: {total_gb:.2f}GB / 20GB")

if total_gb > 19:  # Near limit
    # Delete oldest files
    sorted_files = sorted(all_files, key=lambda f: f.create_time)
    for f in sorted_files[:10]:  # Delete 10 oldest
        client.files.delete(name=f.name)
        print(f"✓ Deleted {f.name}")
```

---

## Best Practices

### 1. Clean Up After Use

```python
# ✅ GOOD - Explicit cleanup
uploaded = client.files.upload(file='temp.jpg')
try:
    response = client.models.generate_content(...)
finally:
    client.files.delete(name=uploaded.name)

# ⚠️ OKAY - Relies on auto-deletion
uploaded = client.files.upload(file='temp.jpg')
response = client.models.generate_content(...)
# Cleaned up after 48 hours
```

### 2. Use Display Names

```python
# ✅ GOOD - Descriptive names
client.files.upload(
    file='photo.jpg',
    config=types.UploadFileConfig(
        display_name='product-photo-blue-mug'
    )
)

# ❌ BAD - No display name
client.files.upload(file='photo.jpg')
```

### 3. Validate Before Upload

```python
import os

def safe_upload(file_path):
    """Validate and upload file."""

    # Check exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} not found")

    # Check size
    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if size_mb > 2000:
        raise ValueError(f"File too large: {size_mb:.2f}MB")

    # Upload
    return client.files.upload(file=file_path)
```

### 4. Track File Lifecycle

```python
# Keep track of what you upload
uploaded_files = {}

# Upload and track
for path in ["img1.jpg", "img2.jpg"]:
    f = client.files.upload(file=path)
    uploaded_files[path] = f.name

# Use them...

# Clean up all
for name in uploaded_files.values():
    client.files.delete(name=name)
```

---

## See Also

- [api-patterns.md](api-patterns.md) - General API usage patterns
- [limitations.md](limitations.md) - File size and retention limits
- [examples.md](examples.md) - Complete code examples
