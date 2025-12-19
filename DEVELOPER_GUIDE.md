# Zombie Quest: Developer Guide

Complete technical documentation for extending and modifying Zombie Quest.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Module Responsibilities](#module-responsibilities)
- [Data Flow](#data-flow)
- [How to Add New Rooms](#how-to-add-new-rooms)
- [How to Add New Items](#how-to-add-new-items)
- [How to Add New Dialogue](#how-to-add-new-dialogue)
- [How to Add New Puzzles](#how-to-add-new-puzzles)
- [How to Add New Zombies](#how-to-add-new-zombies)
- [Audio System Guide](#audio-system-guide)
- [Visual Effects System](#visual-effects-system)
- [Testing Procedures](#testing-procedures)
- [Common Development Tasks](#common-development-tasks)
- [Performance Optimization](#performance-optimization)

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────┐
│                   main.py                       │
│              (Entry Point)                      │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│               GameEngine                        │
│  (zombie_quest/engine.py)                       │
│  - Main game loop                               │
│  - State management                             │
│  - Event handling                               │
└──┬──────────┬──────────┬──────────┬────────────┘
   │          │          │          │
   ▼          ▼          ▼          ▼
┌──────┐  ┌──────┐  ┌──────┐  ┌──────────┐
│Rooms │  │ UI   │  │Audio │  │Characters│
└──┬───┘  └──┬───┘  └──┬───┘  └──┬───────┘
   │         │         │         │
   ▼         ▼         ▼         ▼
┌──────────────────────────────────────┐
│        Supporting Systems             │
│  - Pathfinding (A*)                  │
│  - Dialogue Trees                    │
│  - Visual Effects                    │
│  - Data Loading                      │
│  - Save/Load                         │
└──────────────────────────────────────┘
```

### Component Interaction Diagram

```
     Player Input
          │
          ▼
    ┌──────────┐
    │  Engine  │◄─────── Config
    └────┬─────┘
         │
    ┌────┴────┬────────┬─────────┐
    ▼         ▼        ▼         ▼
  Room       UI      Audio    Effects
    │         │        │         │
    ▼         │        │         │
Characters    │        │         │
    │         │        │         │
    ▼         ▼        ▼         ▼
  ┌────────────────────────────────┐
  │      Rendering Pipeline        │
  │  (Pygame Surface Composition)  │
  └────────────────────────────────┘
```

---

## Module Responsibilities

### Core Modules

#### `engine.py`
**Purpose**: Main game engine and state machine

**Key Classes**:
- `GameEngine`: Main game loop, event handling, state management

**Responsibilities**:
- Run game loop at 60 FPS
- Handle keyboard/mouse input
- Manage game states (PLAYING, PAUSED, DIALOGUE, etc.)
- Coordinate updates between all systems
- Handle room transitions

**Dependencies**: rooms, characters, ui, audio, effects, dialogue

---

#### `rooms.py`
**Purpose**: Room and hotspot management

**Key Classes**:
- `Room`: Room container with hotspots, zombies, and backgrounds
- `Hotspot`: Interactive objects within rooms

**Responsibilities**:
- Define walkable/priority zones
- Manage hotspots and their verbs
- Handle pathfinding integration
- Draw room backgrounds and characters

**Data Format**: Loads from `game_data.json`

---

#### `characters.py`
**Purpose**: Player and zombie AI

**Key Classes**:
- `Hero`: Player character with movement and health
- `Zombie`: Enemy AI with music response system
- `ZombieSpawner`: Factory for creating zombies

**Responsibilities**:
- Player pathfinding and keyboard movement
- Zombie AI (wander, chase, music response)
- Health and damage system
- Character animations

**Key Features**:
- Music-responsive zombie states
- A* pathfinding integration
- Invincibility frames
- Squash/stretch animation

---

#### `ui.py`
**Purpose**: User interface components

**Key Classes**:
- `VerbBar`: Verb selection bar
- `MessageBox`: Text display with typewriter effect
- `Inventory`: Item management
- `InventoryWindow`: Item display UI
- `PauseMenu`: Pause menu overlay

**Responsibilities**:
- Render all UI elements
- Handle UI input (mouse/keyboard)
- Display health hearts
- Inventory management

---

#### `audio.py`
**Purpose**: Procedural audio synthesis and spatial audio

**Key Classes**:
- `AudioManager`: Master audio controller
- `WaveformGenerator`: Synthesize waveforms
- `ProceduralMusicLayer`: Dynamic music layers
- `SpatialAudio`: 3D audio positioning
- `AudioEventSystem`: Event-driven audio

**Responsibilities**:
- Synthesize all sound effects
- Generate procedural music
- Spatial audio with distance attenuation
- Room-specific ambient soundscapes
- Tension-based music layering

---

#### `dialogue.py`
**Purpose**: Branching dialogue system

**Key Classes**:
- `DialogueTree`: Complete conversation tree
- `DialogueNode`: Single dialogue node
- `DialogueChoice`: Player choice option
- `DialogueManager`: Active dialogue renderer

**Responsibilities**:
- Parse dialogue trees
- Manage conversation state
- Check requirements (items/flags)
- Apply effects (give items, set flags)
- Render dialogue UI

---

#### `data_loader.py`
**Purpose**: JSON data parsing

**Functions**:
- `load_game_data()`: Load main game JSON
- `build_rooms()`: Create Room objects from data
- `build_items()`: Create Item objects from data

**Responsibilities**:
- Parse JSON configuration
- Validate data structure
- Convert data to game objects

---

### Supporting Modules

#### `pathfinding.py`
**Purpose**: A* pathfinding algorithm

**Key Classes**:
- `GridPathfinder`: A* implementation with walkable mask

**Responsibilities**:
- Find optimal paths through rooms
- Respect walkable zones
- Optimize for performance

---

#### `effects.py`
**Purpose**: Visual effects and screen transitions

**Key Classes**:
- `ParticleSystem`: Particle emitter
- `ScreenTransition`: Fade effects
- `GlowEffect`: Screen glow pulses
- `ScreenShake`: Camera shake
- `ScanlineOverlay`: CRT scanline effect

**Responsibilities**:
- Manage particle lifecycle
- Render visual effects
- Create screen transitions
- Add retro visual polish

---

#### `config.py`
**Purpose**: Centralized configuration

**Classes**:
- `DisplayConfig`: Window and rendering settings
- `GameplayConfig`: Game mechanics constants
- `AnimationConfig`: Animation timing
- `AudioConfig`: Audio volumes
- `ColorPalette`: Game color scheme
- `GameState`: State machine enum

**Responsibilities**:
- Eliminate magic numbers
- Centralize tuning parameters
- Define color palette

---

#### `resources.py`
**Purpose**: Asset loading and font management

**Functions**:
- `load_serif_font()`: Load bitmap font
- `create_placeholder_background()`: Generate backgrounds
- `create_walkable_mask()`: Generate collision masks

**Responsibilities**:
- Load fonts and assets
- Create procedural backgrounds
- Generate collision geometry

---

#### `sprites.py`
**Purpose**: Pixel art sprite generation

**Functions**:
- `create_hero_animations()`: Generate hero sprites
- `create_zombie_animations()`: Generate zombie sprites
- `create_verb_icon()`: Create UI icons
- `create_heart_icon()`: Create health icons

**Responsibilities**:
- Procedurally generate all sprites
- Create animation frames
- Apply visual effects to sprites

---

#### `backgrounds.py`
**Purpose**: Detailed room backgrounds

**Functions**:
- `get_room_background()`: Generate room-specific backgrounds

**Responsibilities**:
- Create visually distinct rooms
- Apply lighting effects
- Generate geometric shapes

---

### Extended Modules

#### `diegetic_audio.py`
**Purpose**: In-game music sources that affect zombies

**Key Classes**:
- `DiegeticAudioManager`: Manage music sources
- `MusicSource`: Individual music emitter

**Responsibilities**:
- Create music zones from musical items
- Calculate music intensity at positions
- Apply music effects to zombies

---

#### `dialogue.py` (Extended)
**Pre-built Dialogues**:
- `create_clerk_dialogue()`: Record store clerk tree
- `create_dj_dialogue()`: DJ Rotten tree
- `create_maya_dialogue()`: Maya ending tree

---

#### `save_system.py`
**Purpose**: Save and load game state

**Key Classes**:
- `SaveSystem`: Serialization manager

**Responsibilities**:
- Save game state to file
- Load saved games
- Validate save data

---

#### `memory.py`
**Purpose**: Progressive examination system

**Key Classes**:
- `MemorySystem`: Track hotspot visits

**Responsibilities**:
- Record examination counts
- Trigger memories on repeated visits
- Generate progressive text

---

#### `item_combinations.py`
**Purpose**: Item crafting system

**Key Classes**:
- `ItemCombiner`: Manage combination recipes

**Responsibilities**:
- Define item recipes
- Check combination validity
- Create new items from combinations

---

## Data Flow

### Game Loop Data Flow

```
Input Events
     │
     ▼
┌──────────────┐
│handle_events()│
└───────┬──────┘
        │
        ▼
┌──────────────┐
│   update()   │ ◄─── dt (delta time)
│              │
│ - Hero      │
│ - Zombies   │
│ - Effects   │
│ - UI        │
│ - Audio     │
└───────┬──────┘
        │
        ▼
┌──────────────┐
│    draw()    │
│              │
│ - Room      │
│ - Characters│
│ - Particles │
│ - UI        │
│ - Effects   │
└───────┬──────┘
        │
        ▼
   pygame.display.flip()
```

### Hotspot Interaction Flow

```
Player Clicks Object
        │
        ▼
┌────────────────────┐
│Find Hotspot at Pos│
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│Set Path to Hotspot│
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│  Hero Walks There  │
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│Perform Action      │
│(Look/Use/Talk)     │
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│ - Check Items      │
│ - Show Message     │
│ - Give Items       │
│ - Transition Room  │
│ - Start Dialogue   │
└────────────────────┘
```

---

## How to Add New Rooms

### Step 1: Define Room in `game_data.json`

```json
{
  "rooms": [
    {
      "id": "new_room",
      "name": "New Room Name",
      "entry_message": "You enter a mysterious new location.",
      "default_entry": [160, 180],
      "size": [320, 200],

      "background": {
        "label": "New Room",
        "gradient": [[40, 20, 60], [80, 50, 120], [30, 10, 50]],
        "accent_lines": [
          {"y": 120, "height": 4, "color": [255, 100, 150]}
        ],
        "shapes": [
          {"shape": "rect", "rect": [50, 80, 100, 60], "color": [80, 80, 100]}
        ]
      },

      "walkable_zones": [
        {
          "shape": "polygon",
          "points": [[20, 180], [300, 180], [300, 195], [20, 195]]
        }
      ],

      "hotspots": [
        {
          "name": "Door",
          "rect": [140, 80, 40, 60],
          "walk_position": [160, 170],
          "verbs": {
            "look": "A mysterious door.",
            "use": "You open the door."
          },
          "target_room": "another_room",
          "transition_verb": "use"
        }
      ],

      "zombies": [
        {"position": [100, 160], "type": "scene"}
      ]
    }
  ]
}
```

### Step 2: Create Room Background (Optional)

Edit `zombie_quest/backgrounds.py`:

```python
def get_room_background(room_id: str, size: Tuple[int, int]) -> Optional[pygame.Surface]:
    """Generate detailed backgrounds for specific rooms."""

    if room_id == "new_room":
        # Custom background generation
        surf = pygame.Surface(size)
        # ... draw custom background ...
        return surf

    # ... existing rooms ...
```

### Step 3: Add Room Ambience (Optional)

Edit `zombie_quest/audio.py`:

```python
def _generate_ambient_soundscapes(self) -> None:
    """Generate ambient soundscapes for each room."""

    # New room ambience
    self.ambience_sounds['new_room'] = self._synth_new_room_ambience()

    # ... existing rooms ...

def _synth_new_room_ambience(self) -> Optional[pygame.mixer.Sound]:
    """Custom ambient sound for new room."""
    def gen(t, dur):
        # Generate custom ambient audio
        return 0.0  # Placeholder

    return self._create_sound_buffer(3.0, gen)
```

### Step 4: Test

```bash
python main.py
```

Navigate to the new room and verify:
- Background renders correctly
- Walkable zones work
- Hotspots are interactive
- Zombies spawn and behave correctly
- Ambient audio plays

---

## How to Add New Items

### Step 1: Define Item in `game_data.json`

```json
{
  "items": [
    {
      "name": "New Item",
      "description": "A mysterious new item with special properties.",
      "icon_color": [200, 100, 255]
    }
  ]
}
```

### Step 2: Add Item to Hotspot

Add to a hotspot's definition:

```json
{
  "name": "Item Pickup",
  "rect": [100, 100, 40, 40],
  "walk_position": [120, 150],
  "verbs": {
    "look": "A gleaming new item sits here.",
    "use": "You pick up the new item."
  },
  "give_item": "New Item",
  "give_item_triggers": ["use"]
}
```

### Step 3: Add Item Logic (If Needed)

Edit `zombie_quest/engine.py`:

```python
def perform_hotspot_action(self, hotspot: Hotspot, verb: Verb) -> None:
    # ... existing code ...

    # Special handling for new item
    if verb == Verb.USE and selected_item and selected_item.name == "New Item":
        # Custom logic for using the new item
        self.message_box.show("You use the new item!")
        self._apply_new_item_effect()
```

### Step 4: Create Item Icon (Optional)

Edit `zombie_quest/sprites.py`:

```python
def create_detailed_item_icon(name: str, color: Tuple[int, int, int],
                             size: int = 32) -> pygame.Surface:
    """Create detailed item icons."""

    if name == "New Item":
        # Custom icon generation
        icon = pygame.Surface((size, size), pygame.SRCALPHA)
        # ... draw custom icon ...
        return icon

    # ... default icon generation ...
```

---

## How to Add New Dialogue

### Step 1: Create Dialogue Tree

Edit `zombie_quest/dialogue.py`:

```python
def create_new_character_dialogue() -> DialogueTree:
    """Create dialogue tree for new character."""
    tree = DialogueTree("New Character")

    # Start node
    tree.add_node(DialogueNode(
        id="start",
        speaker="New Character",
        text="Hello, traveler. What brings you here?",
        choices=[
            DialogueChoice(
                text="Just passing through.",
                next_node="passing_through"
            ),
            DialogueChoice(
                text="I'm looking for something.",
                next_node="looking",
            ),
            DialogueChoice(
                text="[Give Item]",
                next_node="give_item",
                requirements=["Item Name"]
            )
        ]
    ))

    # Additional nodes
    tree.add_node(DialogueNode(
        id="passing_through",
        speaker="New Character",
        text="Safe travels, then.",
        choices=[]  # Ends dialogue
    ))

    tree.add_node(DialogueNode(
        id="looking",
        speaker="New Character",
        text="Aren't we all? What specifically?",
        choices=[
            DialogueChoice(
                text="Answers.",
                next_node="answers"
            )
        ]
    ))

    tree.add_node(DialogueNode(
        id="give_item",
        speaker="New Character",
        text="Ah, this is exactly what I needed! Take this reward.",
        choices=[],
        effects=[
            (DialogueEffect.REMOVE_ITEM, "Item Name"),
            (DialogueEffect.GIVE_ITEM, "Reward Item"),
            (DialogueEffect.SET_FLAG, "gave_item_to_npc")
        ]
    ))

    return tree
```

### Step 2: Register Dialogue Tree

Edit `zombie_quest/engine.py` in `__init__()`:

```python
self.dialogue_trees: Dict[str, object] = {
    "clerk": create_clerk_dialogue(),
    "dj": create_dj_dialogue(),
    "maya": create_maya_dialogue(),
    "new_character": create_new_character_dialogue(),  # Add this
}
```

### Step 3: Add Talk Hotspot

In `game_data.json`:

```json
{
  "name": "New Character",
  "rect": [200, 100, 50, 80],
  "walk_position": [225, 170],
  "talk_target": "new_character",
  "verbs": {
    "look": "A mysterious character stands here.",
    "talk": "You approach the character."
  }
}
```

### Dialogue Features

#### Requirements
Choices can require items or flags:

```python
DialogueChoice(
    text="[Show Badge]",
    next_node="show_badge",
    requirements=["Police Badge", "talked_to_mayor"]
)
```

#### Effects
Dialogue can trigger multiple effects:

```python
effects=[
    (DialogueEffect.GIVE_ITEM, "Reward"),
    (DialogueEffect.REMOVE_ITEM, "Quest Item"),
    (DialogueEffect.SET_FLAG, "quest_complete"),
    (DialogueEffect.HEAL, "1")
]
```

#### Conditional Nodes
Nodes can have conditions:

```python
DialogueNode(
    id="after_quest",
    speaker="Character",
    text="You've completed the quest!",
    conditions=["quest_complete"],
    choices=[]
)
```

---

## How to Add New Puzzles

### Puzzle Type 1: Item Exchange

**Pattern**: Give Item A to get Item B

**Implementation**:
```json
{
  "name": "Puzzle NPC",
  "talk_target": "npc_name",
  "verbs": {
    "use": "You offer the item.",
    "use_success": "The NPC accepts and gives you a reward!",
    "use_missing": "The NPC isn't interested in that."
  },
  "required_item": "Item A",
  "give_item": "Item B",
  "remove_item": "Item A",
  "give_item_triggers": ["use"],
  "remove_item_triggers": ["use"]
}
```

### Puzzle Type 2: Multi-Solution Puzzle

**Pattern**: Multiple items can solve the same puzzle

**Implementation**:
```json
{
  "name": "Locked Door",
  "required_item": "Key",
  "alternate_items": ["Lockpick", "Crowbar"],
  "verbs": {
    "use": "You try to open the door.",
    "use_success": "The door opens!",
    "use_missing": "The door is locked."
  },
  "target_room": "next_room",
  "transition_verb": "use",
  "requires_success_for_transition": true
}
```

### Puzzle Type 3: Item Combination

Edit `zombie_quest/item_combinations.py`:

```python
def __init__(self):
    self.recipes = [
        CombinationRecipe(
            inputs=["Item A", "Item B"],
            output="Combined Item",
            message="You combine the items!",
            flag="combined_items"
        )
    ]
```

### Puzzle Type 4: Flag-Gated Access

**Pattern**: Access requires completing previous steps

**Implementation**:
```json
{
  "name": "Secret Door",
  "required_flag": "found_secret",
  "verbs": {
    "look": "A hidden door!",
    "use": "You open the secret passage.",
    "use_missing": "The door won't budge."
  },
  "target_room": "secret_area",
  "transition_verb": "use"
}
```

### Puzzle Testing Checklist

- [ ] Can the puzzle be solved?
- [ ] Are all required items obtainable?
- [ ] Do failure messages make sense?
- [ ] Can the player get stuck?
- [ ] Are there multiple solutions?
- [ ] Do flags reset properly?

---

## How to Add New Zombies

### Step 1: Create Zombie Type

Edit `zombie_quest/characters.py`:

```python
def _get_music_affinities(self) -> Dict[str, float]:
    """Get music type affinities for this zombie type."""
    affinities = {
        'scene': { ... },
        'bouncer': { ... },
        'rocker': { ... },
        'dj': { ... },
        'new_type': {  # Add new type
            'new_wave': 1.2,
            'electronic': 1.5,
            'guitar': 0.7,
            'punk': 0.9,
            'ambient': 1.3
        }
    }
    return affinities.get(self.zombie_type, affinities['scene'])
```

### Step 2: Create Zombie Sprite

Edit `zombie_quest/sprites.py`:

```python
def create_zombie_animations(zombie_type: str = "scene",
                            scale: float = 2.5) -> Dict[str, List[pygame.Surface]]:
    """Create zombie animations for each direction."""

    # Define colors by zombie type
    zombie_colors = {
        'scene': {'base': (140, 200, 160), 'accent': (100, 160, 120)},
        'bouncer': {'base': (180, 140, 120), 'accent': (140, 100, 80)},
        'rocker': {'base': (200, 160, 140), 'accent': (160, 120, 100)},
        'dj': {'base': (160, 180, 200), 'accent': (120, 140, 160)},
        'new_type': {'base': (255, 100, 150), 'accent': (200, 50, 100)}  # Add this
    }

    # ... rest of sprite generation ...
```

### Step 3: Add to Spawner

Edit `zombie_quest/characters.py`:

```python
class ZombieSpawner:
    ZOMBIE_TYPES = ["scene", "bouncer", "rocker", "dj", "new_type"]  # Add new type

    @staticmethod
    def create_zombie(position: WorldPos, room_id: str = "") -> Zombie:
        """Create a zombie with appropriate type for the room."""
        type_by_room = {
            "hennepin_outside": ["bouncer", "scene"],
            "record_store": ["scene", "rocker"],
            "college_station": ["dj", "scene"],
            "backstage_stage": ["rocker", "scene", "bouncer"],
            "new_room": ["new_type", "scene"],  # Add room mapping
        }

        types = type_by_room.get(room_id, ["scene"])
        zombie_type = random.choice(types)

        return Zombie(position, zombie_type)
```

### Step 4: Add Zombie Audio

Edit `zombie_quest/audio.py`:

```python
def _generate_all_sounds(self) -> None:
    """Generate all synthesized sound effects."""

    # Zombie sounds (multiple types with variations)
    for zombie_type in ['scene', 'bouncer', 'rocker', 'dj', 'new_type']:  # Add new type
        self.sounds[f'zombie_groan_{zombie_type}'] = self._synth_zombie_groan(zombie_type)
        self.sounds[f'zombie_alert_{zombie_type}'] = self._synth_zombie_alert(zombie_type)
        self.sounds[f'zombie_attack_{zombie_type}'] = self._synth_zombie_attack(zombie_type)
```

### Step 5: Place in Rooms

In `game_data.json`:

```json
{
  "zombies": [
    {
      "position": [150, 160],
      "type": "new_type"
    }
  ]
}
```

---

## Audio System Guide

### Audio Architecture

```
AudioManager
    │
    ├── SFX System
    │   ├── Synthesized sounds
    │   └── Spatial audio
    │
    ├── Music System
    │   ├── Procedural layers
    │   └── Tension-based mixing
    │
    ├── Ambient System
    │   ├── Room-specific loops
    │   └── Environmental sounds
    │
    └── Event System
        └── Decoupled audio triggers
```

### Creating New Sound Effects

```python
def _synth_custom_sound(self) -> Optional[pygame.mixer.Sound]:
    """Create a custom synthesized sound."""
    envelope = ADSR(attack=0.02, decay=0.1, sustain=0.6, release=0.2)

    def gen(t, dur):
        # Generate waveform
        freq = 440 + 100 * (t / dur)  # Rising pitch
        tone = WaveformGenerator.sine(freq, t)

        # Apply envelope
        return tone * envelope.get_amplitude(t, dur)

    return self._create_sound_buffer(0.5, gen)
```

### Using Spatial Audio

```python
# Play sound with 3D positioning
self.audio.play_spatial(
    sound_name='zombie_groan',
    source_pos=(zombie.position.x, zombie.position.y),
    listener_pos=(hero.position.x, hero.position.y),
    volume=0.8
)
```

### Adding Music Layers

```python
# Add new procedural music layer
self.music_layers.append(ProceduralMusicLayer(
    name="new_layer",
    base_freq=220,  # A3
    pattern=[0, 2, 4, 7, 9, 11, 12, 7],  # Musical pattern
    waveform="triangle",
    duration=8.0
))

# Activate layer based on tension
if tension == TensionLevel.CUSTOM:
    self._set_layer_volumes(new_layer=0.5)
```

---

## Visual Effects System

### Particle System

```python
# Emit particles
self.particles.emit_sparkle(
    x=position.x,
    y=position.y,
    color=COLORS.NEON_GOLD
)

# Custom particle emission
for i in range(20):
    self.particles.add_particle(
        x=position.x,
        y=position.y,
        vx=random.uniform(-50, 50),
        vy=random.uniform(-50, 50),
        lifetime=1.0,
        color=custom_color
    )
```

### Screen Effects

```python
# Screen shake
self.screen_shake.shake(intensity=10.0, duration=0.5)

# Glow pulse
self.glow.pulse(color=COLORS.HOT_MAGENTA, duration=2.0)

# Room transition
self.transition.start_transition(halfway_callback=lambda: self.change_room("next_room"))
```

---

## Testing Procedures

### Manual Testing Checklist

#### Basic Functionality
- [ ] Game launches without errors
- [ ] All controls respond correctly
- [ ] Rooms load and display properly
- [ ] Hotspots are clickable
- [ ] Dialogue trees work
- [ ] Inventory system functions
- [ ] Save/load works

#### Gameplay Testing
- [ ] Pathfinding works correctly
- [ ] Zombies behave as expected
- [ ] Musical items affect zombies
- [ ] Combat damage and health work
- [ ] Item collection works
- [ ] Puzzle solutions work
- [ ] Room transitions work

#### Edge Cases
- [ ] Clicking outside walkable zones
- [ ] Using wrong items on hotspots
- [ ] Exhausting dialogue options
- [ ] Filling inventory to capacity
- [ ] Multiple zombies attacking simultaneously
- [ ] Rapid clicking/keyboard input

### Headless Testing

```bash
# Run automated validation
python main.py --headless

# Expected output:
# - 120 frames processed
# - All validations passed
# - No crashes
```

### Unit Testing (Future)

Create `tests/test_pathfinding.py`:

```python
import pytest
from zombie_quest.pathfinding import GridPathfinder

def test_pathfinding_straight_line():
    # Test A* finds direct path
    pathfinder = GridPathfinder(create_empty_mask())
    path = pathfinder.find_path((0, 0), (10, 0))
    assert len(path) == 11

def test_pathfinding_obstacle():
    # Test A* navigates around obstacles
    pathfinder = GridPathfinder(create_mask_with_obstacle())
    path = pathfinder.find_path((0, 0), (10, 0))
    assert path is not None
    assert (5, 0) not in path  # Obstacle position
```

### Integration Testing

Test complete workflows:

```python
def test_item_trading_flow():
    """Test: Get flyer -> Trade for demo -> Trade for pass"""
    engine = GameEngine(base_path)

    # Get flyer
    hotspot = engine.current_room.find_hotspot_by_name("Poster Kiosk")
    engine.perform_hotspot_action(hotspot, Verb.USE)
    assert engine.inventory.has_item("Gig Flyer")

    # Enter record store
    # ... etc
```

---

## Common Development Tasks

### Adding a New Game State

Edit `zombie_quest/config.py`:

```python
class GameState:
    MENU = "menu"
    PLAYING = "playing"
    CUSTOM_STATE = "custom_state"  # Add new state
```

Edit `zombie_quest/engine.py`:

```python
def handle_events(self) -> None:
    if self.state == GameState.CUSTOM_STATE:
        self._handle_custom_state_event(event)
```

### Adding Configuration Options

Edit `zombie_quest/config.py`:

```python
@dataclass(frozen=True)
class GameplayConfig:
    HERO_SPEED: float = 75.0
    CUSTOM_OPTION: int = 100  # Add new config
```

Use in code:

```python
from .config import GAMEPLAY

value = GAMEPLAY.CUSTOM_OPTION
```

### Debugging Tools

#### Visual Debugging

```python
# Show walkable zones (for debugging)
def draw_debug_zones(surface, room):
    # Draw walkable mask with transparency
    debug_surf = room.walkable_mask.copy()
    debug_surf.set_alpha(100)
    surface.blit(debug_surf, (0, 0))

    # Draw hotspot rectangles
    for hotspot in room.hotspots:
        pygame.draw.rect(surface, (255, 0, 0), hotspot.rect, 2)
```

#### Console Logging

```python
# Add verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)
logger.debug(f"Hero position: {hero.position}")
logger.info(f"Zombie count: {len(room.zombies)}")
```

---

## Performance Optimization

### Profiling

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Run game loop
engine.run()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

### Common Optimizations

#### 1. Sprite Caching

```python
# Cache generated sprites
_sprite_cache = {}

def get_sprite(key):
    if key not in _sprite_cache:
        _sprite_cache[key] = generate_sprite(key)
    return _sprite_cache[key]
```

#### 2. Pathfinding Optimization

```python
# Only recalculate path when needed
if self.target_changed or self.path_blocked:
    self.path = pathfinder.find_path(start, end)
```

#### 3. Audio Optimization

```python
# Limit concurrent sounds
MAX_CONCURRENT_SOUNDS = 8

if active_sounds < MAX_CONCURRENT_SOUNDS:
    sound.play()
```

#### 4. Particle Limit

```python
# Limit active particles
MAX_PARTICLES = 100

if len(self.particles) >= MAX_PARTICLES:
    self.particles.pop(0)  # Remove oldest
```

---

## Development Best Practices

### Code Style
- Follow PEP 8
- Use type hints
- Document complex functions
- Keep functions small and focused

### Git Workflow
```bash
# Feature branch
git checkout -b feature/new-room

# Commit frequently
git commit -m "Add new room background"

# Push and create PR
git push origin feature/new-room
```

### Documentation
- Update this guide when adding features
- Comment complex algorithms
- Keep API reference current
- Document breaking changes

---

**Happy developing!** If you build something cool with Zombie Quest, we'd love to hear about it!
