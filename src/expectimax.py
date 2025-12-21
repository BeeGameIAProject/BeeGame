import copy
from .game_manager import GameManager
from .heuristica import Heuristica

class GameState:
    """
    Contenedor inmutable (conceptualmente) del estado del juego.
    Se usa para simular turnos futuros sin afectar el juego real.
    """

    def __init__(self, tablero, abeja, pos_abeja, humanidad, eventos_azar, turno):
        self.tablero = tablero
        self.abeja = abeja
        self.pos_abeja = pos_abeja
        self.humanidad = humanidad
        self.eventos_azar = eventos_azar
        self.turno = turno

    def clonar(self):
        """
        Crea una copia profunda del estado.
        """
        return GameState(
            copy.deepcopy(self.tablero),
            copy.deepcopy(self.abeja),
            self.pos_abeja,  # Tupla es inmutable, no necesita copia
            copy.deepcopy(self.humanidad),
            copy.deepcopy(self.eventos_azar),
            self.turno
        )


class ExpectimaxAI:
    """
    Motor de decisión para la Abeja (Agente MAX).
    Explora el árbol de juego considerando a la Humanidad (MIN) y el Clima (CHANCE).
    """

    def __init__(self, max_depth=3, heuristica=None, nectar_objetivo=GameManager().nectar_objetivo):
        self.max_depth = max_depth
        self.nodos_explorados = 0
        self.heuristica = heuristica if heuristica else Heuristica()
        self.nectar_objetivo = nectar_objetivo

    def get_mejor_accion(self, estado):
        """Entrada principal: Retorna la mejor acción calculada."""
        self.nodos_explorados = 0
        acciones = self._get_acciones_abeja(estado)

        if not acciones:
            return None

        mejor_valor = float('-inf')
        mejor_accion = None

        for accion in acciones:
            nuevo_estado = self._aplicar_accion_abeja(estado, accion)
            # El siguiente nivel es MIN (Humanidad)
            valor = self._expectimax(nuevo_estado, 1, 'MIN')

            if valor > mejor_valor:
                mejor_valor = valor
                mejor_accion = accion

        return mejor_accion

    def _expectimax(self, estado, profundidad, tipo_agente):
        """Núcleo recursivo del algoritmo."""
        self.nodos_explorados += 1

        # Caso Base: Profundidad máxima o juego terminado
        if profundidad >= self.max_depth or self._es_terminal(estado):
            return self.heuristica.evaluar(estado)

        if tipo_agente == 'MAX':
            return self._nodo_max(estado, profundidad)
        elif tipo_agente == 'MIN':
            return self._nodo_min(estado, profundidad)
        elif tipo_agente == 'CHANCE':
            return self._nodo_chance(estado, profundidad)

        return 0.0

    def _nodo_max(self, estado, profundidad):
        """Turno de la Abeja (Maximizar)."""
        acciones = self._get_acciones_abeja(estado)
        if not acciones:
            return self.heuristica.evaluar(estado)

        mejor_valor = float('-inf')
        for accion in acciones:
            nuevo_estado = self._aplicar_accion_abeja(estado, accion)
            valor = self._expectimax(nuevo_estado, profundidad + 1, 'MIN')
            mejor_valor = max(mejor_valor, valor)

        return mejor_valor

    def _nodo_min(self, estado, profundidad):
        """Turno de la Humanidad (Minimizar)."""
        acciones = estado.humanidad.obtener_acciones_validas(estado.tablero, estado.pos_abeja)
        if not acciones:
            return self._expectimax(estado, profundidad + 1, 'CHANCE')

        peor_valor = float('inf')
        for accion in acciones:
            nuevo_estado = self._aplicar_accion_humanidad(estado, accion)
            valor = self._expectimax(nuevo_estado, profundidad + 1, 'CHANCE')
            peor_valor = min(peor_valor, valor)

        return peor_valor

    def _nodo_chance(self, estado, profundidad):
        """Turno del Entorno (Promedio ponderado)."""
        # Obtenemos probabilidades
        p_lluvia = estado.eventos_azar.prob_lluvia
        p_sol = estado.eventos_azar.prob_sol
        p_normal = 1.0 - (p_lluvia + p_sol)

        valor_esperado = 0.0

        # Iteramos los posibles climas
        escenarios = [("Lluvia", p_lluvia), ("Sol", p_sol), ("Normal", p_normal)]

        for clima, probabilidad in escenarios:
            if probabilidad > 0:
                estado_simulado = estado.clonar()
                # Forzamos el clima y aplicamos efectos
                estado_simulado.eventos_azar.clima_actual = clima
                self._aplicar_evento_clima(estado_simulado)

                # Siguiente nivel vuelve a ser MAX (profundidad aumenta)
                val = self._expectimax(estado_simulado, profundidad + 1, 'MAX')
                valor_esperado += probabilidad * val

        return valor_esperado

    # === Generación y Aplicación de Acciones ===

    def _get_acciones_abeja(self, estado):
        """Genera acciones usando la lógica de la clase Bee."""
        acciones = []
        abeja = estado.abeja
        tablero = estado.tablero
        pos = estado.pos_abeja

        # Movimiento y Recolección
        vecinos = abeja.obtener_vecinos(tablero, pos)

        for vec in vecinos:
            # Opción A: Recoger (si hay flor y energía)
            if tablero.es_flor(vec[0], vec[1]):
                flor = tablero.get_celda(vec[0], vec[1])
                if flor.esta_viva() and abeja.puede_cargar_nectar() and abeja.tiene_energia(abeja.coste_recoleccion):
                    acciones.append(('recoger', vec))

            # Opción B: Moverse (si es transitable y energía)
            # Nota: tablero.es_transitable ya maneja si es obstáculo
            if tablero.es_transitable(vec[0], vec[1]):
                if abeja.tiene_energia(abeja.coste_movimiento):
                    acciones.append(('mover', vec))

        # Descansar
        if abeja.energia < abeja.max_energia:
            acciones.append(('descansar', None))

        # Descargar (Solo en colmena)
        if tablero.es_colmena(pos[0], pos[1]) and abeja.nectar_cargado > 0:
            acciones.append(('descargar', tablero.pos_colmena))

        return acciones

    def _aplicar_accion_abeja(self, estado, accion):
        nuevo_estado = estado.clonar()
        tipo, destino = accion

        if tipo == 'recoger':
            nuevo_estado.abeja.recoger_nectar_y_polinizar(nuevo_estado.tablero, destino)
            nuevo_estado.pos_abeja = destino

        elif tipo == 'mover':
            nuevo_estado.abeja.mover(nuevo_estado.tablero, nuevo_estado.pos_abeja, destino)
            nuevo_estado.pos_abeja = destino

        elif tipo == 'descansar':
            nuevo_estado.abeja.descansar()

        elif tipo == 'descargar':
            nuevo_estado.abeja.descargar_nectar_en_colmena(nuevo_estado.tablero, destino)
            nuevo_estado.abeja.recuperar_energia_en_colmena(nuevo_estado.tablero, destino)

        return nuevo_estado

    def _aplicar_accion_humanidad(self, estado, accion):
        nuevo_estado = estado.clonar()
        nuevo_estado.humanidad.ejecutar_accion(nuevo_estado.tablero, accion, nuevo_estado.pos_abeja)
        return nuevo_estado

    def _aplicar_evento_clima(self, estado):
        estado.eventos_azar.aplicar_efectos_clima(estado.tablero)

    def _es_terminal(self, estado):
        if not estado.abeja.esta_viva(): return True
        if estado.tablero.contar_flores_vivas() == 0: return True
        if estado.tablero.nectar_en_colmena >= self.nectar_objetivo: return True
        return False