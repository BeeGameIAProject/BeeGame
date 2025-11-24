import random
from flower import Flower

class Board():
    """
    Representa el tablero del juego con dimensiones N×N.
    Contiene el rusc, flores, obstáculos y gestiona el estado del juego.
    """
    def __init__(self, filas=10, columnas=10):
        self.filas = filas
        self.columnas = columnas
        self.grid = [[None for _ in range(columnas)] for _ in range(filas)]
        self.rusc_pos = None  # Posición de la colmena
        self.flores = []  # Lista de flores en el tablero
        self.obstaculos = []  # Lista de posiciones con obstáculos
        self.nectar_en_rusc = 0  # Néctar acumulado en la colmena
        self.turno = 0  # Contador de turnos
        
    def fila(self):
        return self.filas
    
    def columna(self):
        return self.columnas
    
    def inicializar_tablero(self, num_flores=15, num_obstaculos=5, rusc_pos=None):
        """
        Inicializa el tablero con el rusc, flores y obstáculos.
        
        Args:
            num_flores: Número de flores a colocar
            num_obstaculos: Número de obstáculos a colocar
            rusc_pos: Posición del rusc (si None, se coloca en el centro)
        """
        # Limpiar tablero
        self.grid = [[None for _ in range(self.columnas)] for _ in range(self.filas)]
        self.flores = []
        self.obstaculos = []
        
        # Colocar rusc (colmena)
        if rusc_pos is None:
            self.rusc_pos = (self.filas // 2, self.columnas // 2)
        else:
            self.rusc_pos = rusc_pos
        self.grid[self.rusc_pos[0]][self.rusc_pos[1]] = "RUSC"
        
        # Colocar flores
        flores_colocadas = 0
        while flores_colocadas < num_flores:
            fila = random.randint(0, self.filas - 1)
            col = random.randint(0, self.columnas - 1)
            if self.grid[fila][col] is None:
                flor = Flower()
                self.grid[fila][col] = flor
                self.flores.append(((fila, col), flor))
                flores_colocadas += 1
        
        # Colocar obstáculos
        obstaculos_colocados = 0
        while obstaculos_colocados < num_obstaculos:
            fila = random.randint(0, self.filas - 1)
            col = random.randint(0, self.columnas - 1)
            if self.grid[fila][col] is None:
                self.grid[fila][col] = "OBSTACULO"
                self.obstaculos.append((fila, col))
                obstaculos_colocados += 1
    
    def get_celda(self, fila, col):
        """Retorna el contenido de una celda."""
        if 0 <= fila < self.filas and 0 <= col < self.columnas:
            return self.grid[fila][col]
        return None
    
    def es_rusc(self, fila, col):
        """Verifica si la posición es el rusc."""
        return (fila, col) == self.rusc_pos
    
    def es_obstaculo(self, fila, col):
        """Verifica si la posición es un obstáculo."""
        return (fila, col) in self.obstaculos
    
    def es_flor(self, fila, col):
        """Verifica si la posición contiene una flor."""
        celda = self.get_celda(fila, col)
        return isinstance(celda, Flower)
    
    def es_transitable(self, fila, col):
        """Verifica si la posición es transitable (no obstáculo)."""
        if not (0 <= fila < self.filas and 0 <= col < self.columnas):
            return False
        celda = self.get_celda(fila, col)
        # Las flores siempre son transitables, solo los obstáculos no lo son
        return celda != "OBSTACULO"
    
    def colocar_obstaculo(self, fila, col):
        """Coloca un obstáculo en la posición especificada."""
        if self.grid[fila][col] is None:
            self.grid[fila][col] = "OBSTACULO"
            self.obstaculos.append((fila, col))
            return True
        return False
    
    def aplicar_pesticida_en(self, fila, col):
        """Aplica pesticida en una posición con flor."""
        celda = self.get_celda(fila, col)
        if isinstance(celda, Flower):
            celda.aplicar_pesticida()
            return True
        return False
    
    def agregar_nectar_al_rusc(self, cantidad):
        """Agrega néctar a la colmena."""
        self.nectar_en_rusc += cantidad
    
    def get_flores_vivas(self):
        """Retorna lista de flores vivas en el tablero."""
        return [(pos, flor) for pos, flor in self.flores if flor.esta_viva()]
    
    def contar_flores_vivas(self):
        """Retorna el número de flores vivas."""
        return len(self.get_flores_vivas())
    
    def incrementar_turno(self):
        """Incrementa el contador de turnos."""
        self.turno += 1
        # Incrementar contador de flores muertas y eliminarlas si es necesario
        self.limpiar_flores_muertas()
    
    def get_turno(self):
        """Retorna el turno actual."""
        return self.turno
    
    def limpiar_flores_muertas(self):
        """Elimina flores muertas que llevan 1 turno muertas."""
        flores_a_eliminar = []
        for pos, flor in self.flores:
            if not flor.esta_viva():
                flor.incrementar_turno_muerta()
                if flor.debe_eliminarse():
                    flores_a_eliminar.append((pos, flor))
                    # Limpiar del grid
                    self.grid[pos[0]][pos[1]] = None
        
        # Eliminar de la lista de flores
        for item in flores_a_eliminar:
            if item in self.flores:
                self.flores.remove(item)
    
    def mostrar_tablero(self):
        """Imprime una representación visual del tablero."""
        print("\n" + "="*50)
        print(f"Turno: {self.turno} | Néctar en Rusc: {self.nectar_en_rusc}")
        print("="*50)
        for i in range(self.filas):
            fila_str = ""
            for j in range(self.columnas):
                celda = self.grid[i][j]
                if celda is None:
                    fila_str += "⬜ "
                elif celda == "RUSC":
                    fila_str += "🏠 "
                elif celda == "OBSTACULO":
                    fila_str += "🪨 "
                elif isinstance(celda, Flower):
                    fila_str += celda.get_symbol() + " "
                else:
                    fila_str += "? "
            print(fila_str)
        print("="*50 + "\n")