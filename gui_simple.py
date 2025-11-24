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
        self.mensaje = "TU TURNO: Haz click en una celda o usa los botones"
        self.clima_actual = "Normal"
        self.game_over = False
        self.resultado = None
        self.celda_seleccionada = None
        self.turno_jugador = True  # True = turno del jugador, False = turno humanidad
        self.ultimo_turno_obstaculo = -3  # Para controlar obstáculos cada 3 turnos
        
        # Variables para A* animado
        self.moviendo_a_star = False
        self.ruta_a_star = []
        self.paso_a_star = 0
        self.timer_a_star = 0
        self.velocidad_a_star = 15  # frames entre pasos
        
        # Variables para eventos climáticos
        self.mostrar_evento_clima = False
        self.mensaje_evento_clima = ""
        self.timer_evento_clima = 0
        self.duracion_evento_clima = 120  # frames (2 segundos a 60fps)
        
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
            
            # Mostrar cantidad de néctar si tiene
            if self.abeja.nectar_cargado > 0:
                texto_nectar = self.font_small.render(str(self.abeja.nectar_cargado), True, NARANJA)
                self.screen.blit(texto_nectar, (x + self.CELL_SIZE - 20, y + self.CELL_SIZE - 20))
        
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
        y_offset += 30
        
        # Indicador de turno
        if self.turno_jugador:
            color_turno = VERDE
            texto_turno = "TU TURNO"
        else:
            color_turno = ROJO
            texto_turno = "HUMANIDAD"
        
        pygame.draw.rect(self.screen, color_turno, (x_panel, y_offset, 250, 25))
        pygame.draw.rect(self.screen, NEGRO, (x_panel, y_offset, 250, 25), 2)
        texto = self.font_normal.render(texto_turno, True, BLANCO if not self.turno_jugador else NEGRO)
        self.screen.blit(texto, (x_panel + 70, y_offset + 2))
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
        
        # Mostrar barra solo hasta el objetivo, pero mostrar número total almacenado
        self.dibujar_barra(x_panel, y_offset, 250, 25, min(actual, objetivo), objetivo, NARANJA, 
                          f"Objetivo: {actual}/{objetivo}")
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
        # Deshabilitar botones si no es turno del jugador
        activo = self.turno_jugador and not self.game_over
        
        # Recoger néctar
        color = VERDE if activo else GRIS
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
        color_a = AZUL if activo else GRIS
        pygame.draw.rect(self.screen, color_a, self.botones['a_star'])
        pygame.draw.rect(self.screen, NEGRO, self.botones['a_star'], 2)
        texto = self.font_small.render("A* al Rusc", True, BLANCO if activo else NEGRO)
        self.screen.blit(texto, (self.botones['a_star'].x + 25, self.botones['a_star'].y + 10))
        
        # Descargar néctar
        color_d = NARANJA if activo else GRIS
        pygame.draw.rect(self.screen, color_d, self.botones['descargar'])
        pygame.draw.rect(self.screen, NEGRO, self.botones['descargar'], 2)
        texto = self.font_small.render("Descargar", True, NEGRO)
        self.screen.blit(texto, (self.botones['descargar'].x + 15, self.botones['descargar'].y + 10))
        
        # Info: Ya no hay botón "siguiente turno" porque se ejecuta automáticamente
        info_rect = self.botones['siguiente']
        pygame.draw.rect(self.screen, GRIS_OSCURO, info_rect)
        pygame.draw.rect(self.screen, NEGRO, info_rect, 2)
        texto = self.font_small.render("Los turnos son", True, BLANCO)
        self.screen.blit(texto, (info_rect.x + 20, info_rect.y + 5))
        texto = self.font_small.render("automaticos", True, BLANCO)
        self.screen.blit(texto, (info_rect.x + 30, info_rect.y + 25))
    
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
    
    def dibujar_evento_climatico(self):
        """Dibuja notificación de evento climático"""
        if not self.mostrar_evento_clima:
            return
        
        # Calcular alpha (transparencia) basado en el timer
        progreso = self.timer_evento_clima / self.duracion_evento_clima
        if progreso > 0.8:
            alpha = int(255 * (1 - (progreso - 0.8) / 0.2))
        else:
            alpha = 255
        
        # Fondo semi-transparente
        ancho_notif = 600
        alto_notif = 80
        x_notif = (self.WINDOW_WIDTH - ancho_notif) // 2
        y_notif = 50
        
        overlay = pygame.Surface((ancho_notif, alto_notif))
        overlay.set_alpha(min(alpha, 230))
        
        # Color según clima
        if self.clima_actual == "Lluvia":
            overlay.fill(AZUL)
        elif self.clima_actual == "Sol":
            overlay.fill(AMARILLO)
        else:
            overlay.fill(GRIS)
        
        self.screen.blit(overlay, (x_notif, y_notif))
        
        # Borde
        pygame.draw.rect(self.screen, NEGRO, (x_notif, y_notif, ancho_notif, alto_notif), 3)
        
        # Texto
        color_texto = BLANCO if self.clima_actual == "Lluvia" else NEGRO
        texto = self.font_normal.render(self.mensaje_evento_clima, True, color_texto)
        rect_texto = texto.get_rect(center=(self.WINDOW_WIDTH // 2, y_notif + alto_notif // 2))
        self.screen.blit(texto, rect_texto)
    
    def actualizar_evento_climatico(self):
        """Actualiza el timer del evento climático"""
        if self.mostrar_evento_clima:
            self.timer_evento_clima += 1
            if self.timer_evento_clima >= self.duracion_evento_clima:
                self.mostrar_evento_clima = False
                self.timer_evento_clima = 0
    
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
        if self.game_over or not self.turno_jugador:
            return False
        
        fila, col = destino
        
        # Verificar si es transitable (ahora incluye flores)
        if self.board.es_transitable(fila, col):
            if self.abeja.mover(self.board, self.pos_abeja, destino):
                # Verificar si hubo daño por pesticida
                from flower import Flower
                celda = self.board.grid[fila][col]
                daño = 0
                if isinstance(celda, Flower) and celda.esta_viva():
                    daño = celda.get_daño_pesticida()
                
                self.pos_abeja = destino
                self.mensaje = f"Movida a ({fila}, {col})"
                
                if daño > 0:
                    self.mensaje += f" | ¡Daño por pesticida! -{daño} vida"
                
                # Si llega al rusc, recuperar energía y vida, y descargar néctar
                if self.board.es_rusc(fila, col):
                    nectar_descargado = self.abeja.nectar_cargado
                    if nectar_descargado > 0:
                        self.abeja.descargar_nectar_en_rusc(self.board, self.pos_abeja)
                    self.abeja.recuperar_energia_en_rusc(self.board, self.pos_abeja)
                    self.mensaje = f"EN EL RUSC: Energia y Vida al máximo!"
                    if nectar_descargado > 0:
                        self.mensaje += f" | {nectar_descargado} néctar descargado!"
                
                # FINALIZAR TURNO DEL JUGADOR
                self.finalizar_turno_jugador()
                return True
            else:
                self.mensaje = "No hay suficiente energia para mover"
        else:
            self.mensaje = "Esa casilla no es transitable"
        return False
    
    def recoger_nectar(self):
        """Intenta recoger néctar de una flor adyacente"""
        if self.game_over or not self.celda_seleccionada or not self.turno_jugador:
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
                    
                    # FINALIZAR TURNO DEL JUGADOR
                    self.finalizar_turno_jugador()
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
        if self.game_over or not self.turno_jugador:
            return False
        
        self.abeja.descansar()
        self.mensaje = f"Descansando... Energia: {self.abeja.energia}/{self.abeja.max_energia}"
        
        # FINALIZAR TURNO DEL JUGADOR
        self.finalizar_turno_jugador()
        return True
    
    def accion_a_star(self):
        """Inicia el movimiento automático hacia el rusc usando A*"""
        if self.game_over or not self.turno_jugador or self.moviendo_a_star:
            return False
        
        ruta = self.abeja.calcular_ruta_a_rusc(self.board, self.pos_abeja)
        
        if ruta and len(ruta) > 1:
            # Iniciar animación de movimiento A*
            self.moviendo_a_star = True
            self.ruta_a_star = ruta
            self.paso_a_star = 1  # Empezar desde el paso 1 (0 es la posición actual)
            self.timer_a_star = 0
            self.mensaje = f"A*: Calculando ruta al rusc ({len(ruta)-1} pasos)..."
            return True
        else:
            self.mensaje = "Ya estas en el rusc"
        return False
    
    def actualizar_a_star(self):
        """Actualiza la animación del movimiento A*"""
        if not self.moviendo_a_star:
            return
        
        self.timer_a_star += 1
        
        # Mover cada cierto número de frames
        if self.timer_a_star >= self.velocidad_a_star:
            self.timer_a_star = 0
            
            if self.paso_a_star < len(self.ruta_a_star):
                siguiente = self.ruta_a_star[self.paso_a_star]
                
                # Intentar mover
                if self.abeja.mover(self.board, self.pos_abeja, siguiente):
                    self.pos_abeja = siguiente
                    self.paso_a_star += 1
                    pasos_restantes = len(self.ruta_a_star) - self.paso_a_star
                    self.mensaje = f"A*: Moviendo... ({pasos_restantes} pasos restantes)"
                else:
                    # Sin energía
                    self.mensaje = "A*: Sin energia!"
                    self.moviendo_a_star = False
                    self.finalizar_turno_jugador()
                    return
            
            # Si llegó al final de la ruta
            if self.paso_a_star >= len(self.ruta_a_star):
                self.moviendo_a_star = False
                
                # Si llegó al rusc, descargar néctar y recuperar energía y vida
                if self.board.es_rusc(self.pos_abeja[0], self.pos_abeja[1]):
                    nectar_descargado = self.abeja.nectar_cargado
                    if nectar_descargado > 0:
                        self.abeja.descargar_nectar_en_rusc(self.board, self.pos_abeja)
                    self.abeja.recuperar_energia_en_rusc(self.board, self.pos_abeja)
                    self.mensaje = f"A*: Llegada al rusc! Energia y Vida al máximo!"
                    if nectar_descargado > 0:
                        self.mensaje += f" | {nectar_descargado} néctar descargado!"
                else:
                    self.mensaje = f"A*: Movimiento completado"
                
                # Finalizar turno
                self.finalizar_turno_jugador()
    
    def accion_descargar(self):
        """Descarga néctar en el rusc"""
        if self.game_over or not self.turno_jugador:
            return False
        
        if self.board.es_rusc(self.pos_abeja[0], self.pos_abeja[1]):
            if self.abeja.descargar_nectar_en_rusc(self.board, self.pos_abeja):
                self.mensaje = f"Nectar descargado! Rusc: {self.board.nectar_en_rusc}/{self.game_manager.nectar_objetivo}"
                
                # FINALIZAR TURNO DEL JUGADOR
                self.finalizar_turno_jugador()
                return True
            else:
                self.mensaje = "No tienes nectar para descargar"
        else:
            self.mensaje = "Debes estar en el rusc para descargar"
        return False
    
    def finalizar_turno_jugador(self):
        """Finaliza el turno del jugador y ejecuta automáticamente el turno de la humanidad"""
        self.turno_jugador = False
        self.turno_humanidad()
    
    def turno_humanidad(self):
        """Ejecuta el turno de la humanidad"""
        if self.game_over:
            return
        
        self.turno += 1
        self.board.incrementar_turno()  # Incrementar turno del board (limpia flores muertas)
        
        # Contar obstáculos actuales
        obstaculos_actuales = sum(1 for fila in self.board.grid for celda in fila if celda == 'OBSTACULO')
        puede_obstaculo = (self.turno - self.ultimo_turno_obstaculo >= 3) and (obstaculos_actuales < 4)
        
        # Turno de la humanidad con restricciones
        acciones_humanidad = self.humanidad_agente.obtener_acciones_validas(self.board, self.pos_abeja)
        
        # Filtrar acciones según restricciones
        acciones_validas = []
        for accion in acciones_humanidad:
            tipo_h, pos_h = accion
            
            if tipo_h == 'obstaculo':
                # Solo si puede colocar obstáculo
                if puede_obstaculo:
                    acciones_validas.append(accion)
            else:  # pesticida
                acciones_validas.append(accion)
        
        if acciones_validas:
            accion_h = acciones_validas[0]
            tipo_h, pos_h = accion_h
            fila, col = pos_h
            
            if tipo_h == 'pesticida':
                flor = self.board.get_celda(fila, col)
                flor.aplicar_pesticida()
                self.mensaje = f"TURNO {self.turno}: Humanidad aplico PESTICIDA en ({fila}, {col})"
            elif tipo_h == 'obstaculo':
                self.board.grid[fila][col] = 'OBSTACULO'
                self.ultimo_turno_obstaculo = self.turno
                self.mensaje = f"TURNO {self.turno}: Humanidad coloco OBSTACULO en ({fila}, {col})"
        else:
            self.mensaje = f"TURNO {self.turno}: Humanidad no pudo actuar"
        
        # Verificar eventos climáticos cada 4 turnos
        if self.turno % 4 == 0:
            self.eventos_azar.generar_evento_clima()
            self.clima_actual = self.eventos_azar.clima_actual
            self.eventos_azar.aplicar_efecto_clima(self.board)
            
            # Mostrar evento climático
            if self.clima_actual == "Lluvia":
                self.mensaje_evento_clima = "☔ LLUVIA: Pesticidas reducidos en todas las flores"
            elif self.clima_actual == "Sol":
                self.mensaje_evento_clima = "☀️ SOL: +20% probabilidad de reproducción"
            else:
                self.mensaje_evento_clima = "🌤️ CLIMA NORMAL"
            
            self.mostrar_evento_clima = True
            self.timer_evento_clima = 0
            
            # Intentar reproducción
            nuevas = 0
            for pos_flor, flor in self.board.flores[:]:
                if flor.polinizacion == 1 and flor.vida > 0:
                    exito, nueva_pos = self.eventos_azar.intentar_reproduccion(self.board, pos_flor)
                    if exito:
                        nuevas += 1
            
            if nuevas > 0:
                self.mensaje_evento_clima += f" | {nuevas} flores nuevas nacieron!"
        
        # Verificar condiciones de finalización
        terminado, resultado, mensaje_final = self.game_manager.verificar_condiciones_finalizacion(
            self.board, self.abeja
        )
        
        if terminado:
            self.game_over = True
            self.resultado = resultado
            self.mensaje = mensaje_final
        else:
            # Devolver el turno al jugador
            self.turno_jugador = True
            self.mensaje += " | TU TURNO"
    
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
                    
                    # Click izquierdo - mover directamente
                    if event.button == 1:  # Click izquierdo
                        celda = self.obtener_celda_click(pos)
                        if celda and self.turno_jugador:
                            # Intentar mover a la celda
                            self.mover_abeja(celda)
                        
                        # Click en botón recoger (solo si es turno del jugador)
                        if self.botones['recoger'].collidepoint(pos) and self.turno_jugador and not self.game_over:
                            self.recoger_nectar()
                        
                        # Click en botón descansar
                        elif self.botones['descansar'].collidepoint(pos) and self.turno_jugador and not self.game_over:
                            self.accion_descansar()
                        
                        # Click en botón A*
                        elif self.botones['a_star'].collidepoint(pos) and self.turno_jugador and not self.game_over:
                            self.accion_a_star()
                        
                        # Click en botón descargar
                        elif self.botones['descargar'].collidepoint(pos) and self.turno_jugador and not self.game_over:
                            self.accion_descargar()
                    
                    # Click derecho - seleccionar casilla
                    elif event.button == 3:  # Click derecho
                        celda = self.obtener_celda_click(pos)
                        if celda and self.turno_jugador:
                            self.celda_seleccionada = celda
                            fila, col = celda
                            self.mensaje = f"Casilla seleccionada: ({fila}, {col})"
            
            # Actualizar animaciones
            if self.moviendo_a_star:
                self.actualizar_a_star()
            
            # Actualizar evento climático
            self.actualizar_evento_climatico()
            
            # Dibujar
            self.screen.fill(BLANCO)
            self.dibujar_tablero()
            self.dibujar_panel_info()
            self.dibujar_botones()
            
            # Dibujar notificación de evento climático
            self.dibujar_evento_climatico()
            
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
