import math
from shape import Polygon


class Flipper:
   

    LENGTH = 95
    BASE_WIDTH = 24
    TIP_WIDTH = 10
    ANGULAR_SPEED = math.radians(720)

    def __init__(self, pivot, rest_angle_deg, active_angle_deg, facing=1):
      
        self.pivot = pivot
        self.rest_angle = math.radians(rest_angle_deg)
        self.active_angle = math.radians(active_angle_deg)
        self.angle = self.rest_angle
        self.active = False
        self.angular_velocity = 0.0

        half_base = self.BASE_WIDTH / 2
        half_tip = self.TIP_WIDTH / 2
        length = self.LENGTH * facing

        # pontos locais, relativos ao pivo, com angulo 0
        self.base_points = [
            (0, -half_base),
            (0, half_base),
            (length, half_tip),
            (length, -half_tip),
        ]

        self.polygon = Polygon(self._world_points(self.angle))

    def _world_points(self, angle):
        px, py = self.pivot
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        result = []
        for x, y in self.base_points:
            rx = x * cos_a - y * sin_a
            ry = x * sin_a + y * cos_a
            result.append((px + rx, py + ry))
        return result

    def set_active(self, active):
        self.active = active

    def update(self, dt):
        target = self.active_angle if self.active else self.rest_angle
        diff = target - self.angle
        step = self.ANGULAR_SPEED * dt

        prev_angle = self.angle
        if abs(diff) <= step:
            self.angle = target
        else:
            self.angle += step if diff > 0 else -step

        self.angular_velocity = (self.angle - prev_angle) / dt if dt > 0 else 0.0
        self.polygon.set_points(self._world_points(self.angle))

    def tip_speed_at(self, point):
    
        rx = point[0] - self.pivot[0]
        ry = point[1] - self.pivot[1]
        vx = -self.angular_velocity * ry
        vy = self.angular_velocity * rx
        return (vx, vy)

    def draw(self, screen):
        color = (130, 200, 255) if self.active else (90, 160, 230)
        self.polygon.draw(screen, color)
