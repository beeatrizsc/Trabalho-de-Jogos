import pygame
import random
from enemy import Enemy
from util import EventHandler

class WaveManager:
    def __init__(self):
        self.current_wave = 1
        self.max_waves = 10
        self.enemies_to_spawn = 0
        self.enemies_alive = 0
        self.spawn_timer = 0
        self.wave_in_progress = False
        self.game_finished = False

        EventHandler().subscribe("EnemyKilled", self.on_enemy_killed)

    def start_next_wave(self):
        if self.current_wave <= self.max_waves and not self.wave_in_progress and not self.game_finished:
            self.wave_in_progress = True
            
            if self.current_wave == self.max_waves:
                total_enemies = 25
            else:
                total_enemies = 3 + (self.current_wave * 2)

            self.enemies_to_spawn = total_enemies
            self.enemies_alive = total_enemies

    def update(self, dt):
        if self.wave_in_progress and self.enemies_to_spawn > 0:
            self.spawn_timer -= dt
            if self.spawn_timer <= 0:
                if self.current_wave == 10:
                    self.spawn_timer = 45 if self.enemies_to_spawn > 1 else 120
                else:
                    self.spawn_timer = 75

                self.spawn_enemy()
                self.enemies_to_spawn -= 1

    def spawn_enemy(self):
        if self.current_wave == 10 and self.enemies_to_spawn == 1:
            lvl = 3
            hp = 3200
            speed = 0.6
            reward = 100
        else:
            if self.current_wave < 4:
                lvl = 1
            elif self.current_wave < 10:
                lvl = 2 if random.random() < (self.current_wave * 0.12) else 1
            else:
                lvl = 2 if random.random() < 0.6 else 1

            if lvl == 1:
                hp = 15 + (self.current_wave * 2)
                speed = 1.0 + (self.current_wave * 0.05)
                reward = 8 + (self.current_wave // 2)
            else:
                hp = 50 + (self.current_wave * 3)
                speed = 0.85 + (self.current_wave * 0.04)
                reward = 16 + self.current_wave

        enemy = Enemy(level=lvl, hp=int(hp), speed=speed, reward=reward)
        EventHandler().notify("SpawnObj", enemy)

    def on_enemy_killed(self, enemy=None):
        if self.wave_in_progress:
            self.enemies_alive -= 1

    def check_wave_completion(self, active_enemies_count):
        # Só finaliza a onda se NÃO HOUVER mais inimigos na tela E o spawner já tiver finalizado
        if self.wave_in_progress and self.enemies_to_spawn <= 0 and active_enemies_count == 0:
            self.wave_in_progress = False
            if self.current_wave >= self.max_waves:
                self.game_finished = True
                pygame.time.set_timer(pygame.USEREVENT + 1, 100, loops=1)
            else:
                self.current_wave += 1