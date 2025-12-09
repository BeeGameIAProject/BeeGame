from . import board

class Humanidad():
    """
    Agente MIN que representa a la humanidad.
    Puede aplicar pesticidas y colocar obstáculos con restricciones de poda estratégica.
    """
    
    def __init__(self, name="Human", player_name="Humanidad"):
        self.name = name
        self.player_name = player_name
        self.radio_pesticida = 2  # Radio de acción para pesticidas (cerca de la abeja)
        self.radio_obstaculo = 3  # Radio de acción para obstáculos (cerca del rusc, EXCLUYENDO rusc)
        self.max_obstaculos = 4   # Máximo número de obstáculos permitidos en el tablero
    
    def to_string(self):
        return f"Agente: {self.player_name}, Icono: {self.name}"
    
    def distancia_manhattan(self, pos1, pos2):
        """Calcula la distancia Manhattan entre dos posiciones."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def obtener_acciones_validas(self, tablero, pos_abeja):
        """
        Retorna todas las acciones válidas según las restricciones de poda estratégica.
        
        Args:
            tablero: El tablero del juego
            pos_abeja: Posición actual de la abeja
            
        Returns:
            Lista de tuplas (tipo_accion, posicion) donde tipo_accion es 'pesticida' u 'obstaculo'
        """
        acciones = []
        
        # Obtener acciones de pesticida (radio 2 de la abeja, solo en flores)
        for pos, flor in tablero.flores:
            if flor.esta_viva():
                distancia = self.distancia_manhattan(pos, pos_abeja)
                if distancia <= self.radio_pesticida:
                    acciones.append(('pesticida', pos))
        
        # Obtener acciones de obstáculo (radio 3 del rusc, en casillas vacías, EXCLUYENDO la casilla del rusc)
        rusc_pos = tablero.rusc_pos
        for i in range(tablero.filas):
            for j in range(tablero.columnas):
                if tablero.get_celda(i, j) is None:  # Casilla vacía
                    distancia = self.distancia_manhattan((i, j), rusc_pos)
                    # Radio 3 pero EXCLUYENDO la casilla del rusc (distancia > 0)
                    if 0 < distancia <= self.radio_obstaculo:
                        acciones.append(('obstaculo', (i, j)))
        
        return acciones
    
    def aplicar_pesticida(self, tablero, posicion, pos_abeja):
        """
        Aplica pesticida en una posición si cumple las restricciones.
        
        Args:
            tablero: El tablero del juego
            posicion: Posición donde aplicar el pesticida
            pos_abeja: Posición actual de la abeja
            
        Returns:
            True si se aplicó exitosamente, False en caso contrario
        """
        fila, col = posicion
        
        # Verificar que hay una flor
        if not tablero.es_flor(fila, col):
            return False
        
        # Verificar restricción de radio
        distancia = self.distancia_manhattan(posicion, pos_abeja)
        if distancia > self.radio_pesticida:
            return False
        
        # Aplicar pesticida
        exito = tablero.aplicar_pesticida_en(fila, col)
        return exito
    
    def colocar_obstaculo(self, tablero, posicion):
        """Coloca un obstáculo en una posición si cumple las restricciones.
        Si ya hay 4 obstáculos, elimina el más antiguo.
        
        Args:
            tablero: El tablero del juego
            posicion: Posición donde colocar el obstáculo
            
        Returns:
            True si se colocó exitosamente, False en caso contrario
        """
        fila, col = posicion
        
        # Verificar que NO es la casilla del rusc
        if (fila, col) == tablero.rusc_pos:
            return False
        
        # Verificar restricción de radio respecto al rusc (1 a 3, excluyendo 0)
        distancia = self.distancia_manhattan(posicion, tablero.rusc_pos)
        if distancia == 0 or distancia > self.radio_obstaculo:
            return False
        
        # Si ya hay 4 obstáculos, eliminar el más antiguo (FIFO)
        if len(tablero.obstaculos) >= self.max_obstaculos:
            obstaculo_antiguo = tablero.obstaculos[0]
            tablero.grid[obstaculo_antiguo[0]][obstaculo_antiguo[1]] = None
            tablero.obstaculos.pop(0)
        
        # Colocar obstáculo
        exito = tablero.colocar_obstaculo(fila, col)
        return exito
    
    def ejecutar_accion(self, tablero, accion, pos_abeja):
        """
        Ejecuta una acción (pesticida u obstáculo).
        
        Args:
            tablero: El tablero del juego
            accion: Tupla (tipo_accion, posicion)
            pos_abeja: Posición actual de la abeja
            
        Returns:
            True si se ejecutó exitosamente, False en caso contrario
        """
        tipo_accion, posicion = accion
        
        if tipo_accion == 'pesticida':
            return self.aplicar_pesticida(tablero, posicion, pos_abeja)
        elif tipo_accion == 'obstaculo':
            return self.colocar_obstaculo(tablero, posicion)
        else:
            return False
    
    def printname(self):
        print(self.name)


if __name__ == "__main__":
    h = Humanidad()
    h.printname()
    print(h.to_string())
