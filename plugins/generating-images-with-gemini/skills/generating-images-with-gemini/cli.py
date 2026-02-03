#!/usr/bin/env python3
"""
Gemini Image Generation CLI

Unified command-line interface for all Gemini image generation templates.
Run templates directly without modifying code.

Usage:
    python cli.py basic "A serene garden" --aspect-ratio 1:1 --output garden.png
    python cli.py edit photo.jpg "Add sunglasses" --output edited.png
    python cli.py batch prompts.jsonl --output-dir ./outputs/
    python cli.py multi-turn "Create a logo" --iterations 3 --output-dir ./versions/
    python cli.py search "Current weather visualization"
"""

import argparse
import sys
import base64
import io
import json
from pathlib import Path
from google import genai
from google.genai import types
from PIL import Image


def basic_command(args):
    """Generate a basic image from a text prompt."""
    client = genai.Client()

    config_kwargs = {}
    if args.aspect_ratio or args.image_size or args.image_only:
        image_config_kwargs = {}
        if args.aspect_ratio:
            image_config_kwargs['aspect_ratio'] = args.aspect_ratio
        if args.image_size:
            image_config_kwargs['image_size'] = args.image_size

        config_kwargs['image_config'] = types.ImageConfig(**image_config_kwargs)

    if args.image_only:
        config_kwargs['response_modalities'] = ['IMAGE']

    config = types.GenerateContentConfig(**config_kwargs) if config_kwargs else None

    print(f"Generating image: '{args.prompt}'")
    if args.aspect_ratio:
        print(f"  Aspect ratio: {args.aspect_ratio}")
    if args.image_size:
        print(f"  Image size: {args.image_size}")

    response = client.models.generate_content(
        model=args.model,
        contents=args.prompt,
        config=config
    )

    # Save the image
    for part in response.parts:
        if part.inline_data:
            image = part.as_image()
            image.save(args.output)
            print(f"✓ Image saved as '{args.output}'")
        elif part.text and not args.image_only:
            print(f"\nModel says: {part.text}")


def edit_command(args):
    """Edit an existing image."""
    client = genai.Client()

    # Load the input image
    if not Path(args.input_image).exists():
        print(f"Error: Input image '{args.input_image}' not found")
        sys.exit(1)

    original = Image.open(args.input_image)

    print(f"Editing image: {args.input_image}")
    print(f"  Instruction: '{args.instruction}'")

    response = client.models.generate_content(
        model=args.model,
        contents=[args.instruction, original]
    )

    # Save the edited image
    for part in response.parts:
        if part.inline_data:
            edited = part.as_image()
            edited.save(args.output)
            print(f"✓ Edited image saved as '{args.output}'")


def batch_command(args):
    """Submit a batch generation job."""
    import json
    import time

    client = genai.Client()

    # Check if prompts file exists
    if not Path(args.prompts_file).exists():
        print(f"Error: Prompts file '{args.prompts_file}' not found")
        sys.exit(1)

    print(f"Submitting batch job from: {args.prompts_file}")

    # Upload the JSONL file
    uploaded = client.files.upload(
        file=args.prompts_file,
        config=types.UploadFileConfig(mime_type='jsonl')
    )

    print(f"✓ File uploaded: {uploaded.name}")

    # Create batch job
    job = client.batches.create(
        model=args.model,
        src=uploaded.name,
        config={'display_name': args.job_name or 'cli-batch-job'}
    )

    print(f"✓ Batch job created: {job.name}")
    print(f"  State: {job.state.name}")

    if args.wait:
        print("\nWaiting for job to complete...")
        while True:
            job = client.batches.get(name=job.name)
            print(f"  Current state: {job.state.name}")

            if job.state.name in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
                break

            time.sleep(30)  # Check every 30 seconds

        if job.state.name == 'SUCCEEDED':
            print(f"\n✓ Batch job completed successfully!")

            if args.output_dir:
                output_dir = Path(args.output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)

                # Download results
                print(f"\nDownloading results to: {output_dir}/")

                result_bytes = client.files.download(file=job.dest.file_name)
                result_content = result_bytes.decode('utf-8')

                # Parse JSONL results
                results = []
                for line in result_content.strip().split('\n'):
                    if line.strip():
                        results.append(json.loads(line))

                print(f"  ✓ Downloaded {len(results)} results")

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
                                image_data = base64.b64decode(part['inlineData']['data'])
                                image = Image.open(io.BytesIO(image_data))
                                image_path = output_dir / f"{key}.png"
                                image.save(image_path)
                                saved_count += 1
                                print(f"    ✓ Saved {image_path}")

                print(f"\n  ✓ Saved {saved_count} images to {output_dir}/")
        else:
            print(f"\n✗ Batch job failed with state: {job.state.name}")
    else:
        print(f"\nJob is running. Check status with:")
        print(f"  python -c \"from google import genai; print(genai.Client().batches.get(name='{job.name}').state.name)\"")


