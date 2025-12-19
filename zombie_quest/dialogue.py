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


def create_maya_dialogue() -> DialogueTree:
    """Create dialogue tree for Maya - the emotional climax of the game.

    This dialogue adapts to the player's backstory and determines the ending.
    Maya is your former bandmate, half-transformed into a zombie, standing at the
    edge of the rooftop. She represents everything you've sacrificed for your art.
    """
    tree = DialogueTree("Maya")

    # Entry nodes - different based on backstory

    # SELLOUT BACKSTORY - Maya is bitter about your betrayal
    tree.add_node(DialogueNode(
        id="start_sellout",
        speaker="Maya",
        text="Of course it's you. The one who got out. The one who made it. Tell me—was it worth it? The contracts, the compromises, the lies?",
        choices=[
            DialogueChoice(
                text="I'm sorry. I should have brought you with me.",
                next_node="sellout_apology",
            ),
            DialogueChoice(
                text="I did what I had to do. The scene was dying anyway.",
                next_node="sellout_defensive",
            ),
            DialogueChoice(
                text="None of it mattered without you. That's why I'm here.",
                next_node="sellout_confession",
            ),
        ],
        conditions=["backstory_sellout"]
    ))

    tree.add_node(DialogueNode(
        id="sellout_apology",
        speaker="Maya",
        text="Sorry? SORRY?! You left me in basement clubs while you posed for magazine covers. You don't get to apologize your way out of this.",
        choices=[
            DialogueChoice(
                text="You're right. I was a coward. But I'm here now.",
                next_node="maya_moment_truth",
            ),
            DialogueChoice(
                text="I came back, didn't I? That should mean something.",
                next_node="maya_rejection_path",
            ),
        ]
    ))

    tree.add_node(DialogueNode(
        id="sellout_defensive",
        speaker="Maya",
        text="*laughs bitterly* Classic. Even now, you can't admit you were wrong. You sold us out. You sold ME out. And for what? A Billboard chart position?",
        choices=[
            DialogueChoice(
                text="I... you're right. I fucked up. I fucked up everything.",
                next_node="maya_moment_truth",
            ),
            DialogueChoice(
                text="At least I'm not the one turning into a zombie.",
                next_node="cruel_path",
            ),
        ]
    ))

    tree.add_node(DialogueNode(
        id="sellout_confession",
        speaker="Maya",
        text="*her expression softens slightly* ...The infection is spreading. I can feel it. My fingers don't remember the chords anymore. They remember... hunger.",
        choices=[
            DialogueChoice(
                text="Then let's play one last show. Together. Before it's too late.",
                next_node="maya_hope_path",
            ),
            DialogueChoice(
                text="Maybe the transformation isn't an ending. Maybe it's evolution.",
                next_node="transcendence_path",
            ),
        ]
    ))

    # PURIST BACKSTORY - Maya respects you but questions your arrival
    tree.add_node(DialogueNode(
        id="start_purist",
        speaker="Maya",
        text="You always kept the faith. Never sold out, never compromised. But now you're here, on a night like this. Why? To save me? Or to save your conscience?",
        choices=[
            DialogueChoice(
                text="Because you'd do the same for me.",
                next_node="purist_loyalty",
            ),
            DialogueChoice(
                text="Because the scene needs you. The music needs you.",
                next_node="purist_idealism",
            ),
            DialogueChoice(
                text="Because I... because I can't lose you.",
                next_node="purist_honesty",
            ),
        ],
        conditions=["backstory_purist"]
    ))

    tree.add_node(DialogueNode(
        id="purist_loyalty",
        speaker="Maya",
        text="Would I? Would I risk infection, risk everything, for someone too proud to admit they care? You always hid behind the music. Behind the 'art.'",
        choices=[
            DialogueChoice(
                text="Then let me be honest now: I need you. The music needs you. I need you.",
                next_node="maya_moment_truth",
            ),
            DialogueChoice(
                text="The art IS what matters. And together, we can still create it.",
                next_node="maya_hope_path",
            ),
        ]
    ))

    tree.add_node(DialogueNode(
        id="purist_idealism",
        speaker="Maya",
        text="*bitter laugh* The scene. Always the scene. What about what I need? What about what I want? I'm not a symbol. I'm not your muse. I'm dying here.",
        choices=[
            DialogueChoice(
                text="You're right. This isn't about the scene. It's about you. About us.",
                next_node="maya_moment_truth",
            ),
            DialogueChoice(
                text="Then die for something beautiful. Die making the music that matters.",
                next_node="cruel_path",
            ),
        ]
    ))

    tree.add_node(DialogueNode(
        id="purist_honesty",
        speaker="Maya",
        text="*eyes widen* ...Finally. Finally you say it. After all these years of pretending it was just about the music. *she steps closer* But is it too late?",
        choices=[
            DialogueChoice(
                text="It's never too late. Come back with me. We'll find a cure, we'll—",
                next_node="maya_hope_path",
            ),
            DialogueChoice(
                text="Maybe. But we can have this moment. This one perfect moment.",
                next_node="transcendence_path",
            ),
        ]
    ))

    # SURVIVOR BACKSTORY - Maya is both hopeful and skeptical
    tree.add_node(DialogueNode(
        id="start_survivor",
        speaker="Maya",
        text="You're still standing. After everything—the overdoses, the closures, the funerals—you're still here. So am I. Barely. What's one more survivor's story, right?",
        choices=[
            DialogueChoice(
                text="This isn't just another tragedy. We can still make it out.",
                next_node="survivor_optimism",
            ),
            DialogueChoice(
                text="Maybe survival isn't always the point. Maybe art is.",
                next_node="survivor_acceptance",
            ),
            DialogueChoice(
                text="I'm tired of losing people. I'm tired of being the one left behind.",
                next_node="survivor_weariness",
            ),
        ],
        conditions=["backstory_survivor"]
    ))

    tree.add_node(DialogueNode(
        id="survivor_optimism",
        speaker="Maya",
        text="*shakes head* You still believe. After everything, you still believe in happy endings. God, I wish I had that. I can feel the infection spreading. Soon I won't be me anymore.",
        choices=[
            DialogueChoice(
                text="Then we fight it. Together. We've survived worse.",
                next_node="maya_hope_path",
            ),
            DialogueChoice(
                text="Maybe 'you' is bigger than just being human. Maybe you can still be Maya.",
                next_node="transcendence_path",
            ),
        ]
    ))

    tree.add_node(DialogueNode(
        id="survivor_acceptance",
        speaker="Maya",
        text="*smiles sadly* There it is. The survivor's philosophy. We endure for the art, for the music, for something bigger than ourselves. But what if I'm just... tired?",
        choices=[
            DialogueChoice(
                text="Then rest. But rest alive. Rest human. Let me help you.",
                next_node="maya_moment_truth",
            ),
            DialogueChoice(
                text="Then let's make one last beautiful thing before the end.",
                next_node="maya_hope_path",
            ),
        ]
    ))

    tree.add_node(DialogueNode(
        id="survivor_weariness",
        speaker="Maya",
        text="*reaches out, her hand trembling* Me too. God, me too. I'm so tired of fighting. But... *she pulls her hand back* I'm scared. I'm so scared of what I'm becoming.",
        choices=[
            DialogueChoice(
                text="*takes her hand* Then don't face it alone. Let's fight this together.",
                next_node="maya_moment_truth",
            ),
            DialogueChoice(
                text="What if becoming something new isn't the end? What if it's freedom?",
                next_node="transcendence_path",
            ),
        ]
    ))

    # CRITICAL NODES - These determine the ending

    tree.add_node(DialogueNode(
        id="maya_moment_truth",
        speaker="Maya",
        text="*tears in her eyes* I want to believe you. I want to believe we can fix this. But look at me—I'm already halfway gone. Can you really accept that?",
        choices=[
            DialogueChoice(
                text="I accept all of you. Human, infected, whatever. You're still Maya.",
                next_node="redemption_path",
                effects=[(DialogueEffect.SET_FLAG, "maya_acceptance")]
            ),
            DialogueChoice(
                text="I... I don't know if I can watch you turn into a monster.",
                next_node="abandonment_path",
            ),
        ]
    ))

    tree.add_node(DialogueNode(
        id="redemption_path",
        speaker="Maya",
        text="*sobbing* God. Goddammit. You actually mean it. After everything, you... *she collapses into your arms* Okay. Okay. Let's go back. Let's try. Let's play that show together.",
        choices=[],
        effects=[
            (DialogueEffect.SET_FLAG, "maya_saved"),
            (DialogueEffect.SET_FLAG, "maya_forgiven"),
            (DialogueEffect.SET_FLAG, "redemption_achieved")
        ]
    ))

    tree.add_node(DialogueNode(
        id="maya_hope_path",
        speaker="Maya",
        text="One last show. Together. Like the old days, before everything got complicated. Before the infection, before the scene died, before... *she picks up her guitar* Yeah. Let's make it count.",
        choices=[
            DialogueChoice(
                text="This isn't goodbye. This is the beginning of something new.",
                next_node="redemption_path",
            ),
            DialogueChoice(
                text="Let's make it legendary. Whatever happens after.",
                next_node="bittersweet_path",
                effects=[(DialogueEffect.SET_FLAG, "last_show_together")]
            ),
        ]
    ))

    tree.add_node(DialogueNode(
        id="bittersweet_path",
        speaker="Maya",
        text="Legendary. Yeah. Even if I'm not fully human by the end of it. Even if this is our swan song. *she smiles through tears* Let's burn down the fucking house.",
        choices=[],
        effects=[
            (DialogueEffect.SET_FLAG, "maya_saved"),
            (DialogueEffect.SET_FLAG, "bittersweet_ending"),
            (DialogueEffect.SET_FLAG, "stayed_for_show")
        ]
    ))

    tree.add_node(DialogueNode(
        id="transcendence_path",
        speaker="Maya",
        text="Evolution. Transformation. Becoming something... more than human. *her eyes glow faintly* Maybe you're right. Maybe death is just a key change. Are you brave enough to change with me?",
        choices=[
            DialogueChoice(
                text="If it means we stay together, yes. Transform me too.",
                next_node="transcendence_accepted",
                effects=[(DialogueEffect.SET_FLAG, "accepted_transformation")]
            ),
            DialogueChoice(
                text="I want to. But I can't. I'm sorry.",
                next_node="transcendence_refused",
            ),
        ]
    ))

    tree.add_node(DialogueNode(
        id="transcendence_accepted",
        speaker="Maya",
        text="*she bites your neck gently* There. Now we're the same. No more human limitations, no more mortality. Just us, and the music, forever. *she takes your hand* Let's show them what eternity sounds like.",
        choices=[],
        effects=[
            (DialogueEffect.SET_FLAG, "maya_transformed"),
            (DialogueEffect.SET_FLAG, "player_transformed"),
            (DialogueEffect.SET_FLAG, "transcendence_ending")
        ]
    ))

    tree.add_node(DialogueNode(
        id="transcendence_refused",
        speaker="Maya",
        text="*steps back* I understand. You want to stay human. Stay safe. I can't blame you. But I... I'm going to let it happen. I'm going to become. *she looks at the city below* Goodbye. Tell them I chose this.",
        choices=[],
        effects=[
            (DialogueEffect.SET_FLAG, "maya_transformed_alone"),
            (DialogueEffect.SET_FLAG, "rejected_transformation"),
            (DialogueEffect.SET_FLAG, "maya_lost")
        ]
    ))

    tree.add_node(DialogueNode(
        id="abandonment_path",
        speaker="Maya",
        text="*her expression hardens* There it is. The truth. You came up here to ease your guilt, not to save me. You want the version of Maya that makes you feel good. Not the real, infected, complicated me.",
        choices=[
            DialogueChoice(
                text="Wait, that's not—I didn't mean—",
                next_node="abandonment_regret",
            ),
            DialogueChoice(
                text="You're right. I can't do this. I'm sorry.",
                next_node="abandonment_final",
                effects=[(DialogueEffect.SET_FLAG, "chose_selfishness")]
            ),
        ]
    ))

    tree.add_node(DialogueNode(
        id="abandonment_regret",
        speaker="Maya",
        text="Too late. I see who you really are now. Go. Go do your show. Be the star. I'll be here, turning into something you can't use for your redemption arc. GET OUT!",
        choices=[],
        effects=[
            (DialogueEffect.SET_FLAG, "maya_abandoned"),
            (DialogueEffect.SET_FLAG, "guilt_path")
        ]
    ))

    tree.add_node(DialogueNode(
        id="abandonment_final",
        speaker="Maya",
        text="*turns away* Yeah. That's what I thought. Go be great without me. Just like always. *her voice breaks* Just... go.",
        choices=[],
        effects=[
            (DialogueEffect.SET_FLAG, "maya_abandoned"),
            (DialogueEffect.SET_FLAG, "chose_selfishness"),
            (DialogueEffect.SET_FLAG, "hollow_victory_ending")
        ]
    ))

    tree.add_node(DialogueNode(
        id="cruel_path",
        speaker="Maya",
        text="*her eyes flash with hurt and rage* ...Get away from me. GET AWAY! You're not here to help. You're here to make yourself feel better. I don't need your pity or your cruelty!",
        choices=[],
        effects=[
            (DialogueEffect.SET_FLAG, "maya_abandoned"),
            (DialogueEffect.SET_FLAG, "cruel_choice"),
            (DialogueEffect.SET_FLAG, "hollow_victory_ending")
        ]
    ))

    tree.add_node(DialogueNode(
        id="maya_rejection_path",
        speaker="Maya",
        text="Mean something? You think showing up erases everything? The years I spent broke and struggling while you got fat on major label money? *she laughs bitterly* You're delusional.",
        choices=[
            DialogueChoice(
                text="I know I can't undo the past. But maybe we can build a future.",
                next_node="maya_moment_truth",
            ),
            DialogueChoice(
                text="Fine. Stay here and rot. I tried.",
                next_node="abandonment_final",
            ),
        ]
    ))

    # Fallback for if something goes wrong
    tree.fallback_node = "start_purist"

    return tree
