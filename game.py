import bee
import board
import humanidad
import chance_events
import expectimax
from heuristica import Heuristica
from game_manager import GameManager

if __name__ == "__main__":
    # Crear tablero 8x8
    tablero = board.Board(8, 8)
    
    # Inicializar tablero con rusc, flores y obstáculos
    tablero.inicializar_tablero(num_flores=12, num_obstaculos=2)
    
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
    
    # Crear gestor del juego con objetivo de néctar
    game_manager = GameManager(nectar_objetivo=50)  # Objetivo reducido para demo
    
    # Mostrar tablero inicial
    print("="*60)
    print("DEMO MVP6 - CONDICIONES DE FINALIZACIÓN")
    print("="*60)
    tablero.mostrar_tablero()
    
    print("\n--- CONFIGURACIÓN ---")
    print(f"🐝 Abeja: {abeja.to_string()}")
    print(f"🎯 Objetivo: {game_manager.nectar_objetivo} unidades de néctar")
    print(f"🤖 IA Expectimax: Profundidad = {ai.max_depth}")
    
    # Posición inicial de la abeja
    pos_abeja = (tablero.rusc_pos[0] - 1, tablero.rusc_pos[1])
    print(f"\nPosición inicial de la abeja: {pos_abeja}")
    
    # Mostrar estado inicial
    game_manager.mostrar_estado(tablero, abeja)
    
    # ===== SIMULACIÓN CON EXPECTIMAX Y CONDICIONES DE FINALIZACIÓN =====
    turno = 0
    max_turnos = 30  # Límite de seguridad
    
    while not game_manager.juego_terminado and turno < max_turnos:
        turno += 1
        print("\n" + "="*60)
        print(f"TURNO {turno}")
        print("="*60)
        
        tablero.incrementar_turno()
        
        # Turno de la abeja usando Expectimax
        if turno % 2 == 1:
            print("\n--- ABEJA (IA EXPECTIMAX) ---")
            
            # Crear estado actual
            estado_actual = expectimax.GameState(
                tablero, abeja, pos_abeja, 
                humanidad_agente, eventos_azar, 
                tablero.get_turno()
            )
            
            # Obtener mejor acción
            mejor_accion = ai.get_best_action(estado_actual)
            
            if mejor_accion:
                tipo_accion, objetivo = mejor_accion
                print(f"Acción: {tipo_accion}", end="")
                
                if tipo_accion == 'recoger':
                    print(f" en {objetivo}")
                    abeja.recoger_nectar_y_polinizar(tablero, objetivo)
                    pos_abeja = objetivo
                
                elif tipo_accion == 'mover':
                    print(f" a {objetivo}")
                    if abeja.mover(tablero, pos_abeja, objetivo):
                        pos_abeja = objetivo
                
                elif tipo_accion == 'descansar':
                    print()
                    abeja.descansar()
                
                elif tipo_accion == 'descargar':
                    print(f" en rusc")
                    abeja.descargar_nectar_en_rusc(tablero, pos_abeja)
                    abeja.recuperar_energia_en_rusc(tablero, pos_abeja)
                
                # Si está en el rusc y tiene néctar, descargar
                if tablero.es_rusc(pos_abeja[0], pos_abeja[1]) and abeja.nectar_cargado > 0:
                    abeja.descargar_nectar_en_rusc(tablero, pos_abeja)
                    abeja.recuperar_energia_en_rusc(tablero, pos_abeja)
            
            print(f"Estado: Vida={abeja.life}, Energía={abeja.energia}, Néctar={abeja.nectar_cargado}")
        
        # Turno de la humanidad
        else:
            print("\n--- HUMANIDAD ---")
            acciones = humanidad_agente.obtener_acciones_validas(tablero, pos_abeja)
            
            if acciones:
                import random
                accion = random.choice(acciones)
                tipo_accion, pos = accion
                print(f"Acción: {tipo_accion} en {pos}")
                humanidad_agente.ejecutar_accion(tablero, accion, pos_abeja)
        
        # Eventos de azar
        if turno % 4 == 0:
            eventos = eventos_azar.ejecutar_eventos_turno(tablero, tablero.get_turno())
            if eventos["evento_clima"]:
                print(f"\n🌦️  Evento climático: {eventos['clima']}")
                if eventos['stats_reproduccion']['flores_nuevas'] > 0:
                    print(f"   🌸 {eventos['stats_reproduccion']['flores_nuevas']} nuevas flores!")
        
        # Verificar condiciones de finalización
        terminado, resultado, mensaje = game_manager.verificar_condiciones_finalizacion(tablero, abeja)
        
        # Mostrar progreso cada 3 turnos
        if turno % 3 == 0 or terminado:
            game_manager.mostrar_estado(tablero, abeja)
        
        if terminado:
            break
    
    # ===== RESUMEN FINAL =====
    print("\n" + "="*60)
    print("TABLERO FINAL")
    print("="*60)
    tablero.mostrar_tablero()
    
    print("\n" + "="*60)
    print("RESUMEN FINAL DEL JUEGO")
    print("="*60)
    
    estado_final = game_manager.get_estado_juego(tablero, abeja)
    print(f"Resultado: {estado_final['resultado'] if estado_final['terminado'] else 'JUEGO INTERRUMPIDO'}")
    print(f"Turnos jugados: {estado_final['turnos']}")
    print(f"Néctar recolectado: {estado_final['nectar_actual']}/{estado_final['nectar_objetivo']}")
    print(f"Progreso: {estado_final['progreso_victoria']:.1f}%")
    print(f"Estado abeja: Vida={estado_final['vida_abeja']}, Energía={estado_final['energia_abeja']}")
    print(f"Flores: {estado_final['flores_vivas']} vivas de {estado_final['flores_totales']} totales")
    
    if estado_final['terminado']:
        print(f"\n{estado_final['mensaje']}")
