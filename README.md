# Pokemon-like Monster Generator with Ollama

An AI agent that queries your local Ollama instance to iteratively generate unique Pokemon-like battling monsters with stats, abilities, and evolution chains.

## Features

- 🎮 Generate unique monster characters with stats and abilities
- 🔗 Create complete evolution chains (3 stages)
- 🎨 Generate themed collections and regions
- ⭐ Create legendary and starter monsters
- 💾 Save and load monster data as JSON
- 🔄 Iterative generation with context awareness

## Prerequisites

1. **Install Ollama**: Download from [ollama.ai](https://ollama.ai)

2. **Pull a model** (choose one):
   ```bash
   ollama pull llama3.2      # Recommended
   ollama pull mistral       # Alternative
   ollama pull phi           # Lighter option
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

### Basic Usage

Generate a batch of monsters:

```bash
python monster_generator.py
```

This will:
- Generate 3 monsters with a "volcanic" theme
- Display their stats and abilities
- Save them to `monsters.json`

### Advanced Examples

**1. Generate Evolution Chains:**
```bash
python advanced_generator.py chains
```

**2. Create a Themed Region:**
```bash
python advanced_generator.py region
```

**3. Build a Competitive Team:**
```bash
python advanced_generator.py team
```

## Usage Examples

### Generate Custom Monsters

```python
from monster_generator import OllamaMonsterGenerator

# Initialize the generator
generator = OllamaMonsterGenerator(
    base_url="http://localhost:11434",
    model="llama3.2"
)

# Generate a single monster
monster = generator.generate_monster(theme="electric")
generator.display_monster(monster)

# Generate a batch
generator.generate_batch(count=5, theme="aquatic", delay=2.0)

# Save results
generator.save_monsters("my_monsters.json")
```

### Generate Evolution Chains

```python
from advanced_generator import AdvancedMonsterGenerator

generator = AdvancedMonsterGenerator(model="llama3.2")

# Create a 3-stage evolution chain
chain = generator.generate_evolution_chain("fire dragon", stages=3)

for monster in chain:
    print(f"Stage {monster.evolution_stage}: {monster.name}")
```

### Generate Starter Trio

```python
generator = AdvancedMonsterGenerator(model="llama3.2")
generator.generate_starter_trio()  # Grass, Fire, Water starters
```

### Create Legendary Monsters

```python
generator = AdvancedMonsterGenerator(model="llama3.2")
legendary = generator.generate_legendary("time and space manipulation")
```

## Configuration

### Change Ollama Model

Edit the `model` parameter:

```python
generator = OllamaMonsterGenerator(
    model="mistral"  # or "phi", "llama3.2", etc.
)
```

### Change Ollama URL

If running Ollama on a different machine:

```python
generator = OllamaMonsterGenerator(
    base_url="http://192.168.1.100:11434"
)
```

### Adjust Temperature

Higher temperature = more creative/random:

```python
# In the query_ollama method, change temperature
response = self.query_ollama(prompt, temperature=0.9)  # 0.0-1.0
```

## Monster Data Structure

Each monster has:

```python
{
    "name": "Flamewyrm",
    "type": "Fire/Dragon",
    "description": "A serpentine dragon wreathed in eternal flames",
    "stats": {
        "HP": 130,
        "Attack": 105,
        "Defense": 85,
        "Speed": 95,
        "Special": 110
    },
    "abilities": [
        "Inferno Breath",
        "Dragon Dance", 
        "Flame Body"
    ],
    "evolution_stage": 3,
    "rarity": "Rare"
}
```

## Tips for Best Results

1. **Use descriptive themes**: Instead of "fire", try "volcanic phoenix" or "molten rock creature"

2. **Iterate with context**: The agent remembers recent monsters and tries to create different ones

3. **Adjust temperature**:
   - Lower (0.5-0.7): More consistent, balanced monsters
   - Higher (0.8-1.0): More creative, unusual monsters

4. **Use evolution chains**: They maintain thematic consistency better than individual generations

5. **Specify stat priorities**: Add "high speed" or "defensive tank" to themes for specialized monsters

## Customization Ideas

### Add New Monster Types
```python
CUSTOM_TYPES = ["Ghost", "Fairy", "Steel", "Fighting", "Poison"]
```

### Create Type Matchups
```python
def get_type_effectiveness(attacker_type, defender_type):
    matchups = {
        "Fire": {"weak_to": ["Water", "Rock"], "strong_against": ["Grass", "Ice"]},
        # ... add more
    }
```

### Implement Battle System
```python
class Battle:
    def calculate_damage(self, attacker, defender, move):
        # Implement damage calculation
        pass
```

### Add Image Generation
Integrate with DALL-E or Stable Diffusion:
```python
def generate_monster_image(monster):
    prompt = f"pixel art pokemon style: {monster.description}"
    # Call image generation API
```

## Troubleshooting

### Ollama Connection Error
```
Error querying Ollama: [Errno 61] Connection refused
```
**Solution**: Make sure Ollama is running:
```bash
ollama serve
```

### Parsing Failures
If monsters aren't parsing correctly:
1. Try a different model (llama3.2 works best)
2. Increase retries in `generate_monster()`
3. Adjust the prompt structure in `create_generation_prompt()`

### Slow Generation
- Reduce `num_predict` in `query_ollama()`
- Use a smaller model like `phi`
- Reduce the batch size

## Project Structure

```
├── monster_generator.py      # Core generator class
├── advanced_generator.py     # Evolution chains & themed collections  
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── monsters.json            # Generated monsters (created after running)
└── examples/
    ├── evolution_chains.json
    ├── volcanic_region.json
    └── competitive_team.json
```

## Next Steps

- [ ] Add type effectiveness chart
- [ ] Implement battle simulation
- [ ] Create monster breeding system
- [ ] Add move/attack generation
- [ ] Generate sprite descriptions
- [ ] Create web UI for monster browsing
- [ ] Add database storage (SQLite)
- [ ] Implement rarity-based stat scaling

## Contributing

Feel free to extend this with:
- New generation strategies
- Battle mechanics
- Type systems
- Evolution mechanics
- Trading/breeding systems

## License

Free to use and modify for your projects!
