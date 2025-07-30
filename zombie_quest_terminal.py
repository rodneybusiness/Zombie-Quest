#!/usr/bin/env python3
"""
1950's Zombie Quest - Terminal Edition
A text-based adventure game playable in the terminal
"""

import random
import time
import json
import os

class Item:
    def __init__(self, name, description, use_action=None):
        self.name = name
        self.description = description
        self.use_action = use_action

class Inventory:
    def __init__(self):
        self.items = []
        self.max_items = 8
        
    def add_item(self, item):
        if len(self.items) < self.max_items:
            self.items.append(item)
            return True
        return False
        
    def remove_item(self, item_name):
        for i, item in enumerate(self.items):
            if item.name == item_name:
                return self.items.pop(i)
        return None
        
    def has_item(self, item_name):
        return any(item.name == item_name for item in self.items)
        
    def show(self):
        if not self.items:
            print("Your inventory is empty.")
            return
        print("\n=== INVENTORY ===")
        for i, item in enumerate(self.items, 1):
            print(f"{i}. {item.name} - {item.description}")

class Room:
    def __init__(self, name, description, exits, items=None, zombies=None):
        self.name = name
        self.description = description
        self.exits = exits  # dict: direction -> room_name
        self.items = items or []
        self.zombies = zombies or []
        
    def describe(self):
        print(f"\n=== {self.name.upper()} ===")
        print(self.description)
        
        if self.items:
            print("\nYou see:")
            for item in self.items:
                print(f"  - {item.name}")
                
        if self.zombies:
            print(f"\n⚠️  There are {len(self.zombies)} zombie(s) here!")
            
        print("\nExits:", ", ".join(self.exits.keys()))

