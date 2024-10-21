import pygame
import json
import os

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Creature Frame Tester")

# Frame rate
FPS = 10  # Adjust FPS if animations are too fast or too slow
clock = pygame.time.Clock()

# Path to the sprite sheet and JSON file
SPRITE_SHEET_PATH = "Creature.png"  # Replace with your sprite sheet file name
JSON_FILE_PATH = "C:/Users/----/OneDrive/Desktop/Projects/TikTokLive-master oct24/TikTokLive-master/Game/GameScripts/Boss_Config.json"
print(f"Looking for JSON file at: {os.path.abspath(JSON_FILE_PATH)}")  # Print the absolute path


# Load the sprite sheet
sprite_sheet = pygame.image.load(SPRITE_SHEET_PATH).convert_alpha()

# Load the JSON animation mapping
with open(JSON_FILE_PATH, 'r') as f:
    animation_data = json.load(f)

# Get the dimensions of each frame
frame_width = sprite_sheet.get_width() // animation_data["Creature"]["columns"]
frame_height = sprite_sheet.get_height() // animation_data["Creature"]["rows"]

# Scale factor
SCALE_FACTOR = animation_data["Creature"]["scale_factor"]

# Load the font to display row numbers
pygame.font.init()
font = pygame.font.SysFont('Arial', 24)

def get_frame(row, col, mirror=False):
    """Extract a frame from the sprite sheet based on row and column."""
    frame = sprite_sheet.subsurface(pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height))
    frame = pygame.transform.scale(frame, (int(frame_width * SCALE_FACTOR), int(frame_height * SCALE_FACTOR)))
    
    # Mirror the frame if the mirror flag is True
    if mirror:
        frame = pygame.transform.flip(frame, True, False)
    
    return frame

def play_action(action_name):
    """Play the frames for the given action and show the row number."""
    action = animation_data["Creature"]["action_mapping"][action_name]
    row = action["row"]
    mirror = action.get("mirror", False)  # Check if mirroring is needed
    
    # Get the start and end frame for the action
    start_frame = action["start_frame"]
    end_frame = action["end_frame"]
    
    # Loop through the frames for the action
    for col in range(start_frame, end_frame + 1):
        frame = get_frame(row, col, mirror)
        # Clear the screen
        screen.fill((0, 0, 0))
        
        # Draw the frame in the center of the screen
        frame_rect = frame.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(frame, frame_rect)
        
        # Display the row number at the top of the screen
        row_text = font.render(f"Row: {row}, Frames: {start_frame} - {end_frame}, Mirrored: {mirror}", True, (255, 255, 255))
        screen.blit(row_text, (10, 10))
        
        # Update the display
        pygame.display.flip()
        
        # Control the frame rate
        clock.tick(FPS)

# Main loop
running = True
current_action = "thrust_attack_bite"  # Start with this action

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                current_action = "thrust_attack_bite"
            elif event.key == pygame.K_2:
                current_action = "run_right"
            elif event.key == pygame.K_3:
                current_action = "run_left"  # Mirrored run left
            elif event.key == pygame.K_4:
                current_action = "spear_thrust_attack"
            elif event.key == pygame.K_5:
                current_action = "idle"
            elif event.key == pygame.K_6:
                current_action = "overhead_attack"
            elif event.key == pygame.K_7:
                current_action = "spear_block"
            elif event.key == pygame.K_8:
                current_action = "attack_with_crouch_idle"
            elif event.key == pygame.K_9:
                current_action = "hit_to_overhead_attack"
            elif event.key == pygame.K_v:
                current_action = "victory_taunt"
            elif event.key == pygame.K_j:
                current_action = "jump_backward"
            elif event.key == pygame.K_l:
                current_action = "jump_left"  # Mirrored jump left
            elif event.key == pygame.K_d:
                current_action = "death"
    
    # Play the current action
    play_action(current_action)

# Quit Pygame
pygame.quit()
