# ***********************************************************************************
#   ExibePoligonos.py
#       Autor: Márcio Sarroglia Pinho
#       pinho@pucrs.br
#   Este programa cria um conjunto de INSTANCIAS
#   Para construir este programa, foi utilizada a biblioteca PyOpenGL, disponível em
#   http://pyopengl.sourceforge.net/documentation/index.html
#
#   Sugere-se consultar também as páginas listadas
#   a seguir:
#   http://bazaar.launchpad.net/~mcfletch/pyopengl-demo/trunk/view/head:/PyOpenGL-Demo/NeHe/lesson1.py
#   http://pyopengl.sourceforge.net/documentation/manual-3.0/index.html#GLUT
#
#   No caso de usar no MacOS, pode ser necessário alterar o arquivo ctypesloader.py,
#   conforme a descrição que está nestes links:
#   https://stackoverflow.com/questions/63475461/unable-to-import-opengl-gl-in-python-on-macos
#   https://stackoverflow.com/questions/6819661/python-location-on-mac-osx
#   Veja o arquivo Patch.rtf, armazenado na mesma pasta deste fonte.
# ***********************************************************************************

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from Poligonos import *
from Instancia import *
from ModeloMatricial import *
from ListaDeCoresRGB import *
from datetime import datetime
import time
import random

# ***********************************************************************************
# Limites da Janela de Seleção
Min = Ponto()
Max = Ponto()

# lista de instancias do Personagens
Personagens = [Instancia() for x in range(200)]
Vidas = 3
Inimigos = 5
UltimoInimigo = -1

AREA_DE_BACKUP = 100 # posicao a partir da qual sao armazenados backups dos personagens

# lista de modelos
Modelos = []

angulo = 0.0
PersonagemAtual = -1
nInstancias = 0

imprimeEnvelope = False

LarguraDoUniverso = 10.0

TempoInicial = time.time()
TempoTotal = time.time()
TempoAnterior = time.time()

# define uma funcao de limpeza de tela
from os import system, name
def clear():
 
    # for windows
    if name == 'nt':
        _ = system('cls')
 
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')
        print("*******************")
        print ("PWD: ", os.getcwd()) 
        
def DesenhaLinha (P1, P2):
    glBegin(GL_LINES)
    glVertex3f(P1.x,P1.y,P1.z)
    glVertex3f(P2.x,P2.y,P2.z)
    glEnd()

# ****************************************************************
def RotacionaAoRedorDeUmPonto(alfa: float, P: Ponto):
    glTranslatef(P.x, P.y, P.z)
    glRotatef(alfa, 0,0,1)
    glTranslatef(-P.x, -P.y, -P.z)

# ***********************************************************************************
def reshape(w,h):

    global Min, Max
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # Cria uma folga na Janela de Selecão, com 10% das dimensoes do poligono
    BordaX = abs(Max.x-Min.x)*0.1
    BordaY = abs(Max.y-Min.y)*0.1
    #glOrtho(Min.x-BordaX, Max.x+BordaX, Min.y-BordaY, Max.y+BordaY, 0.0, 1.0)
    glOrtho(Min.x, Max.x, Min.y, Max.y, 0.0, 1.0)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity()

# **************************************************************
def DesenhaEixos():
    global Min, Max

    Meio = Ponto(); 
    Meio.x = (Max.x+Min.x)/2
    Meio.y = (Max.y+Min.y)/2
    Meio.z = (Max.z+Min.z)/2

    glBegin(GL_LINES)
    #  eixo horizontal
    glVertex2f(Min.x,Meio.y)
    glVertex2f(Max.x,Meio.y)
    #  eixo vertical
    glVertex2f(Meio.x,Min.y)
    glVertex2f(Meio.x,Max.y)
    glEnd()

# ***********************************************************************************
def TestaColisao(P1, P2) -> bool :

    # cout << "\n-----\n" << endl;
    # Personagens[Objeto1].ImprimeEnvelope("Envelope 1: ", "\n");
    # Personagens[Objeto2].ImprimeEnvelope("\nEnvelope 2: ", "\n");
    # cout << endl;

    # Testa todas as arestas do envelope de
    # um objeto contra as arestas do outro
       
    for i in range(4):
        A = Personagens[P1].Envelope[i]
        B = Personagens[P1].Envelope[(i+1)%4]
        for j in range(4):
            # print ("Testando ", i," contra ",j)
            # Personagens[Objeto1].ImprimeEnvelope("\nEnvelope 1: ", "\n");
            # Personagens[Objeto2].ImprimeEnvelope("Envelope 2: ", "\n");
            C = Personagens[P2].Envelope[j]
            D = Personagens[P2].Envelope[(j+1)%4]
            # A.imprime("A:","\n");
            # B.imprime("B:","\n");
            # C.imprime("C:","\n");
            # D.imprime("D:","\n\n");    
            if HaInterseccao(A, B, C, D):
                return True
    return False

