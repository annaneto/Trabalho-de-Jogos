import pygame
import sys
import random

pygame.init()

LARGURA = 600
ALTURA = 400
BLOCO = 20
FPS = 10

# area reservada no canto pro placar, pra comida nunca nascer escondida atras dele
AREA_PLACAR_LARGURA = BLOCO * 7
AREA_PLACAR_ALTURA = BLOCO * 2

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Snake Game - Pygame")
clock = pygame.time.Clock()

# cores
FUNDO = (24, 26, 27)
FUNDO_GRADE = (32, 35, 36)
VERDE_COBRA = (46, 204, 113)
VERDE_CABECA = (39, 174, 96)
VERMELHO_COMIDA = (231, 76, 60)
BRANCO = (255, 255, 255)
PRETO = (20, 20, 20)

AZUL_BOTAO = (41, 128, 185)
AZUL_BOTAO_HOVER = (52, 152, 219)
VERMELHO_BOTAO = (192, 57, 43)
VERMELHO_BOTAO_HOVER = (231, 76, 60)
SOMBRA_BOTAO = (15, 15, 15)

fonte_titulo = pygame.font.SysFont("Arial", 40, bold=True)
fonte = pygame.font.SysFont("Arial", 22)

# botoes do menu (x, y, largura, altura)
botao_jogar = pygame.Rect(200, 160, 200, 50)
botao_sair = pygame.Rect(200, 230, 200, 50)


def gerar_comida(cobra):
   
    pos_valida = False
    while not pos_valida:
        x = random.randrange(0, LARGURA, BLOCO)
        y = random.randrange(0, ALTURA, BLOCO)
        dentro_do_placar = x < AREA_PLACAR_LARGURA and y < AREA_PLACAR_ALTURA
        if (x, y) not in cobra and not dentro_do_placar:
            pos_valida = True
    return (x, y)


