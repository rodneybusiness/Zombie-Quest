"""Tests for dialogue system."""
import pytest

from zombie_quest.dialogue import (
    DialogueChoice,
    DialogueNode,
    DialogueTree,
    DialogueEffect,
    create_clerk_dialogue,
    create_dj_dialogue,
)


class TestDialogueChoice:
    """Test dialogue choice functionality."""

    def test_choice_creation(self):
        choice = DialogueChoice(text="Hello", next_node="greeting")
        assert choice.text == "Hello"
        assert choice.next_node == "greeting"

    def test_choice_availability_no_requirements(self):
        choice = DialogueChoice(text="Test", requirements=[])
        assert choice.is_available([], {}) is True

    def test_choice_with_item_requirement(self):
        choice = DialogueChoice(text="Use key", requirements=["Key"])
        assert choice.is_available(["Key"], {}) is True
        assert choice.is_available([], {}) is False

    def test_choice_with_flag_requirement(self):
        choice = DialogueChoice(text="Continue", requirements=["talked_to_npc"])
        assert choice.is_available([], {"talked_to_npc": True}) is True
        assert choice.is_available([], {}) is False

    def test_choice_with_negative_requirement(self):
        choice = DialogueChoice(text="First meeting", requirements=["!met_before"])
        assert choice.is_available([], {"met_before": False}) is True
        assert choice.is_available([], {"met_before": True}) is False


class TestDialogueNode:
    """Test dialogue node functionality."""

    def test_node_creation(self):
        node = DialogueNode(
            id="start",
            speaker="NPC",
            text="Hello there!",
        )
        assert node.id == "start"
        assert node.speaker == "NPC"
        assert node.text == "Hello there!"

    def test_node_with_choices(self):
        choices = [
            DialogueChoice(text="Hi!", next_node="greeting"),
            DialogueChoice(text="Bye", next_node=None),
        ]
        node = DialogueNode(
            id="start",
            speaker="NPC",
            text="What do you want?",
            choices=choices,
        )
        assert len(node.choices) == 2


class TestDialogueTree:
    """Test dialogue tree functionality."""

    def test_tree_creation(self):
        tree = DialogueTree("Test NPC")
        assert tree.character_name == "Test NPC"
        assert len(tree.nodes) == 0

    def test_add_node(self):
        tree = DialogueTree("Test NPC")
        node = DialogueNode(id="start", speaker="NPC", text="Hello!")
        tree.add_node(node)
        assert "start" in tree.nodes
        assert tree.start_node == "start"

    def test_get_starting_node_default(self):
        tree = DialogueTree("Test NPC")
        tree.add_node(DialogueNode(id="start", speaker="NPC", text="Hello!"))
        tree.add_node(DialogueNode(id="other", speaker="NPC", text="Other"))

        node = tree.get_starting_node([], {})
        assert node.id == "start"

    def test_get_starting_node_with_conditions(self):
        tree = DialogueTree("Test NPC")
        tree.add_node(DialogueNode(id="start", speaker="NPC", text="Hello!"))
        tree.add_node(DialogueNode(
            id="has_item",
            speaker="NPC",
            text="You have the item!",
            conditions=["special_item"]
        ))

        # Without item, returns start
        node = tree.get_starting_node([], {})
        assert node.id == "start"

        # With item, returns conditional node
        node = tree.get_starting_node(["special_item"], {})
        assert node.id == "has_item"


class TestPrebuiltDialogues:
    """Test the pre-built dialogue trees."""

    def test_clerk_dialogue_exists(self):
        tree = create_clerk_dialogue()
        assert tree is not None
        assert tree.character_name == "Record Store Clerk"
        assert len(tree.nodes) > 0

    def test_dj_dialogue_exists(self):
        tree = create_dj_dialogue()
        assert tree is not None
        assert tree.character_name == "DJ Rotten"
        assert len(tree.nodes) > 0

    def test_clerk_dialogue_has_start(self):
        tree = create_clerk_dialogue()
        node = tree.get_starting_node([], {})
        assert node is not None

    def test_dj_dialogue_has_start(self):
        tree = create_dj_dialogue()
        node = tree.get_starting_node([], {})
        assert node is not None


class TestDialogueEffect:
    """Test dialogue effect enumeration."""

    def test_effect_types_exist(self):
        assert DialogueEffect.GIVE_ITEM.value == "give_item"
        assert DialogueEffect.REMOVE_ITEM.value == "remove_item"
        assert DialogueEffect.SET_FLAG.value == "set_flag"
        assert DialogueEffect.HEAL.value == "heal"
