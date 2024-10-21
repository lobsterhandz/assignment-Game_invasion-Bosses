# GameScripts/ball.py
import pygame
import random

class Ball(pygame.sprite.Sprite):
    def __init__(self, start_pos, direction, user, ball_type="default", diamond_count=1, screen_width=1080, screen_height=1920):
        super().__init__()
        size = 20 + diamond_count * 2
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)

        if ball_type == "like":
            color = (0, 255, 0)
        elif ball_type == "comment":
            color = (0, 0, 255)
        elif ball_type == "gift":
            color = (255, 223, 0)
        else:
            color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))

        pygame.draw.circle(self.image, color, (size // 2, size // 2), size // 2)
        glow_radius = size // 4
        for i in range(glow_radius, 0, -1):
            pygame.draw.circle(self.image, (color[0], color[1], color[2], int(255 * (i / glow_radius))), (size // 2, size // 2), (size // 2) + i)

        self.rect = self.image.get_rect(center=start_pos)
        self.direction = direction
        self.user = user
        self.target_x, self.target_y = screen_width // 2, screen_height // 3
        self.speed = 5
        self.damage = diamond_count * 10

    def update(self, boss, notification_queue):
        dx = self.target_x - self.rect.x
        dy = self.target_y - self.rect.y
        dist = max(1, (dx ** 2 + dy ** 2) ** 0.5)
        self.rect.x += int(self.speed * dx / dist)
        self.rect.y += int(self.speed * dy / dist)

        boss_center_rect = boss.rect.inflate(-boss.rect.width * 0.5, -boss.rect.height * 0.5)
        if self.rect.colliderect(boss_center_rect):
            boss.hurt()
            self.kill()
            notification_queue.append((f"-{self.damage} HP", boss.rect.center))