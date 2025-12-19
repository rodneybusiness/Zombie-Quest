"""Memory and revisit system for tracking player interactions with hotspots.

This system creates a sense of deepening narrative as players re-examine locations,
unlocking memories and protagonist reflections tied to their backstory.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class HotspotMemory:
    """Tracks interactions with a specific hotspot."""
    hotspot_id: str
    room_id: str
    examination_count: int = 0
    first_visit_time: float = 0.0
    last_visit_time: float = 0.0
    flags_unlocked: List[str] = field(default_factory=list)

    def record_examination(self, game_time: float) -> int:
        """Record an examination and return the new count."""
        if self.examination_count == 0:
            self.first_visit_time = game_time
        self.last_visit_time = game_time
        self.examination_count += 1
        return self.examination_count


class MemorySystem:
    """Manages protagonist memories and hotspot revisit text."""

    def __init__(self) -> None:
        # Track all hotspot interactions: (room_id, hotspot_name) -> HotspotMemory
        self.hotspot_memories: Dict[Tuple[str, str], HotspotMemory] = {}

        # Protagonist backstory memories
        self.backstory_memories: Dict[str, List[str]] = {
            "backstory_sellout": [
                "The neon reminds you of the first time you signed away your soul for a spotlight.",
                "You remember Maya's face when you told her you were 'going solo.' The betrayal in her eyes.",
                "Every surface here feels like a mirror reflecting your compromises.",
            ],
            "backstory_purist": [
                "This place holds the ghost of every pure moment, every uncompromised chord.",
                "You remember when the scene was family, before the infection, before the loss.",
                "The weight of authenticity presses down. You've never wavered. But at what cost?",
            ],
            "backstory_survivor": [
                "Too many ghosts haunt these corners. Friends lost to overdoses, venues closed forever.",
                "You remember the funerals. So many funerals. And yet, you're still standing.",
                "Survival isn't victory. It's just... continuing. Is that enough?",
            ],
        }

        # Location-specific memory text (room_id -> memory fragments)
        self.location_memories: Dict[str, List[str]] = {
            "hennepin_outside": [
                "You played your first real gig here, back when the neon felt like promise instead of warning.",
                "Maya used to meet you under this marquee. Before everything got complicated.",
                "The street hasn't changed. But you have. The question is: for better or worse?",
            ],
            "record_store": [
                "You used to spend entire paychecks here, hunting for the perfect vinyl obscurity.",
                "Maya bought you your first import here. A gesture that felt like love, before you knew what that meant.",
                "The smell of vinyl and cardboard triggers something primal: hunger for the next great discovery.",
            ],
            "college_station": [
                "Your demo first played here, crackling through these exact speakers. The DJ said 'You're going places.'",
                "Maya's voice echoed in this booth once, interviewing about the scene. She was so passionate. So alive.",
                "College radio was supposed to change everything. Instead, it was just the beginning.",
            ],
            "backstage_stage": [
                "Behind every stage, there's a moment of terror before the lights. You've lived that moment a hundred times.",
                "Maya's pre-show ritual: three deep breaths, one shot of whiskey, a muttered prayer to the gods of rock.",
                "The backstage is where masks come off. Where you see who people really are.",
            ],
            "green_room": [
                "Green rooms are liminal spaces—between the person you are and the person you become on stage.",
                "You remember the last real conversation with Maya, right here. Before the infection. Before the end.",
                "Every band that passed through left ghosts. You can feel them watching, judging.",
            ],
            "rooftop_confrontation": [
                "Heights make you honest. Up here, there's nowhere to hide from the truth.",
                "The city below is beautiful and terrible. Like the scene. Like everything you've ever loved.",
                "This is where it ends. Or where it begins. The rooftop knows which, even if you don't.",
            ],
            "final_stage": [
                "Every musician dreams of this moment. The question is: what are you willing to sacrifice for it?",
                "The stage doesn't care about your past. Only what you give it right now.",
                "This is the altar. Your music is the offering. What do you pray for?",
            ],
        }

        # Hotspot-specific progressive text
        self.hotspot_progressive_text: Dict[str, Dict[int, str]] = {}
        self._initialize_hotspot_text()

    def _initialize_hotspot_text(self) -> None:
        """Initialize progressive examination text for specific hotspots."""
        # Poster Kiosk progression
        self.hotspot_progressive_text[("hennepin_outside", "Poster Kiosk")] = {
            1: "Flyers for Husker Du and The Suburbs flutter in the warm night.",
            2: "Beneath the fresh flyers, you spot older ones—bands that never made it. Forgotten dreams on cheap paper.",
            3: "Your own band's flyer used to hang here. Maya designed it. You wonder if any fragments remain, buried deep.",
        }

        # Marquee progression
        self.hotspot_progressive_text[("hennepin_outside", "Marquee")] = {
            1: "Tonight: The Neon Dead with special guest Soul Asylum (undead mix).",
            2: "The marquee letters cast shadows that look like prison bars. Or musical staff lines. Depends on your perspective.",
            3: "You remember when seeing your name up there meant everything. Now you're not sure what it means at all.",
        }

        # Record Clerk progression
        self.hotspot_progressive_text[("record_store", "Record Clerk")] = {
            1: "A clerk polishes seven-inches with ritual precision.",
            2: "The clerk's movements are practiced, meditative. They've been doing this for years. Like you with your music.",
            3: "You recognize the clerk now—they were at your first show. They remember you too. The recognition is complicated.",
        }

        # Listening Booth progression
        self.hotspot_progressive_text[("record_store", "Listening Booth")] = {
            1: "A coffin-shaped listening booth thrums with low frequencies.",
            2: "Maya used to drag you in here, forcing you to listen to obscure imports. 'Expand your vocabulary,' she'd say.",
            3: "The booth is empty now, but you swear you can hear echoes of all the music it's contained. A sonic archive.",
        }

        # DJ Rotten progression
        self.hotspot_progressive_text[("college_station", "DJ Rotten")] = {
            1: "Stacks of cassettes teeter beside a flickering console.",
            2: "Rotten has probably broken more bands than any major label. And championed more too.",
            3: "There's a loyalty in the underground. Rotten embodies it—supporting the scene even as it dies.",
        }

        # Poster Wall progression
        self.hotspot_progressive_text[("college_station", "Poster Wall")] = {
            1: "Gig posters layer the wall: Husker Du, The Replacements, Prince.",
            2: "Each poster is a time capsule. A moment when anything felt possible.",
            3: "You find a corner where Maya's handwriting peeks through: 'Music saves.' You hope she still believes it.",
        }

        # Vintage Couch progression
        self.hotspot_progressive_text[("green_room", "Vintage Couch")] = {
            1: "A worn leather couch that's seen countless pre-show jitters.",
            2: "The couch remembers every nervous breakdown, every ecstatic celebration, every quiet goodbye.",
            3: "You and Maya used to sit here, running through the setlist one last time. The ritual felt sacred.",
        }

        # Maya hotspot progression
        self.hotspot_progressive_text[("rooftop_confrontation", "Maya")] = {
            1: "Maya's silhouette trembles against the skyline. Half-human, half-something else.",
            2: "She's trying so hard to hold onto herself. You can see the fight in every tremor.",
            3: "This is the person you'd die for. The person you might have already killed. The weight is unbearable.",
        }

        # Skyline View progression
        self.hotspot_progressive_text[("rooftop_confrontation", "Skyline View")] = {
            1: "Minneapolis spreads below: clubs, record stores, all the places where dreams lived and died.",
            2: "The city is a circuit board of neon and shadow. Every light a story. Every dark space a loss.",
            3: "From up here, the infection looks almost beautiful. The chaos has an aesthetic. That's the horror.",
        }

    def record_examination(
        self,
        room_id: str,
        hotspot_name: str,
        game_time: float = 0.0
    ) -> int:
        """Record a hotspot examination and return the examination count."""
        key = (room_id, hotspot_name)

        if key not in self.hotspot_memories:
            self.hotspot_memories[key] = HotspotMemory(
                hotspot_id=hotspot_name,
                room_id=room_id
            )

        return self.hotspot_memories[key].record_examination(game_time)

    def get_examination_count(self, room_id: str, hotspot_name: str) -> int:
        """Get the number of times a hotspot has been examined."""
        key = (room_id, hotspot_name)
        if key not in self.hotspot_memories:
            return 0
        return self.hotspot_memories[key].examination_count

    def get_progressive_text(
        self,
        room_id: str,
        hotspot_name: str,
        default_text: str,
        verb: str = "look"
    ) -> str:
        """Get progressive text for a hotspot based on examination count.

        Returns specialized text for 2nd and 3rd examinations if available,
        otherwise returns the default text.
        """
        # Only apply progressive text for "look" verb
        if verb != "look":
            return default_text

        key = (room_id, hotspot_name)
        count = self.get_examination_count(room_id, hotspot_name)

        # Get progressive text if available
        if key in self.hotspot_progressive_text:
            progressive = self.hotspot_progressive_text[key]
            # Use count or max available
            actual_count = min(count + 1, max(progressive.keys()))
            return progressive.get(actual_count, default_text)

        return default_text

    def get_backstory_memory(self, backstory_flag: str, index: int = 0) -> Optional[str]:
        """Get a specific memory fragment for a backstory."""
        memories = self.backstory_memories.get(backstory_flag, [])
        if 0 <= index < len(memories):
            return memories[index]
        return None

    def get_location_memory(self, room_id: str, index: int = 0) -> Optional[str]:
        """Get a specific memory fragment for a location."""
        memories = self.location_memories.get(room_id, [])
        if 0 <= index < len(memories):
            return memories[index]
        return None

    def trigger_random_memory(
        self,
        room_id: str,
        backstory_flags: List[str]
    ) -> Optional[str]:
        """Trigger a random memory based on location and backstory.

        Used for ambient memory triggers when entering rooms or examining
        hotspots multiple times.
        """
        import random

        # 50% chance of location memory, 50% backstory memory
        if random.random() < 0.5:
            # Location memory
            memories = self.location_memories.get(room_id, [])
            if memories:
                return random.choice(memories)
        else:
            # Backstory memory
            for flag in backstory_flags:
                if flag in self.backstory_memories:
                    memories = self.backstory_memories[flag]
                    if memories:
                        return random.choice(memories)

        return None

    def unlock_memory_flag(
        self,
        room_id: str,
        hotspot_name: str,
        flag: str
    ) -> None:
        """Mark a memory flag as unlocked for a hotspot."""
        key = (room_id, hotspot_name)
        if key in self.hotspot_memories:
            if flag not in self.hotspot_memories[key].flags_unlocked:
                self.hotspot_memories[key].flags_unlocked.append(flag)

    def has_memory_flag(
        self,
        room_id: str,
        hotspot_name: str,
        flag: str
    ) -> bool:
        """Check if a memory flag has been unlocked."""
        key = (room_id, hotspot_name)
        if key not in self.hotspot_memories:
            return False
        return flag in self.hotspot_memories[key].flags_unlocked
