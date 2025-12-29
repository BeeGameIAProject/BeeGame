# BeeGame Simulator

Este repositorio contiene el código fuente de **BeeGame**, un proyecto de simulación desarrollado en Python mediante la librería `pygame`. El sistema modela un ecosistema simplificado donde un agente inteligente (una abeja) debe optimizar la recolección de recursos mientras gestiona su supervivencia frente a un agente antagonista (la humanidad) y factores estocásticos ambientales.

El objetivo principal de este trabajo es la implementación, análisis y comparación de algoritmos de Búsqueda Adversaria y Aprendizaje por Refuerzo en un entorno de cuadrícula (tablero $NxN$).

## Descripción del Proyecto

El simulador plantea un problema de toma de decisiones en un entorno dinámico e incierto. Los componentes principales son:

* **Agente (MAX):** La Abeja. Su función de utilidad se maximiza al recolectar néctar, polinizar flores y depositar el recurso en la colmena, manteniendo niveles óptimos de energía y salud.
* **Adversario (MIN):** La Humanidad. Actúa como un agente hostil que intenta minimizar la utilidad de la abeja mediante la colocación estratégica de obstáculos y la aplicación de pesticidas.
* **Entorno Estocástico (CHANCE):** Eventos climáticos (Lluvia, Sol, Normal) que ocurren con una frecuencia determinada y afectan las propiedades del entorno, como la toxicidad de las flores o su tasa de reproducción.

## Instalación y Ejecución

### Requisitos
* Python.
* Librería `pygame`.

### Pasos para ejecutar
1.  Clonar este repositorio:
    ```bash
    git clone https://github.com/BeeGameIAProject/BeeGame.git
    cd BeeGame
    ```

2.  Instalar las dependencias necesarias:
    ```bash
    pip install pygame
    ```

3.  Iniciar la simulación:
    ```bash
    python main.py
    ```

## Algoritmos Implementados

El núcleo del proyecto se basa en la comparación de dos enfoques distintos para la toma de decisiones del agente antagonista, mientras el agente protagonista utiliza búsqueda heurística y pathfinding.

### 1. Expectimax (Búsqueda Adversaria con Incertidumbre)
Algoritmo utilizado para planificar movimientos considerando la naturaleza no determinista del clima.
* **Profundidad:** Configurable (por defecto 2 niveles).
* **Modelado:** Árbol de búsqueda con nodos MAX (Abeja), MIN (Humanidad) y CHANCE (Clima).
* **Heurística:** Evalúa la utilidad de los estados hoja basándose en factores ponderados como salud, energía, néctar recolectado, distancia a objetivos y proximidad de amenazas.

### 2. Q-Learning (Aprendizaje por Refuerzo)
Implementación de un agente que aprende una política de comportamiento óptima a través de la interacción directa con el entorno (ensayo y error).
* **Espacio de Estados:** Discretizado en una tupla `(Cuadrante, Nivel de Flores, Estado de Energía)` para reducir la dimensionalidad y acelerar la convergencia.
* **Sistema de Recompensas:** Otorga refuerzos positivos (+10/+5) por acciones ofensivas efectivas a corta distancia y penalizaciones (-1) por acciones irrelevantes.
* **Política:** Epsilon-Greedy, balanceando la exploración de nuevas acciones con la explotación del conocimiento adquirido.

### 3. A* (Pathfinding)
Utilizado por el agente abeja para la navegación espacial eficiente hacia la colmena. Incorpora un factor de ruido aleatorio en la función de coste para simular un comportamiento orgánico y no perfectamente determinista.

## Métricas y Evaluación

La interfaz gráfica incluye un panel de métricas en tiempo real para evaluar el desempeño de los algoritmos:

* **T (Tiempo):** Coste computacional de cada decisión en segundos. Permite analizar la latencia introducida por la profundidad del árbol de búsqueda frente a la inmediatez de la tabla Q.
* **Nodos:** Cantidad de estados explorados por turno. Esta métrica es exclusiva para Expectimax e indica la complejidad del árbol de decisión en ese instante.
* **Err (Error):** Una métrica adaptativa según el algoritmo activo:
    * **En Q-Learning (TD-Error):** Representa el Error de Diferencia Temporal. Mide la discrepancia entre la recompensa esperada y la realmente obtenida. Un valor decreciente hacia cero indica que el agente está aprendiendo y sus predicciones se alinean con la realidad.
    * **En Expectimax (Volatilidad):** Calculada como la diferencia absoluta entre la evaluación heurística estática del estado actual y la evaluación profunda tras la búsqueda. Un valor alto indica que la búsqueda profunda ha revelado información táctica (amenazas u oportunidades) que la evaluación superficial ignoraba.
* **Error semántico (`error_sem`):** Métrica interpretativa externa que evalúa la coherencia estratégica de la acción tomada por la IA. Se define como la diferencia entre la distancia desde la acción ejecutada (por ejemplo, la colocación de un pesticida) hasta la posición de la abeja y la distancia mínima entre la abeja y la flor viva más cercana en ese mismo estado. Un valor bajo indica una decisión alineada con una intuición estratégica inmediata, mientras que un valor alto señala una desviación respecto a una alternativa razonable, sin implicar necesariamente un fallo del algoritmo.
## Estructura del Código

El proyecto sigue una arquitectura modular donde la lógica está desacoplada de la vista:

* `main.py`: Punto de entrada de la aplicación.
* `gui.py`: Gestión de la interfaz gráfica, bucle principal y renderizado (Vista/Controlador).
* `board.py` & `flower.py`: Lógica del tablero, gestión de la cuadrícula y entidades (Modelo).
* `bee.py`: Lógica del agente protagonista y navegación A*.
* `humanidad.py`: Lógica y acciones disponibles para el agente antagonista.
* `expectimax.py` & `heuristica.py`: Motor de decisión basado en árbol de búsqueda.
* `qlearning.py`: Motor de aprendizaje por refuerzo tabular.
* `chance_events.py`: Gestión de probabilidades climáticas y reproducción.
* `game_manager.py`: Definición de reglas de finalización (victoria/derrota).

## Controles

* **Clic Izquierdo:** Mover manualmente a la abeja (durante el turno del jugador).
* **Clic Derecho:** Inspeccionar el estado detallado de una flor.
* **Botón "Recoger":** Recolectar néctar y polinizar.
* **Botón "Descansar":** Recuperar energía.
* **Botón "Ir a la colmena":** Activa el piloto automático A*.
* **Botón "Cambiar IA":** Alterna en tiempo real el algoritmo que controla a la Humanidad (Expectimax vs Q-Learning).

## Autores

Proyecto realizado para la asignatura de **Inteligencia Artificial** - Universitat de Barcelona

* **Emma Loberas Carlosena**
* **Jose Candon Rubio**
* **Daniel Barceló Monclus**
* **Pau González Lopez**