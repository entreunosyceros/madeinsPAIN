# madeinsPAIN

<img width="1024" height="512" alt="logo" src="https://github.com/user-attachments/assets/01f10678-6ef8-41b0-8fb1-bf0b647c49c9" />

Juego RPG de terminal escrito en Python. Recorre un mapa procedural, derrota políticos españoles en combates por turnos y consigue **la jubilación**.

Disponible en dos versiones:
- **Terminal** (curses): versión de texto en la terminal.
- **Pygame**: versión gráfica con sprites pixel-art, animaciones, tienda de leyes y música chiptune 8-bit que taladra la cabeza que no veas.


> ⚠️ Este proyecto es una **sátira** con fines de pasar el rato y practicar Python. Todos los personajes son ficticios... bueno, casi.

---

## Tabla de contenidos

- [Instalación](#instalación)
- [Cómo jugar](#cómo-jugar)
- [Controles](#controles)
- [Clases de personaje](#clases-de-personaje)
- [Políticos enemigos](#políticos-enemigos)
- [Tienda de leyes](#tienda-de-leyes)
- [Escalado de enemigos](#escalado-de-enemigos)
- [Objetivo del juego](#objetivo-del-juego)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Licencia y disclaimer](#licencia-y-disclaimer)

---

## Instalación

1. **Clona el repositorio:**

```bash
git clone https://github.com/tuusuario/madeinsPAIN.git
cd madeinsPAIN
```

2. **Ejecuta el juego:**

```bash
python3 run_app.py
```

El lanzador crea automáticamente el entorno virtual (`.venv/`), instala las dependencias y te deja elegir entre la versión **Terminal** o **Gráfica**.

### Ejecución manual (sin lanzador)

```bash
# Crear y activar entorno virtual
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Versión Terminal
python3 main.py

# Versión Gráfica (Pygame)
python3 pygame_game.py
```

---

## Cómo jugar

1. **Splash screen** (solo Pygame): muestra `img/logo.png` durante 4 segundos. Pulsa `ENTER` para saltarlo. Suena música chiptune de fondo durante todo el juego.
2. **Pantalla de título:** Pulsa `ENTER` para comenzar o `Q`/`ESC` para salir.
3. **Selecciona tu clase social:** Usa las flechas ↑/↓ y pulsa `ENTER`.
4. **Tutorial:** Lee las 4 páginas de instrucciones. Pulsa `ENTER` o `→` para avanzar, `←` para retroceder.
5. **Ponle nombre:** Escribe tu nombre y confirma con `ENTER`.
6. **Explora el mapa:** Muévete con las flechas o WASD. El mapa tiene **cámara** que sigue al jugador.
7. **Encuentra enemigos:** Al pisar la casilla de un político entrarás en combate.
8. **Recolecta recompensas:** Oro (`$`), pociones (`!`) y fuentes de salud (`+`).
9. **Sube de nivel:** Gana XP derrotando enemigos. Al subir de nivel se abre la **tienda de leyes**.
10. **Compra leyes:** Usa tu oro para comprar habilidades que te hacen más fuerte.
11. **¡Jubílate!** Al alcanzar el **nivel 10** consigues la jubilación.

---

## Controles

<img width="881" height="492" alt="pantalla-madeinspain" src="https://github.com/user-attachments/assets/2d79b079-9200-480f-8e19-e1fb5760a85b" />


### En el mapa

| Tecla | Acción |
|-------|--------|
| `↑` `↓` `←` `→` | Moverse por el mapa |
| `W` `A` `S` `D` | Moverse (alternativa) |
| `Q` / `ESC` | Salir del juego |

### En combate

| Tecla | Acción |
|-------|--------|
| `A` | **Atacar** |
| `D` | **Defender** (reduce a la mitad el daño del siguiente golpe enemigo) |
| `P` | **Poción** (recupera ~40 % de HP; consume 1) |
| `H` | **Huir** (50 % de éxito; si fallas pierdes el turno) |

### En la tienda de leyes

| Tecla | Acción |
|-------|--------|
| `↑` `↓` | Navegar entre habilidades |
| `ENTER` | Comprar la habilidad seleccionada |
| `ESC` | Salir de la tienda y volver al mapa |

---

## Clases de personaje

| Clase | Símbolo | HP | Daño | Especial |
|-------|---------|-----|------|----------|
| **Trabajador** | `T` | 120 | 15-25 | +3 defensa |
| **Parado** | `D` | 90 | 12-22 | 20 % esquiva |
| **Parado de larga duración** | `L` | 70 | 22-38 | Alto daño |
| **Empresario** | `E` | 50 | 18-32 | Empieza con 50 de oro, 15 % esquiva |

---

## Enemigos

Los enemigos aparecen distribuidos por dificultad: los más débiles salan al principio; los más duros aparecen más adelante. Cada enemigo **oscila 2 tiles** desde su posición y **respeta los muros** como el jugador.

| Político | Símbolo | HP | Daño |
|----------|---------|-----|------|
| **Figaredo** | `G` | 20 | 2-5 |
| **Feijóo** | `F` | 30 | 3-7 |
| **Abascal** | `A` | 35 | 4-9 |
| **Ayuso** | `I` | 40 | 5-10 |
| **Puigdemont** | `C` | 45 | 5-11 |
| **Yolanda Díaz** | `Y` | 60 | 8-15 |
| **Sánchez** | `S` | 70 | 10-18 |
| **Rufián** | `R` | 80 | 11-20 |
| **Belarra** | `B` | 85 | 12-21 |
| **Junqueras** | `J` | 95 | 13-23 |

### Comportamiento de enemigos

- Se mueven **±2 tiles** desde su posición original, oscilando continuamente.
- **No atraviesan muros**: si hay un obstáculo, se deslizan hasta la última casilla válida.
- **No se solapan entre sí**: si un enemigo ocupa una casilla, otro no puede moverse ahí.
- Al comprar una habilidad, los enemigos del mapa actual se **re-escalan** automáticamente.

---

## Tienda de leyes (solo versión gráfica)

Al **subir de nivel**, aparece una tienda donde puedes comprar leyes que otorgan habilidades permanentes. Los enemigos del mapa actual se reescalan automáticamente.

### Categorías y habilidades

| Categoría | Habilidad | Coste | Efecto |
|-----------|-----------|-------|--------|
| **Leyes Orgánicas** | Ley de amnistía | 120 | +20 % HP máximo y curación completa |
| | Ley de educación | 150 | +15 % daño de ataque |
| **Leyes Ordinarias** | Ley de presupuestos | 80 | +5 daño (mín y máx) |
| | Ley de seguridad ciudadana | 100 | +3 defensa |
| **Normas con rango de ley** | Real Decreto-ley | 70 | +2 defensa y +25 HP máximo |
| | Ley de refuerzo | 90 | +30 HP máximo |
| **Reglamentos** | Reglamento europeo | 50 | +10 % esquiva |
| | Reglamento sancionador | 60 | +3 daño y +1 defensa |
| **Leyes Autonómicas** | Ley del Parlament | 40 | +2 pociones y +10 HP máximo |
| | Decreto 78/2025 | 55 | +8 % esquiva y +1 defensa |

---

## Escalado de enemigos

Los enemigos se vuelven más difíciles según cuántas **habilidades** haya comprado el jugador. Cada habilidad aumenta su HP y daño un **15 %**.

---

## Música (solo versión gráfica)

El juego incluye **música chiptune procedural** generada en tiempo real con ondas cuadradas, al estilo de los RPG de los años 80. No requiere archivos de audio externos.

| Escena | Estilo |
|--------|--------|
| **Menú / Exploración** | Melodía épica con progresión Am-F-G-Em |
| **Combate** | Ritmo rápido y agresivo (150 BPM) |
| **Tienda** | Melodía tranquila y misteriosa (75 BPM) |

La música se genera con `pygame.mixer.Sound` usando ondas cuadradas, triangulares y envolventes ADSR para conseguir el sonido auténtico de consolas de 8 bits.

| Habilidades | Multiplicador | Ejemplo (base 50 HP, 10-20 daño) |
|-------------|--------------|----------------------------------|
| 0 | ×1.00 | 50 HP, 10-20 daño |
| 1 | ×1.15 | 57 HP, 11-23 daño |
| 3 | ×1.45 | 72 HP, 14-29 daño |
| 5 | ×1.75 | 87 HP, 17-35 daño |
| 10 | ×2.50 | 125 HP, 25-50 daño |

---

## Objetivo del juego

Sube de nivel derrotando políticos. Necesitas **~57 combates** (6-8 mapas) para alcanzar el nivel 10 y conseguir la **jubilación**.

### Progresión de niveles

| Nivel | XP necesaria | Combates aprox. |
|-------|-------------|-----------------|
| 1 → 2 | 50 | ~2 |
| 2 → 3 | 65 | ~2-3 |
| 3 → 4 | 84 | ~3 |
| 4 → 5 | 109 | ~4 |
| 5 → 6 | 141 | ~5 |
| 6 → 7 | 183 | ~7 |
| 7 → 8 | 237 | ~9 |
| 8 → 9 | 308 | ~11 |
| 9 → 10 | 400 | ~15 |

Al subir de nivel recuperas toda la vida, ganas +15 HP máximo y +2 al daño.

---

## Estructura del proyecto

```
.
├── run_app.py          # Lanzador: crea venv, instala deps, elige version.
├── main.py             # Punto de entrada (versión terminal).
├── pygame_game.py      # Punto de entrada (versión gráfica Pygame).
├── pygame_ui.py        # Renderizado gráfico: sprites, mapas, menus, tienda.
├── pygame_combat.py    # Combate interactivo con animaciones Pygame.
├── music.py            # Generador de musica chiptune procedural 8-bit.
├── engine.py           # Bucle de exploración (terminal).
├── player.py           # Clases, stats, progresión, habilidades (compartido).
├── map.py              # Generación procedural, enemigos, recompensas, escalado.
├── ui.py               # Capa de presentación (terminal, curses).
├── combat_engine.py    # Combate interactivo (terminal, curses).
├── combat_ui.py        # Utilidades gráficas del combate (terminal).
├── img/                # Assets gráficos (logo, sprites).
│   └── logo.png        # Imagen del splash screen.
├── requirements.txt    # Dependencias del proyecto.
└── README.md           # Este archivo.
```

### Arquitectura

- **Modelo:** `player.py` + `map.py` (datos puros, compartidos por ambas versiones).
- **Controlador:** `engine.py` / `pygame_game.py` (lógica de juego).
- **Vista terminal:** `ui.py` + `combat_ui.py` (renderizado con `curses`).
- **Vista gráfica:** `pygame_ui.py` + `pygame_combat.py` (renderizado con `pygame`).
- **Entry points:** `main.py` (curses) y `pygame_game.py` (Pygame).
- **Lanzador:** `run_app.py` (gestiona venc y lanza la versión elegida).

---

## Licencia y disclaimer

Este software se distribuye bajo licencia **MIT**.

> **Aviso:** Todos los nombres, personajes y situaciones representados en este juego son **ficticios** o utilizados en un contexto de **sátira y parodia**. No representan opiniones políticas reales del autor. No se pretende ofender a ninguna persona ni partido político. Si te ofendes fácilmente, juega en modo *Zen* (no existe, pero sería una buena idea).

---

**Hecho con Python, cafeína y un poco de cinismo.** ☕
