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

    def get_phrase(self, event_type, name, count):
        # Get the list of possible phrases for the event type from JSON data
        possible_phrases = self.phrases.get(event_type, [])
        if not possible_phrases:
            return None

        # Avoid repeating the last used phrase for the event type
        last_phrase = self.last_phrases.get(event_type)
        possible_phrases = [p.format(name=name, count=count) for p in possible_phrases if p != last_phrase]

        # Choose a new phrase and store it as the last used one
        new_phrase = random.choice(possible_phrases)
        self.last_phrases[event_type] = new_phrase

        return new_phrase

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
            bubble_font = self.get_available_font('Comic Sans MS', 48, bold=True)
            max_width = 500

            # Extract username and rest of the text using regex
            match = re.match(r'^(.*?):\s*(.*)$', self.speech_bubble)
            if match:
                username, rest_of_text = match.groups()
            else:
                username = ""
                rest_of_text = self.speech_bubble

            # Wrap the rest of the speech bubble text
            wrapped_lines = self.wrap_text(rest_of_text, bubble_font, max_width)

            # Calculate the total height of the wrapped text
            line_height = bubble_font.get_linesize()
            bubble_height = len(wrapped_lines) * line_height + line_height  # Extra height for the username
            bubble_width = max([bubble_font.size(line)[0] for line in wrapped_lines] + [bubble_font.size(username)[0]]) + 40  # Add padding

            # Position the bubble above or around the boss, ensuring no overlap with previous bubbles
            bubble_rect = pygame.Rect(0, 0, bubble_width, bubble_height + 40)  # Include padding for the bubble background
            bubble_rect.center = (self.boss_rect.centerx, self.boss_rect.top - (bubble_height // 2) - 60)

            # Make sure the bubble doesn't go off-screen
            bubble_rect.clamp_ip(pygame.display.get_surface().get_rect())

            screen = pygame.display.get_surface()  # Get current display surface

            # Draw the speech bubble background (rounded rectangle with a tail)
            bubble_surf = pygame.Surface((bubble_rect.width, bubble_rect.height), pygame.SRCALPHA)
            bubble_surf.fill((255, 255, 255, min(255, self.speech_timer * 4)))  # Adjust alpha based on speech_timer
            pygame.draw.rect(bubble_surf, (255, 255, 255), bubble_surf.get_rect(), border_radius=15)  # Draw rounded rectangle
            screen.blit(bubble_surf, bubble_rect.topleft)

            # Draw the tail of the speech bubble
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

    def wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            width, _ = font.size(' '.join(current_line))
            if width > max_width:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def render_outlined_text(self, text, font, text_color, outline_color):
        base = font.render(text, True, outline_color)
        outline = pygame.Surface((base.get_width() + 4, base.get_height() + 4), pygame.SRCALPHA)

        # Draw outline
        positions = [(2, 0), (0, 2), (4, 2), (2, 4), (0, 0), (4, 0), (0, 4), (4, 4)]
        for pos in positions:
            outline.blit(base, pos)

        # Draw the main text in the center of the outline
        text_surface = font.render(text, True, text_color)
        outline.blit(text_surface, (2, 2))

        return outline

    def get_available_font(self, font_name, size, bold=False):
        # Create a unique key for the requested font
        font_key = (font_name, size, bold)
        if font_key in self.font_cache:
            return self.font_cache[font_key]

        # Try to load the requested font
        try:
            font = pygame.font.SysFont(font_name, size, bold=bold)
            test_surface = font.render("Test", True, (0, 0, 0))  # Test if font can render properly
            self.font_cache[font_key] = font
            return font
        except Exception as e:
            print(f"Error loading font '{font_name}': {e}")

        # If the requested font fails, fall back to Arial Unicode MS or similar
        fallback_fonts = ["Arial Unicode MS", "DejaVu Sans", "Noto Sans", "Arial"]
        for fallback_font in fallback_fonts:
            try:
                font = pygame.font.SysFont(fallback_font, size, bold=bold)
                test_surface = font.render("Test", True, (0, 0, 0))  # Test if font can render properly
                self.font_cache[font_key] = font
                print(f"Fallback to font: {fallback_font}")
                return font
            except Exception as e:
                print(f"Error loading fallback font '{fallback_font}': {e}")

        # As a last resort, use the default system font
        print("Using default system font.")
        font = pygame.font.Font(None, size)
        self.font_cache[font_key] = font
        return font
