"""
Batch Image Generation with Gemini

This template demonstrates batch generation for high-volume image creation at 50% cost savings.
Perfect for generating many images where you can wait up to 24 hours for results.

Batch Generation Workflow Checklist
====================================
Copy this checklist to track progress:

- [ ] Step 1: Prepare prompts (JSONL format with request keys)
- [ ] Step 2: Submit batch job (upload JSONL, create batch)
- [ ] Step 3: Poll for completion (target: up to 24hrs, often faster)
- [ ] Step 4: Download results (fetch output JSONL)
- [ ] Step 5: Verify output quality (check all images generated correctly)

Tips:
- Batch API offers 50% cost reduction vs standard API
- Jobs typically complete faster than 24hr target
- Use for non-urgent, high-volume generation
- Monitor with client.batches.get(name=job_name)
"""

import json
import time
from google import genai
from google.genai import types

# Initialize client
client = genai.Client()


def create_batch_requests_jsonl(prompts: list[str], output_file: str):
    """Create a JSONL file with batch requests."""

    with open(output_file, "w") as f:
        for i, prompt in enumerate(prompts):
            request = {
                "key": f"request-{i}",
                "request": {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generation_config": {
                        "responseModalities": ["TEXT", "IMAGE"]
                    }
                }
            }
            f.write(json.dumps(request) + "\n")

    print(f"✓ Created {output_file} with {len(prompts)} requests")


def submit_batch_job(jsonl_file: str, job_name: str):
    """Upload JSONL file and submit batch job."""

    # Upload the JSONL file
    print(f"Uploading {jsonl_file}...")
    uploaded_file = client.files.upload(
        file=jsonl_file,
        config=types.UploadFileConfig(
            display_name=job_name,
            mime_type='jsonl'
        )
    )
    print(f"✓ File uploaded: {uploaded_file.name}")

    # Create batch job
    print(f"Creating batch job '{job_name}'...")
    batch_job = client.batches.create(
        model="gemini-2.5-flash-image",
        src=uploaded_file.name,
        config={'display_name': job_name}
    )

    print(f"✓ Batch job created: {batch_job.name}")
    print(f"  State: {batch_job.state.name}")
    print(f"  Created: {batch_job.create_time}")

    return batch_job


def monitor_batch_job(job_name: str, poll_interval: int = 10):
    """Monitor batch job until completion."""

    completed_states = {
        'JOB_STATE_SUCCEEDED',
        'JOB_STATE_FAILED',
        'JOB_STATE_CANCELLED',
        'JOB_STATE_EXPIRED'
    }

    print(f"\nMonitoring job: {job_name}")
    print("(Ctrl+C to stop monitoring - job will continue in background)\n")

    try:
        while True:
            batch_job = client.batches.get(name=job_name)

            state = batch_job.state.name
            print(f"State: {state}", end="")

            if hasattr(batch_job, 'request_counts'):
                counts = batch_job.request_counts
                print(f" | Succeeded: {counts.succeeded} | Failed: {counts.failed} | Total: {counts.total}")
            else:
                print()

            if state in completed_states:
                print(f"\n✓ Job {state}")
                return batch_job

            time.sleep(poll_interval)

    except KeyboardInterrupt:
        print(f"\n⚠ Stopped monitoring. Job continues in background.")
        print(f"Check status with: client.batches.get(name='{job_name}')")
        return None


def download_batch_results(job_name: str, output_dir: str = "."):
    """Download and process batch job results."""

    batch_job = client.batches.get(name=job_name)

    if batch_job.state.name != 'JOB_STATE_SUCCEEDED':
        print(f"⚠ Job not succeeded yet. Current state: {batch_job.state.name}")
        return

    print(f"\nDownloading results from {batch_job.dest.file_name}...")
    result_bytes = client.files.download(file=batch_job.dest.file_name)
    result_content = result_bytes.decode('utf-8')

    # Parse JSONL results
    results = []
    for line in result_content.strip().split('\n'):
        results.append(json.loads(line))

    print(f"✓ Downloaded {len(results)} results")

    # Save images from results
    saved_count = 0
    for result in results:
        key = result.get('key', 'unknown')
        response = result.get('response', {})
        candidates = response.get('candidates', [])

        if candidates:
            content = candidates[0].get('content', {})
            parts = content.get('parts', [])

            for part in parts:
                if 'inlineData' in part:
                    # Extract and save image
                    import base64
                    from PIL import Image
                    import io

                    image_data = base64.b64decode(part['inlineData']['data'])
                    image = Image.open(io.BytesIO(image_data))
                    image_path = f"{output_dir}/{key}.png"
                    image.save(image_path)
                    saved_count += 1
                    print(f"  ✓ Saved {image_path}")

    print(f"\n✓ Saved {saved_count} images to {output_dir}/")


