# Zombie Quest: API Reference

Complete technical reference for all public classes, methods, and data structures.

## Table of Contents

- [Core Engine](#core-engine)
- [Room System](#room-system)
- [Character System](#character-system)
- [UI Components](#ui-components)
- [Audio System](#audio-system)
- [Dialogue System](#dialogue-system)
- [Effects System](#effects-system)
- [Utility Systems](#utility-systems)
- [Configuration](#configuration)
- [Data Structures](#data-structures)

---

## Core Engine

### `GameEngine`

Main game engine that coordinates all systems.

**Location**: `zombie_quest/engine.py`

#### Constructor

```python
def __init__(self, base_path: str) -> None
```

**Parameters**:
- `base_path` (str): Path to game directory containing game_data.json

**Initializes**:
- Pygame window and display
- All game systems (rooms, characters, UI, audio, effects)
- Game data from JSON
- Starting room and hero position

#### Methods

##### `run()`
```python
def run(self) -> None
```

Main game loop. Runs at 60 FPS until game ends.

**Flow**:
1. Process events
2. Update game state
3. Render frame
4. Display to screen

---

##### `handle_events()`
```python
def handle_events(self) -> None
```

Process all input events (keyboard, mouse).

**Handles**:
- Mouse clicks (movement, interaction)
- Keyboard input (WASD, verbs, shortcuts)
- Window events (close, minimize)

---

##### `update(dt: float)`
```python
def update(self, dt: float) -> None
```

Update all game systems.

**Parameters**:
- `dt` (float): Delta time in seconds since last frame

**Updates**:
- Hero movement and pathfinding
- Zombie AI and positions
- Visual effects and particles
- Audio layers and music
- UI elements and animations

---

##### `draw()`
```python
def draw(self) -> None
```

Render all game elements to screen.

**Rendering Order**:
1. Room background
2. Characters (depth-sorted)
3. Particles and effects
4. UI elements
5. Dialogue (if active)
6. Scanline overlay

---

##### `change_room(room_id, position, message, announce)`
```python
def change_room(
    self,
    room_id: str,
    position: Optional[Tuple[int, int]] = None,
    message: Optional[str] = None,
    announce: bool = True
) -> None
```

Transition to a different room.

**Parameters**:
- `room_id` (str): ID of target room
- `position` (Optional[Tuple[int, int]]): Hero spawn position, defaults to room's default entry
- `message` (Optional[str]): Custom entry message, defaults to room's entry message
- `announce` (bool): Whether to show entry message

**Side Effects**:
- Clears hero pathfinding
- Triggers room ambient audio
- Shows transition effect
- Resets camera

---

##### `perform_hotspot_action(hotspot, verb)`
```python
def perform_hotspot_action(self, hotspot: Hotspot, verb: Verb) -> None
```

Execute a verb action on a hotspot.

**Parameters**:
- `hotspot` (Hotspot): Target hotspot
- `verb` (Verb): Action to perform (WALK/LOOK/USE/TALK)

**Behavior**:
- Checks for required items
- Shows appropriate message
- Gives/removes items
- Triggers room transitions
- Starts dialogue trees

---

##### `give_item_to_inventory(item_name)`
```python
def give_item_to_inventory(self, item_name: str) -> None
```

Add an item to player inventory.

**Parameters**:
- `item_name` (str): Name of item to add

**Side Effects**:
- Adds item to inventory
- Shows pickup message
- Plays pickup sound
- Emits sparkle particles

---

## Room System

### `Room`

Represents a game location with hotspots, zombies, and navigation data.

**Location**: `zombie_quest/rooms.py`

#### Constructor

```python
def __init__(self, data: Dict) -> None
```

**Parameters**:
- `data` (Dict): Room definition from game_data.json

**Data Structure**:
```json
{
  "id": "room_id",
  "name": "Room Name",
  "entry_message": "Entry text",
  "default_entry": [x, y],
  "size": [width, height],
  "background": { ... },
  "walkable_zones": [ ... ],
  "priority_regions": [ ... ],
  "hotspots": [ ... ],
  "zombies": [ ... ]
}
```

#### Properties

- `id` (str): Unique room identifier
- `name` (str): Display name
- `size` (Tuple[int, int]): Room dimensions
- `background` (pygame.Surface): Background image
- `walkable_mask` (pygame.Surface): Collision mask
- `priority_mask` (pygame.Surface): Layer priority mask
- `hotspots` (List[Hotspot]): Interactive objects
- `zombies` (List[Zombie]): Room enemies
- `bounds` (pygame.Rect): Room boundaries
- `pathfinder` (GridPathfinder): A* pathfinding

#### Methods

##### `draw(surface, hero)`
```python
def draw(self, surface: pygame.Surface, hero: Hero) -> None
```

Render room and all characters.

**Parameters**:
- `surface` (pygame.Surface): Target surface
- `hero` (Hero): Player character

**Rendering**:
1. Blit background
2. Sort characters by Y position
3. Draw each character
4. Draw priority overlay if hero is behind objects

---

##### `is_walkable(position)`
```python
def is_walkable(self, position: Tuple[float, float]) -> bool
```

Check if position is walkable.

**Parameters**:
- `position` (Tuple[float, float]): (x, y) coordinates

**Returns**: `bool` - True if walkable, False if blocked

**Uses**: Walkable mask to determine accessibility

---

##### `find_hotspot(position)`
```python
def find_hotspot(self, position: Tuple[int, int]) -> Optional[Hotspot]
```

Find hotspot at given position.

**Parameters**:
- `position` (Tuple[int, int]): Click position

**Returns**: `Optional[Hotspot]` - Hotspot if found, None otherwise

---

### `Hotspot`

Interactive object within a room.

**Location**: `zombie_quest/rooms.py`

#### Properties

- `rect` (pygame.Rect): Clickable area
- `name` (str): Display name
- `verbs` (Dict[str, str]): Verb responses
- `walk_position` (Optional[Tuple[int, int]]): Where hero walks to interact
- `required_item` (Optional[str]): Item needed to interact
- `give_item` (Optional[str]): Item given on interaction
- `remove_item` (Optional[str]): Item removed on interaction
- `talk_target` (Optional[str]): Dialogue tree to start
- `target_room` (Optional[str]): Room to transition to
- `target_position` (Optional[Tuple[int, int]]): Spawn position in target room
- `transition_verb` (str): Verb that triggers transition (default: "use")
- `requires_success_for_transition` (bool): Must have required item to transition

#### Methods

##### `message_for(verb, outcome)`
```python
def message_for(self, verb: str, outcome: str = "default") -> str
```

Get message for verb and outcome.

**Parameters**:
- `verb` (str): Verb name ("look", "use", "talk")
- `outcome` (str): Outcome ("default", "success", "missing")

**Returns**: `str` - Message to display

**Message Keys**:
- `look`: Default look message
- `use_success`: Successful use with required item
- `use_missing`: Use without required item
- `use_default`: Default use message
- `talk`: Talk message

---

## Character System

### `Hero`

Player character with movement and health.

**Location**: `zombie_quest/characters.py`

**Inherits**: `Character`

#### Constructor

```python
def __init__(self, position: WorldPos) -> None
```

**Parameters**:
- `position` (WorldPos): Starting (x, y) position

**Initializes**:
- Health system (3 hearts)
- Pathfinding support
- Keyboard movement
- Animations (4 directions, 4 frames each)

#### Properties

- `position` (pygame.Vector2): Current position
- `speed` (float): Movement speed (75.0 pixels/sec)
- `health` (int): Current health (0-3)
- `max_health` (int): Maximum health (3)
- `is_invincible` (bool): Invincibility state after damage
- `invincibility_timer` (float): Remaining invincibility time
- `path` (List[pygame.Vector2]): Pathfinding waypoints
- `current_target` (Optional[pygame.Vector2]): Next waypoint
- `keyboard_velocity` (pygame.Vector2): Keyboard movement vector
- `using_keyboard` (bool): Currently using keyboard movement

#### Methods

##### `set_destination(destination, pathfinder)`
```python
def set_destination(self, destination: WorldPos, pathfinder: GridPathfinder) -> None
```

Set pathfinding destination (mouse click movement).

**Parameters**:
- `destination` (WorldPos): Target (x, y) position
- `pathfinder` (GridPathfinder): Room pathfinder

**Side Effects**:
- Calculates A* path
- Sets first waypoint as target
- Disables keyboard movement

---

##### `handle_keyboard_input(keys_pressed)`
```python
def handle_keyboard_input(self, keys_pressed: pygame.key.ScancodeWrapper) -> None
```

Process keyboard movement (WASD/arrows).

**Parameters**:
- `keys_pressed`: Pygame key state

**Controls**:
- W/Up: Move up
- A/Left: Move left
- S/Down: Move down
- D/Right: Move right

**Side Effects**:
- Sets keyboard velocity
- Enables keyboard movement mode
- Clears pathfinding

---

##### `update(dt, room_bounds, walkable_check)`
```python
def update(
    self,
    dt: float,
    room_bounds: Optional[pygame.Rect] = None,
    walkable_check: Optional[callable] = None
) -> None
```

Update hero position and state.

**Parameters**:
- `dt` (float): Delta time
- `room_bounds` (Optional[pygame.Rect]): Room boundaries
- `walkable_check` (Optional[callable]): Function to check if position is walkable

**Updates**:
- Invincibility timer
- Movement (keyboard or pathfinding)
- Animation frames
- Squash/stretch effects

---

##### `take_damage(amount)`
```python
def take_damage(self, amount: int = 1) -> bool
```

Apply damage to hero.

**Parameters**:
- `amount` (int): Damage amount (default: 1)

**Returns**: `bool` - True if hero died, False otherwise

**Side Effects**:
- Reduces health
- Activates invincibility (1.5 seconds)
- Triggers visual effects

---

##### `heal(amount)`
```python
def heal(self, amount: int = 1) -> None
```

Heal the hero.

**Parameters**:
- `amount` (int): Heal amount (default: 1)

**Effects**:
- Increases health (capped at max_health)

---

##### `has_arrived()`
```python
def has_arrived(self) -> bool
```

Check if hero has reached destination.

**Returns**: `bool` - True if no movement in progress

---

### `Zombie`

Enemy character with AI and music response.

**Location**: `zombie_quest/characters.py`

**Inherits**: `Character`

#### Constructor

```python
def __init__(self, position: WorldPos, zombie_type: str = "scene") -> None
```

**Parameters**:
- `position` (WorldPos): Starting position
- `zombie_type` (str): Type ("scene", "bouncer", "rocker", "dj")

**Initializes**:
- AI timers and state
- Music preferences
- Type-specific animations

#### Properties

- `zombie_type` (str): Zombie type/personality
- `wander_timer` (float): Time until next wander decision
- `wander_direction` (pygame.Vector2): Current movement direction
- `detection_radius` (float): Player detection range (90 pixels)
- `is_chasing` (bool): Currently chasing player
- `music_state` (ZombieMusicState): Current music effect state
- `music_effect_timer` (float): Remaining music effect duration
- `music_affinities` (Dict[str, float]): Music type preferences

#### Methods

##### `respond_to_music(music_type, intensity)`
```python
def respond_to_music(self, music_type: str, intensity: float) -> ZombieMusicState
```

Calculate zombie response to music.

**Parameters**:
- `music_type` (str): Music type ("guitar", "electronic", "new_wave", "punk", "ambient")
- `intensity` (float): Music intensity (0.0 to 1.0)

**Returns**: `ZombieMusicState` - New state based on affinity and intensity

**States**:
- HOSTILE (< 0.3 effective intensity): Normal behavior
- ENTRANCED (0.3-0.6): Frozen in place
- DANCING (0.6-0.9): Swaying, harmless
- REMEMBERING (> 0.9): Brief lucidity

---

##### `apply_music_effect(music_type, intensity)`
```python
def apply_music_effect(self, music_type: str, intensity: float) -> None
```

Apply music effect to zombie.

**Parameters**:
- `music_type` (str): Music type
- `intensity` (float): Music intensity

**Side Effects**:
- Changes music state
- Sets effect timer
- Higher priority states override lower

---

##### `is_harmless()`
```python
def is_harmless(self) -> bool
```

Check if zombie is currently harmless.

**Returns**: `bool` - True if in ENTRANCED, DANCING, or REMEMBERING state

---

##### `update(dt, hero_position, room_rect)`
```python
def update(
    self,
    dt: float,
    hero_position: WorldPos,
    room_rect: pygame.Rect
) -> bool
```

Update zombie AI and position.

**Parameters**:
- `dt` (float): Delta time
- `hero_position` (WorldPos): Hero position for AI
- `room_rect` (pygame.Rect): Room boundaries

**Returns**: `bool` - True if zombie touched hero (and is hostile)

**Behavior**:
- Updates music state timer
- AI decision-making (wander, chase, or music effect)
- Movement and collision
- Animation updates

---

## UI Components

### `VerbBar`

Top bar with verb selection and health display.

**Location**: `zombie_quest/ui.py`

#### Constructor

```python
def __init__(self, width: int, height: int) -> None
```

**Parameters**:
- `width` (int): Bar width
- `height` (int): Bar height

#### Properties

- `selected_verb` (Verb): Currently selected verb
- `hovered_verb` (Optional[Verb]): Verb under mouse cursor
- `verb_icons` (List[Tuple[Verb, Surface, Rect]]): Icon data
- `inventory_rect` (pygame.Rect): Inventory button
- `options_rect` (pygame.Rect): Options button
- `health_display` (HealthDisplay): Heart icon display

#### Methods

##### `draw(surface, hero_health)`
```python
def draw(self, surface: pygame.Surface, hero_health: int = 3) -> None
```

Render verb bar.

**Parameters**:
- `surface` (pygame.Surface): Target surface
- `hero_health` (int): Current hero health

---

##### `handle_click(position)`
```python
def handle_click(self, position: Tuple[int, int]) -> Optional[str]
```

Handle mouse click on verb bar.

**Parameters**:
- `position` (Tuple[int, int]): Click position

**Returns**: `Optional[str]` - Action ("verb", "inventory", "options") or None

---

##### `handle_key(key)`
```python
def handle_key(self, key: int) -> Optional[str]
```

Handle keyboard shortcut.

**Parameters**:
- `key` (int): Pygame key code

**Returns**: `Optional[str]` - Action or None

**Keys**:
- 1: Walk verb
- 2: Look verb
- 3: Use verb
- 4: Talk verb
- I: Inventory
- P: Options

---

### `Inventory`

Item collection and management.

**Location**: `zombie_quest/ui.py`

#### Constructor

```python
def __init__(self, max_items: int = 8) -> None
```

**Parameters**:
- `max_items` (int): Maximum inventory capacity

#### Properties

- `items` (List[Item]): Collected items
- `selected_item` (Optional[Item]): Currently selected item
- `max_items` (int): Capacity limit

#### Methods

##### `add_item(item)`
```python
def add_item(self, item: Item) -> bool
```

Add item to inventory.

**Parameters**:
- `item` (Item): Item to add

**Returns**: `bool` - True if added, False if inventory full

---

##### `remove_item(name)`
```python
def remove_item(self, name: str) -> Optional[Item]
```

Remove item from inventory.

**Parameters**:
- `name` (str): Item name

**Returns**: `Optional[Item]` - Removed item or None

---

##### `has_item(name)`
```python
def has_item(self, name: str) -> bool
```

Check if inventory contains item.

**Parameters**:
- `name` (str): Item name

**Returns**: `bool` - True if item present

---

##### `select_item(item)`
```python
def select_item(self, item: Optional[Item]) -> None
```

Select item for use.

**Parameters**:
- `item` (Optional[Item]): Item to select, None to deselect

---

### `MessageBox`

Text display with typewriter effect.

**Location**: `zombie_quest/ui.py`

#### Methods

##### `show(message)`
```python
def show(self, message: str) -> None
```

Display a message with typewriter effect.

**Parameters**:
- `message` (str): Text to display

**Effects**:
- Starts typewriter animation
- Sets display timer

---

##### `skip_typing()`
```python
def skip_typing(self) -> None
```

Instantly show full message.

---

##### `update(dt)`
```python
def update(self, dt: float) -> None
```

Update typewriter effect and timer.

**Parameters**:
- `dt` (float): Delta time

---

## Audio System

### `AudioManager`

Master audio controller with procedural synthesis.

**Location**: `zombie_quest/audio.py`

#### Constructor

```python
def __init__(self) -> None
```

**Initializes**:
- Pygame mixer
- All synthesized sounds
- Procedural music layers
- Ambient soundscapes
- Event system

#### Methods

##### `play(sound_name, volume)`
```python
def play(self, sound_name: str, volume: float = 1.0) -> None
```

Play a sound effect.

**Parameters**:
- `sound_name` (str): Sound identifier
- `volume` (float): Volume multiplier (0.0 to 1.0)

**Available Sounds**:
- Movement: footstep, footstep_concrete, footstep_carpet
- Items: pickup, item_use, item_error
- Doors: door, door_creak, door_slam
- Combat: hit, death, health_low
- Zombies: zombie_groan_{type}, zombie_alert_{type}
- UI: ui_click, ui_select, message, success, error
- Environment: electric_hum, neon_flicker, vinyl_crackle

---

##### `play_spatial(sound_name, source_pos, listener_pos, volume, fallback_sound)`
```python
def play_spatial(
    self,
    sound_name: str,
    source_pos: Tuple[float, float],
    listener_pos: Tuple[float, float],
    volume: float = 1.0,
    fallback_sound: Optional[str] = None
) -> None
```

Play sound with 3D spatial positioning.

**Parameters**:
- `sound_name` (str): Sound to play
- `source_pos` (Tuple[float, float]): Sound origin (x, y)
- `listener_pos` (Tuple[float, float]): Listener position (x, y)
- `volume` (float): Base volume
- `fallback_sound` (Optional[str]): Alternative sound if primary not found

**Effects**:
- Calculates distance attenuation
- Applies stereo panning
- Reduces volume based on distance

---

##### `set_music_tension(tension, room_id)`
```python
def set_music_tension(self, tension: TensionLevel, room_id: Optional[str] = None) -> None
```

Set music tension level with room-specific themes.

**Parameters**:
- `tension` (TensionLevel): Tension level (SAFE, EXPLORATION, DANGER, CHASE)
- `room_id` (Optional[str]): Current room for room-specific music

**Effects**:
- Crossfades music layers
- Adjusts layer volumes
- Blends room-specific themes

**Tension Levels**:
- SAFE: Gentle, room-specific music
- EXPLORATION: Normal exploration with light tension
- DANGER: Zombie detected, increased tension
- CHASE: Active zombie chase, maximum intensity

---

##### `update_music(dt)`
```python
def update_music(self, dt: float) -> None
```

Update procedural music (call every frame).

**Parameters**:
- `dt` (float): Delta time

**Updates**:
- Music layer crossfading
- Procedural pattern generation
- Layer volume envelopes

---

##### `set_room_ambience(room_id)`
```python
def set_room_ambience(self, room_id: str) -> None
```

Set ambient sound for room.

**Parameters**:
- `room_id` (str): Room identifier

**Effects**:
- Stops current ambience
- Plays room-specific ambient loop
- Updates music layers for room theme

---

## Dialogue System

### `DialogueTree`

Complete dialogue tree for an NPC.

**Location**: `zombie_quest/dialogue.py`

#### Constructor

```python
def __init__(self, character_name: str) -> None
```

**Parameters**:
- `character_name` (str): Character name for display

#### Properties

- `character_name` (str): NPC name
- `nodes` (Dict[str, DialogueNode]): All dialogue nodes
- `start_node` (Optional[str]): Starting node ID
- `fallback_node` (Optional[str]): Default node if conditions fail

#### Methods

##### `add_node(node)`
```python
def add_node(self, node: DialogueNode) -> None
```

Add a node to the tree.

**Parameters**:
- `node` (DialogueNode): Node to add

---

##### `get_starting_node(inventory_items, flags)`
```python
def get_starting_node(
    self,
    inventory_items: List[str],
    flags: Dict[str, bool]
) -> Optional[DialogueNode]
```

Get appropriate starting node based on state.

**Parameters**:
- `inventory_items` (List[str]): Player inventory
- `flags` (Dict[str, bool]): Game flags

**Returns**: `Optional[DialogueNode]` - Starting node or None

**Logic**:
1. Check nodes with conditions first
2. Return first matching node
3. Fall back to start_node

---

### `DialogueNode`

Single node in dialogue tree.

**Location**: `zombie_quest/dialogue.py`

#### Properties

- `id` (str): Unique node identifier
- `speaker` (str): Speaker name
- `text` (str): Dialogue text
- `choices` (List[DialogueChoice]): Player choices
- `auto_next` (Optional[str]): Auto-advance to next node
- `conditions` (List[str]): Requirements to show this node
- `effects` (List[Tuple[DialogueEffect, str]]): Effects when entering node

---

### `DialogueChoice`

Player choice option.

**Location**: `zombie_quest/dialogue.py`

#### Properties

- `text` (str): Choice text
- `next_node` (Optional[str]): Node to jump to (None = end)
- `requirements` (List[str]): Items/flags required
- `effects` (List[Tuple[DialogueEffect, str]]): Effects when chosen
- `visible_when_unavailable` (bool): Show even if unavailable

#### Methods

##### `is_available(inventory_items, flags)`
```python
def is_available(
    self,
    inventory_items: List[str],
    flags: Dict[str, bool]
) -> bool
```

Check if choice is currently available.

**Parameters**:
- `inventory_items` (List[str]): Player inventory
- `flags` (Dict[str, bool]): Game flags

**Returns**: `bool` - True if all requirements met

---

### `DialogueManager`

Active dialogue renderer and controller.

**Location**: `zombie_quest/dialogue.py`

#### Methods

##### `start_dialogue(tree, inventory_items, flags)`
```python
def start_dialogue(
    self,
    tree: DialogueTree,
    inventory_items: List[str],
    flags: Dict[str, bool]
) -> bool
```

Start a dialogue.

**Parameters**:
- `tree` (DialogueTree): Dialogue tree to start
- `inventory_items` (List[str]): Player inventory
- `flags` (Dict[str, bool]): Game flags

**Returns**: `bool` - True if dialogue started successfully

---

##### `handle_input(event, inventory_items, flags)`
```python
def handle_input(
    self,
    event: pygame.event.Event,
    inventory_items: List[str],
    flags: Dict[str, bool]
) -> Optional[List[Tuple[DialogueEffect, str]]]
```

Handle input during dialogue.

**Parameters**:
- `event` (pygame.event.Event): Input event
- `inventory_items` (List[str]): Player inventory
- `flags` (Dict[str, bool]): Game flags

**Returns**: `Optional[List[Tuple[DialogueEffect, str]]]` - Effects to apply

**Controls**:
- Space/Enter: Advance/Select choice
- Up/Down: Navigate choices
- Escape: End dialogue

---

## Effects System

### `ParticleSystem`

Particle emitter and manager.

**Location**: `zombie_quest/effects.py`

#### Methods

##### `emit_sparkle(x, y, color)`
```python
def emit_sparkle(self, x: float, y: float, color: Tuple[int, int, int]) -> None
```

Emit sparkle particles.

**Parameters**:
- `x` (float): X position
- `y` (float): Y position
- `color` (Tuple[int, int, int]): Particle color

---

##### `emit_damage(x, y)`
```python
def emit_damage(self, x: float, y: float) -> None
```

Emit damage particles.

---

##### `emit_ambient_dust(rect)`
```python
def emit_ambient_dust(self, rect: pygame.Rect) -> None
```

Emit ambient dust particles in room.

---

##### `update(dt)`
```python
def update(self, dt: float) -> None
```

Update all particles.

---

##### `draw(surface)`
```python
def draw(self, surface: pygame.Surface) -> None
```

Render all particles.

---

### `ScreenTransition`

Fade effects for room transitions.

**Location**: `zombie_quest/effects.py`

#### Methods

##### `start_transition(halfway_callback)`
```python
def start_transition(self, halfway_callback: Optional[Callable] = None) -> None
```

Start fade transition.

**Parameters**:
- `halfway_callback` (Optional[Callable]): Function to call at halfway point

---

## Utility Systems

### `GridPathfinder`

A* pathfinding algorithm.

**Location**: `zombie_quest/pathfinding.py`

#### Constructor

```python
def __init__(self, walkable_mask: pygame.Surface) -> None
```

**Parameters**:
- `walkable_mask` (pygame.Surface): Walkable area mask

#### Methods

##### `find_path(start, goal)`
```python
def find_path(
    self,
    start: Tuple[float, float],
    goal: Tuple[float, float]
) -> List[Tuple[float, float]]
```

Find optimal path using A*.

**Parameters**:
- `start` (Tuple[float, float]): Starting position
- `goal` (Tuple[float, float]): Goal position

**Returns**: `List[Tuple[float, float]]` - Waypoint list

---

## Configuration

### Global Config Objects

**Location**: `zombie_quest/config.py`

#### `DISPLAY`
Display configuration.

**Properties**:
- `ROOM_WIDTH` (int): 320
- `ROOM_HEIGHT` (int): 200
- `UI_BAR_HEIGHT` (int): 40
- `MESSAGE_HEIGHT` (int): 36
- `WINDOW_WIDTH` (int): 320
- `WINDOW_HEIGHT` (int): 276

---

#### `GAMEPLAY`
Gameplay configuration.

**Properties**:
- `HERO_SPEED` (float): 75.0
- `ZOMBIE_SPEED` (float): 42.0
- `ZOMBIE_DETECTION_RADIUS` (float): 90.0
- `ZOMBIE_WANDER_INTERVAL` (float): 2.5
- `HERO_MAX_HEALTH` (int): 3
- `HERO_INVINCIBILITY_TIME` (float): 1.5
- `ARRIVAL_TOLERANCE` (float): 2.0
- `INTERACTION_RADIUS` (float): 40.0

---

#### `COLORS`
Color palette.

**Properties**:
- `DEEP_PURPLE`: (30, 10, 60)
- `HOT_MAGENTA`: (255, 20, 147)
- `CYAN_GLOW`: (0, 255, 255)
- `NEON_GOLD`: (255, 215, 0)
- `UI_TEXT`: (240, 230, 250)
- And many more...

---

#### `GameState`
Game state enumeration.

**Values**:
- `MENU`: "menu"
- `PLAYING`: "playing"
- `PAUSED`: "paused"
- `DIALOGUE`: "dialogue"
- `INVENTORY`: "inventory"
- `TRANSITION`: "transition"
- `GAME_OVER`: "game_over"
- `CREDITS`: "credits"

---

## Data Structures

### Item Structure (JSON)

```json
{
  "name": "Item Name",
  "description": "Item description text",
  "icon_color": [R, G, B]
}
```

---

### Hotspot Structure (JSON)

```json
{
  "name": "Hotspot Name",
  "rect": [x, y, width, height],
  "walk_position": [x, y],
  "verbs": {
    "look": "Look message",
    "use": "Use message",
    "talk": "Talk message"
  },
  "required_item": "Item Name",
  "give_item": "Item Name",
  "remove_item": "Item Name",
  "target_room": "room_id",
  "target_position": [x, y],
  "transition_verb": "use"
}
```

---

### Room Structure (JSON)

```json
{
  "id": "room_id",
  "name": "Room Name",
  "entry_message": "Entry text",
  "default_entry": [x, y],
  "size": [width, height],
  "background": { ... },
  "walkable_zones": [ ... ],
  "priority_regions": [ ... ],
  "hotspots": [ ... ],
  "zombies": [ ... ]
}
```

---

## Integration Examples

### Example 1: Playing with Audio

```python
from zombie_quest.audio import get_audio_manager

# Get global audio instance
audio = get_audio_manager()

# Play simple sound
audio.play('pickup', volume=0.8)

# Play spatial sound
audio.play_spatial(
    'zombie_groan',
    source_pos=(100, 150),
    listener_pos=(hero.position.x, hero.position.y),
    volume=0.6
)

# Set music tension
from zombie_quest.audio import TensionLevel
audio.set_music_tension(TensionLevel.CHASE, room_id='backstage')
```

---

### Example 2: Creating Custom Dialogue

```python
from zombie_quest.dialogue import DialogueTree, DialogueNode, DialogueChoice, DialogueEffect

tree = DialogueTree("Merchant")

tree.add_node(DialogueNode(
    id="greeting",
    speaker="Merchant",
    text="Welcome! What can I get you?",
    choices=[
        DialogueChoice(
            text="What do you sell?",
            next_node="catalog"
        ),
        DialogueChoice(
            text="[Buy Item for 100 gold]",
            next_node="purchase",
            requirements=["100_gold"],
            effects=[
                (DialogueEffect.GIVE_ITEM, "Potion"),
                (DialogueEffect.REMOVE_ITEM, "100_gold")
            ]
        )
    ]
))
```

---

### Example 3: Room Transitions

```python
# In engine.py
def trigger_room_change(self, target_room_id: str):
    """Transition to new room with effects."""

    # Start fade out
    def halfway():
        self.change_room(target_room_id)

    self.transition.start_transition(halfway_callback=halfway)
    self.audio.play('door', volume=0.6)
```

---

**This API reference covers all major public interfaces. For implementation details, see the source code.**
