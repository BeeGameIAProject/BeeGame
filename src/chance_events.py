import random
from .flower import Flower

class ChanceEvents:
    """
    Gestiona los eventos aleatorios del entorno: Clima y Reproducción.
    Actúa como el nodo 'CHANCE' en la lógica del juego.
    """

    def __init__(self):
        # Configuración de Clima
        self.frecuencia_clima = 4
        self.prob_lluvia = 0.10
        self.prob_sol = 0.15

        # Configuración de Reproducción
        self.prob_reproduccion_base = 0.20
        self.bonus_reproduccion_sol = 0.20

        # Estado
        self.clima_actual = "Normal"

    def debe_activar_evento(self, turno_actual):
        """Determina si en este turno corresponde ejecutar eventos climáticos."""
        return turno_actual > 0 and turno_actual % self.frecuencia_clima == 0

    def generar_nuevo_clima(self):
        """Calcula aleatoriamente el nuevo estado del clima."""
        rand = random.random()

        if rand < self.prob_lluvia:
            self.clima_actual = "Lluvia"
        elif rand < self.prob_lluvia + self.prob_sol:
            self.clima_actual = "Sol"
        else:
            self.clima_actual = "Normal"

        return self.clima_actual

    def aplicar_efectos_clima(self, tablero):
        """Aplica los cambios inmediatos que el clima provoca en el tablero."""
        if self.clima_actual == "Lluvia":
            # La lluvia limpia pesticidas
            for _, flor in tablero.flores:
                if flor.esta_viva() and flor.pesticidas > 0:
                    flor.reducir_pesticida(1)

        # Sol y Normal no tienen efectos inmediatos sobre el tablero,
        # sus efectos son pasivos (probabilidades)

    def obtener_probabilidad_reproduccion(self):
        """Calcula la probabilidad de reproducción según el clima actual."""
        prob = self.prob_reproduccion_base
        if self.clima_actual == "Sol":
            prob += self.bonus_reproduccion_sol
        return prob

    def intentar_reproduccion(self, tablero, pos_flor):
        """Intenta reproducir una flor específica en una casilla adyacente vacía."""
        fila, col = pos_flor
        flor = tablero.get_celda(fila, col)

        # Validar estado de la flor
        if not isinstance(flor, Flower) or not flor.esta_viva() or not flor.esta_polinizada():
            return False, None

        # Tirada de dados
        if random.random() > self.obtener_probabilidad_reproduccion():
            return False, None

        # Buscar espacio libre
        vecinos = self._obtener_vecinos_vacios(tablero, fila, col)

        if not vecinos:
            return False, None

        # Crear nueva flor
        nueva_pos = random.choice(vecinos)
        nueva_flor = Flower()

        # Inserción manual en el tablero
        tablero.grid[nueva_pos[0]][nueva_pos[1]] = nueva_flor
        tablero.flores.append((nueva_pos, nueva_flor))

        return True, nueva_pos

    def _obtener_vecinos_vacios(self, tablero, fila, col):
        """Ayudante para encontrar casillas libres alrededor de una posición."""
        casillas_libres = []

        # 8 direcciones posibles (cambios en fila y columna)
        direcciones = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]

        for delta_fila, delta_columna in direcciones:
            nueva_fila = fila + delta_fila
            nueva_columna = col + delta_columna

            # Verificar que las nuevas coordenadas estén dentro del tablero
            if 0 <= nueva_fila < tablero.filas and 0 <= nueva_columna < tablero.columnas:
                # Verificar si la casilla está vacía
                if tablero.get_celda(nueva_fila, nueva_columna) is None:
                    casillas_libres.append((nueva_fila, nueva_columna))

        return casillas_libres

    def ejecutar_ciclo(self, tablero, turno_actual):
        """
        Orquesta el ciclo completo de eventos de azar: Clima -> Efectos -> Reproducción.
        Llamado al final de los turnos clave.
        """
        if not self.debe_activar_evento(turno_actual):
            return None

        # Cambiar Clima
        self.generar_nuevo_clima()

        # Efectos inmediatos (ej: lluvia limpia pesticidas)
        self.aplicar_efectos_clima(tablero)

        # Reproducción
        nuevas = 0
        # Iteramos sobre una copia para no romper el bucle al añadir flores
        flores_actuales = list(tablero.flores)

        for pos, flor in flores_actuales:
            if flor.esta_polinizada():
                exito, _ = self.intentar_reproduccion(tablero, pos)
                if exito:
                    nuevas += 1

        return {
            "clima": self.clima_actual,
            "nuevas_flores": nuevas
        }

    def reset_clima(self):
        self.clima_actual = "Normal"