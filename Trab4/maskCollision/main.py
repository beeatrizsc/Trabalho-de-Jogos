import pygame
import math

pygame.init()
screen = pygame.display.set_mode((800, 500))
pygame.display.set_caption("Golf Star Quest")
clock = pygame.time.Clock()

# Fontes Padrão
font_p = pygame.font.SysFont("Arial", 14, bold=True)
font_m = pygame.font.SysFont("Arial", 18, bold=True)
font_g = pygame.font.SysFont("Arial", 26, bold=True)

# -------------------------------------------------------------
# 1. CARREGAMENTO DAS IMAGENS (PIXEL ART / ARQUIVOS PNG)
# -------------------------------------------------------------
try:
    img_bola = pygame.image.load("bola.png").convert_alpha()
    img_bola = pygame.transform.scale(img_bola, (20, 20))

    img_estrela_amarela = pygame.image.load("estrela.png").convert_alpha()
    img_estrela_amarela = pygame.transform.scale(img_estrela_amarela, (32, 32))
    img_estrela_amarela_hub = pygame.transform.scale(img_estrela_amarela, (20, 20))
    img_estrela_amarela_win = pygame.transform.scale(img_estrela_amarela, (64, 64))

    img_estrela_cinza = pygame.image.load("estrelacinza.png").convert_alpha()
    img_estrela_cinza = pygame.transform.scale(img_estrela_cinza, (32, 32))
    img_estrela_cinza_hub = pygame.transform.scale(img_estrela_cinza, (20, 20))
    img_estrela_cinza_win = pygame.transform.scale(img_estrela_cinza, (64, 64))

    img_trofeu = pygame.image.load("trofeu.png").convert_alpha()
    img_trofeu = pygame.transform.scale(img_trofeu, (32, 32))
except pygame.error as e:
    print(f"Erro ao carregar imagem: {e}")
    print("Certifique-se de que os arquivos 'bola.png', 'estrela.png', 'estrelacinza.png' e 'trofeu.png' estão na mesma pasta do código!")

# -------------------------------------------------------------
# 2. FUNÇÕES VISUAIS E GERADORES
# -------------------------------------------------------------

def desenhar_estrela(surface, x, y, ativa=True):
    img = img_estrela_amarela if ativa else img_estrela_cinza
    surface.blit(img, (x - 12, y - 12))

def desenhar_estrela_hub(surface, x, y, ativa=True):
    img = img_estrela_amarela_hub if ativa else img_estrela_cinza_hub
    surface.blit(img, (x - 10, y - 10))

def desenhar_estrela_vitoria(surface, x, y, ativa=True):
    img = img_estrela_amarela_win if ativa else img_estrela_cinza_win
    surface.blit(img, (x - 32, y - 32))

def desenhar_icone_trofeu(surface, x, y):
    surface.blit(img_trofeu, (x + 4, y + 4))

def criar_paredes_nivel(nivel):
    surf = pygame.Surface((800, 500), pygame.SRCALPHA)
    cor = (200, 160, 60)
    if nivel == 1:
        pygame.draw.rect(surf, cor, (50, 80, 700, 340), 16, border_radius=10)
    elif nivel == 2:
        pygame.draw.line(surf, cor, (50, 80), (750, 80), 16)
        pygame.draw.line(surf, cor, (50, 80), (50, 420), 16)
        pygame.draw.line(surf, cor, (50, 420), (400, 420), 16)
        pygame.draw.line(surf, cor, (400, 420), (400, 250), 16)
        pygame.draw.line(surf, cor, (400, 250), (750, 250), 16)
        pygame.draw.line(surf, cor, (750, 80), (750, 250), 16)
    elif nivel in (3, 4, 5):
        pygame.draw.rect(surf, cor, (50, 80, 700, 340), 16, border_radius=10)
        pygame.draw.line(surf, cor, (320, 80), (320, 280), 16)
        if nivel == 5:
            pygame.draw.line(surf, cor, (500, 220), (500, 420), 16)
    return surf

def criar_areia_nivel(nivel):
    surf = pygame.Surface((800, 500), pygame.SRCALPHA)
    if nivel in (3, 5):
        pygame.draw.ellipse(surf, (225, 198, 130), (160, 280, 130, 80))
        if nivel == 5:
            pygame.draw.ellipse(surf, (225, 198, 130), (550, 120, 110, 70))
    return surf

def criar_buraco_nivel(nivel):
    surf = pygame.Surface((800, 500), pygame.SRCALPHA)
    pos_buracos = {1: (700, 250), 2: (700, 160), 3: (700, 350), 4: (700, 160), 5: (700, 350)}
    pos = pos_buracos.get(nivel, (700, 250))
    pygame.draw.circle(surf, (20, 20, 20), pos, 18)
    return surf, pos

