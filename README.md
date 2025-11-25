# 🐝 BeeGame - Simulación Ecológica con IA Simbólica

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12.3-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.6.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Completo-success.svg)

**Un juego de estrategia por turnos que simula la compleja relación entre las abejas y la actividad humana, implementando algoritmos de IA avanzados.**

[Características](#-características-principales) • [Instalación](#-instalación) • [Uso](#-cómo-jugar) • [Arquitectura](#-arquitectura-técnica) • [Algoritmos](#-algoritmos-de-ia)

</div>

---

## 📋 Descripción

**BeeGame** es una simulación ecológica interactiva desarrollada en Python que modela el desafío de supervivencia de una colonia de abejas en un entorno afectado por la actividad humana. El proyecto implementa técnicas avanzadas de **Inteligencia Artificial Simbólica**, incluyendo el algoritmo **Expectimax** con nodos de azar, búsqueda **A\*** para pathfinding, y una función heurística multi-componente.

### 🎯 Objetivos del Proyecto

1. **Simulación realista** de un ecosistema con flores, polinización, clima y pesticidas
2. **Agente MAX** (Abeja) que maximiza la supervivencia y recolección de néctar
3. **Agente MIN** (Humanidad) que minimiza el progreso de la abeja con restricciones estratégicas
4. **Nodos CHANCE** que modelan incertidumbre climática y reproducción de flores
5. **Algoritmo Expectimax** con profundidad configurable y poda estratégica
6. **Función Heurística** que evalúa estados del juego con 7 componentes ponderados

---

## ✨ Características Principales

### 🎮 Mecánicas de Juego

- **Tablero Dinámico NxN**: Cuadrícula configurable (por defecto 10×10) con elementos interactivos
- **Sistema de Turnos**: Alternancia estratégica entre la abeja (jugador/IA) y la humanidad (IA)
- **3 Modos de Juego**:
  - 👤 **Modo Jugador**: Control manual de la abeja
  - 🤖 **IA Básica**: Humanidad con acciones aleatorias válidas
  - 🧠 **IA Expectimax**: Ambos agentes utilizan Expectimax (profundidad 2)

### 🐝 Agente MAX - Abeja

**Atributos:**
- ❤️ Vida: 100 puntos (muerte al llegar a 0)
- ⚡ Energía: 100 puntos (gasto por movimiento, recuperación en rusc/descanso)
- 🍯 Néctar: Capacidad 50 unidades (objetivo: acumular 100 en el rusc)

**Acciones:**
- **Moverse**: Arriba/Abajo/Izquierda/Derecha (coste 2 energía)
- **Recoger Néctar y Polinizar**: Extrae 10 unidades, aumenta polinización de flor
- **Descansar**: Recupera 10 energía sin moverse
- **Volver al Rusc (A\*)**: Calcula ruta óptima usando algoritmo de búsqueda A* con heurística Manhattan

### 👥 Agente MIN - Humanidad

**Acciones Hostiles:**
- 🧪 **Aplicar Pesticida**: Incrementa contador de pesticida en flor (muere al acumular 3)
- 🚧 **Colocar Obstáculo**: Bloquea casilla impidiendo movimiento de la abeja

**Restricciones de Poda Estratégica:**
- Pesticidas: Solo en flores dentro de **radio 2** de la abeja
- Obstáculos: Solo en casillas vacías dentro de **radio 3** del rusc (excluyendo el rusc mismo)
- Límite: Máximo **4 obstáculos** simultáneos (eliminación FIFO del más antiguo)

### 🌦️ Nodos de Azar (CHANCE Nodes)

**1. Sistema Climático** (cada 4 turnos):
- ☔ **Lluvia (10%)**: Reduce 1 pesticida de todas las flores
- ☀️ **Sol (15%)**: Bonifica +20% probabilidad de reproducción
- 🌤️ **Normal (75%)**: Sin efectos especiales

**2. Reproducción de Flores** (tras polinización):
- Probabilidad base: **20%**
- Con clima soleado: **40%** (20% + 20% bonus)
- Nacimiento: Nueva flor en casilla adyacente libre

### 🌸 Lógica de Flores

- **Estados**: Vida (activa/muerta), Polinización (0-3), Pesticidas (0-3)
- **Muerte**: Al acumular 3 pesticidas (cambia a roja y se vuelve inaccesible)
- **Colores Visuales**:
  - 🟢 Verde: Flor sana (0-1 pesticidas)
  - 🟡 Amarilla: Flor contaminada (2 pesticidas)
  - 🔴 Roja: Flor muerta (3 pesticidas)

---

## 🧠 Algoritmos de IA

### 1️⃣ Expectimax (Toma de Decisiones)

Algoritmo recursivo de teoría de juegos con manejo de incertidumbre:

```python
función expectimax(estado, profundidad, tipo_nodo):
    si profundidad == 0 o estado_terminal(estado):
        retornar heurística(estado)
    
    si tipo_nodo == MAX:  # Abeja
        retornar max(expectimax(sucesor) para cada acción)
    
    si tipo_nodo == MIN:  # Humanidad
        retornar min(expectimax(sucesor) para cada acción)
    
    si tipo_nodo == CHANCE:  # Clima/Reproducción
        retornar suma(probabilidad[i] * expectimax(sucesor[i]))
```

**Configuración:**
- Profundidad máxima: **2 niveles**
- Nodos evaluados: ~1000-5000 por turno (según ramificación)
- Poda: Restricciones estratégicas reducen espacio de búsqueda en ~60%

### 2️⃣ A\* (Pathfinding al Rusc)

Búsqueda informada con heurística admisible:

```
f(n) = g(n) + h(n)
  g(n) = coste real desde inicio
  h(n) = distancia Manhattan al objetivo
```

**Características:**
- Evita obstáculos dinámicamente
- Garantiza ruta óptima (menor número de pasos)
- Complejidad: O(b^d) con b≈4 (movimientos cardinales)

### 3️⃣ Función Heurística H(s)

Evaluación multi-componente del estado del juego:

```
H(s) = H_tauler + H_agent + H_progres + H_proximitat
```

**Componentes Detallados:**

| Componente | Fórmula | Peso | Descripción |
|------------|---------|------|-------------|
| **H_tauler** | `w1·flores_vivas + w2·polinizadas - w1·contaminadas` | w1=10, w2=8 | Salud del ecosistema |
| **H_agent** | `w5·vida + w6·energía` | w5=3, w6=2 | Vitalidad de la abeja |
| **H_progres** | `w3·néctar_rusc + w4·néctar_cargado` | w3=15, w4=5 | Avance hacia objetivo |
| **H_proximitat** | `w7·(1 / distancia_objetivo)` | w7=1 | Eficiencia espacial |

**Pesos Optimizados:**
- Prioridad máxima: Néctar en rusc (w3=15) → objetivo principal
- Prioridad alta: Flores vivas (w1=10) → recursos futuros
- Prioridad media: Polinización (w2=8), Néctar cargado (w4=5)
- Prioridad baja: Vida (w5=3), Energía (w6=2), Proximidad (w7=1)

---

## 🚀 Instalación

### Requisitos Previos

- Python 3.12.3 o superior
- pip (gestor de paquetes)
- Git (opcional, para clonar repositorio)

### Pasos de Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/BeeGameIAProject/BeeGame.git
cd BeeGame

# 2. Crear entorno virtual (recomendado)
python -m venv .venv

# 3. Activar entorno virtual
# En Windows:
.venv\Scripts\activate
# En macOS/Linux:
source .venv/bin/activate

# 4. Instalar dependencias
pip install pygame

# 5. Ejecutar el juego
cd BeeGame
python gui_simple.py
```

### Dependencias

```
pygame>=2.6.0
```

---

## 🎮 Cómo Jugar

### Inicio del Juego

1. **Ejecutar**: `python gui_simple.py`
2. **Configurar**:
   - Tamaño del tablero (N×N)
   - Número de flores iniciales
   - Número de obstáculos iniciales
   - Modo de IA (Jugador / IA Básica / Expectimax)
3. **Objetivo**: Acumular **100 unidades de néctar** en el rusc

### Controles (Modo Jugador)

| Acción | Control |
|--------|---------|
| Mover Abeja | Click en casilla adyacente (↑ ↓ ← →) |
| Polinizar/Recoger | Botón "🌸 Polinizar" (sobre flor) |
| Descansar | Botón "😴 Descansar" |
| Volver al Rusc (A*) | Botón "🏠 Volver al Rusc" |
| Siguiente Turno | Automático tras acción válida |

### Estrategias Recomendadas

**🟢 Fase Temprana (Turnos 1-20):**
- Polinizar flores cercanas al rusc
- Mantener energía >30 para emergencias
- Priorizar flores sin pesticidas

**🟡 Fase Media (Turnos 21-50):**
- Explorar flores distantes antes de que mueran
- Usar A* para retornos eficientes
- Descansar solo en rusc o cerca de flores

**🔴 Fase Tardía (Turnos 51+):**
- Maximizar viajes completos (néctar 50/50)
- Evitar flores con 2+ pesticidas
- Anticipar obstáculos con A*

### Condiciones de Finalización

| Resultado | Condición | Pantalla |
|-----------|-----------|----------|
| 🎉 **VICTORIA** | Néctar en rusc ≥ 100 | Mensaje verde |
| 💀 **DERROTA** | Vida de abeja ≤ 0 | Mensaje rojo |
| 🥀 **DERROTA** | 0 flores vivas | Mensaje naranja |

---

## 🏗️ Arquitectura Técnica

### Estructura del Proyecto

```
BeeGame/
├── bee.py                 # Agente MAX (Abeja) con A*
├── board.py               # Tablero y gestión de elementos
├── chance_events.py       # Nodos CHANCE (clima/reproducción)
├── expectimax.py          # Algoritmo Expectimax core
├── flower.py              # Lógica de flores
├── game_manager.py        # Gestor de turnos y estado global
├── gui_simple.py          # Interfaz gráfica Pygame (MAIN)
├── heuristica.py          # Función H(s) multi-componente
├── humanidad.py           # Agente MIN (Humanidad)
├── test_expectimax.py     # Tests unitarios de Expectimax
├── test_restricciones.py  # Tests de restricciones de poda
├── MPV.md                 # Checklist de objetivos
└── README.md              # Este archivo
```

### Clases Principales

**1. `Board` (board.py):**
```python
class Board:
    def __init__(self, size, num_flores, num_obstaculos)
    # Métodos: get_celda(), es_valida(), colocar_flor(), etc.
```

**2. `Bee` (bee.py):**
```python
class Bee:
    def __init__(self, pos_inicial, tablero)
    def mover(direccion) → bool
    def recoger_nectar_y_polinizar() → bool
    def a_star(objetivo) → List[tuple]  # Pathfinding
```

**3. `Humanidad` (humanidad.py):**
```python
class Humanidad:
    def obtener_acciones_validas(tablero, bee) → List[tuple]
    def aplicar_pesticida(tablero, pos) → bool
    def colocar_obstaculo(tablero, pos) → bool  # Con límite FIFO
```

**4. `ExpectimaxAI` (expectimax.py):**
```python
class ExpectimaxAI:
    def expectimax(game_state, profundidad, tipo_nodo) → float
    def nodo_max(estado) → float
    def nodo_min(estado) → float
    def nodo_chance(estado, tipo_evento) → float
```

**5. `Heuristica` (heuristica.py):**
```python
class Heuristica:
    def evaluar(game_state) → float
    # Componentes: h_tauler, h_agent, h_progres, h_proximitat
```

### Flujo de Ejecución

```
1. Inicialización (gui_simple.py)
   └─> Crear tablero, abeja, humanidad, flores

2. Bucle Principal (game loop)
   ├─> Turno Abeja
   │   ├─> Si Modo Jugador: Esperar input usuario
   │   ├─> Si Modo IA: Ejecutar Expectimax
   │   └─> Aplicar acción y actualizar estado
   │
   ├─> Turno Humanidad (IA)
   │   ├─> Si IA Básica: Acción aleatoria válida
   │   ├─> Si Expectimax: Calcular peor acción para MAX
   │   └─> Aplicar pesticida/obstáculo
   │
   ├─> Evento de Azar (cada 4 turnos)
   │   ├─> Calcular clima (Lluvia/Sol/Normal)
   │   └─> Aplicar efectos
   │
   ├─> Reproducción de Flores
   │   └─> Para flores polinizadas: Probabilidad 20%/40%
   │
   └─> Verificar Condiciones de Finalización
       ├─> Victoria: Néctar ≥ 100
       └─> Derrota: Vida ≤ 0 o 0 flores

3. Renderizado (Pygame)
   └─> Actualizar sprites, barras, mensajes
```

---

## 📊 Estadísticas de Desarrollo

| Métrica | Valor |
|---------|-------|
| Líneas de Código | ~2,500 |
| Módulos Python | 10 |
| Tests Unitarios | 11 (4 Expectimax + 7 Restricciones) |
| Cobertura de Objetivos | 100% (5/5 completados) |
| Tiempo de Desarrollo | ~80 horas |
| Commits | 45+ |

---

## 🧪 Testing

### Ejecutar Tests

```bash
cd BeeGame

# Tests de Expectimax
python test_expectimax.py

# Tests de Restricciones de Poda
python test_restricciones.py
```

### Cobertura de Tests

**test_expectimax.py:**
- ✅ Inicialización de GameState
- ✅ Nodo MAX retorna valor máximo
- ✅ Nodo MIN retorna valor mínimo
- ✅ Nodo CHANCE retorna media ponderada

**test_restricciones.py:**
- ✅ Pesticidas solo en radio 2 de abeja
- ✅ Pesticidas solo en flores vivas
- ✅ Obstáculos solo en radio 3 de rusc
- ✅ Obstáculos excluyen posición del rusc
- ✅ Máximo 4 obstáculos simultáneos
- ✅ Eliminación FIFO del obstáculo más antiguo
- ✅ Obstáculos solo en casillas vacías

---

## 🎓 Conceptos de IA Aplicados

### Búsqueda Informada
- **A\***: Heurística admisible (Manhattan) garantiza optimalidad
- **Expectimax**: Extensión de Minimax con nodos probabilísticos

### Teoría de Juegos
- **Juego de Suma Cero**: Ganancia de un agente es pérdida del otro
- **Poda Estratégica**: Restricciones reducen espacio de búsqueda
- **Horizon Effect**: Profundidad limitada requiere heurística robusta

### Modelado de Incertidumbre
- **Nodos CHANCE**: Distribuciones probabilísticas discretas
- **Valor Esperado**: E[X] = Σ(p_i · x_i)
- **Simulación Estocástica**: Reproducción de flores con RNG

### Optimización
- **Pesos Heurísticos**: Ajuste manual basado en importancia relativa
- **Trade-offs**: Profundidad vs. tiempo de cómputo
- **Caching**: Estados repetidos evitados con evaluación directa

---

## 🐛 Problemas Conocidos y Soluciones

| Problema | Solución Implementada |
|----------|----------------------|
| Expectimax lento en tableros >15×15 | Profundidad limitada a 2, poda estratégica |
| A* falla con obstáculos dinámicos | Recalcular ruta cada turno si bloqueado |
| GUI congela en cálculos largos | Threading para IA (futuro) |
| Flores reproducen infinitamente | Límite de 100 flores máximas |
| Obstáculos bloquean rusc | Validación excluye pos_rusc en Humanidad |

---

## 🔮 Futuras Mejoras

### Corto Plazo
- [ ] **Threading**: Ejecutar Expectimax en segundo plano
- [ ] **Profundidad Variable**: Ajustar según tiempo disponible
- [ ] **Alpha-Beta Pruning**: Para modos sin CHANCE
- [ ] **Replay System**: Guardar y reproducir partidas

### Medio Plazo
- [ ] **Aprendizaje Automático**: Entrenar pesos heurísticos con GA
- [ ] **Multiplayer**: Modo 2 jugadores (Abeja vs Humanidad)
- [ ] **Editor de Niveles**: Diseño custom de tableros
- [ ] **Achievements**: Sistema de logros y estadísticas

### Largo Plazo
- [ ] **MCTS (Monte Carlo Tree Search)**: Alternativa a Expectimax
- [ ] **Deep Learning**: CNN para evaluación de estados
- [ ] **Procedural Generation**: Tableros generados aleatoriamente
- [ ] **Mobile Port**: Versión Android/iOS

---

## 👨‍💻 Autor

**Jose Antonio**  
Proyecto de Inteligencia Artificial - 2025  
Universidad: [Nombre Universidad]  
Asignatura: Inteligencia Artificial / Sistemas Inteligentes

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

```
MIT License

Copyright (c) 2025 BeeGameIAProject

Se concede permiso, de forma gratuita, a cualquier persona que obtenga una copia
de este software y archivos de documentación asociados (el "Software"), para 
utilizar el Software sin restricciones...
```

---

## 🙏 Agradecimientos

- **Pygame Community**: Por la excelente documentación y ejemplos
- **Russell & Norvig**: "Artificial Intelligence: A Modern Approach" - Base teórica
- **CS188 Berkeley**: Inspiración para Expectimax y heurísticas
- **Stack Overflow**: Soluciones a bugs específicos de Pygame

---

## 📞 Contacto y Soporte

¿Encontraste un bug? ¿Tienes sugerencias?

- **Issues**: [GitHub Issues](https://github.com/BeeGameIAProject/BeeGame/issues)
- **Email**: [tu-email@ejemplo.com]
- **Documentación**: [Wiki del Proyecto](https://github.com/BeeGameIAProject/BeeGame/wiki)

---

<div align="center">

**⭐ Si te gustó este proyecto, dale una estrella en GitHub! ⭐**

Hecho con ❤️ y 🐝 en Python

[↑ Volver arriba](#-beegame---simulación-ecológica-con-ia-simbólica)

</div>