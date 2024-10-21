import re
import asyncio
import pygame
from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent, GiftEvent, LikeEvent, JoinEvent, FollowEvent
from datetime import datetime
import emoji

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("TikTok Live Interaction Display")
font = pygame.font.Font("C:\\Users\\----\\OneDrive\\Desktop\\Projects\\TikTokLive-master oct24\\TikTokLive-master\\Game\\Fonts\\NotoColorEmoji.ttf", 36)

# Connect to the TikTok live
client = TikTokLiveClient(unique_id="migo.238")

# Define regex for different character types
ALPHABETS_REGEX = re.compile(r'[a-zA-ZÀ-ſ؀-ۿЀ-ӿ]+')
DIGITS_REGEX = re.compile(r'\d+')
SPECIAL_CHARACTERS_REGEX = re.compile(r'[!@#$%^&*(),.?":{}|<>_]')

# Helper function to classify username characters
def classify_username_characters(username):
    try:
        alphabets = len(ALPHABETS_REGEX.findall(username))
        digits = len(DIGITS_REGEX.findall(username))
        emojis = sum(1 for char in username if emoji.is_emoji(char))
        special_characters = len(SPECIAL_CHARACTERS_REGEX.findall(username))
    except Exception as e:
        print(f"Error classifying username characters: {e}")
        alphabets, digits, emojis, special_characters = 0, 0, 0, 0

    return {
        "alphabets": alphabets,
        "digits": digits,
        "emojis": emojis,
        "special_characters": special_characters
    }

# Helper function to get current datetime
def current_datetime():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Function to display text on Pygame screen
def display_text(text, y_offset):
    if not text.strip():
        return  # Skip rendering if the text is empty
    screen.fill((0, 0, 0))  # Clear screen
    try:
        text_surface = font.render(text, True, (255, 255, 255))
        if text_surface.get_width() > 0:  # Ensure the text_surface has a valid width
            screen.blit(text_surface, (20, y_offset))
            pygame.display.flip()
    except pygame.error as e:
        print(f"Pygame rendering error: {e}")

# Event handler for comments
@client.on(CommentEvent)
async def on_comment(event: CommentEvent):
    username = event.user.unique_id
    if not username.strip() or not event.comment.strip():
        return  # Skip if username or comment is empty
    character_types = classify_username_characters(username)
    output = f"[COMMENT] {current_datetime()} - {username}: {event.comment}\nUsername Character Types: {character_types}"
    print(output)
    display_text(output, 50)

# Event handler for gifts
@client.on(GiftEvent)
async def on_gift(event: GiftEvent):
    username = event.user.unique_id
    if not username.strip():
        return  # Skip if username is empty
    character_types = classify_username_characters(username)
    gift_name = getattr(event.gift, 'describe', 'Unknown Gift')
    diamonds = getattr(event.gift, 'repeat_count', 0) * getattr(event.gift, 'diamond_count', 0)
    output = f"[GIFT] {current_datetime()} - {username} sent {gift_name} worth {diamonds} diamonds\nUsername Character Types: {character_types}"
    print(output)
    display_text(output, 100)

# Event handler for joining the stream
@client.on(JoinEvent)
async def on_join(event: JoinEvent):
    username = event.user.unique_id
    if not username.strip():
        return  # Skip if username is empty
    character_types = classify_username_characters(username)
    output = f"[JOIN] {current_datetime()} - {username} joined the stream\nUsername Character Types: {character_types}"
    print(output)
    display_text(output, 150)

# Event handler for likes
@client.on(LikeEvent)
async def on_like(event: LikeEvent):
    username = event.user.unique_id
    if not username.strip():
        return  # Skip if username is empty
    character_types = classify_username_characters(username)
    output = f"[LIKE] {current_datetime()} - {username} liked the stream.\nUsername Character Types: {character_types}"
    print(output)
    display_text(output, 200)

# Event handler for follows
@client.on(FollowEvent)
async def on_follow(event: FollowEvent):
    username = event.user.unique_id
    if not username.strip():
        return  # Skip if username is empty
    character_types = classify_username_characters(username)
    output = f"[FOLLOW] {current_datetime()} - {username} followed\nUsername Character Types: {character_types}"
    print(output)
    display_text(output, 250)

# Error handling for connection
async def run_client():
    while True:
        try:
            print("Attempting to connect to TikTok Live...")
            await client.start()
        except Exception as e:
            print(f"Connection error: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(run_client())
    except KeyboardInterrupt:
        print("Game interrupted by user.")
    finally:
        pygame.quit()