# Estado do Jogo
nivel_atual = 1
max_niveis = 5
estrelas_por_nivel = {i: [False, False, False] for i in range(1, max_niveis + 1)}

# Títulos salvos permanentemente durante as jogatinas
titulos_conquistados_permanentes = set()

posicoes_estrelas_niveis = {
    1: [(250, 240), (450, 240), (600, 240)],
    2: [(200, 200), (300, 350), (600, 160)],
    3: [(220, 320), (400, 180), (580, 250)],
    4: [(180, 180), (380, 350), (550, 180)],
    5: [(220, 320), (420, 250), (600, 150)]
}

def total_estrelas_jogatina():
    return sum(sum(e) for e in estrelas_por_nivel.values())

def carregar_nivel(num_nivel):
    global paredes_img, paredes_mask, areia_img, areia_mask, buraco_img, pos_buraco
    global bola_x, bola_y, bola_vx, bola_vy, em_movimento, tacadas, max_tacadas, vitoria, derrota
    
    paredes_img = criar_paredes_nivel(num_nivel)
    paredes_mask = pygame.mask.from_surface(paredes_img)
    areia_img = criar_areia_nivel(num_nivel)
    areia_mask = pygame.mask.from_surface(areia_img)
    buraco_img, pos_buraco = criar_buraco_nivel(num_nivel)
    buraco_mask = pygame.mask.from_surface(buraco_img)

    bola_x, bola_y = 100, 250
    bola_vx, bola_vy = 0.0, 0.0
    em_movimento = False
    tacadas = 0
    max_tacadas = 5 if num_nivel in (4, 5) else 999
    vitoria = False
    derrota = False
    return buraco_mask

def reiniciar_jogatina_completa():
    global nivel_atual, estrelas_por_nivel, exibir_achievements, buraco_mask
    nivel_atual = 1
    estrelas_por_nivel = {i: [False, False, False] for i in range(1, max_niveis + 1)}
    exibir_achievements = False
    buraco_mask = carregar_nivel(nivel_atual)

bola_img = img_bola
bola_mask = pygame.mask.from_surface(bola_img)
buraco_mask = carregar_nivel(nivel_atual)

arrastando_taco = False
exibir_achievements = False

