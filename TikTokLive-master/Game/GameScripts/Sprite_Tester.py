# sprite_tester.py
import pygame
import os
from Game.GameScripts.Sprite_Loader import load_all_bosses


# Initialize Pygame
pygame.init()

# Screen setup
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Sprite Tester")
clock = pygame.time.Clock()

# Load all Boss Animations
boss_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Bosses"))
all_bosses_animations = load_all_bosses(boss_directory)

# Initialize first boss as current boss
boss_names = list(all_bosses_animations.keys())
current_boss_index = 0
current_boss_name = boss_names[current_boss_index]
current_boss_frames = all_bosses_animations[current_boss_name]

current_action = "idle"
current_frame = 0
frame_interval = 10  # Number of frames to wait before updating
frame_counter = 0

# Main loop
running = True
while running:
    screen.fill((0, 0, 0))  # Fill screen with black

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                current_action = "idle"
            elif event.key == pygame.K_2:
                current_action = "attack"
            elif event.key == pygame.K_3:
                current_action = "hurt"
            elif event.key == pygame.K_4:
                current_action = "die"
            elif event.key == pygame.K_5:
                current_action = "taunt"
            elif event.key == pygame.K_6:
                current_action = "special"
            elif event.key == pygame.K_RIGHT:
                # Switch to the next boss
                current_boss_index = (current_boss_index + 1) % len(boss_names)
                current_boss_name = boss_names[current_boss_index]
                current_boss_frames = all_bosses_animations[current_boss_name]
                current_frame = 0
                print(f"Switched to boss: {current_boss_name}")
            elif event.key == pygame.K_LEFT:
                # Switch to the previous boss
                current_boss_index = (current_boss_index - 1) % len(boss_names)
                current_boss_name = boss_names[current_boss_index]
                current_boss_frames = all_bosses_animations[current_boss_name]
                current_frame = 0
                print(f"Switched to boss: {current_boss_name}")

    # Update frame
    frame_counter += 1
    if frame_counter >= frame_interval:
        frame_counter = 0
        current_frame = (current_frame + 1) % len(current_boss_frames[current_action])

    # Draw the current frame of the boss
    current_image = current_boss_frames[current_action][current_frame]
    screen.blit(current_image, (screen_width // 2 - current_image.get_width() // 2, screen_height // 2 - current_image.get_height() // 2))

    # Update the display
    pygame.display.flip()
    clock.tick(60)  # Cap the frame rate at 60 FPS

# Quit Pygame
pygame.quit()