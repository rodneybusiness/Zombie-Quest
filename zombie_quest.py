import pygame
import math
import time

# Sierra 256-color VGA palette
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

# Leroy 8x8 font bitmap (monochrome)
LEROY_FONT = """
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
"""

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
        font_surface = self.render_text(self.message, 15)  # White text
        text_x = (self.width - font_surface.get_width()) // 2
        text_y = (self.height - font_surface.get_height()) // 2
        self.surface.blit(font_surface, (text_x, text_y))
        
        screen.blit(self.surface, (0, screen.get_height() - self.height))
        
    def render_text(self, text, color_index):
        char_width, char_height = 8, 8
        surface = pygame.Surface((len(text) * char_width, char_height))
        surface.set_colorkey((0, 0, 0))
        
        for i, char in enumerate(text):
            if char == ' ':
                continue
            char_surface = self.render_char(char, color_index)
            surface.blit(char_surface, (i * char_width, 0))
            
        return surface
        
    def render_char(self, char, color_index):
        # Simple character rendering - just a colored rectangle for MVP
        char_surface = pygame.Surface((8, 8))
        char_surface.fill(VGA_PALETTE[color_index])
        return char_surface

class Hotspot:
    def __init__(self, x, y, width, height, action, name):
        self.rect = pygame.Rect(x, y, width, height)
        self.action = action
        self.name = name

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
        
        # Generate 32x48 sprite sheet with 4 rows of 8 frames each
        self.sprite_sheet = self.generate_sprite_sheet()
        
    def generate_sprite_sheet(self):
        sheet = pygame.Surface((256, 192))  # 8 frames * 32px wide, 4 directions * 48px tall
        sheet.set_colorkey((0, 0, 0))
        
        for direction in range(4):
            for frame in range(8):
                x = frame * 32
                y = direction * 48
                
                # Draw stickman for each frame
                self.draw_stickman_frame(sheet, x, y, direction, frame)
                
        return sheet
        
    def draw_stickman_frame(self, surface, x, y, direction, frame):
        # NES-style stickman
        color = VGA_PALETTE[15]  # White
        
        # Head
        pygame.draw.circle(surface, color, (x + 16, y + 8), 4)
        
        # Body
        pygame.draw.line(surface, color, (x + 16, y + 12), (x + 16, y + 28), 2)
        
        # Arms (animate based on frame)
        arm_swing = math.sin(frame * 0.5) * 3
        pygame.draw.line(surface, color, (x + 16, y + 16), (x + 12 + arm_swing, y + 20), 2)
        pygame.draw.line(surface, color, (x + 16, y + 16), (x + 20 - arm_swing, y + 20), 2)
        
        # Legs (animate based on frame)
        leg_swing = math.sin(frame * 0.5) * 4
        pygame.draw.line(surface, color, (x + 16, y + 28), (x + 12 + leg_swing, y + 36), 2)
        pygame.draw.line(surface, color, (x + 16, y + 28), (x + 20 - leg_swing, y + 36), 2)
        
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
        
    def draw(self, screen, priority_mask):
        # Get current sprite
        sprite_x = self.animation_frame * 32
        sprite_y = self.direction * 48
        
        sprite = pygame.Surface((32, 48))
        sprite.set_colorkey((0, 0, 0))
        sprite.blit(self.sprite_sheet, (0, 0), (sprite_x, sprite_y, 32, 48))
        
        # Apply vertical bob
        draw_y = self.y - 48 + self.bob_offset
        
        # Check priority mask for walk-behind
        if priority_mask:
            mask_rect = pygame.Rect(self.x - 16, draw_y, 32, 48)
            if priority_mask.get_at((self.x, draw_y + 24))[0] < 128:  # Behind
                screen.blit(sprite, (self.x - 16, draw_y))
            else:  # In front
                screen.blit(sprite, (self.x - 16, draw_y))
        else:
            screen.blit(sprite, (self.x - 16, draw_y))

