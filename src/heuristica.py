"""
Módulo de heurística para el algoritmo Expectimax.
Implementa la función de evaluación H(s) para determinar la utilidad de un estado.
"""

class Heuristica():
    """
    Función heurística completa para evaluar estados del juego.
    
    Esta clase combina múltiples factores (sub-heurísticas) para generar un valor numérico
    que representa qué tan favorable es un estado para la Abeja.

    Fórmula General:
    H(s) = H_tablero + H_agente + H_progreso + H_proximidad + H_amenaza - H_obstaculos
    """
    
    def __init__(self, w1=10, w2=8, w3=15, w4=5, w5=3, w6=2, w7=1, w8=5, w9=5):
        """
        Inicializa los pesos de la heurística.
        Estos pesos determinan la importancia relativa de cada factor en la toma de decisiones.

        Args:
            w1 (float): Peso para flores vivas (mantenimiento del ecosistema).
            w2 (float): Peso para flores polinizadas (objetivo secundario).
            w3 (float): Peso para néctar en la colmena (objetivo principal).
            w4 (float): Peso para néctar cargado en el inventario de la abeja.
            w5 (float): Peso para la salud (vida) de la abeja.
            w6 (float): Peso para la energía (movimiento) de la abeja.
            w7 (float): Peso para la proximidad a los objetivos inmediatos.
            w8 (float): Peso para la evaluación de amenazas o densidad de recursos seguros.
            w9 (float): Peso para la penalización por obstáculos en el tablero.
        """
        self.w1 = w1
        self.w2 = w2
        self.w3 = w3
        self.w4 = w4
        self.w5 = w5
        self.w6 = w6
        self.w7 = w7
        self.w8 = w8
        self.w9 = w9
    
    def evaluar(self, estado):
        """
        Evalúa un estado del juego y retorna su valor heurístico numérico.

        El algoritmo Expectimax usará este valor para comparar nodos hoja.
        Un valor alto favorece a MAX (Abeja), un valor bajo favorece a MIN (Humanidad).

        Args:
            estado: Objeto que contiene toda la información del juego.

        Returns:
            float: Valor heurístico del estado.
        """
        # === Estados terminales (condiciones de fin de juego) ===
        # Derrota: si la abeja muere, es el peor estado posible
        # Retornamos un negativo muy grande (equivalente a -infinito)
        if not estado.abeja.esta_viva():
            return -100000

        # Derrota: si no quedan flores, el ecosistema colapsa
        if estado.tablero.contar_flores_vivas() == 0:
            return -100000

        # Victoria: si se alcanza el objetivo de néctar en la colmena
        # Retornamos un positivo muy grande (equivalente a +infinito)
        nectar_objetivo = 100
        if estado.tablero.nectar_en_colmena >= nectar_objetivo:
            return 100000
        
        # === Cálculo de componentes heurísticos ==
        h_tablero = self.h_tablero(estado)  # Estado del entorno (flores)
        h_agent = self.h_agent(estado)  # Estado interno (salud/energía)
        h_progreso = self.h_progreso(estado)  # Avance hacia la victoria
        h_proximidad = self.h_proximidad(estado)  # Distancia a la meta inmediata
        h_amenaza = self.h_amenaza(estado)  # Disponibilidad de recursos seguros
        h_obstaculos = self.h_obstaculos(estado)  # Cantidad de bloqueos
        
        # === Combinamos los componentes con pesos ===
        # Nota sobre H_obstaculos:
        #   Se RESTA porque la presencia de obstáculos es negativa para la abeja.
        #   Como MIN intenta minimizar este valor total, MIN intentará maximizar h_obstaculos.
        valor_total = h_tablero + h_agent + h_progreso + h_proximidad + h_amenaza - h_obstaculos
        
        return valor_total
    
    def h_tablero(self, estado):
        """
        H_tablero: Valoración de la salud general del ecosistema.

        Estrategia:
        - Premiar la cantidad de flores vivas y polinizadas.
        - Penalizar fuertemente la presencia de pesticidas.
        """
        valor = 0
        
        # Contamos las flores en diferentes estados
        flores_vivas = 0
        flores_polinizadas = 0
        flores_contaminadas = 0
        total_pesticidas = 0
        
        for pos, flor in estado.tablero.flores:
            if flor.esta_viva():
                flores_vivas += 1
                
                if flor.esta_polinizada():
                    flores_polinizadas += 1

                # Detectamos contaminación antes de que la flor muera
                if flor.pesticidas > 0:
                    flores_contaminadas += 1
                    total_pesticidas += flor.pesticidas
        
        # Valoramos las flores vivas (más flores = mejor)
        valor += self.w1 * flores_vivas
        
        # Valoramos las flores polinizadas (importante para reproducción)
        valor += self.w2 * flores_polinizadas
        
        # Penalizamos las flores contaminadas
        valor -= 5 * flores_contaminadas
        
        # Penalizamos los pesticidas totales
        valor -= 3 * total_pesticidas
        
        return valor
    
    def h_agent(self, estado):
        """
        H_agent: Valoración de la supervivencia y capacidad operativa de la abeja.

        Estrategia:
        - Mantener vida y energía altas.
        - Penalización no lineal (muy fuerte) si los valores caen a niveles críticos,
          forzando a la IA a priorizar la supervivencia sobre la recolección en esos casos.
        """
        valor = 0
        
        # Normalizamos la vida (0-1) para aplicar los pesos
        ratio_vida = estado.abeja.vida / estado.abeja.max_vida
        valor += self.w5 * ratio_vida * 100
        
        # Normalizamos la energía (0-1)
        ratio_energia = estado.abeja.energia / estado.abeja.max_energia
        valor += self.w6 * ratio_energia * 100
        
        # Penalizamos fuertemente si la vida es crítica (<30%)
        if ratio_vida < 0.3:
            valor -= 500  # Prioridad absoluta: curarse/huir
        
        # Penalizamos si la energía es muy baja (<20%)
        if ratio_energia < 0.2:
            valor -= 200  # Prioridad alta: descansar/comer
        
        return valor
    
    def h_progreso(self, estado):
        """
        H_progreso: Medición del avance hacia la condición de victoria.

        Distingue entre:
        1. Néctar asegurado (en colmena).
        2. Néctar potencial (en inventario).
        3. Bonus por hitos (25%, 50%, 75%) para incentivar el cierre del juego.
        """
        valor = 0
        
        # Néctar asegurado (w3 es el peso más alto)
        valor += self.w3 * estado.tablero.nectar_en_colmena
        
        # Néctar cargado (potencial para depositar)
        valor += self.w4 * estado.abeja.nectar_cargado
        
        # Bonus si está cerca de completar el objetivo
        nectar_objetivo = 100
        progreso = (estado.tablero.nectar_en_colmena + estado.abeja.nectar_cargado) / nectar_objetivo
        
        if progreso > 0.75:
            valor += 1000  # Muy cerca de ganar
        elif progreso > 0.5:
            valor += 500   # A mitad de camino
        elif progreso > 0.25:
            valor += 200   # Buen progreso
        
        return valor
    
    def h_proximidad(self, estado):
        """
        H_proximidad: Heurística dinámica basada en el estado interno.

        Comportamiento:
        - Modo Recolección: Si el inventario está bajo, busca la flor sana más cercana.
        - Modo Entrega: Si el inventario está lleno (>60%), busca la colmena.

        Usamos distancia inversa (1/d) para que valores más altos signifiquen "más cerca".
        """
        valor = 0
        pos_abeja = estado.pos_abeja
        
        # Si la abeja está llena (o casi), su meta es la colmena
        # Usamos 60% de capacidad como umbral
        capacidad = estado.abeja.capacidad_nectar

        # Caso 1: La abeja tiene suficiente néctar, debe volver a casa
        if estado.abeja.nectar_cargado >= (capacidad * 0.6):
            distancia_colmena = self.distancia_chebyshev(pos_abeja, estado.tablero.pos_colmena)
            
            # Cuanto más cerca de la colmena, mejor (valor inverso)
            if distancia_colmena > 0:
                valor += (20.0 / distancia_colmena) * self.w7
            else:
                valor += 50 * self.w7 # Recompensa por estar en la colmena
        
        # # Caso 2: La abeja necesita recolectar, su meta es la flor sana más cercana
        else:
            flores_vivas = estado.tablero.get_flores_vivas()
            
            if flores_vivas:
                distancia_min = float('inf')
                for pos_flor, flor in flores_vivas:
                    # Solo consideramos flores con néctar y sin pesticidas graves si es posible
                    if flor.pesticidas == 0:
                        dist = self.distancia_chebyshev(pos_abeja, pos_flor)
                        if dist < distancia_min:
                            distancia_min = dist
                
                if distancia_min != float('inf') and distancia_min > 0:
                    valor += (10.0 / distancia_min) * self.w7
                elif distancia_min == 0:
                    valor += 20 * self.w7 # Recompensa por estar en una flor
        
        return valor

    def h_amenaza(self, estado):
        """
        H_amenaza: Evaluación de densidad de oportunidades seguras.

        Calcula qué tan cerca está la abeja de flores sanas.
        Esto actúa como una medida de "seguridad de recursos". Si el jugador MIN (Humanidad)
        destruye una flor cercana a la abeja, este valor disminuye, por lo tanto,
        el algoritmo detecta esa acción como negativa para MAX.
        """
        h_amenaza = 0
        pos_abeja = estado.pos_abeja
        
        for pos_flor, flor in estado.tablero.flores:
            if flor.esta_viva() and flor.pesticidas == 0:
                dist = self.distancia_chebyshev(pos_abeja, pos_flor)
                # Evitamos división por cero y limitamos la distancia mínima a 1
                if dist < 1: dist = 1
                h_amenaza += (10.0 / dist)
        
        return h_amenaza * self.w8

    def h_obstaculos(self, estado):
        """
        H_obstaculos: Conteo de obstáculos en el tablero.

        Esta función retorna un valor positivo basado en la cantidad de obstáculos.
        En la función `evaluar`, este valor se RESTA.
        Esto significa que para el jugador MIN (que busca minimizar el valor total),
        crear obstáculos es una buena estrategia.
        """
        n_obstaculos = len(estado.tablero.obstaculos)
        return n_obstaculos * self.w9
    
    def distancia_chebyshev(self, pos1, pos2):
        """Calcula la distancia Chebyshev entre dos posiciones."""
        return max(abs(pos1[0] - pos2[0]), abs(pos1[1] - pos2[1]))
    
    def to_string(self):
        """Retorna una representación legible de la configuración actual de pesos."""
        return f"""Configuración de Pesos Heurísticos:
              w1 (Flores Vivas):       {self.w1}
              w2 (Flores Polinizadas): {self.w2}
              w3 (Néctar Colmena):     {self.w3} [Prioridad Alta]
              w4 (Néctar Inventario):  {self.w4}
              w5 (Vida Abeja):         {self.w5}
              w6 (Energía Abeja):      {self.w6}
              w7 (Proximidad):         {self.w7}
              w8 (Amenaza/Recursos):   {self.w8}
              w9 (Obstáculos):         {self.w9}"""


if __name__ == "__main__":
    h = Heuristica()
    print("--- Sistema de Heurística Inicializado ---")
    print(h.to_string())
    print("\nFórmula de Evaluación:")
    print("H(s) = H_tablero + H_agent + H_progres + H_proximidad + H_amenaza - H_obstaculos")