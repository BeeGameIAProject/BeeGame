"""
Interfaz Gráfica Mejorada (GUI) para el juego BeeGame
MVP7: Implementación con Pygame - Visuals Overhaul
"""

import pygame
import sys
import math
from board import Board
from bee import Bee
from humanidad import Humanidad
from chance_events import ChanceEvents
from expectimax import ExpectimaxAI
from heuristica import Heuristica
from game_manager import GameManager

# --- PALETA DE COLORES MEJORADA (Tonos Pastel y Naturales) ---
C_FONDO_PANEL = (245, 245, 247)
C_TEXTO_PRINCIPAL = (50, 50, 50)
C_TEXTO_SECUNDARIO = (100, 100, 100)

# Tablero
C_CESPED_CLARO = (167, 217, 72)
C_CESPED_OSCURO = (142, 204, 57)
C_SELECCION = (100, 200, 255, 100) # Con Alpha
C_TRANSITABLE = (255, 255, 255, 50)

# Elementos
C_RUSC_BASE = (219, 166, 23)
C_RUSC_DETALLE = (166, 124, 0)
C_OBSTACULO_BASE = (120, 120, 120)
C_OBSTACULO_SOMBRA = (80, 80, 80)

# Abeja
C_ABEJA_CUERPO = (255, 220, 0)
C_ABEJA_RAYAS = (40, 40, 40)
C_ABEJA_ALAS = (200, 240, 255, 150)

# Flores
C_FLOR_SANA = (255, 255, 255)       # Margaritas
C_FLOR_POLINIZADA = (255, 200, 100) # Naranja suave
C_FLOR_CENTRO = (255, 220, 0)
C_PESTICIDA_LEVE = (200, 100, 200)
C_PESTICIDA_GRAVE = (130, 50, 130)

# UI
C_BARRA_FONDO = (200, 200, 200)
C_VIDA = (231, 76, 60)
C_ENERGIA = (52, 152, 219)
C_NECTAR = (241, 196, 15)
C_BOTON_ACTIVO = (255, 255, 255)
C_BOTON_HOVER = (230, 230, 230)
C_BOTON_BORDE = (200, 200, 200)

