"""
Basic Text-to-Image Generation with Gemini

This template demonstrates simple text-to-image generation using Gemini 2.5 Flash Image.
"""

from google import genai
from google.genai import types

# Initialize client
client = genai.Client()

# Simple generation
def generate_basic_image():
    """Generate a single image from a text prompt."""

    prompt = "A serene Japanese garden with koi pond at sunset, cherry blossoms in bloom"

    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=prompt
    )

    # Save the generated image
    for part in response.parts:
        if part.inline_data:
            image = part.as_image()
            image.save("generated_image.png")
            print("✓ Image saved as 'generated_image.png'")
        elif part.text:
            print(f"Model says: {part.text}")


# Generation with configuration
def generate_with_config():
    """Generate an image with specific configuration options."""

    prompt = """
    A high-resolution product photograph of a minimalist ceramic coffee mug in matte black,
    presented on a polished concrete surface. Studio lighting with soft shadows. Square format.
    """

    config = types.GenerateContentConfig(
        image_config=types.ImageConfig(
            # 1:1 aspect ratio works well for product photos
            # - Square format ideal for e-commerce (uniform grid displays)
            # - Also good for: social media, avatars, logos
            aspect_ratio="1:1"
        ),
        response_modalities=['IMAGE']  # Image only, no text response
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=prompt,
        config=config
    )

    # Save the image
    for part in response.parts:
        if part.inline_data:
            image = part.as_image()
            image.save("product_photo.png")
            print("✓ Product photo saved as 'product_photo.png'")


# High-resolution generation (Gemini 3 Pro)
def generate_high_res():
    """Generate a high-resolution image using Gemini 3 Pro."""

    prompt = """
    Create a vibrant infographic that explains photosynthesis for middle school students.
    Include labeled diagrams of a leaf, sun, water, and CO2. Use bright, educational colors.
    """

    config = types.GenerateContentConfig(
        image_config=types.ImageConfig(
            # 16:9 aspect ratio for infographics/presentations
            # - Matches widescreen displays (laptops, projectors)
            # - Good for: YouTube thumbnails, desktop wallpapers
            aspect_ratio="16:9",

            # 2K resolution balances quality vs file size for infographics
            # - 1K: Too low resolution, text becomes hard to read
            # - 4K: Overkill unless for print, larger file size
            # - 2K: Sweet spot for digital displays
            # CRITICAL: Must use uppercase 'K' ("2K" not "2k")
            image_size="2K"
        ),
        response_modalities=['TEXT', 'IMAGE']
    )

    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=prompt,
        config=config
    )

    # Save the image
    for part in response.parts:
        if part.text:
            print(f"Description: {part.text}")
        elif part.inline_data:
            image = part.as_image()
            image.save("infographic_2k.png")
            print("✓ High-res infographic saved as 'infographic_2k.png'")


# Streaming generation
def generate_streaming():
    """Generate an image with streaming for progress updates."""

    prompt = "A futuristic city skyline at night with neon lights and flying cars"

    print("Generating image...")

    for chunk in client.models.generate_content_stream(
        model="gemini-2.5-flash-image",
        contents=prompt
    ):
        # Print any text output as it streams
        for part in chunk.candidates[0].content.parts:
            if part.text:
                print(part.text, end="")

    print("\n✓ Generation complete!")

    # Note: To save the image with streaming, you need to collect the final chunk
    # For simplicity, use non-streaming generate_content() when you need to save


if __name__ == "__main__":
    print("Gemini Image Generation - Basic Examples\n")

    # Run examples
    print("1. Basic generation...")
    generate_basic_image()

    print("\n2. Generation with configuration...")
    generate_with_config()

    print("\n3. High-resolution generation (Gemini 3 Pro)...")
    generate_high_res()

    print("\n4. Streaming generation...")
    generate_streaming()

    print("\n✓ All examples completed!")
