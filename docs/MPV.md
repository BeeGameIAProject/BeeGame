# Lista de MVP (Producto Mínimo Viable) - Proyecto IA

## 1. Entorn de Simulació (Tablero y Lógica)
- [x] **Implementación del Tablero**: Crear una matriz bidimensional de $N \times N$ casillas (dimensiones configurables, p.ej. $20 \times 20$ o $10 \times 10$).
    - [ ] Probar tamaños del tablero 9*9 para que haya casilla central.
- [x] **Elementos del Tablero**: Colocación inicial del rusc (colmena), flores y obstáculos.
    - [ ] Arreglar emojis de los botones.
    - [ ] Replantear boton de descargar.
- [x] **Lógica de las Flores**:
    - [x] Implementar estados: vida, nivel de polinización y contador de pesticidas.
    - [x] Implementar muerte de la flor si acumula 3 unidades de pesticida.
    - [ ] Gestionar la evolución dinámica (reproducción o muerte).
    - [x] Poner daño de pesticida al recoger el nectar de flores con pesticida, no solo al pasar por ellas.
- [x] **Lógica del Rusc**: Definir como punto de retorno para descargar néctar y recuperar energía.
    - [ ] Eliminar limite de nectar del Rusc.
- [x] **Gestión de Turnos**: Implementar sistema secuencial para agentes y eventos de azar.


## 2. Agentes Principales
### 2.1 Agente MAX (Abeja - Controlado por Jugador)
- [x] **Atributos**: Implementar vida, energía y capacidad de almacenamiento de néctar.
- [x] **Acciones Básicas**:
    - [x] Moverse por el tablero (coste de energía).
        - [x] Ajustar que no se pueda mover en la misma casilla (que no pierda energia al hacerlo).
    - [x] Recoger néctar y polinizar flores.
    - [x] Descansar (recuperar energía).
- [x] **Acción Especial (Algoritmo A*)**:
    - [x] Implementar botón "volver al rusc".
    - [x] Calcular ruta óptima usando algoritmo de búsqueda $A^{*}$ ($f(n) = g(n) + h(n)$).
    - [ ] **A* con Aleatoriedad**: Introducir factor estocástico (noise) en costes iguales para evitar rutas deterministas/repetitivas.

### 2.2 Agente MIN (Humanidad - Controlado por IA)
- [x] **Acciones**:
    - [x] Aplicar pesticidas (daña flores).
    - [x] Colocar obstáculos (bloquea paso).
        - [ ] Revisar los limites para colocar los obstaculos (cerca del Rusc o la abeja no puede).
- [x] **Restricciones de Acción (Poda Estratégica)**:
    - [x] Limitar aplicación de pesticidas a un radio de 2 casillas de la abeja.
    - [x] Limitar colocación de obstáculos a un radio de 2 casillas del rusc.
    - [x] Restringir pesticidas solo a casillas con flores.

## 3. Integración de Nodos de Azar (Incertidumbre)
- [x] **Sistema de Clima (Chance Node 1)**:
    - [x] Activar evento cada 4 turnos.
    - [x] **Estados y Probabilidades**:
        - [x] Lluvia (10%): Resta 1 unidad de pesticida a flores afectadas.
        - [x] Sol (15%): +20% probabilidad de reproducción en flores polinizadas.
        - [x] Normal (75%): Sin efectos.
- [x] **Sistema de Reproducción (Chance Node 2)**:
    - [x] Ejecutar tras polinización exitosa.
    - [x] Calcular nacimiento de nueva flor basado en probabilidad base (20%) + bonificación climática si aplica.

## 4. Algoritmo de IA (Core)
- [x] **Implementación Expectimax**:
    - [x] Crear función recursiva `expectimax(estado, profundidad, agente)`.
    - [x] Gestionar nodos MAX (Abeja): Seleccionar mejor valor.
    - [x] Gestionar nodos MIN (Humanidad): Seleccionar peor valor para MAX.
    - [x] Gestionar nodos CHANCE (Clima/Reproducción): Calcular media ponderada por probabilidad.
- [x] **Limitación de Profundidad**: Establecer profundidad máxima de búsqueda para viabilidad computacional.
- [ ] **Aprendizaje por Refuerzo (Experimental)**:
    - [ ] **Considerar Q-Learning**: Investigar implementación para aprendizaje de interacción con objetos (valores Q para estados de flores/obstáculos).

## 5. Heurística y Evaluación
- [x] **Función Heurística $H(s)$**: Implementar fórmula de evaluación de estado para nodos hoja/límite.
    - [x] Fórmula: $H(s) = H_{tauler} + H_{agent} + H_{progrés} + H_{proximitat}$.
- [x] **Componentes Heurísticos**:
    - [x] $H_{tauler}$: Valorar flores sanas y polinizadas vs. contaminadas.
    - [x] $H_{agent}$: Valorar vida y energía de la abeja.
    - [x] $H_{progrés}$: Valorar néctar en rusc y néctar cargado.
    - [x] $H_{proximitat}$: Valorar distancia a objetivos según estado del inventario.
- [x] **Ajuste de Pesos**: Definir variables para los pesos ($w_1$ a $w_7$) para calibración.

## 6. Condiciones de Finalización
- [x] **Victoria**: La abeja acumula la cantidad objetivo de néctar.
- [x] **Derrota**:
    - [x] Vida de la abeja llega a 0.
    - [x] No quedan flores disponibles en el tablero.

## 7. Interfaz Gráfica y Control (GUI)
- [x] **Ventana de Juego**:
    - [x] Implementar librería gráfica (Pygame/Tkinter) para eliminar la terminal.
    - [x] Renderizar cuadrícula $N \times N$ con sprites/imágenes.
- [x] **Control de Usuario (Input)**:
    - [x] Mapear clics de ratón a coordenadas del tablero.
    - [x] Botones en pantalla para acciones: Polinizar, Descansar, Volver al Rusc ($A^*$).
- [x] **Feedback Visual**:
    - [x] Mostrar barras de vida y energía en tiempo real.
    - [x] Visualizar efectos climáticos (icono de sol/lluvia) y pesticidas (cambio de color en flor).