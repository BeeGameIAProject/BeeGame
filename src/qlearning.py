import random
import pickle  # Opcional, per guardar/carregar coneixement

class QLearningAI:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.2):
        self.q_table = {}  # Diccionari { (estat, accio): valor }
        self.alpha = alpha # Taxa d'aprenentatge
        self.gamma = gamma # Factor de descompte
        self.epsilon = epsilon # Probabilitat d'exploració

    def obtener_estado(self, board, pos_abeja):
        """
        Reduce la complejidad del tablero a una tupla.
        Estado: (cuadrante abeja, numero flores vivas, energia abeja (alta o baja))
        """
        # 1Determinamos el cuadrante de la abeja (0, 1, 2, 3)
        filas, cols = board.filas, board.columnas
        f, c = pos_abeja
        if f < filas/2 and c < cols/2: quad = 0
        elif f < filas/2 and c >= cols/2: quad = 1
        elif f >= filas/2 and c < cols/2: quad = 2
        else: quad = 3
        
        # Contamos las flores sanas
        num_flors = len([fl for pos, fl in board.flores if fl.vida > 0])
        
        # Miramos el nivel de energia de la abeja (0: critica, 1: normal)
        energia_status = 1 if board.abeja.energia > 20 else 0
        
        return (quad, num_flors, energia_status)

    def escoger_accion(self, estado, acciones_disponibles):
        if not acciones_disponibles:
            return None
            
        # Exploracion
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(acciones_disponibles)
        
        # Explotacion (mejor Q-value)
        mejor_q = -float('inf')
        mejor_accion = random.choice(acciones_disponibles)
        
        for accion in acciones_disponibles:
            # Convertimos la accion en una representacion hasheable
            key = (estado, str(accion))
            q_val = self.q_table.get(key, 0.0)
            if q_val > mejor_q:
                mejor_q = q_val
                mejor_accion = accion
                
        return mejor_accion

    def update(self, estado, accion, recompensa, estado_siguiente, acciones_siguientes):
        """Actualitzación segun la ecuación de Bellman"""
        key = (estado, str(accion))
        old_q = self.q_table.get(key, 0.0)
        
        # Calculamos max Q(s', a')
        max_q_next = 0.0
        if acciones_siguientes:
            max_q_next = max([self.q_table.get((estado_siguiente, str(a)), 0.0) for a in acciones_siguientes])
            
        # Fórmula Q-Learning
        new_q = old_q + self.alpha * (recompensa + self.gamma * max_q_next - old_q)
        self.q_table[key] = new_q 