class Room:
    def __init__(self, name, background_color, walkbox, hotspots, priority_mask=None):
        self.name = name
        self.background_color = background_color
        self.walkbox = walkbox
        self.hotspots = hotspots
        self.priority_mask = priority_mask
        self.palette_cycle_timer = 0
        self.palette_cycle_index = 0
        
    def generate_background(self, width, height):
        surface = pygame.Surface((width, height))
        surface.fill(self.background_color)
        
        if self.name == "street_vga":
            # Street scene with buildings
            pygame.draw.rect(surface, VGA_PALETTE[8], (0, 0, width, height//2))  # Sky
            pygame.draw.rect(surface, VGA_PALETTE[7], (0, height//2, width, height//2))  # Ground
            pygame.draw.rect(surface, VGA_PALETTE[6], (50, 50, 60, 100))  # Building 1
            pygame.draw.rect(surface, VGA_PALETTE[6], (150, 60, 60, 90))  # Building 2
            pygame.draw.rect(surface, VGA_PALETTE[6], (250, 40, 60, 110))  # Building 3
            
        elif self.name == "diner_vga":
            # Diner scene
            pygame.draw.rect(surface, VGA_PALETTE[1], (0, 0, width, height))  # Dark background
            pygame.draw.rect(surface, VGA_PALETTE[15], (50, 50, 220, 100))  # Diner counter
            pygame.draw.rect(surface, VGA_PALETTE[12], (100, 80, 40, 40))  # Stool 1
            pygame.draw.rect(surface, VGA_PALETTE[12], (180, 80, 40, 40))  # Stool 2
            
        return surface
        
    def generate_priority_mask(self, width, height):
        if not self.priority_mask:
            return None
            
        mask = pygame.Surface((width, height))
        mask.fill((255, 255, 255))
        
        if self.name == "street_vga":
            # Doorframe priority
            pygame.draw.rect(mask, (128, 128, 128), (260, 120, 40, 60))
            
        elif self.name == "diner_vga":
            # Counter priority
            pygame.draw.rect(mask, (128, 128, 128), (50, 50, 220, 100))
            
        return mask
        
    def update_palette_cycle(self, surface):
        if self.name == "diner_vga":
            self.palette_cycle_timer += 1
            if self.palette_cycle_timer >= 12:  # 0.2s at 60fps
                self.palette_cycle_timer = 0
                self.palette_cycle_index = (self.palette_cycle_index + 1) % 4
                
                # Cycle neon colors
                neon_colors = [VGA_PALETTE[12], VGA_PALETTE[13], VGA_PALETTE[14], VGA_PALETTE[15]]
                surface.set_palette_at(12, neon_colors[self.palette_cycle_index])
                surface.set_palette_at(13, neon_colors[(self.palette_cycle_index + 1) % 4])
                surface.set_palette_at(14, neon_colors[(self.palette_cycle_index + 2) % 4])
                surface.set_palette_at(15, neon_colors[(self.palette_cycle_index + 3) % 4])

class Game:
    def __init__(self):
        pygame.init()
        self.width, self.height = 320, 200
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("1950's Zombie Quest")
        
        # Set VGA palette
        self.screen.set_palette(VGA_PALETTE)
        
        # Create rooms
        self.rooms = self.create_rooms()
        self.current_room = "street_vga"
        
        # Create hero
        self.hero = Hero(160, 150)
        
        # Create message bar
        self.message_bar = MessageBar(self.width, 20)
        
        # Game state
        self.clock = pygame.time.Clock()
        self.running = True
        
    def create_rooms(self):
        rooms = {}
        
        # Street room
        street_hotspots = [
            Hotspot(260, 120, 40, 60, "goto_diner", "door"),
            Hotspot(100, 140, 32, 40, "poke_trash", "trashcan")
        ]
        rooms["street_vga"] = Room("street_vga", VGA_PALETTE[8], 
                                 pygame.Rect(20, 100, 280, 80), street_hotspots, True)
        
        # Diner room
        diner_hotspots = [
            Hotspot(20, 140, 40, 60, "goto_street", "exit")
        ]
        rooms["diner_vga"] = Room("diner_vga", VGA_PALETTE[1], 
                                pygame.Rect(20, 100, 280, 80), diner_hotspots, True)
        
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
                self.execute_hotspot_action(hotspot.action)
                break
                
    def execute_hotspot_action(self, action):
        if action == "goto_diner":
            self.current_room = "diner_vga"
            self.hero.x = 280
            self.hero.y = 150
            self.hero.set_target(self.hero.x, self.hero.y)
        elif action == "goto_street":
            self.current_room = "street_vga"
            self.hero.x = 20
            self.hero.y = 150
            self.hero.set_target(self.hero.x, self.hero.y)
        elif action == "poke_trash":
            self.message_bar.show_message("You poke around. Gross!")
            
    def update(self):
        room = self.rooms[self.current_room]
        self.hero.update(room.walkbox)
        self.message_bar.update()
        room.update_palette_cycle(self.screen)
        
    def draw(self):
        room = self.rooms[self.current_room]
        
        # Draw background
        background = room.generate_background(self.width, self.height)
        self.screen.blit(background, (0, 0))
        
        # Generate priority mask
        priority_mask = room.generate_priority_mask(self.width, self.height)
        
        # Draw hero
        self.hero.draw(self.screen, priority_mask)
        
        # Draw message bar
        self.message_bar.draw(self.screen)
        
        pygame.display.flip()
        
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