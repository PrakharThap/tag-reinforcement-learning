from config import SCREEN_WIDTH, SCREEN_HEIGHT


class Camera:
    def __init__(self, map_width: float, map_height: float):
        self.x: float = 0.0
        self.y: float = 0.0
        self.map_width = map_width
        self.map_height = map_height

    def update(self, target_x: float, target_y: float):
        self.x = target_x - SCREEN_WIDTH / 2
        self.y = target_y - SCREEN_HEIGHT / 2
        self.x = max(0.0, min(self.x, self.map_width - SCREEN_WIDTH))
        self.y = max(0.0, min(self.y, self.map_height - SCREEN_HEIGHT))
