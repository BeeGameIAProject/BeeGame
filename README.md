# 🐝 BeeGame - Simulación Ecológica con IA

![Python](https://img.shields.io/badge/Python-3.12.3-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.6.0-green.svg)
![Status](https://img.shields.io/badge/Status-Completo-success.svg)

---

## 📋 ¿Qué es BeeGame?

**BeeGame** es un juego de estrategia por turnos donde controlas una abeja que debe sobrevivir y recolectar néctar en un entorno hostil. El proyecto implementa algoritmos de **Inteligencia Artificial** avanzados como **Expectimax**, **A\*** y funciones heurísticas para crear una experiencia de juego desafiante.

### 🌍 Objetivo Educativo

Este proyecto busca **concienciar sobre la importancia de las abejas y el medio ambiente** a través de una experiencia interactiva. Al jugar, experimentas los desafíos reales que enfrentan las abejas en ecosistemas afectados por pesticidas y la actividad humana. El juego demuestra cómo:

- 🐝 Las abejas son **esenciales para la polinización** y el equilibrio ecológico
- 🧪 Los **pesticidas** representan una amenaza grave para su supervivencia
- 🌸 La **desaparición de flores** afecta directamente la cadena alimentaria
- 🚧 Los **obstáculos ambientales** dificultan su labor polinizadora

A través de la mecánica del juego, se evidencia la lucha constante de estos insectos por sobrevivir mientras cumplen su función vital en la naturaleza.

---

## 🎮 Cómo Funciona

### El Tablero
- Cuadrícula de **10×10 casillas** (configurable)
- Elementos: 🏠 Rusc (colmena), 🌸 Flores, 🚧 Obstáculos, 🐝 Abeja

### La Abeja (Tú)
- **❤️ Vida**: 100 puntos
- **⚡ Energía**: 100 puntos (gasta 2 por movimiento)
- **🍯 Néctar**: Capacidad de 50 unidades
- **Objetivo**: Acumular unidades de néctar en el rusc

### La Humanidad (IA)
- Intenta impedir que ganes usando:
  - 🧪 **Pesticidas**: Matan flores (mueren al acumular 3)
  - 🚧 **Obstáculos**: Bloquean tu paso

### Eventos Aleatorios
Cada 4 (aproximadamente) turnos ocurre un evento climático:
- ☔ **Lluvia (10%)**: Limpia pesticidas de las flores
- ☀️ **Sol (15%)**: Aumenta reproducción de flores
- 🌤️ **Normal (75%)**: Sin efectos

---

## 🚀 Instalación

```bash
# 1. Clonar o descargar el proyecto
cd BeeGame

# 2. Crear entorno virtual (opcional pero recomendado)
python -m venv .venv
.venv\Scripts\activate  # En Windows
source .venv/bin/activate  # En Linux/Mac

# 3. Instalar Pygame
pip install pygame

# 4. Ejecutar el juego
cd BeeGame
python main.py
```

---

## 🎯 Cómo Jugar

### Configuración Inicial
Al iniciar el juego, elige:
- Tamaño del tablero
- Número de flores
- Modo de juego:
  - **👤 Jugador**: Tú controlas la abeja
  - **🤖 IA Básica**: La humanidad juega aleatoriamente
  - **🧠 Expectimax**: Ambos usan IA avanzada

### Controles

| Acción | Cómo hacerlo |
|--------|--------------|
| **Mover** | Click en casilla adyacente |
| **Polinizar** | Botón "🌸 Polinizar" |
| **Descansar** | Botón "😴 Descansar" (recupera 10 energía) |
| **Volver al Rusc** | Botón "🏠 Volver al Rusc" (usa A* para ruta óptima) |


### Ganar y Perder

| Resultado | Condición |
|-----------|-----------|
| 💀 **DERROTA** | Tu vida llega a 0 |
| 🥀 **DERROTA** | No quedan flores vivas en el tablero |

---

## 🧠 Tecnología Utilizada

### Algoritmos de IA
- **Expectimax**: Toma decisiones óptimas considerando probabilidades
- **A\* (A-Star)**: Calcula la ruta más corta al rusc evitando obstáculos
- **Función Heurística**: Evalúa qué tan bueno es un estado del juego

### Mecánicas Inteligentes
- La IA solo puede poner pesticidas cerca de la abeja (radio 2)
- Los obstáculos solo se pueden colocar cerca del rusc (radio 3)
- Máximo 4 obstáculos a la vez (se elimina el más antiguo)

---

## 📁 Estructura del Proyecto

```
BeeGame/
├── src/                       # Código fuente
│   ├── bee.py                 # Lógica de la abeja (movimiento, A*)
│   ├── board.py               # Tablero del juego
│   ├── chance_events.py       # Eventos climáticos aleatorios
│   ├── expectimax.py          # Algoritmo de IA principal
│   ├── flower.py              # Lógica de las flores
│   ├── game_manager.py        # Gestión de victoria/derrota
│   ├── heuristica.py          # Evaluación de estados
│   └── humanidad.py           # Lógica de la humanidad (IA enemiga)
├── docs/                      # Documentación
│   └── MPV.md                 # Checklist de objetivos completados
├── main.py                    # ▶️ EJECUTAR ESTE ARCHIVO
├── gui_simple.py              # Interfaz gráfica del juego
└── README.md                  # Este archivo
```

---

## 🎓 ¿Qué Aprenderás?

Este proyecto demuestra:
- Algoritmos de búsqueda informada (A*)
- Teoría de juegos (Expectimax con nodos de azar)
- Modelado de incertidumbre
- Funciones heurísticas multi-componente
- Desarrollo de juegos con Pygame

---

## 📞 Ayuda

¿Problemas para ejecutar el juego?

1. Asegúrate de tener Python 3.12+ instalado
2. Instala Pygame: `pip install pygame`
3. Ejecuta desde la carpeta BeeGame: `python main.py`

---

<div align="center">

Hecho con ❤️ y 🐝 en Python

</div>