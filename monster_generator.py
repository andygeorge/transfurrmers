#!/usr/bin/env python3
"""
Pokemon-like Monster Generator using Ollama
Iteratively creates unique battling monsters with stats and abilities
"""

import requests
import json
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class Monster:
    """Represents a Pokemon-like battling monster"""
    name: str
    type: str
    description: str
    stats: Dict[str, int]
    abilities: List[str]
    evolution_stage: int
    rarity: str
    
    def to_dict(self):
        return asdict(self)


class OllamaMonsterGenerator:
    """Agent that queries Ollama to generate monsters"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2"):
        self.base_url = base_url
        self.model = model
        self.monsters_created = []
        
    def query_ollama(self, prompt: str, temperature: float = 0.8) -> str:
        """Send a prompt to Ollama and get the response"""
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "temperature": temperature,
            "options": {
                "num_predict": 500
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()["response"]
        except requests.exceptions.RequestException as e:
            print(f"Error querying Ollama: {e}")
            return ""
    
    def create_generation_prompt(self, iteration: int, theme: Optional[str] = None) -> str:
        """Create a structured prompt for monster generation"""
        
        # Build context from previously created monsters
        context = ""
        if self.monsters_created:
            context = "\n\nPreviously created monsters (create something different):\n"
            for monster in self.monsters_created[-3:]:  # Last 3 monsters
                context += f"- {monster.name} ({monster.type})\n"
        
        theme_text = f" with a {theme} theme" if theme else ""
        
        prompt = f"""Create a unique Pokemon-like battling monster{theme_text}. 
{context}

Provide the following in a structured format:

NAME: [Creative monster name]
TYPE: [Element type: Fire/Water/Grass/Electric/Ice/Psychic/Dark/Dragon/etc.]
DESCRIPTION: [One sentence description of appearance and personality]
STATS:
- HP: [50-150]
- Attack: [30-120]
- Defense: [30-120]
- Speed: [30-120]
- Special: [30-120]
ABILITIES: [List 2-3 unique battle abilities]
EVOLUTION_STAGE: [1, 2, or 3]
RARITY: [Common/Uncommon/Rare/Epic/Legendary]

