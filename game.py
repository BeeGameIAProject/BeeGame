import bee
import board

if __name__ == "__main__":
    # Crear tablero 10x10
    tablero = board.Board(10, 10)
    
    # Inicializar tablero con rusc, flores y obstáculos
    tablero.inicializar_tablero(num_flores=15, num_obstaculos=5)
    
    # Mostrar tablero inicial
    print("TABLERO INICIAL:")
    tablero.mostrar_tablero()
    
    # Crear abeja
    abeja = bee.Bee(100, True)
    print("\nEstado de la abeja:")
    print(abeja.to_string())
    
    # Ejemplo de mecánicas
    print("\n--- EJEMPLO DE MECÁNICAS ---")
    
    # Incrementar turno
    tablero.incrementar_turno()
    
    # Aplicar pesticida en una flor (si hay flores)
    flores_vivas = tablero.get_flores_vivas()
    if flores_vivas:
        pos_flor, flor = flores_vivas[0]
        print(f"\nFlor en posición {pos_flor}:")
        print(flor.to_string())
        
        print("\nAplicando pesticida...")
        tablero.aplicar_pesticida_en(pos_flor[0], pos_flor[1])
        print(flor.to_string())
    
    # Mostrar tablero actualizado
    print("\nTABLERO DESPUÉS DE 1 TURNO:")
    tablero.mostrar_tablero()
    
    print(f"\nFlores vivas en tablero: {tablero.contar_flores_vivas()}")
    print(f"Posición del rusc: {tablero.rusc_pos}")
