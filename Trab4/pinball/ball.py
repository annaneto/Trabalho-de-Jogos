import math
import pygame


class Ball:
    RADIUS = 10
    GRAVITY = 900.0        
    MAX_SPEED = 1400.0
    COLOR = (240, 220, 90)

    def __init__(self, pos):
        self.pos = [float(pos[0]), float(pos[1])]
        self.vel = [0.0, 0.0]
        self.radius = self.RADIUS
        self.launched = False
        self.trail = []

    def reset(self, pos):
        self.pos = [float(pos[0]), float(pos[1])]
        self.vel = [0.0, 0.0]
        self.launched = False
        self.trail.clear()

    def apply_gravity(self, dt):
        if self.launched:
            self.vel[1] += self.GRAVITY * dt

    def clamp_speed(self):
        speed = math.hypot(self.vel[0], self.vel[1])
        if speed > self.MAX_SPEED:
            scale = self.MAX_SPEED / speed
            self.vel[0] *= scale
            self.vel[1] *= scale

    def integrate(self, dt):
        self.pos[0] += self.vel[0] * dt
        self.pos[1] += self.vel[1] * dt

    def speed(self):
        return math.hypot(self.vel[0], self.vel[1])

    def update_trail(self):
        self.trail.append(tuple(self.pos))
        if len(self.trail) > 10:
            self.trail.pop(0)

    def draw(self, screen):
        for i, p in enumerate(self.trail):
            alpha_radius = max(2, int(self.radius * (i + 1) / len(self.trail)))
            pygame.draw.circle(
                screen, (110, 100, 40), (int(p[0]), int(p[1])), alpha_radius
            )

        pygame.draw.circle(
            screen, self.COLOR, (int(self.pos[0]), int(self.pos[1])), self.radius
        )
        pygame.draw.circle(
            screen, (120, 110, 30),
            (int(self.pos[0]), int(self.pos[1])), self.radius, 1
        )
