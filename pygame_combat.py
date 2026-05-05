#!/usr/bin/env python3
"""
pygame_combat.py

Motor de combate interactivo con Pygame.

Gestiona el bucle de combate por turnos, animaciones de ataque
(flecha, flash, impacto), acciones del jugador (atacar, defender,
pocion, huir) y resolucion (victoria / derrota / huida).
"""

import pygame
import random
import time
from pygame_ui import PygameUI


# Estados internos del combate.
COMBAT_RUNNING   = "running"
COMBAT_WON       = "won"
COMBAT_LOST      = "lost"
COMBAT_FLED      = "fled"


class PygameCombat:
    """Motor de combate por turnos con interfaz grafica Pygame."""

    def __init__(self, screen, player, enemy, ui):
        """Inicializa el combate.

        Args:
            screen: Superficie de Pygame.
            player: Instancia de Player.
            enemy: Instancia de Enemy.
            ui: Instancia de PygameUI para dibujar.
        """
        self.screen = screen
        self.player = player
        self.enemy = enemy
        self.ui = ui
        self.clock = pygame.time.Clock()
        self.defending = False
        self.turn = 0  # 0 = turno del jugador, 1 = turno del enemigo.
        self.msg = ""
        self.msg_color = (255, 255, 255)
        self.state = COMBAT_RUNNING
        self.anim_arrow_dir = "none"
        self.anim_arrow_progress = 0.0
        self.anim_flash_player = False
        self.anim_flash_enemy = False
        self.anim_phase = "idle"  # "idle", "loading", "impact", "waiting"
        self.anim_timer = 0
        self.waiting_for_input = True  # Solo aplica al turno del jugador.
        self.wait_timer = 0
        self.pending_damage = 0  # Danio pendiente: se aplica al finalizar la animacion.

    def run(self):
        """Bucle principal del combate. Devuelve el resultado.

        Returns:
            str: "won", "lost" o "fled".
        """
        self.msg = "Tu turno! Elige una accion..."
        self.msg_color = (255, 255, 255)
        self.waiting_for_input = True

        while self.state == COMBAT_RUNNING:
            self.ui.tick()
            self._update_animation()

            # Dibuja la escena actual.
            self.ui.draw_combat(
                self.player, self.enemy,
                msg=self.msg,
                msg_color=self.msg_color,
                flash_player=self.anim_flash_player,
                flash_enemy=self.anim_flash_enemy,
                arrow_dir=self.anim_arrow_dir,
                arrow_progress=self.anim_arrow_progress,
            )
            pygame.display.flip()

            # Procesa entrada del jugador solo en su turno.
            if self.turn % 2 == 0 and self.anim_phase == "idle":
                self._handle_player_input()
            elif self.turn % 2 == 1 and self.anim_phase == "idle":
                self._enemy_turn()
            elif self.anim_phase != "idle":
                if self.anim_phase == "waiting":
                    self.wait_timer -= 1
                    if self.wait_timer <= 0:
                        self.anim_phase = "idle"
                        if self.player.is_alive() and self.enemy.is_alive():
                            self.turn += 1
                            if self.turn % 2 == 0:
                                self.msg = "Tu turno! Elige una accion..."
                                self.msg_color = (255, 255, 255)
                                self.waiting_for_input = True

            self.clock.tick(30)

        return self.state

    def _handle_player_input(self):
        """Procesa las teclas pulsadas durante el turno del jugador."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.state = "fled"
                return
            if event.type == pygame.KEYDOWN:
                key = event.key

                if key in (pygame.K_a,):
                    self._do_attack()
                elif key in (pygame.K_d,):
                    self._do_defend()
                elif key in (pygame.K_p,):
                    self._do_potion()
                elif key in (pygame.K_h,):
                    self._do_flee()
                elif key in (pygame.K_ESCAPE,):
                    self._do_flee()

    def _update_animation(self):
        """Avanza los temporizadores de animacion de ataque."""
        if self.anim_phase == "loading":
            # La flecha crece gradualmente.
            self.anim_arrow_progress = min(1.0, self.anim_arrow_progress + 0.06)
            if self.anim_arrow_progress >= 1.0:
                self.anim_phase = "impact"
                self.anim_timer = 6  # Frames de flash.

        elif self.anim_phase == "impact":
            # Parpadeo invertido en el receptor.
            if self.turn % 2 == 0:
                self.anim_flash_enemy = True
            else:
                self.anim_flash_player = True
            self.anim_timer -= 1
            if self.anim_timer <= 0:
                self.anim_flash_player = False
                self.anim_flash_enemy = False
                self.anim_phase = "idle"

                # Aplicar danio pendiente al terminar la animacion.
                if self.pending_damage > 0:
                    if self.turn % 2 == 0:
                        # Jugador ataca: aplicar danio al enemigo.
                        self.enemy.hp = max(0, self.enemy.hp - self.pending_damage)
                        self.msg = (f"IMPACTO! {self.enemy.name} "
                                    f"recibe {self.pending_damage} de dano!")
                    else:
                        # Enemigo ataca: aplicar danio al jugador
                        # (usa take_damage para respetar defensa).
                        actual = self.player.take_damage(self.pending_damage)
                        self.msg = (f"{self.enemy.name} ataca y "
                                    f"te hace {actual} de dano!")
                    self.msg_color = (255, 50, 50)
                self.pending_damage = 0

                # Comprueba si el combate termino tras el impacto.
                if not self.enemy.is_alive():
                    self._show_combat_won()
                    return
                elif not self.player.is_alive():
                    self._show_combat_lost()
                    return
                self.turn += 1
                if self.turn % 2 == 0:
                    self.msg = "Tu turno! Elige una accion..."
                    self.msg_color = (255, 255, 255)
                    self.waiting_for_input = True
                else:
                    self.waiting_for_input = False

    # --- Acciones del jugador ---

    def _do_attack(self):
        """El jugador ataca al enemigo (daño se aplica tras la animacion)."""
        self.pending_damage = self.player.attack_damage()
        self.msg = f"Atacas a {self.enemy.name}..."
        self.msg_color = (255, 50, 50)
        self.waiting_for_input = False
        self.anim_arrow_dir = "right"
        self.anim_arrow_progress = 0.0
        self.anim_phase = "loading"
        self.defending = False

    def _do_defend(self):
        """El jugador se pone en guardia (defensa x2)."""
        self.defending = True
        self.msg = "Te pones en guardia! Defensa x2 este turno."
        self.msg_color = (100, 200, 255)
        self.waiting_for_input = False
        self.anim_phase = "waiting"
        self.wait_timer = 25
        self.anim_arrow_dir = "none"

    def _do_potion(self):
        """El jugador usa una pocion de curacion."""
        if self.player.potions > 0:
            self.player.potions -= 1
            healed = self.player.heal()
            self.msg = f"Usas una pocion! Recuperas {healed} HP."
            self.msg_color = (0, 255, 200)
        else:
            self.msg = "No tienes pociones!"
            self.msg_color = (255, 100, 100)
            return  # No gastar turno.
        self.waiting_for_input = False
        self.anim_phase = "waiting"
        self.wait_timer = 30
        self.anim_arrow_dir = "none"

    def _do_flee(self):
        """El jugador intenta huir del combate (50% de exito)."""
        if random.random() < 0.5:
            self.msg = "Has huido del combate!"
            self.msg_color = (255, 255, 100)
            self.anim_arrow_dir = "none"
            # Dibuja un frame final.
            self.ui.draw_combat(self.player, self.enemy,
                                msg=self.msg, msg_color=self.msg_color)
            pygame.display.flip()
            pygame.time.wait(600)
            self.state = COMBAT_FLED
        else:
            self.msg = "No puedes huir! El enemigo te bloquea."
            self.msg_color = (255, 100, 100)
            self.waiting_for_input = False
            self.anim_phase = "waiting"
            self.wait_timer = 25
            self.anim_arrow_dir = "none"

    # --- Turno del enemigo ---

    def _enemy_turn(self):
        """El enemigo ataca al jugador (daño se aplica tras la animacion)."""
        dmg = self.enemy.attack_damage()
        if self.defending:
            dmg = max(0, dmg // 2)
            self.defending = False

        # Guardar el danio para aplicarlo al finalizar la animacion.
        self.pending_damage = dmg
        self._dodge_chance = random.random() < self.player.dodge

        if self._dodge_chance:
            self.msg = f"{self.enemy.name} ataca pero ESQUIVAS el golpe!"
            self.msg_color = (100, 255, 100)
            self.anim_arrow_dir = "none"
            self.anim_phase = "waiting"
            self.wait_timer = 30
            self.waiting_for_input = False
            # Esquivar: no hay animacion, aplicar de inmediato (ya es 0).
            self.pending_damage = 0
        else:
            self.msg = f"{self.enemy.name} ataca..."
            self.msg_color = (255, 50, 50)
            self.anim_arrow_dir = "left"
            self.anim_arrow_progress = 0.0
            self.anim_phase = "loading"
            self.waiting_for_input = False

    # --- Fin del combate ---

    def _show_combat_won(self):
        """Muestra pantalla temporal de victoria y cambia el estado."""
        self.msg = f"VICTORIA! Has derrotado a {self.enemy.name}!"
        self.msg_color = (255, 215, 0)
        self.ui.draw_combat(self.player, self.enemy,
                            msg=self.msg, msg_color=self.msg_color)
        pygame.display.flip()
        pygame.time.wait(800)
        self.state = COMBAT_WON

    def _show_combat_lost(self):
        """Muestra pantalla temporal de derrota y cambia el estado."""
        self.msg = "Has sido derrotado..."
        self.msg_color = (255, 0, 0)
        self.anim_flash_player = True
        self.ui.draw_combat(self.player, self.enemy,
                            msg=self.msg, msg_color=self.msg_color,
                            flash_player=True)
        pygame.display.flip()
        pygame.time.wait(1000)
        self.state = COMBAT_LOST

    # --- Resultado ---

    def show_result(self):
        """Muestra la pantalla de resultado del combate.

        Returns:
            dict: {"gold", "xp", "leveled", "level"} si gano,
                  o None si perdio/huyo.
        """
        if self.state == COMBAT_WON:
            gold = self.enemy.gold_reward
            xp = self.enemy.xp_reward
            self.player.gold += gold
            leveled = self.player.add_xp(xp)
            return {"gold": gold, "xp": xp, "leveled": leveled,
                    "level": self.player.level}
        return None
