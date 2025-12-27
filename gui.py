"""
Interfaz Gráfica (GUI) para el juego BeeGame.
Orquesta la interacción entre el usuario, el renderizado y los agentes.
"""

import sys
import math
import time
from statistics import mean
import pygame

from src.qlearning import QLearningAI
from src.board import Board
from src.bee import Bee
from src.humanidad import Humanidad
from src.chance_events import ChanceEvents
from src.expectimax import ExpectimaxAI, GameState
from src.heuristica import Heuristica
from src.game_manager import GameManager

# === CONFIGURACIÓN Y CONSTANTES VISUALES ===

# Colores UI
C_FONDO_PANEL = (245, 245, 247)
C_TEXTO_PRINCIPAL = (50, 50, 50)
C_TEXTO_SECUNDARIO = (100, 100, 100)

# Colores Tablero
C_CESPED_CLARO = (167, 217, 72)
C_CESPED_OSCURO = (142, 204, 57)
C_SELECCION = (100, 200, 255, 100)
C_TRANSITABLE = (255, 255, 255, 50)

# Colores Entidades
C_COLMENA_BASE = (219, 166, 23)
C_COLMENA_DETALLE = (166, 124, 0)
C_OBSTACULO_BASE = (120, 120, 120)
C_OBSTACULO_MADERA = (139, 69, 19)
C_OBSTACULO_BARRAS = (160, 82, 45)

# Colores Abeja
C_ABEJA_CUERPO = (255, 220, 0)
C_ABEJA_RAYAS = (40, 40, 40)
C_ABEJA_ALAS = (200, 240, 255, 150)

# Colores Flores y Estado
C_FLOR_SANA = (255, 255, 255)
C_FLOR_POLINIZADA = (255, 200, 100)
C_FLOR_CENTRO = (255, 220, 0)
C_PESTICIDA_LEVE = (200, 100, 200)
C_PESTICIDA_GRAVE = (130, 50, 130)

# Colores Barras
C_VIDA = (231, 76, 60)
C_ENERGIA = (52, 152, 219)
C_NECTAR = (241, 196, 15)

# Botones
C_BOTON_ACTIVO = (255, 255, 255)
C_BOTON_HOVER = (230, 230, 230)
C_BOTON_BORDE = (200, 200, 200)


