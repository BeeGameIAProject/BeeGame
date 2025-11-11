import board
class Bee():
    
    def  __init__(self,life, first_move=True,name="🐝",player_name="Bee"):
        self.life = life
        self.first_move = first_move
        self.name = name
        self.player_name = player_name
        self.daño_ataque = 10
        self.max_vida = life
    
    def to_string(self):
        return f"Life: {self.life}, Juga primer: {self.first_move}, Icona: {self.name}, Nom jugador: {self.player_name}"
    
    def is_valid_move(self,board,start,to):
        """Comprueba si el movimiento es válido (estilo rey de ajedrez)."""
        filas = board.fila()
        columnas = board.columna()

        # Comprobar límites
        if not (0 <= to[0] < filas and 0 <= to[1] < columnas):
            print("Moviment invàlid: fora del tauler.")
            return False

        if abs(start[0] - to[0]) <= 1 and abs(start[1] - to[1]) <= 1:
            return True

        print("Moviment invàlid.")
        return False

    def abella_tocada(self):
        """Baja la vida con daño predeteminado"""
        self.life -=self.daño_ataque
        if self.life <0:
            self.life = 0
        
    def baixar_vida(self,ataque):
        """Baja la vida con daño especifico"""
        self.life -=ataque
        if self.life <0:
            self.life = 0
        
    def pujar_vida(self,cura):
        """Puja la vida"""
        
        self.life += cura
        if self.life > self.max_vida:
            self.life = self.max_vida 
    
    def next_moves(self, board, position):
        """Retorna els seguents moviments posibles"""
        m = []
        filas = board.fila()
        columnas = board.columna()
        fila, col = position

        # Movimientos posibles 
        direcciones = [(-1, -1), (-1, 0), (-1, 1),( 0, -1),( 0, 1),( 1, -1), ( 1, 0), ( 1, 1)]
        m = [
        (fila + df, col + dc)
        for df, dc in direcciones
        if 0 <= fila + df < filas and 0 <= col + dc < columnas
        ]
        return m    
    def esta_viva(self):
        """Devuelve True si la abeja sigue viva."""
        return self.life >= 0

    def printname(self):
        print(self.name)


if __name__ == "__main__":
    b = Bee(100,True)
    b.printname()
    print(b.to_string())