# ***********************************************************************************
def AtualizaEnvelope(i):
    global Personagens
    id = Personagens[i].IdDoModelo
    MM = Modelos[id]

    P = Personagens[i]
    V = P.Direcao * (MM.nColunas/2.0)
    V.rotacionaZ(90)
    A = P.PosicaoDoPersonagem + V
    B = A + P.Direcao* MM.nLinhas
    
    V = P.Direcao * MM.nColunas
    V.rotacionaZ(-90)
    C = B + V

    V = P.Direcao * -1 * MM.nLinhas
    D = C + V

    # Desenha o envelope
    # SetColor(Red)
    # glBegin(GL_LINE_LOOP)
    # glVertex2f(A.x, A.y)
    # glVertex2f(B.x, B.y)
    # glVertex2f(C.x, C.y)
    # glVertex2f(D.x, D.y)
    # glEnd()
    # if (imprimeEnvelope):
    #     A.imprime("A:");
    #     B.imprime("B:");
    #     C.imprime("C:");
    #     D.imprime("D:");
    #     print("");

    Personagens[i].Envelope[0] = A
    Personagens[i].Envelope[1] = B
    Personagens[i].Envelope[2] = C
    Personagens[i].Envelope[3] = D

# ***********************************************************************************
# Gera sempre uma posicao na metade de baixo da tela
def GeraPosicaoAleatoria():
        x = random.randint(-LarguraDoUniverso, LarguraDoUniverso)
        y = random.randint(-LarguraDoUniverso, 0)
        return Ponto (x,y)

def RemoveVidaHud():
    global nInstancias
    for i in range(0, nInstancias):
        if Personagens[i].Decoracao: # remove uma vida do hud
            Personagens.pop(i)
            nInstancias = nInstancias - 1
            Personagens.insert(99, Instancia())
            # if Vidas <= 0:
            #     print("Voce Perdeu")
            break

# ***********************************************************************************
def AtualizaJogo():
    global imprimeEnvelope, nInstancias, Personagens, LarguraDoUniverso, Vidas, Inimigos, UltimoInimigo
    #  Esta funcao deverá atualizar todos os elementos do jogo
    #  em funcao das novas posicoes dos personagens
    #  Entre outras coisas, deve-se:
    
    #   - calcular colisões
    #  Para calcular as colisoes eh preciso fazer o calculo do envelopes de
    #  todos os personagens

    for i in range (0, nInstancias):
        AtualizaEnvelope(i) 
        if (imprimeEnvelope): # pressione E para alterar esta flag
            # print("Envelope ", i)
            Personagens[i].ImprimeEnvelope("","")
    imprimeEnvelope = False
    
    if Inimigos == 0:
        print("Voce Ganhou")
        os._exit(0)
        
    if Vidas <= 0:
        print("Voce Perdeu")
        os._exit(0)
    
    print(Vidas)
        
    # Testa a colisao do personagem principal com todos os outros objetos
    for i in range(1,nInstancias):
        if TestaColisao(0, i):
            if Personagens[i].Decoracao: # se for uma decoracao nao colide
                continue
            
            if Personagens[i].Projetil:
                if UltimoInimigo != Personagens[i].QuemAtirou:
                    UltimoInimigo = Personagens[i].QuemAtirou
                    Vidas -= 1
                    RemoveVidaHud()
            else: ## se for um inimigo colidindo com a nave
                if UltimoInimigo != Personagens[i].IdDoModelo:
                    print("last enemy", UltimoInimigo)
                    UltimoInimigo = Personagens[i].IdDoModelo
                    Vidas -= 1
                    RemoveVidaHud()
                
            Personagens.pop(i)
            Personagens.insert(99, Instancia())
            nInstancias = nInstancias - 1    
    
    # npc's atiram no personagem
    for i in range(1, nInstancias):
        if Personagens[i].Projetil or Personagens[i].Decoracao: # se for um projetil ou vida nao atira
            continue
            
        if random.randint(1, 300) == 5: # ganbiarra só para que o tiro das naves sejam aleatórios
            for j in range(random.randint(1, 10)):
                direcao = (Personagens[0].Posicao - Personagens[i].Posicao) 
                comprimento = math.sqrt(direcao.x ** 2 + direcao.y ** 2) # normalizando o vetor de direção
                if comprimento != 0:
                    direcao.x /= comprimento
                    direcao.y /= comprimento
                atirar(i, direcao, 10)
                
    # Testa tiros do jogador 
    for i in range (1, nInstancias - 1):
        if Personagens[i].Projetil or Personagens[i].Decoracao: # se for um projetil ou uma decoracao nao precisa testar
            continue
        for j in range (i + 1, nInstancias):
            if TestaColisao(i, j):
                if Personagens[j].Projetil and Personagens[j].QuemAtirou == i: # tiro nao pode colidir com o personagem que está atirando
                    continue
                if Personagens[j].QuemAtirou == 0:
                    Personagens.pop(i)
                    Personagens.insert(99, Instancia())
                    nInstancias = nInstancias - 1
                    Inimigos -= 1
            
    # impede que as naves saiam pra fora            
    for i, personagem in enumerate(Personagens[0:nInstancias]):
        if personagem.Projetil:
            estaFora = EstaForaDoUniverso(personagem.Posicao)
            if estaFora:
                Personagens.pop(i)
                Personagens.insert(AREA_DE_BACKUP, Instancia())
                nInstancias = nInstancias - 1
                if (Personagens[personagem.QuemAtirou].Ativos - 1) >= 0:
                    Personagens[personagem.QuemAtirou].Ativos -= 1
            continue

        # Verifica e ajusta a posição horizontal
        if personagem.Posicao.x > LarguraDoUniverso:
            personagem.Posicao.x = -LarguraDoUniverso
        elif personagem.Posicao.x < -LarguraDoUniverso:
            personagem.Posicao.x = LarguraDoUniverso

        # Verifica e ajusta a posição vertical
        if personagem.Posicao.y > LarguraDoUniverso:
            personagem.Posicao.y = -LarguraDoUniverso
        elif personagem.Posicao.y < -LarguraDoUniverso:
            personagem.Posicao.y = LarguraDoUniverso

