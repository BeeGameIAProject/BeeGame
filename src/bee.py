import heapq
import random
from .flower import Flower

class Bee:
    """
    Representa a la abeja (MAX).
    Gestiona sus estadísticas vitales, inventario y movimiento.
    """

    def __init__(self, vida, energia=100, capacidad_nectar=30, factor_a_star=0.5):
        self.vida = vida
        self.max_vida = vida
        self.energia = energia
        self.max_energia = energia

        # Inventario
        self.nectar_cargado = 0
        self.capacidad_nectar = capacidad_nectar

        # Costes y estadísticas
        self.daño_ataque = 10
        self.coste_movimiento = 5
        self.coste_recoleccion = 3
        self.nectar_por_flor = 10

        # Navegación
        self.factor_a_star = factor_a_star

    def esta_viva(self):
        """Indica si la abeja tiene vida mayor a 0."""
        return self.vida > 0

    def tiene_energia(self, cantidad):
        """Verifica si hay suficiente energía para una acción."""
        return self.energia >= cantidad

    def puede_cargar_nectar(self):
        """Verifica si queda espacio en el inventario."""
        return self.nectar_cargado < self.capacidad_nectar

    def recibir_daño(self, cantidad):
        """Reduce la vida asegurando que no baje de 0."""
        self.vida -= cantidad
        if self.vida < 0:
            self.vida = 0

    def recuperar_vida(self, cantidad):
        """Aumenta la vida asegurando que no supere el máximo."""
        self.vida += cantidad
        if self.vida > self.max_vida:
            self.vida = self.max_vida

    def recuperar_energia(self, cantidad):
        """Aumenta la energía asegurando que no supere el máximo."""
        self.energia += cantidad
        if self.energia > self.max_energia:
            self.energia = self.max_energia

    def es_movimiento_valido(self, tablero, inicio, destino):
        """
        Verifica si el movimiento es válido geométricamente (distancia 1).
        """
        filas = tablero.filas
        columnas = tablero.columnas

        # Verificar límites del tablero
        if not (0 <= destino[0] < filas and 0 <= destino[1] < columnas):
            return False

        # Verificar distancia Chebyshev
        dist_fila = abs(inicio[0] - destino[0])
        dist_col = abs(inicio[1] - destino[1])

        return max(dist_fila, dist_col) <= 1

    def obtener_vecinos(self, tablero, posicion):
        """
        Retorna coordenadas adyacentes válidas.
        """
        fila_actual, col_actual = posicion
        vecinos = []

        # 8 direcciones posibles (cambios en fila y columna)
        direcciones = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]

        for delta_fila, delta_columna in direcciones:
            nueva_fila = fila_actual + delta_fila
            nueva_columna = col_actual + delta_columna

            # Verificar que las nuevas coordenadas estén dentro del tablero
            if 0 <= nueva_fila < tablero.filas and 0 <= nueva_columna < tablero.columnas:
                vecinos.append((nueva_fila, nueva_columna))

        return vecinos

    def aplicar_daño_por_flor(self, tablero, posicion):
        """Si la flor en la posición tiene pesticida, aplica daño a la abeja."""
        celda = tablero.get_celda(posicion[0], posicion[1])
        if isinstance(celda, Flower) and celda.esta_viva():
            daño = celda.get_daño_pesticida()
            if daño > 0:
                self.recibir_daño(daño)
                return daño
        return 0

    def mover(self, tablero, pos_actual, pos_destino):
        """Intenta mover la abeja y aplica costes/efectos."""
        # Validaciones
        if not self.tiene_energia(self.coste_movimiento):
            return False

        if not self.es_movimiento_valido(tablero, pos_actual, pos_destino):
            return False

        if not tablero.es_transitable(pos_destino[0], pos_destino[1]):
            return False

        # Aplicar movimiento
        self.aplicar_daño_por_flor(tablero, pos_destino)

        if pos_actual != pos_destino:
            self.energia -= self.coste_movimiento

        return True

    def recoger_nectar_y_polinizar(self, tablero, posicion):
        """Recoge néctar de una flor y la poliniza."""
        if not self.tiene_energia(self.coste_recoleccion):
            return False

        if not self.puede_cargar_nectar():
            return False

        fila, col = posicion
        celda = tablero.get_celda(fila, col)

        if not isinstance(celda, Flower) or not celda.esta_viva():
            return False

        # Ejecutar acción
        celda.polinizar()

        cantidad = min(self.nectar_por_flor, self.capacidad_nectar - self.nectar_cargado)
        self.nectar_cargado += cantidad
        self.energia -= self.coste_recoleccion

        return True

    def descansar(self, cantidad=20):
        """Recupera energía."""
        self.recuperar_energia(cantidad)
        return True

    def descargar_nectar_en_colmena(self, tablero, posicion):
        """Vacía la mochila en la colmena."""
        if tablero.es_colmena(posicion[0], posicion[1]) and self.nectar_cargado > 0:
            tablero.agregar_nectar_a_la_colmena(self.nectar_cargado)
            self.nectar_cargado = 0
            return True
        return False

    def recuperar_energia_en_colmena(self, tablero, posicion):
        """Restaura stats al máximo en la colmena."""
        if tablero.es_colmena(posicion[0], posicion[1]):
            self.energia = self.max_energia
            self.vida = self.max_vida
            return True
        return False

    def calcular_ruta_a_colmena(self, tablero, pos_actual, factor_aleatorio=None):
        """Calcula ruta A* hacia la colmena."""
        destino = tablero.pos_colmena
        ruido = self.factor_a_star if factor_aleatorio is None else factor_aleatorio
        return self._a_star(tablero, pos_actual, destino, ruido)

    def _a_star(self, tablero, inicio, objetivo, factor_ruido):
        """
        Algoritmo A* interno.
        Usa una cola de prioridad para encontrar el camino óptimo con ruido añadido.
        """
        # Cada elemento de frontera: (coste_total_estimado, pasos_g, posicion_actual, camino_recorrido)
        frontera = []
        heapq.heappush(frontera, (0, 0, inicio, [inicio]))

        visitados = set()

        while frontera:
            _, coste_g, actual, camino = heapq.heappop(frontera)

            if actual == objetivo:
                return camino

            if actual in visitados:
                continue

            visitados.add(actual)

            # Explorar vecinos
            for vecino in self.obtener_vecinos(tablero, actual):
                if vecino in visitados:
                    continue

                # Bloquear obstaculos (excepto si es el destino final, por si acaso)
                if not tablero.es_transitable(vecino[0], vecino[1]) and vecino != objetivo:
                    continue

                nuevo_g = coste_g + 1

                # Heurística: Distancia Chebyshev
                h = max(abs(vecino[0] - objetivo[0]), abs(vecino[1] - objetivo[1]))

                # Inyección de aleatoriedad para simular comportamiento orgánico
                ruido = random.uniform(0, factor_ruido)
                nuevo_f = nuevo_g + h + ruido

                nuevo_camino = camino + [vecino]
                heapq.heappush(frontera, (nuevo_f, nuevo_g, vecino, nuevo_camino))

        return []  # No se encontró ningún camino