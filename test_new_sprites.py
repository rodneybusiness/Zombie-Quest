#!/usr/bin/env python3
"""Test script to visualize the new 24x48 pixel character sprites."""

import pygame
import sys

# Add the zombie_quest module to path
sys.path.insert(0, '/home/user/Zombie-Quest')

from zombie_quest.sprites import (
    create_maya_sprite,
    create_johnny_chrome_sprite,
    create_promoter_sprite,
    create_clerk_sprite,
    create_dj_rotten_sprite
)


def main():
    pygame.init()

    # Create window to display all sprites
    window_width = 800
    window_height = 600
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Zombie Quest - New Character Sprites")

    # Background
    bg_color = (30, 20, 50)

    # Character data
    characters = [
        {
            'name': 'MAYA - The Lost Bandmate',
            'func': create_maya_sprite,
            'pos': (100, 100),
            'desc': 'Half-transformed zombie bassist with purple/green transformation'
        },
        {
            'name': 'JOHNNY CHROME - The Friendly Zombie',
            'func': create_johnny_chrome_sprite,
            'pos': (300, 100),
            'desc': 'Lucid zombie in vintage 1950s suit with dignity'
        },
        {
            'name': 'THE PROMOTER - The Villain',
            'func': create_promoter_sprite,
            'pos': (500, 100),
            'desc': 'Sleazy 80s exec with occult power (red/black)'
        },
        {
            'name': 'RECORD STORE CLERK',
            'func': create_clerk_sprite,
            'pos': (200, 350),
            'desc': 'Music nerd with flannel, glasses, and impeccable taste'
        },
        {
            'name': 'DJ ROTTEN',
            'func': create_dj_rotten_sprite,
            'pos': (500, 350),
            'desc': 'Punk DJ with mohawk, headphones, and attitude'
        }
    ]

    # Font for labels
    font = pygame.font.Font(None, 20)
    title_font = pygame.font.Font(None, 32)

    current_frame = 0
    clock = pygame.time.Clock()
    frame_timer = 0
    frame_delay = 500  # ms between frames

    running = True
    while running:
        dt = clock.tick(60)
        frame_timer += dt

        # Animate frames
        if frame_timer >= frame_delay:
            frame_timer = 0
            current_frame = (current_frame + 1) % 4

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Advance frame manually
                    current_frame = (current_frame + 1) % 4

        # Clear screen
        screen.fill(bg_color)

        # Title
        title = title_font.render("NEW CORE CHARACTER SPRITES (24x48)", True, (255, 200, 100))
        screen.blit(title, (window_width // 2 - title.get_width() // 2, 20))

        # Frame indicator
        frame_text = font.render(f"Frame: {current_frame + 1}/4 (SPACE to advance, ESC to quit)", True, (200, 200, 220))
        screen.blit(frame_text, (window_width // 2 - frame_text.get_width() // 2, 55))

        # Draw each character
        for char in characters:
            # Generate sprite for current frame
            sprite = char['func'](current_frame)

            # Scale up 2x for better visibility
            scaled = pygame.transform.scale(sprite, (48, 96))

            # Draw sprite
            pos = char['pos']
            screen.blit(scaled, (pos[0] - 24, pos[1] - 96))

            # Draw name
            name_text = font.render(char['name'], True, (255, 255, 100))
            screen.blit(name_text, (pos[0] - name_text.get_width() // 2, pos[1] + 10))

            # Draw description (wrapped)
            desc_words = char['desc'].split()
            line = ""
            y_offset = 30
            for word in desc_words:
                test_line = line + word + " "
                if font.size(test_line)[0] > 180:
                    desc_text = font.render(line, True, (180, 180, 200))
                    screen.blit(desc_text, (pos[0] - desc_text.get_width() // 2, pos[1] + y_offset))
                    line = word + " "
                    y_offset += 18
                else:
                    line = test_line
            if line:
                desc_text = font.render(line, True, (180, 180, 200))
                screen.blit(desc_text, (pos[0] - desc_text.get_width() // 2, pos[1] + y_offset))

            # Draw border around character area
            pygame.draw.rect(screen, (100, 80, 120),
                           (pos[0] - 60, pos[1] - 110, 120, 180), 2)

        # Animation frame labels
        frame_labels = ["1: Idle/Standing", "2: Walking/Gesturing", "3: Action", "4: Special"]
        label_y = 550
        label = font.render(f"Current: {frame_labels[current_frame]}", True, (255, 200, 150))
        screen.blit(label, (window_width // 2 - label.get_width() // 2, label_y))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
