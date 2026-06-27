import pygame


class InputHandler:
    @staticmethod
    def get_p1_action(keys) -> tuple[float, float]:
        dx = dy = 0.0
        if keys[pygame.K_w]:
            dy -= 1.0
        if keys[pygame.K_s]:
            dy += 1.0
        if keys[pygame.K_a]:
            dx -= 1.0
        if keys[pygame.K_d]:
            dx += 1.0
        return dx, dy

    @staticmethod
    def get_p2_action(keys) -> tuple[float, float]:
        dx = dy = 0.0
        if keys[pygame.K_UP]:
            dy -= 1.0
        if keys[pygame.K_DOWN]:
            dy += 1.0
        if keys[pygame.K_LEFT]:
            dx -= 1.0
        if keys[pygame.K_RIGHT]:
            dx += 1.0
        return dx, dy
