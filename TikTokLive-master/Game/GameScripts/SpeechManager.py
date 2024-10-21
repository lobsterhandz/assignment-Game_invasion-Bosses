import random
import pygame
import json
import os
import re

class SpeechManager:
    def __init__(self):
        self.speech_bubble = None
        self.speech_timer = 0
        self.boss_rect = None
        self.last_phrases = {
            "gift": None,
            "comment": None,
            "subscription": None
        }
        self.highlight_colors = {}  # Store highlight colors for each speech bubble
        self.load_phrases_from_json()
        self.font_cache = {}  # Cache fonts for reuse

    def load_phrases_from_json(self):
        # Load phrases from a JSON file in the same directory as this script
        json_path = os.path.join(os.path.dirname(__file__), 'sayings.json')
        try:
            with open(json_path, 'r') as file:
                self.phrases = json.load(file)
        except FileNotFoundError:
            print(f"Error: The sayings JSON file '{json_path}' was not found.")
            self.phrases = {
                "gift": [],
                "comment": [],
                "subscription": []
            }
        except json.JSONDecodeError:
            print(f"Error: The sayings JSON file '{json_path}' is not valid JSON.")
            self.phrases = {
                "gift": [],
                "comment": [],
                "subscription": []
            }

    def set_speech_bubble(self, speech, rect, duration=100):
        # Set the speech bubble with the given text
        self.speech_bubble = speech
        self.speech_timer = duration
        self.boss_rect = rect

        # Split the speech by the first occurrence of ":" to get the username and rest of the speech
        if ":" in speech:
            username, _ = speech.split(":", 1)
        else:
            username = speech

        # Generate a random color for the entire username if not already stored
        if username not in self.highlight_colors:
            random_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            self.highlight_colors[username] = random_color

    def draw_speech_bubble(self):
        if self.speech_timer > 0 and self.speech_bubble and self.boss_rect:
            # Get screen width and height dynamically
            screen = pygame.display.get_surface()
            screen_width, screen_height = screen.get_size()

            # Set the max bubble width as a percentage of the screen width
            max_width = int(screen_width * 0.7)  # Bubble width is now 70% of screen width

            # Retrieve the font and extract the username and rest of the text
            bubble_font = self.get_available_font('Comic Sans MS', 48, bold=True)
            match = re.match(r'^(.*?):\s*(.*)$', self.speech_bubble)
            if match:
                username, rest_of_text = match.groups()
            else:
                username = ""
                rest_of_text = self.speech_bubble

            # Wrap the rest of the speech bubble text
            wrapped_lines = self.wrap_text(rest_of_text, bubble_font, max_width)

            # Calculate the total height and width of the bubble
            line_height = bubble_font.get_linesize()
            bubble_height = len(wrapped_lines) * line_height + line_height  # Extra height for the username
            bubble_width = min(max([bubble_font.size(line)[0] for line in wrapped_lines] + [bubble_font.size(username)[0]]) + 40, max_width)  # Add padding and ensure it does not exceed max_width

            # Position the bubble above or around the boss
            bubble_rect = pygame.Rect(0, 0, bubble_width, bubble_height + 40)  # Include padding for bubble background
            bubble_rect.center = (self.boss_rect.centerx, self.boss_rect.top - (bubble_height // 2) - 60)

            # Adjust the bubble position to make sure it doesn't go off-screen
            if bubble_rect.left < 0:
                bubble_rect.left = 10  # Padding from the left edge
            if bubble_rect.right > screen_width:
                bubble_rect.right = screen_width - 10  # Padding from the right edge
            if bubble_rect.top < 0:
                bubble_rect.top = 10  # Padding from the top edge
            if bubble_rect.bottom > screen_height:
                bubble_rect.bottom = screen_height - 10  # Padding from the bottom edge

            # Draw the speech bubble background (rounded rectangle with a tail)
            bubble_surf = pygame.Surface((bubble_rect.width, bubble_rect.height), pygame.SRCALPHA)
            bubble_surf.fill((255, 255, 255, min(255, self.speech_timer * 4)))  # Adjust alpha based on speech_timer
            pygame.draw.rect(bubble_surf, (255, 255, 255), bubble_surf.get_rect(), border_radius=15)
            screen.blit(bubble_surf, bubble_rect.topleft)

            # Draw the tail of the speech bubble pointing towards the boss
            tail_points = [
                (self.boss_rect.centerx, self.boss_rect.top),  # Pointing to the character
                (bubble_rect.centerx - 20, bubble_rect.bottom),
                (bubble_rect.centerx + 20, bubble_rect.bottom)
            ]
            pygame.draw.polygon(screen, (255, 255, 255), tail_points)

            # Retrieve the color for the current username
            random_text_color = self.highlight_colors.get(username, (0, 0, 0))

            # Draw the username with the generated random color
            if username:
                username_surface = bubble_font.render(username, True, random_text_color)
                username_rect = username_surface.get_rect(midtop=(bubble_rect.centerx, bubble_rect.top + 20))
                screen.blit(username_surface, username_rect)
                text_y_offset = username_rect.bottom + 10  # Adjust for spacing below the username
            else:
                text_y_offset = bubble_rect.top + 20  # Default if no username

            # Draw each line of the rest of the text
            for i, line in enumerate(wrapped_lines):
                text_surface = bubble_font.render(line, True, (0, 0, 0))  # Normal black text
                text_rect = text_surface.get_rect(midtop=(bubble_rect.centerx, text_y_offset + i * line_height))
                screen.blit(text_surface, text_rect)

            self.speech_timer -= 1
