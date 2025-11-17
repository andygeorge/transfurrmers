import requests
import json
import random
import time
import os
import signal
import sys
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
        self.battles = []
        self.champion = None
        self.running = True
        
        # Set up signal handler for graceful exit
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def signal_handler(self, sig, frame):
        """Handle Ctrl+C to exit gracefully."""
        print("\nReceived interrupt signal. Saving data and exiting...")
        self.running = False
        
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
    
    def generate_creature(self, base_prompt: Optional[str] = None, difficulty: int = 1) -> Dict:
        """
        Generate a new Pokemon-like creature.
        
        Args:
            base_prompt: Optional custom prompt
            difficulty: Difficulty level (1-5) to influence creature strength
            
        Returns:
            A dictionary representing the generated creature
        """
        self.current_generation += 1
        
        # Adjust the prompt based on difficulty
        difficulty_modifier = ""
        if difficulty >= 2:
            difficulty_modifier = f"Make this creature moderately powerful (difficulty {difficulty}/5). "
        if difficulty >= 3:
            difficulty_modifier = f"Make this creature strong (difficulty {difficulty}/5). "
        if difficulty >= 4:
            difficulty_modifier = f"Make this creature very strong (difficulty {difficulty}/5). "
        if difficulty >= 5:
            difficulty_modifier = f"Make this creature extremely powerful, a true champion (difficulty {difficulty}/5). "
            
        prompt = base_prompt or f"""
        Create a unique Pokemon-like creature with the following characteristics:
        - A creative name
        - One or two types (e.g., Fire, Water, Grass, Electric, Psychic, etc.)
        - A brief description of its appearance and behavior
        - 2-3 special abilities
        - Stats: HP, Attack, Defense, Speed (values between 30-100)
        
        {difficulty_modifier}
        
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
                
            # Add battle stats
            creature_data["wins"] = 0
            creature_data["losses"] = 0
            creature_data["total_battles"] = 0
            
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
                "generation": self.current_generation,
                "wins": 0,
                "losses": 0,
                "total_battles": 0
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
        Battle Record: {creature1.get('wins', 0)} wins, {creature1.get('losses', 0)} losses
        
        Creature 2:
        Name: {creature2['name']}
        Type: {creature2['type']}
        Abilities: {creature2['abilities']}
        Stats: {creature2['stats']}
        Battle Record: {creature2.get('wins', 0)} wins, {creature2.get('losses', 0)} losses
        
        Consider type advantages, stats, abilities, and battle experience in your simulation.
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
            
            # Update battle records
            if battle_result["winner"] == creature1["name"]:
                creature1["wins"] = creature1.get("wins", 0) + 1
                creature2["losses"] = creature2.get("losses", 0) + 1
            else:
                creature2["wins"] = creature2.get("wins", 0) + 1
                creature1["losses"] = creature1.get("losses", 0) + 1
                
            creature1["total_battles"] = creature1.get("total_battles", 0) + 1
            creature2["total_battles"] = creature2.get("total_battles", 0) + 1
            
            return battle_result
            
        except json.JSONDecodeError:
            print("Failed to parse battle JSON from response. Raw response:")
            print(response)
            
            # Return a fallback battle result
            winner = creature1["name"] if creature1["stats"]["attack"] > creature2["stats"]["attack"] else creature2["name"]
            
            # Update battle records
            if winner == creature1["name"]:
                creature1["wins"] = creature1.get("wins", 0) + 1
                creature2["losses"] = creature2.get("losses", 0) + 1
            else:
                creature2["wins"] = creature2.get("wins", 0) + 1
                creature1["losses"] = creature1.get("losses", 0) + 1
                
            creature1["total_battles"] = creature1.get("total_battles", 0) + 1
            creature2["total_battles"] = creature2.get("total_battles", 0) + 1
            
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
        
    def save_battles_to_json(self, filename: str = "pokemon_battles.json"):
        """
        Save all battle results to a JSON file.
        
        Args:
            filename: The filename to save to
        """
        with open(filename, "w") as f:
            json.dump(self.battles, f, indent=2)
        print(f"Saved {len(self.battles)} battles to {filename}")
    
    def print_creature(self, creature: Dict, is_champion: bool = False):
        """
        Print a creature in a formatted way.
        
        Args:
            creature: The creature dictionary to print
            is_champion: Whether this creature is the current champion
        """
        if is_champion:
            print("🏆 CURRENT CHAMPION 🏆")
            print("=" * 40)
            
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
        print("Battle Record:")
        print(f"  - Wins: {creature.get('wins', 0)}")
        print(f"  - Losses: {creature.get('losses', 0)}")
        print(f"  - Total Battles: {creature.get('total_battles', 0)}")
        
        if is_champion:
            print("=" * 40)
        else:
            print("-" * 40)
    
    def print_battle(self, battle_result: Dict):
        """
        Print a battle result in a formatted way.
        
        Args:
            battle_result: The battle result dictionary
        """
        print(f"\n⚔️ BATTLE #{len(self.battles) + 1} ⚔️")
        print("-" * 40)
        
        for i, log_entry in enumerate(battle_result["battle_log"], 1):
            print(f"Turn {i}: {log_entry}")
            
        print("-" * 40)
        print(f"🏆 Winner: {battle_result['winner']} after {battle_result['turns']} turns!")
        print(f"Battle took place on {battle_result['timestamp']}")
        print("-" * 40)
    
    def run_tournament(self):
        """
        Run an infinite tournament where the champion battles against increasingly powerful challengers.
        """
        print("🎮 POKEMON CREATURE EVOLUTION TOURNAMENT 🎮")
        print("=" * 50)
        print("Generating initial creatures...")
        
        # Generate the first two creatures
        creature1 = self.generate_creature(difficulty=2)
        creature2 = self.generate_creature(difficulty=2)
        
        print("\nInitial creatures:")
        self.print_creature(creature1)
        self.print_creature(creature2)
        
        # Battle them to determine the first champion
        print("\nFirst battle to determine the champion:")
        battle_result = self.simulate_battle(creature1, creature2)
        self.print_battle(battle_result)
        self.battles.append(battle_result)
        
        # Set the champion
        if battle_result["winner"] == creature1["name"]:
            self.champion = creature1
        else:
            self.champion = creature2
            
        print(f"\n{self.champion['name']} is the first champion!")
        self.print_creature(self.champion, is_champion=True)
        
        # Start the infinite tournament
        battle_count = 1
        difficulty = 2
        
        while self.running:
            battle_count += 1
            
            # Gradually increase difficulty
            if battle_count % 5 == 0 and difficulty < 5:
                difficulty += 1
                print(f"\n⚠️ DIFFICULTY INCREASED TO {difficulty}/5! ⚠️")
            
            print(f"\nGenerating challenger #{battle_count} (Difficulty: {difficulty}/5)...")
            challenger = self.generate_creature(difficulty=difficulty)
            self.print_creature(challenger)
            
            print(f"\nBattle #{battle_count}: Champion vs Challenger")
            battle_result = self.simulate_battle(self.champion, challenger)
            self.print_battle(battle_result)
            self.battles.append(battle_result)
            
            # Check if the champion was defeated
            if battle_result["winner"] != self.champion["name"]:
                print(f"\n💀 The champion {self.champion['name']} has been defeated by {challenger['name']}!")
                print(f"The champion had {self.champion.get('wins', 0)} victories.")
                
                # Set the new champion
                self.champion = challenger
                print(f"\n🏆 {self.champion['name']} is the new champion!")
                self.print_creature(self.champion, is_champion=True)
            else:
                print(f"\n✅ The champion {self.champion['name']} defends their title!")
                print(f"The champion now has {self.champion.get('wins', 0)} victories.")
                
            # Save progress every 5 battles
            if battle_count % 5 == 0:
                self.save_creatures_to_json()
                self.save_battles_to_json()
                print(f"\n💾 Progress saved after {battle_count} battles.")
                
            # Small delay to prevent overwhelming Ollama
            time.sleep(1)
            
        # Save final state
        self.save_creatures_to_json()
        self.save_battles_to_json()
        print(f"\nFinal state saved after {battle_count} battles.")
        print(f"The final champion was {self.champion['name']} with {self.champion.get('wins', 0)} victories.")

# Example usage
if __name__ == "__main__":
    # Initialize the generator with environment variables from .env
    generator = PokemonCreatureGenerator()
    
    # Run the tournament
    generator.run_tournament()