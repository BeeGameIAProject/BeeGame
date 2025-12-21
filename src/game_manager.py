"""
Módulo de gestión de condiciones de finalización del juego.
Define las reglas de victoria y derrota.
"""

class GameManager():
    """
    Gestiona las condiciones de finalización del juego y el estado general.
    """
    
    def __init__(self, nectar_objetivo=100):
        """
        Inicializa el gestor del juego.
        
        Args:
            nectar_objetivo: Cantidad de néctar necesaria para ganar
        """
        self.nectar_objetivo = nectar_objetivo
        self.juego_terminado = False
        self.resultado = None  # 'VICTORIA', 'DERROTA_ABEJA_MUERTA', etc
        self.mensaje_final = ""
    
    def verificar_condiciones_finalizacion(self, tablero, abeja):
        """
        Verifica todas las condiciones de finalización del juego.
        
        Args:
            tablero: El tablero del juego
            abeja: La abeja jugadora
            
        Returns:
            Tupla (terminado, resultado, mensaje)
        """
        if self.verificar_victoria(tablero):
            self.juego_terminado = True
            self.resultado = 'VICTORIA'
            self.mensaje_final = f" ¡VICTORIA! Has llegado al objetivo de néctar"
            return True, self.resultado, self.mensaje_final
        
        # Verificamos derrota por muerte de abeja
        if self.verificar_derrota_abeja_muerta(abeja):
            self.juego_terminado = True
            self.resultado = 'DERROTA_ABEJA_MUERTA'
            self.mensaje_final = "¡DERROTA! La abeja ha muerto"
            return True, self.resultado, self.mensaje_final
        
        # Verificamos derrota por extinción de flores
        if self.verificar_derrota_sin_flores(tablero):
            self.juego_terminado = True
            self.resultado = 'DERROTA_SIN_FLORES'
            self.mensaje_final = "¡DERROTA! No quedan flores vivas en el tablero"
            return True, self.resultado, self.mensaje_final

        # Verificamos derrota por falta de energía
        if abeja.energia <= 0:
            self.juego_terminado = True
            self.resultado = 'DERROTA_SIN_ENERGIA'
            self.mensaje_final = "¡DERROTA! La abeja se ha quedado sin energía"
            return True, self.resultado, self.mensaje_final
        
        # El juego continua
        return False, None, ""
    
    def verificar_victoria(self, tablero):
        """
        Verifica si se ha alcanzado la condición de victoria.
        
        Condición: Néctar en la colmena >= objetivo
        
        Args:
            tablero: El tablero del juego
            
        Returns:
            True si se cumple la condición de victoria
        """
        return tablero.nectar_en_colmena >= self.nectar_objetivo
    
    def verificar_derrota_abeja_muerta(self, abeja):
        """
        Verifica si la abeja ha muerto.
        
        Condición: Vida de la abeja <= 0
        
        Args:
            abeja: La abeja jugadora
            
        Returns:
            True si la abeja está muerta
        """
        return not abeja.esta_viva() or abeja.vida <= 0
    
    def verificar_derrota_sin_flores(self, tablero):
        """
        Verifica si no quedan flores vivas.
        
        Condición: Número de flores vivas = 0
        
        Args:
            tablero: El tablero del juego
            
        Returns:
            True si no hay flores vivas
        """
        return tablero.contar_flores_vivas() == 0
    
    def get_progreso_victoria(self, tablero):
        """
        Calcula el progreso hacia la victoria.
        
        Args:
            tablero: El tablero del juego
            
        Returns:
            Porcentaje de progreso (0-100)
        """
        return min(100, (tablero.nectar_en_colmena / self.nectar_objetivo) * 100)
    
    def get_estado_juego(self, tablero, abeja):
        """
        Retorna un resumen del estado actual del juego.
        
        Args:
            tablero: El tablero del juego
            abeja: La abeja jugadora
            
        Returns:
            Diccionario con información del estado
        """
        progreso = self.get_progreso_victoria(tablero)
        
        return {
            'terminado': self.juego_terminado,
            'resultado': self.resultado,
            'mensaje': self.mensaje_final,
            'nectar_actual': tablero.nectar_en_colmena,
            'nectar_objetivo': self.nectar_objetivo,
            'progreso_victoria': progreso,
            'vida_abeja': abeja.vida,
            'energia_abeja': abeja.energia,
            'flores_vivas': tablero.contar_flores_vivas(),
            'flores_totales': len(tablero.flores),
            'turnos': tablero.get_turno()
        }

    def reset(self):
        """Reinicia el estado del gestor del juego."""
        self.juego_terminado = False
        self.resultado = None
        self.mensaje_final = ""

if __name__ == "__main__":
    print("Game Manager implementado")
    print("\nCondiciones de finalización:")
    print("  ✓ Victoria: Néctar en la colmena >= objetivo")
    print("  ✗ Derrota: Vida de abeja <= 0")
    print("  ✗ Derrota: Flores vivas = 0")
    
    gm = GameManager(nectar_objetivo=100)
    print(f"\nObjetivo de néctar: {gm.nectar_objetivo}")
