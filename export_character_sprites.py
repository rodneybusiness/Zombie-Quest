#!/usr/bin/env python3
"""Export character sprites as PNG files for visual verification."""

import pygame
import sys
import os

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

    # Create output directory
    output_dir = "/home/user/Zombie-Quest/character_sprites_export"
    os.makedirs(output_dir, exist_ok=True)

    characters = {
        'maya': create_maya_sprite,
        'johnny_chrome': create_johnny_chrome_sprite,
        'promoter': create_promoter_sprite,
        'clerk': create_clerk_sprite,
        'dj_rotten': create_dj_rotten_sprite
    }

    print("Generating character sprites...")
    print(f"Output directory: {output_dir}\n")

    for char_name, sprite_func in characters.items():
        print(f"Generating {char_name}...")

        # Generate all 4 frames
        for frame in range(4):
            sprite = sprite_func(frame)

            # Scale up 4x for better visibility in file
            scaled = pygame.transform.scale(sprite, (96, 192))

            # Save as PNG
            filename = f"{char_name}_frame_{frame}.png"
            filepath = os.path.join(output_dir, filename)
            pygame.image.save(scaled, filepath)
            print(f"  ✓ Saved: {filename}")

        # Create a sprite sheet with all 4 frames
        sheet_width = 96 * 4
        sheet_height = 192
        sheet = pygame.Surface((sheet_width, sheet_height), pygame.SRCALPHA)

        for frame in range(4):
            sprite = sprite_func(frame)
            scaled = pygame.transform.scale(sprite, (96, 192))
            sheet.blit(scaled, (frame * 96, 0))

        sheet_filename = f"{char_name}_spritesheet.png"
        sheet_filepath = os.path.join(output_dir, sheet_filename)
        pygame.image.save(sheet, sheet_filepath)
        print(f"  ✓ Saved: {sheet_filename} (all frames)\n")

    print(f"\n✅ All sprites exported successfully!")
    print(f"📁 Location: {output_dir}")
    print(f"📊 Total files: {len(characters) * 5} (4 frames + 1 sprite sheet per character)")

    # Create an info file
    info_path = os.path.join(output_dir, "README.txt")
    with open(info_path, 'w') as f:
        f.write("ZOMBIE QUEST - CHARACTER SPRITES\n")
        f.write("=" * 50 + "\n\n")
        f.write("This directory contains exported character sprites.\n\n")
        f.write("FILE NAMING:\n")
        f.write("  <character>_frame_<0-3>.png - Individual frames (96x192 pixels, 4x scale)\n")
        f.write("  <character>_spritesheet.png - All 4 frames in one image (384x192 pixels)\n\n")
        f.write("CHARACTERS:\n")
        f.write("  - maya: The Lost Bandmate (half-transformed zombie bassist)\n")
        f.write("  - johnny_chrome: The Friendly Zombie (1950s suit, philosophical)\n")
        f.write("  - promoter: The Villain (80s power suit, occult)\n")
        f.write("  - clerk: Record Store Clerk (flannel, glasses, music nerd)\n")
        f.write("  - dj_rotten: DJ Rotten (punk mohawk, headphones)\n\n")
        f.write("ANIMATION FRAMES:\n")
        f.write("  Frame 0: Idle/Standing\n")
        f.write("  Frame 1: Walking/Gesturing\n")
        f.write("  Frame 2: Action (playing instrument, talking, etc.)\n")
        f.write("  Frame 3: Special (transforming, unique pose, etc.)\n\n")
        f.write("ORIGINAL SIZE: 24x48 pixels\n")
        f.write("EXPORTED SIZE: 96x192 pixels (4x scale for visibility)\n\n")
        f.write("Generated: 2025-12-19\n")

    print(f"📄 Info file created: README.txt\n")

    pygame.quit()


if __name__ == "__main__":
    main()
