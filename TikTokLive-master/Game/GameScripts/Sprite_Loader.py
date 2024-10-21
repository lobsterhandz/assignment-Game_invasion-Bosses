# SpriteLoader.py
import os
import pygame

def load_sprite_sheet(path, columns, rows):
    sprite_sheet = pygame.image.load(path).convert_alpha()
    sheet_width, sheet_height = sprite_sheet.get_size()
    frame_width = sheet_width // columns
    frame_height = sheet_height // rows
    frames = []
    for col in range(columns):
        for row in range(rows):
            frame = sprite_sheet.subsurface((col * frame_width, row * frame_height, frame_width, frame_height)).copy()
            # Scale the frame to 150% (50% larger)
            frame = pygame.transform.scale(frame, (int(frame_width * 3.0), int(frame_height * 3.0)))
            frames.append(frame)
    return frames

def load_boss_sprites(boss_dir=None):
    if boss_dir is None:
        boss_dir = os.path.join(os.getcwd(), "Game", "Bosses")
    
    if not os.path.exists(boss_dir):
        raise FileNotFoundError(f"The directory '{boss_dir}' does not exist. Please add a valid 'Bosses' folder.")

    boss_sprites = []
    for filename in os.listdir(boss_dir):
        if filename.endswith(".png"):
            frames = load_sprite_sheet(os.path.join(boss_dir, filename), 9, 6)
            if frames:  # Ensure frames were loaded correctly
                boss_sprites.append(frames)
    return boss_sprites