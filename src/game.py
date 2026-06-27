import random
import pygame

from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    COLOR_BACKGROUND,
    COLOR_HUD,
    COLOR_INDICATOR,
    COLOR_MENU_BG,
    COLOR_MENU_TEXT,
    COLOR_MENU_TITLE,
    TAG_DISTANCE,
    INVINCIBILITY_TIME,
    ROUND_TIME,
)
from map.tilemap import TileMap
from entities.player import Player
from input import InputHandler
from camera import Camera


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("RL Tag")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "menu"

        self.map_index = 0
        self.map_names = ["map_01.json", "map_02.json", "map_03.json"]
        self.tilemap = TileMap(self.map_names[self.map_index])

        spawn1 = self.tilemap.get_random_floor_pos()
        spawn2 = self.tilemap.get_random_floor_pos()
        while spawn1 == spawn2:
            spawn2 = self.tilemap.get_random_floor_pos()

        self.players = [
            Player(spawn1[0], spawn1[1], is_tagger=True),
            Player(spawn2[0], spawn2[1], is_tagger=False),
        ]

        self.camera = Camera(
            self.tilemap.get_pixel_width(), self.tilemap.get_pixel_height()
        )

        self.tagger_score = 0
        self.runner_score = 0
        self.round_timer = ROUND_TIME

        self.font_large = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 28)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self._handle_events()
            self._update(dt)
            self._render()
            pygame.display.flip()
        pygame.quit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if self.state == "menu":
                    if event.key == pygame.K_SPACE:
                        self._start_round()
                elif self.state == "round_end":
                    if event.key == pygame.K_SPACE:
                        self._next_map()
                        self._start_round()

    def _start_round(self):
        self.state = "playing"
        self.round_timer = ROUND_TIME
        self._spawn_players()

    def _spawn_players(self):
        spawn1 = self.tilemap.get_random_floor_pos()
        spawn2 = self.tilemap.get_random_floor_pos()
        while spawn1 == spawn2:
            spawn2 = self.tilemap.get_random_floor_pos()

        tagger = next(p for p in self.players if p.is_tagger)
        runner = next(p for p in self.players if not p.is_tagger)

        # Randomize who starts as tagger each round
        if random.random() < 0.5:
            tagger, runner = runner, tagger

        tagger.is_tagger = True
        runner.is_tagger = False
        tagger.pos.update(spawn1)
        runner.pos.update(spawn2)
        tagger.vel.update(0, 0)
        runner.vel.update(0, 0)
        tagger.set_invincible(INVINCIBILITY_TIME)
        runner.set_invincible(INVINCIBILITY_TIME)

    def _next_map(self):
        self.map_index = (self.map_index + 1) % len(self.map_names)
        self.tilemap = TileMap(self.map_names[self.map_index])
        self.camera = Camera(
            self.tilemap.get_pixel_width(), self.tilemap.get_pixel_height()
        )
        self._spawn_players()

    def _update(self, dt: float):
        if self.state != "playing":
            return

        keys = pygame.key.get_pressed()
        dx1, dy1 = InputHandler.get_p1_action(keys)
        dx2, dy2 = InputHandler.get_p2_action(keys)
        self.players[0].set_velocity(dx1, dy1)
        self.players[1].set_velocity(dx2, dy2)

        for player in self.players:
            player.update(dt, self.tilemap)

        self._check_tag(dt)

        cx = (self.players[0].pos.x + self.players[1].pos.x) / 2
        cy = (self.players[0].pos.y + self.players[1].pos.y) / 2
        self.camera.update(cx, cy)

    def _check_tag(self, dt: float):
        tagger = next(p for p in self.players if p.is_tagger)
        runner = next(p for p in self.players if not p.is_tagger)

        if not runner.is_invincible:
            dist = tagger.pos.distance_to(runner.pos)
            if dist < TAG_DISTANCE:
                tagger.is_tagger = False
                runner.is_tagger = True
                runner.set_invincible(INVINCIBILITY_TIME)

                self.tagger_score += 1

        self.round_timer -= dt
        if self.round_timer <= 0:
            self.runner_score += 1
            self.state = "round_end"

    def _render(self):
        self.screen.fill(COLOR_BACKGROUND)

        if self.state == "menu":
            self._render_menu()
            return

        self.tilemap.render(self.screen, self.camera.x, self.camera.y)
        sorted_players = sorted(self.players, key=lambda p: p.pos.y)
        for player in sorted_players:
            player.render(self.screen, self.camera.x, self.camera.y)

        self._render_hud()

        if self.state == "round_end":
            self._render_round_end()

    def _render_hud(self):
        score_surf = self.font_small.render(
            f"Tagger: {self.tagger_score}  Runner: {self.runner_score}", True, COLOR_HUD
        )
        self.screen.blit(score_surf, (10, 10))

        timer_surf = self.font_small.render(
            f"Time: {max(0, int(self.round_timer))}", True, COLOR_HUD
        )
        tw = timer_surf.get_width()
        self.screen.blit(timer_surf, (SCREEN_WIDTH // 2 - tw // 2, 10))

        role_surf = self.font_small.render(
            f"P1: {'TAGGER' if self.players[0].is_tagger else 'RUNNER'}   |   P2: {'TAGGER' if self.players[1].is_tagger else 'RUNNER'}",
            True,
            COLOR_INDICATOR,
        )
        rw = role_surf.get_width()
        self.screen.blit(role_surf, (SCREEN_WIDTH // 2 - rw // 2, SCREEN_HEIGHT - 30))

        map_surf = self.font_small.render(
            f"Map: {self.map_names[self.map_index]}", True, COLOR_HUD
        )
        self.screen.blit(map_surf, (10, SCREEN_HEIGHT - 30))

    def _render_menu(self):
        self.screen.fill(COLOR_MENU_BG)

        title = self.font_large.render("RL TAG", True, COLOR_MENU_TITLE)
        tw = title.get_width()
        self.screen.blit(title, (SCREEN_WIDTH // 2 - tw // 2, SCREEN_HEIGHT // 2 - 80))

        prompt = self.font_small.render("Press SPACE to start", True, COLOR_MENU_TEXT)
        pw = prompt.get_width()
        self.screen.blit(prompt, (SCREEN_WIDTH // 2 - pw // 2, SCREEN_HEIGHT // 2 - 20))

        controls = [
            "P1: WASD   P2: Arrow Keys",
            "Press SPACE to start/next round",
            "Press ESC to quit",
        ]
        y = SCREEN_HEIGHT // 2 + 30
        for line in controls:
            surf = self.font_small.render(line, True, COLOR_MENU_TEXT)
            sw = surf.get_width()
            self.screen.blit(surf, (SCREEN_WIDTH // 2 - sw // 2, y))
            y += 30

    def _render_round_end(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        if self.round_timer <= 0:
            msg = "Time's up! Runner scores!"
        else:
            msg = "Tag! Tagger scores!"

        text = self.font_large.render(msg, True, COLOR_MENU_TITLE)
        tw = text.get_width()
        self.screen.blit(text, (SCREEN_WIDTH // 2 - tw // 2, SCREEN_HEIGHT // 2 - 40))

        prompt = self.font_small.render(
            "Press SPACE for next round", True, COLOR_MENU_TEXT
        )
        pw = prompt.get_width()
        self.screen.blit(prompt, (SCREEN_WIDTH // 2 - pw // 2, SCREEN_HEIGHT // 2 + 10))