Be creative and ensure this monster is distinct from previous ones!"""
        
        return prompt
    
    def parse_monster_response(self, response: str) -> Optional[Monster]:
        """Parse Ollama's response into a Monster object"""
        try:
            lines = response.strip().split('\n')
            monster_data = {}
            stats = {}
            abilities = []
            
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith("NAME:"):
                    monster_data['name'] = line.split(":", 1)[1].strip()
                elif line.startswith("TYPE:"):
                    monster_data['type'] = line.split(":", 1)[1].strip()
                elif line.startswith("DESCRIPTION:"):
                    monster_data['description'] = line.split(":", 1)[1].strip()
                elif line.startswith("STATS:"):
                    current_section = "stats"
                elif line.startswith("ABILITIES:"):
                    current_section = "abilities"
                    # Sometimes abilities are on the same line
                    ability_text = line.split(":", 1)[1].strip()
                    if ability_text:
                        abilities.append(ability_text)
                elif line.startswith("EVOLUTION_STAGE:"):
                    try:
                        monster_data['evolution_stage'] = int(line.split(":", 1)[1].strip())
                    except:
                        monster_data['evolution_stage'] = 1
                elif line.startswith("RARITY:"):
                    monster_data['rarity'] = line.split(":", 1)[1].strip()
                elif current_section == "stats" and ":" in line:
                    # Parse stat lines like "- HP: 100" or "HP: 100"
                    stat_line = line.lstrip('-').strip()
                    if ":" in stat_line:
                        stat_name, stat_value = stat_line.split(":", 1)
                        try:
                            stats[stat_name.strip()] = int(stat_value.strip())
                        except:
                            pass
                elif current_section == "abilities" and line.startswith("-"):
                    abilities.append(line.lstrip('-').strip())
            
            # Create monster if we have minimum required fields
            if all(key in monster_data for key in ['name', 'type', 'description']):
                return Monster(
                    name=monster_data['name'],
                    type=monster_data['type'],
                    description=monster_data['description'],
                    stats=stats if stats else {"HP": 100, "Attack": 50, "Defense": 50, "Speed": 50, "Special": 50},
                    abilities=abilities if abilities else ["Tackle", "Growl"],
                    evolution_stage=monster_data.get('evolution_stage', 1),
                    rarity=monster_data.get('rarity', 'Common')
                )
            
        except Exception as e:
            print(f"Error parsing monster: {e}")
            
        return None
    
    def generate_monster(self, theme: Optional[str] = None, retries: int = 2) -> Optional[Monster]:
        """Generate a single monster with retries"""
        iteration = len(self.monsters_created)
        
        for attempt in range(retries):
            print(f"\n🔮 Generating monster #{iteration + 1} (attempt {attempt + 1})...")
            
            prompt = self.create_generation_prompt(iteration, theme)
            response = self.query_ollama(prompt)
            
            if response:
                monster = self.parse_monster_response(response)
                if monster:
                    self.monsters_created.append(monster)
                    print(f"✨ Created: {monster.name} ({monster.type})")
                    return monster
            
            if attempt < retries - 1:
                print("⚠️ Failed to parse, retrying...")
                time.sleep(1)
        
        print("❌ Failed to generate monster")
        return None
    
    def generate_batch(self, count: int = 5, theme: Optional[str] = None, delay: float = 1.0):
        """Generate multiple monsters iteratively"""
        print(f"\n🎮 Starting batch generation of {count} monsters...")
        if theme:
            print(f"📝 Theme: {theme}")
        
        for i in range(count):
            monster = self.generate_monster(theme)
            if monster:
                self.display_monster(monster)
            
            # Small delay between generations
            if i < count - 1:
                time.sleep(delay)
        
        print(f"\n✅ Generated {len(self.monsters_created)} monsters total!")
    
    def display_monster(self, monster: Monster):
        """Display a monster's information"""
        print("\n" + "="*60)
        print(f"🐉 {monster.name}")
        print("="*60)
        print(f"Type: {monster.type}")
        print(f"Rarity: {monster.rarity}")
        print(f"Evolution Stage: {monster.evolution_stage}")
        print(f"\n{monster.description}")
        
        print("\n📊 Stats:")
        for stat, value in monster.stats.items():
            bar = "█" * (value // 10)
            print(f"  {stat:10s}: {value:3d} {bar}")
        
        print("\n⚡ Abilities:")
        for ability in monster.abilities:
            print(f"  • {ability}")
        print()
    
    def save_monsters(self, filename: str = "monsters.json"):
        """Save all generated monsters to a JSON file"""
        data = [monster.to_dict() for monster in self.monsters_created]
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Saved {len(data)} monsters to {filename}")
    
    def load_monsters(self, filename: str = "monsters.json"):
        """Load monsters from a JSON file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            self.monsters_created = [Monster(**monster_data) for monster_data in data]
            print(f"📂 Loaded {len(self.monsters_created)} monsters from {filename}")
        except FileNotFoundError:
            print(f"❌ File {filename} not found")


def main():
    """Main function demonstrating the monster generator"""
    
    # Initialize the generator
    # Change the model name to whatever you have installed in Ollama
    generator = OllamaMonsterGenerator(
        base_url="http://lenovo-legion-5.andygeor.ge:11434",
        model="hf.co/unsloth/Qwen3-4B-Thinking-2507-GGUF:Q8_0"  # or "mistral", "phi", etc.
    )
    
    print("🎮 Pokemon-like Monster Generator")
    print("=" * 60)
    
    # Example 1: Generate a few monsters with a theme
    generator.generate_batch(count=3, theme="volcanic", delay=2.0)
    
    # Example 2: Generate without a theme
    # generator.generate_batch(count=2, delay=2.0)
    
    # Save all created monsters
    generator.save_monsters("monsters.json")
    
    # Display all monsters
    print("\n\n🏆 ALL CREATED MONSTERS:")
    print("=" * 60)
    for i, monster in enumerate(generator.monsters_created, 1):
        print(f"\n#{i}. {monster.name} - {monster.type} ({monster.rarity})")


if __name__ == "__main__":
    main()