def multi_turn_command(args):
    """Create images with iterative refinement."""
    client = genai.Client()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Configure for multi-turn
    config_kwargs = {'response_modalities': ['TEXT', 'IMAGE']}
    if args.aspect_ratio or args.image_size:
        image_config_kwargs = {}
        if args.aspect_ratio:
            image_config_kwargs['aspect_ratio'] = args.aspect_ratio
        if args.image_size:
            image_config_kwargs['image_size'] = args.image_size
        config_kwargs['image_config'] = types.ImageConfig(**image_config_kwargs)

    config = types.GenerateContentConfig(**config_kwargs)

    chat = client.chats.create(model=args.model, config=config)

    print(f"Starting multi-turn refinement:")
    print(f"  Initial prompt: '{args.initial_prompt}'")
    print(f"  Iterations: {args.iterations}")
    print(f"  Output directory: {output_dir}/")

    # Initial generation
    print(f"\nIteration 1: Initial generation")
    response = chat.send_message(args.initial_prompt)

    for part in response.parts:
        if part.inline_data:
            image = part.as_image()
            output_path = output_dir / "version_1.png"
            image.save(output_path)
            print(f"  ✓ Saved: {output_path}")
        elif part.text:
            print(f"  Model: {part.text[:100]}...")

    # Refinement iterations
    for i in range(2, args.iterations + 1):
        if args.interactive:
            refinement = input(f"\nIteration {i} - Enter refinement instruction (or 'done' to finish): ")
            if refinement.lower() == 'done':
                break
        else:
            # Auto-generate refinement prompts
            refinement_prompts = [
                "Make the colors more vibrant and adjust the composition",
                "Add more details and refine the overall style",
                "Final polish - enhance quality and fix any issues"
            ]
            refinement = refinement_prompts[min(i-2, len(refinement_prompts)-1)]

        print(f"\nIteration {i}: {refinement}")
        response = chat.send_message(refinement)

        for part in response.parts:
            if part.inline_data:
                image = part.as_image()
                output_path = output_dir / f"version_{i}.png"
                image.save(output_path)
                print(f"  ✓ Saved: {output_path}")
            elif part.text:
                print(f"  Model: {part.text[:100]}...")

    print(f"\n✓ Multi-turn refinement complete! {args.iterations} versions saved to {output_dir}/")


def search_command(args):
    """Generate images with Google Search grounding."""
    client = genai.Client()

    # Google Search only available on Gemini 3 Pro
    if not args.model.startswith('gemini-3'):
        print("Warning: Google Search grounding only available on Gemini 3 Pro models")
        print(f"  Switching from {args.model} to gemini-3-pro-image-preview")
        args.model = "gemini-3-pro-image-preview"

    config = types.GenerateContentConfig(
        tools=[{"google_search": {}}],
        response_modalities=['TEXT', 'IMAGE']
    )

    print(f"Generating with Google Search grounding:")
    print(f"  Prompt: '{args.prompt}'")

    response = client.models.generate_content(
        model=args.model,
        contents=args.prompt,
        config=config
    )

    # Save the image
    for part in response.parts:
        if part.inline_data:
            image = part.as_image()
            image.save(args.output)
            print(f"✓ Image saved as '{args.output}'")
        elif part.text:
            print(f"\nModel description:\n{part.text}")

    # Show grounding chunks if available
    if hasattr(response, 'candidates') and response.candidates:
        candidate = response.candidates[0]
        if hasattr(candidate, 'grounding_metadata'):
            print("\nGrounding sources:")
            for chunk in candidate.grounding_metadata.grounding_chunks:
                if hasattr(chunk, 'web'):
                    print(f"  - {chunk.web.title}: {chunk.web.uri}")


