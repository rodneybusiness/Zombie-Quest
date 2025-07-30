import os
# Set up display for headless environment before importing pygame
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import pygame
import math
import time
import random
import json

# Sierra 256-color VGA palette (as RGB tuples for modern Pygame)
VGA_PALETTE = [
    (0, 0, 0), (0, 0, 170), (0, 170, 0), (0, 170, 170), (170, 0, 0), (170, 0, 170), (170, 85, 0), (170, 170, 170),
    (85, 85, 85), (85, 85, 255), (85, 255, 85), (85, 255, 255), (255, 85, 85), (255, 85, 255), (255, 255, 85), (255, 255, 255),
    (0, 0, 0), (20, 20, 20), (32, 32, 32), (44, 44, 44), (56, 56, 56), (68, 68, 68), (80, 80, 80), (96, 96, 96),
    (112, 112, 112), (128, 128, 128), (144, 144, 144), (160, 160, 160), (180, 180, 180), (200, 200, 200), (224, 224, 224), (252, 252, 252),
    (0, 0, 252), (64, 0, 252), (124, 0, 252), (188, 0, 252), (252, 0, 252), (252, 0, 188), (252, 0, 124), (252, 0, 64),
    (252, 0, 0), (252, 64, 0), (252, 124, 0), (252, 188, 0), (252, 252, 0), (188, 252, 0), (124, 252, 0), (64, 252, 0),
    (0, 252, 0), (0, 252, 64), (0, 252, 124), (0, 252, 188), (0, 252, 252), (0, 188, 252), (0, 124, 252), (0, 64, 252),
    (124, 124, 252), (156, 124, 252), (188, 124, 252), (220, 124, 252), (252, 124, 252), (252, 124, 220), (252, 124, 188), (252, 124, 156),
    (252, 124, 124), (252, 156, 124), (252, 188, 124), (252, 220, 124), (252, 252, 124), (220, 252, 124), (188, 252, 124), (156, 252, 124),
    (124, 252, 124), (124, 252, 156), (124, 252, 188), (124, 252, 220), (124, 252, 252), (124, 220, 252), (124, 188, 252), (124, 156, 252),
    (180, 180, 252), (196, 180, 252), (212, 180, 252), (228, 180, 252), (252, 180, 252), (252, 180, 228), (252, 180, 212), (252, 180, 196),
    (252, 180, 180), (252, 196, 180), (252, 212, 180), (252, 228, 180), (252, 252, 180), (228, 252, 180), (212, 252, 180), (196, 252, 180),
    (180, 252, 180), (180, 252, 196), (180, 252, 212), (180, 252, 228), (180, 252, 252), (180, 228, 252), (180, 212, 252), (180, 196, 252),
    (0, 0, 112), (28, 0, 112), (56, 0, 112), (84, 0, 112), (112, 0, 112), (112, 0, 84), (112, 0, 56), (112, 0, 28),
    (112, 0, 0), (112, 28, 0), (112, 56, 0), (112, 84, 0), (112, 112, 0), (84, 112, 0), (56, 112, 0), (28, 112, 0),
    (0, 112, 0), (0, 112, 28), (0, 112, 56), (0, 112, 84), (0, 112, 112), (0, 84, 112), (0, 56, 112), (0, 28, 112),
    (56, 56, 112), (68, 56, 112), (84, 56, 112), (96, 56, 112), (112, 56, 112), (112, 56, 96), (112, 56, 84), (112, 56, 68),
    (112, 56, 56), (112, 68, 56), (112, 84, 56), (112, 96, 56), (112, 112, 56), (96, 112, 56), (84, 112, 56), (68, 112, 56),
    (56, 112, 56), (56, 112, 68), (56, 112, 84), (56, 112, 96), (56, 112, 112), (56, 96, 112), (56, 84, 112), (56, 68, 112),
    (80, 80, 112), (88, 80, 112), (96, 80, 112), (104, 80, 112), (112, 80, 112), (112, 80, 104), (112, 80, 96), (112, 80, 88),
    (112, 80, 80), (112, 88, 80), (112, 96, 80), (112, 104, 80), (112, 112, 80), (104, 112, 80), (96, 112, 80), (88, 112, 80),
    (80, 112, 80), (80, 112, 88), (80, 112, 96), (80, 112, 104), (80, 112, 112), (80, 104, 112), (80, 96, 112), (80, 88, 112),
    (0, 0, 64), (16, 0, 64), (32, 0, 64), (48, 0, 64), (64, 0, 64), (64, 0, 48), (64, 0, 32), (64, 0, 16),
    (64, 0, 0), (64, 16, 0), (64, 32, 0), (64, 48, 0), (64, 64, 0), (48, 64, 0), (32, 64, 0), (16, 64, 0),
    (0, 64, 0), (0, 64, 16), (0, 64, 32), (0, 64, 48), (0, 64, 64), (0, 48, 64), (0, 32, 64), (0, 16, 64),
    (32, 32, 64), (40, 32, 64), (48, 32, 64), (56, 32, 64), (64, 32, 64), (64, 32, 56), (64, 32, 48), (64, 32, 40),
    (64, 32, 32), (64, 40, 32), (64, 48, 32), (64, 56, 32), (64, 64, 32), (56, 64, 32), (48, 64, 32), (40, 64, 32),
    (32, 64, 32), (32, 64, 40), (32, 64, 48), (32, 64, 56), (32, 64, 64), (32, 56, 64), (32, 48, 64), (32, 40, 64),
    (44, 44, 64), (48, 44, 64), (52, 44, 64), (56, 44, 64), (60, 44, 64), (64, 44, 64), (64, 44, 60), (64, 44, 56),
    (64, 44, 52), (64, 44, 48), (64, 44, 44), (64, 48, 44), (64, 52, 44), (64, 56, 44), (64, 60, 44), (64, 64, 44),
    (60, 64, 44), (56, 64, 44), (52, 64, 44), (48, 64, 44), (44, 64, 44), (44, 64, 48), (44, 64, 52), (44, 64, 56),
    (44, 64, 60), (44, 64, 64), (44, 60, 64), (44, 56, 64), (44, 52, 64), (44, 48, 64), (0, 0, 0), (252, 252, 252)
]

