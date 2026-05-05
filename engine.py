#!/usr/bin/env python3
"""
engine.py

Motor principal del juego. Gestiona el bucle de exploracion sobre el mapa,
intercepta las pulsaciones del teclado y deriva hacia el sistema de combate
cuando el jugador se encuentra con un enemigo, o hacia la recoleccion de
recompensas.
"""

import curses
from combat_engine import CombatEngine
from map import GameMap


class Engine:
    """Bucle de juego: exploracion, encuentros y transiciones."""

    def __init__(self, stdscr, ui, player, game_map):
        """Inicializa el motor con las dependencias necesarias.

        Args:
            stdscr: Ventana de curses para lectura de teclado.
            ui: Instancia de UI encargada de todo el dibujado.
            player: Instancia de Player con el estado del avatar.
            game_map: Instancia de GameMap con enemigos y recompensas.
        """
        self.stdscr = stdscr
        self.ui = ui
        self.player = player
        self.map = game_map
        self.running = True

    def run(self):
        """Bucle principal de exploracion.

        Dibuja el mapa, lee input de teclado, mueve al jugador, detecta
        colisiones con enemigos o recompensas y deriva al motor de combate.
        """
        while self.running and self.player.is_alive():
            self.ui.draw_map(self.map, self.player)

            key = self.stdscr.getch()

            # Salir del juego: Q, q o ESC (codigo 27).
            if key == ord("q") or key == ord("Q") or key == 27:
                self.running = False
                break

            # --- Movimiento (flechas o WASD) ---
            dx, dy = 0, 0
            if key in (curses.KEY_UP, ord("w"), ord("W")):
                dy = -1
            elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
                dy = 1
            elif key in (curses.KEY_LEFT, ord("a"), ord("A")):
                dx = -1
            elif key in (curses.KEY_RIGHT, ord("d"), ord("D")):
                dx = 1

            if dx == 0 and dy == 0:
                continue  # Tecla no reconocida para movimiento.

            old_x, old_y = self.player.x, self.player.y

            if not self.player.move(dx, dy, self.map):
                continue  # Movimiento bloqueado por muro o borde.

            # --- Encuentro con enemigo ---
            enemy = self.map.get_enemy_at(self.player.x, self.player.y)
            if enemy:
                combat = CombatEngine(self.stdscr, self.player, enemy)
                result = combat.run()

                if result == "won":
                    self.map.remove_enemy(enemy)
                    # Victoria final: alcanzar nivel 10 = jubilacion.
                    if self.player.level >= 10:
                        self.ui.retirement_screen(self.player)
                        self.running = False
                        break
                    # Si no quedan enemigos, generar una nueva zona.
                    if len(self.map.enemies) == 0:
                        self.ui.zone_cleared(self.player)
                        self.map = GameMap()
                        self.player.x = 2
                        self.player.y = 2
                elif result == "fled":
                    # El jugador huyo: vuelve a la casilla anterior.
                    self.player.x = old_x
                    self.player.y = old_y
                elif result == "lost":
                    self.running = False
                continue

            # --- Recoleccion de recompensa ---
            reward = self.map.get_reward_at(self.player.x, self.player.y)
            if reward:
                if reward.rtype == "gold":
                    self.player.gold += reward.amount
                elif reward.rtype == "potion":
                    self.player.potions += reward.amount
                elif reward.rtype == "health":
                    self.player.heal(reward.amount)

                self.map.remove_reward(reward)
                self.ui.reward_found(reward)

        # --- Pantalla final ---
        if not self.player.is_alive():
            self.ui.game_over(self.player, len(self.map.enemies))
        else:
            self.ui.game_over(self.player, len(self.map.enemies))
