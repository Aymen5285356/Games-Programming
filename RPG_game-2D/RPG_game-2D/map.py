import pygame
from settings import TILE_SIZE, GREEN, BLACK

class Map:
    def __init__(self):
        self.tiles = [
            "11111111111111111111",
            "10000000000000000001",
            "10000000000000000001",
            "10000000000000000001",
            "10000000000000000001",
            "10000000000000000001",
            "10000000000000000001",
            "10000000000000000001",
            "10000000000000000001",
            "10000000000000000001",
            "10000000000000000001",
            "11111111111111111111",
        ]
        self.walls = []
        self.create_walls()

    def create_walls(self):
        self.walls = []
        for row_index, row in enumerate(self.tiles):
            for col_index, tile in enumerate(row):
                if tile == "1":
                    wall = pygame.Rect(
                        col_index * TILE_SIZE,
                        row_index * TILE_SIZE,
                        TILE_SIZE,
                        TILE_SIZE
                    )
                    self.walls.append(wall)

    def draw(self, screen):
        for row_index, row in enumerate(self.tiles):
            for col_index, tile in enumerate(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE
                if tile == "1":
                    pygame.draw.rect(screen, GREEN, (x, y, TILE_SIZE, TILE_SIZE))
                    pygame.draw.rect(screen, BLACK, (x, y, TILE_SIZE, TILE_SIZE), 2)
                else:
                    pygame.draw.rect(screen, (40, 40, 40), (x, y, TILE_SIZE, TILE_SIZE))