# ***********************************************************************************
def EstaForaDoUniverso(posicao):
    global LarguraDoUniverso
    return posicao.x > LarguraDoUniverso or posicao.x < -LarguraDoUniverso or posicao.y > LarguraDoUniverso or posicao.y < -LarguraDoUniverso
# ***********************************************************************************
def AtualizaPersonagens(tempoDecorrido):
    global nInstancias
    for i in range (0, nInstancias):
        Personagens[i].AtualizaPosicao(tempoDecorrido) #(tempoDecorrido)
    AtualizaJogo()

# ***********************************************************************************
def DesenhaPersonagens():
    global PersonagemAtual, nInstancias
    
    for i in range (0, nInstancias):
        PersonagemAtual = i
        Personagens[i].Desenha()
        
# ***********************************************************************************
def display():
    global TempoInicial, TempoTotal, TempoAnterior

    TempoAtual = time.time()

    TempoTotal =  TempoAtual - TempoInicial

    DiferencaDeTempo = TempoAtual - TempoAnterior

	# Limpa a tela coma cor de fundo
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    #glLineWidth(3)
    # glColor3f(1,1,1) # R, G, B  [0..1]
    # DesenhaEixos()

    DesenhaPersonagens()
    AtualizaPersonagens(DiferencaDeTempo)
    
    glutSwapBuffers()
    TempoAnterior = TempoAtual
    
def atirar(personagem_index, direcao, velocidade):
    global nInstancias
    
    personagem = Personagens[personagem_index]
    
    if personagem.Ativos >= 10:
        return
    
    projetil = Personagens[nInstancias]
    
    personagem.Centro = ((personagem.Envelope[1] + personagem.Envelope[2]) * 0.5)
    personagem.Ativos += 1
    projetil.Escala = Ponto(1,1)
    projetil.Direcao = direcao
    projetil.Posicao = personagem.Centro + personagem.Direcao * 0.8
    projetil.Rotacao = personagem.Rotacao
    projetil.IdDoModelo = 1
    projetil.Modelo = DesenhaPersonagemMatricial
    projetil.Pivot = CalculaPivot(1)
    projetil.Velocidade = velocidade + personagem.Velocidade
    projetil.Projetil = True
    projetil.QuemAtirou = personagem_index
    nInstancias = nInstancias + 1

# ***********************************************************************************
# The function called whenever a key is pressed. 
# Note the use of Python tuples to pass in: (key, x, y)
#ESCAPE = '\033'
ESCAPE = b'\x1b'
def keyboard(*args):
    global imprimeEnvelope
    print (args)
    # If escape is pressed, kill everything.
    if args[0] == b'q':
        os._exit(0)
    if args[0] == b' ':
        atirar(0, copy.deepcopy(Personagens[0].Direcao), 80)
    if args[0] == ESCAPE:
        os._exit(0)
    if args[0] == b'e':
        imprimeEnvelope = True
