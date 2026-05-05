#!/usr/bin/env python3
"""
pygame_game.py

Punto de entrada de la version grafica de madeinsPAIN (Pygame).

Orquesta la maquina de estados del juego:
    menu -> seleccion -> nombre -> exploracion <-> combate -> resultado

El juego se ejecuta con Pygame y reutiliza los modelos de datos
de player.py y map.py.
"""

import pygame
import sys
import os
from player import Player, CLASSES
from map import GameMap
from map import ENEMY_SCALE_PER_ABILITY
from pygame_ui import PygameUI, TILE_H, HUD_H, TILE_W
from pygame_combat import PygameCombat
from music import MusicPlayer

# Ruta del directorio del proyecto (para cargar assets).
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


# --- Estados del juego ---
STATE_MENU       = "menu"
STATE_SELECT     = "select"
STATE_TUTORIAL   = "tutorial"
STATE_NAME       = "name"
STATE_EXPLORING  = "exploring"
STATE_COMBAT     = "combat"
STATE_FIGHT_INTRO = "fight_intro"
STATE_REWARD     = "reward"
STATE_ZONE_CLEARED = "zone_cleared"
STATE_VICTORY    = "victory"       # Tras ganar un combate.
STATE_SHOP       = "shop"          # Tienda de leyes tras subir de nivel.
STATE_GAME_OVER  = "game_over"
STATE_RETIREMENT = "retirement"


