import requests
import json
import random
import time
import os
from typing import Dict, List, Optional

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not installed. Using default values or environment variables.")
    print("To install: pip install python-dotenv")

class PokemonCreatureGenerator:
    def __init__(self, ollama_url: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the Pokemon creature generator.
        
        Args:
            ollama_url: URL of your Ollama instance (will use OLLAMA_HOST from .env if not provided)
            model: The model to use in Ollama (will use OLLAMA_MODEL from .env if not provided)
        """
        # Use provided values, environment variables, or defaults
        self.ollama_url = ollama_url or os.getenv("OLLAMA_HOST", "http://localhost:11434/api/generate")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama2")
        
        print(f"Using Ollama URL: {self.ollama_url}")
        print(f"Using model: {self.model}")
        
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
    
    def generate_creature(self, base_prompt: Optional[str] = None) -> Dict:
        """
        Generate a new Pokemon-like creature.
        
        Args:
            base_prompt: Optional custom prompt
            
        Returns:
            A dictionary representing the generated creature
        """
        self.current_generation += 1
        
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
    
    def simulate_battle(self, creature1: Dict, creature2: Dict) -> Dict:
        """
        Simulate a battle between two creatures by sending their stats to Ollama.
        
        Args:
            creature1: The first creature
            creature2: The second creature
            
        Returns:
            A dictionary containing the battle result
        """
        prompt = f"""
        Simulate a turn-by-turn battle between these two Pokemon-like creatures:
        
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
        
        Consider type advantages, stats, and abilities in your simulation.
        Describe the battle in 3-5 turns, showing damage dealt and any special effects.
        Declare a winner at the end.
        
        Provide the response in JSON format with these fields:
        - battle_log: array of strings describing each turn
        - winner: name of the winning creature
        - turns: number of turns the battle lasted
        """
        
        response = self.query_ollama(prompt)
        
        try:
            # Extract JSON from the response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].strip()
            else:
                json_str = response.strip()
                
            battle_result = json.loads(json_str)
            
            # Add metadata
            battle_result["creature1_id"] = creature1["id"]
            battle_result["creature2_id"] = creature2["id"]
            battle_result["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
            
            return battle_result
            
        except json.JSONDecodeError:
            print("Failed to parse battle JSON from response. Raw response:")
            print(response)
            
            # Return a fallback battle result
            winner = creature1["name"] if creature1["stats"]["attack"] > creature2["stats"]["attack"] else creature2["name"]
            return {
                "battle_log": [
                    f"{creature1['name']} attacks {creature2['name']}!",
                    f"{creature2['name']} retaliates!",
                    f"The battle is intense!"
                ],
                "winner": winner,
                "turns": 3,
                "creature1_id": creature1["id"],
                "creature2_id": creature2["id"],
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def save_creatures_to_json(self, filename: str = "pokemon_creatures.json"):
        """
        Save all generated creatures to a JSON file.
        
        Args:
            filename: The filename to save to
        """
        with open(filename, "w") as f:
            json.dump(self.creatures, f, indent=2)
        print(f"Saved {len(self.creatures)} creatures to {filename}")
        
    def save_battle_to_json(self, battle_result: Dict, filename: str = "pokemon_battles.json"):
        """
        Save a battle result to a JSON file.
        
        Args:
            battle_result: The battle result dictionary
            filename: The filename to save to
        """
        battles = []
        
        # Try to load existing battles
        try:
            with open(filename, "r") as f:
                battles = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            battles = []
            
        # Add the new battle
        battles.append(battle_result)
        
        # Save all battles
        with open(filename, "w") as f:
            json.dump(battles, f, indent=2)
        print(f"Saved battle to {filename}")
    
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
        print("-" * 40)
    
    def print_battle(self, battle_result: Dict):
        """
        Print a battle result in a formatted way.
        
        Args:
            battle_result: The battle result dictionary
        """
        print(f"\nBattle between Creature #{battle_result['creature1_id']} and Creature #{battle_result['creature2_id']}:")
        print("-" * 40)
        
        for i, log_entry in enumerate(battle_result["battle_log"], 1):
            print(f"Turn {i}: {log_entry}")
            
        print("-" * 40)
        print(f"Winner: {battle_result['winner']} after {battle_result['turns']} turns!")
        print(f"Battle took place on {battle_result['timestamp']}")
        print("-" * 40)

# Example usage
if __name__ == "__main__":
    # Initialize the generator with environment variables from .env
    generator = PokemonCreatureGenerator()
    
    # Generate two creatures
    print("Generating two creatures for battle...")
    creature1 = generator.generate_creature()
    generator.print_creature(creature1)
    time.sleep(1)  # Add a small delay to avoid overwhelming Ollama
    
    creature2 = generator.generate_creature()
    generator.print_creature(creature2)
    time.sleep(1)
    
    # Save creatures to JSON
    generator.save_creatures_to_json()
    
    # Simulate a battle between the two creatures
    print("\nSimulating battle...")
    battle_result = generator.simulate_battle(creature1, creature2)
    generator.print_battle(battle_result)
    
    # Save the battle result to JSON
    generator.save_battle_to_json(battle_result)
    