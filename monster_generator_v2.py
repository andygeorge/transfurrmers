#!/usr/bin/env python3
"""
Improved Pokemon-like Monster Generator with robust parsing
"""

import requests
import json
import re
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
    """Agent that queries Ollama to generate monsters with robust parsing"""
    
    def __init__(self, base_url: str = "http://lenovo-legion-5.andygeor.ge:11434", model: str = "hf.co/unsloth/Qwen3-4B-Thinking-2507-GGUF:Q8_0", debug: bool = False):
        self.base_url = base_url
        self.model = model
        self.debug = debug
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
                "num_predict": 400
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=600)
            response.raise_for_status()
            result = response.json()["response"]
            
            if self.debug:
                print("\n" + "="*60)
                print("DEBUG - Ollama Response:")
                print("="*60)
                print(result)
                print("="*60 + "\n")
            
            return result
        except requests.exceptions.RequestException as e:
            print(f"❌ Error querying Ollama: {e}")
            print(f"   Make sure Ollama is running: ollama serve")
            return ""
    
    def create_generation_prompt(self, iteration: int, theme: Optional[str] = None) -> str:
        """Create a simplified prompt that's easier to parse"""
        
        context = ""
        if self.monsters_created:
            context = "\nAvoid creating monsters similar to: "
            context += ", ".join([m.name for m in self.monsters_created[-3:]])
        
        theme_text = f" (Theme: {theme})" if theme else ""
        
        # Simplified, more structured prompt
        prompt = f"""Create a unique Pokemon-like monster{theme_text}.{context}

Respond in EXACTLY this format:

NAME: [creative name]
TYPE: [Fire, Water, Grass, Electric, Ice, Psychic, Dark, Dragon, or similar]
DESCRIPTION: [one sentence about appearance and behavior]
HP: [number between 50-150]
ATTACK: [number between 30-120]
DEFENSE: [number between 30-120]
SPEED: [number between 30-120]
SPECIAL: [number between 30-120]
ABILITY1: [first ability name]
ABILITY2: [second ability name]
EVOLUTION: [1, 2, or 3]
RARITY: [Common, Uncommon, Rare, Epic, or Legendary]

Keep it simple and follow the format exactly."""

        print(prompt)
        
        return prompt
    
    def parse_monster_response(self, response: str) -> Optional[Monster]:
        """Improved parsing with multiple fallback strategies"""
        try:
            # Strategy 1: Try simple line-by-line parsing
            monster = self._parse_line_by_line(response)
            if monster:
                return monster
            
            # Strategy 2: Try regex-based extraction
            if self.debug:
                print("⚠️  Line-by-line parsing failed, trying regex...")
            monster = self._parse_with_regex(response)
            if monster:
                return monster
            
            # Strategy 3: Try flexible extraction
            if self.debug:
                print("⚠️  Regex parsing failed, trying flexible extraction...")
            monster = self._parse_flexible(response)
            if monster:
                return monster
                
        except Exception as e:
            if self.debug:
                print(f"❌ Parsing error: {e}")
        
        return None
    
    def _parse_line_by_line(self, response: str) -> Optional[Monster]:
        """Parse response line by line (most reliable)"""
        data = {
            'name': None,
            'type': None,
            'description': None,
            'stats': {},
            'abilities': [],
            'evolution_stage': 1,
            'rarity': 'Common'
        }
        
        lines = response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Handle different separators
            if ':' not in line:
                continue
                
            key, value = line.split(':', 1)
            key = key.strip().upper()
            value = value.strip()
            
            if not value:
                continue
            
            # Parse each field
            if 'NAME' in key:
                data['name'] = value
            elif 'TYPE' in key:
                data['type'] = value
            elif 'DESCRIPTION' in key or 'DESC' in key:
                data['description'] = value
            elif 'HP' in key:
                data['stats']['HP'] = self._extract_number(value)
            elif 'ATTACK' in key or 'ATK' in key:
                data['stats']['Attack'] = self._extract_number(value)
            elif 'DEFENSE' in key or 'DEF' in key:
                data['stats']['Defense'] = self._extract_number(value)
            elif 'SPEED' in key or 'SPD' in key:
                data['stats']['Speed'] = self._extract_number(value)
            elif 'SPECIAL' in key or 'SP' in key:
                data['stats']['Special'] = self._extract_number(value)
            elif 'ABILITY' in key or 'MOVE' in key:
                if value and value not in data['abilities']:
                    data['abilities'].append(value)
            elif 'EVOLUTION' in key or 'STAGE' in key or 'EVO' in key:
                data['evolution_stage'] = self._extract_number(value, default=1)
            elif 'RARITY' in key or 'RARE' in key:
                data['rarity'] = value
        
        # Validate we have minimum required fields
        if data['name'] and data['type'] and len(data['stats']) >= 3:
            # Fill in missing stats with defaults
            for stat in ['HP', 'Attack', 'Defense', 'Speed', 'Special']:
                if stat not in data['stats']:
                    data['stats'][stat] = 50
            
            # Ensure we have at least one ability
            if not data['abilities']:
                data['abilities'] = ['Tackle', 'Growl']
            
            if not data['description']:
                data['description'] = f"A {data['type']}-type monster"
            
            return Monster(
                name=data['name'],
                type=data['type'],
                description=data['description'],
                stats=data['stats'],
                abilities=data['abilities'],
                evolution_stage=data['evolution_stage'],
                rarity=data['rarity']
            )
        
        return None
    
    def _parse_with_regex(self, response: str) -> Optional[Monster]:
        """Parse using regex patterns"""
        data = {}
        
        # Extract name
        name_match = re.search(r'NAME:\s*(.+?)(?:\n|$)', response, re.IGNORECASE)
        if name_match:
            data['name'] = name_match.group(1).strip()
        
        # Extract type
        type_match = re.search(r'TYPE:\s*(.+?)(?:\n|$)', response, re.IGNORECASE)
        if type_match:
            data['type'] = type_match.group(1).strip()
        
        # Extract description
        desc_match = re.search(r'DESCRIPTION:\s*(.+?)(?:\n|$)', response, re.IGNORECASE)
        if desc_match:
            data['description'] = desc_match.group(1).strip()
        
        # Extract stats
        stats = {}
        for stat_name in ['HP', 'ATTACK', 'DEFENSE', 'SPEED', 'SPECIAL']:
            pattern = rf'{stat_name}:\s*(\d+)'
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                stats[stat_name.title() if stat_name != 'HP' else 'HP'] = int(match.group(1))
        
        # Extract abilities
        abilities = []
        for i in range(1, 4):
            ability_match = re.search(rf'ABILITY{i}:\s*(.+?)(?:\n|$)', response, re.IGNORECASE)
            if ability_match:
                abilities.append(ability_match.group(1).strip())
        
        # Evolution stage
        evo_match = re.search(r'EVOLUTION:\s*(\d+)', response, re.IGNORECASE)
        evolution_stage = int(evo_match.group(1)) if evo_match else 1
        
        # Rarity
        rarity_match = re.search(r'RARITY:\s*(.+?)(?:\n|$)', response, re.IGNORECASE)
        rarity = rarity_match.group(1).strip() if rarity_match else 'Common'
        
        if data.get('name') and data.get('type') and stats:
            return Monster(
                name=data['name'],
                type=data['type'],
                description=data.get('description', f"A {data['type']} type monster"),
                stats=stats,
                abilities=abilities if abilities else ['Tackle'],
                evolution_stage=evolution_stage,
                rarity=rarity
            )
        
        return None
    
    def _parse_flexible(self, response: str) -> Optional[Monster]:
        """Last resort: extract any numbers and create a basic monster"""
        # Find any capitalized words that could be a name
        words = response.split()
        potential_names = [w.strip(',:;.!?') for w in words if w and w[0].isupper() and len(w) > 3]
        
        # Find all numbers
        numbers = re.findall(r'\b(\d{2,3})\b', response)
        numbers = [int(n) for n in numbers if 20 <= int(n) <= 200]
        
        if potential_names and len(numbers) >= 3:
            stats = {
                'HP': numbers[0] if len(numbers) > 0 else 80,
                'Attack': numbers[1] if len(numbers) > 1 else 60,
                'Defense': numbers[2] if len(numbers) > 2 else 60,
                'Speed': numbers[3] if len(numbers) > 3 else 60,
                'Special': numbers[4] if len(numbers) > 4 else 60,
            }
            
            return Monster(
                name=potential_names[0],
                type='Normal',
                description=f"A mysterious {potential_names[0]} creature",
                stats=stats,
                abilities=['Tackle', 'Defend'],
                evolution_stage=1,
                rarity='Common'
            )
        
        return None
    
    def _extract_number(self, text: str, default: int = 50) -> int:
        """Extract first number from text"""
        match = re.search(r'\d+', text)
        if match:
            num = int(match.group())
            return max(1, min(200, num))  # Clamp between 1-200
        return default
    
    def generate_monster(self, theme: Optional[str] = None, retries: int = 3) -> Optional[Monster]:
        """Generate a single monster with retries"""
        iteration = len(self.monsters_created)
        
        for attempt in range(retries):
            print(f"\n🔮 Generating monster #{iteration + 1} (attempt {attempt + 1}/{retries})...")
            
            prompt = self.create_generation_prompt(iteration, theme)
            response = self.query_ollama(prompt)
            
            if response:
                monster = self.parse_monster_response(response)
                if monster:
                    self.monsters_created.append(monster)
                    print(f"✅ Created: {monster.name} ({monster.type})")
                    return monster
            
            if attempt < retries - 1:
                print(f"⚠️  Parsing failed, retrying in 2 seconds...")
                time.sleep(2)
        
        print("❌ Failed to generate valid monster after all retries")
        return None
    
    def generate_batch(self, count: int = 5, theme: Optional[str] = None, delay: float = 1.0):
        """Generate multiple monsters iteratively"""
        print(f"\n🎮 Batch Generation: {count} monsters")
        if theme:
            print(f"📝 Theme: {theme}")
        
        successful = 0
        for i in range(count):
            monster = self.generate_monster(theme)
            if monster:
                self.display_monster(monster)
                successful += 1
            
            if i < count - 1:
                time.sleep(delay)
        
        print(f"\n✅ Successfully generated {successful}/{count} monsters")
    
    def display_monster(self, monster: Monster):
        """Display monster information"""
        print("\n" + "="*60)
        print(f"🐉 {monster.name}")
        print("="*60)
        print(f"Type: {monster.type} | Rarity: {monster.rarity} | Stage: {monster.evolution_stage}")
        print(f"\n{monster.description}")
        
        print("\n📊 Stats:")
        for stat, value in monster.stats.items():
            bar = "█" * (value // 10)
            print(f"  {stat:10s}: {value:3d} {bar}")
        
        print("\n⚡ Abilities:")
        for ability in monster.abilities:
            print(f"  • {ability}")
    
    def save_monsters(self, filename: str = "monsters.json"):
        """Save all generated monsters to JSON"""
        data = [monster.to_dict() for monster in self.monsters_created]
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\n💾 Saved {len(data)} monsters to {filename}")


def main():
    """Main demo"""
    import sys
    
    # Check if debug flag is passed
    debug_mode = '--debug' in sys.argv or '-d' in sys.argv
    
    print("🎮 Pokemon-like Monster Generator v2")
    print("=" * 60)
    
    if debug_mode:
        print("🐛 DEBUG MODE ENABLED - Will show Ollama responses\n")
    
    # Initialize generator
    generator = OllamaMonsterGenerator(
        base_url="http://lenovo-legion-5.andygeor.ge:11434",
        model="hf.co/unsloth/Qwen3-4B-Thinking-2507-GGUF:Q8_0",  # Change to your model
        debug=debug_mode
    )
    
    # Test connection first
    print("🔌 Testing Ollama connection...")
    test_response = generator.query_ollama("Say 'hello' and nothing else", temperature=0.1)
    if not test_response:
        print("\n❌ Cannot connect to Ollama!")
        print("   Please make sure Ollama is running:")
        print("   → ollama serve")
        return
    print("✅ Connected to Ollama\n")
    
    # Generate monsters
    generator.generate_batch(count=3, theme="fire", delay=2.0)
    
    # Save results
    generator.save_monsters("monsters_v2.json")
    
    print("\n🎯 Tips:")
    print("  • Run with --debug flag to see raw Ollama responses")
    print("  • Change the model in the code if llama3.2 doesn't work")
    print("  • Try themes like 'water', 'dragon', 'electric', 'ghost'")


if __name__ == "__main__":
    main()