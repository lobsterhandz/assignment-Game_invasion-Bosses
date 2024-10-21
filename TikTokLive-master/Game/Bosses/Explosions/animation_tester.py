import pygame
import os
import random

# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((800, 600))  # Adjust the size to your preference
pygame.display.set_caption("Explosion Animation Test")

# Set up the clock for controlling frame rate
clock = pygame.time.Clock()

# Set up the font for displaying folder name
font = pygame.font.Font(None, 36)

# Function to load images from a folder
def load_images_from_folder(folder):
    image_files = sorted([f for f in os.listdir(folder) if f.endswith('.png')], key=lambda x: int(x.split('.')[0]))
    images = []
    for img in image_files:
        try:
            loaded_image = pygame.image.load(os.path.join(folder, img)).convert_alpha()
            scaled_image = pygame.transform.scale(loaded_image, (loaded_image.get_width() * 8, loaded_image.get_height() * 8))  # Increase size by scaling
            images.append(scaled_image)
        except pygame.error as e:
            print(f"Failed to load image {img}: {e}")
    if not images:
        print(f"No images loaded from folder: {folder}")
    return images

# Get list of explosion folders relative to the current script directory
current_dir = os.path.dirname(os.path.abspath(__file__))
explosion_folders = [f for f in os.listdir(current_dir) if os.path.isdir(os.path.join(current_dir, f))]
current_folder = random.choice(explosion_folders)
images = load_images_from_folder(os.path.join(current_dir, current_folder))

# Main loop
running = True
frame = 0
used_folders = [current_folder]
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Change to a new random explosion folder, not repeating the last one
                available_folders = [f for f in explosion_folders if f not in used_folders]
                if not available_folders:
                    used_folders = []
                    available_folders = explosion_folders
                current_folder = random.choice(available_folders)
                images = load_images_from_folder(os.path.join(current_dir, current_folder))
                used_folders.append(current_folder)
                frame = 0

    # Clear the screen
    screen.fill((0, 0, 0))

    # Display the current frame
    if images and frame < len(images):
        screen.blit(images[frame], (200, 150))  # Adjust the position to your preference
        frame += 1
    else:
        frame = 0  # Loop the animation for testing purposes

    # Render and display the folder name
    folder_text = font.render(f"Folder: {current_folder}", True, (255, 255, 255))
    screen.blit(folder_text, (10, 10))

    # Update the display
    pygame.display.flip()

    # Control the frame rate (e.g., 10 FPS)
    clock.tick(10)

# Quit Pygame
pygame.quit()