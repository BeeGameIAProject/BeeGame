"""
Interfaz Gráfica (GUI) para el juego BeeGame
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
        self.WINDOW_HEIGHT = self.BOARD_HEIGHT + 100  # Espacio para botones
        
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("🐝 BeeGame - Proyecto IA")
        
        # Fuentes
        self.font_title = pygame.font.Font(None, 32)
        self.font_normal = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)
        
        # Inicializar componentes del juego
        self.board = Board(filas, columnas)
        self.board.inicializar_tablero(num_flores=12, num_obstaculos=2)
        
        self.bee = Bee(life=100)
        self.pos_bee = (self.board.rusc_pos[0] - 1, self.board.rusc_pos[1])
        
        self.humanidad = Humanidad()
        self.chance_events = ChanceEvents()
        self.heuristica = Heuristica(w1=10, w2=8, w3=15, w4=5, w5=3, w6=2, w7=1)
        self.expectimax = ExpectimaxAI(max_depth=2, heuristica=self.heuristica)
        self.game_manager = GameManager(nectar_objetivo=nectar_objetivo)
        
        # Variables de control
        self.turno = 0
        self.modo_juego = "MANUAL"  # MANUAL o IA
        self.celda_seleccionada = None
        self.mensaje = "¡Bienvenido a BeeGame!"
        self.clima_actual = "Normal"
        self.game_over = False
        self.resultado = None
        
        # Botones
        self.botones = self.crear_botones()
        
        # Clock para FPS
        self.clock = pygame.time.Clock()
        
    def crear_botones(self):
        """Crea los botones de la interfaz"""
        y_start = self.BOARD_HEIGHT + 10
        botones = {
            'polinizar': pygame.Rect(10, y_start, 120, 40),
            'descansar': pygame.Rect(140, y_start, 120, 40),
            'a_star': pygame.Rect(270, y_start, 150, 40),
            'modo_ia': pygame.Rect(430, y_start, 120, 40),
            'siguiente': pygame.Rect(self.BOARD_WIDTH - 130, y_start, 120, 40),
        }
        return botones
    
    def dibujar_celda(self, fila, col, x, y):
        """Dibuja una celda individual del tablero"""
        # Fondo de la celda
        pygame.draw.rect(self.screen, VERDE, (x, y, self.CELL_SIZE, self.CELL_SIZE))
        pygame.draw.rect(self.screen, NEGRO, (x, y, self.CELL_SIZE, self.CELL_SIZE), 2)
        
        # Contenido de la celda
        celda = self.board.tablero[fila][col]
        
        # Dibujar elementos
        if celda == '🏠':  # Rusc
            pygame.draw.circle(self.screen, AMARILLO, 
                             (x + self.CELL_SIZE//2, y + self.CELL_SIZE//2), 
                             self.CELL_SIZE//3)
            texto = self.font_normal.render("RUSC", True, NEGRO)
            self.screen.blit(texto, (x + 8, y + self.CELL_SIZE//2 - 10))
            
        elif celda == '🪨':  # Obstáculo
            pygame.draw.rect(self.screen, GRIS_OSCURO, 
                           (x + 10, y + 10, self.CELL_SIZE - 20, self.CELL_SIZE - 20))
            
        elif isinstance(celda, type(self.board.flores[0]) if self.board.flores else object):  # Flor
            flor = celda
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
                    texto = self.font_small.render("✓", True, VERDE_OSCURO)
                    self.screen.blit(texto, (x + self.CELL_SIZE - 20, y + 5))
                    
                if flor.pesticidas > 0:
                    texto = self.font_small.render(f"☠{flor.pesticidas}", True, ROJO)
                    self.screen.blit(texto, (x + 5, y + 5))
            else:
                # Flor muerta
                pygame.draw.line(self.screen, MARRON, (x + 20, y + 20), 
                               (x + self.CELL_SIZE - 20, y + self.CELL_SIZE - 20), 3)
                pygame.draw.line(self.screen, MARRON, (x + self.CELL_SIZE - 20, y + 20), 
                               (x + 20, y + self.CELL_SIZE - 20), 3)
        
        # Dibujar abeja si está en esta posición
        if (fila, col) == self.pos_bee:
            pygame.draw.circle(self.screen, NEGRO,
                             (x + self.CELL_SIZE//2, y + self.CELL_SIZE//2),
                             self.CELL_SIZE//5)
            texto = self.font_small.render("🐝", True, AMARILLO)
            self.screen.blit(texto, (x + self.CELL_SIZE//2 - 8, y + self.CELL_SIZE//2 - 8))
        
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
        texto = self.font_title.render("INFO", True, NEGRO)
        self.screen.blit(texto, (x_panel + 80, y_offset))
        y_offset += 40
        
        # Turno
        texto = self.font_normal.render(f"Turno: {self.turno}", True, NEGRO)
        self.screen.blit(texto, (x_panel, y_offset))
        y_offset += 30
        
        # Modo
        color_modo = VERDE_OSCURO if self.modo_juego == "IA" else AZUL
        texto = self.font_normal.render(f"Modo: {self.modo_juego}", True, color_modo)
        self.screen.blit(texto, (x_panel, y_offset))
        y_offset += 40
        
        # --- Estado de la Abeja ---
        texto = self.font_normal.render("🐝 ABEJA", True, NEGRO)
        self.screen.blit(texto, (x_panel, y_offset))
        y_offset += 30
        
        # Barra de vida
        self.dibujar_barra(x_panel, y_offset, 250, 20, self.bee.life, 100, ROJO, "Vida")
        y_offset += 30
        
        # Barra de energía
        self.dibujar_barra(x_panel, y_offset, 250, 20, self.bee.energia, 100, AZUL, "Energía")
        y_offset += 30
        
        # Néctar cargado
        texto = self.font_small.render(f"Néctar: {self.bee.nectar_cargado}/50", True, NEGRO)
        self.screen.blit(texto, (x_panel, y_offset))
        y_offset += 40
        
        # --- Progreso ---
        texto = self.font_normal.render("🍯 PROGRESO", True, NEGRO)
        self.screen.blit(texto, (x_panel, y_offset))
        y_offset += 30
        
        objetivo = self.game_manager.nectar_objetivo
        actual = self.board.nectar_en_rusc
        self.dibujar_barra(x_panel, y_offset, 250, 25, actual, objetivo, NARANJA, 
                          f"Néctar: {actual}/{objetivo}")
        y_offset += 40
        
        # --- Flores ---
        flores_vivas = sum(1 for f in self.board.flores if f.vida > 0)
        texto = self.font_small.render(f"Flores vivas: {flores_vivas}/{len(self.board.flores)}", 
                                      True, VERDE_OSCURO)
        self.screen.blit(texto, (x_panel, y_offset))
        y_offset += 40
        
        # --- Clima ---
        texto = self.font_normal.render("🌦️ CLIMA", True, NEGRO)
        self.screen.blit(texto, (x_panel, y_offset))
        y_offset += 25
        
        color_clima = AZUL if self.clima_actual == "Lluvia" else (AMARILLO if self.clima_actual == "Sol" else GRIS)
        texto = self.font_normal.render(self.clima_actual, True, color_clima)
        self.screen.blit(texto, (x_panel, y_offset))
        y_offset += 40
        
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
        # Polinizar
        color = VERDE if not self.game_over else GRIS
        pygame.draw.rect(self.screen, color, self.botones['polinizar'])
        pygame.draw.rect(self.screen, NEGRO, self.botones['polinizar'], 2)
        texto = self.font_small.render("Polinizar", True, NEGRO)
        self.screen.blit(texto, (self.botones['polinizar'].x + 15, self.botones['polinizar'].y + 10))
        
        # Descansar
        pygame.draw.rect(self.screen, color, self.botones['descansar'])
        pygame.draw.rect(self.screen, NEGRO, self.botones['descansar'], 2)
        texto = self.font_small.render("Descansar", True, NEGRO)
        self.screen.blit(texto, (self.botones['descansar'].x + 15, self.botones['descansar'].y + 10))
        
        # A* Volver al Rusc
        pygame.draw.rect(self.screen, color, self.botones['a_star'])
        pygame.draw.rect(self.screen, NEGRO, self.botones['a_star'], 2)
        texto = self.font_small.render("A* al Rusc", True, NEGRO)
        self.screen.blit(texto, (self.botones['a_star'].x + 20, self.botones['a_star'].y + 10))
        
        # Modo IA
        color_modo = VERDE_OSCURO if self.modo_juego == "IA" else AZUL
        pygame.draw.rect(self.screen, color_modo, self.botones['modo_ia'])
        pygame.draw.rect(self.screen, NEGRO, self.botones['modo_ia'], 2)
        texto = self.font_small.render("Modo IA", True, BLANCO)
        self.screen.blit(texto, (self.botones['modo_ia'].x + 20, self.botones['modo_ia'].y + 10))
        
        # Siguiente turno
        color = NARANJA if not self.game_over else GRIS
        pygame.draw.rect(self.screen, color, self.botones['siguiente'])
        pygame.draw.rect(self.screen, NEGRO, self.botones['siguiente'], 2)
        texto = self.font_small.render("Siguiente", True, NEGRO)
        self.screen.blit(texto, (self.botones['siguiente'].x + 20, self.botones['siguiente'].y + 10))
    
    def dibujar_game_over(self):
        """Dibuja pantalla de game over"""
        # Overlay semi-transparente
        overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(NEGRO)
        self.screen.blit(overlay, (0, 0))
        
        # Texto principal
        if self.resultado == "VICTORIA":
            texto = self.font_title.render("🎉 ¡VICTORIA! 🎉", True, AMARILLO)
        else:
            texto = self.font_title.render("💀 DERROTA 💀", True, ROJO)
        
        rect_texto = texto.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 - 50))
        self.screen.blit(texto, rect_texto)
        
        # Detalles
        detalles = [
            f"Turnos: {self.turno}",
            f"Néctar: {self.board.nectar_en_rusc}/{self.game_manager.nectar_objetivo}",
            f"Flores vivas: {sum(1 for f in self.board.flores if f.vida > 0)}",
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
    
    def manejar_click_tablero(self, celda):
        """Maneja clicks en el tablero"""
        if self.game_over or self.modo_juego == "IA":
            return
        
        fila, col = celda
        self.celda_seleccionada = celda
        
        # Si la abeja puede moverse a esa celda
        if self.board.tablero[fila][col] in ['⬜', '🏠']:
            if self.bee.mover(fila, col, self.board):
                self.mensaje = f"Abeja movida a ({fila}, {col})"
            else:
                self.mensaje = "No se puede mover ahí"
        
        # Si hay una flor, intentar recoger néctar
        elif isinstance(self.board.tablero[fila][col], type(self.board.flores[0]) if self.board.flores else object):
            flor = self.board.tablero[fila][col]
            if self.bee.esta_adyacente(fila, col):
                if self.bee.recoger_nectar_y_polinizar(fila, col, self.board):
                    self.mensaje = f"¡Néctar recolectado! ({self.bee.nectar_cargado}/50)"
                else:
                    self.mensaje = "No se puede recoger de esa flor"
            else:
                self.mensaje = "Debes estar adyacente a la flor"
    
    def accion_descansar(self):
        """Ejecuta acción de descansar"""
        if self.game_over or self.modo_juego == "IA":
            return
        
        self.bee.descansar()
        self.mensaje = f"Descansando... Energía: {self.bee.energia}/100"
    
    def accion_a_star(self):
        """Ejecuta A* para volver al rusc"""
        if self.game_over or self.modo_juego == "IA":
            return
        
        ruta = self.bee.calcular_ruta_a_rusc(self.board)
        if ruta and len(ruta) > 1:
            # Mover al siguiente paso en la ruta
            siguiente = ruta[1]
            if self.bee.mover(siguiente[0], siguiente[1], self.board):
                self.mensaje = f"Siguiendo ruta A* ({len(ruta)-1} pasos restantes)"
        else:
            self.mensaje = "Ya estás en el rusc o no hay ruta"
    
    def turno_humanidad(self):
        """Ejecuta turno de la humanidad (IA)"""
        acciones = self.humanidad.obtener_acciones_validas(self.board, self.bee)
        if acciones:
            accion = acciones[0]  # Tomar la primera acción válida
            tipo, pos = accion
            fila, col = pos
            
            if tipo == 'pesticida':
                flor = self.board.tablero[fila][col]
                flor.aplicar_pesticida()
                self.mensaje = f"Humanidad aplicó pesticida en ({fila}, {col})"
            elif tipo == 'obstaculo':
                self.board.tablero[fila][col] = '🪨'
                self.mensaje = f"Humanidad colocó obstáculo en ({fila}, {col})"
    
    def verificar_eventos_clima(self):
        """Verifica y aplica eventos climáticos"""
        if self.turno % 4 == 0 and self.turno > 0:
            clima = self.chance_events.generar_evento_clima()
            self.clima_actual = clima
            self.chance_events.aplicar_efecto_clima(clima, self.board)
            
            # Intentar reproducción de flores
            nuevas = 0
            for flor in self.board.flores[:]:
                if flor.polinizacion == 1 and flor.vida > 0:
                    prob = self.chance_events.calcular_probabilidad_reproduccion(clima)
                    if self.chance_events.intentar_reproduccion(flor, prob, self.board):
                        nuevas += 1
            
            if nuevas > 0:
                self.mensaje = f"Clima: {clima} - {nuevas} nuevas flores"
            else:
                self.mensaje = f"Clima: {clima}"
    
    def siguiente_turno(self):
        """Avanza al siguiente turno"""
        if self.game_over:
            return
        
        self.turno += 1
        
        # Turno de la humanidad
        self.turno_humanidad()
        
        # Verificar eventos climáticos
        self.verificar_eventos_clima()
        
        # Verificar condiciones de finalización
        terminado, resultado, mensaje = self.game_manager.verificar_condiciones_finalizacion(
            self.board, self.bee
        )
        
        if terminado:
            self.game_over = True
            self.resultado = resultado
            self.mensaje = mensaje
    
    def turno_ia(self):
        """Ejecuta un turno completo de la IA"""
        if self.game_over:
            return
        
        # La abeja juega con Expectimax
        mejor_accion = self.expectimax.obtener_mejor_accion(
            self.board, self.bee, self.humanidad, self.chance_events
        )
        
        if mejor_accion:
            tipo, pos = mejor_accion
            
            if tipo == 'mover':
                fila, col = pos
                self.bee.mover(fila, col, self.board)
                self.mensaje = f"IA movió a ({fila}, {col})"
            elif tipo == 'recoger':
                fila, col = pos
                self.bee.recoger_nectar_y_polinizar(fila, col, self.board)
                self.mensaje = f"IA recolectó néctar en ({fila}, {col})"
            elif tipo == 'descansar':
                self.bee.descansar()
                self.mensaje = "IA descansó"
        
        # Continuar con siguiente turno
        self.siguiente_turno()
    
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
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    
                    # Click en tablero
                    celda = self.obtener_celda_click(pos)
                    if celda:
                        self.manejar_click_tablero(celda)
                    
                    # Click en botones
                    if self.botones['polinizar'].collidepoint(pos):
                        if self.celda_seleccionada:
                            self.manejar_click_tablero(self.celda_seleccionada)
                    
                    elif self.botones['descansar'].collidepoint(pos):
                        self.accion_descansar()
                    
                    elif self.botones['a_star'].collidepoint(pos):
                        self.accion_a_star()
                    
                    elif self.botones['modo_ia'].collidepoint(pos):
                        self.modo_juego = "IA" if self.modo_juego == "MANUAL" else "MANUAL"
                        self.mensaje = f"Modo cambiado a {self.modo_juego}"
                    
                    elif self.botones['siguiente'].collidepoint(pos):
                        if self.modo_juego == "MANUAL":
                            self.siguiente_turno()
                        else:
                            self.turno_ia()
            
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
    juego = BeeGameGUI(filas=8, columnas=8, nectar_objetivo=50)
    juego.run()
