"""Enhanced game engine with full keyboard/mouse controls and visual polish.

Features:
- Complete WASD/Arrow key movement
- Mouse point-and-click navigation
- Particle effects and screen transitions
- Audio system with synthesized sounds
- Dialogue system with branching conversations
- Health system with damage and invincibility
- Save/load game functionality
- Pause menu
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import pygame

from .characters import Hero, ZombieSpawner, ZombieMusicState
from .config import DISPLAY, GAMEPLAY, COLORS, GameState
from .data_loader import build_items, build_rooms, load_game_data
from .rooms import Hotspot, Room
from .ui import Inventory, InventoryWindow, MessageBox, Verb, VerbBar, PauseMenu, VERB_KEYS
from .effects import ParticleSystem, ScreenTransition, GlowEffect, ScreenShake, ScanlineOverlay
from .audio import get_audio_manager
from .dialogue import DialogueManager, DialogueEffect, create_clerk_dialogue, create_dj_dialogue, create_maya_dialogue
from .backgrounds import get_room_background
from .diegetic_audio import get_diegetic_audio
from .memory import MemorySystem

ROOM_WIDTH = DISPLAY.ROOM_WIDTH
ROOM_HEIGHT = DISPLAY.ROOM_HEIGHT
UI_BAR_HEIGHT = DISPLAY.UI_BAR_HEIGHT
MESSAGE_HEIGHT = DISPLAY.MESSAGE_HEIGHT
WINDOW_SIZE = (DISPLAY.WINDOW_WIDTH, DISPLAY.WINDOW_HEIGHT)


class GameEngine:
    """Main game engine with full controls and effects."""

    def __init__(self, base_path: str) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Neon Dead Quest: Minneapolis '82")
        self.clock = pygame.time.Clock()

        # Load game data
        data = load_game_data(base_path)
        self.rooms = build_rooms(data.get("rooms", []))
        hero_data = data.get("hero", {})

        # Safely get start room with validation
        if not self.rooms:
            raise RuntimeError("No rooms loaded from game_data.json")

        start_room_id = hero_data.get("start_room")
        if not start_room_id or start_room_id not in self.rooms:
            start_room_id = next(iter(self.rooms.keys()))

        self.current_room: Room = self.rooms[start_room_id]
        hero_start = tuple(hero_data.get("position", (ROOM_WIDTH // 2, int(ROOM_HEIGHT * 0.8))))
        self.hero = Hero(hero_start)

        # Room surface
        self.room_surface = pygame.Surface((ROOM_WIDTH, ROOM_HEIGHT), pygame.SRCALPHA)

        # UI components
        self.verb_bar = VerbBar(WINDOW_SIZE[0], UI_BAR_HEIGHT)
        self.message_box = MessageBox(WINDOW_SIZE[0], MESSAGE_HEIGHT)
        self.message_box.rect.topleft = (0, WINDOW_SIZE[1] - MESSAGE_HEIGHT)
        self.pause_menu = PauseMenu(WINDOW_SIZE[0], WINDOW_SIZE[1])

        # Inventory
        self.inventory = Inventory()
        self.inventory_window = InventoryWindow(
            self.inventory,
            pygame.Rect(40, UI_BAR_HEIGHT + 20, WINDOW_SIZE[0] - 80, 140),
        )

        # Items catalog
        self.items_catalog = build_items(data.get("items", []))
        for item_name in data.get("starting_inventory", []):
            item = self.items_catalog.get(item_name)
            if item:
                self.inventory.add_item(item)

        # Visual effects
        self.particles = ParticleSystem()
        self.transition = ScreenTransition()
        self.glow = GlowEffect()
        self.screen_shake = ScreenShake()
        self.scanlines = ScanlineOverlay(WINDOW_SIZE, intensity=0.08)

        # Audio
        self.audio = get_audio_manager()

        # Diegetic audio system
        self.diegetic_audio = get_diegetic_audio()

        # Dialogue system
        self.dialogue_manager = DialogueManager(WINDOW_SIZE[0], WINDOW_SIZE[1])
        self.dialogue_trees: Dict[str, object] = {
            "clerk": create_clerk_dialogue(),
            "dj": create_dj_dialogue(),
            "maya": create_maya_dialogue(),
        }
        self.game_flags: Dict[str, bool] = {}

        # Memory system for hotspot revisits and protagonist reflections
        self.memory_system = MemorySystem()

        # Protagonist backstory system
        self.protagonist_data = data.get("protagonist", {})
        self.backstory_selected = self.protagonist_data.get("selected_backstory", "purist")
        backstory_info = self.protagonist_data.get("backstories", {}).get(self.backstory_selected, {})

        # Set backstory flags
        for flag in backstory_info.get("flags", []):
            self.game_flags[flag] = True

        # Endings data
        self.endings_data = data.get("endings", {})

        # Game state
        self.state = GameState.PLAYING
        self.pending_interaction: Optional[Tuple[Hotspot, Verb]] = None
        self.running = True

        # Generate detailed backgrounds for rooms
        self._generate_room_backgrounds()

        # Initial message
        initial_message = self.current_room.entry_message or "The Minneapolis night hums with feedback."
        if initial_message:
            self.message_box.show(initial_message)

        # Set initial room ambience
        if self.audio.event_system:
            self.audio.event_system.trigger('room_enter', {'room_id': start_room_id})

        # Set initial diegetic sources
        self.diegetic_audio.set_room(start_room_id)

    def _generate_room_backgrounds(self) -> None:
        """Generate detailed backgrounds for all rooms."""
        for room_id, room in self.rooms.items():
            bg = get_room_background(room_id, room.size)
            if bg:
                room.background = bg

    def run(self) -> None:
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()
            pygame.display.flip()
        pygame.quit()

    def handle_events(self) -> None:
        """Handle all input events."""
        # Update hover states
        mouse_pos = pygame.mouse.get_pos()
        self.verb_bar.update_hover(mouse_pos)
        if self.inventory_window.visible:
            self.inventory_window.update_hover(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue

            # Handle based on current state
            if self.state == GameState.PAUSED:
                self._handle_pause_event(event)
            elif self.dialogue_manager.active:
                self._handle_dialogue_event(event)
            else:
                self._handle_playing_event(event)

    def _handle_pause_event(self, event: pygame.event.Event) -> None:
        """Handle input while paused."""
        if event.type == pygame.KEYDOWN:
            result = self.pause_menu.handle_key(event.key)
            if result:
                self._handle_pause_action(result)
            if not self.pause_menu.visible:
                self.state = GameState.PLAYING

    def _handle_pause_action(self, action: str) -> None:
        """Handle pause menu selection."""
        if action == "resume":
            self.pause_menu.visible = False
            self.state = GameState.PLAYING
            self.audio.play("ui_select")
        elif action == "save_game":
            self.message_box.show("Game saved to the neon void.")
            self.audio.play("success")
        elif action == "load_game":
            self.message_box.show("Restored from the neon void.")
            self.audio.play("success")
        elif action == "quit":
            self.running = False

    def _handle_dialogue_event(self, event: pygame.event.Event) -> None:
        """Handle input during dialogue."""
        effects = self.dialogue_manager.handle_input(
            event,
            self.inventory.get_item_names(),
            self.game_flags
        )
        if effects:
            self._apply_dialogue_effects(effects)

    def _apply_dialogue_effects(self, effects: List[Tuple[DialogueEffect, str]]) -> None:
        """Apply effects from dialogue choices."""
        for effect, value in effects:
            if effect == DialogueEffect.GIVE_ITEM:
                self.give_item_to_inventory(value)
                self.audio.play("pickup")
                self.particles.emit_sparkle(
                    self.hero.position.x,
                    self.hero.position.y - 20,
                    COLORS.NEON_GOLD
                )
            elif effect == DialogueEffect.REMOVE_ITEM:
                self.inventory.remove_item(value)
            elif effect == DialogueEffect.SET_FLAG:
                self.game_flags[value] = True
            elif effect == DialogueEffect.CLEAR_FLAG:
                self.game_flags[value] = False
            elif effect == DialogueEffect.HEAL:
                heal_amount = int(value) if isinstance(value, int) else (int(value) if isinstance(value, str) and value.isdigit() else 1)
                self.hero.heal(heal_amount)
                self.audio.play("success")
            elif effect == DialogueEffect.DAMAGE:
                damage_amount = int(value) if isinstance(value, int) else (int(value) if isinstance(value, str) and value.isdigit() else 1)
                self._damage_hero(damage_amount)

    def _handle_playing_event(self, event: pygame.event.Event) -> None:
        """Handle input while playing."""
        if event.type == pygame.KEYDOWN:
            self._handle_keydown(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_click(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.inventory_window.visible:
                self.inventory_window.handle_event(event)

    def _handle_keydown(self, event: pygame.event.Event) -> None:
        """Handle keyboard input."""
        key = event.key

        # Escape - pause or close windows
        if key == pygame.K_ESCAPE:
            if self.inventory_window.visible:
                self.inventory_window.close()
                self.audio.play("ui_click")
            else:
                self.pause_menu.toggle()
                self.state = GameState.PAUSED if self.pause_menu.visible else GameState.PLAYING
                self.audio.play("ui_click")
            return

        # Pause menu shortcut
        if key == pygame.K_p and not self.inventory_window.visible:
            self.pause_menu.toggle()
            self.state = GameState.PAUSED if self.pause_menu.visible else GameState.PLAYING
            self.audio.play("ui_click")
            return

        # Inventory shortcut
        if key == pygame.K_i:
            self.inventory_window.toggle()
            self.audio.play("ui_click")
            return

        # Inventory navigation
        if self.inventory_window.visible:
            selected = self.inventory_window.handle_key(key)
            if selected:
                self.message_box.show(f"Selected {selected.name}.")
                self.audio.play("ui_select")
            return

        # Verb selection
        action = self.verb_bar.handle_key(key)
        if action == "verb":
            self.audio.play("ui_click")
            return

        # Tab to cycle verbs
        if key == pygame.K_TAB:
            if event.mod & pygame.KMOD_SHIFT:
                self.verb_bar.cycle_prev()
            else:
                self.verb_bar.cycle_next()
            self.audio.play("ui_click")
            return

        # Space/Enter to interact with nearest hotspot
        if key in (pygame.K_SPACE, pygame.K_RETURN):
            if self.message_box.is_typing:
                self.message_box.skip_typing()
            else:
                self._interact_with_nearest_hotspot()
            return

    def _handle_mouse_click(self, event: pygame.event.Event) -> None:
        """Handle mouse click."""
        if event.button == 1:  # Left click
            # Check inventory window first
            if self.inventory_window.visible:
                selected = self.inventory_window.handle_event(event)
                if selected:
                    self.message_box.show(f"Selected {selected.name}.")
                    self.audio.play("ui_select")
                return

            # Check verb bar
            if self.verb_bar.rect.collidepoint(event.pos):
                action = self.verb_bar.handle_click(event.pos)
                if action == "inventory":
                    self.inventory_window.toggle()
                    self.audio.play("ui_click")
                elif action == "options":
                    self.pause_menu.toggle()
                    self.state = GameState.PAUSED if self.pause_menu.visible else GameState.PLAYING
                    self.audio.play("ui_click")
                elif action == "verb":
                    self.audio.play("ui_click")
                return

            # Room click
            self.handle_room_click(event.pos)

        elif event.button == 3:  # Right click - cycle verbs
            verb = self.verb_bar.cycle_next()
            self.message_box.show(f"Selected {verb.value.title()} icon.")
            self.audio.play("ui_click")

    def handle_room_click(self, position: Tuple[int, int]) -> None:
        """Handle click within the room area."""
        room_pos = self.screen_to_room(position)
        if room_pos is None:
            return

        verb = self.verb_bar.selected_verb

        if verb == Verb.WALK:
            self.hero.set_destination(room_pos, self.current_room.pathfinder)
            self.pending_interaction = None
            return

        # Check for hotspot
        hotspot = self.current_room.find_hotspot((int(room_pos[0]), int(room_pos[1])))
        if not hotspot:
            # Walk to clicked position even with other verbs
            self.hero.set_destination(room_pos, self.current_room.pathfinder)
            self.message_box.show("There's nothing of interest there.")
            return

        self.request_hotspot_interaction(hotspot, verb)

    def _interact_with_nearest_hotspot(self) -> None:
        """Interact with the nearest hotspot."""
        if not self.current_room.hotspots:
            return

        hero_pos = self.hero.position
        nearest = None
        nearest_dist = float('inf')

        for hotspot in self.current_room.hotspots:
            center = pygame.Vector2(hotspot.rect.center)
            dist = (center - hero_pos).length()
            if dist < nearest_dist and dist < GAMEPLAY.INTERACTION_RADIUS:
                nearest = hotspot
                nearest_dist = dist

        if nearest:
            verb = self.verb_bar.selected_verb
            self.perform_hotspot_action(nearest, verb)
            self.audio.play("ui_select")

    def request_hotspot_interaction(self, hotspot: Hotspot, verb: Verb) -> None:
        """Request interaction with a hotspot."""
        target = hotspot.walk_position or (hotspot.rect.centerx, hotspot.rect.bottom)
        self.hero.set_destination(target, self.current_room.pathfinder)
        self.pending_interaction = (hotspot, verb)

    def screen_to_room(self, position: Tuple[int, int]) -> Optional[Tuple[float, float]]:
        """Convert screen coordinates to room coordinates."""
        x, y = position
        if y < UI_BAR_HEIGHT or y >= UI_BAR_HEIGHT + ROOM_HEIGHT:
            return None
        room_y = y - UI_BAR_HEIGHT
        return float(x), float(room_y)

    def update(self, dt: float) -> None:
        """Update game state."""
        # Update audio (music layers, etc.)
        self.audio.update_music(dt)

        # Update diegetic audio sources
        self.diegetic_audio.update(dt)

        # Update effects
        self.glow.update(dt)
        self.particles.update(dt)
        self.transition.update(dt)
        shake_offset = self.screen_shake.update(dt)

        # Skip gameplay updates if paused or in dialogue
        if self.state == GameState.PAUSED:
            return

        if self.dialogue_manager.active:
            self.dialogue_manager.update(dt, self.inventory.get_item_names(), self.game_flags)
            return

        # Update hero with keyboard input
        keys = pygame.key.get_pressed()
        self.hero.handle_keyboard_input(keys)

        # Update hero position
        room_rect = pygame.Rect(0, 0, ROOM_WIDTH, ROOM_HEIGHT)
        self.hero.update(
            dt,
            room_bounds=room_rect,
            walkable_check=self.current_room.is_walkable
        )

        # Update room and zombies
        self._update_room(dt)

        # Update music tension based on zombie proximity
        self._update_music_tension()

        # Check for pending interactions
        if self.pending_interaction and self.hero.has_arrived():
            hotspot, verb = self.pending_interaction
            self.pending_interaction = None
            self.perform_hotspot_action(hotspot, verb)

        # Update UI
        self.message_box.update(dt)

        # Ambient particles
        if not self.transition.active:
            self.particles.emit_ambient_dust(pygame.Rect(0, 0, ROOM_WIDTH, ROOM_HEIGHT))

    def _update_room(self, dt: float) -> None:
        """Update room entities including zombies."""
        hero_pos = self.hero.foot_position

        # Apply music effects to zombies based on diegetic sources
        self._apply_music_to_zombies()

        for zombie in self.current_room.zombies:
            room_rect = pygame.Rect(0, 0, ROOM_WIDTH, ROOM_HEIGHT)
            collision = zombie.update(dt, hero_pos, room_rect)

            if collision:
                self._damage_hero(1)

            # Zombie groans with spatial audio
            # Modify groan based on music state
            if zombie.should_groan():
                zombie_pos = zombie.foot_position
                volume = 0.5

                # Adjust groan volume/pitch based on music state
                if zombie.music_state == ZombieMusicState.DANCING:
                    volume = 0.3  # Quieter, happier groans
                elif zombie.music_state == ZombieMusicState.REMEMBERING:
                    volume = 0.2  # Very quiet, contemplative

                # Use spatial audio for zombie groans
                self.audio.play_spatial(
                    f'zombie_groan_{zombie.zombie_type}',
                    source_pos=zombie_pos,
                    listener_pos=hero_pos,
                    volume=volume,
                    fallback_sound='zombie_groan'
                )

    def _apply_music_to_zombies(self) -> None:
        """Apply diegetic music effects to all zombies in the room."""
        for zombie in self.current_room.zombies:
            zombie_pos = zombie.foot_position

            # Get all music affecting this zombie
            music_effects = self.diegetic_audio.get_music_at_position(zombie_pos)

            # Apply each music effect
            for music_type, intensity in music_effects:
                zombie.apply_music_effect(music_type, intensity)

    def _update_music_tension(self) -> None:
        """Update music tension based on zombie proximity and threat level."""
        from .audio import TensionLevel
        import math

        room_id = self.current_room.id

        if not self.current_room.zombies:
            # No zombies - safe
            self.audio.set_music_tension(TensionLevel.SAFE, room_id)
            return

        hero_pos = self.hero.foot_position
        min_distance = float('inf')
        chasing_count = 0
        harmless_count = 0

        for zombie in self.current_room.zombies:
            zombie_pos = zombie.foot_position
            distance = math.sqrt(
                (zombie_pos[0] - hero_pos[0])**2 +
                (zombie_pos[1] - hero_pos[1])**2
            )
            min_distance = min(min_distance, distance)

            if zombie.is_chasing and not zombie.is_harmless():
                chasing_count += 1
            elif zombie.is_harmless():
                harmless_count += 1

        # Set tension based on proximity and chase state
        # If all zombies are harmless due to music, reduce tension
        if harmless_count == len(self.current_room.zombies):
            # All zombies pacified by music!
            self.audio.set_music_tension(TensionLevel.SAFE, room_id)
        elif chasing_count > 0 and min_distance < 50:
            # Active chase, very close
            self.audio.set_music_tension(TensionLevel.CHASE, room_id)
        elif chasing_count > 0 or min_distance < 100:
            # Being chased or zombie nearby
            self.audio.set_music_tension(TensionLevel.DANGER, room_id)
        elif min_distance < 150:
            # Zombie in detection range
            self.audio.set_music_tension(TensionLevel.EXPLORATION, room_id)
        else:
            # Far from all zombies
            self.audio.set_music_tension(TensionLevel.SAFE, room_id)

    def _damage_hero(self, amount: int) -> None:
        """Apply damage to hero."""
        if self.hero.take_damage(amount):
            # Hero died
            self.state = GameState.GAME_OVER
            self.message_box.show("The neon fades to black...")
            self.audio.play("death")
        else:
            # Took damage but survived
            self.audio.play("hit")
            self.screen_shake.shake(8.0, 0.3)
            self.particles.emit_damage(self.hero.position.x, self.hero.position.y - 20)

            # Play low health warning if critically hurt
            if self.hero.health == 1:
                self.audio.play("health_low", volume=0.4)

    def perform_hotspot_action(self, hotspot: Hotspot, verb: Verb) -> None:
        """Execute an action on a hotspot."""
        selected_item = self.inventory.selected_item
        interaction_outcome = "default"

        # Check for item combination attempts (when using an item without a required item hotspot)
        if verb == Verb.USE and selected_item and not hotspot.required_item:
            # Try to combine with another item from inventory
            if self._try_item_combination(selected_item.name, hotspot):
                return  # Combination handled

        # Check for musical item usage (special handling)
        if verb == Verb.USE and selected_item:
            musical_items = ['Guitar Pick', 'Demo Tape', 'Setlist', 'Vinyl Record']
            if selected_item.name in musical_items:
                self._use_musical_item(selected_item.name, hotspot)
                return

        # Check for NPC dialogue
        if verb == Verb.TALK and hotspot.talk_target:
            tree = self.dialogue_trees.get(hotspot.talk_target)
            if tree:
                self.dialogue_manager.start_dialogue(
                    tree,
                    self.inventory.get_item_names(),
                    self.game_flags
                )
                return

        if verb == Verb.LOOK:
            # Record the examination and get progressive text
            exam_count = self.memory_system.record_examination(
                self.current_room.id,
                hotspot.name
            )
            base_message = hotspot.message_for("look", interaction_outcome)
            message = self.memory_system.get_progressive_text(
                self.current_room.id,
                hotspot.name,
                base_message,
                "look"
            )

            # On 3rd+ examination, sometimes add a memory trigger
            if exam_count >= 3:
                import random
                if random.random() < 0.3:  # 30% chance
                    backstory_flags = [f for f in self.game_flags.keys() if f.startswith("backstory_")]
                    memory = self.memory_system.trigger_random_memory(
                        self.current_room.id,
                        backstory_flags
                    )
                    if memory:
                        message = f"{message}\n\n{memory}"

            self.audio.play("message")
        elif verb == Verb.TALK:
            message = hotspot.message_for("talk", interaction_outcome)
            self.audio.play("message")
        elif verb == Verb.USE:
            if hotspot.required_item:
                # Check if player has required item OR any alternate item
                has_required = selected_item and selected_item.name == hotspot.required_item
                has_alternate = selected_item and hotspot.alternate_items and selected_item.name in hotspot.alternate_items

                if has_required or has_alternate:
                    interaction_outcome = "success"
                    message = hotspot.message_for("use", interaction_outcome)
                    self.audio.play("success")

                    # Set flag if configured
                    if hotspot.set_flag:
                        self.game_flags[hotspot.set_flag] = True

                    if hotspot.remove_item and verb.value in hotspot.remove_item_triggers:
                        self.inventory.remove_item(hotspot.remove_item)
                    if hotspot.give_item and verb.value in hotspot.give_item_triggers:
                        self.give_item_to_inventory(hotspot.give_item)
                        hotspot.give_item = None

                    # Handle alternate rewards
                    if hotspot.alternate_reward:
                        self.give_item_to_inventory(hotspot.alternate_reward)

                    # Track solution path
                    if has_alternate and selected_item:
                        self.game_flags[f"used_{selected_item.name.lower().replace(' ', '_')}_solution"] = True

                    if selected_item:
                        self.inventory.select_item(None)
                else:
                    interaction_outcome = "missing"
                    message = hotspot.message_for("use", interaction_outcome)
                    self.audio.play("error")
            else:
                interaction_outcome = "success"
                message = hotspot.message_for("use", interaction_outcome)

                # Set flag if configured
                if hotspot.set_flag:
                    self.game_flags[hotspot.set_flag] = True

                if hotspot.give_item and verb.value in hotspot.give_item_triggers:
                    self.give_item_to_inventory(hotspot.give_item)
                    hotspot.give_item = None
                    self.audio.play("pickup")
        else:
            message = hotspot.message_for(verb.value, interaction_outcome)

        # Handle item rewards
        if hotspot.give_item and verb.value in hotspot.give_item_triggers and interaction_outcome != "missing":
            self.give_item_to_inventory(hotspot.give_item)
            hotspot.give_item = None

        if hotspot.remove_item and verb.value in hotspot.remove_item_triggers and interaction_outcome == "success":
            self.inventory.remove_item(hotspot.remove_item)

        # Handle room transitions
        should_transition = False
        if hotspot.target_room and hotspot.transition_verb == verb.value:
            if hotspot.requires_success_for_transition:
                should_transition = interaction_outcome == "success"
            else:
                should_transition = interaction_outcome != "missing"

        if should_transition:
            # Start transition effect
            combined_message_parts: List[str] = []
            if message:
                combined_message_parts.append(message)
            transition_text = hotspot.transition_message
            if transition_text:
                combined_message_parts.append(transition_text)

            def do_transition():
                self.change_room(
                    hotspot.target_room,
                    hotspot.target_position,
                    message=None,
                    announce=False,
                )

            self.audio.play("door")
            self.transition.start_transition(halfway_callback=do_transition)

            if not combined_message_parts:
                combined_message = self.current_room.entry_message or f"You arrive at {self.current_room.name}."
            else:
                combined_message = " ".join(combined_message_parts)

            if combined_message:
                self.message_box.show(combined_message)
            return

        if not message:
            message = "Nothing happens."
        self.message_box.show(message)

    def _use_musical_item(self, item_name: str, hotspot: Hotspot) -> None:
        """Use a musical item to affect nearby zombies.

        Args:
            item_name: Name of the musical item
            hotspot: Hotspot where item is being used (for positioning)
        """
        # Create diegetic audio source
        hero_pos = self.hero.foot_position
        source = self.diegetic_audio.create_item_source(item_name, hero_pos)

        if source:
            self.diegetic_audio.add_temporary_source(source)

            # Count affected zombies
            affected_count = 0
            affected_types = set()

            for zombie in self.current_room.zombies:
                zombie_pos = zombie.foot_position
                intensity = source.get_intensity_at(zombie_pos)

                if intensity > 0.05:
                    # This zombie is affected
                    zombie.apply_music_effect(source.music_type, intensity)
                    affected_count += 1
                    affected_types.add(zombie.zombie_type)

                    # Visual feedback - sparkles around affected zombies
                    self.particles.emit_sparkle(
                        zombie.position.x,
                        zombie.position.y - 30,
                        COLORS.NEON_CYAN
                    )

            # Item-specific messages
            messages = {
                'Guitar Pick': [
                    "You strum a powerful chord on the pick.",
                    "The guitar riff echoes through the space.",
                    "Your guitar work fills the air with raw energy."
                ],
                'Demo Tape': [
                    "The demo tape crackles to life with basement energy.",
                    "Your band's sound floods the room from the cassette.",
                    "The tape hiss gives way to your new wave masterpiece."
                ],
                'Setlist': [
                    "You hum the setlist melodies, note by note.",
                    "The familiar tunes flow from your memory.",
                    "You perform the setlist a cappella."
                ],
                'Vinyl Record': [
                    "The vinyl spins, unleashing The Neon Dead's fury.",
                    "Rare pressing fills the air with punk energy.",
                    "The record crackles with zombie Minneapolis."
                ]
            }

            import random
            base_message = random.choice(messages.get(item_name, ["You use the musical item."]))

            # Add feedback about affected zombies
            if affected_count > 0:
                type_names = [t.title() for t in affected_types]
                zombie_desc = " and ".join(type_names) if len(type_names) > 1 else type_names[0]
                effect_message = f" {affected_count} {zombie_desc} zombie{'s' if affected_count > 1 else ''} react to the music!"
                full_message = base_message + effect_message
            else:
                full_message = base_message + " But no zombies are close enough to hear."

            self.message_box.show(full_message)
            self.audio.play("success", volume=0.8)

            # Visual effects
            self.particles.emit_sparkle(
                self.hero.position.x,
                self.hero.position.y - 20,
                COLORS.NEON_GOLD
            )
            self.glow.pulse(COLORS.NEON_CYAN, 0.3)
        else:
            self.message_box.show(f"You can't use the {item_name} here.")
            self.audio.play("error")

    def give_item_to_inventory(self, item_name: str) -> None:
        """Add an item to the player's inventory."""
        item = self.items_catalog.get(item_name)
        if item and not self.inventory.has_item(item.name):
            self.inventory.add_item(item)
            self.message_box.show(f"You stash the {item.name} in your flight case.")
            self.audio.play("pickup")
            self.particles.emit_sparkle(
                self.hero.position.x,
                self.hero.position.y - 20,
                item.icon_color
            )

    def change_room(
        self,
        room_id: str,
        position: Optional[Tuple[int, int]] = None,
        message: Optional[str] = None,
        announce: bool = True,
    ) -> None:
        """Change to a different room."""
        room = self.rooms.get(room_id)
        if not room:
            return

        self.current_room = room
        destination = position or room.default_entry
        self.hero.position.update(destination)
        self.hero.path = []
        self.hero.current_target = None
        self.hero.using_keyboard = False
        self.pending_interaction = None

        # Trigger room ambience change
        if self.audio.event_system:
            self.audio.event_system.trigger('room_enter', {'room_id': room_id})

        # Update diegetic audio sources for new room
        self.diegetic_audio.set_room(room_id)

        if announce:
            entry_message = message or room.entry_message or f"You arrive at {room.name}."
            if entry_message:
                self.message_box.show(entry_message)

    def draw(self) -> None:
        """Render the game."""
        # Get shake offset
        shake_x, shake_y = self.screen_shake.update(0)

        # Clear screen
        self.screen.fill((0, 0, 0))

        # Draw room
        self.current_room.draw(self.room_surface, self.hero)

        # Draw particles on room surface
        self.particles.draw(self.room_surface)

        # Blit room to screen with shake offset
        self.screen.blit(self.room_surface, (shake_x, UI_BAR_HEIGHT + shake_y))

        # Draw UI
        self.verb_bar.draw(self.screen, self.hero.health)
        self.message_box.draw(self.screen)

        # Draw inventory window
        if self.inventory_window.visible:
            self.inventory_window.draw(self.screen)

        # Draw dialogue
        if self.dialogue_manager.active:
            self.dialogue_manager.draw(
                self.screen,
                self.inventory.get_item_names(),
                self.game_flags
            )

        # Draw pause menu
        if self.state == GameState.PAUSED:
            self.pause_menu.draw(self.screen)

        # Draw transition effect last
        self.transition.draw(self.screen)

        # Scanline overlay for retro feel
        self.scanlines.draw(self.screen)

    def _try_item_combination(self, item_name: str, hotspot: Hotspot) -> bool:
        """
        Try to combine the selected item with items in inventory.
        Returns True if combination was attempted (whether successful or not).
        """
        from .item_combinations import get_item_combiner

        combiner = get_item_combiner()

        # Check if this item can combine with any other inventory items
        for inventory_item in self.inventory.items:
            if inventory_item.name == item_name:
                continue  # Skip the selected item itself

            if combiner.can_combine(item_name, inventory_item.name):
                # Found a combination!
                success, message, new_item, items_to_remove = combiner.combine(
                    item_name,
                    inventory_item.name,
                    self.inventory.items,
                    self.items_catalog
                )

                if success and new_item:
                    # Remove consumed items
                    for item_to_remove in items_to_remove:
                        self.inventory.remove_item(item_to_remove)

                    # Add new item
                    self.inventory.add_item(new_item)
                    self.items_catalog[new_item.name] = new_item

                    # Show success message
                    self.message_box.show(message or f"You combined items to create {new_item.name}!")
                    self.audio.play("success")

                    # Particle effect
                    self.particles.emit_sparkle(
                        self.hero.position.x,
                        self.hero.position.y - 20,
                        new_item.icon_color
                    )

                    # Set any flags from the recipe
                    recipe = combiner.find_recipe(item_name, inventory_item.name)
                    if recipe and recipe.flag:
                        self.game_flags[recipe.flag] = True

                    # Deselect item
                    self.inventory.select_item(None)

                    return True

        return False

    def check_ending_conditions(self) -> Optional[str]:
        """Check if any ending conditions are met and return the ending ID."""
        for ending_id, ending_data in self.endings_data.items():
            required_flags = ending_data.get("required_flags", [])
            forbidden_flags = ending_data.get("forbidden_flags", [])

            # Check all required flags are present
            all_required = all(self.game_flags.get(flag, False) for flag in required_flags)

            # Check no forbidden flags are present
            no_forbidden = all(not self.game_flags.get(flag, False) for flag in forbidden_flags)

            if all_required and no_forbidden:
                return ending_id

        return None

    def trigger_ending(self, ending_id: Optional[str] = None) -> None:
        """Trigger a game ending."""
        if ending_id is None:
            ending_id = self.check_ending_conditions()

        if ending_id is None:
            # Default ending if no conditions met
            ending_id = "human"

        ending_data = self.endings_data.get(ending_id)
        if not ending_data:
            return

        # Set game state to show ending
        self.state = GameState.GAME_OVER

        # Display ending text
        ending_name = ending_data.get("name", "The End")
        ending_text = ending_data.get("text", "The story ends here.")
        ending_theme = ending_data.get("thematic_message", "")

        # Create a comprehensive ending message
        full_ending = f"=== {ending_name.upper()} ===\n\n{ending_text}"
        if ending_theme:
            full_ending += f"\n\n--- {ending_theme} ---"

        self.message_box.show(full_ending)

        # Play appropriate ending sound
        emotional_tone = ending_data.get("emotional_tone", "")
        if "triumphant" in emotional_tone or "cathartic" in emotional_tone:
            self.audio.play("success", volume=0.8)
        elif "hollow" in emotional_tone or "bittersweet" in emotional_tone:
            self.audio.play("message", volume=0.6)
        elif "transcendent" in emotional_tone or "strange" in emotional_tone:
            self.audio.play("pickup", volume=0.7)
        else:
            self.audio.play("message", volume=0.5)

        # Visual effect for ending
        self.glow.pulse(COLORS.HOT_MAGENTA, 2.0)
