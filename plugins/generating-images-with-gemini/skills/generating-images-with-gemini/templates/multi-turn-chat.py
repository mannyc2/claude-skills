"""
Multi-Turn Image Refinement with Gemini

This template demonstrates iterative image refinement through conversational editing.
Perfect for gradually perfecting an image through multiple rounds of feedback.

Multi-Turn Refinement Workflow Checklist
=========================================
Copy this checklist to track progress:

- [ ] Step 1: Initial generation (create base image)
- [ ] Step 2: Refine colors/style (adjust overall aesthetic)
- [ ] Step 3: Adjust details (fine-tune specific elements)
- [ ] Step 4: Final polish (last tweaks and improvements)
- [ ] Step 5: Save all versions for comparison

Tips:
- Use chat.send_message() to maintain conversation context
- SDK automatically preserves thought signatures (Gemini 3 Pro)
- Each refinement builds on previous image
- Save intermediate versions to track evolution
- Use Gemini 3 Pro for complex multi-turn workflows
"""

from google import genai
from google.genai import types

# Initialize client
client = genai.Client()


def basic_multi_turn():
    """Simple multi-turn conversation for iterative refinement."""

    # Create a chat session
    chat = client.chats.create(
        model="gemini-3-pro-image-preview",
        config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE']
        )
    )

    # Turn 1: Initial generation
    print("Turn 1: Creating initial logo...")
    response1 = chat.send_message("Create a minimalist logo for a coffee shop called 'Bean There'")

    for part in response1.parts:
        if part.text:
            print(f"  Model: {part.text}")
        elif part.inline_data:
            image1 = part.as_image()
            image1.save("logo_v1.png")
            print("  ✓ Saved as 'logo_v1.png'")

    # Turn 2: First refinement
    print("\nTurn 2: Making it more minimalist...")
    response2 = chat.send_message("Make it more minimalist and use brown tones")

    for part in response2.parts:
        if part.text:
            print(f"  Model: {part.text}")
        elif part.inline_data:
            image2 = part.as_image()
            image2.save("logo_v2.png")
            print("  ✓ Saved as 'logo_v2.png'")

    # Turn 3: Final tweak
    print("\nTurn 3: Adding final element...")
    response3 = chat.send_message("Add a small coffee bean icon in the design")

    for part in response3.parts:
        if part.text:
            print(f"  Model: {part.text}")
        elif part.inline_data:
            image3 = part.as_image()
            image3.save("logo_final.png")
            print("  ✓ Saved as 'logo_final.png'")

    print("\n✓ Multi-turn refinement complete!")


def advanced_multi_turn_with_config():
    """Advanced multi-turn with different configurations per turn."""

    chat = client.chats.create(
        model="gemini-3-pro-image-preview",
        config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE'],
            system_instruction="You are a professional graphic designer with expertise in infographics."
        )
    )

    # Turn 1: Generate infographic
    print("Turn 1: Creating infographic...")
    message1 = "Create a vibrant infographic explaining photosynthesis for students"
    response1 = chat.send_message(message1)

    for part in response1.parts:
        if part.inline_data:
            part.as_image().save("infographic_v1.png")
            print("  ✓ Saved as 'infographic_v1.png'")

    # Turn 2: Translate to Spanish with specific config
    print("\nTurn 2: Translating to Spanish...")
    message2 = "Update this infographic to be in Spanish. Keep all other elements the same."
    config2 = types.GenerateContentConfig(
        image_config=types.ImageConfig(
            # 16:9 aspect ratio for infographics
            # - Matches widescreen displays for presentations
            aspect_ratio="16:9",

            # 2K resolution for final polished version
            # - Higher quality than 1K for professional use
            # - Not 4K to keep file size reasonable
            # - Good balance for digital displays/sharing
            image_size="2K"
        )
    )
    response2 = chat.send_message(message2, config=config2)

    for part in response2.parts:
        if part.inline_data:
            part.as_image().save("infographic_spanish_2k.png")
            print("  ✓ Saved as 'infographic_spanish_2k.png'")

    print("\n✓ Advanced multi-turn complete!")


