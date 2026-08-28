import random
import pygame
from abc import ABC, abstractmethod


def load_image_safe(path, size=(32, 32)):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    except Exception:
        return None


class obj(ABC):
    def __init__(self, x, y, sprites):
        self.x = x
        self.y = y
        self.sprites = sprites

    def draw(self, screen):
        if self.sprites:
            screen.blit(self.sprites[0], (self.x, self.y))

    @abstractmethod
    def update(self, dt):
        pass


class Cell(obj):
    def __init__(self, x, y, size, grid_x, grid_y, coffee_imgs):
        super().__init__(x, y, [])
        self.size = size
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.coffee_imgs = coffee_imgs

        self.revealed = False
        self.content = None
        self.consumed = False
        self.is_bug_alive = True
        self.is_cleared = False
        self.damage_val = 0
        self.xp_val = 0
        self.neighbor_damage = 0

        self.mark_number = 0

        self.font_small = pygame.font.Font(None, 16)
        self.font_big = pygame.font.Font(None, 24)
        self.font_mark = pygame.font.Font(None, 26)

    def reveal(self, player, grid):
        if not self.revealed:
            self.revealed = True
            self.mark_number = 0

            if self.content == "BAÚ":
                self.is_bug_alive = False
                grid.remaining_items["BAÚ"] -= 1
                return True

            if self.content in Grid.BUG_DATABASE:
                if self.damage_val > player.hp:
                    player.hp = 0
                    player.game_over = True
                    return True

                player.hp -= self.damage_val
                player.xp += self.xp_val
                grid.remaining_items[self.content] -= 1
                self.is_bug_alive = False
                grid.calculate_neighbor_damages()

                # Checa se o Meltdown foi derrotado
                if self.content == "MELTDOWN":
                    player.victory = True

                return True
            return True

        if self.revealed and self.content == "BAÚ" and not self.is_cleared:
            player.xp += 5
            self.is_cleared = True
            return True

        if self.revealed and self.content in Grid.BUG_DATABASE and self.is_bug_alive:
            if self.damage_val > player.hp:
                player.hp = 0
                player.game_over = True
                return True

            player.hp -= self.damage_val
            player.xp += self.xp_val
            grid.remaining_items[self.content] -= 1
            self.is_bug_alive = False
            grid.calculate_neighbor_damages()

            if self.content == "MELTDOWN":
                player.victory = True

            return True

        if self.revealed and self.content in Grid.BUG_DATABASE and not self.is_bug_alive:
            self.is_cleared = True
            return True

        return False

    def drink_coffee(self, player, grid):
        if self.revealed and self.content == "CAFÉ" and not self.consumed:
            self.consumed = True
            self.is_cleared = True
            player.hp = player.max_hp
            grid.remaining_items["CAFÉ"] -= 1
            return True
        return False

    def update(self, dt):
        pass

    def draw_gem(self, screen, cx, cy, color=(255, 215, 0)):
        pygame.draw.polygon(
            screen,
            color,
            [
                (cx, cy - 5),
                (cx + 4, cy - 1),
                (cx, cy + 5),
                (cx - 4, cy - 1)
            ]
        )

    def draw(self, screen, is_selected=False):
        rect = pygame.Rect(self.x, self.y, self.size, self.size)

        if not self.revealed:
            pygame.draw.rect(screen, (45, 48, 60), rect)
            pygame.draw.rect(screen, (70, 74, 92), rect, 2)

            if self.mark_number > 0:
                txt_mark = self.font_mark.render(str(self.mark_number), True, (52, 211, 153))
                txt_rect = txt_mark.get_rect(center=rect.center)
                screen.blit(txt_mark, txt_rect)
        else:
            pygame.draw.rect(screen, (28, 30, 38), rect)
            pygame.draw.rect(screen, (42, 45, 56), rect, 1)

            if self.content == "CAFÉ" and not self.is_cleared:
                img = self.coffee_imgs[0]
                if img:
                    screen.blit(img, (self.x + (self.size - img.get_width()) // 2, self.y + 6))
                else:
                    txt = self.font_big.render("☕", True, (100, 255, 100))
                    screen.blit(txt, (self.x + 14, self.y + 12))

            elif self.content == "BAÚ" and not self.is_cleared:
                box_rect = pygame.Rect(self.x + 4, self.y + 10, 44, 28)
                pygame.draw.rect(screen, (160, 110, 30), box_rect, border_radius=4)
                pygame.draw.rect(screen, (220, 170, 50), box_rect, width=1, border_radius=4)

                self.draw_gem(screen, self.x + 12, self.y + 24)
                txt_b = self.font_small.render("+5XP", True, (255, 255, 200))
                screen.blit(txt_b, (self.x + 18, self.y + 17))

            elif self.content in Grid.BUG_DATABASE and not self.is_cleared:
                if self.is_bug_alive:
                    txt_code = self.font_small.render(self.content, True, (255, 90, 90))
                    txt_dmg = self.font_big.render(str(self.damage_val), True, (255, 215, 0))
                    screen.blit(txt_code, (self.x + 5, self.y + 5))
                    screen.blit(txt_dmg, (self.x + 18, self.y + 24))
                else:
                    txt_code = self.font_small.render(self.content, True, (130, 135, 150))
                    screen.blit(txt_code, (self.x + 5, self.y + 5))

                    self.draw_gem(screen, self.x + 12, self.y + 31)
                    txt_xp = self.font_small.render(f"+{self.xp_val}", True, (255, 255, 200))
                    screen.blit(txt_xp, (self.x + 20, self.y + 25))

            elif (self.content is None or self.is_cleared) and self.neighbor_damage > 0:
                color = (210, 215, 225)
                if self.neighbor_damage >= 10:
                    color = (255, 190, 60)
                if self.neighbor_damage >= 20:
                    color = (255, 70, 70)

                txt = self.font_big.render(str(self.neighbor_damage), True, color)
                txt_rect = txt.get_rect(center=rect.center)
                screen.blit(txt, txt_rect)

        if is_selected:
            pygame.draw.rect(screen, (255, 220, 0), rect, 3)


class DraftMenu:
    def __init__(self):
        self.active = False
        self.target_cell = None
        self.rect = pygame.Rect(0, 0, 210, 170)
        self.font = pygame.font.Font(None, 20)

    def open(self, cell, screen_w, screen_h):
        self.active = True
        self.target_cell = cell
        self.rect.x = min(cell.x + cell.size + 5, screen_w - self.rect.width - 10)
        self.rect.y = min(cell.y, screen_h - self.rect.height - 10)

    def close(self):
        self.active = False
        self.target_cell = None

    def handle_click(self, pos):
        if not self.active or not self.target_cell:
            return False

        if not self.rect.collidepoint(pos):
            self.close()
            return True

        mx, my = pos
        rel_x, rel_y = mx - self.rect.x, my - self.rect.y

        if 10 <= rel_x <= 200 and 130 <= rel_y <= 158:
            self.target_cell.mark_number = 0
            self.close()
            return True

        for i in range(16):
            col, row = i % 4, i // 4
            bx = 10 + col * 48
            by = 10 + row * 28
            if bx <= rel_x <= bx + 42 and by <= rel_y <= by + 24:
                self.target_cell.mark_number = i + 1
                self.close()
                return True

        return True

    def draw(self, screen):
        if not self.active:
            return

        pygame.draw.rect(screen, (35, 38, 48), self.rect, border_radius=8)
        pygame.draw.rect(screen, (52, 211, 153), self.rect, width=2, border_radius=8)

        for i in range(16):
            col, row = i % 4, i // 4
            bx = self.rect.x + 10 + col * 48
            by = self.rect.y + 10 + row * 28
            b_rect = pygame.Rect(bx, by, 42, 24)

            pygame.draw.rect(screen, (50, 54, 68), b_rect, border_radius=4)
            num_txt = self.font.render(str(i + 1), True, (220, 225, 235))
            txt_rect = num_txt.get_rect(center=b_rect.center)
            screen.blit(num_txt, txt_rect)

        clear_rect = pygame.Rect(self.rect.x + 10, self.rect.y + 130, 190, 28)
        pygame.draw.rect(screen, (70, 40, 45), clear_rect, border_radius=4)
        c_txt = self.font.render("Remover Marca", True, (255, 150, 150))
        c_rect = c_txt.get_rect(center=clear_rect.center)
        screen.blit(c_txt, c_rect)


class Grid(obj):
    BUG_DATABASE = {
        "SYN": {"damage": 1, "name": "Syntax Error"},
        ";": {"damage": 2, "name": "Ponto e Vírgula"},
        "404": {"damage": 3, "name": "Not Found"},
        "L10k": {"damage": 4, "name": "Linha 10.000"},
        "+1": {"damage": 5, "name": "Off-by-One"},
        "NaN": {"damage": 6, "name": "Not a Number"},
        "NULL": {"damage": 7, "name": "Null Pointer"},
        "LOOP": {"damage": 8, "name": "Infinite Loop"},
        "GIT": {"damage": 9, "name": "Merge Conflict"},
        "STACK": {"damage": 10, "name": "Stack Overflow"},
        "Leak": {"damage": 11, "name": "Memory Leak"},
        "RACE": {"damage": 12, "name": "Race Condition"},
        "PROD": {"damage": 13, "name": "Bug em Produção"},
        "HACK": {"damage": 14, "name": "SQL Injection"},
        "CRASH": {"damage": 15, "name": "Kernel Panic"},
        "MELTDOWN": {"damage": 16, "name": "Fumaça no Servidor"},
    }

    def __init__(self, x, y, rows, cols, cell_size):
        super().__init__(x, y, [])
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.cells = []
        self.bug_info = Grid.BUG_DATABASE
        self.state = "SELECTING_START"

        coffee_full = load_image_safe("coffee_full.png", (cell_size - 12, cell_size - 12))
        coffee_empty = load_image_safe("coffee_empty.png", (cell_size - 12, cell_size - 12))
        self.coffee_imgs = (coffee_full, coffee_empty)

        self.fixed_counts = {
            "SYN": 14, ";": 12, "404": 10, "L10k": 8, "+1": 12,
            "NaN": 5, "NULL": 4, "LOOP": 4, "GIT": 2,
            "STACK": 1, "Leak": 1, "RACE": 1, "PROD": 1, "HACK": 1,
            "CRASH": 1, "MELTDOWN": 1,
            "CAFÉ": 12,
            "BAÚ": 6
        }

        self.remaining_items = {b: self.fixed_counts[b] for b in self.fixed_counts}

        self.cells = [
            [
                Cell(
                    self.x + c * self.cell_size,
                    self.y + r * self.cell_size,
                    self.cell_size,
                    c,
                    r,
                    self.coffee_imgs
                )
                for c in range(self.cols)
            ]
            for r in range(self.rows)
        ]

    def select_start_cell(self, start_col, start_row):
        self.state = "PLAYING"

        star_cluster = [(start_row, start_col)]
        candidates = []
        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) != (start_row, start_col):
                    dist = abs(r - start_row) + abs(c - start_col)
                    candidates.append((dist, r, c))

        candidates.sort(key=lambda x: x[0])
        for _, r, c in candidates[:12]:
            star_cluster.append((r, c))

        coffee_star_cell = star_cluster[1]
        self.cells[coffee_star_cell[0]][coffee_star_cell[1]].content = "CAFÉ"

        low_bugs = ["SYN", "SYN", ";", ";", "404"]
        mid_bugs = ["+1", "+1"]
        high_bug = [random.choice(["NaN", "NULL"])]

        star_bug_pool = low_bugs + mid_bugs + high_bug
        random.shuffle(star_bug_pool)

        star_outer_cells = star_cluster[2:]
        random.shuffle(star_outer_cells)

        placed_in_star = {}
        for r, c in star_outer_cells[:8]:
            bug = star_bug_pool.pop()
            cell = self.cells[r][c]
            cell.content = bug
            cell.damage_val = self.BUG_DATABASE[bug]["damage"]
            cell.xp_val = cell.damage_val
            placed_in_star[bug] = placed_in_star.get(bug, 0) + 1

        available_positions = [
            (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
            if (r, c) not in star_cluster
        ]
        random.shuffle(available_positions)

        counts_to_place = dict(self.fixed_counts)
        counts_to_place["CAFÉ"] -= 1
        for bug, count in placed_in_star.items():
            counts_to_place[bug] -= count

        for item, count in counts_to_place.items():
            for _ in range(count):
                if not available_positions:
                    break
                r, c = available_positions.pop()
                cell = self.cells[r][c]
                cell.content = item
                if item in self.BUG_DATABASE:
                    cell.damage_val = self.BUG_DATABASE[item]["damage"]
                    cell.xp_val = cell.damage_val

        self.calculate_neighbor_damages()

        for r, c in star_cluster:
            self.cells[r][c].revealed = True

    def calculate_neighbor_damages(self):
        for r in range(self.rows):
            for c in range(self.cols):
                total_damage = 0
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols:
                            neighbor = self.cells[nr][nc]
                            if (
                                neighbor.content in self.BUG_DATABASE
                                and neighbor.is_bug_alive
                            ):
                                total_damage += neighbor.damage_val

                self.cells[r][c].neighbor_damage = total_damage

    def update(self, dt):
        for row in self.cells:
            for cell in row:
                cell.update(dt)

    def draw(self, screen, cursor_pos):
        for r in range(self.rows):
            for c in range(self.cols):
                is_selected = r == cursor_pos[1] and c == cursor_pos[0]
                self.cells[r][c].draw(screen, is_selected)

    def get_cell_from_mouse(self, mouse_pos):
        mx, my = mouse_pos
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.cells[r][c]
                if (
                    cell.x <= mx < cell.x + self.cell_size
                    and cell.y <= my < cell.y + self.cell_size
                ):
                    return cell
        return None
