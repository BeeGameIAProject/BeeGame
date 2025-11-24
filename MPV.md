# Lista de MVP (Producto Mínimo Viable) - Proyecto IA

## 1. Entorno de Simulació (Tablero y Lógica)
- [x] **Implementación del Tablero**: Crear una matriz bidimensional de $N \times N$ casillas (dimensiones configurables, p.ej. $20 \times 20$ o $10 \times 10$).
- [x] **Elementos del Tablero**: Colocación inicial del rusc (colmena), flores y obstáculos.
- [x] **Lógica de las Flores**:
    - [x] Implementar estados: vida, nivel de polinización y contador de pesticidas.
    - [x] Implementar muerte de la flor si acumula 3 unidades de pesticida.
    - [ ] Gestionar la evolución dinámica (reproducción o muerte).
- [x] **Lógica del Rusc**: Definir como punto de retorno para descargar néctar y recuperar energía.
- [x] **Gestión de Turnos**: Implementar sistema secuencial para agentes y eventos de azar.

## 2. Agentes Principales
### 2.1 Agente MAX (Abeja - Controlado por Jugador)
- [x] **Atributos**: Implementar vida, energía y capacidad de almacenamiento de néctar.
- [x] **Acciones Básicas**:
    - [x] Moverse por el tablero (coste de energía).
    - [x] Recoger néctar y polinizar flores.
    - [x] Descansar (recuperar energía).
- [x] **Acción Especial (Algoritmo A*)**:
    - [x] Implementar botón "volver al rusc".
    - [x] Calcular ruta óptima usando algoritmo de búsqueda $A^{*}$ ($f(n) = g(n) + h(n)$).

### 2.2 Agente MIN (Humanidad - Controlado por IA)
- [x] **Acciones**:
    - [x] Aplicar pesticidas (daña flores).
    - [x] Colocar obstáculos (bloquea paso).
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
- [ ] **Implementación Expectimax**:
    - [ ] Crear función recursiva `expectimax(estado, profundidad, agente)`.
    - [ ] Gestionar nodos MAX (Abeja): Seleccionar mejor valor.
    - [ ] Gestionar nodos MIN (Humanidad): Seleccionar peor valor para MAX.
    - [ ] Gestionar nodos CHANCE (Clima/Reproducción): Calcular media ponderada por probabilidad.
- [ ] **Limitación de Profundidad**: Establecer profundidad máxima de búsqueda para viabilidad computacional.

## 5. Heurística y Evaluación
- [ ] **Función Heurística $H(s)$**: Implementar fórmula de evaluación de estado para nodos hoja/límite.
    - [ ] Fórmula: $H(s) = H_{tauler} + H_{agent} + H_{progrés} + H_{proximitat}$.
- [ ] **Componentes Heurísticos**:
    - [ ] $H_{tauler}$: Valorar flores sanas y polinizadas vs. contaminadas.
    - [ ] $H_{agent}$: Valorar vida y energía de la abeja.
    - [ ] $H_{progrés}$: Valorar néctar en rusc y néctar cargado.
    - [ ] $H_{proximitat}$: Valorar distancia a objetivos según estado del inventario.
- [ ] **Ajuste de Pesos**: Definir variables para los pesos ($w_1$ a $w_7$) para calibración.

## 6. Condiciones de Finalización
- [ ] **Victoria**: La abeja acumula la cantidad objetivo de néctar.
- [ ] **Derrota**:
    - [ ] Vida de la abeja llega a 0.
    - [ ] No quedan flores disponibles en el tablero.