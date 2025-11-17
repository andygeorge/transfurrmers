#!/usr/bin/env python3
"""
Simple demo showing the most common use cases
"""

from monster_generator import OllamaMonsterGenerator

def demo():
    print("🎮 Monster Generator Demo")
    print("=" * 60)
    
    # Initialize
    generator = OllamaMonsterGenerator(
        base_url="http://localhost:11434",
        model="llama3.2"  # Change to your installed model
    )
    
    print("\n1️⃣  Generating a single fire-type monster...")
    monster = generator.generate_monster(theme="fire dragon")
    if monster:
        generator.display_monster(monster)
    
    print("\n2️⃣  Generating 3 water-themed monsters...")
    generator.generate_batch(count=3, theme="aquatic", delay=1.0)
    
    # Save all
    generator.save_monsters("demo_monsters.json")
    print("\n✅ All monsters saved to demo_monsters.json")
    
    # Show summary
    print(f"\n📊 Summary: Generated {len(generator.monsters_created)} monsters")
    print("\nMonster Names:")
    for i, m in enumerate(generator.monsters_created, 1):
        print(f"  {i}. {m.name} ({m.type}) - {m.rarity}")


if __name__ == "__main__":
    demo()