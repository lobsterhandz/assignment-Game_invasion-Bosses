# main.py
import asyncio
import pygame
import random
from TikTokLive import TikTokLiveClient
from TikTokLive.events import LikeEvent, CommentEvent, GiftEvent, SubscribeEvent
from websockets.exceptions import ConnectionClosedError
from Game.GameScripts.Sprite_Loader import load_boss_sprites
import os
import json
from Game.GameScripts.Bosses import Boss
import time
from Game.GameScripts.SpeechManager import SpeechManager

speech_manager = SpeechManager()

# Then continue using it as necessary...

# Add timestamp to the notifications to track how long they should appear
notification_queue = []

# Initialize pygame
pygame.init()
screen_width, screen_height = 1080, 1920  # Set resolution to 1080x1920 for Portrait mode
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("TikTok Smiley Invaders")
font = pygame.font.SysFont(None, 36)  # Increase font size for better readability
fullscreen = False

# Leaderboard dictionaries
leaderboard = {}

# Load Boss configuration
config_path = os.path.join(os.getcwd(), "Game", "Bosses", "Boss_Config.json")
if not os.path.exists(config_path):
    raise FileNotFoundError(f"The configuration file '{config_path}' does not exist. Please ensure it is present.")

with open(config_path, 'r') as config_file:
    boss_config = json.load(config_file)

# Load all boss sprite sheets
boss_sprites = load_boss_sprites()

# Verify if we have any sprites loaded
if not boss_sprites:
    raise RuntimeError("No boss sprite sheets found in the 'Bosses' folder. Please add valid sprite sheets and try again.")

# List to hold notifications
notification_queue = []

# Initialize the boss and groups
all_sprites = pygame.sprite.Group()  # Define all_sprites before creating Boss instance
boss_name = "Creature"  # You can dynamically choose this or iterate through different bosses

if boss_name not in boss_config:
    raise ValueError(f"No configuration found for boss '{boss_name}'. Please ensure it is included in the configuration file.")

# Create the Boss instance
boss = Boss(
    boss_name,
    random.choice(boss_sprites),
    screen_width,
    screen_height,
    notification_queue,
    boss_sprites,
    config=boss_config[boss_name],
    all_sprites=all_sprites  # all_sprites is now properly defined
)