def main():
    parser = argparse.ArgumentParser(
        description='Gemini Image Generation CLI - Generate and edit images using Google Gemini API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic generation
  %(prog)s basic "A serene Japanese garden" --output garden.png

  # Generation with 1:1 aspect ratio (good for tiles/patterns)
  %(prog)s basic "Seamless stone texture" --aspect-ratio 1:1 --image-size 2K --output tile.png

  # Edit an existing image
  %(prog)s edit photo.jpg "Add sunglasses to the person" --output edited.png

  # Batch generation
  %(prog)s batch prompts.jsonl --wait --output-dir ./outputs/

  # Multi-turn refinement (interactive)
  %(prog)s multi-turn "Create a minimalist logo" --iterations 3 --interactive --output-dir ./versions/

  # Generate with Google Search grounding
  %(prog)s search "Infographic about current global temperature trends" --output climate.png

For more information, see the reference documentation in reference/*.md
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Basic generation command
    basic_parser = subparsers.add_parser('basic', help='Generate a single image from text prompt')
    basic_parser.add_argument('prompt', help='Text prompt describing the desired image')
    basic_parser.add_argument('--output', '-o', default='output.png', help='Output image filename (default: output.png)')
    basic_parser.add_argument('--aspect-ratio', '-ar', help='Aspect ratio (1:1, 16:9, 9:16, 4:3, etc.)')
    basic_parser.add_argument('--image-size', '-s', choices=['1K', '2K', '4K'], help='Image size (Gemini 3 Pro only)')
    basic_parser.add_argument('--image-only', action='store_true', help='Generate image only, no text response')
    basic_parser.add_argument('--model', '-m', default='gemini-2.5-flash-image', help='Model to use (default: gemini-2.5-flash-image)')
    basic_parser.set_defaults(func=basic_command)

    # Edit command
    edit_parser = subparsers.add_parser('edit', help='Edit an existing image')
    edit_parser.add_argument('input_image', help='Path to image to edit')
    edit_parser.add_argument('instruction', help='Editing instruction (e.g., "Add sunglasses")')
    edit_parser.add_argument('--output', '-o', default='edited.png', help='Output image filename (default: edited.png)')
    edit_parser.add_argument('--model', '-m', default='gemini-2.5-flash-image', help='Model to use')
    edit_parser.set_defaults(func=edit_command)

    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Submit batch generation job')
    batch_parser.add_argument('prompts_file', help='Path to JSONL file with prompts')
    batch_parser.add_argument('--output-dir', '-d', help='Directory to save results')
    batch_parser.add_argument('--job-name', '-n', help='Display name for the batch job')
    batch_parser.add_argument('--wait', '-w', action='store_true', help='Wait for job to complete (may take up to 24hrs)')
    batch_parser.add_argument('--model', '-m', default='gemini-2.5-flash-image', help='Model to use')
    batch_parser.set_defaults(func=batch_command)

    # Multi-turn command
    multi_parser = subparsers.add_parser('multi-turn', help='Iterative image refinement through multiple turns')
    multi_parser.add_argument('initial_prompt', help='Initial prompt for first image')
    multi_parser.add_argument('--iterations', '-i', type=int, default=3, help='Number of refinement iterations (default: 3)')
    multi_parser.add_argument('--output-dir', '-d', default='./versions/', help='Directory to save versions (default: ./versions/)')
    multi_parser.add_argument('--aspect-ratio', '-ar', help='Aspect ratio')
    multi_parser.add_argument('--image-size', '-s', choices=['1K', '2K', '4K'], help='Image size (Gemini 3 Pro only)')
    multi_parser.add_argument('--interactive', action='store_true', help='Prompt for refinement instructions interactively')
    multi_parser.add_argument('--model', '-m', default='gemini-3-pro-image-preview', help='Model to use (default: gemini-3-pro-image-preview)')
    multi_parser.set_defaults(func=multi_turn_command)

    # Search command
    search_parser = subparsers.add_parser('search', help='Generate with Google Search grounding (Gemini 3 Pro only)')
    search_parser.add_argument('prompt', help='Text prompt for generation with current data')
    search_parser.add_argument('--output', '-o', default='search_output.png', help='Output image filename (default: search_output.png)')
    search_parser.add_argument('--model', '-m', default='gemini-3-pro-image-preview', help='Model to use')
    search_parser.set_defaults(func=search_command)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute the command
    try:
        args.func(args)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