class BeeGameGUI:
    def __init__(self, filas=8, columnas=8, nectar_objetivo=50):
        pygame.init()
        
        # Configuración de la ventana
        self.CELL_SIZE = 75  # Celdas un poco más grandes para detalle
        self.PANEL_WIDTH = 400
        self.BOARD_WIDTH = columnas * self.CELL_SIZE
        self.BOARD_HEIGHT = filas * self.CELL_SIZE
        self.WINDOW_WIDTH = self.BOARD_WIDTH + self.PANEL_WIDTH
        self.WINDOW_HEIGHT = max(self.BOARD_HEIGHT + 50, 800) # +50 para texto abajo
        
        # Activar anti-aliasing y transparencia
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("BeeGame Simulator - Entorno Eco-Sistémico")
        
        # Fuentes del sistema para mejor legibilidad
        try:
            self.font_title = pygame.font.SysFont("Segoe UI", 36, bold=True)
            self.font_subtitle = pygame.font.SysFont("Segoe UI", 24, bold=True)
            self.font_normal = pygame.font.SysFont("Segoe UI", 18)
            self.font_bold = pygame.font.SysFont("Segoe UI", 18, bold=True)
            self.font_small = pygame.font.SysFont("Consolas", 14)
        except:
            self.font_title = pygame.font.Font(None, 40)
            self.font_subtitle = pygame.font.Font(None, 28)
            self.font_normal = pygame.font.Font(None, 22)
            self.font_bold = pygame.font.Font(None, 22)
            self.font_small = pygame.font.Font(None, 18)

        # Inicializar componentes del juego (Misma lógica que antes)
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
        self.mensaje = "Bienvenido. Selecciona una acción."
        self.clima_actual = "Normal"
        self.game_over = False
        self.resultado = None
        self.celda_seleccionada = None
        self.turno_jugador = True
        self.ultimo_turno_obstaculo = -3
        
        # Control de flores muertas { (f, c): turno_muerte }
        self.flores_muertas_timer = {}
        
        # Animación A*
        self.moviendo_a_star = False
        self.ruta_a_star = []
        self.paso_a_star = 0
        self.timer_a_star = 0
        self.velocidad_a_star = 10 
        
        # Eventos clima
        self.mostrar_evento_clima = False
        self.mensaje_evento_clima = ""
        self.timer_evento_clima = 0
        self.duracion_evento_clima = 180
        self.mostrar_tooltip_clima = False
        
        # Botones (layout actualizado)
        self.botones = self.crear_botones()
        
        self.clock = pygame.time.Clock()

    def crear_botones(self):
        x_start = self.BOARD_WIDTH + 25
        y_start = self.WINDOW_HEIGHT - 220
        w = 165
        h = 50
        gap = 20
        
        return {
            'recoger': pygame.Rect(x_start, y_start, w, h),
            'descansar': pygame.Rect(x_start + w + gap, y_start, w, h),
            'a_star': pygame.Rect(x_start, y_start + h + gap, w, h),
            'descargar': pygame.Rect(x_start + w + gap, y_start + h + gap, w, h),
        }

    # --- FUNCIONES DE DIBUJO PROCEDIMENTAL ---

    def dibujar_tablero(self):
        for fila in range(self.board.filas):
            for col in range(self.board.columnas):
                x = col * self.CELL_SIZE
                y = fila * self.CELL_SIZE
                
                # Patrón de ajedrez
                color_bg = C_CESPED_CLARO if (fila + col) % 2 == 0 else C_CESPED_OSCURO
                pygame.draw.rect(self.screen, color_bg, (x, y, self.CELL_SIZE, self.CELL_SIZE))
                
                # Renderizar contenido
                self.dibujar_contenido_celda(fila, col, x, y)
                
                # Highlight selección
                if self.celda_seleccionada == (fila, col):
                    s = pygame.Surface((self.CELL_SIZE, self.CELL_SIZE), pygame.SRCALPHA)
                    s.fill(C_SELECCION)
                    self.screen.blit(s, (x, y))
                    pygame.draw.rect(self.screen, (255, 255, 255), (x, y, self.CELL_SIZE, self.CELL_SIZE), 3)

        # Dibujar instrucciones debajo del tablero
        self.dibujar_instrucciones_control()

    def dibujar_instrucciones_control(self):
        texto = "Click izquierdo: Moverse  |  Click derecho: Seleccionar casilla"
        surf = self.font_normal.render(texto, True, C_TEXTO_PRINCIPAL)
        # Centrar debajo del tablero
        x = (self.BOARD_WIDTH // 2) - (surf.get_width() // 2)
        y = self.BOARD_HEIGHT + 15
        self.screen.blit(surf, (x, y))

    def dibujar_contenido_celda(self, fila, col, x, y):
        celda = self.board.grid[fila][col]
        center_x = x + self.CELL_SIZE // 2
        center_y = y + self.CELL_SIZE // 2
        
        # 1. Dibujar Rusc
        if celda == 'RUSC':
            self.dibujar_rusc(center_x, center_y)
            
        # 2. Dibujar Obstáculo
        elif celda == 'OBSTACULO':
            self.dibujar_obstaculo(center_x, center_y)
            
        # 3. Dibujar Flor
        elif self.board.es_flor(fila, col):
            flor = self.board.get_celda(fila, col)
            self.dibujar_flor(center_x, center_y, flor, (fila, col))

        # 4. Dibujar Abeja (encima de todo)
        if (fila, col) == self.pos_abeja:
            self.dibujar_abeja(center_x, center_y)

    def dibujar_rusc(self, cx, cy):
        # Base hexagonal (simulada con polígono) o circular estilizada
        radio = self.CELL_SIZE // 2.5
        pygame.draw.circle(self.screen, C_RUSC_BASE, (cx, cy), radio)
        
        # Capas/Anillos
        for i in range(3):
            offset = i * 8
            rect_w = radio * 1.5
            rect_h = 10
            r_rect = pygame.Rect(cx - rect_w//2, cy - 15 + offset, rect_w, rect_h)
            pygame.draw.rect(self.screen, C_RUSC_DETALLE, r_rect, border_radius=5)
            
        # Entrada
        pygame.draw.circle(self.screen, (50, 30, 0), (cx, cy + 10), 8)

    def dibujar_obstaculo(self, cx, cy):
        # Piedra estilizada
        rect = pygame.Rect(cx - 25, cy - 20, 50, 40)
        pygame.draw.rect(self.screen, C_OBSTACULO_BASE, rect, border_radius=10)
        # Sombra/Relieve
        pygame.draw.rect(self.screen, C_OBSTACULO_SOMBRA, (cx - 15, cy - 10, 30, 20), border_radius=5)
        # Cruz roja pequeña
        pygame.draw.line(self.screen, (200, 50, 50), (cx-10, cy-10), (cx+10, cy+10), 3)
        pygame.draw.line(self.screen, (200, 50, 50), (cx+10, cy-10), (cx-10, cy+10), 3)

    def dibujar_flor(self, cx, cy, flor, pos_grid):
        # Gestión de desaparición de flores muertas
        if flor.vida <= 0:
            if pos_grid not in self.flores_muertas_timer:
                self.flores_muertas_timer[pos_grid] = self.turno
            
            turnos_muerta = self.turno - self.flores_muertas_timer[pos_grid]
            
            # Si han pasado más de 2 turnos desde que murió, no se dibuja (desaparece)
            if turnos_muerta > 2:
                return 

            # Dibujar flor marchita
            pygame.draw.line(self.screen, (100, 80, 50), (cx, cy), (cx, cy+20), 3) # Tallo
            pygame.draw.circle(self.screen, (100, 80, 50), (cx, cy-5), 8) # Cabeza muerta
            
            # Indicador visual de desvanecimiento (opcional)
            if turnos_muerta >= 2: # Último turno visible
                 texto = self.font_small.render("X", True, (50, 0, 0))
                 self.screen.blit(texto, (cx-5, cy-25))
            return

        # Si la flor revive o es nueva, borrar del timer de muertas
        if pos_grid in self.flores_muertas_timer:
            del self.flores_muertas_timer[pos_grid]

        # Tallo
        pygame.draw.line(self.screen, (50, 150, 50), (cx, cy+25), (cx, cy), 4)

        # Determinar color pétalos
        color_petalo = C_FLOR_SANA
        if flor.polinizacion == 1:
            color_petalo = C_FLOR_POLINIZADA
        
        if flor.pesticidas >= 2:
            color_petalo = C_PESTICIDA_GRAVE
        elif flor.pesticidas >= 1:
            color_petalo = C_PESTICIDA_LEVE

        # Dibujar 5 pétalos
        radio_petalo = 12
        offset_petalo = 15
        for i in range(5):
            angle = (2 * math.pi / 5) * i
            px = cx + math.cos(angle) * offset_petalo
            py = cy + math.sin(angle) * offset_petalo
            pygame.draw.circle(self.screen, color_petalo, (px, py), radio_petalo)
            pygame.draw.circle(self.screen, (200, 200, 200), (px, py), radio_petalo, 1) # Borde sutil

        # Centro
        pygame.draw.circle(self.screen, C_FLOR_CENTRO, (cx, cy), 10)
        
        # Indicador PESTICIDA (Partículas)
        if flor.pesticidas > 0:
            for i in range(flor.pesticidas * 3):
                ox = cx + math.cos(i) * 20
                oy = cy + math.sin(i) * 20 - 20
                pygame.draw.circle(self.screen, (255, 50, 50), (ox, oy), 3)

    def dibujar_abeja(self, cx, cy):
        # Alas (con transparencia)
        alas_surf = pygame.Surface((60, 40), pygame.SRCALPHA)
        pygame.draw.ellipse(alas_surf, C_ABEJA_ALAS, (0, 0, 25, 40)) # Ala izq
        pygame.draw.ellipse(alas_surf, C_ABEJA_ALAS, (35, 0, 25, 40)) # Ala der
        # Rotar alas ligeramente si se está moviendo (efecto visual simple)
        if self.moviendo_a_star:
            offset_ala = math.sin(pygame.time.get_ticks() * 0.02) * 5
            self.screen.blit(alas_surf, (cx - 30, cy - 25 + offset_ala))
        else:
            self.screen.blit(alas_surf, (cx - 30, cy - 25))

        # Cuerpo
        cuerpo_rect = pygame.Rect(cx - 15, cy - 12, 30, 24)
        pygame.draw.rect(self.screen, C_ABEJA_CUERPO, cuerpo_rect, border_radius=12)
        
        # Rayas
        pygame.draw.line(self.screen, C_ABEJA_RAYAS, (cx-5, cy-12), (cx-5, cy+12), 4)
        pygame.draw.line(self.screen, C_ABEJA_RAYAS, (cx+5, cy-12), (cx+5, cy+12), 4)
        
        # Ojos
        pygame.draw.circle(self.screen, (0, 0, 0), (cx + 8, cy - 4), 3)
        pygame.draw.circle(self.screen, (0, 0, 0), (cx + 8, cy + 4), 3)
        
        # Carga (mochila de polen)
        if self.abeja.nectar_cargado > 0:
             pygame.draw.circle(self.screen, C_NECTAR, (cx - 8, cy), 6)

    # --- UI & PANELES ---

    def dibujar_panel_info(self):
        # Fondo panel
        panel_rect = pygame.Rect(self.BOARD_WIDTH, 0, self.PANEL_WIDTH, self.WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, C_FONDO_PANEL, panel_rect)
        pygame.draw.line(self.screen, (200, 200, 200), (self.BOARD_WIDTH, 0), (self.BOARD_WIDTH, self.WINDOW_HEIGHT), 2)
        
        x_pad = self.BOARD_WIDTH + 25
        y = 30
        
        # Título
        txt = self.font_title.render("BeeGame IA", True, C_TEXTO_PRINCIPAL)
        self.screen.blit(txt, (x_pad, y))
        y += 50
        

        # Sección Estadísticas
        self.dibujar_seccion_stats(x_pad, y)
        y += 200
        
        self.dibujar_separador(y)
        y += 20
        
        # Clima
        self.dibujar_widget_clima(x_pad, y)
        y += 80
        
        # Caja de Mensajes (Log)
        self.dibujar_log(x_pad, y)

    def dibujar_separador(self, y):
        pygame.draw.line(self.screen, (220, 220, 220), 
                         (self.BOARD_WIDTH + 20, y), 
                         (self.WINDOW_WIDTH - 20, y), 1)

    def dibujar_seccion_stats(self, x, y):
        # Título sección
        self.screen.blit(self.font_subtitle.render("Estado de la Colmena", True, C_TEXTO_SECUNDARIO), (x, y))
        y += 35
        
        # Barras
        self.crear_barra_progreso(x, y, "Vida", self.abeja.life, self.abeja.max_vida, C_VIDA)
        y += 45
        self.crear_barra_progreso(x, y, "Energía", self.abeja.energia, self.abeja.max_energia, C_ENERGIA)
        y += 45
        
        # Néctar Rusc (Objetivo)
        obj = self.game_manager.nectar_objetivo
        act = self.board.nectar_en_rusc
        self.crear_barra_progreso(x, y, f"Miel en Rusc ({act}/{obj})", act, obj, C_RUSC_BASE)
        y += 45
        
        # Néctar Mochila
        txt = self.font_normal.render(f"Mochila: {self.abeja.nectar_cargado} / {self.abeja.capacidad_nectar}", True, C_TEXTO_PRINCIPAL)
        self.screen.blit(txt, (x, y))

    def crear_barra_progreso(self, x, y, etiqueta, valor, maximo, color):
        # Texto
        lbl = self.font_small.render(etiqueta, True, C_TEXTO_SECUNDARIO)
        self.screen.blit(lbl, (x, y))
        
        # Barra Fondo
        rect_bg = pygame.Rect(x, y + 18, 350, 12)
        pygame.draw.rect(self.screen, (230, 230, 230), rect_bg, border_radius=6)
        
        # Barra Valor
        if maximo > 0:
            ancho = int((valor / maximo) * 350)
            ancho = max(0, min(ancho, 350))
            rect_val = pygame.Rect(x, y + 18, ancho, 12)
            pygame.draw.rect(self.screen, color, rect_val, border_radius=6)

    def dibujar_widget_clima(self, x, y):
        rect_clima = pygame.Rect(x, y, 350, 60)
        pygame.draw.rect(self.screen, (255, 255, 255), rect_clima, border_radius=10)
        pygame.draw.rect(self.screen, (220, 220, 230), rect_clima, 1, border_radius=10)
        
        # Icono clima (simplificado)
        cx = x + 40
        cy = y + 30
        
        if self.clima_actual == "Lluvia":
            pygame.draw.circle(self.screen, (100, 100, 150), (cx, cy-5), 15)
            # Gotas
            pygame.draw.line(self.screen, C_ENERGIA, (cx-5, cy+10), (cx-10, cy+20), 2)
            pygame.draw.line(self.screen, C_ENERGIA, (cx+5, cy+10), (cx, cy+20), 2)
            color_txt = C_ENERGIA
        elif self.clima_actual == "Sol":
            pygame.draw.circle(self.screen, (255, 200, 0), (cx, cy), 12)
            # Rayos
            for i in range(0, 360, 45):
                rad = math.radians(i)
                pygame.draw.line(self.screen, (255, 200, 0), 
                                 (cx + math.cos(rad)*15, cy + math.sin(rad)*15),
                                 (cx + math.cos(rad)*20, cy + math.sin(rad)*20), 2)
            color_txt = (200, 150, 0)
        else:
            pygame.draw.circle(self.screen, (200, 200, 200), (cx, cy), 15)
            pygame.draw.circle(self.screen, (220, 220, 220), (cx+10, cy+5), 12)
            color_txt = C_TEXTO_SECUNDARIO
            
        txt_c = self.font_bold.render(f"Clima: {self.clima_actual}", True, color_txt)
        self.screen.blit(txt_c, (x + 80, y + 20))
        
        # Botón de ayuda "?"
        mouse_pos = pygame.mouse.get_pos()
        help_rect = pygame.Rect(x + 310, y + 10, 30, 30)
        hover_help = help_rect.collidepoint(mouse_pos)
        
        # Círculo de ayuda
        color_help = (100, 150, 255) if hover_help else (150, 150, 150)
        pygame.draw.circle(self.screen, color_help, (x + 325, y + 25), 15)
        pygame.draw.circle(self.screen, (255, 255, 255), (x + 325, y + 25), 15, 2)
        
        # Símbolo "?"
        txt_help = self.font_subtitle.render("?", True, (255, 255, 255))
        self.screen.blit(txt_help, (x + 318, y + 12))
        
        # Guardar rect para detección de click
        self.help_clima_rect = help_rect
        
        # Mostrar tooltip si está activo
        if self.mostrar_tooltip_clima:
            self.dibujar_tooltip_clima(x, y)

    def dibujar_tooltip_clima(self, x, y):
        """Dibuja un tooltip explicando los estados del clima"""
        tooltip_width = 320
        tooltip_height = 180
        tooltip_x = x + 15
        tooltip_y = y + 70
        
        # Fondo del tooltip con sombra
        shadow = pygame.Rect(tooltip_x + 3, tooltip_y + 3, tooltip_width, tooltip_height)
        pygame.draw.rect(self.screen, (0, 0, 0, 100), shadow, border_radius=8)
        
        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
        pygame.draw.rect(self.screen, (250, 250, 250), tooltip_rect, border_radius=8)
        pygame.draw.rect(self.screen, (100, 100, 100), tooltip_rect, 2, border_radius=8)
        
        # Título
        titulo = self.font_bold.render("Estados del Clima:", True, C_TEXTO_PRINCIPAL)
        self.screen.blit(titulo, (tooltip_x + 10, tooltip_y + 10))
        
        # Explicaciones
        explicaciones = [
            ("☀ Sol:", "Flores regeneran vida más rápido", (255, 200, 0)),
            ("      Favorece el crecimiento", "", (100, 100, 100)),
            ("", "", (0, 0, 0)),
            ("🌧 Lluvia:", "Flores pueden perder vida", C_ENERGIA),
            ("      Condiciones adversas", "", (100, 100, 100)),
            ("", "", (0, 0, 0)),
            ("☁ Normal:", "Sin efectos especiales", C_TEXTO_SECUNDARIO),
            ("      Balance natural", "", (100, 100, 100)),
        ]
        
        y_offset = tooltip_y + 40
        for texto, desc, color in explicaciones:
            if texto:
                txt = self.font_small.render(texto, True, color)
                self.screen.blit(txt, (tooltip_x + 15, y_offset))
                if desc:
                    txt_desc = self.font_small.render(desc, True, color)
                    self.screen.blit(txt_desc, (tooltip_x + 100, y_offset))
            y_offset += 18
    
    def dibujar_log(self, x, y):
        rect_log = pygame.Rect(x, y, 350, 100)
        pygame.draw.rect(self.screen, (255, 255, 255), rect_log, border_radius=5)
        pygame.draw.rect(self.screen, (200, 200, 200), rect_log, 1, border_radius=5)
        
        # Wrap de texto simple
        palabras = self.mensaje.split(' ')
        lineas = []
        actual = ""
        for p in palabras:
            test = actual + p + " "
            if len(test) > 40:
                lineas.append(actual)
                actual = p + " "
            else:
                actual = test
        lineas.append(actual)
        
        # Dibujar últimas 4 líneas
        off_y = y + 10
        for linea in lineas[-4:]:
            txt = self.font_small.render(linea, True, C_TEXTO_PRINCIPAL)
            self.screen.blit(txt, (x + 10, off_y))
            off_y += 20

    def dibujar_botones(self):
        mouse_pos = pygame.mouse.get_pos()
        activo_global = self.turno_jugador and not self.game_over
        
        for key, rect in self.botones.items():
            hover = rect.collidepoint(mouse_pos) and activo_global
            
            # Colores
            if not activo_global:
                bg = (230, 230, 230)
                border = (200, 200, 200)
                txt_c = (150, 150, 150)
            elif hover:
                bg = C_BOTON_HOVER
                border = (100, 100, 100)
                txt_c = C_TEXTO_PRINCIPAL
            else:
                bg = C_BOTON_ACTIVO
                border = C_BOTON_BORDE
                txt_c = C_TEXTO_PRINCIPAL
            
            # Dibujar botón con sombra
            if activo_global and not hover:
                pygame.draw.rect(self.screen, (200, 200, 200), (rect.x, rect.y+3, rect.width, rect.height), border_radius=8)
                
            pygame.draw.rect(self.screen, bg, rect, border_radius=8)
            pygame.draw.rect(self.screen, border, rect, 2, border_radius=8)
            
            # Texto e Icono (simulado con texto)
            label = key.replace("_", " ").upper()
            if key == "recoger": icon = "🌼"
            elif key == "descansar": icon = "💤"
            elif key == "a_star": icon = "🏠"
            elif key == "descargar": icon = "📥"
            
            # Render texto
            try:
                # Intentar renderizar emoji si la fuente lo soporta, si no, solo texto
                txt_s = self.font_bold.render(f"{icon} {label}", True, txt_c)
            except:
                txt_s = self.font_bold.render(f"{label}", True, txt_c)
                
            cx = rect.x + rect.width // 2 - txt_s.get_width() // 2
            cy = rect.y + rect.height // 2 - txt_s.get_height() // 2
            self.screen.blit(txt_s, (cx, cy))

    # --- LÓGICA DE JUEGO (Mantenida del original, acortada aquí para brevedad) ---
    
    def dibujar_evento_climatico(self):
        if not self.mostrar_evento_clima: return
        
        overlay = pygame.Surface((self.WINDOW_WIDTH, 80), pygame.SRCALPHA)
        color_bg = (50, 50, 50, 220)
        if "Sol" in self.mensaje_evento_clima: color_bg = (255, 200, 0, 220)
        elif "Lluvia" in self.mensaje_evento_clima: color_bg = (50, 50, 200, 220)
            
        overlay.fill(color_bg)
        
        y_pos = self.WINDOW_HEIGHT // 2 - 40
        self.screen.blit(overlay, (0, y_pos))
        
        txt = self.font_title.render(self.mensaje_evento_clima, True, (255, 255, 255))
        cx = self.WINDOW_WIDTH // 2 - txt.get_width() // 2
        cy = y_pos + 40 - txt.get_height() // 2
        self.screen.blit(txt, (cx, cy))

    # ... [Resto de métodos lógicos como obtener_celda_click, mover_abeja, etc. IDÉNTICOS A TU CÓDIGO ANTERIOR] ...
    # ... [Solo asegúrate de llamar a self.dibujar_botones() y self.dibujar_panel_info() dentro del loop] ...
    
    # He incluido aquí los métodos necesarios para que funcione el COPY-PASTE directo
    # Replicando lógica esencial para no romper el script:

    def obtener_celda_click(self, pos):
        x, y = pos
        if x < self.BOARD_WIDTH and y < self.BOARD_HEIGHT:
            return (y // self.CELL_SIZE, x // self.CELL_SIZE)
        return None

    def mover_abeja(self, destino):
        if self.game_over or not self.turno_jugador: return False
        fila, col = destino
        
        if self.board.es_transitable(fila, col):
            if self.abeja.mover(self.board, self.pos_abeja, destino):
                # Chequeo pesticida
                celda = self.board.get_celda(fila, col)
                daño = 0
                if hasattr(celda, 'pesticidas') and celda.pesticidas > 0:
                     # Lógica simplificada de daño si la celda es flor
                     daño = celda.get_daño_pesticida() if hasattr(celda, 'get_daño_pesticida') else 0

                self.pos_abeja = destino
                self.mensaje = f"Movimiento a ({fila}, {col})"
                if daño > 0: self.mensaje += f" ¡Daño -{daño}!"

                if self.board.es_rusc(fila, col):
                    recuperado = self.abeja.descargar_nectar_en_rusc(self.board, self.pos_abeja)
                    self.abeja.recuperar_energia_en_rusc(self.board, self.pos_abeja)
                    self.mensaje = "¡En casa! Energía recuperada y miel descargada."

                self.finalizar_turno_jugador()
                return True
            else:
                self.mensaje = "¡Sin energía suficiente!"
        else:
            self.mensaje = "Camino bloqueado."
        return False

    def recoger_nectar(self):
        if self.game_over or not self.celda_seleccionada: 
            self.mensaje = "Selecciona una flor primero."
            return
        
        f, c = self.celda_seleccionada
        # Check adyacencia
        if abs(self.pos_abeja[0]-f) <= 1 and abs(self.pos_abeja[1]-c) <= 1:
            if self.board.es_flor(f, c):
                if self.abeja.recoger_nectar_y_polinizar(self.board, (f, c)):
                    self.mensaje = "¡Néctar recogido y polinizado!"
                    self.finalizar_turno_jugador()
                else:
                    self.mensaje = "No se puede recoger (vacía o llena)."
            else:
                self.mensaje = "Eso no es una flor."
        else:
            self.mensaje = "¡Demasiado lejos!"

    def accion_descansar(self):
        if self.game_over: return
        self.abeja.descansar()
        self.mensaje = "Zzz... Recuperando energía."
        self.finalizar_turno_jugador()

    def accion_a_star(self):
        if self.game_over or self.moviendo_a_star: return
        ruta = self.abeja.calcular_ruta_a_rusc(self.board, self.pos_abeja)
        if ruta and len(ruta) > 1:
            self.moviendo_a_star = True
            self.ruta_a_star = ruta
            self.paso_a_star = 1
            self.timer_a_star = 0
            self.mensaje = "Piloto automático activado (A*)..."
        else:
            self.mensaje = "Ya estás en casa o no hay ruta."

    def accion_descargar(self):
        if self.board.es_rusc(self.pos_abeja[0], self.pos_abeja[1]):
            self.abeja.descargar_nectar_en_rusc(self.board, self.pos_abeja)
            self.mensaje = "Miel descargada manual."
            self.finalizar_turno_jugador()
        else:
            self.mensaje = "Debes estar en el rusc."

    def actualizar_a_star(self):
        self.timer_a_star += 1
        if self.timer_a_star >= self.velocidad_a_star:
            self.timer_a_star = 0
            if self.paso_a_star < len(self.ruta_a_star):
                dest = self.ruta_a_star[self.paso_a_star]
                if self.abeja.mover(self.board, self.pos_abeja, dest):
                    self.pos_abeja = dest
                    self.paso_a_star += 1
                else:
                    self.moviendo_a_star = False # Sin energía
            else:
                self.moviendo_a_star = False
                self.mensaje = "Llegada a destino (A*)."
                # Auto-descarga al llegar
                if self.board.es_rusc(*self.pos_abeja):
                    self.abeja.descargar_nectar_en_rusc(self.board, self.pos_abeja)
                    self.abeja.recuperar_energia_en_rusc(self.board, self.pos_abeja)
                self.finalizar_turno_jugador()

    def finalizar_turno_jugador(self):
        self.turno_jugador = False
        self.turno_humanidad()

    def turno_humanidad(self):
        if self.game_over: return
        self.turno += 1
        
        # IA Lógica
        acciones = self.humanidad_agente.obtener_acciones_validas(self.board, self.pos_abeja)
        # Filtro simple para demo (Prioriza atacar)
        accion_realizada = False
        
        # Verificar si puede poner obstaculo (cada 3 turnos)
        obstaculos_cnt = sum(1 for r in self.board.grid for c in r if c == 'OBSTACULO')
        puede_obs = (self.turno - self.ultimo_turno_obstaculo >= 3) and (obstaculos_cnt < 5)

        for tipo, pos in acciones:
            if tipo == 'pesticida':
                f, c = pos
                flor = self.board.get_celda(f, c)
                flor.aplicar_pesticida()
                self.mensaje = f"¡ALERTA! Pesticida en ({f},{c})"
                accion_realizada = True
                break
            elif tipo == 'obstaculo' and puede_obs:
                self.board.grid[pos[0]][pos[1]] = 'OBSTACULO'
                self.ultimo_turno_obstaculo = self.turno
                self.mensaje = f"¡CUIDADO! Obstáculo en ({pos[0]},{pos[1]})"
                accion_realizada = True
                break
        
        if not accion_realizada:
            self.mensaje = "La humanidad observa..."

        # Clima y Eventos
        if self.turno % 4 == 0:
            self.eventos_azar.generar_evento_clima()
            self.clima_actual = self.eventos_azar.clima_actual
            self.eventos_azar.aplicar_efecto_clima(self.board)
            self.mensaje_evento_clima = f"Clima: {self.clima_actual.upper()}"
            self.mostrar_evento_clima = True
            self.timer_evento_clima = 0
            
            # Reproducción
            nuevas = 0
            for pos_f, flor in self.board.flores[:]:
                if flor.polinizacion == 1 and flor.vida > 0:
                    exito, _ = self.eventos_azar.intentar_reproduccion(self.board, pos_f)
                    if exito: nuevas += 1
            if nuevas: self.mensaje_evento_clima += f" (+{nuevas} Flores)"

        # Check Fin
        fin, res, msg = self.game_manager.verificar_condiciones_finalizacion(self.board, self.abeja)
        if fin:
            self.game_over = True
            self.resultado = res
            self.mensaje = msg
        else:
            self.turno_jugador = True

    def actualizar_evento_climatico(self):
        if self.mostrar_evento_clima:
            self.timer_evento_clima += 1
            if self.timer_evento_clima > self.duracion_evento_clima:
                self.mostrar_evento_clima = False

    def run(self):
        running = True
        while running:
            # Eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if event.button == 1: # Left Click
                        # Check botón de ayuda clima
                        if hasattr(self, 'help_clima_rect') and self.help_clima_rect.collidepoint(pos):
                            self.mostrar_tooltip_clima = not self.mostrar_tooltip_clima
                            continue
                        
                        # Check botones
                        clicked_btn = False
                        if self.turno_jugador and not self.game_over:
                            for key, rect in self.botones.items():
                                if rect.collidepoint(pos):
                                    if key == 'recoger': self.recoger_nectar()
                                    elif key == 'descansar': self.accion_descansar()
                                    elif key == 'a_star': self.accion_a_star()
                                    elif key == 'descargar': self.accion_descargar()
                                    clicked_btn = True
                                    break
                        
                        # Si no es botón, es tablero
                        if not clicked_btn:
                            celda = self.obtener_celda_click(pos)
                            if celda and self.turno_jugador:
                                self.mover_abeja(celda)

                    elif event.button == 3: # Right Click
                        celda = self.obtener_celda_click(pos)
                        if celda: self.celda_seleccionada = celda

            # Updates
            if self.moviendo_a_star: self.actualizar_a_star()
            self.actualizar_evento_climatico()

            # Render
            self.screen.fill((255, 255, 255)) # Fondo base
            self.dibujar_tablero()
            self.dibujar_panel_info()
            self.dibujar_botones()
            self.dibujar_evento_climatico()
            
            if self.game_over:
                # Overlay simple Game Over
                s = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.SRCALPHA)
                s.fill((0,0,0,180))
                self.screen.blit(s, (0,0))
                color_res = C_CESPED_CLARO if self.resultado == "VICTORIA" else C_VIDA
                txt = self.font_title.render(self.resultado, True, color_res)
                self.screen.blit(txt, (self.WINDOW_WIDTH//2 - txt.get_width()//2, self.WINDOW_HEIGHT//2))

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    juego = BeeGameGUI(filas=8, columnas=8, nectar_objetivo=50)
    juego.run()