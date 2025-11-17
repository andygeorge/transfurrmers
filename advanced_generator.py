#!/usr/bin/env python3
"""
Advanced Monster Generator - Creates evolution chains and themed collections
"""

from monster_generator import OllamaMonsterGenerator, Monster
import json
from typing import List, Optional


class AdvancedMonsterGenerator(OllamaMonsterGenerator):
    """Extended generator with evolution chains and themed sets"""
    
    def generate_evolution_chain(self, base_theme: str, stages: int = 3) -> List[Monster]:
        """Generate a complete evolution chain"""
        print(f"\n🔗 Generating {stages}-stage evolution chain: {base_theme}")
        chain = []
        
        for stage in range(1, stages + 1):
            prompt = self.create_evolution_prompt(base_theme, stage, chain)
            response = self.query_ollama(prompt, temperature=0.7)
            
            if response:
                monster = self.parse_monster_response(response)
                if monster:
                    monster.evolution_stage = stage
                    chain.append(monster)
                    self.monsters_created.append(monster)
                    print(f"  Stage {stage}: {monster.name}")
        
        return chain
    
    def create_evolution_prompt(self, base_theme: str, stage: int, previous_forms: List[Monster]) -> str:
        """Create a prompt for a specific evolution stage"""
        
        if stage == 1:
            prompt = f"""Create the FIRST evolution stage of a {base_theme}-themed monster.

This should be a cute, small, basic form that will evolve into stronger forms.

NAME: [Simple, cute name]
TYPE: [Element type appropriate for {base_theme}]
DESCRIPTION: [Small, adorable creature description]
STATS:
- HP: [60-80]
- Attack: [30-50]
- Defense: [30-50]
- Speed: [40-60]
- Special: [30-50]
ABILITIES: [1-2 basic abilities]
EVOLUTION_STAGE: 1
RARITY: Common"""
        
        else:
            prev_name = previous_forms[-1].name
            prev_type = previous_forms[-1].type
            
            if stage == 2:
                power_level = "intermediate"
                stat_range = "HP: 90-110, Attack: 60-80, Defense: 60-80, Speed: 60-80, Special: 60-80"
            else:
                power_level = "final, powerful"
                stat_range = "HP: 120-150, Attack: 90-120, Defense: 90-120, Speed: 90-120, Special: 90-120"
            
            prompt = f"""Create the evolution of {prev_name} (stage {stage} of 3).

Previous form: {prev_name} - {prev_type}
Theme: {base_theme}

This should be a {power_level} evolution that builds upon the previous form's design.
The name should feel related to {prev_name} but more mature/powerful.

NAME: [Evolution name related to {prev_name}]
TYPE: {prev_type}
DESCRIPTION: [More mature, powerful version of previous form]
STATS:
- {stat_range}
ABILITIES: [2-3 stronger abilities, can reference previous abilities evolved]
EVOLUTION_STAGE: {stage}
RARITY: {"Uncommon" if stage == 2 else "Rare"}"""
        
        return prompt
    
    def generate_themed_collection(self, theme: str, count: int = 6):
        """Generate a collection of monsters around a specific theme"""
        print(f"\n🎨 Generating themed collection: {theme}")
        print(f"   Target: {count} unique monsters")
        
        themes_variety = [
            f"{theme} - aggressive type",
            f"{theme} - defensive type", 
            f"{theme} - speed type",
            f"{theme} - balanced type",
            f"{theme} - special attacker",
            f"{theme} - support type"
        ]
        
        for i in range(min(count, len(themes_variety))):
            self.generate_monster(theme=themes_variety[i])
    
    def generate_starter_trio(self):
        """Generate a classic starter trio (Grass/Fire/Water)"""
        print("\n🌟 Generating Starter Trio!")
        
        types = [
            ("Grass", "plant-based"),
            ("Fire", "flame-based"),
            ("Water", "aquatic")
        ]
        
        for element_type, theme in types:
            prompt = f"""Create a STARTER monster for trainers - {theme}.

This should be a stage 1 evolution monster that's friendly and appealing.

NAME: [Cute, memorable name]
TYPE: {element_type}
DESCRIPTION: [Friendly, appealing first partner monster]
STATS:
- HP: 70
- Attack: 45
- Defense: 45
- Speed: 50
- Special: 50
ABILITIES: [2 basic {element_type} abilities]
EVOLUTION_STAGE: 1
RARITY: Uncommon"""
            
            response = self.query_ollama(prompt)
            if response:
                monster = self.parse_monster_response(response)
                if monster:
                    self.monsters_created.append(monster)
                    self.display_monster(monster)
    
    def generate_legendary(self, theme: str):
        """Generate a legendary/mythical monster"""
        print(f"\n⭐ Generating LEGENDARY monster: {theme}")
        
        prompt = f"""Create a LEGENDARY, mythical monster with a {theme} theme.

This should be an incredibly rare, powerful, and majestic creature.

NAME: [Epic, legendary-sounding name]
TYPE: [Can be dual-type like "Dragon/Psychic"]
DESCRIPTION: [Majestic, powerful, legendary creature with lore]
STATS:
- HP: 150
- Attack: 110
- Defense: 110
- Speed: 100
- Special: 120
ABILITIES: [3-4 unique, powerful signature abilities]
EVOLUTION_STAGE: 3
RARITY: Legendary"""
        
        response = self.query_ollama(prompt)
        if response:
            monster = self.parse_monster_response(response)
            if monster:
                self.monsters_created.append(monster)
                self.display_monster(monster)
                return monster
        return None


def example_evolution_chains():
    """Example: Create multiple evolution chains"""
    generator = AdvancedMonsterGenerator(model="llama3.2")
    
    # Generate a few evolution chains
    chains = [
        generator.generate_evolution_chain("electric mouse", stages=3),
        generator.generate_evolution_chain("fire dragon", stages=3),
        generator.generate_evolution_chain("water turtle", stages=3)
    ]
    
    generator.save_monsters("evolution_chains.json")
    return chains


def example_themed_region():
    """Example: Create monsters for a themed region"""
    generator = AdvancedMonsterGenerator(model="llama3.2")
    
    print("\n🗺️  GENERATING VOLCANIC REGION MONSTERS")
    print("="*60)
    
    # Starter trio
    generator.generate_starter_trio()
    
    # Evolution chain for regional legendary
    generator.generate_evolution_chain("volcanic phoenix", stages=3)
    
    # Themed collection
    generator.generate_themed_collection("volcano", count=4)
    
    # A legendary
    generator.generate_legendary("volcanic god of destruction")
    
    generator.save_monsters("volcanic_region.json")


def example_competitive_team():
    """Example: Generate a balanced competitive team"""
    generator = AdvancedMonsterGenerator(model="llama3.2")
    
    print("\n🏆 GENERATING COMPETITIVE BATTLE TEAM")
    print("="*60)
    
    roles = [
        ("physical sweeper", "fast, high attack"),
        ("special sweeper", "high special attack, good speed"),
        ("tank", "high HP and defense"),
        ("support", "defensive with healing abilities"),
        ("mixed attacker", "balanced offensive stats"),
        ("wall breaker", "extremely high attack")
    ]
    
    for role, description in roles:
        print(f"\n📍 Generating {role}...")
        generator.generate_monster(theme=description)
    
    generator.save_monsters("competitive_team.json")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
        if mode == "chains":
            example_evolution_chains()
        elif mode == "region":
            example_themed_region()
        elif mode == "team":
            example_competitive_team()
        else:
            print("Usage: python advanced_generator.py [chains|region|team]")
    else:
        # Default: run themed region example
        example_themed_region()