class BeeGameGUI:
    """Clase principal que maneja la ventana, eventos y bucle del juego."""

    def __init__(self, filas=9, columnas=9, nectar_objetivo=100):
        pygame.init()
        self.clock = pygame.time.Clock()

        # Configuración de dimensiones
        self.CELL_SIZE = 62
        self.PANEL_WIDTH = 400
        self.BOARD_WIDTH = columnas * self.CELL_SIZE
        self.BOARD_HEIGHT = filas * self.CELL_SIZE
        self.WINDOW_WIDTH = self.BOARD_WIDTH + self.PANEL_WIDTH
        self.WINDOW_HEIGHT = max(self.BOARD_HEIGHT + 100, 730)

        # Configuración pantalla
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("BeeGame Simulator - Entorno Eco-Sistémico")

        # Fuentes
        self._inicializar_fuentes()

        # Inicialización de lógica
        self.filas_init = filas
        self.columnas_init = columnas
        self.nectar_objetivo_init = nectar_objetivo
        self._inicializar_juego()

    def _inicializar_fuentes(self):
        """Intenta cargar fuentes del sistema, con fallback por defecto."""
        try:
            self.font_title = pygame.font.SysFont("Segoe UI", 36, bold=True)
            self.font_subtitle = pygame.font.SysFont("Segoe UI", 24, bold=True)
            self.font_normal = pygame.font.SysFont("Segoe UI", 18)
            self.font_bold = pygame.font.SysFont("Segoe UI", 18, bold=True)
            self.font_small = pygame.font.SysFont("Consolas", 14)
        except Exception:
            self.font_title = pygame.font.Font(None, 40)
            self.font_subtitle = pygame.font.Font(None, 28)
            self.font_normal = pygame.font.Font(None, 22)
            self.font_bold = pygame.font.Font(None, 22)
            self.font_small = pygame.font.Font(None, 18)

    def _inicializar_juego(self):
        """Reinicia todos los componentes y estados del juego."""
        # Entidades
        self.board = Board(self.filas_init, self.columnas_init)
        self.board.inicializar_tablero(num_flores=12, num_obstaculos=2)

        start_pos = (self.board.pos_colmena[0] - 1, self.board.pos_colmena[1])
        self.abeja = Bee(vida=50)
        self.pos_abeja = start_pos

        self.humanidad_agente = Humanidad()
        self.eventos_azar = ChanceEvents()
        self.game_manager = GameManager(nectar_objetivo=self.nectar_objetivo_init)

        # IAs
        self.heuristica = Heuristica()
        self.ai = ExpectimaxAI(max_depth=2, heuristica=self.heuristica, nectar_objetivo=self.nectar_objetivo_init)
        self.q_agent = QLearningAI(alpha=0.5, gamma=0.9, epsilon=0.3)

        # Estado UI/Control
        self.turno = 0
        self.mensaje = "Bienvenido. Selecciona una acción."
        self.clima_actual = "Normal"
        self.game_over = False
        self.resultado = None
        self.celda_seleccionada = None
        self.turno_jugador = True
        self.ultima_flor_recolectada = None
        self.flores_muertas_timer = {}

        # Configuración IA
        self.usar_expectimax = True
        self.usar_qlearning = False
        self.calculando_ia = False
        self.nodos_explorados = 0
        self.tiempo_calculo_ia = 0
        self.ia_error = [0]
        self.error_semantic = [0]

        # Animaciones y Eventos
        self.moviendo_a_star = False
        self.ruta_a_star = []
        self.paso_a_star = 0
        self.timer_a_star = 0
        self.velocidad_a_star = 10
        self.factor_random = 0.5

        self.mostrar_evento_clima = False
        self.mensaje_evento_clima = ""
        self.timer_evento_clima = 0
        self.duracion_evento_clima = 180
        self.mostrar_tooltip_clima = False

        self.botones = self._crear_rectangulos_botones()

    def _crear_rectangulos_botones(self):
        """Define la geometría de los botones."""
        x = self.BOARD_WIDTH + 25
        y = 580
        w, h = 165, 50
        gap = 20

        bx = (self.BOARD_WIDTH // 2) - (140 // 2)
        by = self.BOARD_HEIGHT + 50

        return {
            'recoger': pygame.Rect(x, y, w, h),
            'descansar': pygame.Rect(x + w + gap, y, w, h),
            'ir_a_la_colmena': pygame.Rect(x, y + h + gap, w, h),
            'cambiar_IA': pygame.Rect(x + w + gap, y + h + gap, w, h),
            'reiniciar': pygame.Rect(bx, by, 140, 40)
        }

    # === LÓGICA DEL JUGADOR (ABEJA) ===

    def mover_abeja(self, destino):
        if self.game_over or not self.turno_jugador: return

        if destino == self.pos_abeja:
            self.mensaje = "Ya estás en esa posición."
            return

        if not self.abeja.es_movimiento_valido(self.board, self.pos_abeja, destino):
            self.mensaje = "¡Demasiado lejos! Solo 1 casilla."
            return

        if not self.board.es_transitable(destino[0], destino[1]):
            self.mensaje = "Camino bloqueado."
            return

        if self.abeja.mover(self.board, self.pos_abeja, destino):
            self._procesar_movimiento_exitoso(destino)
        else:
            self.mensaje = "¡No tienes energía suficiente!"

    def _procesar_movimiento_exitoso(self, destino):
        self.ultima_flor_recolectada = None
        self.pos_abeja = destino

        msg = f"Movimiento a {destino}"

        celda = self.board.get_celda(*destino)
        daño = getattr(celda, 'get_daño_pesticida', lambda: 0)()
        if daño > 0:
            msg += f" ¡Daño -{daño}!"
            self.factor_random = 0.75

        if self.board.es_colmena(*destino):
            miel = self.abeja.nectar_cargado
            self.abeja.descargar_nectar_en_colmena(self.board, self.pos_abeja)
            self.abeja.recuperar_energia_en_colmena(self.board, self.pos_abeja)
            msg = "¡En casa! Recuperado." + (f" Miel: +{miel}" if miel > 0 else "")
            self.factor_random = 0.25

        self.mensaje = msg
        self.finalizar_turno_jugador()

    def recoger_nectar(self):
        if self.game_over or not self.celda_seleccionada:
            self.mensaje = "Selecciona una flor primero (clic derecho)."
            return

        f, c = self.celda_seleccionada
        if (f, c) == self.ultima_flor_recolectada:
            self.mensaje = "Ya has recolectado aquí."
            return

        if max(abs(self.pos_abeja[0] - f), abs(self.pos_abeja[1] - c)) > 1:
            self.mensaje = "¡Acércate más a la flor!"
            return

        if self.abeja.recoger_nectar_y_polinizar(self.board, (f, c)):
            self.ultima_flor_recolectada = (f, c)
            self.mensaje = f"¡Néctar +10! Flor polinizada en ({f},{c})"
            self.celda_seleccionada = None
            self.finalizar_turno_jugador()
        else:
            self._explicar_fallo_recoleccion()

    def _explicar_fallo_recoleccion(self):
        if not self.abeja.tiene_energia(self.abeja.coste_recoleccion):
            self.mensaje = "Sin energía para recolectar."
        elif not self.abeja.puede_cargar_nectar():
            self.mensaje = "Mochila llena."
        else:
            self.mensaje = "Flor no válida o vacía."

    def accion_descansar(self):
        if self.game_over: return
        self.abeja.descansar()
        self.mensaje = "Descansando... Energía +20"
        self.finalizar_turno_jugador()

    def accion_volver_colmena_a_star(self):
        if self.game_over or self.moviendo_a_star: return

        ruta = self.abeja.calcular_ruta_a_colmena(self.board, self.pos_abeja, self.factor_random)

        if ruta and len(ruta) > 1:
            coste = (len(ruta) - 1) * self.abeja.coste_movimiento
            if self.abeja.energia < coste:
                self.mensaje = f"A* Alerta: Energía insuficiente ({self.abeja.energia}/{coste})."
            else:
                self.moviendo_a_star = True
                self.ruta_a_star = ruta
                self.paso_a_star = 1
                self.timer_a_star = 0
                self.mensaje = "Piloto automático A* activado..."
        else:
            self.mensaje = "No se encontró ruta o ya estás en casa."

    def finalizar_turno_jugador(self):
        self.turno_jugador = False
        self.turno_humanidad()

    # === LÓGICA DE LA IA (HUMANIDAD) ===

    def turno_humanidad(self):
        if self.game_over: return
        self.turno += 1

        acciones = self.humanidad_agente.obtener_acciones_validas(self.board, self.pos_abeja)
        accion_realizada = False

        start_time = time.time()
        self.calculando_ia = True

        if self.usar_expectimax:
            accion_realizada = self._ejecutar_logica_expectimax(acciones)
        elif self.usar_qlearning:
            accion_realizada = self._ejecutar_logica_qlearning(acciones)
        else:
            accion_realizada = self._ejecutar_logica_basica(acciones)

        self.tiempo_calculo_ia = time.time() - start_time
        self.calculando_ia = False

        if not accion_realizada:
            self.mensaje = "La humanidad observa..."

        self._procesar_eventos_azar()
        self._verificar_estado_juego()

    def _ejecutar_logica_expectimax(self, acciones):
        if not acciones: return False

        self.ai.nodos_explorados = 0

        estado_base = GameState(self.board, self.abeja, self.pos_abeja,
                                self.humanidad_agente, self.eventos_azar, self.turno)

        # Calculamos la valoración superficial (sin pensar) del estado actual
        valor_estatico = self.heuristica.evaluar(estado_base)

        mejor_accion = None
        peor_valor_para_abeja = float('inf')

        for accion in acciones:
            estado_sim = estado_base.clonar()
            estado_sim.humanidad.ejecutar_accion(estado_sim.tablero, accion, estado_sim.pos_abeja)

            valor = self.ai._expectimax(estado_sim, 0, 'CHANCE')

            if valor < peor_valor_para_abeja:
                peor_valor_para_abeja = valor
                mejor_accion = accion

        self.nodos_explorados = self.ai.nodos_explorados

        if mejor_accion:
            self._aplicar_accion_humanidad(mejor_accion, "Expectimax")

            # El "Error" es la diferencia entre lo que parecía (estático) y lo que calculó (profundo)
            # Nota: usamos abs() para ver la magnitud del cambio de opinión
            diferencia_juicio = abs(valor_estatico - peor_valor_para_abeja)
            self.ia_error.append(diferencia_juicio)
            self._calcular_error_decision_humana(mejor_accion)
            return True
        return False

    def _ejecutar_logica_qlearning(self, acciones):
        self.nodos_explorados = 0

        estado_s = self.q_agent.obtener_estado(self.board, self.pos_abeja, self.abeja)
        accion = self.q_agent.escoger_accion(estado_s, acciones)

        if accion:
            self._aplicar_accion_humanidad(accion, "Q-Learning")
            recompensa = self._calcular_recompensa_qlearning(accion)

            estado_s_prime = self.q_agent.obtener_estado(self.board, self.pos_abeja, self.abeja)
            nuevas_acciones = self.humanidad_agente.obtener_acciones_validas(self.board, self.pos_abeja)

            # CAPTURAMOS EL ERROR AQUÍ
            td_error = self.q_agent.update(estado_s, accion, recompensa, estado_s_prime, nuevas_acciones)
            self._calcular_error_decision_humana(accion)
            # Lo guardamos para la gráfica/stats (sobrescribiendo el cálculo de distancia anterior)
            self.ia_error.append(td_error)
            return True
        return False

    def _ejecutar_logica_basica(self, acciones):
        self.nodos_explorados = 0
        for accion in acciones:
            tipo, _ = accion
            if tipo == 'pesticida':
                self._aplicar_accion_humanidad(accion, "IA Básica")
                return True

        if acciones:
            self._aplicar_accion_humanidad(acciones[0], "IA Básica")
            return True
        return False

    def _aplicar_accion_humanidad(self, accion, nombre_ia):
        self.humanidad_agente.ejecutar_accion(self.board, accion, self.pos_abeja)
        tipo, pos = accion
        self.mensaje = f"{nombre_ia}: {tipo.capitalize()} en {pos}"
    def _calcular_error_decision_humana(self, accion_elegida):
        """
        Calcula el error como la diferencia entre la acción tomada por la IA
        y un escenario alternativo razonable (flor más cercana a la abeja).

        Este error mide desalineación estratégica, NO aprendizaje.
        """
        tipo, pos_accion = accion_elegida

        # Distancia entre la acción realizada y la abeja
        dist_accion = self.humanidad_agente.distancia_chebyshev(
            pos_accion, self.pos_abeja
        )

        # Distancia entre la abeja y la flor viva más cercana
        flores_vivas = [p for p, fl in self.board.flores if fl.vida > 0]
        dist_flor = 0

        if flores_vivas:
            dist_flor = min(
                self.humanidad_agente.distancia_chebyshev(p, self.pos_abeja)
                for p in flores_vivas
            )

        # Error = diferencia entre decisión real y escenario alternativo
        error = abs(dist_accion - dist_flor)

        self.error_semantic.append(error)

    def _calcular_recompensa_qlearning(self, accion):
        tipo, pos = accion
        if tipo == 'pesticida':
            dist = self.humanidad_agente.distancia_chebyshev(pos, self.pos_abeja)
            if dist <= 1: return 10
            if dist <= 2: return 5
            return -1
        if tipo == 'obstaculo':
            return 2
        return 0

    def _calcular_y_registrar_error(self, pos_accion):
        dist_accion = self.humanidad_agente.distancia_chebyshev(pos_accion, self.pos_abeja)
        flores = [p for p, fl in self.board.flores if fl.esta_viva()]
        dist_flor = 0
        if flores:
            dist_flor = min(self.humanidad_agente.distancia_chebyshev(p, self.pos_abeja) for p in flores)

        error = abs(dist_accion - dist_flor)
        self.ia_error.append(error)

    def _procesar_eventos_azar(self):
        res = self.eventos_azar.ejecutar_ciclo(self.board, self.turno)

        if res:
            self.clima_actual = res["clima"]
            nuevas = res["nuevas_flores"]

            self.mensaje_evento_clima = f"Clima: {self.clima_actual.upper()}"
            if nuevas > 0: self.mensaje_evento_clima += f" (+{nuevas} Flores)"

            self.mostrar_evento_clima = True
            self.timer_evento_clima = 0

            if self.clima_actual == "Lluvia":
                self.factor_random = 0.8
            elif self.clima_actual == "Sol":
                self.factor_random = 0.25
            else:
                self.factor_random = 0.5

    def _verificar_estado_juego(self):
        fin, res, msg = self.game_manager.verificar_condiciones_finalizacion(self.board, self.abeja)
        if fin:
            self.game_over = True
            self.resultado = res
            self.mensaje = msg
        else:
            self.turno_jugador = True

    # === BUCLE PRINCIPAL Y EVENTOS ===

    def run(self):
        running = True
        while running:
            # Eventos Pygame
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self._manejar_clic(event.button, pygame.mouse.get_pos())

            # Actualización Lógica
            self._actualizar_animaciones()

            # Dibujado
            self._dibujar_escena()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

    def _manejar_clic(self, boton, pos):
        if self.mostrar_tooltip_clima:
            if hasattr(self, 'close_tooltip_rect') and self.close_tooltip_rect.collidepoint(pos):
                self.mostrar_tooltip_clima = False
                return
            self.mostrar_tooltip_clima = False
            return

        if hasattr(self, 'help_clima_rect') and self.help_clima_rect.collidepoint(pos):
            self.mostrar_tooltip_clima = not self.mostrar_tooltip_clima
            return

        # Clic izquierdo (acciones)
        if boton == 1:
            if 'reiniciar' in self.botones and self.botones['reiniciar'].collidepoint(pos):
                self._inicializar_juego()
                return

            if self.turno_jugador and not self.game_over:
                for key, rect in self.botones.items():
                    if rect.collidepoint(pos):
                        if key == 'recoger':
                            self.recoger_nectar()
                        elif key == 'descansar':
                            self.accion_descansar()
                        elif key == 'ir_a_la_colmena':
                            self.accion_volver_colmena_a_star()
                        elif key == 'cambiar_IA':
                            self.usar_expectimax = not self.usar_expectimax
                            self.usar_qlearning = not self.usar_expectimax
                            # Feedback visual inmediato o log
                            self.mensaje = f"IA Cambiada a {'Expectimax' if self.usar_expectimax else 'Q-Learning'}"
                        return

                celda = self._obtener_coordenada_tablero(pos)
                if celda: self.mover_abeja(celda)

        # Clic derecho (selección)
        elif boton == 3:
            celda = self._obtener_coordenada_tablero(pos)
            if celda:
                f, c = celda
                if self.board.es_flor(f, c) and self.board.get_celda(f, c).esta_viva():
                    self.celda_seleccionada = celda
                else:
                    self.celda_seleccionada = None

    def _actualizar_animaciones(self):
        # Animación A*
        if self.moviendo_a_star:
            self.timer_a_star += 1
            if self.timer_a_star >= self.velocidad_a_star:
                self.timer_a_star = 0
                if self.paso_a_star < len(self.ruta_a_star):
                    dest = self.ruta_a_star[self.paso_a_star]
                    if self.abeja.mover(self.board, self.pos_abeja, dest):
                        self.pos_abeja = dest
                        self.paso_a_star += 1
                    else:
                        self.moviendo_a_star = False
                else:
                    self.moviendo_a_star = False
                    if self.board.es_colmena(*self.pos_abeja):
                        self.abeja.descargar_nectar_en_colmena(self.board, self.pos_abeja)
                        self.abeja.recuperar_energia_en_colmena(self.board, self.pos_abeja)
                    self.finalizar_turno_jugador()

        # Banner Clima
        if self.mostrar_evento_clima:
            self.timer_evento_clima += 1
            if self.timer_evento_clima > self.duracion_evento_clima:
                self.mostrar_evento_clima = False

    def _obtener_coordenada_tablero(self, pos):
        x, y = pos
        if x < self.BOARD_WIDTH and y < self.BOARD_HEIGHT:
            return (y // self.CELL_SIZE, x // self.CELL_SIZE)
        return None

    # === DIBUJADO ===

    def _dibujar_escena(self):
        self.screen.fill((255, 255, 255))
        self.dibujar_tablero()
        self.dibujar_panel_info()
        self.dibujar_botones()
        self.dibujar_evento_climatico()
        if self.mostrar_tooltip_clima:
            self.dibujar_tooltip_clima()
        if self.game_over:
            self._dibujar_game_over()

    def dibujar_tablero(self):
        for f in range(self.board.filas):
            for c in range(self.board.columnas):
                x, y = c * self.CELL_SIZE, f * self.CELL_SIZE

                # Fondo (patrón ajedrez)
                color = C_CESPED_CLARO if (f + c) % 2 == 0 else C_CESPED_OSCURO
                pygame.draw.rect(self.screen, color, (x, y, self.CELL_SIZE, self.CELL_SIZE))

                # Entidades
                cx, cy = x + self.CELL_SIZE // 2, y + self.CELL_SIZE // 2
                if self.board.es_colmena(f, c):
                    self.dibujar_colmena(cx, cy)
                elif self.board.es_obstaculo(f, c):
                    self.dibujar_obstaculo(cx, cy)
                elif self.board.es_flor(f, c):
                    self.dibujar_flor(cx, cy, self.board.get_celda(f, c), (f, c))

                # Abeja
                if (f, c) == self.pos_abeja:
                    self.dibujar_abeja(cx, cy)

                # Selección
                if self.celda_seleccionada == (f, c):
                    s = pygame.Surface((self.CELL_SIZE, self.CELL_SIZE), pygame.SRCALPHA)
                    s.fill(C_SELECCION)
                    self.screen.blit(s, (x, y))
                    pygame.draw.rect(self.screen, (255, 255, 255), (x, y, self.CELL_SIZE, self.CELL_SIZE), 3)

        self._dibujar_texto_instrucciones()

    def _dibujar_texto_instrucciones(self):
        txt = self.font_normal.render("Clic Izq: Mover | Clic Der: Seleccionar", True, C_TEXTO_PRINCIPAL)
        self.screen.blit(txt, (self.BOARD_WIDTH // 2 - txt.get_width() // 2, self.BOARD_HEIGHT + 15))

    # === MÉTODOS DE DIBUJO DETALLADOS ===

    def dibujar_colmena(self, cx, cy):
        radio = self.CELL_SIZE // 2.5
        pygame.draw.circle(self.screen, C_COLMENA_BASE, (cx, cy), radio)
        # Capas de la colmena
        for i in range(3):
            offset = i * 8
            rect_w = radio * 1.5
            r_rect = pygame.Rect(cx - rect_w // 2, cy - 15 + offset, rect_w, 10)
            pygame.draw.rect(self.screen, C_COLMENA_DETALLE, r_rect, border_radius=5)
        # Entrada
        pygame.draw.circle(self.screen, (50, 30, 0), (cx, cy + 10), 8)

    def dibujar_obstaculo(self, cx, cy):
        # Valla detallada
        num_postes = 3
        ancho_poste = 15
        alto_poste = 62
        espaciado = 4
        ancho_total = (ancho_poste * num_postes) + (espaciado * (num_postes - 1))

        for i in range(num_postes):
            x = cx - ancho_total // 2 + i * (ancho_poste + espaciado) + 7
            r = pygame.Rect(x - ancho_poste // 2, cy - alto_poste // 2, ancho_poste, alto_poste)
            pygame.draw.rect(self.screen, C_OBSTACULO_MADERA, r)

        # Barras transversales
        pygame.draw.rect(self.screen, C_OBSTACULO_BARRAS,
                         (cx - ancho_total // 2 - 5, cy - alto_poste // 4, ancho_total + 10, 10))
        pygame.draw.rect(self.screen, C_OBSTACULO_BARRAS,
                         (cx - ancho_total // 2 - 5, cy + alto_poste // 4, ancho_total + 10, 10))

    def dibujar_flor(self, cx, cy, flor, pos):
        # Flor muerta / marchita
        if not flor.esta_viva():
            if pos not in self.flores_muertas_timer:
                self.flores_muertas_timer[pos] = self.turno

            turnos_muerta = self.turno - self.flores_muertas_timer[pos]
            if turnos_muerta > 2: return  # Desaparece

            pygame.draw.line(self.screen, (100, 80, 50), (cx, cy), (cx, cy + 20), 3)  # Tallo
            pygame.draw.circle(self.screen, (100, 80, 50), (cx, cy - 5), 8)  # Flor muerta

            if turnos_muerta >= 2:
                txt = self.font_small.render("X", True, (50, 0, 0))
                self.screen.blit(txt, (cx - 5, cy - 25))
            return

        if pos in self.flores_muertas_timer: del self.flores_muertas_timer[pos]

        pygame.draw.line(self.screen, (50, 150, 50), (cx, cy + 25), (cx, cy), 4)  # Tallo

        # Pétalos
        color = C_FLOR_SANA
        if flor.esta_polinizada(): color = C_FLOR_POLINIZADA
        if flor.pesticidas >= 2:
            color = C_PESTICIDA_GRAVE
        elif flor.pesticidas >= 1:
            color = C_PESTICIDA_LEVE

        radio_petalo = 12
        for i in range(5):
            angle = (2 * math.pi / 5) * i
            px = cx + math.cos(angle) * 15
            py = cy + math.sin(angle) * 15
            pygame.draw.circle(self.screen, color, (px, py), radio_petalo)
            pygame.draw.circle(self.screen, (200, 200, 200), (px, py), radio_petalo, 1)  # Borde

        pygame.draw.circle(self.screen, C_FLOR_CENTRO, (cx, cy), 10)

        # Partículas pesticida
        if flor.pesticidas > 0:
            for i in range(flor.pesticidas * 3):
                ox = cx + math.cos(i) * 20
                oy = cy + math.sin(i) * 20 - 20
                pygame.draw.circle(self.screen, (255, 50, 50), (ox, oy), 3)

    def dibujar_abeja(self, cx, cy):
        # Alas
        offset = math.sin(pygame.time.get_ticks() * 0.02) * 5 if self.moviendo_a_star else 0
        alas = pygame.Surface((60, 40), pygame.SRCALPHA)
        pygame.draw.ellipse(alas, C_ABEJA_ALAS, (0, 0, 25, 40))  # Ala izq
        pygame.draw.ellipse(alas, C_ABEJA_ALAS, (35, 0, 25, 40))  # Ala der
        self.screen.blit(alas, (cx - 30, cy - 25 + offset))

        # Cuerpo y rayas
        pygame.draw.rect(self.screen, C_ABEJA_CUERPO, (cx - 15, cy - 12, 30, 24), border_radius=12)
        pygame.draw.line(self.screen, C_ABEJA_RAYAS, (cx - 5, cy - 12), (cx - 5, cy + 12), 4)
        pygame.draw.line(self.screen, C_ABEJA_RAYAS, (cx + 5, cy - 12), (cx + 5, cy + 12), 4)

        # Ojos
        pygame.draw.circle(self.screen, (0, 0, 0), (cx + 8, cy - 4), 3)
        pygame.draw.circle(self.screen, (0, 0, 0), (cx + 8, cy + 4), 3)

        # Mochila
        if self.abeja.nectar_cargado > 0:
            pygame.draw.circle(self.screen, C_NECTAR, (cx - 8, cy), 6)

    def dibujar_evento_climatico(self):
        """Dibuja un banner notificando el cambio de clima."""
        if not self.mostrar_evento_clima: return

        overlay = pygame.Surface((self.WINDOW_WIDTH, 80), pygame.SRCALPHA)
        c = (50, 50, 50, 220)
        if "Sol" in self.mensaje_evento_clima:
            c = (255, 200, 0, 220)
        elif "Lluvia" in self.mensaje_evento_clima:
            c = (50, 50, 200, 220)
        overlay.fill(c)

        y = self.WINDOW_HEIGHT // 2 - 40
        self.screen.blit(overlay, (0, y))

        txt = self.font_title.render(self.mensaje_evento_clima, True, (255, 255, 255))
        self.screen.blit(txt, (self.WINDOW_WIDTH // 2 - txt.get_width() // 2, y + 25))

    def dibujar_tooltip_clima(self):
        # Tooltip
        w, h = 400, 280
        x = (self.WINDOW_WIDTH - w) // 2
        y = (self.WINDOW_HEIGHT - h) // 2

        # Fondo y sombra
        s = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 150))
        self.screen.blit(s, (0, 0))

        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, border_radius=15)

        # Botón close
        self.close_tooltip_rect = pygame.Rect(rect.right - 40, rect.top + 10, 30, 30)
        pygame.draw.circle(self.screen, (200, 50, 50), self.close_tooltip_rect.center, 14)
        self.screen.blit(self.font_bold.render("X", True, (255, 255, 255)), (rect.right - 35, rect.top + 8))

        # Contenido
        title = self.font_subtitle.render("Estados del Clima", True, C_TEXTO_PRINCIPAL)
        self.screen.blit(title, (x + (w - title.get_width()) // 2, y + 20))

        off_y = y + 80
        info = [
            ("🌧 Lluvia (10%)", "Limpia pesticidas", (52, 152, 219)),
            ("☀ Sol (15%)", "+20% Reproducción", (230, 150, 0)),
            ("☁ Normal (75%)", "Sin efectos", (100, 100, 100))
        ]

        for titulo, desc, color in info:
            t = self.font_bold.render(titulo, True, color)
            d = self.font_small.render(desc, True, C_TEXTO_PRINCIPAL)
            self.screen.blit(t, (x + 60, off_y))
            self.screen.blit(d, (x + 60, off_y + 25))
            off_y += 60

    def dibujar_panel_info(self):
        rect = pygame.Rect(self.BOARD_WIDTH, 0, self.PANEL_WIDTH, self.WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, C_FONDO_PANEL, rect)

        x = self.BOARD_WIDTH + 25
        y = 30
        self.screen.blit(self.font_title.render("BeeGame IA", True, C_TEXTO_PRINCIPAL), (x, y))

        y += 60
        self._barra(x, y, "Vida", self.abeja.vida, self.abeja.max_vida, C_VIDA)
        y += 50
        self._barra(x, y, "Energía", self.abeja.energia, self.abeja.max_energia, C_ENERGIA)
        y += 50
        self._barra(x, y, f"Mochila ({self.abeja.nectar_cargado})", self.abeja.nectar_cargado, self.abeja.capacidad_nectar, C_NECTAR)
        y += 50

        # === RECUADRO MIEL ===
        r_miel = pygame.Rect(x, y, 350, 40)
        pygame.draw.rect(self.screen, (255, 248, 220), r_miel, border_radius=8)
        pygame.draw.rect(self.screen, C_COLMENA_DETALLE, r_miel, 2, border_radius=8)

        txt_miel = self.font_bold.render(
            f"Miel en Colmena: {self.board.nectar_en_colmena} / {self.nectar_objetivo_init}", True, C_COLMENA_DETALLE)
        self.screen.blit(txt_miel, (x + 20, y + 10))

        y += 60
        self.dibujar_widget_clima(x, y)
        y += 80
        self.dibujar_widget_ia(x, y)
        y += 90
        self.dibujar_log(x, y)

    def _barra(self, x, y, texto, val, max_val, color):
        self.screen.blit(self.font_small.render(texto, True, C_TEXTO_SECUNDARIO), (x, y))
        pygame.draw.rect(self.screen, (230, 230, 230), (x, y + 20, 350, 10), border_radius=5)
        if max_val > 0:
            w = int((val / max_val) * 350)
            pygame.draw.rect(self.screen, color, (x, y + 20, w, 10), border_radius=5)

    def dibujar_widget_clima(self, x, y):
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, 350, 60), border_radius=10)
        c = C_TEXTO_PRINCIPAL
        if self.clima_actual == "Lluvia":
            c = C_ENERGIA
        elif self.clima_actual == "Sol":
            c = (200, 150, 0)

        self.screen.blit(self.font_bold.render(f"Clima: {self.clima_actual}", True, c), (x + 20, y + 20))

        # Botón ayuda
        self.help_clima_rect = pygame.Rect(x + 310, y + 15, 30, 30)
        pygame.draw.circle(self.screen, (150, 150, 255), self.help_clima_rect.center, 15)
        self.screen.blit(self.font_bold.render("?", True, (255, 255, 255)), (x + 319, y + 18))

    def dibujar_widget_ia(self, x, y):
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, 350, 70), border_radius=10)
        t = "IA Expectimax" if self.usar_expectimax else "IA Q-Learning"
        self.screen.blit(self.font_bold.render(t, True, C_TEXTO_PRINCIPAL), (x + 20, y+5))

        # Stats
        stats = f"Nodos: {self.nodos_explorados} | T: {self.tiempo_calculo_ia * 1000:.0f}ms | Err(IA): {mean(self.ia_error):.1f}"
        self.screen.blit(self.font_small.render(stats, True, C_TEXTO_SECUNDARIO), (x + 20, y + 32))
        stats = f"Err(Sem): {mean(self.error_semantic):.1f}"
        self.screen.blit(self.font_small.render(stats, True, C_TEXTO_SECUNDARIO), (x + 20, y + 50))

    def dibujar_log(self, x, y):
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, 350, 80), border_radius=5)
        txt = self.font_small.render(self.mensaje[:45], True, C_TEXTO_PRINCIPAL)
        self.screen.blit(txt, (x + 10, y + 10))

    def dibujar_botones(self):
        m = pygame.mouse.get_pos()
        for k, r in self.botones.items():
            act = r.collidepoint(m)
            c = C_BOTON_HOVER if act else (240, 240, 240)
            pygame.draw.rect(self.screen, c, r, border_radius=5)
            pygame.draw.rect(self.screen, (200, 200, 200), r, 2, border_radius=5)
            t = self.font_bold.render(k.replace("_", " ").upper(), True, C_TEXTO_PRINCIPAL)
            self.screen.blit(t, (r.centerx - t.get_width() // 2, r.centery - t.get_height() // 2))

    def _dibujar_game_over(self):
        s = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        self.screen.blit(s, (0, 0))

        color = C_CESPED_CLARO if self.resultado == self.game_manager.RES_VICTORIA else C_VIDA
        txt = self.font_title.render(self.mensaje, True, color)
        self.screen.blit(txt, (self.WINDOW_WIDTH // 2 - txt.get_width() // 2, self.WINDOW_HEIGHT // 2))