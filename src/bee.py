import heapq
from .flower import Flower
import random # necesario para A* con aleatoriedad

class Bee():
    
    def  __init__(self, vida, energia=100, capacidad_nectar=30, first_move=True, factor_a_star=0.5):
        self.vida = vida
        self.max_vida = vida
        self.energia = energia
        self.max_energia = energia
        self.nectar_cargado = 0
        self.capacidad_nectar = capacidad_nectar
        self.daño_ataque = 10
        self.coste_movimiento = 5  # Energía que cuesta moverse
        self.coste_recoleccion = 3  # Energía que cuesta recoger néctar
        self.nectar_por_flor = 10  # Cantidad de néctar que se obtiene por flor
        self.factor_a_star = factor_a_star  # Controla cuánta aleatoriedad se inyecta en A*

    def is_valid_move(self,board,start,to):
        """Comprueba si el movimiento es válido (estilo rey de ajedrez)."""
        filas = board.fila()
        columnas = board.columna()

        # Comprobamos los límites
        if not (0 <= to[0] < filas and 0 <= to[1] < columnas):
            return False

        if abs(start[0] - to[0]) <= 1 and abs(start[1] - to[1]) <= 1:
            return True

        return False
    
    def aplicar_daño_por_flor(self, board, posicion):
        """Aplica daño a la abeja si pasa por una flor con pesticidas."""
        celda = board.get_celda(posicion[0], posicion[1])
        if isinstance(celda, Flower) and celda.esta_viva():
            daño = celda.get_daño_pesticida()
            if daño > 0:
                self.bajar_vida(daño)
                return daño
        return 0

    def abeja_tocada(self):
        """Baja la vida con daño predeterminado"""
        self.vida -= self.daño_ataque
        if self.vida <0:
            self.vida = 0
        
    def bajar_vida(self, ataque):
        """Baja la vida con daño específico"""
        self.vida -= ataque
        if self.vida <0:
            self.vida = 0
        
    def subir_vida(self, cura):
        """Sube la vida"""
        self.vida += cura
        if self.vida > self.max_vida:
            self.vida = self.max_vida
    
    def next_moves(self, board, position):
        """Retorna los siguientes movimientos posibles"""
        m = []
        filas = board.fila()
        columnas = board.columna()
        fila, col = position

        # Movimientos posibles
        direcciones = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        m = [
            (fila + df, col + dc)
            for df, dc in direcciones
            if 0 <= fila + df < filas and 0 <= col + dc < columnas
        ]
        return m

    def esta_viva(self):
        """Devuelve True si la abeja sigue viva."""
        return self.vida > 0
    
    def tiene_energia(self, cantidad):
        """Verifica si la abeja tiene suficiente energía."""
        return self.energia >= cantidad
    
    def puede_cargar_nectar(self):
        """Verifica si la abeja puede cargar más néctar."""
        return self.nectar_cargado < self.capacidad_nectar
    
    def mover(self, tablero, pos_actual, pos_destino):
        """Mueve la abeja a una nueva posición. Retorna True si fue exitoso."""
        if not self.tiene_energia(self.coste_movimiento):
            return False
        
        if not self.is_valid_move(tablero, pos_actual, pos_destino):
            return False
        
        if not tablero.es_transitable(pos_destino[0], pos_destino[1]):
            return False
        
        # Aplicamos daño si pasa por una flor con pesticidas
        self.aplicar_daño_por_flor(tablero, pos_destino)
        if pos_actual[0] != pos_destino[0] or pos_actual[1] != pos_destino[1]:
            self.energia -= self.coste_movimiento
        return True
    
    def recoger_nectar_y_polinizar(self, tablero, posicion):
        """Recoge néctar de una flor y la poliniza. Retorna True si fue exitoso."""
        if not self.tiene_energia(self.coste_recoleccion):
            return False
        
        if not self.puede_cargar_nectar():
            return False
        
        fila, col = posicion
        if not tablero.es_flor(fila, col):
            return False
        
        flor = tablero.get_celda(fila, col)
        if not flor.esta_viva():
            return False
        
        # Poliniza la flor
        flor.polinizar()
        
        # Recoge néctar
        cantidad_recolectada = min(self.nectar_por_flor, self.capacidad_nectar - self.nectar_cargado)
        self.nectar_cargado += cantidad_recolectada
        self.energia -= self.coste_recoleccion
        
        return True
    
    def descansar(self, cantidad=20):
        """Recupera energía descansando."""
        self.energia += cantidad
        if self.energia > self.max_energia:
            self.energia = self.max_energia
        return True
    
    def descargar_nectar_en_colmena(self, tablero, posicion):
        """Descarga el néctar en la colmena si la abeja está en esa posición."""
        fila, col = posicion
        if not tablero.es_colmena(fila, col):
            return False
        
        if self.nectar_cargado == 0:
            return False
        
        tablero.agregar_nectar_a_la_colmena(self.nectar_cargado)
        self.nectar_cargado = 0
        return True
    
    def recuperar_energia_en_colmena(self, tablero, posicion):
        """Recupera energía y vida completa si está en la colmena."""
        fila, col = posicion
        if not tablero.es_colmena(fila, col):
            return False
        
        self.energia = self.max_energia
        self.vida = self.max_vida
        return True
    
    def calcular_ruta_a_colmena(self, tablero, pos_actual, factor_aleatorio=None, destino=None):
        """Calcula la ruta a la colmena usando A* con aleatoriedad controlada."""

        factor = self.factor_a_star if factor_aleatorio is None else factor_aleatorio
        if destino is None:
            destino = tablero.pos_colmena
        return self.a_star_random(tablero, pos_actual, destino, factor_aleatorio=factor)
    
    # A* con aleatoriedad
    def a_star_random(self, tablero, inicio, objetivo, factor_aleatorio=0.5):
        """Implementa el algoritmo A* para encontrar la ruta óptima.
        Retorna una lista de posiciones desde inicio hasta objetivo.
        """
        def heuristica(pos1, pos2):
            # Distancia Chebyshev (porque la abeja se puede mover en 8 direcciones)
            return max(abs(pos1[0] - pos2[0]), abs(pos1[1] - pos2[1]))
        
        # Cola de prioridad: (f, g, posicion, camino)
        open_set = []
        heapq.heappush(open_set, (0, 0, inicio, [inicio]))
        
        # Conjunto de nodos visitados
        closed_set = set()
        
        while open_set:
            f, g, actual, camino = heapq.heappop(open_set)
            
            if actual == objetivo:
                return camino
            
            if actual in closed_set:
                continue
            
            closed_set.add(actual)
            
            # Explorar vecinos
            vecinos = self.next_moves(tablero, actual)

            # Mezclar los vecinos para que el orden de evaluación
            # para que no sea siempre arriba, abajo, izquerda, derecha
            for vecino in vecinos:
                if vecino in closed_set:
                    continue
                
                if not tablero.es_transitable(vecino[0], vecino[1]):
                    continue
                
                g_nuevo = g + 1
                h = heuristica(vecino, objetivo)

                # Aleatoriedad:
                # generamos un coste extra aleatorio, esto aplica la aleatoriedad
                # el factor_aleatorio hasta como de mal puede jugar, mas alto, peor jugará, si toca el numero mas alto
                ruido = random.uniform(0, factor_aleatorio)
                f_nuevo = g_nuevo + h + ruido
                
                nuevo_camino = camino + [vecino]
                heapq.heappush(open_set, (f_nuevo, g_nuevo, vecino, nuevo_camino))
        
        return []  # No se encontró ruta
