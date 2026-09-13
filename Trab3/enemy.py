import pygame
from abc import ABC,abstractmethod
from util import colored_sprite,EventHandler

class Enemy:
    def __init__(self,pos,player):
        self.pos=pygame.Vector2(pos); self.player=player; self.radius=16; self.speed=85; self.hp=2
        self.state=ApproachingState(self)
    def update(self,dt):self.state.update(dt)
    def draw(self,screen):self.state.draw(screen)
    def take_damage(self):self.state.take_damage()
    def change_state(self,new_state):self.state.delete();self.state=new_state(self)
    def destroy(self):EventHandler().notify("EnemyKilled",self);EventHandler().notify("DestroyObj",self)

class EnemyState(ABC):
    def __init__(self,enemy):self.E=enemy
    def draw(self,screen):screen.blit(self.sprite,(int(self.E.pos.x-self.E.radius),int(self.E.pos.y-self.E.radius)))
    def delete(self):pass
    def take_damage(self):pass
    @abstractmethod
    def update(self,dt):pass

class ApproachingState(EnemyState):
    sprite=colored_sprite((220,70,70),(32,32))
    def update(self,dt):
        d=self.E.player.pos-self.E.pos
        if d.length_squared():self.E.pos+=d.normalize()*self.E.speed*dt
        if self.E.pos.distance_to(self.E.player.pos)<=self.E.radius+self.E.player.radius:
            self.E.player.damage();self.E.change_state(AttackingState)
    def take_damage(self):
        self.E.hp-=1
        if self.E.hp<=0:self.E.destroy()
        else:self.E.change_state(StunnedState)

class AttackingState(EnemyState):
    sprite=colored_sprite((180,40,40),(36,36))
    def __init__(self,enemy):super().__init__(enemy);self.elapsed=0
    def update(self,dt):
        self.elapsed+=dt
        if self.elapsed>=.5:self.E.change_state(ApproachingState)
    def take_damage(self):
        self.E.hp-=1
        if self.E.hp<=0:self.E.destroy()
        else:self.E.change_state(StunnedState)

class StunnedState(EnemyState):
    sprite=colored_sprite((80,160,255),(32,32))
    def __init__(self,enemy):super().__init__(enemy);self.elapsed=0
    def update(self,dt):
        self.elapsed+=dt
        if self.elapsed>=.7:self.E.change_state(ApproachingState)
    def take_damage(self):
        self.E.hp-=1
        if self.E.hp<=0:self.E.destroy()
