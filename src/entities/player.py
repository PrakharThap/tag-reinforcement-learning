import math
import pygame

from config import PLAYER_SPEED, PLAYER_RADIUS, COLOR_TAGGER, COLOR_RUNNER


class Player:
    def __init__(self, x: float, y: float, is_tagger: bool = False):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.is_tagger = is_tagger
        self.radius = PLAYER_RADIUS
        self.invincible_timer: float = 0.0

    @property
    def color(self):
        return COLOR_TAGGER if self.is_tagger else COLOR_RUNNER

    def set_velocity(self, dx: float, dy: float):
        length = math.sqrt(dx * dx + dy * dy)
        if length > 0:
            dx /= length
            dy /= length
        self.vel.x = dx * PLAYER_SPEED
        self.vel.y = dy * PLAYER_SPEED

    def update(self, dt: float, tilemap):
        px, py = self.pos.x, self.pos.y

        self.pos.x += self.vel.x * dt
        if self._collides_with_wall(tilemap):
            self.pos.x = px

        self.pos.y += self.vel.y * dt
        if self._collides_with_wall(tilemap):
            self.pos.y = py

        if self.invincible_timer > 0:
            self.invincible_timer -= dt

    def _collides_with_wall(self, tilemap) -> bool:
        r = self.radius
        cx, cy = self.pos.x, self.pos.y
        checks = [
            (cx - r, cy - r),
            (cx + r, cy - r),
            (cx - r, cy + r),
            (cx + r, cy + r),
            (cx, cy),
        ]
        for x, y in checks:
            if tilemap.is_wall(x, y):
                return True
        return False

    def set_invincible(self, duration: float):
        self.invincible_timer = duration

    @property
    def is_invincible(self) -> bool:
        return self.invincible_timer > 0

    def render(self, surface: pygame.Surface, camera_x: float, camera_y: float):
        sx = self.pos.x - camera_x
        sy = self.pos.y - camera_y

        pygame.draw.circle(surface, self.color, (int(sx), int(sy)), self.radius)
        pygame.draw.circle(surface, (0, 0, 0), (int(sx), int(sy)), self.radius, 2)

        if self.vel.length() > 0:
            normalized = self.vel.normalize()
            ex = sx + normalized.x * self.radius * 1.8
            ey = sy + normalized.y * self.radius * 1.8
            pygame.draw.line(surface, (255, 255, 255), (sx, sy), (ex, ey), 3)

        if self.invincible_timer > 0:
            flash = int(128 + 127 * math.sin(self.invincible_timer * 30))
            ring_color = (flash, flash, flash)
            pygame.draw.circle(surface, ring_color, (int(sx), int(sy)), self.radius + 4, 2)
