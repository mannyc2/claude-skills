"""
Image Editing with Gemini

This template demonstrates various image editing capabilities using Gemini's
semantic editing (no masks required).
"""

from google import genai
from PIL import Image

# Initialize client
client = genai.Client()


def add_elements_to_image(input_path: str, output_path: str):
    """Add new elements to an existing image."""

    image = Image.open(input_path)

    prompt = """
    Using the provided image, add a small wizard hat on the cat's head.
    Make it look natural and match the lighting of the photo.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[prompt, image]
    )

    for part in response.parts:
        if part.inline_data:
            edited = part.as_image()
            edited.save(output_path)
            print(f"✓ Edited image saved as '{output_path}'")


def semantic_inpainting(input_path: str, output_path: str):
    """Change specific elements without affecting the rest of the image."""

    image = Image.open(input_path)

    # No mask needed - Gemini uses semantic understanding
    prompt = """
    Using the provided image of a living room, change only the blue sofa to be
    a vintage, brown leather chesterfield sofa. Keep everything else exactly
    the same, including the pillows, lighting, and composition.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[prompt, image]
    )

    for part in response.parts:
        if part.inline_data:
            edited = part.as_image()
            edited.save(output_path)
            print(f"✓ Semantically edited image saved as '{output_path}'")


def style_transfer(input_path: str, output_path: str):
    """Apply artistic style to a photo."""

    image = Image.open(input_path)

    prompt = """
    Transform this photograph into the artistic style of Vincent van Gogh's
    'Starry Night'. Preserve the original composition, but render everything
    with swirling, impasto brushstrokes and a dramatic palette of deep blues
    and bright yellows.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[prompt, image]
    )

    for part in response.parts:
        if part.inline_data:
            stylized = part.as_image()
            stylized.save(output_path)
            print(f"✓ Stylized image saved as '{output_path}'")


def multi_image_composition(image1_path: str, image2_path: str, output_path: str):
    """Combine elements from multiple images."""

    image1 = Image.open(image1_path)
    image2 = Image.open(image2_path)

    prompt = """
    Create a professional e-commerce fashion photo. Take the blue floral dress
    from the first image and let the woman from the second image wear it.
    Generate a realistic, full-body shot with proper lighting and shadows.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[image1, image2, prompt]
    )

    for part in response.parts:
        if part.inline_data:
            composite = part.as_image()
            composite.save(output_path)
            print(f"✓ Composite image saved as '{output_path}'")


def remove_elements(input_path: str, output_path: str):
    """Remove specific elements from an image."""

    image = Image.open(input_path)

    prompt = """
    Remove the person from this photo while maintaining the natural appearance
    of the scene. Fill in the background seamlessly as if they were never there.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[prompt, image]
    )

    for part in response.parts:
        if part.inline_data:
            cleaned = part.as_image()
            cleaned.save(output_path)
            print(f"✓ Cleaned image saved as '{output_path}'")


def sketch_to_photo(sketch_path: str, output_path: str):
    """Convert a sketch to a photorealistic image."""

    sketch = Image.open(sketch_path)

    prompt = """
    Turn this rough pencil sketch of a futuristic car into a polished photo of
    the finished concept car in a showroom. Keep the sleek lines and low profile
    from the sketch but add metallic blue paint and neon rim lighting. Make it
    photorealistic.
    """

    # Use Gemini 3 Pro for better photorealistic rendering
    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=[prompt, sketch]
    )

    for part in response.parts:
        if part.inline_data:
            photo = part.as_image()
            photo.save(output_path)
            print(f"✓ Photorealistic render saved as '{output_path}'")


def preserve_details(subject_path: str, overlay_path: str, output_path: str):
    """Combine images while preserving specific details."""

    subject = Image.open(subject_path)
    overlay = Image.open(overlay_path)

    prompt = """
    Take the first image of the woman. Add the logo from the second image onto
    her t-shirt. Ensure the woman's face and features remain completely unchanged.
    The logo should look naturally printed on the fabric, following the shirt's
    folds and contours.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[subject, overlay, prompt]
    )

    for part in response.parts:
        if part.inline_data:
            result = part.as_image()
            result.save(output_path)
            print(f"✓ Result with preserved details saved as '{output_path}'")


if __name__ == "__main__":
    print("Gemini Image Editing - Examples\n")
    print("Note: Update the file paths below with your actual images\n")

    # Example usage (update paths to your actual files)

    # 1. Add elements
    # add_elements_to_image("cat.jpg", "cat_with_hat.png")

    # 2. Semantic inpainting (change specific elements)
    # semantic_inpainting("living_room.jpg", "living_room_edited.png")

    # 3. Style transfer
    # style_transfer("city_photo.jpg", "city_vangogh.png")

    # 4. Multi-image composition
    # multi_image_composition("dress.jpg", "model.jpg", "fashion_composite.png")

    # 5. Remove elements
    # remove_elements("photo_with_person.jpg", "photo_cleaned.png")

    # 6. Sketch to photo
    # sketch_to_photo("car_sketch.jpg", "car_render.png")

    # 7. Preserve details
    # preserve_details("person.jpg", "logo.png", "person_with_logo.png")

    print("✓ Template ready! Uncomment examples and update file paths to run.")
