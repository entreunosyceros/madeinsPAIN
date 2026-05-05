#!/usr/bin/env python3
"""
main.py

Punto de entrada del juego **madeinsPAIN**.

Inicializa curses, crea las instancias de UI, jugador, mapa y motor, y
lanza el flujo principal:
    1. Pantalla de titulo
    2. Seleccion de clase
    3. Introduccion del nombre
    4. Bucle de exploracion y combate
"""

import curses
from ui import UI
from player import Player, CLASSES
from map import GameMap
from engine import Engine


def main(stdscr):
    """Orquesta todo el flujo del juego.

    Args:
        stdscr: Ventana principal de curses proporcionada por
                `curses.wrapper()`.
    """
    # Oculta el cursor de la terminal para que no parpadee en el mapa.
    curses.curs_set(0)
    # Bloquea esperando entrada (modo sincrono).
    stdscr.nodelay(0)

    ui = UI(stdscr)

    # --- Flujo de inicio ---
    ui.title_screen()

    char_class = ui.select_class()

    name = ui.input_name(char_class)

    # --- Creacion de entidades ---
    player = Player(name=name, char_class=char_class)
    game_map = GameMap()

    # --- Bucle principal ---
    engine = Engine(stdscr, ui, player, game_map)
    engine.run()


if __name__ == "__main__":
    curses.wrapper(main)
