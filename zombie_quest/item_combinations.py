"""Item combination system for creating new items from existing ones.

This module allows players to combine items in their inventory to create
new items or unlock hidden information. Supports multiple solution paths
and creative puzzle-solving.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .ui import Item


@dataclass
class CombinationRecipe:
    """A recipe for combining two items."""
    item1: str
    item2: str
    result_item: str
    result_description: str
    success_message: str
    # Flag to set when combination is successful (for tracking alternate paths)
    flag: Optional[str] = None
    # Whether the original items are consumed
    consume_items: bool = True


class ItemCombiner:
    """Handles combining inventory items to create new items or effects."""

    def __init__(self):
        self.recipes: List[CombinationRecipe] = self._build_recipes()
        # Track which combinations have been discovered
        self.discovered_combinations: List[str] = []

    def _build_recipes(self) -> List[CombinationRecipe]:
        """Define all possible item combinations."""
        return [
            # Scratched Tape - plays backwards message when examined
            CombinationRecipe(
                item1="Demo Tape",
                item2="Guitar Pick",
                result_item="Scratched Tape",
                result_description="A demo tape with deliberate scratches. When played backwards, it reveals the phrase 'The zombies fear the B-side'.",
                success_message="You carefully scratch the tape with the pick. The damage creates a hidden backwards message!",
                flag="discovered_backwards_message",
                consume_items=True
            ),

            # Hidden Track Revelation - combining setlist with vinyl reveals secret
            CombinationRecipe(
                item1="Setlist",
                item2="Vinyl Record",
                result_item="Annotated Setlist",
                result_description="The setlist with vinyl track numbers cross-referenced. Track 13 (unlisted) is called 'Zombie Lullaby'.",
                success_message="Cross-referencing the setlist with the vinyl reveals an unlisted track - a zombie lullaby!",
                flag="discovered_zombie_lullaby",
                consume_items=False  # Keep both items
            ),

            # Fake VIP Credentials - combining flyer and pass
            CombinationRecipe(
                item1="Gig Flyer",
                item2="Backstage Pass",
                result_item="VIP All-Access Pass",
                result_description="A carefully doctored pass that combines elements from the flyer and backstage pass. Looks legitimate in dim lighting.",
                success_message="You layer the flyer design over the pass, creating convincing VIP credentials!",
                flag="created_vip_pass",
                consume_items=True
            ),

            # Amplified Pick - Guitar pick + Vinyl for enhanced power
            CombinationRecipe(
                item1="Guitar Pick",
                item2="Vinyl Record",
                result_item="Resonant Pick",
                result_description="A guitar pick that vibrates with the grooves of 'Zombie Minneapolis'. It hums with strange energy.",
                success_message="You trace the pick along the vinyl's grooves. It begins to resonate with undead frequencies!",
                flag="created_resonant_pick",
                consume_items=False  # Keep the pick
            ),

            # Demo + Setlist = Complete Recording
            CombinationRecipe(
                item1="Demo Tape",
                item2="Setlist",
                result_item="Complete Recording",
                result_description="A demo tape with the full setlist recorded. It's a complete performance that could rival the main act.",
                success_message="You follow the setlist to enhance your demo, creating a full performance recording!",
                flag="created_complete_recording",
                consume_items=False
            ),

            # Paper + Marker = Custom Flyer (alternate path item)
            CombinationRecipe(
                item1="Blank Paper",
                item2="Marker",
                result_item="Handmade Flyer",
                result_description="A DIY gig flyer with raw energy. Your own design captures the punk spirit perfectly.",
                success_message="You design your own flyer - it's rough, but authentic. The clerk will respect this.",
                flag="created_handmade_flyer",
                consume_items=True
            ),

            # Screwdriver function - pick can be used as tool
            CombinationRecipe(
                item1="Guitar Pick",
                item2="Vent Cover",
                result_item="Removed Vent Cover",
                result_description="A vent cover you unscrewed with a guitar pick. The shaft beyond beckons.",
                success_message="You use the pick's edge to carefully unscrew the vent cover. Sneaky!",
                flag="opened_ventilation",
                consume_items=False  # Keep the pick
            ),
        ]

    def can_combine(self, item1_name: str, item2_name: str) -> bool:
        """Check if two items can be combined."""
        return self.find_recipe(item1_name, item2_name) is not None

    def find_recipe(self, item1_name: str, item2_name: str) -> Optional[CombinationRecipe]:
        """Find a recipe for two items (order doesn't matter)."""
        for recipe in self.recipes:
            if (recipe.item1 == item1_name and recipe.item2 == item2_name) or \
               (recipe.item1 == item2_name and recipe.item2 == item1_name):
                return recipe
        return None

    def combine(
        self,
        item1_name: str,
        item2_name: str,
        inventory_items: List[Item],
        items_catalog: Dict[str, Item]
    ) -> Tuple[bool, Optional[str], Optional[Item], List[str]]:
        """
        Attempt to combine two items.

        Returns:
            (success, message, new_item, items_to_remove)
        """
        recipe = self.find_recipe(item1_name, item2_name)

        if not recipe:
            return (
                False,
                "These items don't seem to work together.",
                None,
                []
            )

        # Check if both items are in inventory
        has_item1 = any(item.name == item1_name for item in inventory_items)
        has_item2 = any(item.name == item2_name for item in inventory_items)

        if not (has_item1 and has_item2):
            return (
                False,
                "You don't have both items needed for this combination.",
                None,
                []
            )

        # Create the result item
        result_item = items_catalog.get(recipe.result_item)
        if not result_item:
            # Create new item if not in catalog
            from .ui import Item, COLORS
            result_item = Item(
                name=recipe.result_item,
                description=recipe.result_description,
                icon_color=COLORS.NEON_GOLD  # Combined items get gold color
            )

        # Track combination
        combo_key = f"{recipe.item1}+{recipe.item2}"
        if combo_key not in self.discovered_combinations:
            self.discovered_combinations.append(combo_key)

        # Determine which items to remove
        items_to_remove = []
        if recipe.consume_items:
            items_to_remove = [item1_name, item2_name]

        return (
            True,
            recipe.success_message,
            result_item,
            items_to_remove
        )

    def get_hint_for_item(self, item_name: str) -> Optional[str]:
        """Get a hint about what an item can be combined with."""
        hints = []
        for recipe in self.recipes:
            if recipe.item1 == item_name:
                hints.append(f"Try combining with {recipe.item2}")
            elif recipe.item2 == item_name:
                hints.append(f"Try combining with {recipe.item1}")

        if hints:
            return "Combination hint: " + hints[0]
        return None

    def get_all_combinations(self) -> List[str]:
        """Get list of all possible combinations (for debugging/hints)."""
        return [f"{r.item1} + {r.item2} = {r.result_item}" for r in self.recipes]


# Singleton instance
_combiner: Optional[ItemCombiner] = None


def get_item_combiner() -> ItemCombiner:
    """Get the global item combiner instance."""
    global _combiner
    if _combiner is None:
        _combiner = ItemCombiner()
    return _combiner
