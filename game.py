import bee
import board
import humanidad
import chance_events
import expectimax
from heuristica import Heuristica

if __name__ == "__main__":
    # Crear tablero 8x8 (más pequeño para demo)
    tablero = board.Board(8, 8)
    
    # Inicializar tablero con rusc, flores y obstáculos
    tablero.inicializar_tablero(num_flores=10, num_obstaculos=2)
    
    # Crear agentes y sistema de eventos
    abeja = bee.Bee(100)
    humanidad_agente = humanidad.Humanidad()
    eventos_azar = chance_events.ChanceEvents()
    
    # Crear heurística personalizada
    heuristica = Heuristica(
        w1=10,  # Flores vivas
        w2=8,   # Flores polinizadas
        w3=15,  # Néctar en rusc
        w4=5,   # Néctar cargado
        w5=3,   # Vida abeja
        w6=2,   # Energía abeja
        w7=1    # Proximidad
    )
    
    # Crear IA Expectimax con heurística
    ai = expectimax.ExpectimaxAI(max_depth=2, heuristica=heuristica)
    
    # Mostrar tablero inicial
    print("="*60)
    print("DEMO MVP5 - HEURÍSTICA COMPLETA")
    print("="*60)
    tablero.mostrar_tablero()
    
    print("\n--- CONFIGURACIÓN ---")
    print(f"🐝 Abeja: {abeja.to_string()}")
    print(f"👨 Humanidad: {humanidad_agente.to_string()}")
    print(f"🤖 IA Expectimax: Profundidad máxima = {ai.max_depth}")
    print(f"\n📊 Heurística:")
    print(heuristica.to_string())
    
    # Posición inicial de la abeja
    pos_abeja = (tablero.rusc_pos[0] - 1, tablero.rusc_pos[1])
    print(f"\nPosición inicial de la abeja: {pos_abeja}")
    
    # ===== SIMULACIÓN CON EXPECTIMAX =====
    for turno in range(1, 6):
        print("\n" + "="*60)
        print(f"TURNO {turno}")
        print("="*60)
        
        tablero.incrementar_turno()
        
        # Turno de la abeja usando Expectimax
        if turno % 2 == 1:
            print("\n--- ABEJA (USANDO EXPECTIMAX) ---")
            
            # Crear estado actual
            estado_actual = expectimax.GameState(
                tablero, abeja, pos_abeja, 
                humanidad_agente, eventos_azar, 
                tablero.get_turno()
            )
            
            # Obtener mejor acción usando Expectimax
            print("🤖 Calculando mejor acción con Expectimax...")
            mejor_accion = ai.get_best_action(estado_actual)
            print(f"   Nodos explorados: {ai.nodes_explored}")
            
            # Evaluar estado actual
            valor_actual = ai.heuristica.evaluar(estado_actual)
            print(f"   Valor heurístico del estado: {valor_actual:.2f}")
            
            if mejor_accion:
                tipo_accion, objetivo = mejor_accion
                print(f"   Mejor acción: {tipo_accion}")
                
                if tipo_accion == 'recoger':
                    print(f"   Objetivo: Recoger néctar en {objetivo}")
                    abeja.recoger_nectar_y_polinizar(tablero, objetivo)
                    pos_abeja = objetivo
                
                elif tipo_accion == 'mover':
                    print(f"   Objetivo: Moverse a {objetivo}")
                    if abeja.mover(tablero, pos_abeja, objetivo):
                        pos_abeja = objetivo
                
                elif tipo_accion == 'descansar':
                    print(f"   Objetivo: Descansar")
                    abeja.descansar()
                
                elif tipo_accion == 'descargar':
                    print(f"   Objetivo: Descargar néctar en rusc")
                    abeja.descargar_nectar_en_rusc(tablero, pos_abeja)
                    abeja.recuperar_energia_en_rusc(tablero, pos_abeja)
                
                print(f"   Estado: {abeja.to_string()}")
            else:
                print("   No hay acciones disponibles")
        
        # Turno de la humanidad (sin IA, acción aleatoria)
        else:
            print("\n--- HUMANIDAD ---")
            acciones = humanidad_agente.obtener_acciones_validas(tablero, pos_abeja)
            
            if acciones:
                # Elegir acción aleatoria
                import random
                accion = random.choice(acciones)
                tipo_accion, pos = accion
                print(f"Acción: {tipo_accion} en {pos}")
                humanidad_agente.ejecutar_accion(tablero, accion, pos_abeja)
            else:
                print("Sin acciones válidas")
        
        # Eventos de azar
        print("\n--- EVENTOS DE AZAR ---")
        eventos = eventos_azar.ejecutar_eventos_turno(tablero, tablero.get_turno())
        
        if eventos["evento_clima"]:
            print(f"🌦️  Clima: {eventos['clima']}")
            if eventos['stats_reproduccion']['flores_nuevas'] > 0:
                print(f"   🌸 {eventos['stats_reproduccion']['flores_nuevas']} nuevas flores!")
        else:
            print(f"Clima: {eventos_azar.get_clima_actual()}")
        
        print(f"\n📊 Flores: {tablero.contar_flores_vivas()} | Néctar rusc: {tablero.nectar_en_rusc}")
    
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
    print(f"Flores vivas: {tablero.contar_flores_vivas()}")
    print(f"Néctar en rusc: {tablero.nectar_en_rusc}")
    print(f"Total nodos explorados por Expectimax: {ai.nodes_explored}")