# -------------------------------------------------------------
# 3. LOOP PRINCIPAL DO JOGO
# -------------------------------------------------------------
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a: # Tecla para abrir/fechar Achievements
                exibir_achievements = not exibir_achievements
                
            if event.key == pygame.K_r: # Reiniciar Nível Atual ou Nova Jogatina
                if exibir_achievements or (nivel_atual == max_niveis and vitoria):
                    reiniciar_jogatina_completa()
                else:
                    buraco_mask = carregar_nivel(nivel_atual)

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            
            # Clique no Botão do Troféu
            if 740 <= mx <= 780 and 15 <= my <= 55:
                exibir_achievements = not exibir_achievements
                continue

            # Clique no Botão da Pop-up de Fim de Nível
            if vitoria and not exibir_achievements:
                if 280 <= mx <= 520 and 340 <= my <= 385:
                    if nivel_atual < max_niveis:
                        nivel_atual += 1
                        buraco_mask = carregar_nivel(nivel_atual)
                    else:
                        exibir_achievements = True
                continue

            # Iniciar Tacada
            if not em_movimento and not vitoria and not derrota and not exibir_achievements:
                if math.hypot(mx - bola_x, my - bola_y) < 30:
                    arrastando_taco = True

        elif event.type == pygame.MOUSEBUTTONUP and arrastando_taco:
            mx, my = pygame.mouse.get_pos()
            dx, dy = bola_x - mx, bola_y - my
            bola_vx, bola_vy = dx * 0.04, dy * 0.04
            
            vel_max = 12.0
            vel_atual = math.hypot(bola_vx, bola_vy)
            if vel_atual > vel_max:
                bola_vx = (bola_vx / vel_atual) * vel_max
                bola_vy = (bola_vy / vel_atual) * vel_max

            arrastando_taco = False
            em_movimento = True
            tacadas += 1

    # -------------------------------------------------------------
    # 4. FÍSICA E LÓGICA
    # -------------------------------------------------------------
    if em_movimento and not exibir_achievements:
        pos_ant_x, pos_ant_y = bola_x, bola_y
        bola_x += bola_vx
        bola_y += bola_vy
        
        atrito = 0.98
        pos_b = (int(bola_x - 10), int(bola_y - 10))

        if areia_mask.overlap(bola_mask, pos_b):
            atrito = 0.88

        bola_vx *= atrito
        bola_vy *= atrito

        # Colisão com Paredes
        if paredes_mask.overlap(bola_mask, pos_b):
            bola_x, bola_y = pos_ant_x, pos_ant_y
            pos_test_x = (int(pos_ant_x + bola_vx - 10), int(pos_ant_y - 10))
            pos_test_y = (int(pos_ant_x - 10), int(pos_ant_y + bola_vy - 10))
            if paredes_mask.overlap(bola_mask, pos_test_x): bola_vx *= -0.75
            if paredes_mask.overlap(bola_mask, pos_test_y): bola_vy *= -0.75

        # Coleta de Estrelas (Visualmente troca a imagem de cinza para amarela)
        for i, pos_e in enumerate(posicoes_estrelas_niveis[nivel_atual]):
            if not estrelas_por_nivel[nivel_atual][i]:
                if math.hypot(bola_x - pos_e[0], bola_y - pos_e[1]) < 20:
                    estrelas_por_nivel[nivel_atual][i] = True

        # Acertar o Buraco
        if buraco_mask.overlap(bola_mask, pos_b) and math.hypot(bola_vx, bola_vy) < 2.5:
            vitoria = True
            em_movimento = False
            bola_x, bola_y = pos_buraco
            
            # Desbloqueia exatamente 1 título ao vencer o Nível 5 (Fim da Jogatina)
            if nivel_atual == max_niveis:
                tot = total_estrelas_jogatina()
                if 0 <= tot <= 4:
                    titulos_conquistados_permanentes.add("Golfista Iniciante")
                elif 5 <= tot <= 9:
                    titulos_conquistados_permanentes.add("Tacada Prata")
                elif 10 <= tot <= 14:
                    titulos_conquistados_permanentes.add("Mestre do Campo")
                elif tot == 15:
                    titulos_conquistados_permanentes.add("Campeão Supremo")

        if math.hypot(bola_vx, bola_vy) < 0.15:
            em_movimento = False
            bola_vx, bola_vy = 0.0, 0.0
            if tacadas >= max_tacadas and not vitoria:
                derrota = True

    # -------------------------------------------------------------
    # 5. RENDERIZAÇÃO NA TELA
    # -------------------------------------------------------------
    screen.fill((34, 139, 34))

    # Campo
    screen.blit(areia_img, (0, 0))
    screen.blit(buraco_img, (0, 0))
    screen.blit(paredes_img, (0, 0))

    # Desenhar Estrelas no Campo
    for i, pos_e in enumerate(posicoes_estrelas_niveis[nivel_atual]):
        ativa = estrelas_por_nivel[nivel_atual][i]
        desenhar_estrela(screen, pos_e[0], pos_e[1], ativa)

    # Desenhar a Bola
    screen.blit(bola_img, (int(bola_x - 10), int(bola_y - 10)))

    # Linha de Mira
    if arrastando_taco:
        mx, my = pygame.mouse.get_pos()
        pygame.draw.line(screen, (255, 200, 0), (bola_x, bola_y), (mx, my), 2)
        dir_x = bola_x + (bola_x - mx)
        dir_y = bola_y + (bola_y - my)
        pygame.draw.line(screen, (255, 255, 255), (bola_x, bola_y), (dir_x, dir_y), 2)

    # HUD Superior
    str_tacadas = f"Tacadas: {tacadas}" if max_tacadas == 999 else f"Tacadas: {tacadas} / {max_tacadas}"
    txt_info = font_m.render(f"Nível {nivel_atual}  |  {str_tacadas}", True, (255, 255, 255))
    screen.blit(txt_info, (20, 20))

    # Estrelas Coletadas no Nível Atual
    txt_est = font_p.render("Estrelas do Nível:", True, (255, 255, 255))
    screen.blit(txt_est, (250, 22))
    for i in range(3):
        desenhar_estrela_hub(screen, 380 + (i * 25), 30, estrelas_por_nivel[nivel_atual][i])

    # Botão de Troféu no Canto Superior
    pygame.draw.rect(screen, (240, 239, 182), (740, 15, 40, 40), border_radius=8)
    desenhar_icone_trofeu(screen, 740, 15)

    # Mensagem de Derrota
    if derrota:
        txt_der1 = font_g.render("LIMITE DE TACADAS ALCANÇADO!", True, (255, 80, 80))
        txt_der2 = font_m.render("Pressione [ R ] para reiniciar este nível", True, (255, 255, 255))
        screen.blit(txt_der1, (210, 210))
        screen.blit(txt_der2, (230, 255))

    # POP-UP DE VITÓRIA DO NÍVEL
    if vitoria and not exibir_achievements:
        overlay = pygame.Surface((800, 500), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        pygame.draw.rect(screen, (245, 245, 250), (220, 90, 360, 320), border_radius=20)
        pygame.draw.rect(screen, (100, 80, 200), (220, 90, 360, 60), border_top_left_radius=20, border_top_right_radius=20)
        
        txt_v = font_g.render("NÍVEL CONCLUÍDO!", True, (255, 255, 255))
        screen.blit(txt_v, (290, 105))

        txt_desf = font_m.render("Estrelas deste Nível:", True, (50, 50, 50))
        screen.blit(txt_desf, (315, 170))
        
        for i in range(3):
            desenhar_estrela_vitoria(screen, 340 + (i * 60), 250, estrelas_por_nivel[nivel_atual][i])

        pygame.draw.rect(screen, (120, 60, 220), (280, 340, 240, 45), border_radius=12)
        msg_btn = "PRÓXIMO NÍVEL" if nivel_atual < max_niveis else "VER RESULTADO FINAL"
        txt_btn = font_m.render(msg_btn, True, (255, 255, 255))
        screen.blit(txt_btn, (325 if nivel_atual < max_niveis else 295, 350))

    # TELA DE ACHIEVEMENTS / LIVRINHO DE CONQUISTAS
    if exibir_achievements:
        overlay = pygame.Surface((800, 500), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        pygame.draw.rect(screen, (245, 235, 210), (150, 30, 500, 440), border_radius=15)
        pygame.draw.rect(screen, (110, 160, 40), (150, 30, 500, 50), border_top_left_radius=15, border_top_right_radius=15)
        
        txt_ach = font_g.render("LIVRO DE CONQUISTAS", True, (255, 255, 255))
        screen.blit(txt_ach, (260, 40))

        lista_achievements = [
            ("Golfista Iniciante", "Finalizar a jogatina com 0 a 4 estrelas", "Golfista Iniciante" in titulos_conquistados_permanentes),
            ("Tacada Prata", "Finalizar a jogatina com 5 a 9 estrelas", "Tacada Prata" in titulos_conquistados_permanentes),
            ("Mestre do Campo", "Finalizar a jogatina com 10 a 14 estrelas", "Mestre do Campo" in titulos_conquistados_permanentes),
            ("Campeão Supremo", "Finalizar a jogatina com 15 estrelas perfeitas", "Campeão Supremo" in titulos_conquistados_permanentes),
        ]

        y_off = 100
        for nome, desc, desbl in lista_achievements:
            pygame.draw.rect(screen, (230, 220, 190), (170, y_off, 460, 60), border_radius=8)
            
            txt_n = font_m.render(nome, True, (50, 40, 30))
            txt_d = font_p.render(desc, True, (100, 90, 80))
            screen.blit(txt_n, (185, y_off + 8))
            screen.blit(txt_d, (185, y_off + 32))

            if desbl:
                pygame.draw.circle(screen, (80, 160, 40), (600, y_off + 30), 16)
                txt_chk = font_m.render("OK", True, (255, 255, 255))
                screen.blit(txt_chk, (588, y_off + 20))
            else:
                pygame.draw.circle(screen, (180, 170, 150), (600, y_off + 30), 16)

            y_off += 70

        # ACHIEVEMENT SECRETO
        pygame.draw.rect(screen, (220, 200, 180), (170, y_off, 460, 60), border_radius=8)
        secreto_desbloqueado = len(titulos_conquistados_permanentes) == 4
        
        nome_sec = "CONQUISTADOR DE TÍTULOS" if secreto_desbloqueado else "???"
        desc_sec = "Desbloqueou todos os 4 títulos em jogatinas!" if secreto_desbloqueado else "???"
        
        txt_sn = font_m.render(nome_sec, True, (120, 30, 140) if secreto_desbloqueado else (100, 100, 100))
        txt_sd = font_p.render(desc_sec, True, (80, 80, 80))
        screen.blit(txt_sn, (185, y_off + 8))
        screen.blit(txt_sd, (185, y_off + 32))

        # Barra de Progresso da Jogatina
        tot_atual = len(titulos_conquistados_permanentes)
        tot_estrela = total_estrelas_jogatina()
        pygame.draw.rect(screen, (180, 180, 180), (170, 430, 460, 12), border_radius=8)
        largura_progresso = int((tot_atual / 4) * 460)
        if largura_progresso > 0:
            pygame.draw.rect(screen, (100, 200, 50), (170, 430, largura_progresso, 12), border_radius=8)

        txt_p = font_p.render(f"Esta Jogatina: {tot_estrela}/15 Estrelas  |  [A] Fechar  |  [R] Nova Jogatina", True, (60, 60, 60))
        screen.blit(txt_p, (180, 448))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
