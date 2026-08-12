# Inicialização
import pygame 
import random
pygame.init()
pygame.font.init()



font = font = pygame.font.Font(None, 50)
Nome = "Beatriz"
texto_temp = font.render(Nome, True, (0,0,0))
largura = texto_temp.get_width()
altura = texto_temp.get_height()

random.seed(Nome)
x, y =  random.randint(0, 500), random.randint(0, 400)

print(y)

# Cria a janela
WIDTH   =  800; HEIGHT =  600
screen = pygame.display.set_mode((WIDTH, HEIGHT))  

#loop
while True: 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        # Desenha
        screen.fill((30, 30, 30))
        pygame.draw.rect(screen, (255,255,255), (x,y,largura,altura))
        screen.blit(font.render(Nome, True, (0,0,0)), (x, y))
        pygame.display.flip()