class Item:
    def __init__(self, name, description, icon_color, use_action=None):
        self.name = name
        self.description = description
        self.icon_color = icon_color
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
        
    def draw(self, screen, x, y):
        # Draw inventory background
        pygame.draw.rect(screen, VGA_PALETTE[8], (x, y, 200, 60))
        pygame.draw.rect(screen, VGA_PALETTE[15], (x, y, 200, 60), 2)
        
        # Draw items
        for i, item in enumerate(self.items):
            item_x = x + 10 + (i * 24)
            item_y = y + 10
            
            # Item icon
            pygame.draw.rect(screen, item.icon_color, (item_x, item_y, 16, 16))
            pygame.draw.rect(screen, VGA_PALETTE[0], (item_x, item_y, 16, 16), 1)
            
            # Item name (shortened)
            font = pygame.font.Font(None, 12)
            text = font.render(item.name[:3], True, VGA_PALETTE[15])
            screen.blit(text, (item_x, item_y + 18))

class MessageBar:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.message = ""
        self.start_time = 0
        self.duration = 3.0
        self.visible = False
        self.surface = pygame.Surface((width, height))
        
    def show_message(self, text):
        self.message = text
        self.start_time = time.time()
        self.visible = True
        
    def update(self):
        if self.visible and time.time() - self.start_time > self.duration:
            self.visible = False
            
    def draw(self, screen):
        if not self.visible:
            return
            
        # Blue gradient background
        for y in range(self.height):
            color_val = max(0, min(255, 64 + (y * 32 // self.height)))
            pygame.draw.line(self.surface, (0, 0, color_val), (0, y), (self.width, y))
            
        # Render text
        font = pygame.font.Font(None, 16)
        text_surface = font.render(self.message, True, VGA_PALETTE[15])
        text_x = (self.width - text_surface.get_width()) // 2
        text_y = (self.height - text_surface.get_height()) // 2
        self.surface.blit(text_surface, (text_x, text_y))
        
        screen.blit(self.surface, (0, screen.get_height() - self.height))

class Hotspot:
    def __init__(self, x, y, width, height, action, name, description="", required_item=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.action = action
        self.name = name
        self.description = description
        self.required_item = required_item

class Zombie:
    def __init__(self, x, y, room):
        self.x = x
        self.y = y
        self.room = room
        self.direction = random.randint(0, 3)
        self.speed = 0.5
        self.animation_frame = 0
        self.animation_timer = 0
        self.alive = True
        
    def update(self, hero_x, hero_y):
        if not self.alive:
            return
            
        # Simple AI: move towards hero
        dx = hero_x - self.x
        dy = hero_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
            
            # Update direction
            if abs(dx) > abs(dy):
                self.direction = 1 if dx < 0 else 2
            else:
                self.direction = 3 if dy < 0 else 0
                
        # Animation
        self.animation_timer += 1
        if self.animation_timer >= 16:
            self.animation_frame = (self.animation_frame + 1) % 4
            self.animation_timer = 0
            
    def draw(self, screen):
        if not self.alive:
            return
            
        # Draw zombie (green stickman)
        color = VGA_PALETTE[10]  # Green
        
        # Head
        pygame.draw.circle(screen, color, (int(self.x), int(self.y) - 20), 6)
        
        # Body
        pygame.draw.line(screen, color, (int(self.x), int(self.y) - 14), (int(self.x), int(self.y)), 3)
        
        # Arms (animated)
        arm_swing = math.sin(self.animation_frame * 0.5) * 4
        pygame.draw.line(screen, color, (int(self.x), int(self.y) - 10), (int(self.x - 8 + arm_swing), int(self.y) - 5), 3)
        pygame.draw.line(screen, color, (int(self.x), int(self.y) - 10), (int(self.x + 8 - arm_swing), int(self.y) - 5), 3)
        
        # Legs (shambling)
        leg_swing = math.sin(self.animation_frame * 0.5) * 3
        pygame.draw.line(screen, color, (int(self.x), int(self.y)), (int(self.x - 6 + leg_swing), int(self.y) + 8), 3)
        pygame.draw.line(screen, color, (int(self.x), int(self.y)), (int(self.x + 6 - leg_swing), int(self.y) + 8), 3)

class Hero:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.speed = 2
        self.direction = 0  # 0=down, 1=left, 2=right, 3=up
        self.animation_frame = 0
        self.animation_timer = 0
        self.bob_offset = 0
        self.bob_timer = 0
        self.health = 100
        self.max_health = 100
        
    def update(self, walkbox):
        # Move towards target
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > self.speed:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
            
            # Update direction
            if abs(dx) > abs(dy):
                self.direction = 1 if dx < 0 else 2
            else:
                self.direction = 3 if dy < 0 else 0
                
            # Animation
            self.animation_timer += 1
            if self.animation_timer >= 8:
                self.animation_frame = (self.animation_frame + 1) % 8
                self.animation_timer = 0
                
                # Vertical bob every other frame
                self.bob_timer += 1
                if self.bob_timer % 2 == 0:
                    self.bob_offset = 1 if self.bob_offset == 0 else 0
        else:
            self.x = self.target_x
            self.y = self.target_y
            
        # Keep within walkbox
        self.x = max(walkbox.left, min(walkbox.right, self.x))
        self.y = max(walkbox.top, min(walkbox.bottom, self.y))
        
    def set_target(self, x, y):
        self.target_x = x
        self.target_y = y
        
    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
        
    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)
        
    def draw(self, screen, priority_mask):
        # Draw hero (blue stickman)
        color = VGA_PALETTE[9]  # Blue
        
        # Head
        pygame.draw.circle(screen, color, (int(self.x), int(self.y) - 20), 6)
        
        # Body
        pygame.draw.line(screen, color, (int(self.x), int(self.y) - 14), (int(self.x), int(self.y)), 3)
        
        # Arms (animated)
        arm_swing = math.sin(self.animation_frame * 0.5) * 4
        pygame.draw.line(screen, color, (int(self.x), int(self.y) - 10), (int(self.x - 8 + arm_swing), int(self.y) - 5), 3)
        pygame.draw.line(screen, color, (int(self.x), int(self.y) - 10), (int(self.x + 8 - arm_swing), int(self.y) - 5), 3)
        
        # Legs (animated)
        leg_swing = math.sin(self.animation_frame * 0.5) * 3
        pygame.draw.line(screen, color, (int(self.x), int(self.y)), (int(self.x - 6 + leg_swing), int(self.y) + 8), 3)
        pygame.draw.line(screen, color, (int(self.x), int(self.y)), (int(self.x + 6 - leg_swing), int(self.y) + 8), 3)

class Room:
    def __init__(self, name, background_color, walkbox, hotspots, zombies=None, priority_mask=None):
        self.name = name
        self.background_color = background_color
        self.walkbox = walkbox
        self.hotspots = hotspots
        self.zombies = zombies or []
        self.priority_mask = priority_mask
        self.background_surface = None
        
    def generate_background(self, width, height):
        if self.background_surface is None:
            self.background_surface = pygame.Surface((width, height))
            self.background_surface.fill(self.background_color)
            
            if self.name == "street_vga":
                # Street scene with buildings
                pygame.draw.rect(self.background_surface, VGA_PALETTE[8], (0, 0, width, height//2))  # Sky
                pygame.draw.rect(self.background_surface, VGA_PALETTE[7], (0, height//2, width, height//2))  # Ground
                pygame.draw.rect(self.background_surface, VGA_PALETTE[6], (50, 50, 60, 100))  # Building 1
                pygame.draw.rect(self.background_surface, VGA_PALETTE[6], (150, 60, 60, 90))  # Building 2
                pygame.draw.rect(self.background_surface, VGA_PALETTE[6], (250, 40, 60, 110))  # Building 3
                pygame.draw.rect(self.background_surface, VGA_PALETTE[12], (260, 120, 40, 60))  # Door
                
            elif self.name == "diner_vga":
                # Diner scene
                pygame.draw.rect(self.background_surface, VGA_PALETTE[1], (0, 0, width, height))  # Dark background
                pygame.draw.rect(self.background_surface, VGA_PALETTE[15], (50, 50, 220, 100))  # Diner counter
                pygame.draw.rect(self.background_surface, VGA_PALETTE[12], (100, 80, 40, 40))  # Stool 1
                pygame.draw.rect(self.background_surface, VGA_PALETTE[12], (180, 80, 40, 40))  # Stool 2
                
            elif self.name == "hospital_vga":
                # Hospital scene
                pygame.draw.rect(self.background_surface, VGA_PALETTE[15], (0, 0, width, height))  # White walls
                pygame.draw.rect(self.background_surface, VGA_PALETTE[8], (50, 50, 80, 120))  # Bed
                pygame.draw.rect(self.background_surface, VGA_PALETTE[12], (200, 50, 60, 80))  # Medical cabinet
                pygame.draw.rect(self.background_surface, VGA_PALETTE[6], (20, 140, 40, 60))  # Exit door
                
            elif self.name == "basement_vga":
                # Basement scene
                pygame.draw.rect(self.background_surface, VGA_PALETTE[0], (0, 0, width, height))  # Dark
                pygame.draw.rect(self.background_surface, VGA_PALETTE[8], (50, 50, 100, 80))  # Workbench
                pygame.draw.rect(self.background_surface, VGA_PALETTE[12], (200, 50, 60, 80))  # Storage
                pygame.draw.rect(self.background_surface, VGA_PALETTE[6], (20, 140, 40, 60))  # Exit
                
        return self.background_surface
        
    def update_zombies(self, hero_x, hero_y):
        for zombie in self.zombies:
            zombie.update(hero_x, hero_y)
            
    def draw_zombies(self, screen):
        for zombie in self.zombies:
            zombie.draw(screen)

class Game:
    def __init__(self):
        pygame.init()
        # Try to initialize audio, but don't fail if no audio device is available
        try:
            pygame.mixer.init()
        except pygame.error:
            print("Warning: No audio device available. Game will run without sound.")
        
        self.width, self.height = 320, 200
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("1950's Zombie Quest - Enhanced Edition")
        
        # Create game objects
        self.inventory = Inventory()
        self.rooms = self.create_rooms()
        self.current_room = "street_vga"
        self.hero = Hero(160, 150)
        self.message_bar = MessageBar(self.width, 20)
        
        # Game state
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = "playing"  # playing, paused, game_over, victory
        self.score = 0
        self.zombies_killed = 0
        
        # Story progress
        self.story_flags = {
            "found_medicine": False,
            "found_weapon": False,
            "cured_zombies": False,
            "escaped": False
        }
        
        # Initialize items
        self.create_items()
        
    def create_items(self):
        self.items = {
            "medicine": Item("Medicine", "A vial of experimental serum", VGA_PALETTE[11], "cure_zombies"),
            "weapon": Item("Weapon", "A trusty baseball bat", VGA_PALETTE[7], "kill_zombie"),
            "key": Item("Key", "A rusty old key", VGA_PALETTE[14], "unlock_door"),
            "flashlight": Item("Flashlight", "Lights up dark places", VGA_PALETTE[15], "light_area")
        }
        
    def create_rooms(self):
        rooms = {}
        
        # Street room
        street_hotspots = [
            Hotspot(260, 120, 40, 60, "goto_diner", "door", "Enter the diner"),
            Hotspot(100, 140, 32, 40, "search_trash", "trashcan", "Search the trash"),
            Hotspot(50, 50, 60, 100, "search_building", "building", "Search the building")
        ]
        street_zombies = [Zombie(200, 100, "street_vga")]
        rooms["street_vga"] = Room("street_vga", VGA_PALETTE[8], 
                                 pygame.Rect(20, 100, 280, 80), street_hotspots, street_zombies, True)
        
        # Diner room
        diner_hotspots = [
            Hotspot(20, 140, 40, 60, "goto_street", "exit", "Exit to street"),
            Hotspot(50, 50, 220, 100, "search_counter", "counter", "Search the counter"),
            Hotspot(100, 80, 40, 40, "sit_stool", "stool", "Sit on stool")
        ]
        diner_zombies = [Zombie(150, 80, "diner_vga")]
        rooms["diner_vga"] = Room("diner_vga", VGA_PALETTE[1], 
                                pygame.Rect(20, 100, 280, 80), diner_hotspots, diner_zombies, True)
        
        # Hospital room
        hospital_hotspots = [
            Hotspot(20, 140, 40, 60, "goto_street", "exit", "Exit to street"),
            Hotspot(200, 50, 60, 80, "search_cabinet", "cabinet", "Search medical cabinet"),
            Hotspot(50, 50, 80, 120, "search_bed", "bed", "Search the bed")
        ]
        rooms["hospital_vga"] = Room("hospital_vga", VGA_PALETTE[15], 
                                   pygame.Rect(20, 100, 280, 80), hospital_hotspots, [], True)
        
        # Basement room
        basement_hotspots = [
            Hotspot(20, 140, 40, 60, "goto_street", "exit", "Exit to street"),
            Hotspot(50, 50, 100, 80, "search_workbench", "workbench", "Search workbench"),
            Hotspot(200, 50, 60, 80, "search_storage", "storage", "Search storage")
        ]
        rooms["basement_vga"] = Room("basement_vga", VGA_PALETTE[0], 
                                   pygame.Rect(20, 100, 280, 80), basement_hotspots, [], True)
        
        return rooms
        
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.check_hotspots()
                elif event.key == pygame.K_i:
                    self.toggle_inventory()
                elif event.key == pygame.K_s:
                    self.save_game()
                elif event.key == pygame.K_l:
                    self.load_game()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    self.handle_mouse_click(mouse_x, mouse_y)
                    
        # Keyboard movement
        keys = pygame.key.get_pressed()
        room = self.rooms[self.current_room]
        
        if keys[pygame.K_LEFT]:
            self.hero.set_target(max(room.walkbox.left, self.hero.x - 10), self.hero.y)
        elif keys[pygame.K_RIGHT]:
            self.hero.set_target(min(room.walkbox.right, self.hero.x + 10), self.hero.y)
        elif keys[pygame.K_UP]:
            self.hero.set_target(self.hero.x, max(room.walkbox.top, self.hero.y - 10))
        elif keys[pygame.K_DOWN]:
            self.hero.set_target(self.hero.x, min(room.walkbox.bottom, self.hero.y + 10))
            
    def handle_mouse_click(self, x, y):
        # Check if clicking on walkbox
        room = self.rooms[self.current_room]
        if room.walkbox.collidepoint(x, y):
            self.hero.set_target(x, y)
        else:
            # Check hotspots
            self.check_hotspots_at(x, y)
            
    def check_hotspots(self):
        self.check_hotspots_at(self.hero.x, self.hero.y)
        
    def check_hotspots_at(self, x, y):
        room = self.rooms[self.current_room]
        for hotspot in room.hotspots:
            if hotspot.rect.collidepoint(x, y):
                self.execute_hotspot_action(hotspot)
                break
                
    def execute_hotspot_action(self, hotspot):
        if hotspot.required_item and not self.inventory.has_item(hotspot.required_item):
            self.message_bar.show_message(f"You need {hotspot.required_item} to do that!")
            return
            
        if hotspot.action == "goto_diner":
            self.current_room = "diner_vga"
            self.hero.x = 280
            self.hero.y = 150
            self.hero.set_target(self.hero.x, self.hero.y)
            self.message_bar.show_message("You enter the diner...")
            
        elif hotspot.action == "goto_street":
            self.current_room = "street_vga"
            self.hero.x = 20
            self.hero.y = 150
            self.hero.set_target(self.hero.x, self.hero.y)
            self.message_bar.show_message("You exit to the street...")
            
        elif hotspot.action == "search_trash":
            if not self.inventory.has_item("weapon"):
                self.inventory.add_item(self.items["weapon"])
                self.message_bar.show_message("You found a baseball bat!")
                self.story_flags["found_weapon"] = True
            else:
                self.message_bar.show_message("Just more garbage...")
                
        elif hotspot.action == "search_building":
            self.message_bar.show_message("The building is locked tight.")
            
        elif hotspot.action == "search_counter":
            if not self.inventory.has_item("key"):
                self.inventory.add_item(self.items["key"])
                self.message_bar.show_message("You found a key!")
            else:
                self.message_bar.show_message("Nothing else here...")
                
        elif hotspot.action == "sit_stool":
            self.message_bar.show_message("You sit down. The stool creaks ominously.")
            
        elif hotspot.action == "search_cabinet":
            if not self.inventory.has_item("medicine"):
                self.inventory.add_item(self.items["medicine"])
                self.message_bar.show_message("You found experimental medicine!")
                self.story_flags["found_medicine"] = True
            else:
                self.message_bar.show_message("The cabinet is empty.")
                
        elif hotspot.action == "search_bed":
            self.message_bar.show_message("Just an empty hospital bed.")
            
        elif hotspot.action == "search_workbench":
            if not self.inventory.has_item("flashlight"):
                self.inventory.add_item(self.items["flashlight"])
                self.message_bar.show_message("You found a flashlight!")
            else:
                self.message_bar.show_message("Just tools and parts.")
                
        elif hotspot.action == "search_storage":
            self.message_bar.show_message("Old boxes and supplies.")
            
    def toggle_inventory(self):
        # Simple inventory display
        self.message_bar.show_message(f"Inventory: {', '.join([item.name for item in self.inventory.items])}")
        
    def save_game(self):
        save_data = {
            "hero_x": self.hero.x,
            "hero_y": self.hero.y,
            "hero_health": self.hero.health,
            "current_room": self.current_room,
            "score": self.score,
            "zombies_killed": self.zombies_killed,
            "story_flags": self.story_flags,
            "inventory": [item.name for item in self.inventory.items]
        }
        
        try:
            with open("savegame.json", "w") as f:
                json.dump(save_data, f)
            self.message_bar.show_message("Game saved!")
        except:
            self.message_bar.show_message("Save failed!")
            
    def load_game(self):
        try:
            with open("savegame.json", "r") as f:
                save_data = json.load(f)
                
            self.hero.x = save_data["hero_x"]
            self.hero.y = save_data["hero_y"]
            self.hero.health = save_data["hero_health"]
            self.current_room = save_data["current_room"]
            self.score = save_data["score"]
            self.zombies_killed = save_data["zombies_killed"]
            self.story_flags = save_data["story_flags"]
            
            # Restore inventory
            self.inventory.items = []
            for item_name in save_data["inventory"]:
                if item_name in self.items:
                    self.inventory.add_item(self.items[item_name])
                    
            self.message_bar.show_message("Game loaded!")
        except:
            self.message_bar.show_message("Load failed!")
            
    def check_zombie_collision(self):
        room = self.rooms[self.current_room]
        for zombie in room.zombies:
            if zombie.alive:
                distance = math.sqrt((self.hero.x - zombie.x)**2 + (self.hero.y - zombie.y)**2)
                if distance < 20:
                    self.hero.take_damage(10)
                    self.message_bar.show_message("A zombie attacks you!")
                    
                    if self.hero.health <= 0:
                        self.game_state = "game_over"
                        self.message_bar.show_message("You have been eaten by zombies!")
                        
    def update(self):
        if self.game_state != "playing":
            return
            
        room = self.rooms[self.current_room]
        self.hero.update(room.walkbox)
        self.message_bar.update()
        room.update_zombies(self.hero.x, self.hero.y)
        self.check_zombie_collision()
        
        # Check victory condition
        if (self.story_flags["found_medicine"] and 
            self.story_flags["found_weapon"] and 
            self.zombies_killed >= 2):
            self.game_state = "victory"
            self.message_bar.show_message("You have survived the zombie apocalypse!")
        
    def draw(self):
        room = self.rooms[self.current_room]
        
        # Draw background
        background = room.generate_background(self.width, self.height)
        self.screen.blit(background, (0, 0))
        
        # Draw zombies
        room.draw_zombies(self.screen)
        
        # Draw hero
        self.hero.draw(self.screen, None)
        
        # Draw UI
        self.draw_ui()
        
        # Draw message bar
        self.message_bar.draw(self.screen)
        
        pygame.display.flip()
        
    def draw_ui(self):
        # Health bar
        health_width = 100
        health_height = 10
        health_x = 10
        health_y = 10
        
        # Background
        pygame.draw.rect(self.screen, VGA_PALETTE[8], (health_x, health_y, health_width, health_height))
        # Health
        current_health_width = int((self.hero.health / self.hero.max_health) * health_width)
        health_color = VGA_PALETTE[10] if self.hero.health > 50 else VGA_PALETTE[12] if self.hero.health > 25 else VGA_PALETTE[4]
        pygame.draw.rect(self.screen, health_color, (health_x, health_y, current_health_width, health_height))
        # Border
        pygame.draw.rect(self.screen, VGA_PALETTE[15], (health_x, health_y, health_width, health_height), 1)
        
        # Score
        font = pygame.font.Font(None, 16)
        score_text = font.render(f"Score: {self.score}", True, VGA_PALETTE[15])
        self.screen.blit(score_text, (120, 10))
        
        # Room name
        room_text = font.render(f"Room: {self.current_room}", True, VGA_PALETTE[15])
        self.screen.blit(room_text, (120, 25))
        
        # Controls hint
        controls_text = font.render("WASD: Move, SPACE: Action, I: Inventory, S: Save, L: Load", True, VGA_PALETTE[15])
        self.screen.blit(controls_text, (10, self.height - 40))
        
        # Game over screen
        if self.game_state == "game_over":
            self.draw_game_over_screen()
        elif self.game_state == "victory":
            self.draw_victory_screen()
        
    def draw_game_over_screen(self):
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill(VGA_PALETTE[0])
        self.screen.blit(overlay, (0, 0))
        
        font = pygame.font.Font(None, 24)
        text = font.render("GAME OVER", True, VGA_PALETTE[4])
        text_x = (self.width - text.get_width()) // 2
        text_y = (self.height - text.get_height()) // 2
        self.screen.blit(text, (text_x, text_y))
        
        font_small = pygame.font.Font(None, 16)
        restart_text = font_small.render("Press ESC to quit", True, VGA_PALETTE[15])
        restart_x = (self.width - restart_text.get_width()) // 2
        restart_y = text_y + 30
        self.screen.blit(restart_text, (restart_x, restart_y))
        
    def draw_victory_screen(self):
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill(VGA_PALETTE[0])
        self.screen.blit(overlay, (0, 0))
        
        font = pygame.font.Font(None, 24)
        text = font.render("VICTORY!", True, VGA_PALETTE[10])
        text_x = (self.width - text.get_width()) // 2
        text_y = (self.height - text.get_height()) // 2
        self.screen.blit(text, (text_x, text_y))
        
        font_small = pygame.font.Font(None, 16)
        score_text = font_small.render(f"Final Score: {self.score}", True, VGA_PALETTE[15])
        score_x = (self.width - score_text.get_width()) // 2
        score_y = text_y + 30
        self.screen.blit(score_text, (score_x, score_y))
        
        restart_text = font_small.render("Press ESC to quit", True, VGA_PALETTE[15])
        restart_x = (self.width - restart_text.get_width()) // 2
        restart_y = score_y + 20
        self.screen.blit(restart_text, (restart_x, restart_y))
        
    def run(self):
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)
            
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()