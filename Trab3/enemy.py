import pygame
from abc import ABC, abstractmethod
from util import colored_sprite, EventHandler

WAYPOINTS = [
    (-64, 2*64 + 128),
    (0*64 + 96, 2*64 + 128),
    (3*64 + 96, 2*64 + 128),
    (3*64 + 96, 6*64 + 128),
    (11*64 + 96, 6*64 + 128),
    (11*64 + 96, 2*64 + 128),
    (14*64 + 96, 2*64 + 128)
]

class Enemy:
    def __init__(self, level=1, hp=5, speed=1.2, reward=10):
        self.pos = pygame.Vector2(WAYPOINTS[0])
        self.target_idx = 1
        self.level = level
        self.radius = 16 if level < 3 else 24
        self.max_hp = hp
        self.hp = hp
        self.base_speed = speed
        self.speed = speed
        self.reward = reward
        self.state = ApproachingState(self)

    def update(self, dt):
        self.state.update(dt)

    def draw(self, screen):
        if self.pos.x >= 32:
            self.state.draw(screen)

    def change_state(self, new_state_class):
        self.state = new_state_class(self)

    def take_damage(self, amount=1, apply_slow=False):
        self.hp -= amount
        if self.hp <= 0:
            EventHandler().notify("GoldEarned", self.reward)
            self.destroy()
        else:
            # Aplica lentidão exclusivamente se o ataque for de Terra
            if apply_slow and not isinstance(self.state, SlowedState):
                self.change_state(SlowedState)

    def destroy(self):
        EventHandler().notify("EnemyKilled", self)
        EventHandler().notify("DestroyObj", self)


class EnemyState(ABC):
    def __init__(self, enemy):
        self.E = enemy
        self.update_sprite()

    @abstractmethod
    def update_sprite(self):
        pass

    def draw(self, screen):
        offset = pygame.Vector2(self.sprite.get_width() // 2, self.sprite.get_height() // 2)
        screen.blit(self.sprite, self.E.pos - offset)

    @abstractmethod
    def update(self, dt):
        pass


class ApproachingState(EnemyState):
    def update_sprite(self):
        if self.E.level == 1:
            self.sprite = colored_sprite((70, 70, 80), (32, 32), shape="circle")
        elif self.E.level == 2:
            self.sprite = colored_sprite((40, 180, 80), (36, 36), shape="circle")
        else:
            self.sprite = colored_sprite((100, 20, 120), (52, 52), shape="circle")
            pygame.draw.circle(self.sprite, (220, 50, 50), (26, 26), 22, 3)

    def update(self, dt):
        target = pygame.Vector2(WAYPOINTS[self.E.target_idx])
        dir_vec = target - self.E.pos
        dist = dir_vec.length()

        if dist < self.E.speed:
            self.E.pos = target
            self.E.target_idx += 1
            if self.E.target_idx >= len(WAYPOINTS):
                damage = 3 if self.E.level == 3 else 1
                for _ in range(damage):
                    EventHandler().notify("BaseDamaged")
                self.E.destroy()
        else:
            if dir_vec.length() > 0:
                self.E.pos += dir_vec.normalize() * self.E.speed


class SlowedState(EnemyState):
    def update_sprite(self):
        if self.E.level == 1:
            self.sprite = colored_sprite((100, 120, 180), (32, 32), shape="circle")
        elif self.E.level == 2:
            self.sprite = colored_sprite((80, 200, 180), (36, 36), shape="circle")
        else:
            self.sprite = colored_sprite((140, 100, 200), (52, 52), shape="circle")

    def __init__(self, enemy):
        super().__init__(enemy)
        self.slow_timer = 50
        self.E.speed = self.E.base_speed * 0.5

    def update(self, dt):
        self.slow_timer -= dt
        
        target = pygame.Vector2(WAYPOINTS[self.E.target_idx])
        dir_vec = target - self.E.pos
        dist = dir_vec.length()

        if dist < self.E.speed:
            self.E.pos = target
            self.E.target_idx += 1
            if self.E.target_idx >= len(WAYPOINTS):
                damage = 3 if self.E.level == 3 else 1
                for _ in range(damage):
                    EventHandler().notify("BaseDamaged")
                self.E.destroy()
        else:
            if dir_vec.length() > 0:
                self.E.pos += dir_vec.normalize() * self.E.speed

        if self.slow_timer <= 0:
            self.E.speed = self.E.base_speed
            self.E.change_state(ApproachingState)