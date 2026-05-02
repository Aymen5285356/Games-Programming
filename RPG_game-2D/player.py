import pygame
from settings import PLAYER_SPEED, BLUE, YELLOW, RED, GREEN

class Player:
    def __init__(self, x=100, y=100):
        self.image = pygame.Surface((32, 32))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hp = 100
        self.max_hp = 100
        self.level = 1
        self.exp = 0
        self.attack_damage = 10

    def move(self, keys, walls):
        new_x = self.rect.x
        new_y = self.rect.y

        if keys[pygame.K_LEFT] or keys[pygame.K_q]:
            new_x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            new_x += PLAYER_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_z]:
            new_y -= PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            new_y += PLAYER_SPEED

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