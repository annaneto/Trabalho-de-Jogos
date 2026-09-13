import random,pygame
from player import Player
from bullet import PlayerBullet
from enemy import Enemy
from util import EventHandler,circle_collision

pygame.init(); WIDTH,HEIGHT,FPS=800,600,60
screen=pygame.display.set_mode((WIDTH,HEIGHT));pygame.display.set_caption("Dino Survivor");clock=pygame.time.Clock()
font=pygame.font.Font(None,32);big_font=pygame.font.Font(None,64)
player=Player((WIDTH//2,HEIGHT//2));objects=[player];enemies=[];bullets=[]
score=0;spawn_timer=0;spawn_interval=1.3;running=True;game_over=False

def add_bullet(data):
    b=PlayerBullet(data["pos"],data["direction"]);bullets.append(b);objects.append(b)
def remove_obj(obj):
    if obj in objects:objects.remove(obj)
    if obj in enemies:enemies.remove(obj)
    if obj in bullets:bullets.remove(obj)
def enemy_killed(enemy):
    global score;score+=1
def player_damaged(player_obj):pass

events=EventHandler()
events.subscribe("CreateBullet",add_bullet);events.subscribe("DestroyObj",remove_obj)
events.subscribe("EnemyKilled",enemy_killed);events.subscribe("PlayerDamaged",player_damaged)

def spawn_enemy():
    side=random.randrange(4)
    if side==0:pos=(random.randrange(WIDTH),-30)
    elif side==1:pos=(WIDTH+30,random.randrange(HEIGHT))
    elif side==2:pos=(random.randrange(WIDTH),HEIGHT+30)
    else:pos=(-30,random.randrange(HEIGHT))
    e=Enemy(pos,player);enemies.append(e);objects.append(e)

def restart():
    global player,objects,enemies,bullets,score,spawn_timer,spawn_interval,game_over
    player=Player((WIDTH//2,HEIGHT//2));objects=[player];enemies=[];bullets=[]
    score=0;spawn_timer=0;spawn_interval=1.3;game_over=False

while running:
    dt=clock.tick(FPS)/1000
    for event in pygame.event.get():
        if event.type==pygame.QUIT:running=False
        elif event.type==pygame.KEYDOWN:
            if event.key==pygame.K_ESCAPE:running=False
            elif event.key==pygame.K_r and game_over:restart()
        elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1 and not game_over:
            player.action_1(event.pos)

    if not game_over:
        spawn_timer+=dt
        if spawn_timer>=spawn_interval:
            spawn_timer=0;spawn_enemy();spawn_interval=max(.35,1.3-score*.015)
        for obj in objects[:]:obj.update(dt)
        for b in bullets[:]:
            if b.destroyed:continue
            for e in enemies[:]:
                if circle_collision(b.pos,b.radius,e.pos,e.radius):
                    b.destroy();e.take_damage();break
        if player.hp<=0:game_over=True

    screen.fill((25,25,35));player.pos,pygame.mouse.get_pos()
    for obj in objects:obj.draw(screen)
    screen.blit(font.render(f"Vida: {player.hp}/{player.max_hp}",True,(240,240,240)),(15,15))
    screen.blit(font.render(f"Pontos: {score}",True,(240,240,240)),(15,45))
    if game_over:
        t=big_font.render("GAME OVER",True,(240,80,80));i=font.render("R: jogar novamente   ESC: sair",True,(240,240,240))
        screen.blit(t,(WIDTH//2-t.get_width()//2,HEIGHT//2-50));screen.blit(i,(WIDTH//2-i.get_width()//2,HEIGHT//2+20))
    pygame.display.flip()
pygame.quit()
