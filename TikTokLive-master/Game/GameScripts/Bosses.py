# Bosses.py
import pygame
import os
import random
from Game.GameScripts.SpeechManager import SpeechManager
speech_manager = SpeechManager()

# Explosion Class
class Explosion(pygame.sprite.Sprite):
    def __init__(self, images, position):
        super().__init__()
        self.images = images
        self.current_frame = 0
        self.image = self.images[self.current_frame]
        self.rect = self.image.get_rect(center=position)
        self.frame_rate = 5  # Number of frames per image
        self.frame_counter = 0

    def update(self):
        # Update frame counter to control animation speed
        self.frame_counter += 1
        if self.frame_counter >= self.frame_rate:
            self.frame_counter = 0
            self.current_frame += 1

            # If we've reached the end of the animation, kill the sprite
            if self.current_frame >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.current_frame]


class Boss(pygame.sprite.Sprite):
    current_background = None

    def __init__(self, name, sprite_frames, screen_width, screen_height, notification_queue, all_boss_sprites, config, all_sprites):
        super().__init__()
        self.name = name
        self.frames = sprite_frames
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=(screen_width // 2, screen_height // 3))  # Adjusted for portrait mode
        self.health = 100
        self.base_health = 100
        self.level = 1
        self.reaction_timer = 0  # Timer to manage reaction duration
        self.idle_timer = 0  # Timer to manage idle behavior
        self.current_expression = "smile"  # Track current expression
        self.frame_update_interval = 10  # Number of frames between animation updates (increase to slow down animation)
        self.frame_counter = 0  # Counter to keep track of frame updates
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.notification_queue = notification_queue
        self.all_boss_sprites = all_boss_sprites
        self.config = config  # Store boss-specific configuration
        self.all_sprites = all_sprites  # Reference to all sprites group
        self.speech_timer = 0

        # Use configuration to initialize boss properties
        if 'health' in self.config:
            self.health = self.config['health']
            self.base_health = self.config['health']
        
        # Load actions from the config
        self.action_mapping = self.config.get("action_mapping", {})

    def change_background(self):
        backgrounds_dir = os.path.join(os.getcwd(), 'Game', 'Bosses', 'Backgrounds')
        if not os.path.exists(backgrounds_dir):
            raise FileNotFoundError(f"Critical Error: The background folder '{backgrounds_dir}' does not exist. Please ensure it is present.")

        background_files = [f for f in os.listdir(backgrounds_dir) if f.endswith(('.jpg', '.png'))]
        if background_files:
            if hasattr(self, 'used_backgrounds') and len(self.used_backgrounds) == len(background_files):
                self.used_backgrounds = []  # Reset if all backgrounds have been used
            available_backgrounds = [f for f in background_files if f not in getattr(self, 'used_backgrounds', [])]
            new_background_path = os.path.join(backgrounds_dir, random.choice(available_backgrounds))
            self.used_backgrounds = getattr(self, 'used_backgrounds', [])
            self.used_backgrounds.append(new_background_path)
            try:
                self.current_background = pygame.transform.scale(pygame.image.load(new_background_path).convert_alpha(), (self.screen_width, self.screen_height))
            except pygame.error as e:
                print(f"Error loading background {new_background_path}: {e}")
                self.current_background = None

    # Updated `spawn_explosion` method in the Boss class

    def spawn_explosion(self, scale_factor=400):  # Scale factor increased to make the explosion 2x bigger
        # Load the explosion folder using a direct path to avoid relative path issues
        base_project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        explosion_base_dir = os.path.join(base_project_dir, 'Game', 'Bosses', 'Explosions')

        # Get the list of explosion folders
        explosion_folders = [f for f in os.listdir(explosion_base_dir) if os.path.isdir(os.path.join(explosion_base_dir, f))]
        
        if not explosion_folders:
            print(f"Error: No explosion folders found in '{explosion_base_dir}'.")
            return

        current_folder = random.choice(explosion_folders)
        images = self.load_images_from_folder(os.path.join(explosion_base_dir, current_folder), scale_factor=scale_factor)

        # Create an explosion sprite at the boss's current position and add it to all_sprites
        explosion = Explosion(images, self.rect.center)
        explosion.frame_rate = 1  # Increase frame rate to play sooner
        self.all_sprites.add(explosion)

    # Updated `load_images_from_folder` method in the Boss class

    def load_images_from_folder(self, folder, scale_factor=400):  # Scale factor increased to match explosion size
        image_files = sorted([f for f in os.listdir(folder) if f.endswith('.png')], key=lambda x: int(x.split('.')[0]))
        images = []
        for img in image_files:
            try:
                loaded_image = pygame.image.load(os.path.join(folder, img)).convert_alpha()
                scaled_image = pygame.transform.scale(loaded_image, (loaded_image.get_width() * scale_factor // 100, loaded_image.get_height() * scale_factor // 100))  # Correct scaling calculation
                images.append(scaled_image)
            except pygame.error as e:
                print(f"Failed to load image {img}: {e}")
        if not images:
            print(f"No images loaded from folder: {folder}")
        return images

    # Updated `hurt` method in the Boss class

    def hurt(self):
        self.health -= 10
        self.set_expression("surprised")
        self.reaction_timer = 20  # Set reaction timer for 20 frames
        self.idle_timer = 0  # Reset idle timer when hurt
        if self.health <= 0:
            if not hasattr(self, 'exploded') or not self.exploded:
                self.spawn_explosion()  # Trigger explosion only when health is 0, with a larger scale
                self.exploded = True  # Ensure explosion only happens once
                self.reset_health()
        else:
            self.reaction_timer = 20  # Reset reaction timer to show surprise before frowning

        # Reset exploded attribute when boss is fully healed
        if self.health == self.base_health:
            self.exploded = False
            # Reset exploded attribute when boss is fully healed
            if self.health == self.base_health:
                self.exploded = False
                # Reset exploded attribute when boss is fully healed
                if self.health == self.base_health:
                    self.exploded = False

    def reset_health(self):
        self.base_health += 50  # Increase health for next round
        self.health = self.base_health
        self.level += 1
        self.set_expression("smile")
        self.spawn_new_boss()

    def spawn_new_boss(self):
        # Ensure the next boss is different
        remaining_boss_sprites = [frames for frames in self.all_boss_sprites if frames != self.frames]
        if not remaining_boss_sprites:
            remaining_boss_sprites = self.all_boss_sprites  # If all have been used, reset the list
        new_frames = random.choice(remaining_boss_sprites)
        self.frames = new_frames
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=(self.screen_width // 2, self.screen_height // 3))  # Adjusted for portrait mode
        # Create poof effect
        poof = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.circle(poof, (200, 200, 200, 128), (50, 50), 50)
        self.notification_queue.append("Poof! A new boss has appeared!")
        # Change background when new boss spawns
        self.change_background()

    def react_to_gift(self, diamond_count, gifter_name):
        self.set_expression("gift")
        self.reaction_timer = 30  # Set reaction timer for 30 frames
        # Get the speech from the sayings.json using the SpeechManager
        speech = speech_manager.get_phrase("gift", gifter_name, diamond_count)
        if speech:
            self.set_speech_bubble(speech, self.rect, duration=100 + (diamond_count * 2))

    def react_to_comment(self, commenter_name):
        self.set_expression("antagonizing")
        self.reaction_timer = 30  # Set reaction timer for 30 frames
        # Get the speech from the sayings.json using the SpeechManager
        speech = speech_manager.get_phrase("comment", commenter_name, None)
        if speech:
            self.set_speech_bubble(speech, self.rect, duration=100)

    def react_to_subscription(self, subscriber_name):
        self.set_expression("smile")
        self.reaction_timer = 50  # Set reaction timer for 50 frames to extend the happy expression
        # Get the speech from the sayings.json using the SpeechManager
        speech = speech_manager.get_phrase("subscription", subscriber_name, None)
        if speech:
            self.set_speech_bubble(speech, self.rect, duration=150)

    def set_speech_bubble(self, speech, rect, duration):
        speech_manager.set_speech_bubble(speech, rect, duration=duration)
        self.idle_timer = 0

    def set_expression(self, expression):
        expression_mapping = {
            "smile": 0,
            "surprised": 1,
            "frown": 2,
            "gift": 3,
            "antagonizing": 4
        }
        self.current_frame = expression_mapping.get(expression, 0)
        self.image = self.frames[self.current_frame]
        self.current_expression = expression

    def update(self):
        # Handle reaction timer
        if self.reaction_timer > 0:
            self.reaction_timer -= 1
            if self.reaction_timer == 0:
                if self.current_expression == "surprised":
                    self.set_expression("frown")
                    self.reaction_timer = 15  # Show frown for a short time
                else:
                    self.set_expression("smile")
        else:
            # Handle idle timer
            self.idle_timer += 1
            if self.idle_timer > 300:  # If idle for too long (e.g., 300 frames)
                self.set_expression("antagonizing")
                
        # Draw speech bubble using SpeechManager
        speech_manager.draw_speech_bubble()

        # Update animation frame at a slower rate
        self.frame_counter += 1
        if self.frame_counter >= self.frame_update_interval:
            self.frame_counter = 0  # Reset the frame counter
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]