# Scale boss sprite
boss.image = pygame.transform.scale(boss.image, (int(boss.rect.width * 1.5), int(boss.rect.height * 1.5)))
boss.rect = boss.image.get_rect(center=(screen_width // 2, screen_height // 3))

# Add boss to the all_sprites group
all_sprites.add(boss)

# Initialize the balls group
balls = pygame.sprite.Group()

# TikTok Client Setup
username = input("Enter the TikTok username to connect to: ")
client = TikTokLiveClient(unique_id=username)

# Function to update leaderboard
def update_leaderboard(user, points):
    if user in leaderboard:
        leaderboard[user] += points
    else:
        leaderboard[user] = points
    sorted_leaderboard = sorted(leaderboard.items(), key=lambda item: item[1], reverse=True)
    return sorted_leaderboard[:5]

# Function to render leaderboard
def render_leaderboard():
    sorted_leaderboard = sorted(leaderboard.items(), key=lambda item: item[1], reverse=True)[:5]  # Sort without updating
    y_offset = 100  # Start Y position for rendering text
    title = font.render("Top Contributors", True, (255, 255, 255))
    screen.blit(title, (screen_width - 300, 40))  # Adjusted for portrait mode
    for index, (user, count) in enumerate(sorted_leaderboard):
        text = font.render(f"{index + 1}. {user}: {count}", True, (255, 255, 255))
        screen.blit(text, (screen_width - 300, y_offset))  # Adjusted for portrait mode
        y_offset += 40

# Function to render health bar
def render_health_bar():
    bar_width = 300  # Increased bar width for better visibility in portrait mode
    bar_height = 25  # Increased bar height
    health_ratio = boss.health / boss.base_health
    health_bar = pygame.Rect(boss.rect.centerx - bar_width // 2, boss.rect.bottom + 120, int(bar_width * health_ratio), bar_height)
    border_rect = pygame.Rect(boss.rect.centerx - bar_width // 2, boss.rect.bottom + 120, bar_width, bar_height)
    pygame.draw.rect(screen, (255, 0, 0), health_bar)
    pygame.draw.rect(screen, (255, 255, 255), border_rect, 2)
    health_text = font.render(f"{boss.health}/{boss.base_health}", True, (255, 255, 255))
    screen.blit(health_text, (boss.rect.centerx - health_text.get_width() // 2, boss.rect.bottom + 150))

# Function to render boss level
def render_boss_level():
    level_text = font.render(f"Level: {boss.level}", True, (255, 255, 255))
    screen.blit(level_text, (boss.rect.centerx - level_text.get_width() // 2, boss.rect.bottom + 80))

# Updated function to render damage notifications
def render_notifications():
    current_time = time.time()
    new_notifications = []

    for notification in notification_queue:
        if isinstance(notification, tuple):
            # Handle damage flash notification
            text, position, timestamp = notification
            # Display notification only for 1.5 seconds
            if current_time - timestamp < 1.5:
                notification_text = font.render(text, True, (255, 0, 0))  # Red text for damage
                # Move notification upwards by reducing the y-position over time
                new_y = position[1] - int((current_time - timestamp) * 80)  # Increased speed at which text moves up
                screen.blit(notification_text, (position[0], new_y))
                new_notifications.append((text, (position[0], new_y), timestamp))

    # Update the notification queue to remove expired damage notifications
    notification_queue[:] = new_notifications

# Ball sprite class
def spawn_ball(from_left, user, ball_type="default", diamond_count=1):
    class Ball(pygame.sprite.Sprite):
        def __init__(self, start_pos, direction, user, ball_type, diamond_count):
            super().__init__()
            size = 20 + diamond_count * 2  # Scale ball size based on diamond count
            self.image = pygame.Surface((size, size), pygame.SRCALPHA)

            if ball_type == "like":
                color = (0, 255, 0)  # Green for likes
            elif ball_type == "comment":
                color = (0, 0, 255)  # Blue for comments
            elif ball_type == "gift":
                color = (255, 223, 0)  # Gold for gifts
            else:
                color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))

            # Draw a glowing circle for the ball
            pygame.draw.circle(self.image, color, (size // 2, size // 2), size // 2, width=0)
            
            self.rect = self.image.get_rect(center=start_pos)
            self.direction = direction
            self.user = user
            self.target_x, self.target_y = screen_width // 2, screen_height // 3  # Adjusted target for portrait mode
            self.speed = 5
            self.damage = diamond_count * 10  # Set damage based on the diamond count

        def update(self):
            dx = self.target_x - self.rect.x
            dy = self.target_y - self.rect.y
            dist = max(1, (dx ** 2 + dy ** 2) ** 0.5)
            self.rect.x += int(self.speed * dx / dist)
            self.rect.y += int(self.speed * dy / dist)

            # Make balls target and collide precisely with the boss center
            boss_center_rect = boss.rect.inflate(-boss.rect.width * 0.5, -boss.rect.height * 0.5)
            if self.rect.colliderect(boss_center_rect):
                boss.hurt()
                self.kill()  # Remove the ball when it collides with the boss

                # Add a slight random offset to make the damage marker pop up in different positions around the hit point
                hit_position = (boss.rect.centerx + random.randint(-30, 30), boss.rect.centery + random.randint(-30, 30))
                notification_queue.append((f"-{self.damage} HP", hit_position, time.time()))

    if from_left:
        start_pos = (0, random.randint(0, screen_height))
        direction = (1, 0)
    else:
        start_pos = (screen_width, random.randint(0, screen_height))
        direction = (-1, 0)
    ball = Ball(start_pos, direction, user, ball_type, diamond_count=diamond_count)
    all_sprites.add(ball)
    balls.add(ball)

@client.on(LikeEvent)
async def on_like(event):
    update_leaderboard(event.user.unique_id, 1)
    spawn_ball(from_left=True, user=event.user.unique_id, ball_type="like")

@client.on(CommentEvent)
async def on_comment(event):
    update_leaderboard(event.user.unique_id, 2)
    spawn_ball(from_left=False, user=event.user.unique_id, ball_type="comment")
    boss.react_to_comment(f"{event.user.unique_id}: {event.comment}")  # Properly format with username and comment text

@client.on(GiftEvent)
async def on_gift(event):
    diamond_count = event.gift.diamond_count if hasattr(event.gift, 'diamond_count') else 10
    update_leaderboard(event.user.unique_id, diamond_count)
    spawn_ball(from_left=True, user=event.user.unique_id, ball_type="gift", diamond_count=diamond_count)
    boss.react_to_gift(diamond_count, f"{event.user.unique_id}: sent {diamond_count} diamonds")  # Include gift details

@client.on(SubscribeEvent)
async def on_follow(event):
    if event.user.is_subscribed:  # Assuming the event has a way to determine if it's a subscriber
        boss.react_to_subscription(f"{event.user.unique_id}")
    else:
        # Handle regular follows differently if desired
        pass

async def tiktok_listen():
    """Handles connecting to TikTok and reconnecting on failure."""
    while True:
        try:
            print("Attempting to connect to TikTok Live...")
            await client.start()
        except ConnectionClosedError as e:
            print(f"Connection closed unexpectedly: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)  # Wait before retrying to connect
        except Exception as e:
            print(f"An unexpected error occurred: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)

async def game_loop():
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                await client.stop()
                pygame.quit()
                return

        # Draw the background if available
        if boss.current_background:
            screen.blit(boss.current_background, (0, 0))
        else:
            screen.fill((0, 0, 0))  # Fallback to black if no background

        # Update all sprites
        all_sprites.update()

        # Draw everything else
        all_sprites.draw(screen)
        render_leaderboard()
        render_health_bar()
        render_boss_level()
        render_notifications()

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)
        await asyncio.sleep(0)  # Yield control to other coroutines

async def main():
    await asyncio.gather(tiktok_listen(), game_loop())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Game interrupted by user.")
