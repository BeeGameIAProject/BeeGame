class Flower:
    """
    Representa una flor.
    Gestiona su ciclo de vida, estado de polinización y niveles de contaminación.
    """

    # Constantes de clase
    MAX_PESTICIDAS = 3
    DAÑO_POR_NIVEL = {0: 0, 1: 5, 2: 10, 3: 15}

    def __init__(self, vida=100):
        self.vida = vida
        self.max_vida = vida
        self.es_polinizada = False
        self.pesticidas = 0
        self.viva = True
        self.turnos_muerta = 0

    def esta_viva(self):
        """Indica si la flor sigue viva."""
        return self.viva

    def esta_polinizada(self):
        """Indica si la flor ha sido polinizada."""
        return self.es_polinizada

    def polinizar(self):
        """Marca la flor como polinizada si está viva."""
        if self.viva:
            self.es_polinizada = True

    def aplicar_pesticida(self):
        """Incrementa nivel de pesticida. Si alcanza el máximo, la flor muere."""
        if not self.viva:
            return

        self.pesticidas += 1
        if self.pesticidas >= self.MAX_PESTICIDAS:
            self.matar()

    def reducir_pesticida(self, cantidad=1):
        """Reduce el nivel de pesticida (ej. por lluvia)."""
        self.pesticidas = max(0, self.pesticidas - cantidad)

    def get_daño_pesticida(self):
        """
        Retorna el daño que esta flor causa a la abeja por contacto.
        Basado en el nivel actual de pesticida.
        """
        # Devuelve el valor del diccionario o 15 si supera el índice (máximo daño)
        return self.DAÑO_POR_NIVEL.get(self.pesticidas, 15)

    def matar(self):
        """Finaliza el ciclo de vida de la flor."""
        self.viva = False
        self.vida = 0
        self.turnos_muerta = 0

    def incrementar_turno_muerta(self):
        """Avanza el contador de descomposición si la flor está muerta."""
        if not self.viva:
            self.turnos_muerta += 1

    def debe_eliminarse(self):
        """Determina si la flor muerta debe ser retirada del tablero."""
        return not self.viva and self.turnos_muerta >= 1

    # Métodos de manipulación de vida (mantenidos por compatibilidad con lógica externa)
    def bajar_vida(self, daño):
        if self.viva:
            self.vida -= daño
            if self.vida <= 0:
                self.matar()

    def subir_vida(self, cura):
        if self.viva:
            self.vida = min(self.max_vida, self.vida + cura)