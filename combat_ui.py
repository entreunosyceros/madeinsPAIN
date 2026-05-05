#!/usr/bin/env python3
"""
combat_ui.py

Utilidades graficas especificas para las pantallas de combate.

Proporciona efectos visuales (typewriter, shake) y dibujado de barras de vida
que utiliza CombatEngine. Se mantiene en un modulo separado para desacoplar
la logica de combate de la presentacion.
"""

import curses
import time


class CombatUI:
    """Herramientas graficas para el motor de combate."""

    def __init__(self, stdscr):
        """
        Args:
            stdscr: Ventana principal de curses.
        """
        self.stdscr = stdscr

    def typewriter(self, y, x, text, delay=0.02):
        """Escribe texto caracter a caracter con efecto maquina de escribir.

        Args:
            y, x: Coordenadas iniciales.
            text: Texto completo.
            delay: Pausa entre cada caracter (segundos).
        """
        for i, char in enumerate(text):
            try:
                self.stdscr.addstr(y, x + i, char)
            except curses.error:
                pass
            self.stdscr.refresh()
            time.sleep(delay)

    def shake(self, intensity=2, duration=0.15):
        """Efecto de temblor de pantalla para impactos.

        Args:
            intensity: No utilizado actualmente (reservado para ampliaciones).
            duration: Duracion aproximada del efecto en segundos.
        """
        for _ in range(int(duration * 20)):
            self.stdscr.clear()
            self.stdscr.refresh()
            time.sleep(0.01)

    def draw_bar(self, y, x, label, value, max_value, length=20, color=0):
        """Dibuja una barra de HP con formato [####----] 45/100.

        Args:
            y, x: Posicion en pantalla.
            label: Texto descriptivo (ej. "JUGADOR ").
            value: Valor actual.
            max_value: Valor maximo.
            length: Numero de caracteres internos de la barra (sin corchetes).
            color: Par de color de curses (0 = sin color especial).
        """
        ratio = max(0, min(1, value / max_value if max_value > 0 else 0))
        filled = int(length * ratio)
        bar = "[" + "#" * filled + "-" * (length - filled) + "]"
        attr = curses.color_pair(color) if color else 0
        try:
            self.stdscr.addstr(y, x, f"{label}{bar} {value}/{max_value}", attr)
        except curses.error:
            pass
