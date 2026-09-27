import math
from shape import Polygon


def regular_polygon(center, radius, sides, rotation_deg=0):
    """Gera os vertices de um poligono regular (usado nos bumpers e
    na zona de bonus)."""
    points = []
    rot = math.radians(rotation_deg)
    for i in range(sides):
        ang = rot + (2 * math.pi * i / sides)
        points.append((
            center[0] + radius * math.cos(ang),
            center[1] + radius * math.sin(ang),
        ))
    return points


class Wall:
    """Obstaculo estatico que so reflete a bola."""

    def __init__(self, points, color=(90, 90, 100)):
        self.polygon = Polygon(points)
        self.color = color

    def draw(self, screen):
        self.polygon.draw(screen, self.color)


class Bumper:
    """Hexagono que reflete a bola com bastante impulso (restituicao > 1,
    como um bumper de pinball de verdade) e tambem soma pontos -- ou
    seja, muda a trajetoria E aplica um efeito ao mesmo tempo."""

    POINTS_VALUE = 100
    RESTITUTION = 1.8

    def __init__(self, center, radius=26, color=(220, 70, 90)):
        self.center = center
        self.radius = radius
        self.color = color
        self.polygon = Polygon(regular_polygon(center, radius, 6))
        self.flash_timer = 0.0

    def hit(self):
        self.flash_timer = 0.15
        return self.POINTS_VALUE

    def update(self, dt):
        if self.flash_timer > 0:
            self.flash_timer = max(0.0, self.flash_timer - dt)

    def draw(self, screen):
        color = (255, 210, 90) if self.flash_timer > 0 else self.color
        self.polygon.draw(screen, color)


class BonusTrigger:
    """Zona de bonus que da pontos e aumenta a velocidade da bola"""

    POINTS_VALUE = 250
    SPEED_BOOST = 1.18
    COOLDOWN = 0.8

    def __init__(self, center, radius=42, color=(120, 220, 160)):
        self.center = center
        self.polygon = Polygon(regular_polygon(center, radius, 5, rotation_deg=-90))
        self.color = color
        self.cooldown_timer = 0.0
        self.flash_timer = 0.0

    def update(self, dt):
        if self.cooldown_timer > 0:
            self.cooldown_timer = max(0.0, self.cooldown_timer - dt)
        if self.flash_timer > 0:
            self.flash_timer = max(0.0, self.flash_timer - dt)

    def try_trigger(self, ball_pos):
        """True se o efeito deve disparar agora (com cooldown pra nao
        somar pontos em todo frame enquanto a bola estiver dentro)."""
        if self.cooldown_timer > 0:
            return False
        if self.polygon.point_inside(ball_pos):
            self.cooldown_timer = self.COOLDOWN
            self.flash_timer = 0.3
            return True
        return False

    def draw(self, screen):
        base = (60, 130, 95)
        color = (170, 255, 200) if self.flash_timer > 0 else base
        self.polygon.draw(screen, color, outline=(220, 255, 230), width=2)
