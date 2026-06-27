import json
import random
from pathlib import Path
import pygame

from config import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_FLOOR, COLOR_WALL, COLOR_WALL_BORDER, COLOR_GRID


class TileMap:
    def __init__(self, filename: str):
        self.tiles: list[list[int]] = []
        self.width: int = 0
        self.height: int = 0
        self.data_dir = Path(__file__).parent / "data"
        self.load(filename)

    def load(self, filename: str):
        path = self.data_dir / filename
        data = json.loads(path.read_text())
        self.width = data["width"]
        self.height = data["height"]
        self.tiles = data["tiles"]

    def is_wall(self, x: float, y: float) -> bool:
        col = int(x // TILE_SIZE)
        row = int(y // TILE_SIZE)
        if 0 <= row < self.height and 0 <= col < self.width:
            return self.tiles[row][col] == 1
        return True

    def is_wall_tile(self, row: int, col: int) -> bool:
        if 0 <= row < self.height and 0 <= col < self.width:
            return self.tiles[row][col] == 1
        return True

    def get_pixel_width(self) -> int:
        return self.width * TILE_SIZE

    def get_pixel_height(self) -> int:
        return self.height * TILE_SIZE

    def get_random_floor_pos(self) -> tuple[float, float]:
        while True:
            row = random.randint(1, self.height - 2)
            col = random.randint(1, self.width - 2)
            if self.tiles[row][col] == 0:
                cx = col * TILE_SIZE + TILE_SIZE // 2
                cy = row * TILE_SIZE + TILE_SIZE // 2
                return (cx, cy)

    def render(self, surface: pygame.Surface, camera_x: float, camera_y: float):
        start_col = max(0, int(camera_x // TILE_SIZE))
        start_row = max(0, int(camera_y // TILE_SIZE))
        end_col = min(self.width, int((camera_x + SCREEN_WIDTH) // TILE_SIZE) + 1)
        end_row = min(self.height, int((camera_y + SCREEN_HEIGHT) // TILE_SIZE) + 1)

        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                tile_type = self.tiles[row][col]
                sx = col * TILE_SIZE - camera_x
                sy = row * TILE_SIZE - camera_y
                rect = pygame.Rect(sx, sy, TILE_SIZE, TILE_SIZE)

                if tile_type == 0:
                    pygame.draw.rect(surface, COLOR_FLOOR, rect)
                    pygame.draw.rect(surface, COLOR_GRID, rect, 1)
                else:
                    pygame.draw.rect(surface, COLOR_WALL, rect)
                    pygame.draw.rect(surface, COLOR_WALL_BORDER, rect, 2)