def simple_batch_workflow():
    """Complete batch workflow: create, submit, monitor, download."""

    # Step 1: Define prompts
    prompts = [
        "A red apple on a white background, studio lighting",
        "A blue butterfly on a flower, macro photography",
        "A yellow sunflower in a field, golden hour",
        "A purple galaxy swirl, space photography",
        "A green forest path in autumn, cinematic",
    ]

    # Step 2: Create JSONL file
    jsonl_file = "batch_requests.jsonl"
    create_batch_requests_jsonl(prompts, jsonl_file)

    # Step 3: Submit batch job
    job = submit_batch_job(jsonl_file, "color-themed-images")

    # Step 4: Monitor (or skip and check back later)
    print("\nNote: Batch jobs can take up to 24 hours (often much faster)")
    print("You can:")
    print("  1. Monitor now (will poll every 10 seconds)")
    print("  2. Skip monitoring and check back later")

    choice = input("\nMonitor now? (y/n): ").strip().lower()

    if choice == 'y':
        completed_job = monitor_batch_job(job.name)
        if completed_job:
            # Step 5: Download results
            download_batch_results(job.name)
    else:
        print(f"\n✓ Job submitted. Check later with:")
        print(f"  job = client.batches.get(name='{job.name}')")
        print(f"  print(job.state.name)")


def advanced_batch_with_configs():
    """Batch generation with different configurations per request."""

    requests = []

    # Generate images with different aspect ratios for testing/comparison
    # 1:1 - Tile-based imagery, social media, product photos
    # 16:9 - Presentations, YouTube thumbnails, desktop wallpapers
    # 9:16 - Mobile screens, Instagram/TikTok stories
    # 4:3 - Traditional photos, slideshows
    aspect_ratios = ["1:1", "16:9", "9:16", "4:3"]
    for i, ratio in enumerate(aspect_ratios):
        request = {
            "key": f"aspect-{ratio.replace(':', '-')}",
            "request": {
                "contents": [{"parts": [{"text": f"A sunset landscape in {ratio} format"}]}],
                "generation_config": {
                    "responseModalities": ["IMAGE"],
                    "imageConfig": {"aspectRatio": ratio}
                }
            }
        }
        requests.append(request)

    # Save to JSONL
    jsonl_file = "batch_configs.jsonl"
    with open(jsonl_file, "w") as f:
        for req in requests:
            f.write(json.dumps(req) + "\n")

    print(f"✓ Created {jsonl_file} with {len(requests)} requests")

    # Submit
    uploaded = client.files.upload(
        file=jsonl_file,
        config=types.UploadFileConfig(mime_type='jsonl')
    )

    job = client.batches.create(
        model="gemini-2.5-flash-image",
        src=uploaded.name,
        config={'display_name': "aspect-ratio-test"}
    )

    print(f"✓ Batch job created: {job.name}")


def list_all_batch_jobs():
    """List all batch jobs for monitoring."""

    print("All batch jobs:\n")
    for job in client.batches.list():
        print(f"Name: {job.name}")
        print(f"  Display Name: {job.display_name if hasattr(job, 'display_name') else 'N/A'}")
        print(f"  State: {job.state.name}")
        print(f"  Created: {job.create_time}")
        if hasattr(job, 'request_counts'):
            counts = job.request_counts
            print(f"  Progress: {counts.succeeded}/{counts.total} succeeded")
        print()


if __name__ == "__main__":
    print("Gemini Batch Image Generation\n")
    print("="*60 + "\n")

    # Choose example
    print("Examples:")
    print("1. Simple batch workflow (5 color-themed images)")
    print("2. Advanced batch with different configurations")
    print("3. List all batch jobs")

    choice = input("\nSelect example (1-3): ").strip()

    if choice == "1":
        simple_batch_workflow()
    elif choice == "2":
        advanced_batch_with_configs()
    elif choice == "3":
        list_all_batch_jobs()
    else:
        print("Invalid choice")

    print("\n✓ Batch generation example completed!")
