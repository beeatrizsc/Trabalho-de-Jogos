import pygame
import sys

TILE_SIZE = 32
GRID_WIDTH = 20
GRID_HEIGHT = 15
MARGIN = 2

WINDOW_WIDTH = GRID_WIDTH * TILE_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * TILE_SIZE

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Autotiling com Dual Grid")
clock = pygame.time.Clock()

world_grid = [[0 for _ in range(GRID_WIDTH + 1)] for _ in range(GRID_HEIGHT + 1)]

BITMASK_TO_TILE_INDEX = {
    0:  12,  # Tudo Água
    1:  15,  # Canto Topo-Esquerdo de grama
    2:  8,   # Canto Topo-Direito de grama
    3:  9,   # Borda Superior
    4:  0,   # Canto Inferior-Esquerdo de grama
    5:  11,  # Lateral Esquerda de grama
    6:  14,  # Diagonais Baixo-Esq + Topo-Dir
    7:  7,   # Quina sem Baixo-Direito
    8:  13,  # Canto Inferior-Direito de grama
    9:  4,   # Diagonais Topo-Esq + Baixo-Dir
    10: 1,   # Lateral Direita de grama
    11: 10,  # Quina sem Baixo-Esquerdo
    12: 3,   # Borda Inferior
    13: 2,   # Quina sem Topo-Direito
    14: 5,   # Quina sem Topo-Esquerdo
    15: 6    # Tudo Grama 
}

def load_custom_tileset(filename):
    spritesheet = pygame.image.load(filename).convert_alpha()
    raw_tiles = []
    
    # Recorta os 16 tiles sequencialmente da imagem
    for row in range(4):
        for col in range(4):
            rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            surf.blit(spritesheet, (0, 0), rect)
            raw_tiles.append(surf)
            
    # Mapeia as imagens recortadas para os valores corretos do Dual Grid
    dual_sprites = {}
    for bitmask, tile_idx in BITMASK_TO_TILE_INDEX.items():
        dual_sprites[bitmask] = raw_tiles[tile_idx]
        
    return dual_sprites

# Carrega a imagem salva
dual_sprites = load_custom_tileset("pixil-frame-0.png")

def draw_dual_grid():
    offset = TILE_SIZE // 2
    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            tl = world_grid[row][col]
            tr = world_grid[row][col + 1]
            bl = world_grid[row + 1][col]
            br = world_grid[row + 1][col + 1]
            
            bitmask = (tl << 0) | (tr << 1) | (bl << 2) | (br << 3)
            
            pos_x = col * TILE_SIZE + offset
            pos_y = row * TILE_SIZE + offset
            
            screen.blit(dual_sprites[bitmask], (pos_x - offset, pos_y - offset))

# --- Loop Principal ---
running = True
while running:
    screen.fill((30, 30, 35))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    # Checa os botões do mouse pressionados
    # mouse_buttons[0] = Botão Esquerdo (Desenha / Grama = 1)
    # mouse_buttons[2] = Botão Direito (Apaga / Água = 0)
    mouse_buttons = pygame.mouse.get_pressed()
    
    if mouse_buttons[0] or mouse_buttons[2]:
        mx, my = pygame.mouse.get_pos()
        gx = mx // TILE_SIZE
        gy = my // TILE_SIZE
        
        # Respeita a margem delimitada
        if MARGIN <= gx <= (GRID_WIDTH - MARGIN) and MARGIN <= gy <= (GRID_HEIGHT - MARGIN):
            # Se for botão esquerdo coloca 1 (Grama), se for direito coloca 0 (Água)
            world_grid[gy][gx] = 1 if mouse_buttons[0] else 0

    # Renderiza o mapa com o autotiling atualizado
    draw_dual_grid()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
