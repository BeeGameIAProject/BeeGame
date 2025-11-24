"""
Módulo de heurística para el algoritmo Expectimax.
Implementa la función H(s) = H_tauler + H_agent + H_progrés + H_proximitat
"""

class Heuristica():
    """
    Función heurística completa para evaluar estados del juego.
    
    Componentes:
    - H_tauler: Valoración del estado del tablero (flores)
    - H_agent: Valoración del estado de la abeja
    - H_progrés: Valoración del progreso hacia la victoria
    - H_proximitat: Valoración de la distancia a objetivos
    
    Fórmula: H(s) = w1*H_tauler + w2*H_agent + w3*H_progrés + w4*H_proximitat
    """
    
    def __init__(self, w1=10, w2=8, w3=15, w4=5, w5=3, w6=2, w7=1):
        """
        Inicializa los pesos de la heurística.
        
        Pesos:
        w1: Peso para flores vivas
        w2: Peso para flores polinizadas
        w3: Peso para néctar en rusc
        w4: Peso para néctar cargado
        w5: Peso para vida de la abeja
        w6: Peso para energía de la abeja
        w7: Peso para proximidad a objetivos
        """
        self.w1 = w1  # Flores vivas
        self.w2 = w2  # Flores polinizadas
        self.w3 = w3  # Néctar en rusc (objetivo principal)
        self.w4 = w4  # Néctar cargado
        self.w5 = w5  # Vida de la abeja
        self.w6 = w6  # Energía de la abeja
        self.w7 = w7  # Proximidad
    
    def evaluar(self, estado):
        """
        Evalúa un estado del juego y retorna su valor heurístico.
        
        Args:
            estado: GameState a evaluar
            
        Returns:
            Valor heurístico del estado
        """
        # Verificar estados terminales
        if not estado.abeja.esta_viva():
            return -100000
        
        if estado.tablero.contar_flores_vivas() == 0:
            return -100000
        
        # Victoria: objetivo de néctar alcanzado
        nectar_objetivo = 100
        if estado.tablero.nectar_en_rusc >= nectar_objetivo:
            return 100000
        
        # Calcular componentes de la heurística
        h_tauler = self.h_tauler(estado)
        h_agent = self.h_agent(estado)
        h_progres = self.h_progres(estado)
        h_proximitat = self.h_proximitat(estado)
        
        # Combinar componentes con pesos
        valor_total = h_tauler + h_agent + h_progres + h_proximitat
        
        return valor_total
    
    def h_tauler(self, estado):
        """
        H_tauler: Valoración del estado del tablero.
        
        Considera:
        - Número de flores vivas
        - Número de flores polinizadas
        - Flores contaminadas (con pesticidas)
        - Balance general del ecosistema
        """
        valor = 0
        
        # Contar flores en diferentes estados
        flores_vivas = 0
        flores_polinizadas = 0
        flores_contaminadas = 0
        total_pesticidas = 0
        
        for pos, flor in estado.tablero.flores:
            if flor.esta_viva():
                flores_vivas += 1
                
                if flor.esta_polinizada():
                    flores_polinizadas += 1
                
                if flor.pesticidas > 0:
                    flores_contaminadas += 1
                    total_pesticidas += flor.pesticidas
        
        # Valorar flores vivas (más flores = mejor)
        valor += self.w1 * flores_vivas
        
        # Valorar flores polinizadas (importante para reproducción)
        valor += self.w2 * flores_polinizadas
        
        # Penalizar flores contaminadas
        valor -= 5 * flores_contaminadas
        
        # Penalizar pesticidas totales
        valor -= 3 * total_pesticidas
        
        return valor
    
    def h_agent(self, estado):
        """
        H_agent: Valoración del estado de la abeja.
        
        Considera:
        - Vida actual vs. vida máxima
        - Energía actual vs. energía máxima
        - Capacidad de continuar operando
        """
        valor = 0
        
        # Normalizar vida (0-1)
        ratio_vida = estado.abeja.life / estado.abeja.max_vida
        valor += self.w5 * ratio_vida * 100
        
        # Normalizar energía (0-1)
        ratio_energia = estado.abeja.energia / estado.abeja.max_energia
        valor += self.w6 * ratio_energia * 100
        
        # Penalizar fuertemente si la vida es crítica (<30%)
        if ratio_vida < 0.3:
            valor -= 500
        
        # Penalizar si la energía es muy baja (<20%)
        if ratio_energia < 0.2:
            valor -= 200
        
        return valor
    
    def h_progres(self, estado):
        """
        H_progrés: Valoración del progreso hacia la victoria.
        
        Considera:
        - Néctar acumulado en el rusc (objetivo principal)
        - Néctar cargado por la abeja
        - Progreso hacia el objetivo de néctar
        """
        valor = 0
        
        # Valorar néctar en rusc (objetivo principal del juego)
        valor += self.w3 * estado.tablero.nectar_en_rusc
        
        # Valorar néctar cargado (potencial para depositar)
        valor += self.w4 * estado.abeja.nectar_cargado
        
        # Bonus si está cerca de completar el objetivo
        nectar_objetivo = 100
        progreso = (estado.tablero.nectar_en_rusc + estado.abeja.nectar_cargado) / nectar_objetivo
        
        if progreso > 0.75:
            valor += 1000  # Muy cerca de ganar
        elif progreso > 0.5:
            valor += 500   # A mitad de camino
        elif progreso > 0.25:
            valor += 200   # Buen progreso
        
        return valor
    
    def h_proximitat(self, estado):
        """
        H_proximitat: Valoración de la distancia a objetivos.
        
        Considera:
        - Distancia a flores (si necesita recoger néctar)
        - Distancia al rusc (si necesita descargar néctar)
        - Prioriza según el estado del inventario
        """
        valor = 0
        
        pos_abeja = estado.pos_abeja
        
        # Si tiene néctar cargado, priorizar estar cerca del rusc
        if estado.abeja.nectar_cargado > 0:
            distancia_rusc = self.distancia_manhattan(pos_abeja, estado.tablero.rusc_pos)
            
            # Mientras más lejos del rusc, peor (invertir distancia)
            valor -= self.w7 * distancia_rusc * 2
            
            # Bonus si está en el rusc
            if distancia_rusc == 0:
                valor += 100
        
        # Si no tiene néctar o tiene espacio, valorar proximidad a flores
        elif estado.abeja.puede_cargar_nectar():
            # Buscar la flor viva más cercana
            flores_vivas = estado.tablero.get_flores_vivas()
            
            if flores_vivas:
                distancia_min = float('inf')
                for pos_flor, flor in flores_vivas:
                    dist = self.distancia_manhattan(pos_abeja, pos_flor)
                    if dist < distancia_min:
                        distancia_min = dist
                
                # Mientras más cerca de una flor, mejor
                valor -= self.w7 * distancia_min
                
                # Bonus si está adyacente a una flor
                if distancia_min == 1:
                    valor += 50
        
        return valor
    
    def distancia_manhattan(self, pos1, pos2):
        """Calcula la distancia Manhattan entre dos posiciones."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def to_string(self):
        """Retorna una representación de los pesos configurados."""
        return f"""Pesos de la Heurística:
  w1 (Flores vivas): {self.w1}
  w2 (Flores polinizadas): {self.w2}
  w3 (Néctar en rusc): {self.w3}
  w4 (Néctar cargado): {self.w4}
  w5 (Vida abeja): {self.w5}
  w6 (Energía abeja): {self.w6}
  w7 (Proximidad): {self.w7}"""


if __name__ == "__main__":
    h = Heuristica()
    print("Heurística implementada")
    print(h.to_string())
    print("\nFórmula: H(s) = H_tauler + H_agent + H_progrés + H_proximitat")
    print("Cada componente pondera diferentes aspectos del estado del juego")
