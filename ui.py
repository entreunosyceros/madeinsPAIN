#!/usr/bin/env python3
"""
ui.py

Capa de presentacion del juego. Se encarga de todo el dibujado en pantalla
mediante la libreria `curses`: mapa, menus, barras de vida, titulos y
transiciones. Tambien gestiona la configuracion de colores.

Todas las operaciones de dibujado estan envueltas en try/except para evitar
crashes si el terminal es demasiado pequeno.
"""

import curses
import time
from map import WALL


class UI:
    """Renderiza todas las pantallas del juego."""

    def __init__(self, stdscr):
        """Inicializa los pares de colores de curses.

        Args:
            stdscr: Ventana principal de curses.
        """
        self.stdscr = stdscr
        self._init_colors()

    # --- Configuracion de colores ---

    def _init_colors(self):
        """Define los pares de color utilizados en todo el juego.

        Pares:
            1 - Rojo    (Trabajador / enemigos)
            2 - Azul    (Parado de larga duracion)
            3 - Verde   (Parado)
            4 - Amarillo (Oro, VS, titulos)
            5 - Magenta (Empresario)
            6 - Cyan    (Pociones)
            7 - Blanco  (Muros)
            8 - Rojo oscuro (titulos de combate)
        """
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_RED, -1)
        curses.init_pair(2, curses.COLOR_BLUE, -1)
        curses.init_pair(3, curses.COLOR_GREEN, -1)
        curses.init_pair(4, curses.COLOR_YELLOW, -1)
        curses.init_pair(5, curses.COLOR_MAGENTA, -1)
        curses.init_pair(6, curses.COLOR_CYAN, -1)
        curses.init_pair(7, curses.COLOR_WHITE, -1)
        curses.init_pair(8, curses.COLOR_RED, curses.COLOR_BLACK)

    # --- Utilidades de dibujado ---

    def center_text(self, y, text, attr=0):
        """Dibuja un texto centrado horizontalmente.

        Args:
            y: Fila donde escribir.
            text: Cadena de texto.
            attr: Atributos de curses (color, negrita, etc.).
        """
        h, w = self.stdscr.getmaxyx()
        x = max(0, (w - len(text)) // 2)
        try:
            self.stdscr.addstr(y, x, text, attr)
        except curses.error:
            pass

    # --- Pantalla de titulo ---

    def title_screen(self):
        """Muestra la pantalla de bienvenida con el nombre del juego.

        Espera ENTER para continuar o Q/ESC para salir.
        """
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()

        # Recuadro decorativo con el titulo del juego.
        box_w = 44
        box_x = max(0, (w - box_w) // 2)
        box_y = max(2, (h - 10) // 2)

        border = "+" + "=" * (box_w - 2) + "+"
        self.stdscr.addstr(box_y, box_x, border, curses.A_BOLD)
        self.stdscr.addstr(box_y + 1, box_x,
                           "|" + " " * (box_w - 2) + "|", curses.A_BOLD)
        self.center_text(box_y + 2, "|  m a d e i n s P A I N              |",
                         curses.A_BOLD | curses.color_pair(4))
        self.center_text(box_y + 3,
                         "|  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~         |",
                         curses.A_BOLD)
        self.center_text(box_y + 4, "|" + " " * (box_w - 2) + "|", curses.A_BOLD)
        self.center_text(box_y + 5, "|  ~  RPG  Terminal  ~                 |",
                         curses.A_DIM)
        self.center_text(box_y + 6,
                         "|" + " " * (box_w - 2) + "|", curses.A_BOLD)
        self.stdscr.addstr(box_y + 7, box_x, border, curses.A_BOLD)

        self.center_text(box_y + 9, "Presiona ENTER para COMENZAR", curses.A_BOLD)
        self.center_text(box_y + 10, "Q o ESC para salir", curses.A_DIM)

        self.stdscr.refresh()
        key = self.stdscr.getch()
        if key in (ord("q"), ord("Q"), 27):
            import sys
            sys.exit(0)

    # --- Seleccion de clase ---

    def select_class(self):
        """Menu interactivo para elegir la clase del personaje.

        Returns:
            str: Clave de la clase seleccionada (ej. "trabajador").
        """
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()

        self.center_text(2, "=== SELECCIONA TU CLASE ===", curses.A_BOLD)

        # Ficha de cada clase disponible.
        classes = [
            {"key": "trabajador", "name": "Trabajador", "char": "T",
             "desc": "Alta vida (120) y defensa. Daño equilibrado.",
             "color": curses.color_pair(1)},
            {"key": "parado", "name": "Parado", "char": "D",
             "desc": "Vida media (90), esquiva ataques enemigos.",
             "color": curses.color_pair(3)},
            {"key": "parado_largo", "name": "Parado de larga duracion", "char": "L",
             "desc": "Poca vida (70) pero gran poder de ataque.",
             "color": curses.color_pair(2)},
            {"key": "empresario", "name": "Empresario", "char": "E",
             "desc": "Vida baja (50), daño alto. Empieza con 50 oro.",
             "color": curses.color_pair(5)},
        ]

        selected = 0
        while True:
            for i, cls in enumerate(classes):
                y = 5 + i * 3
                prefix = "> " if i == selected else "  "
                marker = " [X]" if i == selected else " [ ]"
                line = f"{prefix}[{cls['char']}]{marker} {cls['name']}"
                attr = cls["color"] | curses.A_BOLD if i == selected else curses.A_DIM
                self.center_text(y, line, attr)
                self.center_text(y + 1, f"      {cls['desc']}",
                                 cls["color"] if i == selected else curses.A_DIM)

            self.center_text(h - 2, "ENTER: confirmar  |  Flechas: elegir  |  Q/ESC: salir",
                             curses.A_DIM)
            self.stdscr.refresh()

            key = self.stdscr.getch()
            if key in (ord("q"), ord("Q"), 27):
                import sys
                sys.exit(0)
            if key == curses.KEY_UP and selected > 0:
                selected -= 1
            elif key == curses.KEY_DOWN and selected < len(classes) - 1:
                selected += 1
            elif key in (10, 13, curses.KEY_ENTER):
                return classes[selected]["key"]

    # --- Introduccion del nombre ---

    def input_name(self, char_class):
        """Pantalla para que el jugador escriba su nombre.

        Args:
            char_class: Clave de la clase ya elegida (solo para mostrarla).

        Returns:
            str: Nombre introducido (sin espacios al inicio/final).
        """
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()

        from player import CLASSES
        cls_name = CLASSES[char_class]["name"]

        self.center_text(4, f"Clase elegida: {cls_name}", curses.A_BOLD)
        self.center_text(6, "Como te llamas, aventurero?")

        name = ""
        while True:
            self.stdscr.move(8, 0)
            self.stdscr.clrtoeol()
            prompt = f"  > {name}_"
            self.center_text(8, prompt, curses.A_BOLD)
            self.center_text(12, "ENTER: confirmar  |  Q/ESC: salir", curses.A_DIM)
            self.stdscr.refresh()

            key = self.stdscr.getch()
            if key in (ord("q"), ord("Q"), 27):
                import sys
                sys.exit(0)
            if key in (10, 13, curses.KEY_ENTER):
                if name.strip():
                    return name.strip()
            elif key in (curses.KEY_BACKSPACE, 127, 8):
                name = name[:-1]
            elif 32 <= key <= 126 and len(name) < 20:
                name += chr(key)

    # --- Mapa de exploracion ---

    def draw_map(self, game_map, player):
        """Dibuja el mapa completo con visibilidad limitada (radio 5).

        Muestra el terreno, enemigos, recompensas, el jugador y una barra
        de estado inferior con HP, nivel, oro, pociones y XP.

        Args:
            game_map: Instancia de GameMap.
            player: Instancia de Player.
        """
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()

        # Centra el mapa en la terminal.
        offset_y = max(0, (h - game_map.height - 3) // 2)
        offset_x = max(0, (w - game_map.width) // 2)

        # Calcula las casillas visibles alrededor del jugador (radio 5).
        visible = set()
        for dy in range(-5, 6):
            for dx in range(-5, 6):
                vx, vy = player.x + dx, player.y + dy
                if 0 <= vx < game_map.width and 0 <= vy < game_map.height:
                    visible.add((vx, vy))

        for y in range(game_map.height):
            for x in range(game_map.width):
                cx = offset_x + x
                cy = offset_y + y

                # Casillas fuera del radio de vision se ocultan (solo muros oscuros).
                if (x, y) not in visible:
                    if game_map.grid[y][x] == WALL:
                        self._safe_addch(cy, cx, " ", curses.A_DIM)
                    continue

                # Dibuja el jugador.
                if player.x == x and player.y == y:
                    self._safe_addch(cy, cx, player.symbol,
                                     curses.color_pair(player.color) | curses.A_BOLD)
                    continue

                # Dibuja enemigos.
                enemy = game_map.get_enemy_at(x, y)
                if enemy:
                    self._safe_addch(cy, cx, enemy.symbol,
                                     curses.color_pair(1) | curses.A_BOLD)
                    continue

                # Dibuja recompensas.
                reward = game_map.get_reward_at(x, y)
                if reward:
                    self._safe_addch(cy, cx, reward.symbol,
                                     curses.color_pair(reward.color) | curses.A_BOLD)
                    continue

                # Dibuja terreno (muro o suelo).
                cell = game_map.grid[y][x]
                if cell == WALL:
                    self._safe_addch(cy, cx, "#", curses.color_pair(7))
                else:
                    self._safe_addch(cy, cx, ".", curses.A_DIM)

        # --- Barra de estado inferior ---
        bar_y = offset_y + game_map.height + 1
        hp_str = f"HP: {player.hp}/{player.max_hp}"
        lvl_str = f"Nivel: {player.level}/10"  # 10 = jubilacion.
        gold_str = f"Oro: {player.gold}"
        pot_str = f"Pociones: {player.potions}"
        xp_str = f"XP: {player.xp}/{player.xp_to_level}"
        name_str = f"{player.name} ({player.class_name})"
        status = f"{name_str} | {hp_str} | {lvl_str} | {gold_str} | {pot_str} | {xp_str}"

        self.stdscr.move(bar_y, 0)
        self.stdscr.clrtoeol()
        self._safe_addstr(bar_y, max(0, (w - len(status)) // 2), status,
                          curses.A_BOLD)

        self._safe_addstr(bar_y + 1, 2,
                          "Flechas/WASD: mover | Q/ESC: salir",
                          curses.A_DIM)

        self.stdscr.refresh()

    # --- Combate (UI auxiliar, el render principal esta en combat_engine.py) ---

    def draw_combat(self, player, enemy, log_msg="", show_menu=True):
        """Dibuja una pantalla de combate basica (fallback).

        Args:
            player: Instancia de Player.
            enemy: Instancia de Enemy.
            log_msg: Mensaje a mostrar en la zona de log.
            show_menu: Si es True, dibuja el menu de acciones.
        """
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()

        self.center_text(1, "=== COMBATE ===", curses.A_BOLD | curses.color_pair(8))

        self.draw_bar(3, w // 4, player.name.upper(), player.hp, player.max_hp,
                      player.color, 30)
        self.draw_bar(5, w // 4, enemy.name.upper(), enemy.hp, enemy.max_hp,
                      1, 30)

        self.center_text(4, f"  {player.symbol}  VS  {enemy.symbol}  ",
                         curses.A_BOLD)

        if log_msg:
            self.stdscr.move(8, 0)
            self.stdscr.clrtoeol()
            self.center_text(8, log_msg, curses.A_BOLD)

        if show_menu:
            menu = ["[A] Atacar", "[D] Defender", "[P] Pocion", "[H] Huir"]
            menu_str = "  |  ".join(menu)
            self._safe_addstr(h - 2, max(0, (w - len(menu_str)) // 2), menu_str,
                              curses.A_BOLD)

        self.stdscr.refresh()

    def draw_bar(self, y, x, label, value, max_val, color, length=25):
        """Dibuja una barra de progreso con texto.

        Args:
            y, x: Posicion en pantalla.
            label: Texto previo a la barra (ej. "JUGADOR ").
            value: Valor actual.
            max_val: Valor maximo.
            color: Par de color de curses.
            length: Longitud de la barra en caracteres.
        """
        ratio = max(0, min(1, value / max_val if max_val > 0 else 0))
        filled = int(length * ratio)

        bar = "[" + "#" * filled + "-" * (length - filled) + "]"
        line = f"{label} {bar} {value}/{max_val}"
        try:
            self.stdscr.addstr(y, x, line, curses.color_pair(color) | curses.A_BOLD)
        except curses.error:
            pass

    # --- Pantallas de transicion ---

    def combat_result(self, player, enemy, won):
        """Muestra el resultado de un combate (victoria o derrota).

        Args:
            player: Instancia de Player.
            enemy: Instancia de Enemy.
            won: True si gano el jugador, False si perdio.
        """
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()

        if won:
            self.center_text(5, f"VICTORIA! Has derrotado a {enemy.name}!",
                             curses.color_pair(3) | curses.A_BOLD)
            self.center_text(7, f"+{enemy.gold_reward} oro  +{enemy.xp_reward} XP",
                             curses.color_pair(4))
        else:
            self.center_text(5, "HAS SIDO DERROTADO...",
                             curses.color_pair(1) | curses.A_BOLD)
            self.center_text(7, "Game Over", curses.A_DIM)

        self.center_text(10, "Presiona cualquier tecla...", curses.A_DIM)
        self.stdscr.refresh()
        self.stdscr.getch()

    def zone_cleared(self, player):
        """Pantalla de transicion al limpiar una zona de enemigos.

        Genera un nuevo mapa automaticamente para mantener el progreso
        hacia la jubilacion.

        Args:
            player: Instancia de Player.
        """
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()

        self.center_text(4, "=== ZONA LIMPIADA ===",
                         curses.A_BOLD | curses.color_pair(4))
        self.center_text(6, f"Has eliminado a todos los politicos de esta zona.",
                         curses.A_BOLD)
        self.center_text(8, f"Nivel: {player.level} | Oro: {player.gold} | "
                         f"Pociones: {player.potions}",
                         curses.A_DIM)
        self.center_text(10, "Generando nueva zona de combate...",
                         curses.color_pair(3) | curses.A_BOLD)
        self.center_text(12, "Presiona cualquier tecla para continuar...",
                         curses.A_DIM)

        self.stdscr.refresh()
        self.stdscr.getch()

    def reward_found(self, reward):
        """Pantalla de pop-up al recoger una recompensa.

        Args:
            reward: Instancia de Reward recien recogida.
        """
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()

        if reward.rtype == "gold":
            msg = f"Has encontrado {reward.amount} monedas de oro!"
            color = curses.color_pair(4)
        elif reward.rtype == "potion":
            msg = "Has encontrado una pocion de curacion!"
            color = curses.color_pair(6)
        else:
            msg = f"Has encontrado una fuente de salud! +{reward.amount} HP"
            color = curses.color_pair(3)

        self.center_text(5, "HAS ENCONTRADO ALGO!", curses.A_BOLD | curses.color_pair(4))
        self.center_text(7, msg, color | curses.A_BOLD)
        self.center_text(10, "Presiona cualquier tecla...", curses.A_DIM)
        self.stdscr.refresh()
        self.stdscr.getch()

    def level_up(self, player):
        """Pantalla de celebracion al subir de nivel.

        Args:
            player: Instancia de Player.
        """
        self.stdscr.clear()
        self.center_text(6, f"SUBISTE DE NIVEL! Nivel {player.level}",
                         curses.color_pair(4) | curses.A_BOLD)
        self.center_text(8, f"Max HP: {player.max_hp}  Daño: {player.min_dmg}-{player.max_dmg}",
                         curses.A_BOLD)
        self.center_text(10, "Presiona cualquier tecla...", curses.A_DIM)
        self.stdscr.refresh()
        self.stdscr.getch()

    def game_over(self, player, enemies_left):
        """Pantalla de fin de partida (tanto si ganas como si pierdes).

        Args:
            player: Instancia de Player.
            enemies_left: Numero de enemigos que quedaban en el mapa.
        """
        self.stdscr.clear()
        self.center_text(5, "=== JUEGO TERMINADO ===", curses.A_BOLD)
        stats = (
            f"Nivel: {player.level} | Oro: {player.gold} | "
            f"Enemigos vivos: {enemies_left}"
        )
        self.center_text(7, stats)
        self.center_text(10, "Presiona cualquier tecla para salir...", curses.A_DIM)
        self.stdscr.refresh()
        self.stdscr.getch()

    def retirement_screen(self, player):
        """Pantalla de victoria definitiva: has conseguido la jubilacion.

        Aparece automaticamente al alcanzar el nivel 10 tras ganar un combate.

        Args:
            player: Instancia de Player.
        """
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()

        box_w = 50
        box_x = max(0, (w - box_w) // 2)
        box_y = max(2, (h - 12) // 2)

        border = "+" + "=" * (box_w - 2) + "+"
        self.stdscr.addstr(box_y, box_x, border, curses.A_BOLD | curses.color_pair(4))
        for i in range(1, 8):
            self.stdscr.addstr(box_y + i, box_x, "|" + " " * (box_w - 2) + "|",
                               curses.A_BOLD | curses.color_pair(4))
        self.stdscr.addstr(box_y + 8, box_x, border, curses.A_BOLD | curses.color_pair(4))

        self.center_text(box_y + 2, "|    ENHORABUENA! HAS CONSEGUIDO     |",
                         curses.A_BOLD | curses.color_pair(3))
        self.center_text(box_y + 3, "|                                    |",
                         curses.A_BOLD | curses.color_pair(4))
        self.center_text(box_y + 4, "|         LA   JUBILACION            |",
                         curses.A_BOLD | curses.color_pair(4))
        self.center_text(box_y + 5, "|                                    |",
                         curses.A_BOLD | curses.color_pair(4))
        self.center_text(box_y + 6,
                         f"|  {player.name} - Nivel {player.level} - {player.gold} oro  |",
                         curses.A_DIM)

        self.center_text(box_y + 10,
                         "Tras anos de lucha... por fin puedes descansar.",
                         curses.A_DIM)
        self.center_text(box_y + 12, "Presiona cualquier tecla para salir...",
                         curses.A_DIM)

        self.stdscr.refresh()
        self.stdscr.getch()

    # --- Efectos visuales ---

    def typewriter(self, y, x, text, delay=0.02):
        """Escribe texto caractar a caracter con efecto maquina de escribir.

        Args:
            y, x: Posicion inicial.
            text: Texto completo a escribir.
            delay: Pausa entre caracteres (segundos).
        """
        for i, char in enumerate(text):
            try:
                self.stdscr.addstr(y, x + i, char)
            except curses.error:
                pass
            self.stdscr.refresh()
            time.sleep(delay)

    def shake(self, duration=0.15):
        """Simula un temblor de pantalla (util en impactos de combate).

        Args:
            duration: Duracion aproximada del efecto en segundos.
        """
        for _ in range(int(duration * 20)):
            self.stdscr.clear()
            self.stdscr.refresh()
            time.sleep(0.008)

    # --- Helpers seguros ---

    def _safe_addch(self, y, x, char, attr=0):
        """Wrapper de addch que ignora errores si el terminal es pequeno."""
        try:
            self.stdscr.addch(y, x, char, attr)
        except curses.error:
            pass

    def _safe_addstr(self, y, x, text, attr=0):
        """Wrapper de addstr que ignora errores si el terminal es pequeno."""
        try:
            self.stdscr.addstr(y, x, text, attr)
        except curses.error:
            pass
