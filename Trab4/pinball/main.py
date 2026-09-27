
import math
import sys
import pygame

from shape import Polygon
from collision import Collide
from ball import Ball
from flipper import Flipper
from entities import Wall, Bumper, BonusTrigger, regular_polygon

WIDTH, HEIGHT = 500, 800
FIELD_LEFT, FIELD_RIGHT = 20, 430
LANE_LEFT, LANE_RIGHT = 450, 490

BG_COLOR = (18, 18, 24)
FIELD_COLOR = (28, 30, 40)

STATE_READY = "ready"
STATE_PLAYING = "playing"
STATE_GAMEOVER = "gameover"

MAX_CHARGE_TIME = 1.1
LAUNCH_MIN_SPEED = 550
LAUNCH_MAX_SPEED = 1250

SUBSTEPS = 4
RESTITUTION_WALL = 0.65
RESTITUTION_FLIPPER = 0.55
FLIPPER_KICK = 0.9


def build_table():
    walls = [
        # bordas
        Wall([(0, 120), (20, 120), (20, 760), (0, 760)]),                     # parede esquerda
        Wall([(FIELD_RIGHT, 120), (LANE_LEFT, 120),
              (LANE_LEFT, 760), (FIELD_RIGHT, 760)]),                         # separador campo/lançador
        Wall([(LANE_RIGHT, 20), (500, 20), (500, 780), (LANE_RIGHT, 780)]),   # parede externa do lançador
        Wall([(LANE_LEFT, 760), (500, 760), (500, 780), (LANE_LEFT, 780)]),   # piso do lançador
        Wall([(20, 20), (FIELD_RIGHT, 20), (FIELD_RIGHT, 40), (20, 40)]),     # topo do campo

        # canto (triangulo - regiao NAO retangular/circular);
        # o canto superior direito fica sem cunha de propósito, pois é
        # por ali que a bola entra vinda do lançador (ver defletor abaixo)
        Wall([(20, 40), (20, 95), (75, 40)]),

        # defletor que leva a bola lançada de volta ao campo (triangulo)
        Wall([(FIELD_RIGHT, 40), (500, 20), (500, 95)], color=(70, 70, 85)),

        # slingshots acima dos flippers (triangulos)
        Wall([(60, 660), (150, 660), (60, 585)], color=(120, 70, 130)),
        Wall([(FIELD_RIGHT - 60, 660), (FIELD_RIGHT - 150, 660), (FIELD_RIGHT - 60, 585)],
             color=(120, 70, 130)),
    ]

    bumpers = [
        Bumper((170, 230)),
        Bumper((280, 230)),
        Bumper((225, 150)),
    ]

    triggers = [
        BonusTrigger((225, 440), radius=42),
    ]

    flippers = [
        Flipper(pivot=(150, 715), rest_angle_deg=35, active_angle_deg=-42, facing=1),
        Flipper(pivot=(300, 715), rest_angle_deg=-35, active_angle_deg=42, facing=-1),
    ]

    return walls, bumpers, triggers, flippers


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pinball - Colisao Poligonal (SAT)")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 22)
        self.big_font = pygame.font.SysFont("consolas", 42, bold=True)

        self.walls, self.bumpers, self.triggers, self.flippers = build_table()
        self.left_flipper, self.right_flipper = self.flippers

        self.lane_rest_pos = (470, 745)
        self.ball = Ball(self.lane_rest_pos)

        self.score = 0
        self.lives = 3
        self.state = STATE_READY
        self.charge = 0.0
        self.charging = False

        self.collidables = self.walls + self.bumpers

        self.stuck_timer = 0.0
        self.stuck_ref_pos = None

    
    def reset_game(self):
        self.score = 0
        self.lives = 3
        self.state = STATE_READY
        self.ball.reset(self.lane_rest_pos)

    def new_ball(self):
        self.ball.reset(self.lane_rest_pos)
        self.state = STATE_READY


    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    self.left_flipper.set_active(True)
                if event.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_l):
                    self.right_flipper.set_active(True)
                if event.key == pygame.K_SPACE and self.state == STATE_READY:
                    self.charging = True
                if event.key == pygame.K_r:
                    self.reset_game()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)

            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    self.left_flipper.set_active(False)
                if event.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_l):
                    self.right_flipper.set_active(False)
                if event.key == pygame.K_SPACE and self.charging:
                    self.launch_ball()

    def launch_ball(self):
        self.charging = False
        power = self.charge / MAX_CHARGE_TIME
        power = max(0.0, min(1.0, power))
        speed = LAUNCH_MIN_SPEED + (LAUNCH_MAX_SPEED - LAUNCH_MIN_SPEED) * power
        self.ball.vel[0] = 0.0
        self.ball.vel[1] = -speed
        self.ball.launched = True
        self.state = STATE_PLAYING
        self.charge = 0.0
        self.stuck_timer = 0.0
        self.stuck_ref_pos = None


    def update(self, dt):
        for flipper in self.flippers:
            flipper.update(dt)
        for bumper in self.bumpers:
            bumper.update(dt)
        for trigger in self.triggers:
            trigger.update(dt)

        if self.state == STATE_READY and self.charging:
            self.charge = min(MAX_CHARGE_TIME, self.charge + dt)

        if self.state != STATE_PLAYING:
            return

        sub_dt = dt / SUBSTEPS
        for _ in range(SUBSTEPS):
            self.ball.apply_gravity(sub_dt)
            self.ball.clamp_speed()
            self.ball.integrate(sub_dt)
            self.resolve_collisions()

        self.ball.update_trail()

        # zonas de bonus: efeito sem alterar a trajetoria
        for trigger in self.triggers:
            if trigger.try_trigger(self.ball.pos):
                self.score += trigger.POINTS_VALUE
                speed = self.ball.speed()
                new_speed = min(Ball.MAX_SPEED, speed * trigger.SPEED_BOOST + 40)
                if speed > 1e-3:
                    scale = new_speed / speed
                    self.ball.vel[0] *= scale
                    self.ball.vel[1] *= scale

        # a bola escapou por baixo dos flippers, perde a vida
        if self.ball.pos[1] - self.ball.radius > HEIGHT:
            self.lose_ball()
            return

        self.check_stuck(dt)

    def check_stuck(self, dt):
        if self.stuck_ref_pos is None:
            self.stuck_ref_pos = tuple(self.ball.pos)
            self.stuck_timer = 0.0
            return

        moved = math.hypot(
            self.ball.pos[0] - self.stuck_ref_pos[0],
            self.ball.pos[1] - self.stuck_ref_pos[1],
        )

        if moved < 6:
            self.stuck_timer += dt
        else:
            self.stuck_timer = 0.0
            self.stuck_ref_pos = tuple(self.ball.pos)

        if self.stuck_timer >= 1.2:
            self.stuck_timer = 0.0
            self.stuck_ref_pos = None
            self.lose_ball()

    def resolve_collisions(self):
        # paredes e cantos (apenas reflete)
        for wall in self.walls:
            result = Collide.circle_polygon(self.ball.pos, self.ball.radius, wall.polygon)
            if result:
                self.apply_collision(result, RESTITUTION_WALL)

        # bumpers (reflete + soma pontos)
        for bumper in self.bumpers:
            result = Collide.circle_polygon(self.ball.pos, self.ball.radius, bumper.polygon)
            if result:
                self.apply_collision(result, Bumper.RESTITUTION)
                self.score += bumper.hit()

        # flippers (reflete + transfere parte da velocidade angular)
        for flipper in self.flippers:
            result = Collide.circle_polygon(self.ball.pos, self.ball.radius, flipper.polygon)
            if result:
                normal, depth = result
                self.push_out(normal, depth)
                self.ball.vel[0], self.ball.vel[1] = Collide.reflect(
                    self.ball.vel, normal, RESTITUTION_FLIPPER
                )
                tip_vx, tip_vy = flipper.tip_speed_at(self.ball.pos)
                self.ball.vel[0] += tip_vx * FLIPPER_KICK
                self.ball.vel[1] += tip_vy * FLIPPER_KICK
                self.ball.clamp_speed()

    def apply_collision(self, result, restitution):
        normal, depth = result
        self.push_out(normal, depth)
        self.ball.vel[0], self.ball.vel[1] = Collide.reflect(
            self.ball.vel, normal, restitution
        )

    def push_out(self, normal, depth):
        self.ball.pos[0] += normal[0] * depth
        self.ball.pos[1] += normal[1] * depth

    def lose_ball(self):
        self.lives -= 1
        if self.lives <= 0:
            self.state = STATE_GAMEOVER
        else:
            self.new_ball()

    def draw(self):
        self.screen.fill(BG_COLOR)
        pygame.draw.rect(self.screen, FIELD_COLOR, (0, 0, WIDTH, HEIGHT))

        for wall in self.walls:
            wall.draw(self.screen)
        for trigger in self.triggers:
            trigger.draw(self.screen)
        for bumper in self.bumpers:
            bumper.draw(self.screen)
        for flipper in self.flippers:
            flipper.draw(self.screen)

        if self.state in (STATE_READY, STATE_PLAYING):
            self.ball.draw(self.screen)

        self.draw_hud()

        if self.state == STATE_GAMEOVER:
            self.draw_center_text("FIM DE JOGO", "Pressione R para reiniciar")
        elif self.state == STATE_READY:
            self.draw_charge_meter()

        pygame.display.flip()

    def draw_hud(self):
        score_surf = self.font.render(f"Pontos: {self.score}", True, (230, 230, 230))
        self.screen.blit(score_surf, (14, 8))

        lives_surf = self.font.render(f"Bolas: {self.lives}", True, (230, 230, 230))
        self.screen.blit(lives_surf, (WIDTH - lives_surf.get_width() - 14, 8))

        if self.state == STATE_READY:
            hint = self.font.render("SEGURE ESPACO p/ carregar e SOLTE p/ lancar",
                                     True, (200, 200, 120))
            self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 30))

    def draw_charge_meter(self):
        if self.charge <= 0:
            return
        ratio = min(1.0, self.charge / MAX_CHARGE_TIME)
        bar_h = 120
        bar_w = 14
        x, y = LANE_LEFT + 8, 760 - int(bar_h * ratio)
        pygame.draw.rect(self.screen, (60, 60, 60), (x, 760 - bar_h, bar_w, bar_h), 1)
        pygame.draw.rect(self.screen, (250, 200, 60), (x, y, bar_w, int(bar_h * ratio)))

    def draw_center_text(self, title, subtitle):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        title_surf = self.big_font.render(title, True, (255, 90, 90))
        sub_surf = self.font.render(subtitle, True, (230, 230, 230))

        self.screen.blit(
            title_surf,
            (WIDTH // 2 - title_surf.get_width() // 2, HEIGHT // 2 - 40)
        )
        self.screen.blit(
            sub_surf,
            (WIDTH // 2 - sub_surf.get_width() // 2, HEIGHT // 2 + 20)
        )

   
    def run(self):
        while True:
            dt = self.clock.tick(60) / 1000.0
            dt = min(dt, 1 / 30)  # evita saltos grandes se a janela travar
            self.handle_events()
            self.update(dt)
            self.draw()


if __name__ == "__main__":
    Game().run()
