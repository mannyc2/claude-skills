"""
Google Search Grounding for Image Generation

This template demonstrates using Google Search grounding to generate images
based on real-time data (only available with Gemini 3 Pro Image Preview).

Perfect for: current events, weather, sports scores, recent news, stock market, etc.
"""

from google import genai
from google.genai import types

# Initialize client
client = genai.Client()


def generate_with_search(prompt: str, output_file: str = "grounded_image.png"):
    """Generate image grounded in real-time Google Search data."""

    config = types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
        image_config=types.ImageConfig(aspect_ratio="16:9"),
        tools=[{"google_search": {}}]  # Enable Google Search grounding
    )

    print(f"Generating with search grounding...")
    print(f"Prompt: {prompt}\n")

    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",  # Only 3 Pro supports grounding
        contents=prompt,
        config=config
    )

    # Extract and display grounding metadata
    if response.candidates and response.candidates[0].grounding_metadata:
        metadata = response.candidates[0].grounding_metadata

        print("📊 Grounding Metadata:")

        # Search entry point (required HTML/CSS for search suggestions)
        if hasattr(metadata, 'search_entry_point'):
            print(f"\n  Search Entry Point: {metadata.search_entry_point}")

        # Grounding chunks (top 3 web sources used)
        if hasattr(metadata, 'grounding_chunks'):
            print(f"\n  Sources Used:")
            for chunk in metadata.grounding_chunks:
                if hasattr(chunk, 'web'):
                    print(f"    - {chunk.web.title}")
                    print(f"      {chunk.web.uri}")

    # Save image and text
    for part in response.parts:
        if part.text:
            print(f"\n📝 Text response:\n{part.text}\n")
        elif part.inline_data:
            image = part.as_image()
            image.save(output_file)
            print(f"✓ Image saved as '{output_file}'")


def weather_visualization():
    """Generate weather forecast visualization."""

    prompt = """
    Visualize the current weather forecast for the next 5 days in San Francisco
    as a clean, modern weather chart. Include temperatures, weather icons,
    and day labels.
    """

    generate_with_search(prompt, "weather_forecast.png")


def sports_infographic():
    """Generate sports game summary."""

    prompt = """
    Create a stylish infographic about last night's NBA championship game.
    Include the final score, key player stats, and team logos.
    """

    generate_with_search(prompt, "game_summary.png")


def stock_market_chart():
    """Generate stock market visualization."""

    prompt = """
    Create a professional chart showing yesterday's performance of major
    tech stocks (Apple, Microsoft, Google, Amazon). Use clean design with
    corporate colors.
    """

    generate_with_search(prompt, "stock_chart.png")


def current_events_graphic():
    """Generate current events visualization."""

    prompt = """
    Design an infographic about the latest space exploration news from this week.
    Make it educational and visually engaging with space-themed colors.
    """

    generate_with_search(prompt, "space_news.png")


def climate_data_visualization():
    """Generate climate data visualization."""

    prompt = """
    Create an infographic showing recent global temperature data and climate
    trends. Use scientific visualization style with accurate data representation.
    """

    generate_with_search(prompt, "climate_data.png")


def multi_turn_grounded_refinement():
    """Use search grounding in multi-turn conversation."""

    chat = client.chats.create(
        model="gemini-3-pro-image-preview",
        config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE'],
            tools=[{"google_search": {}}]  # Enable grounding for all turns
        )
    )

    print("Multi-turn conversation with Google Search grounding:\n")

    # Turn 1: Generate initial visualization
    print("Turn 1: Creating visualization...")
    r1 = chat.send_message(
        "Create a timeline of major tech announcements from this week"
    )

    for part in r1.parts:
        if part.inline_data:
            part.as_image().save("tech_timeline_v1.png")
            print("✓ Saved tech_timeline_v1.png")

    # Turn 2: Refine
    print("\nTurn 2: Refining design...")
    r2 = chat.send_message(
        "Make it more minimalist and add company logos"
    )

    for part in r2.parts:
        if part.inline_data:
            part.as_image().save("tech_timeline_v2.png")
            print("✓ Saved tech_timeline_v2.png")

    # Display sources used
    if r1.candidates and r1.candidates[0].grounding_metadata:
        print("\n📚 Sources consulted:")
        for chunk in r1.candidates[0].grounding_metadata.grounding_chunks:
            if hasattr(chunk, 'web'):
                print(f"  - {chunk.web.title}")


def handle_grounding_metadata(response):
    """Helper function to extract and display grounding metadata."""

    if not response.candidates:
        return

    metadata = response.candidates[0].grounding_metadata
    if not metadata:
        return

    result = {
        'search_entry_point': None,
        'sources': []
    }

    # Extract search entry point
    if hasattr(metadata, 'search_entry_point'):
        result['search_entry_point'] = metadata.search_entry_point

    # Extract source chunks
    if hasattr(metadata, 'grounding_chunks'):
        for chunk in metadata.grounding_chunks:
            if hasattr(chunk, 'web'):
                result['sources'].append({
                    'title': chunk.web.title,
                    'uri': chunk.web.uri
                })

    return result


def advanced_grounding_example():
    """Advanced example with detailed metadata handling."""

    prompt = """
    Create a comprehensive infographic about recent developments in AI.
    Include key milestones, major announcements, and trending topics.
    Use modern, tech-forward design.
    """

    config = types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
        image_config=types.ImageConfig(
            aspect_ratio="16:9",
            image_size="2K"  # High resolution
        ),
        tools=[{"google_search": {}}]
    )

    print("Generating AI developments infographic with search grounding...\n")

    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=prompt,
        config=config
    )

    # Process metadata
    metadata = handle_grounding_metadata(response)

    if metadata:
        print("🔍 Grounding Information:")
        print(f"\nSources consulted: {len(metadata['sources'])}")
        for i, source in enumerate(metadata['sources'], 1):
            print(f"\n{i}. {source['title']}")
            print(f"   {source['uri']}")

    # Save image
    for part in response.parts:
        if part.inline_data:
            part.as_image().save("ai_developments_2k.png")
            print(f"\n✓ Saved ai_developments_2k.png (2K resolution)")


if __name__ == "__main__":
    print("Gemini Image Generation with Google Search Grounding\n")
    print("⚠️  Note: Only works with gemini-3-pro-image-preview")
    print("="*60 + "\n")

    # Choose example
    print("Examples:")
    print("1. Weather forecast visualization")
    print("2. Sports game infographic")
    print("3. Stock market chart")
    print("4. Current events graphic")
    print("5. Climate data visualization")
    print("6. Multi-turn grounded refinement")
    print("7. Advanced grounding with 2K resolution")

    choice = input("\nSelect example (1-7): ").strip()

    examples = {
        "1": weather_visualization,
        "2": sports_infographic,
        "3": stock_market_chart,
        "4": current_events_graphic,
        "5": climate_data_visualization,
        "6": multi_turn_grounded_refinement,
        "7": advanced_grounding_example
    }

    if choice in examples:
        print(f"\n{'='*60}\n")
        examples[choice]()
    else:
        print("Invalid choice")

    print("\n✓ Google Search grounding example completed!")
    print("\n💡 Tip: Grounding works best for recent events, data, and factual content")
