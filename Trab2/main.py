import sys
import pygame
from grid import Grid, DraftMenu


class Player:
    PROGRESSION_TABLE = [
        (5, 4),   # Estagiário I
        (5, 5),   # Estagiário II
        (6, 7),   # Estagiário III
        (6, 9),   # Estagiário IV
        (7, 9),   # Dev Júnior I
        (7, 10),  # Dev Júnior II
        (8, 12),  # Dev Júnior III
        (8, 14),  # Dev Júnior IV
        (9, 16),  # Dev Pleno I
        (10, 18), # Dev Pleno II
        (11, 21), # Dev Pleno III
        (12, 24), # Dev Pleno IV
        (13, 28), # Dev Sênior I
        (14, 32), # Dev Sênior II
        (15, 36), # Dev Sênior III
        (16, 40), # Dev Sênior IV
    ]

    def __init__(self, name="Jorge"):
        self.name = name
        self.titles = ["Estagiário", "Dev Júnior", "Dev Pleno", "Dev Sênior"]

        self.title_idx = 0
        self.sub_level = 1
        self.level_step = 0

        self.max_hp, self.xp_target = self.PROGRESSION_TABLE[0]
        self.hp = self.max_hp
        self.xp = 0
        self.game_over = False
        self.victory = False

        self.jorge_frame = 0
        self.jorge_timer = 0.0
        self.coffee_cycles_left = 0
        self.aura_frame = 0
        self.aura_timer = 0.0

    @property
    def full_title(self):
        roman = ["I", "II", "III", "IV"]
        extra = ""
        # Caso ultrapasse o limite da tabela
        if self.level_step >= len(self.PROGRESSION_TABLE):
            extra = f" (+{self.level_step - len(self.PROGRESSION_TABLE) + 1})"
            return f"Dev Sênior IV{extra}"
        return f"{self.titles[self.title_idx]} {roman[self.sub_level - 1]}"

    def can_level_up(self):
        return self.xp >= self.xp_target

    def do_level_up(self):
        if not self.can_level_up():
            return False

        # Se já estiver no nível máximo (Dev Sênior IV)
        if self.level_step >= len(self.PROGRESSION_TABLE) - 1:
            self.xp -= self.xp_target
            self.level_step += 1
            self.max_hp += 1  # Ganha +1 de HP máximo permanente
            self.hp = self.max_hp
            return True

        self.xp -= self.xp_target
        self.level_step += 1

        if self.sub_level < 4:
            self.sub_level += 1
        elif self.title_idx < len(self.titles) - 1:
            self.title_idx += 1
            self.sub_level = 1

        self.max_hp, self.xp_target = self.PROGRESSION_TABLE[self.level_step]
        self.hp = self.max_hp
        return True

    def trigger_coffee_effect(self, cycles=3):
        self.coffee_cycles_left = cycles
        self.aura_frame = 0
        self.aura_timer = 0.0

    def update_animations(self, dt, jorge_frames_count, aura_frames_count):
        self.jorge_timer += dt
        if self.jorge_timer >= (1.0 / 4):
            self.jorge_timer = 0.0
            self.jorge_frame = (self.jorge_frame + 1) % max(1, jorge_frames_count)

        if self.coffee_cycles_left > 0:
            self.aura_timer += dt
            if self.aura_timer >= (1.0 / 10):
                self.aura_timer = 0.0
                self.aura_frame += 1
                if self.aura_frame >= aura_frames_count:
                    self.aura_frame = 0
                    self.coffee_cycles_left -= 1


def load_spritesheet(path, frame_w=128, frame_h=128, scale_to=(128, 128)):
    try:
        sheet = pygame.image.load(path).convert_alpha()
        sheet_w, _ = sheet.get_size()
        frames = []

        for x in range(0, sheet_w, frame_w):
            if x + frame_w <= sheet_w:
                sub_surf = sheet.subsurface(pygame.Rect(x, 0, frame_w, frame_h))
                scaled_surf = pygame.transform.scale(sub_surf, scale_to)
                frames.append(scaled_surf)

        return frames if frames else [pygame.Surface(scale_to, pygame.SRCALPHA)]
    except Exception:
        surf = pygame.Surface(scale_to, pygame.SRCALPHA)
        surf.fill((70, 70, 90))
        return [surf]


def draw_gem_icon(screen, cx, cy, color=(255, 215, 0)):
    pygame.draw.polygon(
        screen,
        color,
        [
            (cx, cy - 8),
            (cx + 6, cy - 1),
            (cx, cy + 8),
            (cx - 6, cy - 1)
        ]
    )


