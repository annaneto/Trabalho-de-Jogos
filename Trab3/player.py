import pygame
from abc import ABC,abstractmethod
from util import colored_sprite,EventHandler

class Player:
    def __init__(self,pos):
        self.pos=pygame.Vector2(pos); self.radius=18; self.speed=260
        self.hp=5; self.max_hp=5; self.state=NormalState(self); self.aim=pygame.Vector2(1,0)
    def update(self,dt): self.state.update(dt)
    def draw(self,screen): self.state.draw(screen)
    def action_1(self,target): self.state.action_1(target)
    def action_2(self): self.state.action_2()
    def change_state(self,new_state): self.state.delete(); self.state=new_state(self)
    def damage(self): self.state.take_damage()
    def shoot(self,target):
        d=pygame.Vector2(target)-self.pos
        if d.length_squared()==0:return
        self.aim=d.normalize()
        EventHandler().notify("CreateBullet",{"pos":self.pos+self.aim*22,"direction":self.aim})

class PlayerState(ABC):
    sprite=colored_sprite((60,220,100),(36,36))
    def __init__(self,player): self.P=player
    def draw(self,screen):
        screen.blit(self.sprite,(int(self.P.pos.x-self.sprite.get_width()/2),int(self.P.pos.y-self.sprite.get_height()/2)))
    def delete(self): pass
    def take_damage(self): pass
    @abstractmethod
    def update(self,dt): pass
    @abstractmethod
    def action_1(self,target): pass
    def action_2(self): pass

class NormalState(PlayerState):
    sprite=colored_sprite((70,220,100),(36,36))
    def update(self,dt):
        keys=pygame.key.get_pressed()
        d=pygame.Vector2(keys[pygame.K_d]-keys[pygame.K_a],keys[pygame.K_s]-keys[pygame.K_w])
        if d.length_squared(): self.P.pos+=d.normalize()*self.P.speed*dt
        self.P.pos.x=max(self.P.radius,min(800-self.P.radius,self.P.pos.x))
        self.P.pos.y=max(self.P.radius,min(600-self.P.radius,self.P.pos.y))
    def action_1(self,target): self.P.shoot(target)
    def take_damage(self):
        self.P.hp-=1; EventHandler().notify("PlayerDamaged",self.P)
        self.P.change_state(DeadState if self.P.hp<=0 else InvincibleState)

class InvincibleState(PlayerState):
    sprite=colored_sprite((255,235,70),(42,42))
    def __init__(self,player): super().__init__(player); self.elapsed=0; self.duration=1.5
    def update(self,dt):
        self.elapsed+=dt; keys=pygame.key.get_pressed()
        d=pygame.Vector2(keys[pygame.K_d]-keys[pygame.K_a],keys[pygame.K_s]-keys[pygame.K_w])
        if d.length_squared(): self.P.pos+=d.normalize()*self.P.speed*dt
        self.P.pos.x=max(self.P.radius,min(800-self.P.radius,self.P.pos.x)); self.P.pos.y=max(self.P.radius,min(600-self.P.radius,self.P.pos.y))
        if self.elapsed>=self.duration:self.P.change_state(NormalState)
    def action_1(self,target): self.P.shoot(target)

class DeadState(PlayerState):
    sprite=colored_sprite((100,100,100),(36,36))
    def update(self,dt): pass
    def action_1(self,target): pass