# Forca o redesenho da tela
    glutPostRedisplay()

# **********************************************************************
#  arrow_keys ( a_keys: int, x: int, y: int )   
# **********************************************************************
def arrow_keys(a_keys: int, x: int, y: int):
    if a_keys == GLUT_KEY_UP:         # Se pressionar UP
        if (Personagens[0].Velocidade + 1) < 80:
            Personagens[0].Velocidade = Personagens[0].Velocidade + 1
    if a_keys == GLUT_KEY_DOWN:       # Se pressionar DOWN
        if (Personagens[0].Velocidade - 1) > -80:
            Personagens[0].Velocidade = Personagens[0].Velocidade - 1 
    if a_keys == GLUT_KEY_LEFT:       # Se pressionar LEFT
        Personagens[0].Rotacao += 5
        Personagens[0].Direcao.rotacionaZ(+5)
    if a_keys == GLUT_KEY_RIGHT:      # Se pressionar RIGHT
        Personagens[0].Rotacao -= 5
        Personagens[0].Direcao.rotacionaZ(-5)
    glutPostRedisplay()

# ***********************************************************************************
#
# ***********************************************************************************
def mouse(button: int, state: int, x: int, y: int):
    global PontoClicado
    if (state != GLUT_DOWN): 
        return
    if (button != GLUT_RIGHT_BUTTON):
        return
    #print ("Mouse:", x, ",", y)
    # Converte a coordenada de tela para o sistema de coordenadas do 
    # Personagens definido pela glOrtho
    vport = glGetIntegerv(GL_VIEWPORT)
    mvmatrix = glGetDoublev(GL_MODELVIEW_MATRIX)
    projmatrix = glGetDoublev(GL_PROJECTION_MATRIX)
    realY = vport[3] - y
    worldCoordinate1 = gluUnProject(x, realY, 0, mvmatrix, projmatrix, vport)

    PontoClicado = Ponto (worldCoordinate1[0],worldCoordinate1[1], worldCoordinate1[2])
    PontoClicado.imprime("Ponto Clicado:")

    glutPostRedisplay()

# ***********************************************************************************
def mouseMove(x: int, y: int):
    #glutPostRedisplay()
    return

# ***********************************************************************************
def CarregaModelos():
    Modelos.append(ModeloMatricial())
    Modelos[0].leModelo("Disparador.txt")
    Modelos.append(ModeloMatricial())
    Modelos[1].leModelo("MatrizProjetil.txt")
    Modelos.append(ModeloMatricial())
    Modelos[2].leModelo("Inimigo1.txt")
    Modelos.append(ModeloMatricial())
    Modelos[3].leModelo("Inimigo2.txt")
    Modelos.append(ModeloMatricial())
    Modelos[4].leModelo("Inimigo3.txt")
    Modelos.append(ModeloMatricial())
    Modelos[5].leModelo("Inimigo4.txt")
    Modelos.append(ModeloMatricial())
    Modelos[6].leModelo("CoracaoCheio.txt")
    Modelos.append(ModeloMatricial())
    Modelos[7].leModelo("CoracaoVazio.txt")
    
    for index, modelo in enumerate(Modelos):
        # print(f'Modelo {index}')
        modelo.Imprime()

def DesenhaCelula():
    glBegin(GL_QUADS)
    glVertex2f(0,0)
    glVertex2f(0,1)
    glVertex2f(1,1)
    glVertex2f(1,0)
    glEnd()

def DesenhaBorda():
    glBegin(GL_LINE_LOOP)
    glVertex2f(0,0)
    glVertex2f(0,1)
    glVertex2f(1,1)
    glVertex2f(1,0)
    glEnd()

# ***********************************************************************************
def DesenhaPersonagemMatricial():
    global PersonagemAtual, count

    MM = ModeloMatricial()
    
    ModeloDoPersonagem = Personagens[PersonagemAtual].IdDoModelo
        
    MM = Modelos[ModeloDoPersonagem]
    # MM.Imprime("Matriz:")
      
    glPushMatrix()
    larg = MM.nColunas
    alt = MM.nLinhas
    # print (alt, " LINHAS e ", larg, " COLUNAS")
    for i in range(alt):
        glPushMatrix()
        for j in range(larg):
            cor = MM.getColor(alt-1-i,j)
            if cor != -1: # nao desenha celulas com -1 (transparentes)
                SetColor(cor)
                DesenhaCelula()
                SetColor(Wheat)
                # DesenhaBorda()
            glTranslatef(1, 0, 0)
        glPopMatrix()
        glTranslatef(0, 1, 0)
    glPopMatrix()