class Game:
    def __init__(self):
        self.inventory = Inventory()
        self.current_room = "street"
        self.health = 100
        self.score = 0
        self.zombies_killed = 0
        self.game_state = "playing"
        
        # Story flags
        self.story_flags = {
            "found_medicine": False,
            "found_weapon": False,
            "cured_zombies": False,
            "escaped": False
        }
        
        # Create items
        self.items = {
            "medicine": Item("Medicine", "A vial of experimental serum", "cure_zombies"),
            "weapon": Item("Weapon", "A trusty baseball bat", "kill_zombie"),
            "key": Item("Key", "A rusty old key", "unlock_door"),
            "flashlight": Item("Flashlight", "Lights up dark places", "light_area")
        }
        
        # Create rooms
        self.rooms = self.create_rooms()
        
    def create_rooms(self):
        rooms = {}
        
        # Street
        rooms["street"] = Room(
            "Street",
            "You're on a dark, foggy street in 1950s America. Old buildings loom in the shadows. "
            "A diner's neon sign flickers in the distance. The air is thick with an eerie silence.",
            {"north": "diner", "east": "hospital", "west": "basement"},
            [self.items["key"]]
        )
        
        # Diner
        rooms["diner"] = Room(
            "Diner",
            "A classic 1950s diner with red vinyl booths and chrome accents. "
            "The jukebox is silent, and the counter is covered in dust. "
            "Something feels... wrong here.",
            {"south": "street"},
            [self.items["weapon"]],
            ["zombie"]
        )
        
        # Hospital
        rooms["hospital"] = Room(
            "Hospital",
            "A sterile hospital corridor with flickering fluorescent lights. "
            "Medical equipment is scattered about. The air smells of antiseptic and... something else.",
            {"west": "street"},
            [self.items["medicine"]]
        )
        
        # Basement
        rooms["basement"] = Room(
            "Basement",
            "A dark, damp basement with exposed pipes and cobwebs. "
            "The air is thick with dust and the smell of old wood.",
            {"east": "street"},
            [self.items["flashlight"]]
        )
        
        return rooms
    
    def show_status(self):
        print(f"\nHealth: {self.health}/100 | Score: {self.score} | Zombies Killed: {self.zombies_killed}")
        print(f"Location: {self.current_room.title()}")
    
    def show_help(self):
        print("\n=== COMMANDS ===")
        print("look/l - Look around")
        print("north/n, south/s, east/e, west/w - Move")
        print("take <item> - Pick up an item")
        print("use <item> - Use an item")
        print("inventory/i - Show inventory")
        print("help/h - Show this help")
        print("quit/q - Quit game")
    
    def handle_command(self, command):
        cmd_parts = command.lower().split()
        if not cmd_parts:
            return
            
        cmd = cmd_parts[0]
        
        if cmd in ['look', 'l']:
            self.rooms[self.current_room].describe()
            
        elif cmd in ['north', 'n', 'south', 's', 'east', 'e', 'west', 'w']:
            self.move(cmd)
            
        elif cmd == 'take':
            if len(cmd_parts) > 1:
                self.take_item(' '.join(cmd_parts[1:]))
            else:
                print("Take what?")
                
        elif cmd == 'use':
            if len(cmd_parts) > 1:
                self.use_item(' '.join(cmd_parts[1:]))
            else:
                print("Use what?")
                
        elif cmd in ['inventory', 'i']:
            self.inventory.show()
            
        elif cmd in ['help', 'h']:
            self.show_help()
            
        elif cmd in ['quit', 'q']:
            print("Thanks for playing!")
            self.game_state = "quit"
            
        else:
            print("I don't understand that command. Type 'help' for available commands.")
    
    def move(self, direction):
        room = self.rooms[self.current_room]
        
        # Map direction aliases
        direction_map = {'n': 'north', 's': 'south', 'e': 'east', 'w': 'west'}
        direction = direction_map.get(direction, direction)
        
        if direction in room.exits:
            new_room = room.exits[direction]
            self.current_room = new_room
            print(f"You move {direction} to the {new_room}.")
            self.rooms[self.current_room].describe()
            
            # Check for zombies
            if self.rooms[self.current_room].zombies:
                self.encounter_zombies()
        else:
            print(f"You can't go {direction} from here.")
    
    def take_item(self, item_name):
        room = self.rooms[self.current_room]
        
        for item in room.items[:]:  # Copy list to avoid modification during iteration
            if item.name.lower() == item_name.lower():
                if self.inventory.add_item(item):
                    room.items.remove(item)
                    print(f"You pick up the {item.name}.")
                    self.score += 10
                    return
                else:
                    print("Your inventory is full!")
                    return
        
        print(f"You don't see a {item_name} here.")
    
    def use_item(self, item_name):
        if not self.inventory.has_item(item_name):
            print(f"You don't have a {item_name}.")
            return
            
        item = None
        for inv_item in self.inventory.items:
            if inv_item.name.lower() == item_name.lower():
                item = inv_item
                break
        
        if item.use_action == "cure_zombies":
            if self.current_room == "diner" and self.rooms[self.current_room].zombies:
                print("You use the medicine on the zombie. It transforms back into a human!")
                self.rooms[self.current_room].zombies.clear()
                self.story_flags["cured_zombies"] = True
                self.score += 50
                self.inventory.remove_item(item_name)
            else:
                print("There are no zombies here to cure.")
                
        elif item.use_action == "kill_zombie":
            if self.rooms[self.current_room].zombies:
                print("You swing the baseball bat at the zombie! It falls to the ground.")
                self.rooms[self.current_room].zombies.clear()
                self.zombies_killed += 1
                self.score += 25
                self.inventory.remove_item(item_name)
            else:
                print("There are no zombies here to fight.")
                
        elif item.use_action == "unlock_door":
            print("You use the key, but there are no locked doors here.")
            
        elif item.use_action == "light_area":
            print("You turn on the flashlight, illuminating the area better.")
            self.score += 5
            
        else:
            print(f"You use the {item.name}, but nothing special happens.")
    
    def encounter_zombies(self):
        print("\n💀 A ZOMBIE APPEARS! 💀")
        print("The zombie lunges at you!")
        
        if self.inventory.has_item("Weapon"):
            print("You quickly grab your baseball bat and defend yourself!")
            self.zombies_killed += 1
            self.score += 25
            self.rooms[self.current_room].zombies.clear()
            print("The zombie is defeated!")
        else:
            print("You have no weapon! The zombie attacks you!")
            self.health -= 30
            print(f"You take 30 damage! Health: {self.health}")
            
            if self.health <= 0:
                print("\n💀 GAME OVER 💀")
                print("You have been killed by zombies!")
                self.game_state = "game_over"
    
    def check_victory(self):
        if (self.story_flags["cured_zombies"] and 
            self.zombies_killed >= 1 and 
            self.score >= 100):
            print("\n🎉 VICTORY! 🎉")
            print("You have successfully survived the zombie apocalypse!")
            print(f"Final Score: {self.score}")
            print("You cured the zombies and escaped with your life!")
            self.game_state = "victory"
    
    def run(self):
        print("🎮 1950's ZOMBIE QUEST - TERMINAL EDITION 🎮")
        print("=" * 50)
        print("You find yourself in a mysterious 1950s town...")
        print("Zombies have taken over! Can you survive and find a cure?")
        print("\nType 'help' for commands.")
        
        # Initial room description
        self.rooms[self.current_room].describe()
        
        while self.game_state == "playing":
            self.show_status()
            
            try:
                command = input("\n> ").strip()
                if command:
                    self.handle_command(command)
                    self.check_victory()
            except KeyboardInterrupt:
                print("\n\nGame interrupted. Thanks for playing!")
                break
            except EOFError:
                print("\n\nGame ended. Thanks for playing!")
                break

if __name__ == "__main__":
    game = Game()
    game.run()