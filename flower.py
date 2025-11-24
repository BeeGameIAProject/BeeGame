class Flower():
    """
    Representa una flor en el tablero del juego.
    Las flores tienen vida, nivel de polinización y contador de pesticidas.
    Mueren cuando el contador de pesticidas llega a 3.
    """
    def __init__(self, vida=100, polinizacion=0, pesticidas=0):
        self.vida = vida
        self.max_vida = vida
        self.polinizacion = polinizacion  # 0: no polinizada, 1: polinizada
        self.pesticidas = pesticidas
        self.viva = True
        
    def aplicar_pesticida(self):
        """Aplica una unidad de pesticida. Mata la flor si llega a 3."""
        if self.viva:
            self.pesticidas += 1
            if self.pesticidas >= 3:
                self.matar()
    
    def reducir_pesticida(self, cantidad=1):
        """Reduce el contador de pesticidas (efecto de lluvia)."""
        self.pesticidas = max(0, self.pesticidas - cantidad)
    
    def polinizar(self):
        """Marca la flor como polinizada."""
        if self.viva:
            self.polinizacion = 1
    
    def esta_polinizada(self):
        """Retorna True si la flor está polinizada."""
        return self.polinizacion == 1
    
    def matar(self):
        """Mata la flor."""
        self.viva = False
        self.vida = 0
    
    def esta_viva(self):
        """Retorna True si la flor está viva."""
        return self.viva
    
    def bajar_vida(self, daño):
        """Reduce la vida de la flor."""
        if self.viva:
            self.vida -= daño
            if self.vida <= 0:
                self.matar()
    
    def subir_vida(self, cura):
        """Incrementa la vida de la flor."""
        if self.viva:
            self.vida += cura
            if self.vida > self.max_vida:
                self.vida = self.max_vida
    
    def to_string(self):
        """Retorna una representación en string de la flor."""
        estado = "Viva" if self.viva else "Muerta"
        polin = "Polinizada" if self.polinizacion else "No polinizada"
        return f"Flor: {estado}, Vida: {self.vida}/{self.max_vida}, {polin}, Pesticidas: {self.pesticidas}/3"
    
    def get_symbol(self):
        """Retorna el símbolo visual de la flor."""
        if not self.viva:
            return "💀"
        if self.polinizacion:
            return "🌸"
        return "🌼"
