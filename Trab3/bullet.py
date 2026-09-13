import pygame
from abc import ABC,abstractmethod
from util import colored_sprite,EventHandler

class Bullet(ABC):
    def __init__(self,pos,direction,speed=650,life_time=1.5,radius=5):
        self.pos=pygame.Vector2(pos); self.direction=pygame.Vector2(direction).normalize()
        self.speed=speed; self.life_time=life_time; self.elapsed=0; self.radius=radius; self.destroyed=False
        self.sprite=colored_sprite((255,240,70),(radius*2,radius*2))
    def update(self,dt):
        if self.destroyed:return
        self.elapsed+=dt; self.pos+=self.direction*self.speed*dt
        if self.elapsed>=self.life_time or not (0<=self.pos.x<=800 and 0<=self.pos.y<=600):self.destroy()
    def draw(self,screen): screen.blit(self.sprite,(int(self.pos.x-self.radius),int(self.pos.y-self.radius)))
    def destroy(self):
        if not self.destroyed:self.destroyed=True; EventHandler().notify("DestroyObj",self)
    @abstractmethod
    def move(self):pass

class PlayerBullet(Bullet):
    def move(self):return self.direction*self.speed
