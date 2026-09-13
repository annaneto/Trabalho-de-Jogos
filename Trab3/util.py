import pygame

def singleton(class_):
    instances={}
    def getinstance(*args,**kwargs):
        if class_ not in instances: instances[class_]=class_(*args,**kwargs)
        return instances[class_]
    return getinstance

@singleton
class EventHandler:
    def __init__(self): self.observers={}
    def subscribe(self,event_type,callback):
        self.observers.setdefault(event_type,[]).append(callback)
    def notify(self,event_type,data=None):
        for callback in self.observers.get(event_type,[]): callback(data)

def colored_sprite(color,size=(32,32),circle=True):
    s=pygame.Surface(size,pygame.SRCALPHA)
    if circle: pygame.draw.circle(s,color,(size[0]//2,size[1]//2),min(size)//2)
    else: s.fill(color)
    return s

def circle_collision(p1,r1,p2,r2):
    return pygame.Vector2(p1).distance_to(pygame.Vector2(p2)) <= r1+r2

circle_collistiion=circle_collision