def novo_jogo():
    meio = (LARGURA // 2, ALTURA // 2)
    cobra = [meio, (meio[0] - BLOCO, meio[1]), (meio[0] - BLOCO * 2, meio[1])]
    direcao = (BLOCO, 0)
    comida = gerar_comida(cobra)
    pontos = 0
    return cobra, direcao, comida, pontos


def botao(tela, rect, texto, cor1, cor2, mouse_pos):
    if rect.collidepoint(mouse_pos):
        cor = cor2
        offset = 2  
    else:
        cor = cor1
        offset = 0

    
    rect_sombra = rect.copy()
    rect_sombra.y += 4
    pygame.draw.rect(tela, SOMBRA_BOTAO, rect_sombra, border_radius=10)

    rect_botao = rect.copy()
    rect_botao.y += offset
    pygame.draw.rect(tela, cor, rect_botao, border_radius=10)

    texto_render = fonte.render(texto, True, BRANCO)
    rect_texto = texto_render.get_rect(center=rect_botao.center)
    tela.blit(texto_render, rect_texto)


def desenhar_grade(tela):
   
    for x in range(0, LARGURA, BLOCO):
        pygame.draw.line(tela, FUNDO_GRADE, (x, 0), (x, ALTURA))
    for y in range(0, ALTURA, BLOCO):
        pygame.draw.line(tela, FUNDO_GRADE, (0, y), (LARGURA, y))


# estado do jogo: MENU, JOGANDO ou GAME_OVER
estado = "MENU"
cobra, direcao, comida, pontos = novo_jogo()
rodando = True

while rodando:
    mouse_pos = pygame.mouse.get_pos()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if estado == "MENU":
                if botao_jogar.collidepoint(evento.pos):
                    cobra, direcao, comida, pontos = novo_jogo()
                    estado = "JOGANDO"
                elif botao_sair.collidepoint(evento.pos):
                    rodando = False

            elif estado == "GAME_OVER":
                if botao_jogar.collidepoint(evento.pos):
                    cobra, direcao, comida, pontos = novo_jogo()
                    estado = "JOGANDO"
                elif botao_sair.collidepoint(evento.pos):
                    estado = "MENU"

        elif evento.type == pygame.KEYDOWN and estado == "JOGANDO":
            if evento.key in (pygame.K_UP, pygame.K_w) and direcao != (0, BLOCO):
                direcao = (0, -BLOCO)
            elif evento.key in (pygame.K_DOWN, pygame.K_s) and direcao != (0, -BLOCO):
                direcao = (0, BLOCO)
            elif evento.key in (pygame.K_LEFT, pygame.K_a) and direcao != (BLOCO, 0):
                direcao = (-BLOCO, 0)
            elif evento.key in (pygame.K_RIGHT, pygame.K_d) and direcao != (-BLOCO, 0):
                direcao = (BLOCO, 0)
            elif evento.key == pygame.K_ESCAPE:
                estado = "MENU"

    if estado == "JOGANDO":
        cabeca_x = cobra[0][0] + direcao[0]
        cabeca_y = cobra[0][1] + direcao[1]
        nova_cabeca = (cabeca_x, cabeca_y)

       
        if nova_cabeca[0] < 0 or nova_cabeca[0] >= LARGURA or nova_cabeca[1] < 0 or nova_cabeca[1] >= ALTURA:
            estado = "GAME_OVER"
        elif nova_cabeca in cobra:
            estado = "GAME_OVER"
        else:
            cobra.insert(0, nova_cabeca)
            if nova_cabeca == comida:
                pontos += 10
                comida = gerar_comida(cobra)
            else:
                cobra.pop()  
    tela.fill(FUNDO)

    if estado == "MENU":
        desenhar_grade(tela)

        
        titulo_sombra = fonte_titulo.render("SNAKE GAME", True, PRETO)
        titulo = fonte_titulo.render("SNAKE GAME", True, VERDE_COBRA)
        pos_x = (LARGURA - titulo.get_width()) // 2
        tela.blit(titulo_sombra, (pos_x + 3, 73))
        tela.blit(titulo, (pos_x, 70))

        botao(tela, botao_jogar, "Jogar", AZUL_BOTAO, AZUL_BOTAO_HOVER, mouse_pos)
        botao(tela, botao_sair, "Sair", VERMELHO_BOTAO, VERMELHO_BOTAO_HOVER, mouse_pos)

    elif estado == "JOGANDO":
        desenhar_grade(tela)

        # comida redonda
        centro_comida = (comida[0] + BLOCO // 2, comida[1] + BLOCO // 2)
        pygame.draw.circle(tela, VERMELHO_COMIDA, centro_comida, BLOCO // 2 - 1)
        pygame.draw.circle(tela, (255, 180, 170), (centro_comida[0] - 3, centro_comida[1] - 3), 3)

        for i in range(len(cobra)):
            if i == 0:
                cor_segmento = VERDE_CABECA
            else:
                cor_segmento = VERDE_COBRA
            retangulo_segmento = (*cobra[i], BLOCO - 1, BLOCO - 1)
            pygame.draw.rect(tela, cor_segmento, retangulo_segmento, border_radius=6)

        # olhos
        cx = cobra[0][0] + BLOCO // 2
        cy = cobra[0][1] + BLOCO // 2
        if direcao == (BLOCO, 0):
            olho1, olho2 = (cx + 4, cy - 5), (cx + 4, cy + 5)
        elif direcao == (-BLOCO, 0):
            olho1, olho2 = (cx - 4, cy - 5), (cx - 4, cy + 5)
        elif direcao == (0, -BLOCO):
            olho1, olho2 = (cx - 5, cy - 4), (cx + 5, cy - 4)
        else:
            olho1, olho2 = (cx - 5, cy + 4), (cx + 5, cy + 4)

        pygame.draw.circle(tela, BRANCO, olho1, 3)
        pygame.draw.circle(tela, BRANCO, olho2, 3)
        pygame.draw.circle(tela, PRETO, olho1, 1)
        pygame.draw.circle(tela, PRETO, olho2, 1)

        # placar 
        texto_pontos = fonte.render(f"Pontos: {pontos}", True, BRANCO)
        caixa_placar = pygame.Rect(5, 5, texto_pontos.get_width() + 14, texto_pontos.get_height() + 8)
        pygame.draw.rect(tela, (0, 0, 0, 120), caixa_placar, border_radius=6)
        tela.blit(texto_pontos, (12, 9))

    elif estado == "GAME_OVER":
        texto_fim = fonte_titulo.render("GAME OVER", True, VERMELHO_COMIDA)
        tela.blit(texto_fim, ((LARGURA - texto_fim.get_width()) // 2, 50))

        texto_pontos_final = fonte.render(f"Pontuacao Final: {pontos}", True, BRANCO)
        tela.blit(texto_pontos_final, ((LARGURA - texto_pontos_final.get_width()) // 2, 105))

        botao(tela, botao_jogar, "Jogar Novamente", AZUL_BOTAO, AZUL_BOTAO_HOVER, mouse_pos)
        botao(tela, botao_sair, "Voltar ao Menu", VERMELHO_BOTAO, VERMELHO_BOTAO_HOVER, mouse_pos)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()