def iterative_editing_workflow():
    """Demonstrate a realistic iterative editing workflow."""

    chat = client.chats.create(
        model="gemini-3-pro-image-preview",
        config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE']
        )
    )

    versions = []

    # Initial creation
    print("Creating product mockup...")
    r1 = chat.send_message(
        "Create a product mockup of a smartphone displaying a weather app. Modern, clean design."
    )
    img1 = r1.parts[0].as_image()
    img1.save("mockup_v1.png")
    versions.append("mockup_v1.png")
    print("✓ Version 1 saved")

    # Refinement 1: Adjust colors
    print("\nRefining colors...")
    r2 = chat.send_message(
        "Change the weather app to use a dark mode theme with blue accents"
    )
    img2 = r2.parts[0].as_image()
    img2.save("mockup_v2.png")
    versions.append("mockup_v2.png")
    print("✓ Version 2 saved")

    # Refinement 2: Add details
    print("\nAdding details...")
    r3 = chat.send_message(
        "Add a hand holding the phone to make it look more realistic. Natural skin tone, casual setting."
    )
    img3 = r3.parts[0].as_image()
    img3.save("mockup_v3.png")
    versions.append("mockup_v3.png")
    print("✓ Version 3 saved")

    # Final polish
    print("\nFinal polish...")
    r4 = chat.send_message(
        "Add subtle shadows and improve the lighting for a professional product photo look"
    )
    img4 = r4.parts[0].as_image()
    img4.save("mockup_final.png")
    versions.append("mockup_final.png")
    print("✓ Final version saved")

    print(f"\n✓ Workflow complete! Generated {len(versions)} versions:")
    for v in versions:
        print(f"  - {v}")


def multi_turn_with_history():
    """Access conversation history for review."""

    chat = client.chats.create(
        model="gemini-3-pro-image-preview",
        config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE']
        )
    )

    # Have a conversation
    chat.send_message("Create a sunset landscape")
    chat.send_message("Make the colors warmer")
    chat.send_message("Add a silhouette of a tree in the foreground")

    # Review history
    print("Conversation history:")
    for message in chat.get_history():
        print(f"\n{message.role.upper()}:")
        for part in message.parts:
            if part.text:
                print(f"  Text: {part.text[:100]}...")  # First 100 chars
            elif hasattr(part, 'inline_data') and part.inline_data:
                print("  [Image generated]")


def thought_inspection():
    """Inspect the model's thinking process (Gemini 3 Pro only)."""

    chat = client.chats.create(
        model="gemini-3-pro-image-preview",
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(include_thoughts=True)
        )
    )

    print("Generating complex infographic (with thinking enabled)...\n")
    response = chat.send_message(
        "Create a detailed infographic about the solar system with accurate planetary sizes"
    )

    # Inspect thoughts and final output
    for part in response.parts:
        if part.thought:
            # This is a thought (reasoning step)
            if part.text:
                print(f"💭 Thought: {part.text}")
            elif hasattr(part, 'as_image'):
                # Interim thought image (not charged)
                print("💭 [Interim thought image generated]")
        else:
            # This is the final output
            if part.text:
                print(f"\n✅ Final text: {part.text}")
            elif part.inline_data:
                image = part.as_image()
                image.save("solar_system.png")
                print("✅ Final image saved as 'solar_system.png'")

    print("\n✓ Thought inspection complete!")


if __name__ == "__main__":
    print("Gemini Multi-Turn Image Refinement - Examples\n")

    # Choose which example to run
    print("1. Basic multi-turn refinement")
    basic_multi_turn()

    print("\n" + "="*60 + "\n")

    print("2. Advanced multi-turn with configuration")
    advanced_multi_turn_with_config()

    print("\n" + "="*60 + "\n")

    print("3. Iterative editing workflow")
    iterative_editing_workflow()

    print("\n" + "="*60 + "\n")

    print("4. Multi-turn with history inspection")
    multi_turn_with_history()

    print("\n" + "="*60 + "\n")

    print("5. Thought inspection (Gemini 3 Pro)")
    thought_inspection()

    print("\n✓ All multi-turn examples completed!")