# ***********************************************************************************
# Esta função deve instanciar todos os personagens do cenário
# ***********************************************************************************
def CriaInstancias():
    global Personagens, nInstancias

    i = 0
    ang = 0
    #Personagens.append(Instancia())
    Personagens[i].Posicao = Ponto (0,0)
    Personagens[i].Escala = Ponto (1, 1)
    Personagens[i].Rotacao = ang
    Personagens[i].IdDoModelo = 0
    Personagens[i].Modelo = DesenhaPersonagemMatricial
    Personagens[i].Pivot = CalculaPivot(Personagens[i].IdDoModelo)
    Personagens[i].Direcao = Ponto(0,1) # direcao do movimento para a cima
    Personagens[i].Direcao.rotacionaZ(ang) # direcao alterada para a direita
    Personagens[i].Velocidade = 0 # move-se a 5 m/s

    # Salva os dados iniciais do personagem i na area de backup
    Personagens[i+AREA_DE_BACKUP] = copy.deepcopy(Personagens[i]) 
    
    padding = 15
    x_inicial = -120
    for i in range(Vidas):
        x_inicial += padding
        # vida
        i = i + 1
        ang = 0
        Personagens[i].Posicao = Ponto (x_inicial, 100)
        Personagens[i].Escala = Ponto (1, 1)
        Personagens[i].Rotacao = ang
        Personagens[i].IdDoModelo = 6
        Personagens[i].Modelo = DesenhaPersonagemMatricial
        Personagens[i].Pivot = CalculaPivot(Personagens[i].IdDoModelo)
        Personagens[i].Direcao = Ponto(0,1) # direcao do movimento para a cima
        Personagens[i].Direcao.rotacionaZ(ang) # direcao alterada para a direita
        Personagens[i].Velocidade = 0 # move-se a 5 m/s
        Personagens[i].Decoracao = True
        Personagens[i+AREA_DE_BACKUP] = copy.deepcopy(Personagens[i]) 
    
    modelos_inimigos = [2,3,4,5]
    
    ## Inimigos
    for j in range(Inimigos):
        i = i + 1
        ang = random.randint(0, 360)
        Personagens[i].Posicao = Ponto(random.randint(-125, 125), random.randint(-125, 0))
        Personagens[i].Escala = Ponto (1,1)
        Personagens[i].Rotacao = ang
        Personagens[i].IdDoModelo = modelos_inimigos[i % 4]
        Personagens[i].Modelo = DesenhaPersonagemMatricial
        Personagens[i].Pivot = CalculaPivot(Personagens[i].IdDoModelo)
        Personagens[i].Direcao = Ponto(0,1) # direcao do movimento para a cima
        Personagens[i].Direcao.rotacionaZ(ang) # direcao alterada para a direita
        Personagens[i].Velocidade = 4   # move-se a 3 m/s

    nInstancias = i+1

def CalculaPivot(nroModelo):
    global Modelos
    MM = Modelos[nroModelo]
    return Ponto (MM.nColunas/2.0, 0) # pode ter um bug aqui pq nao mexi na escala
    
# ***********************************************************************************
def init():
    global Min, Max
    global TempoInicial, LarguraDoUniverso
    # Define a cor do fundo da tela (AZUL)
    glClearColor(0, 0, 0, 0)
    
    clear() # limpa o console
    CarregaModelos()
    CriaInstancias()

    LarguraDoUniverso = 125
    Min = Ponto(-LarguraDoUniverso,-LarguraDoUniverso)
    Max = Ponto(LarguraDoUniverso,LarguraDoUniverso)

    TempoInicial = time.time()
    print("Inicio: ", datetime.now())
    print("TempoInicial", TempoInicial)

def animate():
    global angulo
    angulo = angulo + 1
    glutPostRedisplay()

# ***********************************************************************************
# Programa Principal
# ***********************************************************************************

glutInit(sys.argv)
glutInitDisplayMode(GLUT_RGBA)
# Define o tamanho inicial da janela grafica do programa
glutInitWindowSize(1200, 1200)
glutInitWindowPosition(150, 150)
wind = glutCreateWindow("Asteroids")
glutDisplayFunc(display)
glutIdleFunc(animate)
glutReshapeFunc(reshape)
glutKeyboardFunc(keyboard)
glutSpecialFunc(arrow_keys)
glutMouseFunc(mouse)
init()

try:
    glutMainLoop()
except SystemExit:
    pass
