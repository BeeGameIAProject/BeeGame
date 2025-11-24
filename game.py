import bee
import board
import humanidad
import chance_events

if __name__ == "__main__":
    # Crear tablero 10x10
    tablero = board.Board(10, 10)
    
    # Inicializar tablero con rusc, flores y obstáculos
    tablero.inicializar_tablero(num_flores=15, num_obstaculos=3)
    
    # Crear agentes y sistema de eventos
    abeja = bee.Bee(100)
    humanidad_agente = humanidad.Humanidad()
    eventos_azar = chance_events.ChanceEvents()
    
    # Mostrar tablero inicial
    print("="*60)
    print("DEMO MVP3 - NODOS DE AZAR (CLIMA Y REPRODUCCIÓN)")
    print("="*60)
    tablero.mostrar_tablero()
    
    print("\n--- ESTADO INICIAL DE LOS AGENTES ---")
    print(f"🐝 Abeja: {abeja.to_string()}")
    print(f"👨 Humanidad: {humanidad_agente.to_string()}")
    print(f"🌦️  Eventos de azar: Activos (cada {eventos_azar.turnos_para_clima} turnos)")
    
    # Posición inicial de la abeja
    pos_abeja = (tablero.rusc_pos[0] - 1, tablero.rusc_pos[1])
    print(f"\nPosición inicial de la abeja: {pos_abeja}")
    
    # ===== SIMULACIÓN DE VARIOS TURNOS =====
    for turno in range(1, 9):
        print("\n" + "="*60)
        print(f"TURNO {turno}")
        print("="*60)
        
        tablero.incrementar_turno()
        
        # Turno de la abeja (turnos impares)
        if turno % 2 == 1:
            print("\n--- ABEJA ---")
            flores_vivas = tablero.get_flores_vivas()
            
            if flores_vivas and abeja.tiene_energia(abeja.coste_recoleccion):
                # Buscar flor no polinizada cercana
                flor_objetivo = None
                for pos_flor, flor in flores_vivas:
                    if not flor.esta_polinizada():
                        flor_objetivo = (pos_flor, flor)
                        break
                
                if flor_objetivo:
                    pos_flor, flor = flor_objetivo
                    print(f"Recolectando néctar en {pos_flor}")
                    abeja.recoger_nectar_y_polinizar(tablero, pos_flor)
                    print(f"Estado: {abeja.to_string()}")
                else:
                    print("Todas las flores están polinizadas. Descansando...")
                    abeja.descansar()
            else:
                print("Descansando para recuperar energía...")
                abeja.descansar()
        
        # Turno de la humanidad (turnos pares)
        else:
            print("\n--- HUMANIDAD ---")
            acciones = humanidad_agente.obtener_acciones_validas(tablero, pos_abeja)
            
            if acciones:
                # Priorizar pesticidas
                pesticidas = [a for a in acciones if a[0] == 'pesticida']
                if pesticidas:
                    accion = pesticidas[0]
                    print(f"Aplicando pesticida en {accion[1]}")
                    humanidad_agente.ejecutar_accion(tablero, accion, pos_abeja)
                else:
                    # Si no hay pesticidas, colocar obstáculo
                    obstaculos = [a for a in acciones if a[0] == 'obstaculo']
                    if obstaculos:
                        accion = obstaculos[0]
                        print(f"Colocando obstáculo en {accion[1]}")
                        humanidad_agente.ejecutar_accion(tablero, accion, pos_abeja)
            else:
                print("Sin acciones válidas disponibles")
        
        # ===== EVENTOS DE AZAR (CHANCE NODES) =====
        print("\n--- EVENTOS DE AZAR ---")
        eventos = eventos_azar.ejecutar_eventos_turno(tablero, tablero.get_turno())
        
        if eventos["evento_clima"]:
            print(f"\n🌦️  ¡EVENTO CLIMÁTICO! {eventos['clima']}")
            
            # Mostrar efectos del clima
            stats_clima = eventos["stats_clima"]
            if eventos["clima"] == "Lluvia":
                print(f"   💧 Lluvia: {stats_clima['pesticidas_reducidos']} pesticidas reducidos en {stats_clima['flores_afectadas']} flores")
            elif eventos["clima"] == "Sol":
                print(f"   ☀️  Sol: {stats_clima.get('mensaje', 'Bonificación a reproducción')}")
            else:
                print(f"   ⛅ Normal: Sin efectos")
            
            # Mostrar reproducción
            stats_repro = eventos["stats_reproduccion"]
            print(f"\n🌸 REPRODUCCIÓN:")
            print(f"   - Flores polinizadas: {stats_repro['flores_polinizadas']}")
            print(f"   - Probabilidad actual: {stats_repro['probabilidad']*100:.0f}%")
            print(f"   - Nuevas flores nacidas: {stats_repro['flores_nuevas']}")
            
            if stats_repro['flores_nuevas'] > 0:
                print(f"   - Posiciones: {stats_repro['posiciones_nuevas']}")
        else:
            clima_actual = eventos_azar.get_clima_actual()
            print(f"Clima actual: {clima_actual} (próximo evento en turno {((tablero.get_turno() // 4) + 1) * 4})")
        
        # Mostrar estadísticas del turno
        print(f"\n📊 Flores vivas: {tablero.contar_flores_vivas()} | Néctar en rusc: {tablero.nectar_en_rusc}")
    
    # ===== RESUMEN FINAL =====
    print("\n" + "="*60)
    print("TABLERO FINAL")
    print("="*60)
    tablero.mostrar_tablero()
    
    print("\n" + "="*60)
    print("RESUMEN FINAL")
    print("="*60)
    print(f"Turnos simulados: {tablero.get_turno()}")
    print(f"Estado abeja: {abeja.to_string()}")
    print(f"Flores totales: {len(tablero.flores)}")
    print(f"Flores vivas: {tablero.contar_flores_vivas()}")
    print(f"Flores polinizadas: {sum(1 for _, f in tablero.flores if f.esta_viva() and f.esta_polinizada())}")
    print(f"Néctar acumulado en rusc: {tablero.nectar_en_rusc}")
    print(f"Clima actual: {eventos_azar.get_clima_actual()}")
