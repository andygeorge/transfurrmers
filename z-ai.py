import requests
import json
import random
import time
from typing import Dict, List, Optional

class PokemonCreatureGenerator:
    def __init__(self, ollama_url: str = "http://lenovo-legion-5.andygeor.ge:11434/api/generate", model: str = "hf.co/unsloth/Qwen3-4B-Thinking-2507-GGUF:Q8_0"):
        """
        Initialize the Pokemon creature generator.
        
        Args:
            ollama_url: URL of your Ollama instance
            model: The model to use in Ollama
        """
        self.ollama_url = ollama_url
        self.model = model
        self.creatures = []
        self.current_generation = 0
        
    def query_ollama(self, prompt: str) -> str:
        """
        Send a query to Ollama and return the response.
        
        Args:
            prompt: The prompt to send to Ollama
            
        Returns:
            The response from Ollama
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(self.ollama_url, json=payload)
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.exceptions.RequestException as e:
            print(f"Error querying Ollama: {e}")
            return ""
    
    def generate_creature(self, base_prompt: Optional[str] = None, evolution: Optional[Dict] = None) -> Dict:
        """
        Generate a new Pokemon-like creature.
        
        Args:
            base_prompt: Optional custom prompt
            evolution: Optional evolution data to base the new creature on
            
        Returns:
            A dictionary representing the generated creature
        """
        self.current_generation += 1
        
        if evolution:
            # Generate an evolution of an existing creature
            prompt = f"""
            Create an evolution of this Pokemon-like creature:
            
            Name: {evolution['name']}
            Type: {evolution['type']}
            Description: {evolution['description']}
            Abilities: {evolution['abilities']}
            Stats: {evolution['stats']}
            
            The evolution should be stronger and have some visual changes.
            Provide the response in JSON format with these fields: name, type, description, abilities (array), stats (hp, attack, defense, speed), and evolution_level.
            """
        else:
            # Generate a new creature from scratch
            prompt = base_prompt or f"""
            Create a unique Pokemon-like creature with the following characteristics:
            - A creative name
            - One or two types (e.g., Fire, Water, Grass, Electric, Psychic, etc.)
            - A brief description of its appearance and behavior
            - 2-3 special abilities
            - Stats: HP, Attack, Defense, Speed (values between 30-100)
            
            Provide the response in JSON format with these fields: name, type, description, abilities (array), stats (hp, attack, defense, speed).
            """
        
        response = self.query_ollama(prompt)
        
        # Try to parse the response as JSON
        try:
            # Sometimes the model might add extra text, so we'll try to extract JSON
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].strip()
            else:
                json_str = response.strip()
                
            creature_data = json.loads(json_str)
            
            # Add some metadata
            creature_data["id"] = len(self.creatures) + 1
            creature_data["generation"] = self.current_generation
            
            # Ensure we have all required fields
            if "stats" not in creature_data:
                creature_data["stats"] = {
                    "hp": random.randint(30, 100),
                    "attack": random.randint(30, 100),
                    "defense": random.randint(30, 100),
                    "speed": random.randint(30, 100)
                }
                
            if "abilities" not in creature_data:
                creature_data["abilities"] = ["Tackle", "Growl"]
                
            self.creatures.append(creature_data)
            return creature_data
            
        except json.JSONDecodeError:
            print("Failed to parse JSON from response. Raw response:")
            print(response)
            
            # Return a fallback creature
            return {
                "id": len(self.creatures) + 1,
                "name": f"Creature-{len(self.creatures) + 1}",
                "type": "Unknown",
                "description": "A mysterious creature that couldn't be properly generated.",
                "abilities": ["Tackle"],
                "stats": {
                    "hp": 50,
                    "attack": 50,
                    "defense": 50,
                    "speed": 50
                },
                "generation": self.current_generation
            }
    
    def generate_battle_scenario(self, creature1_id: int, creature2_id: int) -> str:
        """
        Generate a battle scenario between two creatures.
        
        Args:
            creature1_id: ID of the first creature
            creature2_id: ID of the second creature
            
        Returns:
            A description of the battle scenario
        """
        creature1 = self.get_creature_by_id(creature1_id)
        creature2 = self.get_creature_by_id(creature2_id)
        
        if not creature1 or not creature2:
            return "One or both creatures not found."
            
        prompt = f"""
        Create a brief battle scenario between these two Pokemon-like creatures:
        
        Creature 1:
        Name: {creature1['name']}
        Type: {creature1['type']}
        Abilities: {creature1['abilities']}
        Stats: {creature1['stats']}
        
        Creature 2:
        Name: {creature2['name']}
        Type: {creature2['type']}
        Abilities: {creature2['abilities']}
        Stats: {creature2['stats']}
        
        Describe how the battle would play out, considering their types, abilities, and stats.
        """
        
        return self.query_ollama(prompt)
    
    def evolve_creature(self, creature_id: int) -> Optional[Dict]:
        """
        Evolve an existing creature.
        
        Args:
            creature_id: ID of the creature to evolve
            
        Returns:
            The evolved creature or None if the original creature wasn't found
        """
        creature = self.get_creature_by_id(creature_id)
        if not creature:
            return None
            
        # Generate the evolution
        evolution = self.generate_creature(evolution=creature)
        
        # Link the evolution to the original
        evolution["evolved_from"] = creature_id
        
        return evolution
    
    def get_creature_by_id(self, creature_id: int) -> Optional[Dict]:
        """
        Get a creature by its ID.
        
        Args:
            creature_id: ID of the creature
            
        Returns:
            The creature dictionary or None if not found
        """
        for creature in self.creatures:
            if creature["id"] == creature_id:
                return creature
        return None
    
    def save_creatures(self, filename: str = "pokemon_creatures.json"):
        """
        Save all generated creatures to a JSON file.
        
        Args:
            filename: The filename to save to
        """
        with open(filename, "w") as f:
            json.dump(self.creatures, f, indent=2)
        print(f"Saved {len(self.creatures)} creatures to {filename}")
    
    def load_creatures(self, filename: str = "pokemon_creatures.json"):
        """
        Load creatures from a JSON file.
        
        Args:
            filename: The filename to load from
        """
        try:
            with open(filename, "r") as f:
                self.creatures = json.load(f)
            print(f"Loaded {len(self.creatures)} creatures from {filename}")
            
            # Update current_generation based on loaded data
            if self.creatures:
                self.current_generation = max(c["generation"] for c in self.creatures)
        except FileNotFoundError:
            print(f"File {filename} not found. Starting with empty creature list.")
            self.creatures = []
            self.current_generation = 0
    
    def print_creature(self, creature: Dict):
        """
        Print a creature in a formatted way.
        
        Args:
            creature: The creature dictionary to print
        """
        print(f"ID: {creature['id']}")
        print(f"Name: {creature['name']}")
        print(f"Type: {creature['type']}")
        print(f"Description: {creature['description']}")
        print("Abilities:")
        for ability in creature['abilities']:
            print(f"  - {ability}")
        print("Stats:")
        for stat, value in creature['stats'].items():
            print(f"  - {stat.capitalize()}: {value}")
        if "evolved_from" in creature:
            print(f"Evolved from: Creature #{creature['evolved_from']}")
        print("-" * 40)

# Example usage
if __name__ == "__main__":
    # Initialize the generator
    generator = PokemonCreatureGenerator()
    
    # Try to load existing creatures
    generator.load_creatures()
    
    # Generate a few new creatures
    print("Generating new creatures...")
    for i in range(3):
        creature = generator.generate_creature()
        generator.print_creature(creature)
        time.sleep(1)  # Add a small delay to avoid overwhelming Ollama
    
    # Evolve one of the creatures
    if generator.creatures:
        print(f"Evolving creature #{generator.creatures[0]['id']}...")
        evolution = generator.evolve_creature(generator.creatures[0]['id'])
        if evolution:
            generator.print_creature(evolution)
    
    # Generate a battle scenario between the first two creatures
    if len(generator.creatures) >= 2:
        print("\nBattle scenario:")
        battle = generator.generate_battle_scenario(
            generator.creatures[0]['id'], 
            generator.creatures[1]['id']
        )
        print(battle)
    
    # Save all creatures
    generator.save_creatures()
