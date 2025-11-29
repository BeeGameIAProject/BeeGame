from . import board
import heapq

class Bee():
    
    def  __init__(self, life, energia=100, capacidad_nectar=50, first_move=True, name="🐝", player_name="Bee"):
        self.life = life
        self.max_vida = life
        self.energia = energia
        self.max_energia = energia
        self.nectar_cargado = 0
        self.capacidad_nectar = capacidad_nectar
        self.first_move = first_move
        self.name = name
        self.player_name = player_name
        self.daño_ataque = 10
        self.coste_movimiento = 5  # Energía que cuesta moverse
        self.coste_recoleccion = 3  # Energía que cuesta recoger néctar
        self.nectar_por_flor = 10  # Cantidad de néctar que se obtiene por flor
    
    def to_string(self):
        return f"Life: {self.life}/{self.max_vida}, Energía: {self.energia}/{self.max_energia}, Néctar: {self.nectar_cargado}/{self.capacidad_nectar}, Icono: {self.name}"
    
    def is_valid_move(self,board,start,to):
        """Comprueba si el movimiento es válido (estilo rey de ajedrez)."""
        filas = board.fila()
        columnas = board.columna()

        # Comprobar límites
        if not (0 <= to[0] < filas and 0 <= to[1] < columnas):
            return False

        if abs(start[0] - to[0]) <= 1 and abs(start[1] - to[1]) <= 1:
            return True

        return False
    
    def aplicar_daño_por_flor(self, board, posicion):
        """Aplica daño a la abeja si pasa por una flor con pesticidas."""
        from .flower import Flower
        celda = board.get_celda(posicion[0], posicion[1])
        if isinstance(celda, Flower) and celda.esta_viva():
            daño = celda.get_daño_pesticida()
            if daño > 0:
                self.bajar_vida(daño)
                return daño
        return 0

    def abeja_tocada(self):
        """Baja la vida con daño predeterminado"""
        self.life -= self.daño_ataque
        if self.life <0:
            self.life = 0
        
    def bajar_vida(self, ataque):
        """Baja la vida con daño específico"""
        self.life -= ataque
        if self.life <0:
            self.life = 0
        
    def subir_vida(self, cura):
        """Sube la vida"""
        self.life += cura
        if self.life > self.max_vida:
            self.life = self.max_vida 
    
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
        return self.life > 0
    
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
        
        # Aplicar daño si pasa por una flor con pesticidas
        daño = self.aplicar_daño_por_flor(tablero, pos_destino)
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
        
        # Polinizar la flor
        flor.polinizar()
        
        # Recoger néctar
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
    
    def descargar_nectar_en_rusc(self, tablero, posicion):
        """Descarga el néctar en el rusc si la abeja está en esa posición."""
        fila, col = posicion
        if not tablero.es_rusc(fila, col):
            return False
        
        if self.nectar_cargado == 0:
            return False
        
        tablero.agregar_nectar_al_rusc(self.nectar_cargado)
        self.nectar_cargado = 0
        return True
    
    def recuperar_energia_en_rusc(self, tablero, posicion):
        """Recupera energía y vida completa si está en el rusc."""
        fila, col = posicion
        if not tablero.es_rusc(fila, col):
            return False
        
        energia_recuperada = self.max_energia - self.energia
        vida_recuperada = self.max_vida - self.life
        self.energia = self.max_energia
        self.life = self.max_vida
        return True
    
    def calcular_ruta_a_rusc(self, tablero, pos_actual):
        """Calcula la ruta óptima al rusc usando el algoritmo A*."""
        return self.a_star(tablero, pos_actual, tablero.rusc_pos)
    
    def a_star(self, tablero, inicio, objetivo):
        """Implementa el algoritmo A* para encontrar la ruta óptima.
        Retorna una lista de posiciones desde inicio hasta objetivo.
        """
        def heuristica(pos1, pos2):
            # Distancia Manhattan
            return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        
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
            for vecino in vecinos:
                if vecino in closed_set:
                    continue
                
                if not tablero.es_transitable(vecino[0], vecino[1]):
                    continue
                
                g_nuevo = g + 1
                h = heuristica(vecino, objetivo)
                f_nuevo = g_nuevo + h
                
                nuevo_camino = camino + [vecino]
                heapq.heappush(open_set, (f_nuevo, g_nuevo, vecino, nuevo_camino))
        
        return []  # No se encontró ruta

    def printname(self):
        print(self.name)


if __name__ == "__main__":
    b = Bee(100,True)
    b.printname()
    print(b.to_string())