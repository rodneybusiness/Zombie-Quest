# Zombie Quest: Comprehensive Implementation Specification
## From 4.1/10 to All-Time Top 10 Contender

**Version:** 1.0
**Target:** Transform Zombie Quest into a legendary gaming experience
**Timeline:** 4-week sprint to excellence

---

## Table of Contents
1. [Story & Narrative Systems (10/10 Target)](#1-story--narrative-systems)
2. [Puzzle Depth & Multi-Path Design (10/10 Target)](#2-puzzle-depth--multi-path-design)
3. [Thematic Integration (10/10 Target)](#3-thematic-integration)
4. [Juice Amplification (10/10 Target)](#4-juice-amplification)
5. [Implementation Roadmap](#5-implementation-roadmap)
6. [Testing & Validation](#6-testing--validation)

---

## 1. Story & Narrative Systems

### 1.1 Protagonist Backstory System

**Goal:** Player chooses one of three backstories that affect dialogue, endings, and character interactions.

#### Data Structure

**File:** `zombie_quest/protagonist.py` (NEW)

```python
"""Protagonist backstory and character progression system."""
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional

class BackstoryType(Enum):
    COWARD = "coward"      # Left the band when things got hard
    SELLOUT = "sellout"    # Took corporate gig, lost authenticity
    BURNOUT = "burnout"    # Pushed too hard, flamed out spectacularly

@dataclass
class Backstory:
    type: BackstoryType
    display_name: str
    description: str
    starting_reputation: int  # Scene cred at start
    maya_relationship: int    # -10 to +10
    special_ability: str
    unique_dialogue_flag: str

BACKSTORIES = {
    BackstoryType.COWARD: Backstory(
        type=BackstoryType.COWARD,
        display_name="The Coward",
        description="You walked away when Maya needed you most. The scene remembers.",
        starting_reputation=-5,
        maya_relationship=-8,
        special_ability="sneak",  # +50% zombie detection avoidance
        unique_dialogue_flag="backstory_coward"
    ),
    BackstoryType.SELLOUT: Backstory(
        type=BackstoryType.SELLOUT,
        display_name="The Sellout",
        display_name="You took the corporate jingle gig. The money was good. Your soul wasn't.",
        starting_reputation=-3,
        maya_relationship=-4,
        special_ability="charm",  # NPCs more receptive to trades
        unique_dialogue_flag="backstory_sellout"
    ),
    BackstoryType.BURNOUT: Backstory(
        type=BackstoryType.BURNOUT,
        display_name="The Burnout",
        description="You burned too bright, too fast. Now you're trying to reignite.",
        starting_reputation=2,
        maya_relationship=3,
        special_ability="fire",  # Music items have stronger effects
        unique_dialogue_flag="backstory_burnout"
    ),
}

class ProtagonistState:
    """Tracks protagonist progression throughout game."""

    def __init__(self, backstory: BackstoryType):
        self.backstory = BACKSTORIES[backstory]
        self.scene_cred = self.backstory.starting_reputation
        self.maya_relationship = self.backstory.maya_relationship
        self.memories_discovered: List[str] = []
        self.character_growth: Dict[str, int] = {
            "courage": 0,
            "authenticity": 0,
            "redemption": 0
        }

    def modify_relationship(self, character: str, amount: int):
        """Modify relationship with key characters."""
        if character == "maya":
            self.maya_relationship = max(-10, min(10,
                self.maya_relationship + amount))

    def gain_scene_cred(self, amount: int, reason: str = ""):
        """Gain scene credibility."""
        self.scene_cred += amount
        # Log for achievement tracking

    def discover_memory(self, memory_id: str):
        """Unlock a memory hotspot."""
        if memory_id not in self.memories_discovered:
            self.memories_discovered.append(memory_id)

    def grow_trait(self, trait: str, amount: int = 1):
        """Increase character growth trait."""
        if trait in self.character_growth:
            self.character_growth[trait] += amount
```

#### Integration with Engine

**File:** `zombie_quest/engine.py`

**Add to `__init__`:**
```python
# Protagonist system
from .protagonist import ProtagonistState, BackstoryType

# After hero initialization
self.protagonist: Optional[ProtagonistState] = None
self.backstory_selected = False
```

**Add method:**
```python
def show_backstory_selection(self) -> None:
    """Display backstory selection screen at game start."""
    # Create backstory selection UI (similar to pause menu)
    from .ui import BackstorySelectionMenu
    self.backstory_menu = BackstorySelectionMenu(
        self.screen_width,
        self.screen_height
    )
    self.state = GameState.BACKSTORY_SELECTION
```

#### New UI Component

**File:** `zombie_quest/ui.py`

**Add class:**
```python
class BackstorySelectionMenu:
    """Backstory selection screen."""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.selected_index = 0
        self.backstories = list(BACKSTORIES.values())
        self.font_title = load_serif_font(24)
        self.font_name = load_serif_font(18)
        self.font_desc = load_serif_font(14)
        self.visible = True

    def handle_key(self, key: int) -> Optional[BackstoryType]:
        """Handle keyboard input, return selected backstory."""
        if key == pygame.K_UP:
            self.selected_index = (self.selected_index - 1) % len(self.backstories)
        elif key == pygame.K_DOWN:
            self.selected_index = (self.selected_index + 1) % len(self.backstories)
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            return self.backstories[self.selected_index].type
        return None

    def draw(self, surface: pygame.Surface):
        """Draw backstory selection screen."""
        # Dark overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        # Title
        title = self.font_title.render(
            "Choose Your Past", True, COLORS.NEON_GOLD
        )
        surface.blit(title, (self.width // 2 - title.get_width() // 2, 40))

        # Backstories
        y_offset = 100
        for i, backstory in enumerate(self.backstories):
            is_selected = i == self.selected_index

            # Name
            color = COLORS.HOT_MAGENTA if is_selected else COLORS.UI_TEXT
            name_surf = self.font_name.render(
                f"{'> ' if is_selected else '  '}{backstory.display_name}",
                True, color
            )
            surface.blit(name_surf, (60, y_offset))

            # Description (if selected)
            if is_selected:
                desc_lines = self._wrap_text(backstory.description, self.width - 120)
                for j, line in enumerate(desc_lines):
                    desc_surf = self.font_desc.render(line, True, COLORS.UI_TEXT)
                    surface.blit(desc_surf, (80, y_offset + 25 + j * 18))

            y_offset += 80 if is_selected else 40

        # Prompt
        prompt = self.font_desc.render(
            "[ENTER] to select  [↑↓] to navigate", True, (150, 150, 170)
        )
        surface.blit(prompt, (self.width // 2 - prompt.get_width() // 2,
                             self.height - 40))

    def _wrap_text(self, text: str, max_width: int) -> List[str]:
        """Wrap text for display."""
        # Implementation similar to DialogueManager._wrap_text
        pass
```

---

### 1.2 Maya Confrontation Scene

**Goal:** Create a branching 8-10 node dialogue tree that changes based on backstory, choices, and items collected.

#### Dialogue Tree Design

**File:** `zombie_quest/dialogue.py`

**Add function:**
```python
def create_maya_dialogue(protagonist: ProtagonistState) -> DialogueTree:
    """Create Maya's dialogue tree based on protagonist's history."""
    tree = DialogueTree("Maya 'Riot' Reyes")

    # Node 1: Initial confrontation (varies by backstory)
    if protagonist.backstory.type == BackstoryType.COWARD:
        tree.add_node(DialogueNode(
            id="maya_start_coward",
            speaker="Maya",
            text="You. I can't believe you have the guts to show your face here after what you did.",
            choices=[
                DialogueChoice(
                    text="Maya, I know I left when you needed me...",
                    next_node="maya_acknowledge_coward"
                ),
                DialogueChoice(
                    text="I'm here now, aren't I?",
                    next_node="maya_deflect_coward"
                ),
                DialogueChoice(
                    text="[Say nothing, look at the ground]",
                    next_node="maya_silence_coward"
                ),
            ],
            conditions=["backstory_coward"]
        ))

        tree.add_node(DialogueNode(
            id="maya_acknowledge_coward",
            speaker="Maya",
            text="Yeah, you left. Right before the biggest show of our lives. I had to cancel. Do you know what that did to me?",
            choices=[
                DialogueChoice(
                    text="I was scared, Maya. I'm still scared.",
                    next_node="maya_honest_fear",
                    effects=[(DialogueEffect.SET_FLAG, "maya_honest_moment")]
                ),
                DialogueChoice(
                    text="I had my reasons...",
                    next_node="maya_weak_excuse"
                ),
            ]
        ))

        tree.add_node(DialogueNode(
            id="maya_deflect_coward",
            speaker="Maya",
            text="*scoffs* Yeah, now that it's convenient for you. Where were you when the scene was falling apart?",
            choices=[
                DialogueChoice(
                    text="I'm sorry. I should have been there.",
                    next_node="maya_apology_path"
                ),
                DialogueChoice(
                    text="I can't change the past, but I can help now.",
                    next_node="maya_action_over_words"
                ),
            ]
        ))

        tree.add_node(DialogueNode(
            id="maya_silence_coward",
            speaker="Maya",
            text="*long pause* ...At least you're not making excuses. That's something.",
            auto_next="maya_tentative_truce",
            effects=[(DialogueEffect.SET_FLAG, "maya_respects_silence")]
        ))

    elif protagonist.backstory.type == BackstoryType.SELLOUT:
        tree.add_node(DialogueNode(
            id="maya_start_sellout",
            speaker="Maya",
            text="Well, well. If it isn't Mr. Corporate. How's the jingle business? Still selling sneakers?",
            choices=[
                DialogueChoice(
                    text="I needed the money. You know how it was.",
                    next_node="maya_money_excuse"
                ),
                DialogueChoice(
                    text="I regret it. Every single day.",
                    next_node="maya_genuine_regret"
                ),
                DialogueChoice(
                    text="At least I didn't starve making 'art'.",
                    next_node="maya_defensive_anger"
                ),
            ],
            conditions=["backstory_sellout"]
        ))

        tree.add_node(DialogueNode(
            id="maya_money_excuse",
            speaker="Maya",
            text="We all needed money. The difference is some of us didn't sell our souls for it.",
            choices=[
                DialogueChoice(
                    text="You're right. I lost myself.",
                    next_node="maya_admit_lost",
                    effects=[(DialogueEffect.SET_FLAG, "maya_sees_remorse")]
                ),
                DialogueChoice(
                    text="Easy for you to say from your authentic high horse.",
                    next_node="maya_bridge_burned"
                ),
            ]
        ))

        tree.add_node(DialogueNode(
            id="maya_genuine_regret",
            speaker="Maya",
            text="*studies you carefully* You mean that, don't you? I can see it in your eyes.",
            auto_next="maya_cautious_opening",
            effects=[(DialogueEffect.SET_FLAG, "maya_sees_change")]
        ))

    elif protagonist.backstory.type == BackstoryType.BURNOUT:
        tree.add_node(DialogueNode(
            id="maya_start_burnout",
            speaker="Maya",
            text="Hey. I heard about what happened. The... incident. Are you okay?",
            choices=[
                DialogueChoice(
                    text="I'm getting better. Trying to, anyway.",
                    next_node="maya_recovery_path"
                ),
                DialogueChoice(
                    text="I'm fine. Let's not talk about it.",
                    next_node="maya_avoid_topic"
                ),
                DialogueChoice(
                    text="Honestly? I'm a mess. But I'm here.",
                    next_node="maya_vulnerable_truth"
                ),
            ],
            conditions=["backstory_burnout"]
        ))

        tree.add_node(DialogueNode(
            id="maya_recovery_path",
            speaker="Maya",
            text="Good. Because we need you tonight. The *real* you, not the self-destructive version.",
            auto_next="maya_needs_help",
            effects=[(DialogueEffect.SET_FLAG, "maya_supportive")]
        ))

        tree.add_node(DialogueNode(
            id="maya_vulnerable_truth",
            speaker="Maya",
            text="*puts hand on your shoulder* I know. But you're still standing. That counts for something.",
            auto_next="maya_mutual_respect",
            effects=[
                (DialogueEffect.SET_FLAG, "maya_trusts_you"),
                (DialogueEffect.HEAL, "1")
            ]
        ))

    # Middle conversation nodes (shared across backstories)
    tree.add_node(DialogueNode(
        id="maya_honest_fear",
        speaker="Maya",
        text="*softens slightly* At least you're being honest now. Fear... I get it. The zombies, the pressure, all of it.",
        choices=[
            DialogueChoice(
                text="I want to make it right. Tell me what you need.",
                next_node="maya_redemption_offer"
            ),
            DialogueChoice(
                text="I thought you'd never forgive me.",
                next_node="maya_forgiveness_question"
            ),
        ]
    ))

    tree.add_node(DialogueNode(
        id="maya_redemption_offer",
        speaker="Maya",
        text="*pauses* ...The show tonight. It's our last chance. If you're serious, I need you on stage. With me.",
        choices=[
            DialogueChoice(
                text="I'll be there. I promise.",
                next_node="maya_acceptance",
                effects=[
                    (DialogueEffect.SET_FLAG, "promised_maya"),
                    (DialogueEffect.SET_FLAG, "maya_path_redemption")
                ]
            ),
            DialogueChoice(
                text="On stage? I don't know if I'm ready...",
                next_node="maya_disappointment"
            ),
        ]
    ))

    tree.add_node(DialogueNode(
        id="maya_forgiveness_question",
        speaker="Maya",
        text="I don't know if I can forgive you. But maybe... maybe we can move forward. If you prove yourself tonight.",
        auto_next="maya_conditional_trust",
        effects=[(DialogueEffect.SET_FLAG, "maya_path_conditional")]
    ))

    # Critical choice node
    tree.add_node(DialogueNode(
        id="maya_needs_help",
        speaker="Maya",
        text="Look, the zombies are getting worse. We need to figure out if music really calms them. Will you help me test it?",
        choices=[
            DialogueChoice(
                text="Yes. Let's do this together.",
                next_node="maya_partnership",
                effects=[(DialogueEffect.SET_FLAG, "maya_partnership_formed")]
            ),
            DialogueChoice(
                text="I need to think about it...",
                next_node="maya_time_running_out"
            ),
            DialogueChoice(
                text="What if we make things worse?",
                next_node="maya_valid_concern"
            ),
        ]
    ))

    # Ending nodes
    tree.add_node(DialogueNode(
        id="maya_acceptance",
        speaker="Maya",
        text="*nods slowly* Okay. Don't make me regret this. Meet me at the stage when you're ready.",
        choices=[],
        effects=[
            (DialogueEffect.SET_FLAG, "maya_ending_reconciliation"),
            (DialogueEffect.GIVE_ITEM, "Maya's Guitar Pick")
        ]
    ))

    tree.add_node(DialogueNode(
        id="maya_disappointment",
        speaker="Maya",
        text="*sighs* Same old story. When it matters most, you fold. Get out of here.",
        choices=[],
        effects=[(DialogueEffect.SET_FLAG, "maya_ending_rejection")]
    ))

    tree.add_node(DialogueNode(
        id="maya_partnership",
        speaker="Maya",
        text="*smiles for the first time* That's the spirit. We're going to save this scene, one riff at a time.",
        choices=[],
        effects=[
            (DialogueEffect.SET_FLAG, "maya_ending_partners"),
            (DialogueEffect.GIVE_ITEM, "Backstage All-Access Pass"),
            (DialogueEffect.HEAL, "2")
        ]
    ))

    tree.add_node(DialogueNode(
        id="maya_bridge_burned",
        speaker="Maya",
        text="You know what? I don't need this. You want to be defensive? Fine. But don't expect my help.",
        choices=[],
        effects=[
            (DialogueEffect.SET_FLAG, "maya_ending_hostile"),
            (DialogueEffect.DAMAGE, "1")
        ]
    ))

    return tree
```

#### Adding Maya as Character

**File:** `game_data.json`

**Add to items array:**
```json
{
  "name": "Maya's Guitar Pick",
  "description": "A purple pick worn smooth by a thousand power chords. It still hums with her energy.",
  "icon_color": [200, 50, 200]
},
{
  "name": "Backstage All-Access Pass",
  "description": "Opens every door in First Avenue. Maya's signature scrawled on the back.",
  "icon_color": [255, 215, 0]
}
```

**Add new room for Maya encounter:**
```json
{
  "id": "backstage_maya",
  "name": "Maya's Dressing Room",
  "entry_message": "Posters of legends cover the walls. Maya stands with her back to you, tuning her bass.",
  "default_entry": [160, 170],
  "background": {
    "label": "Dressing Room",
    "gradient": [[40, 20, 50], [80, 40, 100], [20, 10, 30]],
    "accent_lines": [
      {"y": 120, "height": 4, "color": [200, 50, 200]},
      {"y": 145, "height": 3, "color": [100, 200, 255]}
    ],
    "shapes": [
      {"shape": "rect", "rect": [30, 85, 80, 55], "color": [60, 50, 70]},
      {"shape": "rect", "rect": [210, 80, 80, 60], "color": [55, 45, 65]}
    ],
    "label_color": [250, 220, 250]
  },
  "walkable_zones": [
    {"shape": "polygon", "points": [[20, 160], [300, 160], [300, 195], [20, 195]]}
  ],
  "hotspots": [
    {
      "name": "Maya",
      "rect": [140, 90, 40, 70],
      "walk_position": [160, 155],
      "talk_target": "maya",
      "verbs": {
        "look": "Maya 'Riot' Reyes. Purple hair, leather jacket, and an expression that could cut glass.",
        "talk": "Time to face the music."
      }
    }
  ]
}
```

**Update engine dialogue trees:**
```python
# In GameEngine.__init__, after existing dialogue trees:
self.dialogue_trees["maya"] = None  # Will be created with protagonist context
```

**Add method to GameEngine:**
```python
def start_maya_dialogue(self) -> None:
    """Start Maya dialogue with protagonist context."""
    if self.protagonist:
        maya_tree = create_maya_dialogue(self.protagonist)
        self.dialogue_trees["maya"] = maya_tree
        self.dialogue_manager.start_dialogue(
            maya_tree,
            self.inventory.get_item_names(),
            self.game_flags
        )
```

---

### 1.3 Memory System

**Goal:** Hotspots remember previous interactions and show different text when re-examined.

#### Data Structure

**File:** `zombie_quest/rooms.py`

**Modify Hotspot class:**
```python
@dataclass
class Hotspot:
    rect: pygame.Rect
    name: str
    verbs: VerbMessages
    walk_position: Optional[Tuple[int, int]] = None
    required_item: Optional[str] = None
    give_item: Optional[str] = None
    remove_item: Optional[str] = None
    talk_target: Optional[str] = None
    target_room: Optional[str] = None
    target_position: Optional[Tuple[int, int]] = None
    transition_verb: str = "use"
    requires_success_for_transition: bool = False
    transition_message: Optional[str] = None
    give_item_triggers: Tuple[str, ...] = ("use",)
    remove_item_triggers: Tuple[str, ...] = ("use",)

    # NEW: Memory system
    memory_stages: Dict[int, VerbMessages] = field(default_factory=dict)
    current_memory_stage: int = 0
    max_memory_stage: int = 0

    def message_for(self, verb: str, outcome: str = "default") -> str:
        """Get message for verb, considering memory stage."""
        # Check if we have memory-specific messages
        if self.memory_stages and self.current_memory_stage in self.memory_stages:
            stage_verbs = self.memory_stages[self.current_memory_stage]
            if outcome and outcome != "default":
                key = f"{verb}_{outcome}"
                if key in stage_verbs:
                    return stage_verbs[key]
            if verb in stage_verbs:
                return stage_verbs[verb]

        # Fall back to default message
        if outcome and outcome != "default":
            key = f"{verb}_{outcome}"
            if key in self.verbs:
                return self.verbs[key]
        default_key = f"{verb}_default"
        if default_key in self.verbs:
            return self.verbs[default_key]
        return self.verbs.get(verb, "Nothing happens.")

    def advance_memory(self) -> bool:
        """Advance to next memory stage. Returns True if advanced."""
        if self.current_memory_stage < self.max_memory_stage:
            self.current_memory_stage += 1
            return True
        return False

    def reset_memory(self) -> None:
        """Reset memory to initial stage."""
        self.current_memory_stage = 0
```

**Update Room._create_hotspot:**
```python
def _create_hotspot(self, data: Dict) -> Hotspot:
    rect = pygame.Rect(data.get("rect", [0, 0, 10, 10]))
    verbs: VerbMessages = data.get("verbs", {})
    walk_position = tuple(data.get("walk_position")) if data.get("walk_position") else None

    # NEW: Parse memory stages
    memory_stages = {}
    max_stage = 0
    if "memory_stages" in data:
        for stage_num, stage_verbs in data["memory_stages"].items():
            stage_int = int(stage_num)
            memory_stages[stage_int] = stage_verbs
            max_stage = max(max_stage, stage_int)

    return Hotspot(
        rect=rect,
        name=data.get("name", "Hotspot"),
        verbs=verbs,
        walk_position=walk_position,
        required_item=data.get("required_item"),
        give_item=data.get("give_item"),
        remove_item=data.get("remove_item"),
        talk_target=data.get("talk_target"),
        target_room=data.get("target_room"),
        target_position=tuple(data.get("target_position")) if data.get("target_position") else None,
        transition_verb=(data.get("transition_verb") or "use").lower(),
        requires_success_for_transition=bool(data.get("requires_success_for_transition", False)),
        transition_message=data.get("transition_message"),
        give_item_triggers=tuple(trigger.lower() for trigger in data.get("give_item_triggers", ["use"])),
        remove_item_triggers=tuple(trigger.lower() for trigger in data.get("remove_item_triggers", ["use"])),
        memory_stages=memory_stages,
        max_memory_stage=max_stage
    )
```

#### Example Memory Hotspot in game_data.json

```json
{
  "name": "Old Band Photo",
  "rect": [180, 90, 50, 40],
  "walk_position": [205, 165],
  "verbs": {
    "look": "A photo of you and Maya on stage. You both look so young, so full of hope."
  },
  "memory_stages": {
    "1": {
      "look": "The photo is faded now. You remember that night - the crowd went wild. Then everything fell apart."
    },
    "2": {
      "look": "You trace your finger over Maya's face. She trusted you once. Maybe... maybe she could again."
    },
    "3": {
      "look": "*You pocket the photo.* Tonight, you'll make new memories. Better ones.",
      "use": "You carefully remove the photo from the frame and slip it into your jacket."
    }
  }
}
```

**Update GameEngine.perform_hotspot_action to advance memory:**
```python
def perform_hotspot_action(self, hotspot: Hotspot, verb: Verb) -> None:
    # ... existing code ...

    # NEW: After showing message, advance memory if applicable
    if verb == Verb.LOOK and hotspot.max_memory_stage > 0:
        if hotspot.advance_memory():
            self.audio.play("memory_unlock", volume=0.3)
            # Track in protagonist if available
            if self.protagonist:
                self.protagonist.discover_memory(f"{self.current_room.id}_{hotspot.name}")
```

---

### 1.4 Four Distinct Endings

**Goal:** Implement 4 unique endings with distinct payoffs and consequences.

#### Ending System

**File:** `zombie_quest/endings.py` (NEW)

```python
"""Ending system for Zombie Quest."""
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List

class EndingType(Enum):
    LEGENDARY_SHOW = "legendary_show"
    UNDEAD_ENCORE = "undead_encore"
    ACOUSTIC_REDEMPTION = "acoustic_redemption"
    SILENT_STAGE = "silent_stage"

@dataclass
class EndingRequirements:
    """Requirements to unlock an ending."""
    required_flags: List[str]
    forbidden_flags: List[str]
    min_scene_cred: int
    min_maya_relationship: int
    required_items: List[str]

@dataclass
class Ending:
    """An ending configuration."""
    type: EndingType
    title: str
    description: str
    requirements: EndingRequirements
    cutscene_text: List[str]  # Sequence of text screens
    ending_image: str  # Image filename
    score_multiplier: float

ENDINGS = {
    EndingType.LEGENDARY_SHOW: Ending(
        type=EndingType.LEGENDARY_SHOW,
        title="Legendary Show",
        description="You and Maya united the living and the undead through the power of music. The scene will never forget this night.",
        requirements=EndingRequirements(
            required_flags=[
                "maya_partnership_formed",
                "zombie_music_discovery",
                "saved_all_npcs",
                "perfect_setlist"
            ],
            forbidden_flags=["maya_ending_hostile"],
            min_scene_cred=10,
            min_maya_relationship=7,
            required_items=["Maya's Guitar Pick", "Perfect Setlist", "Backstage All-Access Pass"]
        ),
        cutscene_text=[
            "The first chord rings out across First Avenue.",
            "Zombies and humans alike fall silent, transfixed.",
            "Maya catches your eye and grins. This is what you were meant to do.",
            "The music swells. The boundaries between living and dead dissolve.",
            "By the encore, everyone is moving as one - a single, pulsing organism of rhythm and life.",
            "You've done it. You've saved the scene.",
            "More than that - you've transcended it."
        ],
        ending_image="legendary_ending.png",
        score_multiplier=2.0
    ),

    EndingType.UNDEAD_ENCORE: Ending(
        type=EndingType.UNDEAD_ENCORE,
        title="Undead Encore",
        description="You chose the zombies over the living. Now you're one of them - undead, but forever rocking.",
        requirements=EndingRequirements(
            required_flags=[
                "embraced_undead",
                "zombie_music_discovery",
                "rejected_maya"
            ],
            forbidden_flags=["maya_partnership_formed"],
            min_scene_cred=-5,
            min_maya_relationship=-5,
            required_items=["Zombie Medallion"]
        ),
        cutscene_text=[
            "The zombie horde accepts you as one of their own.",
            "Your heartbeat slows... then stops.",
            "But the music doesn't stop. It never stops.",
            "You take the stage, pale and powerful.",
            "The zombies worship you. The living flee in terror.",
            "Maya watches from the shadows, tears streaming down her face.",
            "You've become something new. Something eternal. Something monstrous."
        ],
        ending_image="undead_ending.png",
        score_multiplier=1.5
    ),

    EndingType.ACOUSTIC_REDEMPTION: Ending(
        type=EndingType.ACOUSTIC_REDEMPTION,
        title="Acoustic Redemption",
        description="The big show didn't happen, but you and Maya played an intimate set in the alley. Sometimes smaller is better.",
        requirements=EndingRequirements(
            required_flags=[
                "maya_path_conditional",
                "acoustic_option_discovered"
            ],
            forbidden_flags=["maya_ending_hostile", "main_stage_ready"],
            min_scene_cred=0,
            min_maya_relationship=3,
            required_items=["Acoustic Guitar"]
        ),
        cutscene_text=[
            "The main stage lies dark and empty.",
            "But in the alley behind First Avenue, you and Maya set up two stools.",
            "A small crowd gathers - maybe twenty people, humans and zombies alike.",
            "No amplifiers. No effects. Just two voices and an acoustic guitar.",
            "It's raw. It's real. It's everything the scene was supposed to be.",
            "Maya smiles at you between songs. 'This is better,' she whispers.",
            "Maybe she's right."
        ],
        ending_image="acoustic_ending.png",
        score_multiplier=1.3
    ),

    EndingType.SILENT_STAGE: Ending(
        type=EndingType.SILENT_STAGE,
        title="Silent Stage",
        description="You failed. The show never happened. The scene is dead, and so are your dreams.",
        requirements=EndingRequirements(
            required_flags=[],  # Default ending if nothing else triggers
            forbidden_flags=[
                "maya_partnership_formed",
                "embraced_undead",
                "acoustic_option_discovered"
            ],
            min_scene_cred=-100,  # Always accessible
            min_maya_relationship=-100,
            required_items=[]
        ),
        cutscene_text=[
            "Showtime comes and goes.",
            "The stage remains empty. The crowd disperses.",
            "Maya doesn't even look at you as she packs up her bass.",
            "The zombies shuffle away into the Minneapolis night.",
            "You stand alone on Hennepin Avenue, watching the neon signs flicker out one by one.",
            "You had your chance. You blew it.",
            "Some stories don't have happy endings."
        ],
        ending_image="silent_ending.png",
        score_multiplier=0.5
    ),
}

def determine_ending(
    flags: Dict[str, bool],
    scene_cred: int,
    maya_relationship: int,
    inventory_items: List[str]
) -> Ending:
    """Determine which ending the player has achieved."""
    # Check endings in priority order
    priority_order = [
        EndingType.LEGENDARY_SHOW,
        EndingType.UNDEAD_ENCORE,
        EndingType.ACOUSTIC_REDEMPTION,
        EndingType.SILENT_STAGE,
    ]

    for ending_type in priority_order:
        ending = ENDINGS[ending_type]
        req = ending.requirements

        # Check required flags
        if not all(flags.get(flag, False) for flag in req.required_flags):
            continue

        # Check forbidden flags
        if any(flags.get(flag, False) for flag in req.forbidden_flags):
            continue

        # Check scene cred
        if scene_cred < req.min_scene_cred:
            continue

        # Check Maya relationship
        if maya_relationship < req.min_maya_relationship:
            continue

        # Check required items
        if not all(item in inventory_items for item in req.required_items):
            continue

        # All requirements met!
        return ending

    # Should never reach here, but return silent stage as ultimate fallback
    return ENDINGS[EndingType.SILENT_STAGE]
```

#### Ending Cutscene System

**File:** `zombie_quest/cutscene.py` (NEW)

```python
"""Cutscene system for endings and story moments."""
import pygame
from typing import List, Optional
from .config import COLORS
from .resources import load_serif_font

class Cutscene:
    """Displays a sequence of text screens with fades."""

    def __init__(self, texts: List[str], width: int, height: int):
        self.texts = texts
        self.width = width
        self.height = height
        self.current_index = 0
        self.fade_state = "fade_in"  # fade_in, display, fade_out
        self.fade_progress = 0.0
        self.display_time = 0.0
        self.fade_duration = 1.5
        self.display_duration = 4.0
        self.complete = False

        self.font = load_serif_font(18)
        self.small_font = load_serif_font(14)

    def update(self, dt: float) -> bool:
        """Update cutscene. Returns True when complete."""
        if self.complete:
            return True

        if self.fade_state == "fade_in":
            self.fade_progress += dt / self.fade_duration
            if self.fade_progress >= 1.0:
                self.fade_progress = 1.0
                self.fade_state = "display"
                self.display_time = 0.0

        elif self.fade_state == "display":
            self.display_time += dt
            if self.display_time >= self.display_duration:
                self.fade_state = "fade_out"
                self.fade_progress = 1.0

        elif self.fade_state == "fade_out":
            self.fade_progress -= dt / self.fade_duration
            if self.fade_progress <= 0.0:
                self.fade_progress = 0.0
                self.current_index += 1

                if self.current_index >= len(self.texts):
                    self.complete = True
                    return True
                else:
                    self.fade_state = "fade_in"

        return False

    def handle_input(self, event: pygame.event.Event) -> None:
        """Allow skipping with space/enter."""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                if self.fade_state == "display":
                    # Skip to fade out
                    self.fade_state = "fade_out"
                    self.fade_progress = 1.0
                elif self.fade_state == "fade_out":
                    # Skip fade out
                    self.fade_progress = 0.0

    def draw(self, surface: pygame.Surface) -> None:
        """Draw current cutscene frame."""
        if self.complete or self.current_index >= len(self.texts):
            return

        # Black background
        surface.fill((0, 0, 0))

        # Get current text
        text = self.texts[self.current_index]

        # Calculate alpha based on fade
        alpha = int(255 * self.fade_progress)

        # Wrap text
        wrapped_lines = self._wrap_text(text, self.width - 100)

        # Calculate total height
        line_height = 24
        total_height = len(wrapped_lines) * line_height
        start_y = (self.height - total_height) // 2

        # Draw each line with fade
        for i, line in enumerate(wrapped_lines):
            text_surf = self.font.render(line, True, COLORS.UI_TEXT)
            text_surf.set_alpha(alpha)
            text_x = (self.width - text_surf.get_width()) // 2
            text_y = start_y + i * line_height
            surface.blit(text_surf, (text_x, text_y))

        # Draw skip prompt if displaying
        if self.fade_state == "display":
            prompt = self.small_font.render(
                "[SPACE to continue]", True, (120, 120, 140)
            )
            prompt.set_alpha(alpha)
            surface.blit(prompt, (self.width - prompt.get_width() - 20,
                                 self.height - 40))

    def _wrap_text(self, text: str, max_width: int) -> List[str]:
        """Wrap text to fit width."""
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            test_width = self.font.size(test_line)[0]
            if test_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines
```

#### Integration with Engine

**File:** `zombie_quest/engine.py`

**Add imports:**
```python
from .endings import determine_ending, EndingType
from .cutscene import Cutscene
```

**Add to __init__:**
```python
self.cutscene: Optional[Cutscene] = None
self.ending_triggered = False
```

**Add method:**
```python
def trigger_ending(self) -> None:
    """Trigger the appropriate ending based on game state."""
    if self.ending_triggered:
        return

    self.ending_triggered = True

    # Determine ending
    scene_cred = self.protagonist.scene_cred if self.protagonist else 0
    maya_rel = self.protagonist.maya_relationship if self.protagonist else 0

    ending = determine_ending(
        self.game_flags,
        scene_cred,
        maya_rel,
        self.inventory.get_item_names()
    )

    # Create cutscene
    self.cutscene = Cutscene(
        ending.cutscene_text,
        WINDOW_SIZE[0],
        WINDOW_SIZE[1]
    )
    self.state = GameState.CUTSCENE

    # Play ending music
    self.audio.play_music(f"ending_{ending.type.value}")
```

**Update handle_events:**
```python
def handle_events(self) -> None:
    # ... existing code ...

    # NEW: Handle cutscene input
    if self.state == GameState.CUTSCENE and self.cutscene:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.cutscene.handle_input(event)
        return
```

**Update update method:**
```python
def update(self, dt: float) -> None:
    # ... existing code ...

    # NEW: Update cutscene
    if self.state == GameState.CUTSCENE and self.cutscene:
        if self.cutscene.update(dt):
            # Cutscene complete, show credits or return to menu
            self.state = GameState.CREDITS
        return
```

**Update draw method:**
```python
def draw(self) -> None:
    # ... existing code ...

    # NEW: Draw cutscene
    if self.state == GameState.CUTSCENE and self.cutscene:
        self.cutscene.draw(self.screen)
        return
```

---

## 2. Puzzle Depth & Multi-Path Design

### 2.1 Multi-Solution Paths

**Goal:** Players can solve puzzles in multiple ways, rewarding creativity and exploration.

#### Item Combination System

**File:** `zombie_quest/items.py` (NEW)

```python
"""Item combination and interaction system."""
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

@dataclass
class ItemCombination:
    """Defines a combination of two items that creates a new item or effect."""
    item_a: str
    item_b: str
    result_item: Optional[str] = None
    effect_flag: Optional[str] = None
    description: str = ""
    consumes_items: bool = True  # Whether to remove source items

# Define all possible combinations
ITEM_COMBINATIONS: List[ItemCombination] = [
    ItemCombination(
        item_a="Demo Tape",
        item_b="Setlist",
        result_item="Perfect Setlist",
        description="You match the demo tape's energy to the setlist. This will be legendary.",
        consumes_items=True
    ),
    ItemCombination(
        item_a="Guitar Pick",
        item_b="Vinyl Record",
        result_item="Improvised Lock Pick",
        description="The pick and vinyl edge combine to form a makeshift lock pick. Punk ingenuity.",
        consumes_items=False  # Keep the items
    ),
    ItemCombination(
        item_a="Gig Flyer",
        item_b="Backstage Pass",
        result_item="VIP All-Access",
        description="You carefully tape the flyer to the pass. Now you look *really* official.",
        consumes_items=True
    ),
    ItemCombination(
        item_a="Maya's Guitar Pick",
        item_b="Setlist",
        result_item="Duet Arrangement",
        description="You arrange the setlist for two players. Maya will love this.",
        consumes_items=False,
        effect_flag="duet_prepared"
    ),
    ItemCombination(
        item_a="Vinyl Record",
        item_b="Demo Tape",
        result_item="Mixed Anthology",
        description="The old and new school combine. Zombies might respond to this hybrid sound.",
        consumes_items=True,
        effect_flag="zombie_music_discovery"
    ),
]

def find_combination(item_a: str, item_b: str) -> Optional[ItemCombination]:
    """Find a valid combination between two items."""
    for combo in ITEM_COMBINATIONS:
        if (combo.item_a == item_a and combo.item_b == item_b) or \
           (combo.item_a == item_b and combo.item_b == item_a):
            return combo
    return None

class ItemCombinationUI:
    """UI for combining items."""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.visible = False
        self.selected_item_a: Optional[str] = None
        self.selected_item_b: Optional[str] = None
        self.result_message: str = ""
        self.font = load_serif_font(14)

    def show(self, item_a: str):
        """Show combination UI with first item selected."""
        self.visible = True
        self.selected_item_a = item_a
        self.selected_item_b = None
        self.result_message = f"Combine {item_a} with..."

    def try_combine(self, item_b: str) -> Optional[Tuple[ItemCombination, str]]:
        """Try to combine selected item with another. Returns (combination, message)."""
        if not self.selected_item_a:
            return None

        combo = find_combination(self.selected_item_a, item_b)
        if combo:
            self.result_message = combo.description
            return (combo, combo.description)
        else:
            self.result_message = f"{self.selected_item_a} and {item_b} don't combine in any useful way."
            return None

    def close(self):
        """Close the combination UI."""
        self.visible = False
        self.selected_item_a = None
        self.selected_item_b = None
        self.result_message = ""

    def draw(self, surface: pygame.Surface, inventory_items: List):
        """Draw combination interface."""
        if not self.visible:
            return

        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        # Draw instruction
        instruction = self.font.render(self.result_message, True, COLORS.NEON_GOLD)
        surface.blit(instruction, (self.width // 2 - instruction.get_width() // 2, 100))

        # Draw available items to combine with
        y_offset = 150
        for item in inventory_items:
            if item.name != self.selected_item_a:
                item_text = self.font.render(
                    f"  {item.name}", True, COLORS.UI_TEXT
                )
                surface.blit(item_text, (self.width // 2 - 80, y_offset))
                y_offset += 25

        # Draw prompt
        prompt = self.font.render(
            "[Click item to combine] [ESC to cancel]", True, (120, 120, 140)
        )
        surface.blit(prompt, (self.width // 2 - prompt.get_width() // 2,
                             self.height - 60))
```

#### Integration with Inventory

**File:** `zombie_quest/ui.py`

**Modify InventoryWindow class:**
```python
class InventoryWindow:
    def __init__(self, inventory: Inventory, rect: pygame.Rect):
        # ... existing code ...
        self.combination_mode = False  # NEW
        self.combining_item: Optional[Item] = None  # NEW

    def handle_event(self, event: pygame.event.Event) -> Optional[Item]:
        # ... existing mouse click handling ...

        # NEW: Right-click to enter combination mode
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            if item_clicked:
                self.combination_mode = True
                self.combining_item = item_clicked
                return None

        # NEW: In combination mode, left-click to combine
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.combination_mode and self.combining_item and item_clicked:
                # Return both items for combination
                # (Engine will handle the combination logic)
                result = (self.combining_item, item_clicked)
                self.combination_mode = False
                self.combining_item = None
                return result

    def draw(self, surface: pygame.Surface):
        # ... existing draw code ...

        # NEW: Draw combination indicator
        if self.combination_mode and self.combining_item:
            combo_text = self.font.render(
                f"Combining: {self.combining_item.name} (click another item)",
                True, COLORS.NEON_GOLD
            )
            surface.blit(combo_text, (self.rect.centerx - combo_text.get_width() // 2,
                                     self.rect.bottom + 5))
```

#### Alternative Puzzle Solutions

**File:** `game_data.json`

**Example: Multiple ways to get backstage pass**

```json
{
  "name": "Backstage Access Puzzle",
  "solutions": [
    {
      "name": "Radio DJ Path",
      "description": "Trade demo tape to DJ Rotten for backstage pass",
      "steps": [
        "Get gig flyer from kiosk",
        "Trade flyer to clerk for demo tape",
        "Trade demo tape to DJ for backstage pass"
      ],
      "difficulty": "easy"
    },
    {
      "name": "Bribery Path",
      "description": "Use vinyl record to bribe the bouncer",
      "steps": [
        "Find vinyl record in green room",
        "Offer vinyl to bouncer zombie",
        "Bouncer lets you backstage"
      ],
      "difficulty": "medium",
      "requires": ["found_green_room"]
    },
    {
      "name": "Stealth Path",
      "description": "Distract bouncer with music and sneak past",
      "steps": [
        "Find portable radio",
        "Place radio near bouncer",
        "Play music to hypnotize bouncer",
        "Sneak past while distracted"
      ],
      "difficulty": "hard",
      "requires": ["zombie_music_discovery"]
    }
  ]
}
```

#### Environmental Puzzle: Sound Board

**File:** `game_data.json`

**Add new room:**
```json
{
  "id": "sound_booth",
  "name": "Sound Booth",
  "entry_message": "Rows of sliders and knobs control the sonic destiny of the venue below.",
  "default_entry": [160, 170],
  "hotspots": [
    {
      "name": "Mixing Board",
      "rect": [120, 100, 80, 60],
      "walk_position": [160, 155],
      "verbs": {
        "look": "A 32-channel analog board. Each slider controls a different aspect of the sound.",
        "use": "You need to know the right settings to make this work.",
        "use_success": "The board lights up! Perfect EQ for zombie pacification."
      },
      "required_item": "Sound Board Manual",
      "give_item": "Zombie Pacification Mix",
      "give_item_triggers": ["use"]
    },
    {
      "name": "Frequency Analyzer",
      "rect": [40, 90, 60, 70],
      "walk_position": [70, 155],
      "verbs": {
        "look": "An oscilloscope shows frequency patterns. Wait... that pattern looks familiar.",
        "use": "You analyze the waveform. 432 Hz... the zombie resonance frequency!"
      },
      "give_item": "Frequency Note",
      "give_item_triggers": ["use"],
      "memory_stages": {
        "1": {
          "look": "The oscilloscope still shows that pattern. You sketch it onto the manual."
        }
      }
    }
  ]
}
```

**Add puzzle items:**
```json
{
  "name": "Sound Board Manual",
  "description": "A dog-eared manual for the mixing board. Several pages have coffee stains.",
  "icon_color": [180, 160, 140]
},
{
  "name": "Frequency Note",
  "description": "A sketch of the zombie resonance frequency: 432 Hz, sub-bass emphasis.",
  "icon_color": [100, 255, 100]
},
{
  "name": "Zombie Pacification Mix",
  "description": "The perfect audio mix to calm the undead. Synthesizer pads with sub-bass drones.",
  "icon_color": [150, 255, 200]
}
```

---

## 3. Thematic Integration

### 3.1 Music-Reactive Zombies

**Goal:** Zombies freeze, dance, or remember humanity when exposed to music.

#### Zombie Music Reactions

**File:** `zombie_quest/characters.py`

**Modify Zombie class:**
```python
class Zombie(Character):
    def __init__(self, position: WorldPos, zombie_type: str = "scene") -> None:
        # ... existing init code ...

        # NEW: Music reaction system
        self.music_state = "normal"  # normal, frozen, dancing, remembering
        self.music_reaction_timer = 0.0
        self.remembering_dialogue: Optional[str] = None

        # Music preferences by type
        self.favorite_genre = {
            "scene": "punk",
            "bouncer": "metal",
            "rocker": "rock",
            "dj": "electronic"
        }.get(zombie_type, "rock")

    def apply_music_effect(self, music_type: str, intensity: float, duration: float):
        """Apply music effect to zombie."""
        # Check if zombie likes this music
        if music_type == self.favorite_genre:
            # Strong reaction - dancing or remembering
            if intensity > 0.7:
                self.music_state = "remembering"
                self.remembering_dialogue = self._get_remembering_dialogue()
            else:
                self.music_state = "dancing"
        else:
            # Mild reaction - frozen/confused
            if intensity > 0.5:
                self.music_state = "frozen"
            else:
                self.music_state = "dancing"

        self.music_reaction_timer = duration

    def _get_remembering_dialogue(self) -> str:
        """Get dialogue for when zombie remembers humanity."""
        memories = {
            "scene": [
                "*groans* ...the first chord... I remember...",
                "I was... at a show... the music was...",
                "*tears of dried blood* ...I had friends..."
            ],
            "bouncer": [
                "I... protected this place... kept everyone safe...",
                "*looks at hands* These hands... stamped so many passes...",
                "The music... it made people happy..."
            ],
            "rocker": [
                "*fingers twitch like playing guitar* ...my band...",
                "We were going to make it... going to be famous...",
                "*shambles sadly* ...the dream died..."
            ],
            "dj": [
                "I... I played this song... on my show...",
                "*groans rhythmically* ...the perfect mix...",
                "People danced... they were alive... *I* was alive..."
            ]
        }
        import random
        return random.choice(memories.get(self.zombie_type, memories["scene"]))

    def update(self, dt: float, hero_position: WorldPos, room_rect: pygame.Rect) -> bool:
        """Update zombie movement with music state."""
        # Update music reaction timer
        if self.music_reaction_timer > 0:
            self.music_reaction_timer -= dt
            if self.music_reaction_timer <= 0:
                self.music_state = "normal"

        # Modify behavior based on music state
        if self.music_state == "frozen":
            # Don't move, don't chase
            self.update_animation(dt, False)
            return False

        elif self.music_state == "dancing":
            # Sway in place, don't chase
            self.wander_direction = pygame.Vector2(
                math.sin(pygame.time.get_ticks() / 500.0) * 0.3,
                0
            )
            self.update_animation(dt, True)
            self.is_chasing = False
            return False

        elif self.music_state == "remembering":
            # Stand still, face hero, show dialogue
            to_hero = pygame.Vector2(hero_position) - self.position
            if to_hero.length() > 0:
                self._update_direction(to_hero.normalize())
            self.update_animation(dt, False)
            return False

        # Normal behavior
        return super().update(dt, hero_position, room_rect)

    def draw(self, surface: pygame.Surface, room_height: int) -> pygame.Rect:
        """Draw zombie with music state indicators."""
        rect = super().draw(surface, room_height)

        # Draw music state indicator
        if self.music_state != "normal":
            indicator_colors = {
                "frozen": (100, 200, 255),
                "dancing": (255, 200, 100),
                "remembering": (255, 100, 255)
            }
            color = indicator_colors.get(self.music_state, (255, 255, 255))

            # Draw glowing circle above zombie
            glow_pos = (int(self.position.x), int(self.position.y - 40))
            for i in range(3):
                alpha = int(100 * (1 - i/3))
                radius = 8 + i * 2
                glow_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*color, alpha),
                                 (radius, radius), radius)
                surface.blit(glow_surf, (glow_pos[0] - radius, glow_pos[1] - radius))

        # Draw remembering dialogue
        if self.music_state == "remembering" and self.remembering_dialogue:
            font = pygame.font.Font(None, 12)
            # Wrap text
            max_width = 150
            words = self.remembering_dialogue.split()
            lines = []
            current_line = ""
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                if font.size(test_line)[0] <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)

            # Draw dialogue box
            box_height = len(lines) * 14 + 10
            box_width = max_width + 10
            box_x = int(self.position.x - box_width // 2)
            box_y = int(self.position.y - 60 - box_height)

            pygame.draw.rect(surface, (20, 20, 30),
                           (box_x, box_y, box_width, box_height))
            pygame.draw.rect(surface, (150, 100, 200),
                           (box_x, box_y, box_width, box_height), 1)

            # Draw text
            for i, line in enumerate(lines):
                text_surf = font.render(line, True, (200, 200, 220))
                surface.blit(text_surf, (box_x + 5, box_y + 5 + i * 14))

        return rect
```

#### Music Item System

**File:** `zombie_quest/items.py`

**Add music item class:**
```python
@dataclass
class MusicItem:
    """An item that produces music and affects zombies."""
    name: str
    music_type: str  # punk, metal, rock, electronic
    intensity: float  # 0.0 to 1.0
    duration: float  # seconds
    radius: int  # pixels
    description: str

MUSIC_ITEMS = {
    "Portable Radio": MusicItem(
        name="Portable Radio",
        music_type="rock",
        intensity=0.6,
        duration=10.0,
        radius=150,
        description="A battery-powered radio playing classic rock. Zombies seem drawn to it."
    ),
    "Vinyl Record": MusicItem(
        name="Vinyl Record",
        music_type="punk",
        intensity=0.8,
        duration=15.0,
        radius=200,
        description="'Zombie Minneapolis' by The Neon Dead. The zombies remember this album."
    ),
    "Demo Tape": MusicItem(
        name="Demo Tape",
        music_type="punk",
        intensity=0.7,
        duration=12.0,
        radius=180,
        description="Raw basement energy. Even the undead can't resist this."
    ),
    "Perfect Setlist": MusicItem(
        name="Perfect Setlist",
        music_type="rock",
        intensity=1.0,
        duration=20.0,
        radius=300,
        description="The ultimate zombie-calming playlist. This could save everyone."
    ),
}

def get_music_item(item_name: str) -> Optional[MusicItem]:
    """Get music item properties if item makes music."""
    return MUSIC_ITEMS.get(item_name)
```

#### Using Music Items

**File:** `zombie_quest/engine.py`

**Add method:**
```python
def use_music_item(self, item_name: str, position: Tuple[float, float]):
    """Use a music item to affect nearby zombies."""
    from .items import get_music_item

    music_item = get_music_item(item_name)
    if not music_item:
        self.message_box.show(f"{item_name} doesn't make music.")
        return

    # Play music sound
    self.audio.play(f"music_{music_item.music_type}", volume=0.7)

    # Affect zombies in radius
    affected_count = 0
    for zombie in self.current_room.zombies:
        zombie_pos = zombie.foot_position
        distance = math.sqrt(
            (zombie_pos[0] - position[0])**2 +
            (zombie_pos[1] - position[1])**2
        )

        if distance <= music_item.radius:
            zombie.apply_music_effect(
                music_item.music_type,
                music_item.intensity,
                music_item.duration
            )
            affected_count += 1

    # Visual effect
    self.particles.emit_burst(
        position[0], position[1],
        COLORS.NEON_GOLD,
        count=30,
        speed=100,
        lifetime=music_item.duration
    )

    # Message
    if affected_count > 0:
        self.message_box.show(
            f"The music affects {affected_count} zombie{'s' if affected_count != 1 else ''}!"
        )
        self.game_flags["zombie_music_discovery"] = True
    else:
        self.message_box.show("The music plays, but no zombies are near enough to hear.")
```

**Update perform_hotspot_action:**
```python
def perform_hotspot_action(self, hotspot: Hotspot, verb: Verb) -> None:
    # ... existing code ...

    # NEW: Allow using music items
    if verb == Verb.USE and selected_item:
        from .items import get_music_item
        music_item = get_music_item(selected_item.name)
        if music_item:
            # Use music item at hotspot location
            self.use_music_item(selected_item.name, hotspot.rect.center)
            return

    # ... rest of existing code ...
```

---

### 3.2 Diegetic Audio Sources

**Goal:** Every room has realistic audio sources (radios, stages, jukeboxes) that affect zombies.

#### Audio Source System

**File:** `zombie_quest/audio_sources.py` (NEW)

```python
"""Diegetic audio sources in rooms."""
from dataclasses import dataclass
from typing import Tuple, Optional
import pygame

@dataclass
class AudioSource:
    """A source of diegetic audio in a room."""
    position: Tuple[int, int]
    name: str
    audio_type: str  # ambient, music, radio, jukebox, stage
    music_genre: str  # punk, rock, metal, electronic
    intensity: float  # 0.0 to 1.0
    radius: int  # effective radius in pixels
    active: bool = True
    visual_indicator: bool = True  # Show glowing indicator

    def draw(self, surface: pygame.Surface, glow_time: float):
        """Draw visual indicator for audio source."""
        if not self.visual_indicator or not self.active:
            return

        # Pulsing glow
        import math
        pulse = (math.sin(glow_time * 3) + 1) / 2
        alpha = int(120 * pulse)

        # Color based on type
        colors = {
            "music": (255, 100, 200),
            "radio": (100, 200, 255),
            "jukebox": (255, 200, 100),
            "stage": (200, 100, 255),
            "ambient": (150, 150, 200)
        }
        color = colors.get(self.audio_type, (200, 200, 200))

        # Draw expanding circles
        for i in range(3):
            layer_radius = 15 + i * 8 + int(pulse * 5)
            glow_surf = pygame.Surface((layer_radius*2, layer_radius*2), pygame.SRCALPHA)
            layer_alpha = int(alpha * (1 - i/3))
            pygame.draw.circle(glow_surf, (*color, layer_alpha),
                             (layer_radius, layer_radius), layer_radius, 2)
            surface.blit(glow_surf,
                        (self.position[0] - layer_radius,
                         self.position[1] - layer_radius))

    def affects_zombie(self, zombie_pos: Tuple[float, float]) -> bool:
        """Check if this audio source affects a zombie at position."""
        if not self.active:
            return False

        import math
        distance = math.sqrt(
            (zombie_pos[0] - self.position[0])**2 +
            (zombie_pos[1] - self.position[1])**2
        )
        return distance <= self.radius
```

#### Room Audio Configuration

**File:** `game_data.json`

**Add audio sources to rooms:**
```json
{
  "id": "hennepin_outside",
  "name": "Hennepin Avenue, 1982",
  "audio_sources": [
    {
      "position": [148, 110],
      "name": "Record Store Speakers",
      "audio_type": "music",
      "music_genre": "punk",
      "intensity": 0.5,
      "radius": 100,
      "visual_indicator": true
    },
    {
      "position": [208, 100],
      "name": "First Ave Bass Rumble",
      "audio_type": "stage",
      "music_genre": "rock",
      "intensity": 0.8,
      "radius": 150,
      "visual_indicator": true
    }
  ]
}
```

**Update rooms.py:**
```python
class Room:
    def __init__(self, data: Dict) -> None:
        # ... existing init code ...

        # NEW: Audio sources
        from .audio_sources import AudioSource
        self.audio_sources: List[AudioSource] = []
        for source_data in data.get("audio_sources", []):
            self.audio_sources.append(AudioSource(
                position=tuple(source_data["position"]),
                name=source_data["name"],
                audio_type=source_data["audio_type"],
                music_genre=source_data["music_genre"],
                intensity=source_data["intensity"],
                radius=source_data["radius"],
                visual_indicator=source_data.get("visual_indicator", True)
            ))

    def update(self, dt: float, hero: Hero) -> None:
        hero_position = hero.foot_position

        for zombie in self.zombies:
            zombie_pos = zombie.foot_position

            # NEW: Check audio source effects
            for audio_source in self.audio_sources:
                if audio_source.affects_zombie(zombie_pos):
                    # Apply continuous music effect from ambient source
                    zombie.apply_music_effect(
                        audio_source.music_genre,
                        audio_source.intensity * 0.5,  # Weaker than direct items
                        dt * 2  # Refresh effect continuously
                    )

            # Update zombie
            zombie.update(dt, hero_position, self.bounds)

    def draw(self, surface: pygame.Surface, hero: Hero) -> None:
        # ... existing background draw ...

        # NEW: Draw audio sources (before characters)
        glow_time = pygame.time.get_ticks() / 1000.0
        for audio_source in self.audio_sources:
            audio_source.draw(surface, glow_time)

        # ... existing character draw ...
```

---

## 4. Juice Amplification

### 4.1 Enhanced Hitstop & Knockback

**Goal:** Increase hitstop from 2 to 6-8 frames and knockback from 120 to 300-400 px/s.

#### Hitstop System

**File:** `zombie_quest/effects.py`

**Add class:**
```python
class Hitstop:
    """Freeze-frame effect on impact."""

    def __init__(self):
        self.active = False
        self.duration = 0.0
        self.timer = 0.0

    def trigger(self, frames: int = 8, fps: int = 60):
        """Trigger hitstop for N frames."""
        self.active = True
        self.duration = frames / fps
        self.timer = 0.0

    def update(self, dt: float) -> bool:
        """Update hitstop. Returns True if time is frozen."""
        if not self.active:
            return False

        self.timer += dt
        if self.timer >= self.duration:
            self.active = False
            self.timer = 0.0
            return False

        return True

    def should_freeze_game(self) -> bool:
        """Check if game logic should be frozen."""
        return self.active
```

**Add to engine.py:**
```python
# In __init__
from .effects import Hitstop
self.hitstop = Hitstop()

# In update method
def update(self, dt: float) -> None:
    # ... audio update ...

    # NEW: Check hitstop
    if self.hitstop.update(dt):
        # Freeze game logic but keep visual effects
        self.particles.update(dt * 0.2)  # Slow motion particles
        return

    # ... rest of update logic ...

# In _damage_hero
def _damage_hero(self, amount: int) -> None:
    if self.hero.take_damage(amount):
        # Hero died
        self.state = GameState.GAME_OVER
        self.message_box.show("The neon fades to black...")
        self.audio.play("death")
        self.hitstop.trigger(frames=12, fps=60)  # Longer hitstop on death
    else:
        # Took damage but survived
        self.audio.play("hit")
        self.hitstop.trigger(frames=8, fps=60)  # NEW: 8-frame hitstop
        self.screen_shake.shake(12.0, 0.4)  # Increased shake
        self.particles.emit_damage(self.hero.position.x, self.hero.position.y - 20)

        if self.hero.health == 1:
            self.audio.play("health_low", volume=0.4)
```

#### Enhanced Knockback

**File:** `zombie_quest/characters.py`

**Modify Hero class:**
```python
class Hero(Character):
    def __init__(self, position: WorldPos) -> None:
        # ... existing init ...

        # NEW: Knockback system
        self.knockback_velocity = pygame.Vector2(0, 0)
        self.is_knocked_back = False

    def take_damage(self, amount: int = 1, knockback_direction: Optional[pygame.Vector2] = None) -> bool:
        """Take damage with optional knockback."""
        if self.is_invincible:
            return False

        self.health = max(0, self.health - amount)
        self.is_invincible = True
        self.invincibility_timer = GAMEPLAY.HERO_INVINCIBILITY_TIME
        self.flash_timer = 0.0

        # NEW: Apply knockback
        if knockback_direction:
            # Increased knockback speed: 350 px/s
            self.knockback_velocity = knockback_direction.normalize() * 350
            self.is_knocked_back = True
            # Cancel pathfinding
            self.path = []
            self.current_target = None

        return self.health <= 0

    def update(self, dt: float, room_bounds: Optional[pygame.Rect] = None,
               walkable_check: Optional[callable] = None) -> None:
        """Update hero position and animation."""
        moving = False

        # Update invincibility
        if self.is_invincible:
            self.invincibility_timer -= dt
            self.flash_timer += dt
            if self.invincibility_timer <= 0:
                self.is_invincible = False
                self.invincibility_timer = 0

        # NEW: Knockback takes highest priority
        if self.is_knocked_back:
            # Apply knockback movement
            self.position += self.knockback_velocity * dt

            # Decelerate knockback
            friction = 0.85  # Decelerates to 15% per frame at 60fps
            self.knockback_velocity *= friction ** (dt * 60)

            # Stop knockback when velocity is low
            if self.knockback_velocity.length() < 10:
                self.knockback_velocity = pygame.Vector2(0, 0)
                self.is_knocked_back = False

            # Clamp to room bounds
            if room_bounds:
                self.position.x = max(room_bounds.left + 10,
                                    min(room_bounds.right - 10, self.position.x))
                self.position.y = max(room_bounds.top + 10,
                                    min(room_bounds.bottom - 10, self.position.y))

            # Update direction
            if self.knockback_velocity.length() > 0:
                self._update_direction(self.knockback_velocity)
            moving = True

        # Rest of update (keyboard, pathfinding) only if not knocked back
        elif self.using_keyboard and self.keyboard_velocity.length_squared() > 0:
            # ... existing keyboard movement ...
            pass

        elif self.current_target is not None:
            # ... existing pathfinding movement ...
            pass

        elif self.path:
            self.current_target = self.path.pop(0)

        self.update_animation(dt, moving)
```

**Update zombie collision:**
```python
def _update_room(self, dt: float) -> None:
    """Update room entities including zombies."""
    hero_pos = self.hero.foot_position

    for zombie in self.current_room.zombies:
        room_rect = pygame.Rect(0, 0, ROOM_WIDTH, ROOM_HEIGHT)
        collision = zombie.update(dt, hero_pos, room_rect)

        if collision:
            # Calculate knockback direction (away from zombie)
            zombie_pos = zombie.foot_position
            direction = pygame.Vector2(
                hero_pos[0] - zombie_pos[0],
                hero_pos[1] - zombie_pos[1]
            )
            if direction.length() > 0:
                direction = direction.normalize()
            else:
                direction = pygame.Vector2(1, 0)  # Default direction

            self._damage_hero(1, knockback_direction=direction)

        # Zombie groans
        if zombie.should_groan():
            zombie_pos = zombie.foot_position
            self.audio.play_spatial(
                f'zombie_groan_{zombie.zombie_type}',
                source_pos=zombie_pos,
                listener_pos=hero_pos,
                volume=0.5,
                fallback_sound='zombie_groan'
            )
```

**Update _damage_hero signature:**
```python
def _damage_hero(self, amount: int, knockback_direction: Optional[pygame.Vector2] = None) -> None:
    """Apply damage to hero with optional knockback."""
    if self.hero.take_damage(amount, knockback_direction):
        # ... existing death code ...
        pass
    else:
        # ... existing damage code ...
        pass
```

---

### 4.2 Squash & Stretch

**Goal:** Apply squash & stretch deformation to character sprites for more dynamic animation.

#### Squash/Stretch System

**File:** `zombie_quest/effects.py`

**Add class:**
```python
@dataclass
class SquashStretch:
    """Squash and stretch deformation for sprites."""
    squash_x: float = 1.0  # Horizontal scale
    squash_y: float = 1.0  # Vertical scale
    target_x: float = 1.0
    target_y: float = 1.0
    recovery_speed: float = 10.0  # How fast to return to normal

    def apply_impact(self, direction: Tuple[float, float], intensity: float = 0.3):
        """Apply squash/stretch from impact in direction."""
        # Squash in direction of impact, stretch perpendicular
        dir_x, dir_y = direction

        if abs(dir_x) > abs(dir_y):
            # Horizontal impact
            self.target_x = 1.0 - intensity
            self.target_y = 1.0 + intensity * 0.5
        else:
            # Vertical impact
            self.target_x = 1.0 + intensity * 0.5
            self.target_y = 1.0 - intensity

    def apply_landing(self, intensity: float = 0.4):
        """Apply squash for landing."""
        self.target_x = 1.0 + intensity * 0.6
        self.target_y = 1.0 - intensity

    def apply_jump(self, intensity: float = 0.3):
        """Apply stretch for jumping."""
        self.target_x = 1.0 - intensity * 0.5
        self.target_y = 1.0 + intensity

    def update(self, dt: float):
        """Update squash/stretch, smoothly returning to normal."""
        # Lerp toward target
        self.squash_x += (self.target_x - self.squash_x) * self.recovery_speed * dt
        self.squash_y += (self.target_y - self.squash_y) * self.recovery_speed * dt

        # Reset target toward normal
        self.target_x += (1.0 - self.target_x) * self.recovery_speed * dt * 0.5
        self.target_y += (1.0 - self.target_y) * self.recovery_speed * dt * 0.5

    def apply_to_surface(self, surface: pygame.Surface) -> pygame.Surface:
        """Apply squash/stretch transform to a surface."""
        width = max(1, int(surface.get_width() * self.squash_x))
        height = max(1, int(surface.get_height() * self.squash_y))
        return pygame.transform.scale(surface, (width, height))

    def reset(self):
        """Reset to no deformation."""
        self.squash_x = 1.0
        self.squash_y = 1.0
        self.target_x = 1.0
        self.target_y = 1.0
```

**Update Character class:**
```python
class Character:
    def __init__(self, name: str, position: WorldPos, animations: Dict[Direction, List[pygame.Surface]], speed: float = 60.0) -> None:
        # ... existing init ...

        # NEW: Squash/stretch
        from .effects import SquashStretch
        self.squash_stretch = SquashStretch()

    def draw(self, surface: pygame.Surface, room_height: int) -> pygame.Rect:
        """Draw character with perspective scaling and squash/stretch."""
        frame = self.current_frame
        scale = self.compute_scale(room_height)
        width = max(1, int(frame.get_width() * scale))
        height = max(1, int(frame.get_height() * scale))
        scaled = pygame.transform.scale(frame, (width, height))

        # NEW: Apply squash/stretch
        scaled = self.squash_stretch.apply_to_surface(scaled)

        draw_pos = (int(self.position.x - scaled.get_width() // 2),
                   int(self.position.y - scaled.get_height()))
        surface.blit(scaled, draw_pos)
        return pygame.Rect(draw_pos, (scaled.get_width(), scaled.get_height()))

    def update_animation(self, dt: float, moving: bool) -> None:
        """Update animation frame and squash/stretch."""
        # ... existing animation code ...

        # NEW: Update squash/stretch
        self.squash_stretch.update(dt)
```

**Update Hero.take_damage:**
```python
def take_damage(self, amount: int = 1, knockback_direction: Optional[pygame.Vector2] = None) -> bool:
    # ... existing damage code ...

    # NEW: Apply squash/stretch on hit
    if knockback_direction:
        self.squash_stretch.apply_impact(
            (knockback_direction.x, knockback_direction.y),
            intensity=0.4
        )

    return self.health <= 0
```

**Add squash/stretch to movement:**
```python
# In Hero.update, when changing direction rapidly
def update(self, dt: float, ...):
    # ... existing code ...

    # NEW: Detect direction changes for squash/stretch
    if self.using_keyboard:
        new_vel = self.keyboard_velocity
        if hasattr(self, '_prev_velocity'):
            # Check for rapid direction change
            dot = self._prev_velocity.dot(new_vel)
            if dot < 0:  # Direction reversed
                self.squash_stretch.apply_impact(
                    (new_vel.x, new_vel.y),
                    intensity=0.2
                )
        self._prev_velocity = new_vel.copy()
```

---

### 4.3 Footstep Synchronization

**Goal:** Sync footstep sounds to animation frames for authentic feel.

#### Footstep System

**File:** `zombie_quest/characters.py`

**Add to Character class:**
```python
class Character:
    def __init__(self, ...):
        # ... existing init ...

        # NEW: Footstep tracking
        self.last_footstep_frame = -1
        self.footstep_frames = [0, 2]  # Frames that trigger footsteps in 4-frame walk cycle

    def update_animation(self, dt: float, moving: bool) -> None:
        """Update animation frame with footstep triggers."""
        direction = self.animation_state.direction
        frames = self.animations.get(direction, [])
        if not frames:
            return

        prev_frame = self.animation_state.frame_index

        if moving:
            self.animation_state.frame_time += dt
            frame_duration = ANIMATION.FRAME_DURATION
            if self.animation_state.frame_time >= frame_duration:
                self.animation_state.frame_time -= frame_duration
                self.animation_state.frame_index = (self.animation_state.frame_index + 1) % len(frames)

                # NEW: Check for footstep trigger
                current_frame = self.animation_state.frame_index
                if current_frame in self.footstep_frames and current_frame != prev_frame:
                    self._trigger_footstep()
        else:
            self.animation_state.frame_index = 0
            self.animation_state.frame_time = 0

        index = min(self.animation_state.frame_index, len(frames) - 1)
        self.current_frame = frames[index]
        self.idle = not moving

    def _trigger_footstep(self):
        """Trigger footstep event (override in subclasses)."""
        pass
```

**Override in Hero:**
```python
class Hero(Character):
    def _trigger_footstep(self):
        """Play footstep sound and particle."""
        # Play footstep sound (will be handled by engine)
        self.needs_footstep_sound = True

        # Slight squash on footfall
        self.squash_stretch.apply_landing(intensity=0.15)
```

**Override in Zombie:**
```python
class Zombie(Character):
    def _trigger_footstep(self):
        """Zombie shambling footstep."""
        self.needs_footstep_sound = True
        self.squash_stretch.apply_landing(intensity=0.1)
```

**Update engine to handle footsteps:**
```python
# In GameEngine.update
def update(self, dt: float) -> None:
    # ... existing code ...

    # Update hero
    self.hero.update(dt, room_bounds=room_rect, walkable_check=self.current_room.is_walkable)

    # NEW: Check for footstep
    if hasattr(self.hero, 'needs_footstep_sound') and self.hero.needs_footstep_sound:
        self.hero.needs_footstep_sound = False

        # Play footstep sound
        self.audio.play("footstep_player", volume=0.3)

        # Emit dust puff
        from .effects import DustPuffEmitter
        if not hasattr(self, 'dust_emitter'):
            self.dust_emitter = DustPuffEmitter()

        direction = None
        if self.hero.using_keyboard:
            direction = (self.hero.keyboard_velocity.x, self.hero.keyboard_velocity.y)

        self.dust_emitter.emit(self.hero.foot_position, direction)

    # Update dust puffs
    if hasattr(self, 'dust_emitter'):
        self.dust_emitter.update(dt)

    # Update room and zombies
    self._update_room(dt)

    # NEW: Check zombie footsteps
    for zombie in self.current_room.zombies:
        if hasattr(zombie, 'needs_footstep_sound') and zombie.needs_footstep_sound:
            zombie.needs_footstep_sound = False
            zombie_pos = zombie.foot_position
            hero_pos = self.hero.foot_position
            self.audio.play_spatial(
                "footstep_zombie",
                source_pos=zombie_pos,
                listener_pos=hero_pos,
                volume=0.2,
                fallback_sound="footstep_zombie"
            )

# In draw method, draw dust puffs
def draw(self) -> None:
    # ... existing room draw ...

    # Draw dust puffs
    if hasattr(self, 'dust_emitter'):
        self.dust_emitter.draw(self.room_surface)

    # ... rest of draw ...
```

---

## 5. Implementation Roadmap

### Week 1: Foundation Systems

**Days 1-2: Backstory & Protagonist System**
- [ ] Create `protagonist.py` with backstory types
- [ ] Create backstory selection UI
- [ ] Integrate with engine initialization
- [ ] Add backstory save/load
- [ ] Test: All three backstories playable

**Days 3-4: Maya Dialogue Tree**
- [ ] Implement Maya dialogue tree (8-10 nodes)
- [ ] Add Maya room and character
- [ ] Connect dialogue to backstory system
- [ ] Add Maya relationship tracking
- [ ] Test: All dialogue paths accessible

**Days 5-7: Memory System & Multi-Endings**
- [ ] Implement memory stages for hotspots
- [ ] Update game_data.json with memory hotspots
- [ ] Create endings.py and cutscene.py
- [ ] Implement 4 distinct endings
- [ ] Add ending determination logic
- [ ] Test: Each ending reachable

**Weekend: Testing & Polish**
- [ ] Full playthrough of each path
- [ ] Bug fixes
- [ ] Balance relationship/cred requirements

---

### Week 2: Puzzle Depth

**Days 8-9: Item Combination**
- [ ] Create items.py with combination system
- [ ] Add combination UI to inventory
- [ ] Define 8-10 item combinations
- [ ] Update game_data.json with combo items
- [ ] Test: All combinations work

**Days 10-11: Multi-Path Puzzles**
- [ ] Document alternative puzzle solutions
- [ ] Add stealth path items/mechanics
- [ ] Add bribery path interactions
- [ ] Add lockpicking mechanics
- [ ] Test: Each path completable

**Days 12-14: Environmental Puzzles**
- [ ] Create sound booth room
- [ ] Add sound board puzzle
- [ ] Create setlist decoding puzzle
- [ ] Add frequency analyzer puzzle
- [ ] Test: Puzzles solvable and satisfying

**Weekend: Puzzle Testing**
- [ ] Playtest all puzzle paths
- [ ] Adjust difficulty curves
- [ ] Add hints for stuck players

---

### Week 3: Thematic Integration

**Days 15-16: Music-Reactive Zombies**
- [ ] Update Zombie class with music states
- [ ] Add music reaction animations
- [ ] Implement "remembering" dialogue
- [ ] Create music items with effects
- [ ] Test: Zombies react appropriately

**Days 17-18: Diegetic Audio Sources**
- [ ] Create audio_sources.py
- [ ] Add audio sources to all rooms
- [ ] Implement visual indicators
- [ ] Add ambient zombie effects
- [ ] Test: Audio sources affect gameplay

**Days 19-21: Music Stealth Mechanics**
- [ ] Refine zombie detection with music
- [ ] Add music-based puzzle solutions
- [ ] Create "zombie pacification" items
- [ ] Balance music effects
- [ ] Test: Music gameplay feels impactful

**Weekend: Thematic Polish**
- [ ] Ensure thematic consistency
- [ ] Add more zombie memory dialogue
- [ ] Polish audio source visuals

---

### Week 4: Juice & Polish

**Days 22-23: Enhanced Hitstop & Knockback**
- [ ] Implement Hitstop class
- [ ] Increase hitstop to 8 frames
- [ ] Upgrade knockback to 350px/s
- [ ] Add screen shake enhancement
- [ ] Test: Combat feels impactful

**Days 24-25: Squash & Stretch**
- [ ] Implement SquashStretch class
- [ ] Apply to all character movement
- [ ] Add impact deformations
- [ ] Add direction-change deformations
- [ ] Test: Animation feels alive

**Days 26-27: Footstep Sync & Polish**
- [ ] Sync footsteps to animation frames
- [ ] Add dust puff effects
- [ ] Implement spatial footstep audio
- [ ] Add surface-specific sounds (optional)
- [ ] Test: Movement feels grounded

**Day 28: Final Polish**
- [ ] Full game balance pass
- [ ] Visual effects polish
- [ ] Audio mix polish
- [ ] Performance optimization
- [ ] Bug fixes

**Days 29-30: QA & Launch Prep**
- [ ] Complete playthrough testing
- [ ] Achievement testing
- [ ] Save/load testing
- [ ] Accessibility testing
- [ ] Documentation update
- [ ] Build release candidate

---

## 6. Testing & Validation

### Testing Checklist

#### Story & Narrative
- [ ] All three backstories playable start-to-finish
- [ ] Maya dialogue accessible for each backstory
- [ ] All dialogue choices lead to valid outcomes
- [ ] Relationship system affects dialogue correctly
- [ ] Memory system progresses hotspots
- [ ] Each of 4 endings reachable
- [ ] Ending requirements correctly evaluated
- [ ] Cutscenes display properly
- [ ] Save/load preserves story state

#### Puzzle Depth
- [ ] All item combinations work
- [ ] Each puzzle has 2+ solutions
- [ ] Alternative paths completable
- [ ] Sound board puzzle solvable
- [ ] Setlist puzzle solvable
- [ ] Combination UI functional
- [ ] Puzzles provide appropriate hints
- [ ] Dead-ends avoided

#### Thematic Integration
- [ ] Zombies react to all music types
- [ ] Music states (frozen, dancing, remembering) visible
- [ ] Audio sources affect zombies in radius
- [ ] Music items work as expected
- [ ] Zombie dialogue appears correctly
- [ ] Music-based stealth functional
- [ ] Thematic consistency maintained

#### Juice
- [ ] Hitstop triggers on damage
- [ ] Knockback feels powerful
- [ ] Squash/stretch on all characters
- [ ] Footsteps sync to animation
- [ ] Dust puffs spawn correctly
- [ ] Screen shake appropriate
- [ ] Particles enhance impacts
- [ ] Audio punch matches visuals

### Performance Targets
- Maintain 60 FPS on target hardware
- < 100ms input latency
- < 2 second load times
- < 50MB memory usage
- No dropped frames during juice effects

### Accessibility Validation
- All features work with colorblind modes
- Reduced motion mode disables intense effects
- Font size options work with new UI
- Dialogue readable at all sizes
- Audio cues supplement visual feedback

---

## Appendix A: File Structure

```
zombie_quest/
├── engine.py           # MODIFY: Add protagonist, cutscenes, endings
├── dialogue.py         # MODIFY: Add Maya dialogue tree
├── characters.py       # MODIFY: Music reactions, squash/stretch, footsteps
├── effects.py          # MODIFY: Add Hitstop, enhanced SquashStretch
├── rooms.py            # MODIFY: Audio sources, memory system
├── ui.py               # MODIFY: Backstory selection, combination UI
├── protagonist.py      # NEW: Backstory and character progression
├── endings.py          # NEW: Ending system and requirements
├── cutscene.py         # NEW: Cutscene playback
├── items.py            # NEW: Item combination and music items
├── audio_sources.py    # NEW: Diegetic audio in rooms
└── config.py           # MODIFY: Add new game states

game_data.json          # MODIFY: Add new rooms, items, puzzles
```

## Appendix B: Data Requirements

### New Items Needed
- Maya's Guitar Pick
- Backstage All-Access Pass
- Perfect Setlist
- Duet Arrangement
- Mixed Anthology
- Improvised Lock Pick
- VIP All-Access
- Sound Board Manual
- Frequency Note
- Zombie Pacification Mix
- Portable Radio
- Acoustic Guitar
- Zombie Medallion

### New Rooms Needed
- Maya's Dressing Room
- Sound Booth
- Acoustic Alley (for ending)

### New Audio Needed
- Ending music tracks (4)
- Footstep sounds (player, zombie)
- Music genre samples (punk, rock, metal, electronic)
- Memory unlock sound
- Combination success sound

---

## Appendix C: Code Integration Points

### Priority 1: Core Systems
1. Protagonist initialization (engine.py __init__)
2. Backstory selection (before game starts)
3. Maya dialogue integration (when entering Maya's room)
4. Ending trigger (when criteria met)

### Priority 2: Gameplay Systems
5. Item combination (inventory interaction)
6. Music item usage (USE verb on music items)
7. Zombie music reactions (zombie update loop)
8. Audio source effects (room update loop)

### Priority 3: Polish Systems
9. Hitstop on damage (damage handler)
10. Enhanced knockback (collision handler)
11. Squash/stretch (character animation)
12. Footstep sync (animation frames)

---

**End of Implementation Specification**

This document provides the complete blueprint for transforming Zombie Quest from a technical prototype into an all-time classic. Each system builds on existing code while adding depth, emotion, and polish.

Execute this plan methodically, test thoroughly, and the result will be a game that players remember forever. The Minneapolis scene needs you. Make it legendary.
