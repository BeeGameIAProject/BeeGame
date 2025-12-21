"""
BeeGame - Simulación Ecológica con IA
Punto de entrada principal del juego
"""

from gui import BeeGameGUI

if __name__ == "__main__":
    juego = BeeGameGUI(filas=9, columnas=9, nectar_objetivo=100)
    juego.run()
