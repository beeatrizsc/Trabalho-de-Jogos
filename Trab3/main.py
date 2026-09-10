import pygame
import random
from tower import Tower, ELEMENT_COLORS
from bullet import Bullet
from enemy import Enemy
from wave_manager import WaveManager
from util import EventHandler, circle_collision

pygame.init()
WIDTH, HEIGHT = 1024, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("O Despertar da Floresta - TD Merge")
clock = pygame.time.Clock()

objects = []
towers = []
grid = {} # (col, row) -> Tower

dragging_tower = None
original_grid_pos = None

gold = 90
rune_cost = 15
base_hp = 10
game_won = False
game_over = False

wave_mgr = WaveManager()

PATH_CELLS = {
    (0,2), (1,2), (2,2), (3,2),
    (3,3), (3,4), (3,5), (3,6),
    (4,6), (5,6), (6,6), (7,6), (8,6), (9,6), (10,6), (11,6),
    (11,5), (11,4), (11,3), (11,2),
    (12,2), (13,2)
}

def remove_obj(obj):
    if obj in objects: objects.remove(obj)

def add_obj(obj):
    objects.append(obj)

def on_base_damaged():
    global base_hp, game_over
    base_hp -= 1
    if base_hp <= 0:
        base_hp = 0
        game_over = True

def on_game_won():
    global game_won
    game_won = True

def on_gold_earned(amount):
    global gold
    gold += amount

EventHandler().subscribe("DestroyObj", remove_obj)
EventHandler().subscribe("SpawnObj", add_obj)
EventHandler().subscribe("BaseDamaged", on_base_damaged)
EventHandler().subscribe("GameWon", on_game_won)
EventHandler().subscribe("GoldEarned", on_gold_earned)

def get_grid_pos(mouse_pos):
    x, y = mouse_pos
    if 64 <= x < 64 + 14*64 and 96 <= y < 96 + 8*64:
        col = int((x - 64) // 64)
        row = int((y - 96) // 64)
        return (col, row)
    return None

running = True
while running:
    dt = 1
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.USEREVENT + 1:
            EventHandler().notify("GameWon")

        elif event.type == pygame.KEYDOWN and not game_over and not game_won:
            if event.key == pygame.K_SPACE:
                wave_mgr.start_next_wave()

            if event.key == pygame.K_c:
                if gold >= rune_cost:
                    empty_cells = [(c, r) for c in range(14) for r in range(8) 
                                   if (c, r) not in grid and (c, r) not in PATH_CELLS]
                    if empty_cells:
                        gold -= rune_cost
                        rune_cost += 5

                        pos = random.choice(empty_cells)
                        elem = random.choice(list(ELEMENT_COLORS.keys()))
                        new_tower = Tower(pos, elem)
                        grid[pos] = new_tower
                        towers.append(new_tower)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over:
            g_pos = get_grid_pos(event.pos)
            if g_pos and g_pos in grid:
                dragging_tower = grid[g_pos]
                dragging_tower.is_dragging = True
                original_grid_pos = g_pos

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and not game_over:
            if dragging_tower:
                dragging_tower.is_dragging = False
                target_gpos = get_grid_pos(event.pos)

                if target_gpos and target_gpos not in PATH_CELLS:
                    if target_gpos not in grid:
                        del grid[original_grid_pos]
                        dragging_tower.grid_pos = target_gpos
                        dragging_tower.pos = pygame.Vector2(64 + target_gpos[0]*64 + 4, 96 + target_gpos[1]*64 + 4)
                        grid[target_gpos] = dragging_tower

                    elif target_gpos != original_grid_pos:
                        target_tower = grid[target_gpos]
                        if (dragging_tower.element == target_tower.element and 
                            dragging_tower.level == target_tower.level and 
                            dragging_tower.level < 3):
                            
                            target_tower.level_up()
                            towers.remove(dragging_tower)
                            del grid[original_grid_pos]
                        else:
                            dragging_tower.pos = pygame.Vector2(64 + original_grid_pos[0]*64 + 4, 96 + original_grid_pos[1]*64 + 4)
                    else:
                        dragging_tower.pos = pygame.Vector2(64 + original_grid_pos[0]*64 + 4, 96 + original_grid_pos[1]*64 + 4)
                else:
                    dragging_tower.pos = pygame.Vector2(64 + original_grid_pos[0]*64 + 4, 96 + original_grid_pos[1]*64 + 4)

                dragging_tower = None

    if not game_over and not game_won:
        wave_mgr.update(dt)
        enemies = [o for o in objects if isinstance(o, Enemy)]
        bullets = [o for o in objects if isinstance(o, Bullet)]

        wave_mgr.check_wave_completion(len(enemies))

        for t in towers:
            t.update(dt, enemies)

        for obj in list(objects):
            obj.update(dt)

        for b in bullets:
            for e in enemies:
                if circle_collision(b.pos, b.radius, e.pos, e.radius):
                    e.take_damage(b.damage, apply_slow=b.apply_slow)
                    b.destroy()
                    break

    # RENDERIZAÇÃO
    screen.fill((28, 38, 28))

    for c in range(14):
        for r in range(8):
            rect = pygame.Rect(64 + c*64, 96 + r*64, 62, 62)
            if (c, r) in PATH_CELLS:
                pygame.draw.rect(screen, (185, 145, 100), rect)
            else:
                pygame.draw.rect(screen, (40, 55, 40), rect)

    for t in towers:
        if t != dragging_tower:
            t.draw(screen)

    # Desenha o alcance e a torre sendo arrastada
    if dragging_tower:
        dragging_tower.pos = pygame.Vector2(mouse_pos) - pygame.Vector2(28, 28)
        dragging_tower.draw_range_preview(screen)  # Círculo semi-transparente
        dragging_tower.draw(screen)

    for obj in objects:
        obj.draw(screen)

    # HUD
    font = pygame.font.SysFont(None, 32)
    screen.blit(font.render(f"Onda: {wave_mgr.current_wave}/{wave_mgr.max_waves}", True, (255, 255, 255)), (30, 25))
    screen.blit(font.render(f"Ouro: R${gold}", True, (255, 215, 0)), (200, 25))
    screen.blit(font.render(f"Vida: {base_hp}", True, (255, 100, 100)), (350, 25))
    screen.blit(font.render(f"[C] Comprar Runa (R${rune_cost})  |  [ESPAÇO] Iniciar Onda", True, (220, 220, 220)), (480, 25))

    if game_won:
        font_large = pygame.font.SysFont(None, 56)
        screen.blit(font_large.render("FLORESTA PURIFICADA! VOCÊ VENCEU!", True, (120, 255, 120)), (180, 380))
    elif game_over:
        font_large = pygame.font.SysFont(None, 56)
        screen.blit(font_large.render("A FLORESTA FOI DESTRUÍDA! GAME OVER", True, (255, 80, 80)), (160, 380))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
    
