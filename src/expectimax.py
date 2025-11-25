import copy
import random
from .bee import Bee
from .humanidad import Humanidad
from .chance_events import ChanceEvents
from .heuristica import Heuristica

class GameState():
    """
    Representa el estado completo del juego para el algoritmo Expectimax.
    """
    def __init__(self, tablero, abeja, pos_abeja, humanidad, eventos_azar, turno):
        self.tablero = tablero
        self.abeja = abeja
        self.pos_abeja = pos_abeja
        self.humanidad = humanidad
        self.eventos_azar = eventos_azar
        self.turno = turno
    
    def copy(self):
        """Crea una copia profunda del estado del juego."""
        # Copiar tablero
        nuevo_tablero = copy.deepcopy(self.tablero)
        
        # Copiar agentes
        nueva_abeja = copy.deepcopy(self.abeja)
        nueva_humanidad = copy.deepcopy(self.humanidad)
        nuevos_eventos = copy.deepcopy(self.eventos_azar)
        
        return GameState(
            nuevo_tablero,
            nueva_abeja,
            self.pos_abeja,  # La posición es una tupla inmutable
            nueva_humanidad,
            nuevos_eventos,
            self.turno
        )


class ExpectimaxAI():
    """
    Implementación del algoritmo Expectimax para el agente MAX (Abeja).
    Gestiona nodos MAX, MIN y CHANCE.
    """
    
    def __init__(self, max_depth=3, heuristica=None):
        self.max_depth = max_depth
        self.nodes_explored = 0
        self.heuristica = heuristica if heuristica else Heuristica()
    
    def get_best_action(self, estado):
        """
        Retorna la mejor acción para la abeja usando Expectimax.
        
        Args:
            estado: GameState actual
            
        Returns:
            Mejor acción a ejecutar
        """
        self.nodes_explored = 0
        acciones_posibles = self.get_acciones_abeja(estado)
        
        if not acciones_posibles:
            return None
        
        mejor_valor = float('-inf')
        mejor_accion = None
        
        for accion in acciones_posibles:
            # Simular la acción
            nuevo_estado = self.aplicar_accion_abeja(estado, accion)
            
            # Evaluar usando Expectimax (siguiente nivel es MIN)
            valor = self.expectimax(nuevo_estado, 1, 'MIN')
            
            if valor > mejor_valor:
                mejor_valor = valor
                mejor_accion = accion
        
        return mejor_accion
    
    def expectimax(self, estado, profundidad, tipo_agente):
        """
        Función recursiva del algoritmo Expectimax.
        
        Args:
            estado: GameState actual
            profundidad: Profundidad actual en el árbol
            tipo_agente: 'MAX' (Abeja), 'MIN' (Humanidad) o 'CHANCE' (Eventos)
            
        Returns:
            Valor esperado del estado
        """
        self.nodes_explored += 1
        
        # Condiciones de terminación
        if profundidad >= self.max_depth or self.es_estado_terminal(estado):
            return self.evaluar_estado(estado)
        
        # Nodo MAX (Abeja)
        if tipo_agente == 'MAX':
            return self.nodo_max(estado, profundidad)
        
        # Nodo MIN (Humanidad)
        elif tipo_agente == 'MIN':
            return self.nodo_min(estado, profundidad)
        
        # Nodo CHANCE (Eventos de azar)
        elif tipo_agente == 'CHANCE':
            return self.nodo_chance(estado, profundidad)
        
        else:
            raise ValueError(f"Tipo de agente desconocido: {tipo_agente}")
    
    def nodo_max(self, estado, profundidad):
        """
        Nodo MAX: La abeja elige la acción que maximiza el valor.
        """
        acciones = self.get_acciones_abeja(estado)
        
        if not acciones:
            return self.evaluar_estado(estado)
        
        mejor_valor = float('-inf')
        
        for accion in acciones:
            nuevo_estado = self.aplicar_accion_abeja(estado, accion)
            # Después de MAX viene MIN
            valor = self.expectimax(nuevo_estado, profundidad + 1, 'MIN')
            mejor_valor = max(mejor_valor, valor)
        
        return mejor_valor
    
    def nodo_min(self, estado, profundidad):
        """
        Nodo MIN: La humanidad elige la acción que minimiza el valor para MAX.
        """
        acciones = self.get_acciones_humanidad(estado)
        
        if not acciones:
            # Si no hay acciones, pasar a CHANCE
            return self.expectimax(estado, profundidad + 1, 'CHANCE')
        
        peor_valor = float('inf')
        
        for accion in acciones:
            nuevo_estado = self.aplicar_accion_humanidad(estado, accion)
            # Después de MIN viene CHANCE
            valor = self.expectimax(nuevo_estado, profundidad + 1, 'CHANCE')
            peor_valor = min(peor_valor, valor)
        
        return peor_valor
    
    def nodo_chance(self, estado, profundidad):
        """
        Nodo CHANCE: Calcula el valor esperado ponderado por probabilidades.
        Considera los eventos climáticos y sus efectos.
        """
        # Probabilidades de los eventos climáticos
        prob_lluvia = estado.eventos_azar.probabilidad_lluvia
        prob_sol = estado.eventos_azar.probabilidad_sol
        prob_normal = estado.eventos_azar.probabilidad_normal
        
        valor_esperado = 0.0
        
        # Escenario 1: Lluvia
        estado_lluvia = estado.copy()
        estado_lluvia.eventos_azar.clima_actual = "Lluvia"
        self.aplicar_evento_clima(estado_lluvia)
        valor_lluvia = self.expectimax(estado_lluvia, profundidad + 1, 'MAX')
        valor_esperado += prob_lluvia * valor_lluvia
        
        # Escenario 2: Sol
        estado_sol = estado.copy()
        estado_sol.eventos_azar.clima_actual = "Sol"
        self.aplicar_evento_clima(estado_sol)
        valor_sol = self.expectimax(estado_sol, profundidad + 1, 'MAX')
        valor_esperado += prob_sol * valor_sol
        
        # Escenario 3: Normal
        estado_normal = estado.copy()
        estado_normal.eventos_azar.clima_actual = "Normal"
        self.aplicar_evento_clima(estado_normal)
        valor_normal = self.expectimax(estado_normal, profundidad + 1, 'MAX')
        valor_esperado += prob_normal * valor_normal
        
        return valor_esperado
    
    def get_acciones_abeja(self, estado):
        """Retorna lista de acciones posibles para la abeja."""
        acciones = []
        
        # Acción: Moverse y recoger néctar en flores adyacentes
        direcciones = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for df, dc in direcciones:
            nueva_pos = (estado.pos_abeja[0] + df, estado.pos_abeja[1] + dc)
            fila, col = nueva_pos
            
            if 0 <= fila < estado.tablero.filas and 0 <= col < estado.tablero.columnas:
                # Si hay una flor, intentar recoger
                if estado.tablero.es_flor(fila, col):
                    flor = estado.tablero.get_celda(fila, col)
                    if flor.esta_viva() and estado.abeja.puede_cargar_nectar():
                        if estado.abeja.tiene_energia(estado.abeja.coste_recoleccion):
                            acciones.append(('recoger', nueva_pos))
                
                # Movimiento simple a casilla transitable
                elif estado.tablero.es_transitable(fila, col):
                    if estado.abeja.tiene_energia(estado.abeja.coste_movimiento):
                        acciones.append(('mover', nueva_pos))
        
        # Acción: Descansar
        if estado.abeja.energia < estado.abeja.max_energia:
            acciones.append(('descansar', None))
        
        # Acción: Descargar néctar en rusc (si está en el rusc)
        if estado.tablero.es_rusc(estado.pos_abeja[0], estado.pos_abeja[1]):
            if estado.abeja.nectar_cargado > 0:
                acciones.append(('descargar', estado.tablero.rusc_pos))
        
        return acciones
    
    def get_acciones_humanidad(self, estado):
        """Retorna lista de acciones posibles para la humanidad."""
        return estado.humanidad.obtener_acciones_validas(estado.tablero, estado.pos_abeja)
    
    def aplicar_accion_abeja(self, estado, accion):
        """Aplica una acción de la abeja y retorna el nuevo estado."""
        nuevo_estado = estado.copy()
        tipo_accion, objetivo = accion
        
        if tipo_accion == 'recoger':
            # Simular recolección (sin mover físicamente, ya está adyacente)
            nuevo_estado.abeja.recoger_nectar_y_polinizar(nuevo_estado.tablero, objetivo)
            nuevo_estado.pos_abeja = objetivo
        
        elif tipo_accion == 'mover':
            # Simular movimiento
            nuevo_estado.abeja.mover(nuevo_estado.tablero, nuevo_estado.pos_abeja, objetivo)
            nuevo_estado.pos_abeja = objetivo
        
        elif tipo_accion == 'descansar':
            nuevo_estado.abeja.descansar()
        
        elif tipo_accion == 'descargar':
            nuevo_estado.abeja.descargar_nectar_en_rusc(nuevo_estado.tablero, objetivo)
            nuevo_estado.abeja.recuperar_energia_en_rusc(nuevo_estado.tablero, objetivo)
        
        return nuevo_estado
    
    def aplicar_accion_humanidad(self, estado, accion):
        """Aplica una acción de la humanidad y retorna el nuevo estado."""
        nuevo_estado = estado.copy()
        nuevo_estado.humanidad.ejecutar_accion(nuevo_estado.tablero, accion, nuevo_estado.pos_abeja)
        return nuevo_estado
    
    def aplicar_evento_clima(self, estado):
        """Aplica los efectos del clima actual al estado."""
        estado.eventos_azar.aplicar_efecto_clima(estado.tablero)
        # Simplificación: no simular reproducción completa en el árbol
        # (demasiado costoso computacionalmente)
    
    def es_estado_terminal(self, estado):
        """Verifica si el estado es terminal (victoria o derrota)."""
        # Derrota: Abeja muerta
        if not estado.abeja.esta_viva():
            return True
        
        # Derrota: No quedan flores
        if estado.tablero.contar_flores_vivas() == 0:
            return True
        
        # Victoria: Néctar objetivo alcanzado (ejemplo: 100)
        if estado.tablero.nectar_en_rusc >= 100:
            return True
        
        return False
    
    def evaluar_estado(self, estado):
        """
        Función heurística para evaluar un estado.
        Usa la heurística completa implementada en heuristica.py.
        """
        return self.heuristica.evaluar(estado)


if __name__ == "__main__":
    print("Expectimax AI implementado")
    print("Configuración:")
    ai = ExpectimaxAI(max_depth=3)
    print(f"  - Profundidad máxima: {ai.max_depth}")
    print(f"  - Nodos MAX: Maximiza valor (Abeja)")
    print(f"  - Nodos MIN: Minimiza valor (Humanidad)")
    print(f"  - Nodos CHANCE: Valor esperado ponderado (Clima)")
