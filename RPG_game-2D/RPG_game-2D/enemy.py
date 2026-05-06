import pygame
import math
from settings import ENEMY_SPEED, RED, GREEN

class Enemy:
    def __init__(self, x=400, y=300):
        self.image = pygame.Surface((32, 32))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hp = 50
        self.max_hp = 50
        self.attack_damage = 5

    def update(self, player, walls):
        dx = player.rect.x - self.rect.x
        dy = player.rect.y - self.rect.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance > 0:
            dx = dx / distance
            dy = dy / distance

            new_x = self.rect.x + dx * ENEMY_SPEED
            new_y = self.rect.y + dy * ENEMY_SPEED

            temp_rect = self.rect.copy()
            temp_rect.x = new_x
            if not self.check_collision(temp_rect, walls):
                self.rect.x = new_x

            temp_rect = self.rect.copy()
            temp_rect.y = new_y
            if not self.check_collision(temp_rect, walls):
                self.rect.y = new_y

    def check_collision(self, rect, walls):
        for wall in walls:
            if rect.colliderect(wall):
                return True
        return False

    def draw(self, screen):
        screen.blit(self.image, self.rect)