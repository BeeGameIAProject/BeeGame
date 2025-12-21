"""
Módulo de heurística para el algoritmo Expectimax.
"""

class Heuristica:
    """
    Función de evaluación H(s) para el algoritmo Expectimax.
    Combina factores ambientales e internos de la abeja.
    """

    def __init__(self, w1=10, w2=8, w3=15, w4=5, w5=3, w6=2, w7=1, w8=5, w9=5):
        self.w_flores_vivas = w1
        self.w_polinizadas = w2
        self.w_nectar_colmena = w3
        self.w_nectar_mochila = w4
        self.w_vida = w5
        self.w_energia = w6
        self.w_proximidad = w7
        self.w_amenaza = w8
        self.w_obstaculos = w9

    def evaluar(self, estado):
        """Retorna el valor numérico (utilidad) de un estado."""
        # Estados Terminales
        if not estado.abeja.esta_viva(): return -100000.0
        if estado.tablero.contar_flores_vivas() == 0: return -100000.0
        if estado.tablero.nectar_en_colmena >= 100: return 100000.0

        # Evaluación Heurística
        valor = (
            self._h_tablero(estado) +
            self._h_agente(estado) +
            self._h_progreso(estado) +
            self._h_proximidad(estado) +
            self._h_amenaza(estado) -
            self._h_obstaculos(estado)
        )
        return valor

    def _h_tablero(self, estado):
        flores_vivas = 0
        flores_polinizadas = 0
        flores_contaminadas = 0
        total_pesticidas = 0

        for _, flor in estado.tablero.flores:
            if flor.esta_viva():
                flores_vivas += 1
                if flor.esta_polinizada(): flores_polinizadas += 1
                if flor.pesticidas > 0:
                    flores_contaminadas += 1
                    total_pesticidas += flor.pesticidas

        return (self.w_flores_vivas * flores_vivas +
                self.w_polinizadas * flores_polinizadas -
                5 * flores_contaminadas -
                3 * total_pesticidas)

    def _h_agente(self, estado):
        ratio_vida = estado.abeja.vida / estado.abeja.max_vida
        ratio_energia = estado.abeja.energia / estado.abeja.max_energia

        valor = (self.w_vida * ratio_vida * 100) + (self.w_energia * ratio_energia * 100)

        if ratio_vida < 0.3: valor -= 500
        if ratio_energia < 0.2: valor -= 200
        return valor

    def _h_progreso(self, estado):
        valor = (self.w_nectar_colmena * estado.tablero.nectar_en_colmena +
                 self.w_nectar_mochila * estado.abeja.nectar_cargado)

        progreso = (estado.tablero.nectar_en_colmena + estado.abeja.nectar_cargado) / 100
        if progreso > 0.75: valor += 1000
        elif progreso > 0.5: valor += 500
        elif progreso > 0.25: valor += 200
        return valor

    def _h_proximidad(self, estado):
        pos_abeja = estado.pos_abeja
        capacidad = estado.abeja.capacidad_nectar

        # Modo: volver a casa (mochila llena > 60%)
        if estado.abeja.nectar_cargado >= (capacidad * 0.6):
            dist = self.distancia_chebyshev(pos_abeja, estado.tablero.pos_colmena)
            return (20.0 / dist * self.w_proximidad) if dist > 0 else (50 * self.w_proximidad)

        # Modo: recolección
        flores_vivas = estado.tablero.get_flores_vivas()
        if not flores_vivas: return 0

        # Buscar flor más cercana sin pesticidas graves
        dist_min = float('inf')
        for pos_flor, flor in flores_vivas:
            if flor.pesticidas == 0:
                d = self.distancia_chebyshev(pos_abeja, pos_flor)
                if d < dist_min: dist_min = d

        if dist_min == float('inf'): return 0
        return (10.0 / dist_min * self.w_proximidad) if dist_min > 0 else (20 * self.w_proximidad)

    def _h_amenaza(self, estado):
        amenaza = 0
        for pos_flor, flor in estado.tablero.flores:
            if flor.esta_viva() and flor.pesticidas == 0:
                dist = max(1, self.distancia_chebyshev(estado.pos_abeja, pos_flor))
                amenaza += (10.0 / dist)
        return amenaza * self.w_amenaza

    def _h_obstaculos(self, estado):
        return len(estado.tablero.obstaculos) * self.w_obstaculos

    @staticmethod
    def distancia_chebyshev(pos1, pos2):
        return max(abs(pos1[0] - pos2[0]), abs(pos1[1] - pos2[1]))