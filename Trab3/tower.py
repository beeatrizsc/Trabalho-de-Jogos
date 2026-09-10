import pygame
from abc import ABC, abstractmethod
from util import colored_sprite, EventHandler
from bullet import Bullet

ELEMENT_COLORS = {
    "Terra": (34, 139, 34),
    "Fogo": (220, 20, 60),
    "Água": (30, 144, 255),
    "Ar": (240, 230, 140)
}

ELEMENT_STATS = {
    "Fogo":  {1: (3, 136, 70), 2: (6, 170, 50), 3: (12, 204, 35)},
    "Água":  {1: (1, 204, 60), 2: (2, 272, 45), 3: (6, 340, 30)},
    "Terra": {1: (1, 136, 45), 2: (2, 170, 35), 3: (4, 204, 25)},
    "Ar":    {1: (1, 68, 24), 2: (1, 102, 12), 3: (1, 136, 6)}
}

class Tower:
    def __init__(self, grid_pos, element="Terra"):
        self.grid_pos = grid_pos
        self.pos = pygame.Vector2(64 + grid_pos[0]*64 + 4, 96 + grid_pos[1]*64 + 4)
        self.level = 1
        self.element = element
        self.cooldown = 0
        self.is_dragging = False
        self.update_stats()
        self.state = Level1State(self)

    def update_stats(self):
        dmg, rng, cd = ELEMENT_STATS[self.element][self.level]
        self.damage = dmg
        self.range = rng
        self.max_cooldown = cd

    @property
    def center_pos(self):
        return self.pos + pygame.Vector2(28, 28)

    def update(self, dt, enemies):
        if self.is_dragging:
            return

        self.cooldown -= dt
        visible_enemies = [e for e in enemies if e.pos.x >= 32]
        self.state.update(dt, visible_enemies)

    def draw(self, screen):
        self.state.draw(screen)

    def draw_range_preview(self, screen):
        # Cria uma superfície transparente para desenhar a área de alcance
        surface_size = int(self.range * 2)
        range_surface = pygame.Surface((surface_size, surface_size), pygame.SRCALPHA)
        
        color = ELEMENT_COLORS.get(self.element, (255, 255, 255))
        # Círculo preenchido com 40 de opacidade (transparente)
        pygame.draw.circle(range_surface, (*color, 40), (self.range, self.range), self.range)
        # Borda com 180 de opacidade
        pygame.draw.circle(range_surface, (*color, 180), (self.range, self.range), self.range, 2)
        
        # Desenha a área centralizada no meio da torre
        top_left = self.center_pos - pygame.Vector2(self.range, self.range)
        screen.blit(range_surface, top_left)

    def level_up(self):
        if self.level < 3:
            self.level += 1
            self.update_stats()
            if self.level == 2:
                self.state = Level2State(self)
            elif self.level == 3:
                self.state = Level3GolemState(self)


class TowerState(ABC):
    def __init__(self, tower):
        self.T = tower
        self.color = ELEMENT_COLORS.get(tower.element, (255, 255, 255))
        self.update_sprite()

    @abstractmethod
    def update_sprite(self):
        pass

    def draw(self, screen):
        screen.blit(self.sprite, self.T.pos)

    def shoot(self, target_pos):
        is_earth = (self.T.element == "Terra")
        bullet = Bullet(self.T.center_pos, target_pos, self.color, damage=self.T.damage, apply_slow=is_earth)
        EventHandler().notify("SpawnObj", bullet)


class Level1State(TowerState):
    def update_sprite(self):
        self.sprite = colored_sprite(self.color, (56, 56))

    def update(self, dt, enemies):
        if self.T.cooldown <= 0:
            for e in enemies:
                if (e.pos - self.T.center_pos).length() <= self.T.range:
                    self.shoot(e.pos)
                    self.T.cooldown = self.T.max_cooldown
                    break


class Level2State(TowerState):
    def update_sprite(self):
        self.sprite = colored_sprite(self.color, (56, 56))
        pygame.draw.rect(self.sprite, (255, 255, 255), (4, 4, 48, 48), 2)

    def update(self, dt, enemies):
        if self.T.cooldown <= 0:
            for e in enemies:
                if (e.pos - self.T.center_pos).length() <= self.T.range:
                    self.shoot(e.pos)
                    self.T.cooldown = self.T.max_cooldown
                    break


class Level3GolemState(TowerState):
    def update_sprite(self):
        self.sprite = colored_sprite(self.color, (56, 56), shape="circle")
        pygame.draw.circle(self.sprite, (255, 255, 255), (28, 28), 12)

    def update(self, dt, enemies):
        if self.T.cooldown <= 0:
            for e in enemies:
                if (e.pos - self.T.center_pos).length() <= self.T.range:
                    self.shoot(e.pos)
                    self.T.cooldown = self.T.max_cooldown
                    break