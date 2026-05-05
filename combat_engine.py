#!/usr/bin/env python3
"""
combat_engine.py

Motor de combate por turnos con animaciones visuales.

Gestiona el bucle de combate (jugador vs enemigo), calcula danios,
aplica estados de defensa y dibuja una interfaz tipo Street Fighter con
barras de vida laterales, flechas de ataque y flash de impacto.

El sistema de layout es adaptativo: si el terminal es suficientemente ancho
(>90 cols) muestra las barras lado a lado; si no, las apila verticalmente.
"""

import curses
import time
import random
from combat_ui import CombatUI


class CombatEngine:
    """Bucle de combate interactivo con animaciones."""

    def __init__(self, stdscr, player, enemy):
        """Prepara el combate con las dos entidades enfrentadas.

        Args:
            stdscr: Ventana de curses.
            player: Instancia de Player (protagonista).
            enemy: Instancia de Enemy (politico).
        """
        self.stdscr = stdscr
        self.ui = CombatUI(stdscr)
        self.player = player
        self.enemy = enemy
        self.defending = False  # True si el jugador eligio Defender este turno.
        self._layout_cache = None  # Cache para no recalcular geometria cada frame.

    # --- Acciones de combate ---

    def player_attack(self):
        """El jugador ataca al enemigo.

        Returns:
            int: Danio infligido.
        """
        dmg = self.player.attack_damage()
        self.enemy.hp = max(0, self.enemy.hp - dmg)
        return dmg

    def enemy_attack(self):
        """El enemigo ataca al jugador (teniendo en cuenta defensa y esquiva).

        Returns:
            int: Danio realmente recibido (0 si esquiva).
        """
        dmg = self.enemy.attack_damage()
        if self.defending:
            dmg = max(0, dmg // 2)
            self.defending = False
        taken = self.player.take_damage(dmg)
        return taken

    # --- Layout adaptativo ---

    def _get_layout(self):
        """Calcula la geometria de la pantalla de combate.

        Devuelve una tupla con toda la informacion necesaria para dibujar
        las barras y simbolos en su sitio. El resultado se cachea para
        optimizar el rendimiento durante las animaciones.

        Returns:
            tuple: (side_by_side, bar_width, left_x, right_x, p_name, e_name,
                    psym_x, esym_x)
        """
        if self._layout_cache:
            return self._layout_cache
        h, w = self.stdscr.getmaxyx()
        bar_w = 14
        p_name = self.player.name[:9].upper()
        e_name = self.enemy.name[:9].upper()
        ph = f"{self.player.hp}/{self.player.max_hp}"
        eh = f"{self.enemy.hp}/{self.enemy.max_hp}"
        # Ancho total de cada barra incluyendo label, corchetes y numeros.
        p_total = len(p_name) + 1 + bar_w + 2 + 1 + len(ph)
        e_total = len(e_name) + 1 + bar_w + 2 + 1 + len(eh)
        # Decide si hay espacio para modo lado a lado.
        side = w >= p_total + e_total + 6
        if side:
            left_x = 4
            right_x = w - e_total - 4
        else:
            left_x = 4
            right_x = 4
        psym_x = left_x + bar_w // 2
        esym_x = right_x + bar_w // 2
        self._layout_cache = (side, bar_w, left_x, right_x, p_name, e_name,
                              psym_x, esym_x)
        return self._layout_cache

    # --- Renderizado base ---

    def _draw_base(self, msg="", flash_player=False, flash_enemy=False,
                   arrow_len=0, arrow_dir="right"):
        """Dibuja una unica trama del combate.

        Es la funcion central de renderizado; se llama varias veces por
        segundo durante las animaciones para crear el efecto de movimiento.

        Args:
            msg: Mensaje informativo a mostrar bajo las barras.
            flash_player: Si True, invierte colores del simbolo jugador (impacto).
            flash_enemy: Si True, invierte colores del simbolo enemigo (impacto).
            arrow_len: Longitud actual de la flecha de ataque (0 = oculta).
            arrow_dir: "right" (jugador ataca) o "left" (enemigo ataca).
        """
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()
        (side, bar_w, left_x, right_x, p_name, e_name,
         psym_x, esym_x) = self._get_layout()

        # Titulo superior.
        title = "=== COMBATE ==="
        try:
            self.stdscr.addstr(0, max(0, (w - len(title)) // 2), title,
                               curses.A_BOLD | curses.color_pair(1))
        except curses.error:
            pass

        # Simbolos de los combatientes con efecto de flash (A_REVERSE).
        p_attr = (curses.color_pair(self.player.color) | curses.A_BOLD
                  | (curses.A_REVERSE if flash_player else 0))
        e_attr = (curses.color_pair(1) | curses.A_BOLD
                  | (curses.A_REVERSE if flash_enemy else 0))

        try:
            self.stdscr.addstr(1, psym_x, self.player.symbol, p_attr)
            self.stdscr.addstr(1, esym_x, self.enemy.symbol, e_attr)
        except curses.error:
            pass

        # Flecha de ataque animada entre los simbolos (solo en modo lado a lado).
        if side and arrow_len > 0:
            mid_start = psym_x + 2
            mid_end = esym_x - 1
            space = mid_end - mid_start
            if space > 0:
                drawn = min(arrow_len, space)
                chars = ">" * drawn if arrow_dir == "right" else "<" * drawn
                offset = 0 if arrow_dir == "right" else space - drawn
                try:
                    self.stdscr.addstr(1, mid_start + offset, chars,
                                       curses.A_BOLD | curses.color_pair(4))
                except curses.error:
                    pass

        # Barras de vida: lado a lado o apiladas segun el ancho del terminal.
        if side:
            self.ui.draw_bar(2, left_x, p_name + " ",
                             self.player.hp, self.player.max_hp, bar_w,
                             self.player.color)
            self.ui.draw_bar(2, right_x,
                             e_name + " ",
                             self.enemy.hp, self.enemy.max_hp, bar_w, 1)
            vs_x = (psym_x + esym_x) // 2
            try:
                self.stdscr.addstr(2, vs_x - 1, "VS",
                                   curses.A_BOLD | curses.color_pair(4))
            except curses.error:
                pass
        else:
            self.ui.draw_bar(2, left_x, p_name + " ",
                             self.player.hp, self.player.max_hp, 20,
                             self.player.color)
            try:
                self.stdscr.addstr(3, 40,
                                   f" {self.player.symbol}  VS  {self.enemy.symbol} ",
                                   curses.A_BOLD)
            except curses.error:
                pass
            self.ui.draw_bar(4, left_x,
                             e_name + " ",
                             self.enemy.hp, self.enemy.max_hp, 20, 1)

        # Mensaje de estado (ej. "Has huido del combate!").
        if msg:
            try:
                row = 4 if side else 6
                self.stdscr.addstr(row, max(0, (w - len(msg)) // 2),
                                   msg, curses.A_BOLD)
            except curses.error:
                pass

        # Menu de acciones y estadisticas inferiores.
        menu = " [A] Atacar  [D] Defender  [P] Pocion  [H] Huir "
        extra = (f"Pociones: {self.player.potions}  |  "
                 f"Oro: {self.player.gold}  |  "
                 f"Nivel: {self.player.level}")
        try:
            self.stdscr.addstr(h - 3, max(0, (w - len(menu)) // 2), menu,
                               curses.A_BOLD)
            self.stdscr.addstr(h - 2, max(0, (w - len(extra)) // 2), extra)
        except curses.error:
            pass

        self.stdscr.refresh()

    # --- Animacion de ataque ---

    def _animate_attack(self, is_player, dmg):
        """Reproduce la animacion visual de un ataque.

        En modo lado a lado: flecha que crece desde el atacante hacia el
        defensor + parpadeo invertido en el receptor. En modo estrecho:
        shake de pantalla simple.

        Args:
            is_player: True si ataca el jugador, False si ataca el enemigo.
            dmg: Cantidad de danio infligido (para mostrarlo en el mensaje).
        """
        (side, bar_w, left_x, right_x, p_name, e_name,
         psym_x, esym_x) = self._get_layout()

        # Terminal estrecha: solo shake basico.
        if not side:
            self._draw_base()
            time.sleep(0.15)
            self.stdscr.clear()
            self.stdscr.refresh()
            time.sleep(0.05)
            self._draw_base()
            time.sleep(0.15)
            return

        attacker = self.player.name if is_player else self.enemy.name
        defender = self.enemy.name if is_player else self.player.name
        arrow_dir = "right" if is_player else "left"

        # 1. Fase de carga: la flecha crece en 4 pasos.
        space = esym_x - psym_x - 2
        steps = 4
        for step in range(steps):
            arrow_len = int(space * (step + 1) / steps)
            # Parpadeo alterno para dar sensacion de tension.
            flash_p = not is_player and step % 2 == 1
            flash_e = is_player and step % 2 == 1
            self._draw_base(
                msg=f"{attacker} ataca...",
                flash_player=flash_p,
                flash_enemy=flash_e,
                arrow_len=arrow_len,
                arrow_dir=arrow_dir
            )
            time.sleep(0.10)

        # 2. Fase de impacto: flash fuerte + shake rapido.
        for _ in range(2):
            self._draw_base(
                msg=f"IMPACTO! {defender} recibe {dmg} de dano!",
                flash_player=not is_player,
                flash_enemy=is_player,
                arrow_len=space,
                arrow_dir=arrow_dir
            )
            time.sleep(0.10)
            self.stdscr.clear()
            self.stdscr.refresh()
            time.sleep(0.06)

        # 3. Frame final con el mensaje de danio.
        self._draw_base(
            msg=f"{defender} recibe {dmg} de dano!",
            flash_player=not is_player,
            flash_enemy=is_player,
            arrow_len=space,
            arrow_dir=arrow_dir
        )
        time.sleep(0.35)

    # --- Bucle principal del combate ---

    def render(self, msg=""):
        """Dibuja un frame estatico del combate (sin animacion).

        Args:
            msg: Texto opcional a mostrar bajo las barras.
        """
        self._draw_base(msg=msg)

    def run(self):
        """Bucle de combate por turnos.

        Turno par  (0, 2, 4...): jugador elige accion.
        Turno impar(1, 3, 5...): enemigo ataca automaticamente.

        Returns:
            str: Resultado del combate: "won", "lost" o "fled".
        """
        turn = 0

        while self.player.is_alive() and self.enemy.is_alive():
            self.render()

            # --- Turno del jugador ---
            if turn % 2 == 0:
                self.render("Tu turno! Elige una accion...")

                while True:
                    key = self.stdscr.getch()
                    key = key if key < 256 else chr(key).lower() if 32 <= key < 256 else key

                    if key in (ord("a"), ord("A")):
                        dmg = self.player_attack()
                        self._animate_attack(True, dmg)
                        break

                    elif key in (ord("d"), ord("D")):
                        self.defending = True
                        self.render("Te pones en guardia! Defensa x2 este turno.")
                        time.sleep(0.4)
                        break

                    elif key in (ord("p"), ord("P")):
                        if self.player.potions > 0:
                            self.player.potions -= 1
                            healed = self.player.heal()
                            msg = f"Usas una pocion! Recuperas {healed} HP."
                        else:
                            msg = "No tienes pociones!"
                            continue
                        self.render(msg)
                        time.sleep(0.5)
                        break

                    elif key in (ord("h"), ord("H")):
                        if random.random() < 0.5:
                            self.render("Has huido del combate!")
                            time.sleep(0.5)
                            return "fled"
                        else:
                            self.render("No puedes huir! El enemigo te bloquea.")
                            time.sleep(0.5)
                            continue

            # --- Turno del enemigo ---
            else:
                dmg = self.enemy_attack()
                if dmg == 0:
                    msg = (f"{self.enemy.name} ataca pero "
                           f"ESQUIVAS el golpe!")
                    self.render(msg)
                    time.sleep(0.5)
                elif self.defending:
                    msg = (f"{self.enemy.name} ataca pero "
                           f"te DEFIENDES! Solo recibes {dmg} de dano.")
                    self._animate_attack(False, dmg)
                else:
                    msg = (f"{self.enemy.name} ataca y "
                           f"te hace {dmg} de dano!")
                    self._animate_attack(False, dmg)

            turn += 1

        # --- Resolucion del combate ---
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()

        if self.player.is_alive():
            # Victoria: suma recompensas y comprueba subida de nivel.
            gold = self.enemy.gold_reward
            xp = self.enemy.xp_reward
            self.player.gold += gold
            leveled = self.player.add_xp(xp)
            try:
                self.stdscr.addstr(5, max(0, (w - 40) // 2),
                                   f" VICTORIA! Has derrotado a {self.enemy.name}! ",
                                   curses.A_BOLD)
                self.stdscr.addstr(7, max(0, (w - 40) // 2),
                                   f"   +{gold} oro    +{xp} XP   ",
                                   curses.A_BOLD)
                if leveled:
                    self.stdscr.addstr(9, max(0, (w - 40) // 2),
                                       f"   SUBISTE DE NIVEL! Nivel {self.player.level}   ",
                                       curses.A_BOLD)
                self.stdscr.addstr(11, max(0, (w - 40) // 2),
                                   "   Presiona cualquier tecla...   ")
            except curses.error:
                pass
            self.stdscr.refresh()
            self.stdscr.getch()
            return "won"
        else:
            # Derrota.
            try:
                self.stdscr.addstr(5, max(0, (w - 40) // 2),
                                   " HAS SIDO DERROTADO... ",
                                   curses.A_BOLD)
                self.stdscr.addstr(7, max(0, (w - 40) // 2),
                                   "        GAME OVER        ",
                                   curses.A_BOLD)
                self.stdscr.addstr(9, max(0, (w - 40) // 2),
                                   " Presiona cualquier tecla ")
            except curses.error:
                pass
            self.stdscr.refresh()
            self.stdscr.getch()
            return "lost"
