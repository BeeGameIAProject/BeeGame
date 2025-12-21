import random
from .flower import Flower

class Board:
    """
    Representa el tablero del juego (Grid).
    Contiene la colmena, flores, obstáculos y gestiona el estado del juego.
    """

    def __init__(self, filas=10, columnas=10):
        self.filas = filas
        self.columnas = columnas
        self.grid = [[None for _ in range(columnas)] for _ in range(filas)]

        # Estado del juego
        self.pos_colmena = None
        self.flores = []  # Lista de tuplas ((r, c), objeto_flor)
        self.obstaculos = []  # Lista de tuplas (r, c)
        self.nectar_en_colmena = 0
        self.turno = 0

    def inicializar_tablero(self, num_flores=15, num_obstaculos=5, pos_colmena=None):
        """
        Reinicia y puebla el tablero de forma segura usando posiciones aleatorias únicas.
        """
        # Reiniciar estado
        self.grid = [[None for _ in range(self.columnas)] for _ in range(self.filas)]
        self.flores = []
        self.obstaculos = []

        # Colocar Colmena
        if pos_colmena is None:
            self.pos_colmena = (self.filas // 2, self.columnas // 2)
        else:
            self.pos_colmena = pos_colmena
        self.grid[self.pos_colmena[0]][self.pos_colmena[1]] = "COLMENA"

        # Generar todas las coordenadas posibles para evitar colisiones
        # Reservamos la posición de inicio de la abeja (encima de la colmena)
        pos_abeja_inicio = (self.pos_colmena[0] - 1, self.pos_colmena[1])

        todas_posiciones = [
            (r, c) for r in range(self.filas) for c in range(self.columnas)
        ]

        # Eliminar posiciones reservadas si existen en la lista
        if self.pos_colmena in todas_posiciones:
            todas_posiciones.remove(self.pos_colmena)
        if pos_abeja_inicio in todas_posiciones:
            todas_posiciones.remove(pos_abeja_inicio)

        # Barajar para aleatoriedad
        random.shuffle(todas_posiciones)

        # Colocar Flores
        # Nos aseguramos de no generar más flores de las que caben
        count_flores = min(num_flores, len(todas_posiciones))
        for _ in range(count_flores):
            pos = todas_posiciones.pop()
            flor = Flower()
            self.grid[pos[0]][pos[1]] = flor
            self.flores.append((pos, flor))

        # Colocar Obstáculos
        count_obs = min(num_obstaculos, len(todas_posiciones))
        for _ in range(count_obs):
            pos = todas_posiciones.pop()
            self.grid[pos[0]][pos[1]] = "OBSTACULO"
            self.obstaculos.append(pos)

    def get_celda(self, fila, col):
        """Retorna el contenido de una celda con seguridad de límites."""
        if 0 <= fila < self.filas and 0 <= col < self.columnas:
            return self.grid[fila][col]
        return None

    def es_colmena(self, fila, col):
        return (fila, col) == self.pos_colmena

    def es_obstaculo(self, fila, col):
        return (fila, col) in self.obstaculos

    def es_flor(self, fila, col):
        celda = self.get_celda(fila, col)
        return isinstance(celda, Flower)

    def es_transitable(self, fila, col):
        """
        Determina si la abeja puede entrar en la celda.
        Transitable si: Vacío, Flor (viva/muerta) o Colmena.
        No transitable si: Obstáculo o Fuera de límites.
        """
        if not (0 <= fila < self.filas and 0 <= col < self.columnas):
            return False

        celda = self.get_celda(fila, col)

        if celda == "OBSTACULO":
            return False

        # En cualquier otro caso se puede pasar
        return True

    def colocar_obstaculo(self, fila, col):
        """Intenta colocar un obstáculo si la celda está vacía."""
        if self.grid[fila][col] is None:
            self.grid[fila][col] = "OBSTACULO"
            self.obstaculos.append((fila, col))
            return True
        return False

    def aplicar_pesticida_en(self, fila, col):
        """Delega la aplicación de pesticida a la flor en la posición."""
        celda = self.get_celda(fila, col)
        if isinstance(celda, Flower):
            celda.aplicar_pesticida()
            return True
        return False

    def agregar_nectar_a_la_colmena(self, cantidad):
        self.nectar_en_colmena += cantidad

    def get_flores_vivas(self):
        return [(pos, flor) for pos, flor in self.flores if flor.esta_viva()]

    def contar_flores_vivas(self):
        return len(self.get_flores_vivas())

    def incrementar_turno(self):
        self.turno += 1
        self.limpiar_flores_muertas()

    def get_turno(self):
        return self.turno

    def limpiar_flores_muertas(self):
        """Gestiona la desaparición de flores muertas tras el tiempo establecido."""
        # Filtramos la lista
        flores_vivas_o_recientes = []

        for pos, flor in self.flores:
            if not flor.esta_viva():
                flor.incrementar_turno_muerta()

                if flor.debe_eliminarse():
                    # Eliminar del grid
                    self.grid[pos[0]][pos[1]] = None
                    # No la añadimos a la nueva lista (se elimina)
                    continue

            # Si está viva o muerta pero reciente, se queda
            flores_vivas_o_recientes.append((pos, flor))

        self.flores = flores_vivas_o_recientes