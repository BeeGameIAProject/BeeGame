class GameManager:
    """
    Gestiona las condiciones de victoria y derrota, así como el estado global de la partida.
    """
    
    # Constantes de estado
    RES_VICTORIA = 'VICTORIA'
    RES_DERROTA_MUERTE = 'DERROTA_MUERTE'
    RES_DERROTA_ECOSISTEMA = 'DERROTA_ECOSISTEMA'
    RES_DERROTA_ENERGIA = 'DERROTA_ENERGIA'
    
    def __init__(self, nectar_objetivo=100):
        self.nectar_objetivo = nectar_objetivo
        self.juego_terminado = False
        self.resultado = None
        self.mensaje_final = ""
    
    def verificar_condiciones_finalizacion(self, tablero, abeja):
        """
        Evalúa el estado actual y determina si el juego ha terminado.
        Retorna: (terminado, resultado, mensaje)
        """
        # Victoria
        if self._es_victoria(tablero):
            return self._finalizar(self.RES_VICTORIA, "¡VICTORIA! Objetivo de néctar alcanzado.")
        
        # Derrotas
        if self._es_abeja_muerta(abeja):
            return self._finalizar(self.RES_DERROTA_MUERTE, "¡DERROTA! La abeja ha muerto.")
        
        if self._es_colapso_ecosistema(tablero):
            return self._finalizar(self.RES_DERROTA_ECOSISTEMA, "¡DERROTA! No quedan flores vivas.")

        if self._es_agotamiento_energia(abeja):
            return self._finalizar(self.RES_DERROTA_ENERGIA, "¡DERROTA! Abeja sin energía.")
        
        # El juego continúa
        return False, None, ""
    
    def _finalizar(self, resultado, mensaje):
        """Método auxiliar para establecer el estado final."""
        self.juego_terminado = True
        self.resultado = resultado
        self.mensaje_final = mensaje
        return True, resultado, mensaje

    def _es_victoria(self, tablero):
        return tablero.nectar_en_colmena >= self.nectar_objetivo
    
    def _es_abeja_muerta(self, abeja):
        """Delegamos la verificación en la propia entidad."""
        return not abeja.esta_viva()
    
    def _es_colapso_ecosistema(self, tablero):
        return tablero.contar_flores_vivas() == 0
    
    def _es_agotamiento_energia(self, abeja):
        return abeja.energia <= 0
    
    def get_progreso_victoria(self, tablero):
        """Calcula el porcentaje de progreso (0-100)."""
        if self.nectar_objetivo <= 0: return 100
        return min(100, (tablero.nectar_en_colmena / self.nectar_objetivo) * 100)
    
    def reset(self):
        """Reinicia los flags de finalización."""
        self.juego_terminado = False
        self.resultado = None
        self.mensaje_final = ""