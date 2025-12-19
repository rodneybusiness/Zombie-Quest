"""Dialogue tree system for branching conversations."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple
from enum import Enum

import pygame

from .config import COLORS, ANIMATION
from .resources import load_serif_font


class DialogueEffect(Enum):
    """Effects that can happen during dialogue."""
    NONE = "none"
    GIVE_ITEM = "give_item"
    REMOVE_ITEM = "remove_item"
    SET_FLAG = "set_flag"
    CLEAR_FLAG = "clear_flag"
    HEAL = "heal"
    DAMAGE = "damage"


@dataclass
class DialogueChoice:
    """A choice the player can make in dialogue."""
    text: str
    next_node: Optional[str] = None  # None means end dialogue
    requirements: List[str] = field(default_factory=list)  # Items or flags required
    effects: List[Tuple[DialogueEffect, str]] = field(default_factory=list)
    visible_when_unavailable: bool = True  # Show grayed out if requirements not met

    def is_available(self, inventory_items: List[str], flags: Dict[str, bool]) -> bool:
        """Check if this choice is currently available."""
        for req in self.requirements:
            if req.startswith("!"):  # Negative requirement
                if req[1:] in inventory_items or flags.get(req[1:], False):
                    return False
            else:
                if req not in inventory_items and not flags.get(req, False):
                    return False
        return True


@dataclass
class DialogueNode:
    """A node in the dialogue tree."""
    id: str
    speaker: str
    text: str
    choices: List[DialogueChoice] = field(default_factory=list)
    auto_next: Optional[str] = None  # Automatically go to next node (for NPC monologues)
    conditions: List[str] = field(default_factory=list)  # Conditions to show this node
    effects: List[Tuple[DialogueEffect, str]] = field(default_factory=list)  # Effects on entering node
    portrait: Optional[str] = None  # Character portrait to show


class DialogueTree:
    """A complete dialogue tree for a character."""

    def __init__(self, character_name: str) -> None:
        self.character_name = character_name
        self.nodes: Dict[str, DialogueNode] = {}
        self.start_node: Optional[str] = None
        self.fallback_node: Optional[str] = None  # Used when no conditions match

    def add_node(self, node: DialogueNode) -> None:
        """Add a node to the tree."""
        self.nodes[node.id] = node
        if self.start_node is None:
            self.start_node = node.id

    def get_starting_node(self, inventory_items: List[str], flags: Dict[str, bool]) -> Optional[DialogueNode]:
        """Get the appropriate starting node based on current state."""
        # Check nodes with conditions first
        for node in self.nodes.values():
            if node.conditions:
                all_met = True
                for cond in node.conditions:
                    if cond.startswith("!"):
                        if cond[1:] in inventory_items or flags.get(cond[1:], False):
                            all_met = False
                            break
                    else:
                        if cond not in inventory_items and not flags.get(cond, False):
                            all_met = False
                            break
                if all_met:
                    return node

        # Fall back to start node
        if self.start_node:
            return self.nodes.get(self.start_node)
        return None


class DialogueManager:
    """Manages active dialogues and rendering."""

    def __init__(self, screen_width: int, screen_height: int) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.active = False
        self.current_tree: Optional[DialogueTree] = None
        self.current_node: Optional[DialogueNode] = None
        self.selected_choice: int = 0

        # Text display
        self.displayed_text = ""
        self.full_text = ""
        self.text_timer = 0.0
        self.text_speed = 30  # Characters per second
        self.text_complete = False

        # Callbacks for effects
        self.effect_callback: Optional[Callable[[DialogueEffect, str], None]] = None

        # Fonts
        self.name_font = load_serif_font(16)
        self.text_font = load_serif_font(14)
        self.choice_font = load_serif_font(12)

        # Box dimensions
        self.box_height = 100
        self.box_margin = 10
        self.box_rect = pygame.Rect(
            self.box_margin,
            screen_height - self.box_height - self.box_margin,
            screen_width - self.box_margin * 2,
            self.box_height
        )

    def start_dialogue(self, tree: DialogueTree, inventory_items: List[str],
                       flags: Dict[str, bool]) -> bool:
        """Start a dialogue. Returns True if dialogue started."""
        node = tree.get_starting_node(inventory_items, flags)
        if not node:
            return False

        self.active = True
        self.current_tree = tree
        self._enter_node(node)
        return True

    def _enter_node(self, node: DialogueNode) -> None:
        """Enter a dialogue node."""
        self.current_node = node
        self.full_text = node.text
        self.displayed_text = ""
        self.text_timer = 0.0
        self.text_complete = False
        self.selected_choice = 0

        # Apply node effects
        for effect, value in node.effects:
            if self.effect_callback:
                self.effect_callback(effect, value)

    def update(self, dt: float, inventory_items: List[str], flags: Dict[str, bool]) -> None:
        """Update the dialogue display."""
        if not self.active or not self.current_node:
            return

        # Typewriter effect
        if not self.text_complete:
            self.text_timer += dt * self.text_speed
            chars_to_show = int(self.text_timer)
            if chars_to_show >= len(self.full_text):
                self.displayed_text = self.full_text
                self.text_complete = True
            else:
                self.displayed_text = self.full_text[:chars_to_show]

    def handle_input(self, event: pygame.event.Event, inventory_items: List[str],
                     flags: Dict[str, bool]) -> Optional[List[Tuple[DialogueEffect, str]]]:
        """Handle input during dialogue. Returns effects to apply if any."""
        if not self.active or not self.current_node:
            return None

        if event.type != pygame.KEYDOWN:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Click to advance or select
                return self._handle_advance(inventory_items, flags)
            return None

        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            return self._handle_advance(inventory_items, flags)
        elif event.key == pygame.K_UP:
            self._move_selection(-1, inventory_items, flags)
        elif event.key == pygame.K_DOWN:
            self._move_selection(1, inventory_items, flags)
        elif event.key == pygame.K_ESCAPE:
            self.end_dialogue()

        return None

    def _handle_advance(self, inventory_items: List[str],
                        flags: Dict[str, bool]) -> Optional[List[Tuple[DialogueEffect, str]]]:
        """Handle advancing the dialogue."""
        if not self.text_complete:
            # Skip to full text
            self.displayed_text = self.full_text
            self.text_complete = True
            return None

        node = self.current_node
        if not node:
            return None

        # Check for auto-advance
        if node.auto_next and not node.choices:
            next_node = self.current_tree.nodes.get(node.auto_next) if self.current_tree else None
            # Guard against self-referencing loops
            if next_node and next_node.id != node.id:
                self._enter_node(next_node)
            else:
                self.end_dialogue()
            return None

        # Handle choice selection
        if node.choices:
            available_choices = [c for c in node.choices
                               if c.is_available(inventory_items, flags)]
            if self.selected_choice < len(available_choices):
                choice = available_choices[self.selected_choice]
                effects = list(choice.effects)

                if choice.next_node and self.current_tree:
                    next_node = self.current_tree.nodes.get(choice.next_node)
                    if next_node:
                        self._enter_node(next_node)
                        return effects

                self.end_dialogue()
                return effects
        else:
            # No choices, end dialogue
            self.end_dialogue()

        return None

    def _move_selection(self, direction: int, inventory_items: List[str],
                        flags: Dict[str, bool]) -> None:
        """Move the choice selection."""
        if not self.current_node or not self.current_node.choices:
            return

        available_choices = [c for c in self.current_node.choices
                           if c.is_available(inventory_items, flags)]
        if not available_choices:
            return

        self.selected_choice = (self.selected_choice + direction) % len(available_choices)

    def end_dialogue(self) -> None:
        """End the current dialogue."""
        self.active = False
        self.current_tree = None
        self.current_node = None

    def draw(self, surface: pygame.Surface, inventory_items: List[str],
             flags: Dict[str, bool]) -> None:
        """Draw the dialogue box."""
        if not self.active or not self.current_node:
            return

        node = self.current_node

        # Draw box background
        box_surf = pygame.Surface((self.box_rect.width, self.box_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(box_surf, (*COLORS.UI_DARK, 230), box_surf.get_rect())
        pygame.draw.rect(box_surf, COLORS.UI_BORDER, box_surf.get_rect(), 2)

        # Draw speaker name
        if node.speaker:
            name_surf = self.name_font.render(node.speaker, True, COLORS.HOT_MAGENTA)
            box_surf.blit(name_surf, (10, 8))

        # Draw text
        y_offset = 28
        text_lines = self._wrap_text(self.displayed_text, self.box_rect.width - 20)
        for line in text_lines[:3]:  # Max 3 lines
            text_surf = self.text_font.render(line, True, COLORS.UI_TEXT)
            box_surf.blit(text_surf, (10, y_offset))
            y_offset += 16

        # Draw choices if text is complete
        if self.text_complete and node.choices:
            available_choices = [c for c in node.choices
                               if c.is_available(inventory_items, flags)]

            choice_y = self.box_rect.height - 10 - len(available_choices) * 14
            for i, choice in enumerate(available_choices):
                prefix = "> " if i == self.selected_choice else "  "
                color = COLORS.NEON_GOLD if i == self.selected_choice else COLORS.UI_TEXT
                choice_surf = self.choice_font.render(prefix + choice.text, True, color)
                box_surf.blit(choice_surf, (10, choice_y))
                choice_y += 14
        elif self.text_complete and not node.choices:
            # Show continue prompt
            prompt = self.choice_font.render("[Press SPACE to continue]", True, (150, 150, 170))
            box_surf.blit(prompt, (self.box_rect.width - prompt.get_width() - 10,
                                   self.box_rect.height - 20))

        surface.blit(box_surf, self.box_rect.topleft)

    def _wrap_text(self, text: str, max_width: int) -> List[str]:
        """Wrap text to fit within max_width."""
        words = text.split(' ')
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            test_width = self.text_font.size(test_line)[0]
            if test_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines


# Pre-built dialogue trees for NPCs
def create_clerk_dialogue() -> DialogueTree:
    """Create dialogue tree for the record store clerk."""
    tree = DialogueTree("Record Store Clerk")

    # Starting state - no flyer
    tree.add_node(DialogueNode(
        id="start_no_flyer",
        speaker="Clerk",
        text="Scene kids only. What have you got for me?",
        choices=[
            DialogueChoice(
                text="Just browsing the stacks.",
                next_node="browsing"
            ),
            DialogueChoice(
                text="Looking for something rare.",
                next_node="rare"
            ),
            DialogueChoice(
                text="[Show Gig Flyer]",
                next_node="show_flyer",
                requirements=["Gig Flyer"]
            ),
        ],
        conditions=["!talked_to_clerk"]
    ))

    tree.add_node(DialogueNode(
        id="browsing",
        speaker="Clerk",
        text="Plenty of wax to dig through. Let me know if you find something choice.",
        choices=[],
        effects=[(DialogueEffect.SET_FLAG, "talked_to_clerk")]
    ))

    tree.add_node(DialogueNode(
        id="rare",
        speaker="Clerk",
        text="I might have something in the back... but you'll need to prove you're part of the scene first.",
        choices=[
            DialogueChoice(
                text="How do I do that?",
                next_node="how_prove"
            ),
            DialogueChoice(
                text="[Show Gig Flyer]",
                next_node="show_flyer",
                requirements=["Gig Flyer"]
            ),
        ]
    ))

    tree.add_node(DialogueNode(
        id="how_prove",
        speaker="Clerk",
        text="Grab a flyer from the kiosk outside First Avenue. That'll show you know what's happening tonight.",
        choices=[]
    ))

    tree.add_node(DialogueNode(
        id="show_flyer",
        speaker="Clerk",
        text="Alright, you're legit. Here - take this demo tape. The band's gonna be huge... if they survive the night.",
        choices=[],
        effects=[
            (DialogueEffect.GIVE_ITEM, "Demo Tape"),
            (DialogueEffect.REMOVE_ITEM, "Gig Flyer"),
            (DialogueEffect.SET_FLAG, "got_demo_tape")
        ]
    ))

    # After getting demo tape
    tree.add_node(DialogueNode(
        id="after_tape",
        speaker="Clerk",
        text="Good luck out there. Take that demo to the college radio station - they might hook you up.",
        choices=[],
        conditions=["got_demo_tape"]
    ))

    return tree


def create_dj_dialogue() -> DialogueTree:
    """Create dialogue tree for the radio DJ."""
    tree = DialogueTree("DJ Rotten")

    tree.add_node(DialogueNode(
        id="start",
        speaker="DJ Rotten",
        text="You're listening to KJRR, your voice in the underground... Wait, you're alive? Most of our listeners are, uh, undead these days.",
        choices=[
            DialogueChoice(
                text="Got anything to get me backstage at First Ave?",
                next_node="backstage_ask"
            ),
            DialogueChoice(
                text="[Offer Demo Tape]",
                next_node="offer_tape",
                requirements=["Demo Tape"]
            ),
            DialogueChoice(
                text="Just checking out the station.",
                next_node="just_looking"
            ),
        ],
        conditions=["!got_backstage_pass"]
    ))

    tree.add_node(DialogueNode(
        id="backstage_ask",
        speaker="DJ Rotten",
        text="First Avenue? On a night like this? You'd need a backstage pass, and I don't give those to just anyone. Bring me something fresh for the airwaves.",
        choices=[]
    ))

    tree.add_node(DialogueNode(
        id="offer_tape",
        speaker="DJ Rotten",
        text="*pops the tape in* ...Oh yeah. Oh YEAH. This is the raw stuff. Bass drops like a coffin lid. You've earned this, rocker.",
        choices=[],
        effects=[
            (DialogueEffect.GIVE_ITEM, "Backstage Pass"),
            (DialogueEffect.REMOVE_ITEM, "Demo Tape"),
            (DialogueEffect.SET_FLAG, "got_backstage_pass")
        ]
    ))

    tree.add_node(DialogueNode(
        id="just_looking",
        speaker="DJ Rotten",
        text="Feel free to soak in the vibes. Just don't touch the mixing board - it's possessed. Literally.",
        choices=[]
    ))

    # After getting pass
    tree.add_node(DialogueNode(
        id="after_pass",
        speaker="DJ Rotten",
        text="That pass will get you past the bouncer. Tell 'em Rotten sent you. Now get out there and rock the undead!",
        choices=[],
        conditions=["got_backstage_pass"]
    ))

    return tree
