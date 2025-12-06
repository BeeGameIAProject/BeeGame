import random
import pickle  # Opcional, per guardar/carregar coneixement

class QLearningAgent:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.2):
        self.q_table = {}  # Diccionari { (estat, accio): valor }
        self.alpha = alpha # Taxa d'aprenentatge
        self.gamma = gamma # Factor de descompte
        self.epsilon = epsilon # Probabilitat d'exploració

    def obtenir_estat_abstracte(self, board, pos_abeja):
        """
        Redueix la complexitat del tauler a una clau simple (tupla).
        Estat: (Quadrant abella, Nº Flors Vives, Energia Abella (Alta/Baixa))
        """
        # 1. Determinar quadrant de l'abella (0, 1, 2, 3)
        filas, cols = board.filas, board.columnas
        f, c = pos_abeja
        if f < filas/2 and c < cols/2: quad = 0
        elif f < filas/2 and c >= cols/2: quad = 1
        elif f >= filas/2 and c < cols/2: quad = 2
        else: quad = 3
        
        # 2. Comptar flors sanes
        num_flors = len([fl for pos, fl in board.flores if fl.vida > 0])
        
        # 3. Nivell energia abella (0: crítica, 1: normal)
        energia_status = 1 if hasattr(board, 'abeja') and board.abeja.energia > 20 else 0
        
        return (quad, num_flors, energia_status)

    def triar_accio(self, estat, accions_disponibles):
        if not accions_disponibles:
            return None
            
        # Exploració (Epsilon-greedy)
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(accions_disponibles)
        
        # Explotació (Millor Q-value)
        millor_q = -float('inf')
        millor_accio = random.choice(accions_disponibles)
        
        for accio in accions_disponibles:
            # Convertim l'acció a una representació hashable (tipus, (f,c))
            key = (estat, str(accio)) 
            q_val = self.q_table.get(key, 0.0)
            if q_val > millor_q:
                millor_q = q_val
                millor_accio = accio
                
        return millor_accio

    def update(self, estat, accio, reward, estat_seguent, accions_seguents):
        """Actualització segons l'equació de Bellman"""
        key = (estat, str(accio))
        old_q = self.q_table.get(key, 0.0)
        
        # Calcular max Q(s', a')
        max_q_next = 0.0
        if accions_seguents:
            max_q_next = max([self.q_table.get((estat_seguent, str(a)), 0.0) for a in accions_seguents])
            
        # Fórmula Q-Learning
        new_q = old_q + self.alpha * (reward + self.gamma * max_q_next - old_q)
        self.q_table[key] = new_q