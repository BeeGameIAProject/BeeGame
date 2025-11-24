# Lista de MVP (Producto Mínimo Viable) - Proyecto IA

## 1. Entorno de Simulació (Tablero y Lógica)
- [ ] [cite_start]**Implementación del Tablero**: Crear una matriz bidimensional de $N \times N$ casillas (dimensiones configurables, p.ej. $20 \times 20$ o $10 \times 10$)[cite: 22, 47, 101].
- [ ] [cite_start]**Elementos del Tablero**: Colocación inicial del rusc (colmena), flores y obstáculos[cite: 47, 102].
- [ ] **Lógica de las Flores**:
    - [ ] [cite_start]Implementar estados: vida, nivel de polinización y contador de pesticidas[cite: 49].
    - [ ] [cite_start]Implementar muerte de la flor si acumula 3 unidades de pesticida[cite: 50, 107, 125].
    - [ ] [cite_start]Gestionar la evolución dinámica (reproducción o muerte)[cite: 51].
- [ ] [cite_start]**Lógica del Rusc**: Definir como punto de retorno para descargar néctar y recuperar energía[cite: 52].
- [ ] [cite_start]**Gestión de Turnos**: Implementar sistema secuencial para agentes y eventos de azar[cite: 55].

## 2. Agentes Principales
### 2.1 Agente MAX (Abeja - Controlado por Jugador)
- [ ] [cite_start]**Atributos**: Implementar vida, energía y capacidad de almacenamiento de néctar[cite: 60, 104].
- [ ] **Acciones Básicas**:
    - [ ] [cite_start]Moverse por el tablero (coste de energía)[cite: 61, 108].
    - [ ] [cite_start]Recoger néctar y polinizar flores[cite: 61].
    - [ ] [cite_start]Descansar (recuperar energía)[cite: 61, 108].
- [ ] **Acción Especial (Algoritmo A*)**:
    - [ ] [cite_start]Implementar botón "volver al rusc"[cite: 28].
    - [ ] [cite_start]Calcular ruta óptima usando algoritmo de búsqueda $A^{*}$ ($f(n) = g(n) + h(n)$)[cite: 28, 167, 168].

### 2.2 Agente MIN (Humanidad - Controlado por IA)
- [ ] **Acciones**:
    - [ ] [cite_start]Aplicar pesticidas (daña flores)[cite: 24, 62].
    - [ ] [cite_start]Colocar obstáculos (bloquea paso)[cite: 24, 62].
- [ ] **Restricciones de Acción (Poda Estratégica)**:
    - [ ] [cite_start]Limitar aplicación de pesticidas a un radio de 2 casillas de la abeja[cite: 105, 135].
    - [ ] [cite_start]Limitar colocación de obstáculos a un radio de 2 casillas del rusc[cite: 105, 135].
    - [ ] [cite_start]Restringir pesticidas solo a casillas con flores[cite: 105].

## 3. Integración de Nodos de Azar (Incertidumbre)
- [ ] **Sistema de Clima (Chance Node 1)**:
    - [ ] [cite_start]Activar evento cada 4 turnos[cite: 69, 111].
    - [ ] **Estados y Probabilidades**:
        - [ ] [cite_start]Lluvia (10%): Resta 1 unidad de pesticida a flores afectadas[cite: 71, 112, 113].
        - [ ] [cite_start]Sol (15%): +20% probabilidad de reproducción en flores polinizadas[cite: 72, 112, 113].
        - [ ] [cite_start]Normal (75%): Sin efectos[cite: 73, 112].
- [ ] **Sistema de Reproducción (Chance Node 2)**:
    - [ ] [cite_start]Ejecutar tras polinización exitosa[cite: 74].
    - [ ] [cite_start]Calcular nacimiento de nueva flor basado en probabilidad base (20%) + bonificación climática si aplica[cite: 114, 141].

## 4. Algoritmo de IA (Core)
- [ ] **Implementación Expectimax**:
    - [ ] [cite_start]Crear función recursiva `expectimax(estado, profundidad, agente)`[cite: 144].
    - [ ] [cite_start]Gestionar nodos MAX (Abeja): Seleccionar mejor valor[cite: 150].
    - [ ] [cite_start]Gestionar nodos MIN (Humanidad): Seleccionar peor valor para MAX[cite: 151].
    - [ ] [cite_start]Gestionar nodos CHANCE (Clima/Reproducción): Calcular media ponderada por probabilidad[cite: 152, 161].
- [ ] [cite_start]**Limitación de Profundidad**: Establecer profundidad máxima de búsqueda para viabilidad computacional[cite: 116, 145].

## 5. Heurística y Evaluación
- [ ] [cite_start]**Función Heurística $H(s)$**: Implementar fórmula de evaluación de estado para nodos hoja/límite[cite: 85, 174].
    - [ ] [cite_start]Fórmula: $H(s) = H_{tauler} + H_{agent} + H_{progrés} + H_{proximitat}$[cite: 176].
- [ ] **Componentes Heurísticos**:
    - [ ] [cite_start]$H_{tauler}$: Valorar flores sanas y polinizadas vs. contaminadas[cite: 179, 182].
    - [ ] [cite_start]$H_{agent}$: Valorar vida y energía de la abeja[cite: 179, 183].
    - [ ] [cite_start]$H_{progrés}$: Valorar néctar en rusc y néctar cargado[cite: 180, 184].
    - [ ] [cite_start]$H_{proximitat}$: Valorar distancia a objetivos según estado del inventario[cite: 185].
- [ ] [cite_start]**Ajuste de Pesos**: Definir variables para los pesos ($w_1$ a $w_7$) para calibración[cite: 117, 181].

## 6. Condiciones de Finalización
- [ ] [cite_start]**Victoria**: La abeja acumula la cantidad objetivo de néctar[cite: 109, 198].
- [ ] **Derrota**:
    - [ ] [cite_start]Vida de la abeja llega a 0[cite: 109, 198].
    - [ ] [cite_start]No quedan flores disponibles en el tablero[cite: 109, 198].