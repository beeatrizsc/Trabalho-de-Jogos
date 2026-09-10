import pygame
from util import EventHandler

class Bullet:
    def __init__(self, pos, target_pos, color, damage=1, apply_slow=False):
        self.pos = pygame.Vector2(pos)
        self.target_pos = pygame.Vector2(target_pos)
        self.color = color
        self.damage = damage
        self.apply_slow = apply_slow
        self.radius = 5
        self.speed = 10
        
        dir_vec = self.target_pos - self.pos
        if dir_vec.length() > 0:
            self.vel = dir_vec.normalize() * self.speed
        else:
            self.vel = pygame.Vector2(0, 0)

    def update(self, dt):
        self.pos += self.vel
        if self.pos.x < 0 or self.pos.x > 1100 or self.pos.y < 0 or self.pos.y > 800:
            self.destroy()

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)

    def destroy(self):
        EventHandler().notify("DestroyObj", self)
