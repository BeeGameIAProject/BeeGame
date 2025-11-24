"""
Interfaz Gráfica Simple (GUI) para el juego BeeGame
MVP7: Implementación con Pygame
"""

import pygame
import sys
from board import Board
from bee import Bee
from humanidad import Humanidad
from chance_events import ChanceEvents
from expectimax import ExpectimaxAI
from heuristica import Heuristica
from game_manager import GameManager

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
GRIS = (200, 200, 200)
GRIS_OSCURO = (100, 100, 100)
VERDE = (0, 200, 0)
VERDE_OSCURO = (0, 150, 0)
ROJO = (255, 0, 0)
AMARILLO = (255, 255, 0)
AZUL = (0, 150, 255)
NARANJA = (255, 165, 0)
MARRON = (139, 69, 19)
ROSA = (255, 182, 193)
MORADO = (200, 100, 200)

class BeeGameGUI:
    def __init__(self, filas=8, columnas=8, nectar_objetivo=50):
        pygame.init()
        
        # Configuración de la ventana
        self.CELL_SIZE = 70
        self.PANEL_WIDTH = 300
        self.BOARD_WIDTH = columnas * self.CELL_SIZE
        self.BOARD_HEIGHT = filas * self.CELL_SIZE
        self.WINDOW_WIDTH = self.BOARD_WIDTH + self.PANEL_WIDTH
        self.WINDOW_HEIGHT = self.BOARD_HEIGHT + 100
        
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("🐝 BeeGame - Proyecto IA")
        
        # Fuentes
        self.font_title = pygame.font.Font(None, 32)
        self.font_normal = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)
        
        # Inicializar componentes del juego
        self.board = Board(filas, columnas)
        self.board.inicializar_tablero(num_flores=12, num_obstaculos=2)
        
        self.abeja = Bee(life=100)
        self.pos_abeja = (self.board.rusc_pos[0] - 1, self.board.rusc_pos[1])
        
        self.humanidad_agente = Humanidad()
        self.eventos_azar = ChanceEvents()
        self.heuristica = Heuristica(w1=10, w2=8, w3=15, w4=5, w5=3, w6=2, w7=1)
        self.ai = ExpectimaxAI(max_depth=2, heuristica=self.heuristica)
        self.game_manager = GameManager(nectar_objetivo=nectar_objetivo)
        
        # Variables de control
        self.turno = 0
        self.mensaje = "Haz click en una celda para mover la abeja"
        self.clima_actual = "Normal"
        self.game_over = False
        self.resultado = None
        self.celda_seleccionada = None
        
        # Botones
        self.botones = self.crear_botones()
        
        # Clock para FPS
        self.clock = pygame.time.Clock()
        
    def crear_botones(self):
        """Crea los botones de la interfaz"""
        y_start = self.BOARD_HEIGHT + 10
        botones = {
            'recoger': pygame.Rect(10, y_start, 110, 40),
            'descansar': pygame.Rect(130, y_start, 110, 40),
            'a_star': pygame.Rect(250, y_start, 140, 40),
            'descargar': pygame.Rect(400, y_start, 110, 40),
            'siguiente': pygame.Rect(self.BOARD_WIDTH - 200, y_start, 180, 50),
        }
        return botones
    
    def dibujar_celda(self, fila, col, x, y):
        """Dibuja una celda individual del tablero"""
        # Fondo de la celda
        pygame.draw.rect(self.screen, VERDE, (x, y, self.CELL_SIZE, self.CELL_SIZE))
        pygame.draw.rect(self.screen, NEGRO, (x, y, self.CELL_SIZE, self.CELL_SIZE), 2)
        
        # Contenido de la celda
        celda = self.board.grid[fila][col]
        
        # Dibujar elementos
        if celda == 'RUSC':  # Rusc
            pygame.draw.circle(self.screen, AMARILLO, 
                             (x + self.CELL_SIZE//2, y + self.CELL_SIZE//2), 
                             self.CELL_SIZE//3)
            texto = self.font_small.render("RUSC", True, NEGRO)
            self.screen.blit(texto, (x + 12, y + self.CELL_SIZE//2 - 8))
            
        elif celda == 'OBSTACULO':  # Obstáculo
            pygame.draw.rect(self.screen, GRIS_OSCURO, 
                           (x + 10, y + 10, self.CELL_SIZE - 20, self.CELL_SIZE - 20))
            
        elif self.board.es_flor(fila, col):  # Flor
            flor = self.board.get_celda(fila, col)
            if flor.vida > 0:
                # Color según estado
                if flor.pesticidas >= 2:
                    color_flor = MORADO  # Muy contaminada
                elif flor.pesticidas >= 1:
                    color_flor = ROSA  # Contaminada
                else:
                    color_flor = AMARILLO if flor.polinizacion == 0 else NARANJA
                
                # Dibujar flor
                pygame.draw.circle(self.screen, color_flor,
                                 (x + self.CELL_SIZE//2, y + self.CELL_SIZE//2),
                                 self.CELL_SIZE//4)
                
                # Indicadores
                if flor.polinizacion == 1:
                    texto = self.font_small.render("P", True, VERDE_OSCURO)
                    self.screen.blit(texto, (x + self.CELL_SIZE - 18, y + 5))
                    
                if flor.pesticidas > 0:
                    texto = self.font_small.render(f"x{flor.pesticidas}", True, ROJO)
                    self.screen.blit(texto, (x + 5, y + 5))
            else:
                # Flor muerta
                pygame.draw.line(self.screen, MARRON, (x + 20, y + 20), 
                               (x + self.CELL_SIZE - 20, y + self.CELL_SIZE - 20), 3)
                pygame.draw.line(self.screen, MARRON, (x + self.CELL_SIZE - 20, y + 20), 
                               (x + 20, y + self.CELL_SIZE - 20), 3)
        
        # Dibujar abeja si está en esta posición
        if (fila, col) == self.pos_abeja:
            pygame.draw.circle(self.screen, AZUL,
                             (x + self.CELL_SIZE//2, y + self.CELL_SIZE//2),
                             self.CELL_SIZE//5)
            pygame.draw.circle(self.screen, AMARILLO,
                             (x + self.CELL_SIZE//2, y + self.CELL_SIZE//2),
                             self.CELL_SIZE//6)
        
        # Resaltar celda seleccionada
        if self.celda_seleccionada == (fila, col):
            pygame.draw.rect(self.screen, AZUL, (x, y, self.CELL_SIZE, self.CELL_SIZE), 4)
    
    def dibujar_tablero(self):
        """Dibuja todo el tablero"""
        for fila in range(self.board.filas):
            for col in range(self.board.columnas):
                x = col * self.CELL_SIZE
                y = fila * self.CELL_SIZE
                self.dibujar_celda(fila, col, x, y)
    
    def dibujar_panel_info(self):
        """Dibuja el panel de información lateral"""
        x_panel = self.BOARD_WIDTH + 10
        y_offset = 10
        
        # Título
        texto = self.font_title.render("BeeGame", True, NEGRO)
        self.screen.blit(texto, (x_panel + 60, y_offset))
        y_offset += 40
        
        # Turno
        texto = self.font_normal.render(f"Turno: {self.turno}", True, NEGRO)
        self.screen.blit(texto, (x_panel, y_offset))
        y_offset += 40
        
        # --- Estado de la Abeja ---
        texto = self.font_normal.render("ABEJA", True, AZUL)
        self.screen.blit(texto, (x_panel, y_offset))
        y_offset += 30
        
        # Barra de vida
        self.dibujar_barra(x_panel, y_offset, 250, 20, self.abeja.life, self.abeja.max_vida, ROJO, "Vida")
        y_offset += 30
        
        # Barra de energía
        self.dibujar_barra(x_panel, y_offset, 250, 20, self.abeja.energia, self.abeja.max_energia, AZUL, "Energía")
        y_offset += 30
        
        # Néctar cargado
        texto = self.font_small.render(f"Néctar: {self.abeja.nectar_cargado}/{self.abeja.capacidad_nectar}", True, NEGRO)
        self.screen.blit(texto, (x_panel, y_offset))
        y_offset += 40
        
        # --- Progreso ---
        texto = self.font_normal.render("PROGRESO", True, NARANJA)
        self.screen.blit(texto, (x_panel, y_offset))
        y_offset += 30
        
        objetivo = self.game_manager.nectar_objetivo
        actual = self.board.nectar_en_rusc
        self.dibujar_barra(x_panel, y_offset, 250, 25, actual, objetivo, NARANJA, 
                          f"Rusc: {actual}/{objetivo}")
        y_offset += 40
        
        # --- Flores ---
        flores_vivas = sum(1 for _, f in self.board.flores if f.vida > 0)
        texto = self.font_small.render(f"Flores: {flores_vivas}/{len(self.board.flores)}", 
                                      True, VERDE_OSCURO)
        self.screen.blit(texto, (x_panel, y_offset))
        y_offset += 30
        
        # --- Clima ---
        color_clima = AZUL if self.clima_actual == "Lluvia" else (AMARILLO if self.clima_actual == "Sol" else GRIS_OSCURO)
        texto = self.font_small.render(f"Clima: {self.clima_actual}", True, color_clima)
        self.screen.blit(texto, (x_panel, y_offset))
        y_offset += 50
        
        # --- Mensaje ---
        palabras = self.mensaje.split()
        linea_actual = ""
        for palabra in palabras:
            test_linea = linea_actual + palabra + " "
            if len(test_linea) > 25:
                texto = self.font_small.render(linea_actual, True, NEGRO)
                self.screen.blit(texto, (x_panel, y_offset))
                y_offset += 22
                linea_actual = palabra + " "
            else:
                linea_actual = test_linea
        if linea_actual:
            texto = self.font_small.render(linea_actual, True, NEGRO)
            self.screen.blit(texto, (x_panel, y_offset))
    
    def dibujar_barra(self, x, y, ancho, alto, valor_actual, valor_max, color, etiqueta=""):
        """Dibuja una barra de progreso"""
        # Fondo
        pygame.draw.rect(self.screen, GRIS, (x, y, ancho, alto))
        
        # Progreso
        if valor_max > 0:
            progreso = min(valor_actual / valor_max, 1.0)
            pygame.draw.rect(self.screen, color, (x, y, ancho * progreso, alto))
        
        # Borde
        pygame.draw.rect(self.screen, NEGRO, (x, y, ancho, alto), 2)
        
        # Etiqueta
        if etiqueta:
            texto = self.font_small.render(etiqueta, True, NEGRO)
            self.screen.blit(texto, (x, y - 18))
    
    def dibujar_botones(self):
        """Dibuja los botones de control"""
        # Recoger néctar
        color = VERDE if not self.game_over else GRIS
        pygame.draw.rect(self.screen, color, self.botones['recoger'])
        pygame.draw.rect(self.screen, NEGRO, self.botones['recoger'], 2)
        texto = self.font_small.render("Recoger", True, NEGRO)
        self.screen.blit(texto, (self.botones['recoger'].x + 20, self.botones['recoger'].y + 10))
        
        # Descansar
        pygame.draw.rect(self.screen, color, self.botones['descansar'])
        pygame.draw.rect(self.screen, NEGRO, self.botones['descansar'], 2)
        texto = self.font_small.render("Descansar", True, NEGRO)
        self.screen.blit(texto, (self.botones['descansar'].x + 15, self.botones['descansar'].y + 10))
        
        # A* al rusc
        pygame.draw.rect(self.screen, AZUL if not self.game_over else GRIS, self.botones['a_star'])
        pygame.draw.rect(self.screen, NEGRO, self.botones['a_star'], 2)
        texto = self.font_small.render("A* al Rusc", True, BLANCO)
        self.screen.blit(texto, (self.botones['a_star'].x + 25, self.botones['a_star'].y + 10))
        
        # Descargar néctar
        pygame.draw.rect(self.screen, NARANJA if not self.game_over else GRIS, self.botones['descargar'])
        pygame.draw.rect(self.screen, NEGRO, self.botones['descargar'], 2)
        texto = self.font_small.render("Descargar", True, NEGRO)
        self.screen.blit(texto, (self.botones['descargar'].x + 15, self.botones['descargar'].y + 10))
        
        # Siguiente turno (Humanidad)
        color = ROJO if not self.game_over else GRIS
        pygame.draw.rect(self.screen, color, self.botones['siguiente'])
        pygame.draw.rect(self.screen, NEGRO, self.botones['siguiente'], 3)
        texto_btn = "TURNO HUMANIDAD" if not self.game_over else "GAME OVER"
        texto = self.font_normal.render(texto_btn, True, BLANCO)
        self.screen.blit(texto, (self.botones['siguiente'].x + 10, self.botones['siguiente'].y + 12))
    
    def dibujar_game_over(self):
        """Dibuja pantalla de game over"""
        # Overlay semi-transparente
        overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(NEGRO)
        self.screen.blit(overlay, (0, 0))
        
        # Texto principal
        if self.resultado == "VICTORIA":
            texto = self.font_title.render("VICTORIA!", True, AMARILLO)
        else:
            texto = self.font_title.render("DERROTA", True, ROJO)
        
        rect_texto = texto.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 - 50))
        self.screen.blit(texto, rect_texto)
        
        # Detalles
        detalles = [
            f"Turnos: {self.turno}",
            f"Nectar: {self.board.nectar_en_rusc}/{self.game_manager.nectar_objetivo}",
            f"Flores vivas: {sum(1 for _, f in self.board.flores if f.vida > 0)}",
        ]
        
        y_offset = self.WINDOW_HEIGHT // 2
        for detalle in detalles:
            texto = self.font_normal.render(detalle, True, BLANCO)
            rect_texto = texto.get_rect(center=(self.WINDOW_WIDTH // 2, y_offset))
            self.screen.blit(texto, rect_texto)
            y_offset += 30
        
        # Instrucciones
        texto = self.font_small.render("Presiona ESC para salir", True, GRIS)
        rect_texto = texto.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT - 30))
        self.screen.blit(texto, rect_texto)
    
    def obtener_celda_click(self, pos):
        """Convierte posición de click a coordenadas de celda"""
        x, y = pos
        if x < self.BOARD_WIDTH and y < self.BOARD_HEIGHT:
            col = x // self.CELL_SIZE
            fila = y // self.CELL_SIZE
            return (fila, col)
        return None
    
    def mover_abeja(self, destino):
        """Mueve la abeja a una celda destino"""
        if self.game_over:
            return False
        
        fila, col = destino
        
        # Verificar si es el rusc o celda vacía
        celda = self.board.grid[fila][col]
        if celda in [None, 'RUSC']:
            if self.abeja.mover(self.board, self.pos_abeja, destino):
                self.pos_abeja = destino
                self.mensaje = f"Abeja movida a ({fila}, {col})"
                
                # Si llega al rusc, recuperar energía
                if self.board.es_rusc(fila, col):
                    self.abeja.recuperar_energia_en_rusc(self.board, self.pos_abeja)
                    self.mensaje += " | Energia recuperada en el rusc"
                
                return True
            else:
                self.mensaje = "No hay suficiente energia para mover"
        else:
            self.mensaje = "Esa casilla no es transitable"
        return False
    
    def recoger_nectar(self):
        """Intenta recoger néctar de una flor adyacente"""
        if self.game_over or not self.celda_seleccionada:
            return False
        
        fila, col = self.celda_seleccionada
        
        # Verificar si es una flor
        if self.board.es_flor(fila, col):
            # Verificar si está adyacente
            df = abs(self.pos_abeja[0] - fila)
            dc = abs(self.pos_abeja[1] - col)
            
            if df <= 1 and dc <= 1:
                if self.abeja.recoger_nectar_y_polinizar(self.board, (fila, col)):
                    self.mensaje = f"Nectar recolectado! ({self.abeja.nectar_cargado}/{self.abeja.capacidad_nectar})"
                    return True
                else:
                    self.mensaje = "No se puede recoger de esa flor"
            else:
                self.mensaje = "Debes estar adyacente a la flor"
        else:
            self.mensaje = "Selecciona una flor primero"
        return False
    
    def accion_descansar(self):
        """La abeja descansa para recuperar energía"""
        if self.game_over:
            return False
        
        self.abeja.descansar()
        self.mensaje = f"Descansando... Energia: {self.abeja.energia}/{self.abeja.max_energia}"
        return True
    
    def accion_a_star(self):
        """Mueve la abeja un paso hacia el rusc usando A*"""
        if self.game_over:
            return False
        
        ruta = self.abeja.calcular_ruta_a_rusc(self.board, self.pos_abeja)
        
        if ruta and len(ruta) > 1:
            siguiente = ruta[1]
            if self.abeja.mover(self.board, self.pos_abeja, siguiente):
                self.pos_abeja = siguiente
                self.mensaje = f"A*: Moviendo hacia rusc ({len(ruta)-1} pasos restantes)"
                
                # Si llegó al rusc, recuperar energía
                if self.board.es_rusc(siguiente[0], siguiente[1]):
                    self.abeja.recuperar_energia_en_rusc(self.board, self.pos_abeja)
                    self.mensaje += " | Energia recuperada"
                
                return True
            else:
                self.mensaje = "No hay suficiente energia"
        else:
            self.mensaje = "Ya estas en el rusc"
        return False
    
    def accion_descargar(self):
        """Descarga néctar en el rusc"""
        if self.game_over:
            return False
        
        if self.board.es_rusc(self.pos_abeja[0], self.pos_abeja[1]):
            if self.abeja.descargar_nectar_en_rusc(self.board, self.pos_abeja):
                self.mensaje = f"Nectar descargado! Rusc: {self.board.nectar_en_rusc}/{self.game_manager.nectar_objetivo}"
                return True
            else:
                self.mensaje = "No tienes nectar para descargar"
        else:
            self.mensaje = "Debes estar en el rusc para descargar"
        return False
    
    def turno_humanidad(self):
        """Ejecuta el turno de la humanidad"""
        if self.game_over:
            return
        
        self.turno += 1
        
        # Turno de la humanidad
        acciones_humanidad = self.humanidad_agente.obtener_acciones_validas(self.board, self.pos_abeja)
        if acciones_humanidad:
            accion_h = acciones_humanidad[0]
            tipo_h, pos_h = accion_h
            fila, col = pos_h
            
            if tipo_h == 'pesticida':
                flor = self.board.get_celda(fila, col)
                flor.aplicar_pesticida()
                self.mensaje = f"TURNO {self.turno}: Humanidad aplico pesticida en ({fila}, {col})"
            elif tipo_h == 'obstaculo':
                self.board.grid[fila][col] = 'OBSTACULO'
                self.mensaje = f"TURNO {self.turno}: Humanidad coloco obstaculo en ({fila}, {col})"
        
        # Verificar eventos climáticos cada 4 turnos
        if self.turno % 4 == 0:
            self.eventos_azar.generar_evento_clima()
            self.clima_actual = self.eventos_azar.clima_actual
            self.eventos_azar.aplicar_efecto_clima(self.board)
            
            # Intentar reproducción
            nuevas = 0
            for pos_flor, flor in self.board.flores[:]:
                if flor.polinizacion == 1 and flor.vida > 0:
                    exito, nueva_pos = self.eventos_azar.intentar_reproduccion(self.board, pos_flor)
                    if exito:
                        nuevas += 1
            
            if nuevas > 0:
                self.mensaje += f" | Clima: {self.clima_actual} ({nuevas} nuevas flores)"
        
        # Verificar condiciones de finalización
        terminado, resultado, mensaje_final = self.game_manager.verificar_condiciones_finalizacion(
            self.board, self.abeja
        )
        
        if terminado:
            self.game_over = True
            self.resultado = resultado
            self.mensaje = mensaje_final
    
    def run(self):
        """Bucle principal del juego"""
        running = True
        
        while running:
            # Eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE and not self.game_over:
                        self.turno_humanidad()
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    
                    # Click en tablero
                    celda = self.obtener_celda_click(pos)
                    if celda:
                        self.celda_seleccionada = celda
                        # Intentar mover a la celda
                        self.mover_abeja(celda)
                    
                    # Click en botón recoger
                    if self.botones['recoger'].collidepoint(pos) and not self.game_over:
                        self.recoger_nectar()
                    
                    # Click en botón descansar
                    elif self.botones['descansar'].collidepoint(pos) and not self.game_over:
                        self.accion_descansar()
                    
                    # Click en botón A*
                    elif self.botones['a_star'].collidepoint(pos) and not self.game_over:
                        self.accion_a_star()
                    
                    # Click en botón descargar
                    elif self.botones['descargar'].collidepoint(pos) and not self.game_over:
                        self.accion_descargar()
                    
                    # Click en botón siguiente (turno humanidad)
                    elif self.botones['siguiente'].collidepoint(pos) and not self.game_over:
                        self.turno_humanidad()
            
            # Dibujar
            self.screen.fill(BLANCO)
            self.dibujar_tablero()
            self.dibujar_panel_info()
            self.dibujar_botones()
            
            if self.game_over:
                self.dibujar_game_over()
            
            pygame.display.flip()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    print("="*60)
    print("INICIANDO INTERFAZ GRÁFICA - MVP7")
    print("="*60)
    juego = BeeGameGUI(filas=8, columnas=8, nectar_objetivo=50)
    juego.run()