def draw_victory_screen(screen, font, title_font):
    overlay = pygame.Surface((1040, 760), pygame.SRCALPHA)
    overlay.fill((10, 25, 15, 230))
    screen.blit(overlay, (0, 0))

    box = pygame.Rect(170, 100, 700, 560)
    pygame.draw.rect(screen, (25, 45, 30), box, border_radius=12)
    pygame.draw.rect(screen, (52, 211, 153), box, width=3, border_radius=12)

    title = title_font.render("SERVIDOR SALVO! VOCÊ VENCEU O JOGO!", True, (100, 255, 160))
    screen.blit(title, (box.x + (box.width - title.get_width()) // 2, box.y + 40))

    sub = font.render("O MELTDOWN foi contido com sucesso antes que o servidor caísse!", True, (200, 240, 210))
    screen.blit(sub, (box.x + (box.width - sub.get_width()) // 2, box.y + 90))

    pygame.draw.line(screen, (60, 100, 75), (box.x + 40, box.y + 130), (box.x + box.width - 40, box.y + 130), 2)

    cred_title = title_font.render("CRÉDITOS DA EQUIPE", True, (255, 215, 0))
    screen.blit(cred_title, (box.x + (box.width - cred_title.get_width()) // 2, box.y + 160))

    credits = [
        "Game Design & Programação: Beatriz dos Santos Cunha",
        "Artes & Animações: Beatriz dos Santos Cunha",
        "Agradecimentos Especiais: Professor João Vitor, por passar essa atividade. "
        "E meu irmão Arthur, que testou todas as versões do jogo e me deu feedbacks valiosos.",
    ]

    y_c = box.y + 220
    for line in credits:
        t = font.render(line, True, (220, 220, 220))
        screen.blit(t, (box.x + (box.width - t.get_width()) // 2, y_c))
        y_c += 35

    pygame.draw.line(screen, (60, 100, 75), (box.x + 40, box.y + 360), (box.x + box.width - 40, box.y + 360), 2)

    restart_txt = title_font.render("Pressione [R] para jogar uma nova partida", True, (255, 255, 120))
    screen.blit(restart_txt, (box.x + (box.width - restart_txt.get_width()) // 2, box.y + 420))


def draw_book_glossary(screen, font, title_font, grid):
    book_rect = pygame.Rect(40, 20, 960, 720)
    pygame.draw.rect(screen, (210, 185, 140), book_rect, border_radius=12)
    pygame.draw.rect(screen, (100, 40, 40), book_rect, width=6, border_radius=12)

    pygame.draw.line(screen, (160, 130, 95), (495, 20), (495, 740), 4)

    title_left = title_font.render("BUGNOMICON & MANUAL DE JOGO", True, (60, 30, 10))
    screen.blit(title_left, (60, 35))

    rules_lines = [
        "Jorge precisa acabar com os bugs do sistema!",
        "Proteja a empresa do meltdown do servidor!",
        "",
        "* Café recupera toda a energia (HP) de Jorge.",
        "  Clique botão direito ou tecla E para tomar.",
        "",
        "* Bugs são resolvidos se Jorge tiver HP",
        "  suficiente (Pode chegar a 0, mas não passar).",
        "",
        "* Números indicam a soma da dificuldade dos",
        "  bugs nas oito casas ao redor.",
        "",
        "* Pressione L para promover ou subir Max HP.",
        "",
        "* Derrote o MELTDOWN para salvar o servidor!",
        "",
        "* Botão direito ou tecla M na casa para rascunho.",
    ]

    y_text = 75
    for line in rules_lines:
        if line.startswith("Jorge") or line.startswith("Proteja"):
            txt = font.render(line, True, (120, 20, 20))
        elif line.startswith("*"):
            txt = font.render(line, True, (60, 30, 10))
        else:
            txt = font.render(line, True, (80, 50, 20))
        screen.blit(txt, (55, y_text))
        y_text += 20

    diag_box = pygame.Rect(55, 450, 420, 270)
    pygame.draw.rect(screen, (195, 170, 125), diag_box, border_radius=6)
    pygame.draw.rect(screen, (120, 95, 65), diag_box, width=2, border_radius=6)

    diag_title = title_font.render("Exemplo de Soma (8 Vizinhos):", True, (60, 30, 10))
    screen.blit(diag_title, (70, 460))

    cell_w, cell_h = 120, 45
    ox, oy = 85, 495

    grid_example = [
        ["SYN (1)", "", "L10k (4)"],
        ["", "5", ""],
        ["", "", ""]
    ]

    for r_idx, row_data in enumerate(grid_example):
        for c_idx, val_txt in enumerate(row_data):
            rect = pygame.Rect(ox + c_idx * cell_w, oy + r_idx * cell_h, cell_w, cell_h)
            pygame.draw.rect(screen, (220, 200, 160), rect)
            pygame.draw.rect(screen, (100, 80, 50), rect, 1)
            if val_txt:
                if "SOMA" in val_txt:
                    t = title_font.render(val_txt, True, (200, 40, 40))
                    screen.blit(t, (ox + c_idx * cell_w + 12, oy + r_idx * cell_h + 12))
                else:
                    t = font.render(val_txt, True, (140, 30, 30))
                    screen.blit(t, (ox + c_idx * cell_w + 20, oy + r_idx * cell_h + 14))

    title_right = title_font.render("LISTA DE BUGS & ITENS", True, (60, 30, 10))
    screen.blit(title_right, (515, 35))

    y_start = 75
    col1_x, col2_x = 510, 745
    card_w, card_h = 225, 62

    all_items = list(grid.bug_info.items()) + [
        ("CAFÉ", {"name": "Café Renovador", "damage": 0}),
        ("BAÚ", {"name": "Baú de Experiência", "damage": 0})
    ]

    for i, (code, info) in enumerate(all_items):
        col = col1_x if i < 9 else col2_x
        y = y_start + (i % 9) * 68

        card = pygame.Rect(col, y, card_w, card_h)
        pygame.draw.rect(screen, (195, 170, 125), card, border_radius=6)
        pygame.draw.rect(screen, (120, 95, 65), card, width=1, border_radius=6)

        count = grid.remaining_items[code]
        status = f"Restam no mapa: {count}" if count > 0 else "RESOLVIDO!"

        if code in ("CAFÉ", "BAÚ"):
            c_code = font.render(f"[Item] {code}", True, (20, 100, 40))
        else:
            c_code = font.render(f"[{info['damage']} Dmg] {code}", True, (140, 20, 20))

        c_name = font.render(f"{info['name']}", True, (50, 50, 50))
        c_count = font.render(status, True, (30, 120, 30) if count == 0 else (120, 40, 40))

        screen.blit(c_code, (col + 8, y + 4))
        screen.blit(c_name, (col + 8, y + 22))
        screen.blit(c_count, (col + 8, y + 40))

    close_txt = title_font.render("[G] Fechar Bugnomicon", True, (100, 40, 40))
    screen.blit(close_txt, (515, 690))


pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 1040, 760
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Code Sweeper: First Edition")

font = pygame.font.Font(None, 22)
title_font = pygame.font.Font(None, 28)

ROWS, COLS = 10, 13
CELL_SIZE = 52
GRID_X = (WIDTH - (COLS * CELL_SIZE)) // 2
GRID_Y = 160

jorge_anim_levels = [
    load_spritesheet("pixilart-sprite (5).png", 128, 128, scale_to=(128, 128)),
    load_spritesheet("pixilart-sprite (6).png", 128, 128, scale_to=(128, 128)),
    load_spritesheet("pixilart-sprite (7).png", 128, 128, scale_to=(128, 128)),
    load_spritesheet("pixilart-sprite (8).png", 128, 128, scale_to=(128, 128)),
]

aura_frames = load_spritesheet("pixilart-sprite (9).png", 128, 128, scale_to=(128, 128))

player = Player("Jorge")
grid = Grid(GRID_X, GRID_Y, ROWS, COLS, CELL_SIZE)
draft_menu = DraftMenu()
cursor_pos = [0, 0]
clock = pygame.time.Clock()

show_glossary = False

while True:
    dt = clock.tick(60) / 1000.0

    current_idx = min(player.title_idx, len(jorge_anim_levels) - 1)
    current_jorge_frames = jorge_anim_levels[current_idx]
    player.update_animations(dt, len(current_jorge_frames), len(aura_frames))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if event.key == pygame.K_g:
                show_glossary = not show_glossary

            if not player.game_over and not player.victory and not show_glossary:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    cursor_pos[0] = max(0, cursor_pos[0] - 1)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    cursor_pos[0] = min(COLS - 1, cursor_pos[0] + 1)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    cursor_pos[1] = max(0, cursor_pos[1] - 1)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    cursor_pos[1] = min(ROWS - 1, cursor_pos[1] + 1)

                elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    if grid.state == "SELECTING_START":
                        grid.select_start_cell(cursor_pos[0], cursor_pos[1])
                    else:
                        cell = grid.cells[cursor_pos[1]][cursor_pos[0]]
                        cell.reveal(player, grid)

                elif event.key == pygame.K_m and grid.state == "PLAYING":
                    cell = grid.cells[cursor_pos[1]][cursor_pos[0]]
                    if not cell.revealed:
                        draft_menu.open(cell, WIDTH, HEIGHT)

                elif event.key in (pygame.K_e,):
                    cell = grid.cells[cursor_pos[1]][cursor_pos[0]]
                    if cell.drink_coffee(player, grid):
                        player.trigger_coffee_effect(cycles=3)

                elif event.key == pygame.K_l:
                    player.do_level_up()

            if event.key == pygame.K_r:
                player = Player("Jorge")
                grid = Grid(GRID_X, GRID_Y, ROWS, COLS, CELL_SIZE)

        elif event.type == pygame.MOUSEBUTTONDOWN and not player.game_over and not player.victory and not show_glossary:
            mx, my = pygame.mouse.get_pos()

            if draft_menu.active:
                if draft_menu.handle_click((mx, my)):
                    continue

            cell = grid.get_cell_from_mouse((mx, my))

            if event.button == 1:
                if cell:
                    cursor_pos = [cell.grid_x, cell.grid_y]
                    if grid.state == "SELECTING_START":
                        grid.select_start_cell(cell.grid_x, cell.grid_y)
                    else:
                        cell.reveal(player, grid)
                elif player.can_level_up() and (WIDTH // 2 - 350) <= mx <= (WIDTH // 2 + 350) and 10 <= my <= 145:
                    player.do_level_up()

            elif event.button == 3 and cell and grid.state == "PLAYING":
                if not cell.revealed:
                    draft_menu.open(cell, WIDTH, HEIGHT)
                else:
                    if cell.drink_coffee(player, grid):
                        player.trigger_coffee_effect(cycles=3)

    grid.update(dt)
    screen.fill((18, 20, 26))

    # HUD Superior
    card_w = 700
    card_x = (WIDTH - card_w) // 2
    card_rect = pygame.Rect(card_x, 10, card_w, 138)
    pygame.draw.rect(screen, (28, 31, 40), card_rect, border_radius=10)

    avatar_bg = pygame.Rect(card_x + 10, 15, 128, 128)
    pygame.draw.rect(screen, (45, 50, 65), avatar_bg, border_radius=8)

    if player.coffee_cycles_left > 0:
        screen.blit(aura_frames[player.aura_frame], (card_x + 10, 15))

    current_frame_idx = player.jorge_frame % len(current_jorge_frames)
    screen.blit(current_jorge_frames[current_frame_idx], (card_x + 10, 15))

    pygame.draw.rect(screen, (60, 65, 85), avatar_bg, width=2, border_radius=8)
    pygame.draw.rect(screen, (60, 65, 85), card_rect, border_radius=10, width=2)

    name_txt = title_font.render(f"{player.name} ({player.full_title})", True, (255, 215, 0))
    screen.blit(name_txt, (card_x + 150, 20))

    hp_label = font.render(f"HP: {player.hp}/{player.max_hp}", True, (255, 100, 100))
    screen.blit(hp_label, (card_x + 150, 55))

    # Desenha as bolinhas de vida
    start_x, start_y = card_x + 235, 61
    for i in range(player.hp):
        pygame.draw.circle(screen, (255, 70, 70), (start_x + i * 14, start_y), 5)

    xp_label = font.render(f"XP: {player.xp}/{player.xp_target}", True, (100, 255, 140))
    screen.blit(xp_label, (card_x + 150, 95))

    if player.can_level_up():
        draw_gem_icon(screen, card_x + 280, 102)
        btn_msg = "⚡ [L] MAX HP +1!" if player.level_step >= len(player.PROGRESSION_TABLE) - 1 else "⚡ [L] SUBIR NÍVEL!"
        lvl_up_alert = font.render(btn_msg, True, (255, 255, 100))
        screen.blit(lvl_up_alert, (card_x + 295, 95))

    btn_book = pygame.Rect(WIDTH - 160, 15, 140, 38)
    pygame.draw.rect(screen, (50, 55, 70), btn_book, border_radius=6)
    pygame.draw.rect(screen, (80, 85, 110), btn_book, width=1, border_radius=6)
    b_txt = font.render("📖 Bugnomicon [G]", True, (220, 225, 240))
    screen.blit(b_txt, (WIDTH - 150, 25))

    grid.draw(screen, cursor_pos)
    draft_menu.draw(screen)

    if show_glossary:
        draw_book_glossary(screen, font, title_font, grid)

    if player.victory:
        draw_victory_screen(screen, font, title_font)
    elif player.game_over:
        go_txt = title_font.render(
            "SYSTEM CRASH! Dano maior que o HP restante. Pressione [R] para Reiniciar",
            True,
            (255, 60, 60),
        )
        screen.blit(go_txt, (WIDTH // 2 - go_txt.get_width() // 2, HEIGHT - 30))

    pygame.display.flip()
