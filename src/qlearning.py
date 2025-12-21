import random

class QLearningAI:
    """
    Agente de Aprendizaje por Refuerzo (Q-Learning).
    Utiliza una tabla (Q-Table) para aprender la mejor política de acción
    basada en recompensas acumuladas.
    """

    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.2):
        self.q_table = {}
        self.alpha = alpha  # Tasa de aprendizaje (cuánto valoramos nueva info)
        self.gamma = gamma  # Factor de descuento (importancia del futuro)
        self.epsilon = epsilon  # Probabilidad de exploración aleatoria

        # Umbrales para discretizar el estado
        self.UMBRAL_FLORES_BAJO = 5
        self.UMBRAL_FLORES_MEDIO = 10
        self.UMBRAL_ENERGIA_SEGURA = 20

    def obtener_estado(self, board, pos_abeja, abeja):
        """
        Convierte la situación compleja del juego en una tupla simple (estado).
        Reduce la dimensionalidad agrupando posiciones en cuadrantes y recursos en niveles.
        """
        filas = board.filas
        cols = board.columnas
        f, c = pos_abeja

        # Determinación del Cuadrante:
        #   0: Arriba a la izquierda
        #   1: Arriba a la derecha
        #   2: Abajo a la izquierda
        #   3: Abajo a la derecha
        fila_central, columna_central = filas / 2, cols / 2
        cuadrante = 0

        if f < fila_central:
            cuadrante = 0 if c < columna_central else 1
        else:
            cuadrante = 2 if c < columna_central else 3

        # Nivel de flores vivas (0: Escasez, 1: Medio, 2: Abundancia)
        # Accedemos directamente a la longitud de la lista filtrada
        num_flores = board.contar_flores_vivas()
        nivel_flores = 0

        if num_flores > self.UMBRAL_FLORES_MEDIO:
            nivel_flores = 2
        elif num_flores > self.UMBRAL_FLORES_BAJO:
            nivel_flores = 1

        # Estado de Energía de la Abeja (0: Crítica, 1: Segura)
        # Ahora accedemos directamente al objeto abeja pasado como argumento
        energia_status = 1 if abeja.energia > self.UMBRAL_ENERGIA_SEGURA else 0

        return (cuadrante, nivel_flores, energia_status)

    def escoger_accion(self, estado, acciones_disponibles):
        """Elige una acción basándose en la política Epsilon-Greedy."""
        if not acciones_disponibles:
            return None

        # Fase de Exploración (azar)
        if random.random() < self.epsilon:
            return random.choice(acciones_disponibles)

        # Fase de Explotación (mejor valor conocido)
        mejor_q = float('-inf')
        mejor_accion = random.choice(acciones_disponibles)  # Valor por defecto

        for accion in acciones_disponibles:
            # Usamos la tupla de acción directamente como clave
            key = (estado, accion)
            q_val = self.q_table.get(key, 0.0)

            if q_val > mejor_q:
                mejor_q = q_val
                mejor_accion = accion

        return mejor_accion

    def update(self, estado, accion, recompensa, estado_siguiente, acciones_siguientes):
        """
        Actualiza el valor Q y retorna el TD Error (cuánto aprendió en este paso).
        """
        key = (estado, accion)
        old_q = self.q_table.get(key, 0.0)

        # Calcular valor futuro
        max_q_next = 0.0
        if acciones_siguientes:
            valores_futuros = [self.q_table.get((estado_siguiente, a), 0.0) for a in acciones_siguientes]
            max_q_next = max(valores_futuros)

        # Cálculo del TD Error (Diferencia entre lo que pasó y lo que esperábamos)
        td_target = recompensa + self.gamma * max_q_next
        td_error = td_target - old_q

        # Actualizamos la tabla
        new_q = old_q + self.alpha * td_error
        self.q_table[key] = new_q

        return abs(td_error)  # Retornamos el valor absoluto del error