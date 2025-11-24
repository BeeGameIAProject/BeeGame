import random
from flower import Flower

class ChanceEvents():
    """
    Gestiona los nodos de azar (Chance Nodes) del juego.
    Incluye sistema de clima y reproducción de flores.
    """
    
    def __init__(self):
        # Configuración del clima
        self.turnos_para_clima = 4  # Cada cuántos turnos ocurre evento climático
        self.probabilidad_lluvia = 0.10  # 10%
        self.probabilidad_sol = 0.15  # 15%
        self.probabilidad_normal = 0.75  # 75%
        
        # Configuración de reproducción
        self.prob_base_reproduccion = 0.20  # 20% base
        self.bonus_sol_reproduccion = 0.20  # +20% con sol
        
        # Estado actual del clima
        self.clima_actual = "Normal"
        self.ultimo_evento_clima = 0
    
    def debe_activar_clima(self, turno_actual):
        """Verifica si debe activarse un evento climático este turno."""
        return turno_actual > 0 and turno_actual % self.turnos_para_clima == 0
    
    def generar_evento_clima(self):
        """
        Genera un evento climático aleatorio según las probabilidades.
        Retorna: "Lluvia", "Sol" o "Normal"
        """
        rand = random.random()
        
        if rand < self.probabilidad_lluvia:
            self.clima_actual = "Lluvia"
        elif rand < self.probabilidad_lluvia + self.probabilidad_sol:
            self.clima_actual = "Sol"
        else:
            self.clima_actual = "Normal"
        
        return self.clima_actual
    
    def aplicar_efecto_clima(self, tablero):
        """
        Aplica el efecto del clima actual a todas las flores del tablero.
        
        Args:
            tablero: El tablero del juego
            
        Returns:
            Diccionario con estadísticas del efecto
        """
        stats = {
            "clima": self.clima_actual,
            "flores_afectadas": 0,
            "pesticidas_reducidos": 0
        }
        
        if self.clima_actual == "Lluvia":
            # Reducir 1 unidad de pesticida a todas las flores
            for pos, flor in tablero.flores:
                if flor.esta_viva() and flor.pesticidas > 0:
                    flor.reducir_pesticida(1)
                    stats["flores_afectadas"] += 1
                    stats["pesticidas_reducidos"] += 1
        
        elif self.clima_actual == "Sol":
            # El efecto del sol se aplica en la reproducción
            stats["mensaje"] = "Bonificación de +20% a reproducción de flores polinizadas"
        
        # Normal no tiene efectos
        
        return stats
    
    def calcular_probabilidad_reproduccion(self):
        """
        Calcula la probabilidad de reproducción actual.
        Incluye bonificación si hay sol.
        """
        prob = self.prob_base_reproduccion
        
        if self.clima_actual == "Sol":
            prob += self.bonus_sol_reproduccion
        
        return prob
    
    def intentar_reproduccion(self, tablero, pos_flor):
        """
        Intenta reproducir una flor polinizada.
        
        Args:
            tablero: El tablero del juego
            pos_flor: Posición de la flor polinizada
            
        Returns:
            Tupla (exito, nueva_posicion) donde exito es True si nació una nueva flor
        """
        fila, col = pos_flor
        flor = tablero.get_celda(fila, col)
        
        # Verificar que la flor está viva y polinizada
        if not isinstance(flor, Flower) or not flor.esta_viva() or not flor.esta_polinizada():
            return False, None
        
        # Calcular probabilidad
        prob_reproduccion = self.calcular_probabilidad_reproduccion()
        
        # Tirar dado
        if random.random() > prob_reproduccion:
            return False, None
        
        # Buscar casilla adyacente vacía para la nueva flor
        casillas_adyacentes = [
            (fila - 1, col - 1), (fila - 1, col), (fila - 1, col + 1),
            (fila, col - 1),                       (fila, col + 1),
            (fila + 1, col - 1), (fila + 1, col), (fila + 1, col + 1)
        ]
        
        # Filtrar casillas válidas y vacías
        casillas_validas = []
        for f, c in casillas_adyacentes:
            if 0 <= f < tablero.filas and 0 <= c < tablero.columnas:
                if tablero.get_celda(f, c) is None:
                    casillas_validas.append((f, c))
        
        if not casillas_validas:
            return False, None  # No hay espacio para nueva flor
        
        # Elegir una casilla aleatoria
        nueva_pos = random.choice(casillas_validas)
        
        # Crear nueva flor
        nueva_flor = Flower()
        tablero.grid[nueva_pos[0]][nueva_pos[1]] = nueva_flor
        tablero.flores.append((nueva_pos, nueva_flor))
        
        return True, nueva_pos
    
    def procesar_reproduccion_flores(self, tablero):
        """
        Procesa la reproducción de todas las flores polinizadas en el tablero.
        
        Args:
            tablero: El tablero del juego
            
        Returns:
            Diccionario con estadísticas de reproducción
        """
        stats = {
            "flores_polinizadas": 0,
            "flores_nuevas": 0,
            "posiciones_nuevas": [],
            "probabilidad": self.calcular_probabilidad_reproduccion()
        }
        
        # Obtener flores polinizadas (hacemos copia para evitar modificar durante iteración)
        flores_polinizadas = [(pos, flor) for pos, flor in tablero.flores 
                              if flor.esta_viva() and flor.esta_polinizada()]
        
        stats["flores_polinizadas"] = len(flores_polinizadas)
        
        # Intentar reproducción de cada flor polinizada
        for pos, flor in flores_polinizadas:
            exito, nueva_pos = self.intentar_reproduccion(tablero, pos)
            if exito:
                stats["flores_nuevas"] += 1
                stats["posiciones_nuevas"].append(nueva_pos)
        
        return stats
    
    def ejecutar_eventos_turno(self, tablero, turno_actual):
        """
        Ejecuta todos los eventos de azar del turno si corresponde.
        
        Args:
            tablero: El tablero del juego
            turno_actual: El número del turno actual
            
        Returns:
            Diccionario con información de los eventos ejecutados
        """
        resultado = {
            "evento_clima": False,
            "clima": None,
            "stats_clima": None,
            "stats_reproduccion": None
        }
        
        # Verificar si toca evento climático
        if self.debe_activar_clima(turno_actual):
            resultado["evento_clima"] = True
            
            # Generar y aplicar clima
            clima = self.generar_evento_clima()
            resultado["clima"] = clima
            resultado["stats_clima"] = self.aplicar_efecto_clima(tablero)
            
            # Procesar reproducción (siempre se intenta, pero probabilidad cambia con clima)
            resultado["stats_reproduccion"] = self.procesar_reproduccion_flores(tablero)
        
        return resultado
    
    def get_clima_actual(self):
        """Retorna el clima actual."""
        return self.clima_actual
    
    def reset_clima(self):
        """Resetea el clima a Normal."""
        self.clima_actual = "Normal"


if __name__ == "__main__":
    # Prueba básica
    chance = ChanceEvents()
    print(f"Probabilidad reproducción base: {chance.prob_base_reproduccion * 100}%")
    
    # Simular evento climático
    clima = chance.generar_evento_clima()
    print(f"Clima generado: {clima}")
    print(f"Probabilidad reproducción con {clima}: {chance.calcular_probabilidad_reproduccion() * 100}%")
