import bee
import board
import humanidad

if __name__ == "__main__":
    # Crear tablero 10x10
    tablero = board.Board(10, 10)
    
    # Inicializar tablero con rusc, flores y obstáculos
    tablero.inicializar_tablero(num_flores=15, num_obstaculos=3)
    
    # Mostrar tablero inicial
    print("="*60)
    print("DEMO MVP2 - AGENTES PRINCIPALES")
    print("="*60)
    tablero.mostrar_tablero()
    
    # Crear agentes
    abeja = bee.Bee(100)
    humanidad_agente = humanidad.Humanidad()
    
    print("\n--- ESTADO INICIAL DE LOS AGENTES ---")
    print(f"🐝 Abeja: {abeja.to_string()}")
    print(f"👨 Humanidad: {humanidad_agente.to_string()}")
    
    # Posición inicial de la abeja (arriba del rusc)
    pos_abeja = (tablero.rusc_pos[0] - 1, tablero.rusc_pos[1])
    print(f"\nPosición inicial de la abeja: {pos_abeja}")
    print(f"Posición del rusc: {tablero.rusc_pos}")
    
    # ===== TURNO 1: ABEJA =====
    print("\n" + "="*60)
    print("TURNO 1 - ABEJA")
    print("="*60)
    
    # Buscar una flor cercana
    flores_vivas = tablero.get_flores_vivas()
    if flores_vivas:
        pos_flor, flor = flores_vivas[0]
        print(f"\nFlor encontrada en {pos_flor}: {flor.to_string()}")
        
        # Recoger néctar y polinizar
        print("\n--- Acción: Recoger néctar y polinizar ---")
        abeja.recoger_nectar_y_polinizar(tablero, pos_flor)
        print(f"Estado abeja: {abeja.to_string()}")
        print(f"Estado flor: {flor.to_string()}")
    
    tablero.incrementar_turno()
    
    # ===== TURNO 2: HUMANIDAD =====
    print("\n" + "="*60)
    print("TURNO 2 - HUMANIDAD")
    print("="*60)
    
    # Obtener acciones válidas
    acciones_validas = humanidad_agente.obtener_acciones_validas(tablero, pos_abeja)
    print(f"\nAcciones válidas disponibles: {len(acciones_validas)}")
    
    # Aplicar pesticida (si hay flores cerca de la abeja)
    pesticidas_disponibles = [a for a in acciones_validas if a[0] == 'pesticida']
    if pesticidas_disponibles:
        print(f"\nPesticidas disponibles: {len(pesticidas_disponibles)}")
        print("\n--- Acción: Aplicar pesticida ---")
        accion = pesticidas_disponibles[0]
        humanidad_agente.ejecutar_accion(tablero, accion, pos_abeja)
    
    # Colocar obstáculo cerca del rusc
    obstaculos_disponibles = [a for a in acciones_validas if a[0] == 'obstaculo']
    if obstaculos_disponibles:
        print(f"\nObstáculos disponibles: {len(obstaculos_disponibles)}")
        print("\n--- Acción: Colocar obstáculo ---")
        accion = obstaculos_disponibles[0]
        humanidad_agente.ejecutar_accion(tablero, accion, pos_abeja)
    
    tablero.incrementar_turno()
    tablero.mostrar_tablero()
    
    # ===== TURNO 3: ABEJA - ALGORITMO A* =====
    print("\n" + "="*60)
    print("TURNO 3 - ABEJA (USANDO A*)")
    print("="*60)
    
    print(f"\nPosición actual de la abeja: {pos_abeja}")
    print(f"Destino: Rusc en {tablero.rusc_pos}")
    
    print("\n--- Acción: Calcular ruta al rusc con A* ---")
    ruta = abeja.calcular_ruta_a_rusc(tablero, pos_abeja)
    
    if ruta:
        print(f"✓ Ruta encontrada con {len(ruta)} pasos:")
        print(f"  {' -> '.join(str(p) for p in ruta)}")
        
        # Simular movimiento al rusc
        if len(ruta) > 1:
            siguiente = ruta[1]
            print(f"\n--- Acción: Moverse de {pos_abeja} a {siguiente} ---")
            if abeja.mover(tablero, pos_abeja, siguiente):
                pos_abeja = siguiente
                print(f"✓ Movimiento exitoso")
                print(f"Estado abeja: {abeja.to_string()}")
    else:
        print("✗ No se encontró ruta al rusc")
    
    # ===== TURNO 4: ABEJA - DESCANSAR =====
    print("\n" + "="*60)
    print("TURNO 4 - ABEJA")
    print("="*60)
    
    print("\n--- Acción: Descansar ---")
    abeja.descansar()
    print(f"Estado abeja: {abeja.to_string()}")
    
    tablero.incrementar_turno()
    
    # ===== RESUMEN FINAL =====
    print("\n" + "="*60)
    print("RESUMEN FINAL")
    print("="*60)
    print(f"Turnos jugados: {tablero.get_turno()}")
    print(f"Estado final abeja: {abeja.to_string()}")
    print(f"Flores vivas: {tablero.contar_flores_vivas()}/{len(tablero.flores)}")
    print(f"Néctar en rusc: {tablero.nectar_en_rusc}")
    
    tablero.mostrar_tablero()
