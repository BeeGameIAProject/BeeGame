import random

class Humanidad:
    """
    Agente MIN.
    Gestiona la aplicación de pesticidas y la colocación estratégica de obstáculos.
    """

    def __init__(self):
        # Configuración de radios y límites
        self.radio_pesticida = 2
        self.radio_obstaculo = 3
        self.max_obstaculos = 4

    def distancia_chebyshev(self, pos1, pos2):
        """Calcula la distancia máxima en un eje (movimiento de Rey)."""
        return max(abs(pos1[0] - pos2[0]), abs(pos1[1] - pos2[1]))

    def obtener_acciones_validas(self, tablero, pos_abeja):
        """Genera todas las jugadas legales para la Humanidad en el turno actual."""
        acciones = []

        # Pesticidas: Solo en flores vivas cerca de la abeja
        for pos, flor in tablero.flores:
            if flor.esta_viva():
                dist = self.distancia_chebyshev(pos, pos_abeja)
                if dist <= self.radio_pesticida:
                    acciones.append(('pesticida', pos))

        # Obstáculos: Cerca de la Colmena O cerca de la Abeja
        candidatos = set()

        # Buscamos candidatos alrededor de la colmena
        celdas_colmena = self._obtener_celdas_candidatas(
            tablero, tablero.pos_colmena, self.radio_obstaculo
        )
        candidatos.update(celdas_colmena)

        # Buscamos candidatos alrededor de la abeja (para bloquearla)
        celdas_abeja = self._obtener_celdas_candidatas(
            tablero, pos_abeja, self.radio_obstaculo
        )
        candidatos.update(celdas_abeja)

        # Filtramos los candidatos que son válidos (vacíos y no son entidades clave)
        pos_colmena = tablero.pos_colmena

        for pos in candidatos:
            # No podemos poner obstáculo sobre la abeja, la colmena o algo que no sea vacío (None)
            if pos == pos_abeja or pos == pos_colmena:
                continue

            if tablero.get_celda(pos[0], pos[1]) is not None:
                continue

            # Regla: Debe estar dentro del radio de influencia de alguno de los objetivos
            # (El helper ya filtra por radio cuadrado, pero verificamos distancia exacta si es necesario)
            acciones.append(('obstaculo', pos))

        # Mezclamos para evitar sesgo posicional en la IA
        random.shuffle(acciones)
        return acciones

    def ejecutar_accion(self, tablero, accion, pos_abeja):
        """Despacha la acción al método correspondiente."""
        tipo, pos = accion

        if tipo == 'pesticida':
            return self._aplicar_pesticida(tablero, pos, pos_abeja)
        elif tipo == 'obstaculo':
            return self.colocar_obstaculo(tablero, pos)

        return False

    def colocar_obstaculo(self, tablero, posicion):
        """
        Intenta colocar un obstáculo gestionando el límite máximo (FIFO).
        Es público porque la GUI lo usa para aplicar decisiones de la IA.
        """
        # Validación básica de seguridad
        if posicion == tablero.pos_colmena:
            return False

        # Gestión de inventario de obstáculos (FIFO)
        if len(tablero.obstaculos) >= self.max_obstaculos:
            # Eliminamos el más antiguo
            viejo_pos = tablero.obstaculos[0]
            # Accedemos al grid para limpiar
            # Si board tuviera un método 'quitar_obstaculo', sería mejor usarlo.
            tablero.grid[viejo_pos[0]][viejo_pos[1]] = None
            tablero.obstaculos.pop(0)

        # Delegamos la colocación al tablero
        return tablero.colocar_obstaculo(posicion[0], posicion[1])

    def _aplicar_pesticida(self, tablero, posicion, pos_abeja):
        """Aplica pesticida validando la distancia."""
        # Doble check de distancia por seguridad
        if self.distancia_chebyshev(posicion, pos_abeja) > self.radio_pesticida:
            return False

        return tablero.aplicar_pesticida_en(posicion[0], posicion[1])

    def _obtener_celdas_candidatas(self, tablero, centro, radio):
        """Retorna una lista de coordenadas dentro del cuadrado definido por el radio."""
        candidatas = []
        cx, cy = centro

        # Calculamos rangos seguros dentro de los límites del tablero
        min_f = max(0, cx - radio)
        max_f = min(tablero.filas, cx + radio + 1)
        min_c = max(0, cy - radio)
        max_c = min(tablero.columnas, cy + radio + 1)

        for f in range(min_f, max_f):
            for c in range(min_c, max_c):
                # Excluimos el centro exacto (la propia entidad)
                if (f, c) != centro:
                    candidatas.append((f, c))

        return candidatas