class Game:
    """Controlador principal de la version grafica."""

    def __init__(self):
        pygame.init()
        # Pantalla: ancho fijo, alto calculado para que el mapa llene hasta el HUD.
        map_rows = 18
        screen_h = map_rows * TILE_H + HUD_H
        screen_w = 40 * TILE_W  # Ancho del mapa + margenes.
        self.screen = pygame.display.set_mode((screen_w, screen_h))
        pygame.display.set_caption("madeinsPAIN - RPG Terminal")
        self.clock = pygame.time.Clock()
        self.running = True

        self.state = STATE_MENU
        self.ui = PygameUI(self.screen)

        # Musica chiptune.
        self.music = MusicPlayer()
        self.music.play("menu")

        # Muestra el splash antes de empezar el juego.
        self.show_splash()

        # Entidades del juego (se inicializan tras la seleccion).
        self.player = None
        self.game_map = None
        self.player_moving = False

        # Datos temporales entre estados.
        self.selected_class = 0
        self.player_name = ""
        self.pending_reward = None
        self.combat = None

        # Estado de la tienda.
        self.shop_selected = 0

        # Estado del tutorial.
        self.tutorial_page = 0

        # Contenido de pantalla de victoria.
        self.victory_gold = 0
        self.victory_xp = 0
        self.victory_leveled = False
        self.combat_start_level = 1

    def show_splash(self):
        """Muestra la pantalla de splash con img/logo.png durante 4 segundos.

        Si la imagen no existe, muestra el texto "madeinsPAIN" centrado
        con un fondo de color.
        """
        logo_path = os.path.join(PROJECT_DIR, "img", "logo.png")
        w, h = self.screen.get_width(), self.screen.get_height()
        clock = pygame.time.Clock()
        # Carga la imagen si existe.
        logo = None
        if os.path.isfile(logo_path):
            try:
                logo = pygame.image.load(logo_path).convert_alpha()
                # Escala proporcional al 60% de la pantalla.
                max_w = int(w * 0.7)
                max_h = int(h * 0.7)
                ratio = min(max_w / logo.get_width(), max_h / logo.get_height())
                new_w = int(logo.get_width() * ratio)
                new_h = int(logo.get_height() * ratio)
                logo = pygame.transform.smoothscale(logo, (new_w, new_h))
            except Exception:
                logo = None

        # Fondo oscuro.
        self.screen.fill((10, 10, 30))

        if logo:
            logo_x = (w - logo.get_width()) // 2
            logo_y = (h - logo.get_height()) // 2
            self.screen.blit(logo, (logo_x, logo_y))
        else:
            # Texto de respaldo si no hay imagen.
            font = pygame.font.SysFont("monospace", 48, bold=True)
            text = font.render("madeinsPAIN", True, (255, 215, 0))
            self.screen.blit(text, ((w - text.get_width()) // 2,
                                    (h - text.get_height()) // 2))

        # Barra de carga.
        bar_w = int(w * 0.4)
        bar_h = 8
        bar_x = (w - bar_w) // 2
        bar_y = h - 40

        pygame.display.flip()

        # Animacion de 4 segundos con fade-in y barra de progreso.
        duration = 4000  # milisegundos.
        elapsed = 0

        while elapsed < duration:
            dt = clock.tick(60)
            elapsed += dt

            # Procesa eventos para que la ventana no se congele.
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_RETURN:
                        # ENTER salta el splash inmediatamente.
                        elapsed = duration

            # Barra de progreso.
            progress = min(1.0, elapsed / duration)
            self.screen.fill((10, 10, 30), (0, bar_y - 5, w, 30))
            pygame.draw.rect(self.screen, (40, 40, 60),
                             (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(self.screen, (0, 180, 0),
                             (bar_x, bar_y, int(bar_w * progress), bar_h))

            if logo:
                self.screen.blit(logo, (logo_x, logo_y))
            else:
                text = font.render("madeinsPAIN", True, (255, 215, 0))
                self.screen.blit(text, ((w - text.get_width()) // 2,
                                        (h - text.get_height()) // 2))

            pygame.display.flip()

    def run(self):
        """Bucle principal del juego."""
        while self.running:
            self.ui.tick()

            # Recolectar eventos una sola vez y procesarlos globalmente.
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        self.music.toggle()

            if not self.running:
                break

            if self.state == STATE_MENU:
                self._loop_menu(events)
            elif self.state == STATE_SELECT:
                self._loop_select(events)
            elif self.state == STATE_TUTORIAL:
                self._loop_tutorial(events)
            elif self.state == STATE_NAME:
                self._loop_name(events)
            elif self.state == STATE_EXPLORING:
                self._loop_exploring(events)
            elif self.state == STATE_COMBAT:
                self._loop_combat()
            elif self.state == STATE_FIGHT_INTRO:
                self._loop_fight_intro(events)
            elif self.state == STATE_REWARD:
                self._loop_reward(events)
            elif self.state == STATE_VICTORY:
                self._loop_victory(events)
            elif self.state == STATE_SHOP:
                self._loop_shop(events)
            elif self.state == STATE_ZONE_CLEARED:
                self._loop_zone_cleared(events)
            elif self.state == STATE_GAME_OVER:
                self._loop_game_over(events)
            elif self.state == STATE_RETIREMENT:
                self._loop_retirement(events)

            pygame.display.flip()
            self.clock.tick(30)

        pygame.quit()
        sys.exit()

    # --- MENU ---

    def _loop_menu(self, events):
        """Pantalla de titulo. ENTER avanza, ESC cierra."""
        self.ui.draw_title()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.state = STATE_SELECT
                elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.running = False

    # --- SELECCION DE CLASE ---

    def _loop_select(self, events):
        """Menu de clase. Flechas para elegir, ENTER confirmar."""
        self.ui.draw_select_class(self.selected_class)
        class_keys = list(CLASSES.keys())

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_class = max(0, self.selected_class - 1)
                elif event.key == pygame.K_DOWN:
                    self.selected_class = min(len(class_keys) - 1,
                                              self.selected_class + 1)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.tutorial_page = 0
                    self.state = STATE_TUTORIAL
                elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.running = False

    # --- TUTORIAL ---

    def _loop_tutorial(self, events):
        """Pantalla de tutorial/instrucciones entre seleccion y nombre."""
        self.ui.draw_tutorial(self.tutorial_page)

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if self.tutorial_page < 3:
                        self.tutorial_page += 1
                    else:
                        self.player_name = ""
                        self.state = STATE_NAME
                elif event.key == pygame.K_RIGHT:
                    self.tutorial_page = min(3, self.tutorial_page + 1)
                elif event.key == pygame.K_LEFT:
                    self.tutorial_page = max(0, self.tutorial_page - 1)
                elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.running = False

    # --- NOMBRE ---

    def _loop_name(self, events):
        """Pantalla de entrada del nombre."""
        class_keys = list(CLASSES.keys())
        cls_name = CLASSES[class_keys[self.selected_class]]["name"]
        self.ui.draw_name_input(self.player_name, cls_name)

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if self.player_name.strip():
                        self._start_game(class_keys[self.selected_class],
                                         self.player_name.strip())
                elif event.key == pygame.K_BACKSPACE:
                    self.player_name = self.player_name[:-1]
                elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.running = False
                else:
                    # Teclas de texto (letras, espacios, numeros).
                    char = event.unicode
                    if char and char.isprintable() and len(self.player_name) < 16:
                        self.player_name += char

    def _start_game(self, char_class, name):
        """Crea el jugador y el mapa, y pasa a exploracion.

        Args:
            char_class: Clave de clase seleccionada.
            name: Nombre del jugador.
        """
        self.player = Player(name=name, char_class=char_class)
        self.game_map = GameMap()
        # Escala enemigos iniciales (0 habilidades = stats base).
        for e in self.game_map.enemies:
            e.scale(self.player.ability_count)
        self.state = STATE_EXPLORING

    # --- EXPLORACION ---

    def _loop_exploring(self, events):
        """Mapa principal: movimiento, encuentros, recompensas."""
        self.ui.draw_map(self.game_map, self.player)

        dx, dy = 0, 0
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.running = False
                    return
                dx, dy = self._key_to_dir(event.key)
            elif event.type == pygame.KEYUP:
                self.player_moving = False

        # Movimiento continuo con flechas mantenidas.
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1

        if dx != 0 or dy != 0:
            old_x, old_y = self.player.x, self.player.y
            if self.player.move(dx, dy, self.game_map):
                self._check_encounter(old_x, old_y)

    def _key_to_dir(self, key):
        """Convierte una tecla de movimiento en desplazamiento (dx, dy)."""
        if key in (pygame.K_UP, pygame.K_w):
            return 0, -1
        elif key in (pygame.K_DOWN, pygame.K_s):
            return 0, 1
        elif key in (pygame.K_LEFT, pygame.K_a):
            return -1, 0
        elif key in (pygame.K_RIGHT, pygame.K_d):
            return 1, 0
        return 0, 0

    def _check_encounter(self, old_x, old_y):
        """Tras moverse, comprueba si hay enemigo o recompensa.

        Args:
            old_x, old_y: Posicion anterior (para huir del combate).
        """
        px, py = self.player.x, self.player.y

        # Enemigo (comprueba posicion visual, no solo la original).
        enemy = self.game_map.get_enemy_at_visual(px, py)
        if enemy:
            self._start_combat(enemy, old_x, old_y)
            return

        # Recompensa.
        reward = self.game_map.get_reward_at(px, py)
        if reward:
            if reward.rtype == "gold":
                self.player.gold += reward.amount
            elif reward.rtype == "potion":
                self.player.potions += reward.amount
            elif reward.rtype == "health":
                self.player.heal(reward.amount)
            self.game_map.remove_reward(reward)
            self.pending_reward = reward
            self.state = STATE_REWARD

    # --- COMBATE ---

    def _start_combat(self, enemy, old_x, old_y):
        """Inicia un combate con un enemigo.

        Args:
            enemy: Instancia de Enemy encontrada.
            old_x, old_y: Posicion del jugador antes del encuentro.
        """
        self.combat_start_level = self.player.level
        self.combat = PygameCombat(self.screen, self.player, enemy, self.ui)
        self.combat_old_x = old_x
        self.combat_old_y = old_y
        self.combat_enemy = enemy
        self.music.play("combat")
        self.state = STATE_FIGHT_INTRO

    def _loop_fight_intro(self, events):
        """Pantalla de presentacion antes del combate."""
        self.ui.draw_fight_intro(self.player, self.combat_enemy, not self.music.muted)

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.state = STATE_COMBAT
                elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                    # Intentar huir (50% de exito).
                    import random
                    if random.random() < 0.5:
                        self.player.x = self.combat_old_x
                        self.player.y = self.combat_old_y
                        self.music.play("menu")
                        self.state = STATE_EXPLORING
                    else:
                        # No pudo huir, entrar en combate.
                        self.state = STATE_COMBAT

    def _loop_combat(self):
        """Bucle del motor de combate Pygame."""
        result = self.combat.run()

        if result == "won":
            self.game_map.remove_enemy(self.combat_enemy)

            # Comprueba victoria final.
            if self.player.level >= 10:
                self.music.stop()
                self.state = STATE_RETIREMENT
                return

            # Comprueba zona vacia.
            if len(self.game_map.enemies) == 0:
                self.music.play("menu")
                self.state = STATE_ZONE_CLEARED
                return

            # Muestra pantalla de victoria.
            self.victory_gold = self.combat.enemy.gold_reward
            self.victory_xp = self.combat.enemy.xp_reward
            self.victory_leveled = (self.player.level > self.combat_start_level)
            self.state = STATE_VICTORY

        elif result == "fled":
            # Vuelve a la posicion anterior.
            self.player.x = self.combat_old_x
            self.player.y = self.combat_old_y
            self.music.play("menu")
            self.state = STATE_EXPLORING

        elif result == "lost":
            self.music.stop()
            self.state = STATE_GAME_OVER

    def _loop_victory(self, events):
        """Pantalla de victoria tras ganar un combate."""
        self.ui.draw_victory(
            self.combat.enemy.name,
            self.victory_gold,
            self.victory_xp,
            self.victory_leveled,
            self.player.level,
        )

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    # Si subio de nivel, va a la tienda de leyes.
                    if self.victory_leveled:
                        self.shop_selected = 0
                        self.music.play("shop")
                        self.state = STATE_SHOP
                    else:
                        self.music.play("menu")
                        self.state = STATE_EXPLORING

    def _loop_reward(self, events):
        """Pantalla de popup al recoger una recompensa."""
        self.ui.draw_reward(self.pending_reward)

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.state = STATE_EXPLORING

    def _loop_zone_cleared(self, events):
        """Pantalla de zona limpiada. ENTER genera nuevo mapa."""
        self.ui.draw_zone_cleared(self.player)

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    # Genera nuevo mapa y reposiciona al jugador.
                    self.game_map = GameMap()
                    self.player.x = 2
                    self.player.y = 2
                    # Escala enemigos segun habilidades del jugador.
                    for e in self.game_map.enemies:
                        e.scale(self.player.ability_count)
                    self.state = STATE_EXPLORING

    # --- TIENDA DE LEYES ---

    def _loop_shop(self, events):
        """Pantalla de la tienda de leyes. El jugador compra habilidades
        antes de volver a explorar. Solo aparece cuando sube de nivel."""
        import player as player_mod
        abilities = list(player_mod.ABILITY_COSTS.keys())
        total = len(abilities)

        self.ui.draw_shop(self.player, self.shop_selected)

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.shop_selected = (self.shop_selected - 1) % total
                elif event.key == pygame.K_DOWN:
                    self.shop_selected = (self.shop_selected + 1) % total
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    key = abilities[self.shop_selected]
                    if self.player.can_afford(key):
                        self.player.buy_ability(key)
                        # Re-escalar todos los enemigos del mapa actual.
                        for e in self.game_map.enemies:
                            e.scale(self.player.ability_count)
                elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.music.play("menu")
                    self.state = STATE_EXPLORING

    def _loop_game_over(self, events):
        """Pantalla de game over."""
        self.ui.draw_defeat(self.player)

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    # Reiniciar al menu.
                    self.music.play("menu")
                    self.state = STATE_MENU
                    self.selected_class = 0
                    self.player_name = ""

    def _loop_retirement(self, events):
        """Pantalla de victoria final: jubilacion."""
        self.ui.draw_retirement(self.player)

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.running = False


if __name__ == "__main__":
    game = Game()
    game.run()
