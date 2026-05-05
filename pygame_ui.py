#!/usr/bin/env python3
"""
pygame_ui.py

Capa de renderizado grafico para madeinsPAIN.

Dibuja sprites pixel-art estilo Super Mario Bros usando las primitivas
de Pygame: rectangulos, circulos, lineas y texto. Incluye animaciones
para el jugador, enemigos, titulo, menus y pantalla de combate.
"""

import pygame
import math
from map import WALL, FLOOR
from player import ABILITY_COSTS

# --- Constantes de layout ---
TILE_W = 22
TILE_H = 22
BAR_W = 220       # Ancho de las barras de vida en combate.
HUD_H = 56        # Alto de la barra de estado (pixeles).
ENEMY_MOVE_TILES = 2  # Desplazamiento maximo de enemigos en tiles.

# --- Colores ---
COLOR_SKY        = (92, 148, 252)  # Azul cielo SMB.
COLOR_BRICK_LIGHT = (190, 100, 60) # Ladrillo claro.
COLOR_BRICK_DARK  = (140, 60, 30)  # Ladrillo oscuro.
COLOR_FLOOR       = (100, 60, 30)  # Suelo oscuro.
COLOR_FLOOR_LT    = (120, 75, 40)  # Suelo claro (detalles).
COLOR_PLAYER_BODY = (0, 0, 178)    # Azul overalls.
COLOR_PLAYER_SKIN = (255, 170, 110)# Piel.
COLOR_PLAYER_HAT  = (255, 0, 0)    # Gorra roja.
COLOR_PLAYER_EYES = (0, 0, 0)      # Ojos.
COLOR_ENEMY_BG    = (40, 40, 40)   # Fondo del sprite enemigo.
COLOR_HP_BAR_BG   = (80, 80, 80)   # Fondo barra de vida.
COLOR_HP_GREEN    = (0, 220, 0)    # HP alta.
COLOR_HP_YELLOW   = (220, 220, 0)  # HP media.
COLOR_HP_RED      = (220, 0, 0)    # HP baja.
COLOR_GOLD        = (255, 215, 0)  # Oro / VS.
COLOR_WHITE       = (255, 255, 255)
COLOR_BLACK       = (0, 0, 0)
COLOR_CYAN        = (0, 200, 200)  # Pociones.
COLOR_HEALTH      = (255, 100, 100)# Fuentes de salud.
COLOR_GRAY        = (150, 150, 150)
COLOR_DARK_GRAY   = (50, 50, 50)
COLOR_MENU_BG     = (20, 20, 60)
COLOR_COMBAT_BG   = (30, 30, 80)
COLOR_VICTORY_BG  = (10, 80, 30)
COLOR_DEFEAT_BG   = (120, 20, 20)
COLOR_RETIRE_BG   = (80, 60, 10)
COLOR_ZONE_BG     = (10, 60, 100)

# --- Paletas de colores por clase ---
CLASS_COLORS = {
    "trabajador":  COLOR_PLAYER_HAT,
    "parado":      (0, 180, 0),
    "parado_largo":(0, 120, 255),
    "empresario":  (180, 0, 180),
}

# --- Diccionario de nombres de politicos a simbolos para enemigos ---
ENEMY_SYMBOL_COLOR = {
    "Figaredo":      (128, 128, 255),   # Azul claro
    "Feijoo":        (100, 100, 255),    # Azul
    "Abascal":       (180, 180, 255),    # Azul pastel
    "Ayuso":         (0, 150, 255),      # Azul vivo
    "Puigdemont":    (0, 200, 200),      # Cyan
    "Yolanda Diaz":  (255, 100, 100),    # Rojo claro
    "Sanchez":       (255, 60, 60),      # Rojo
    "Rufian":        (200, 50, 50),      # Rojo oscuro
    "Ione Belarra":  (255, 80, 80),      # Rojo vivo
    "Junqueras":     (180, 30, 30),      # Granate
}


def get_enemy_color(name):
    """Devuelve el color asociado a un politico por su nombre."""
    return ENEMY_SYMBOL_COLOR.get(name, (200, 200, 200))


def create_player_sprite():
    """Crea un sprite del jugador estilo Mario (32x32 px)."""
    s = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Gorra
    pygame.draw.rect(s, COLOR_PLAYER_HAT, (2, 0, 28, 8))
    pygame.draw.rect(s, (200, 0, 0), (4, 0, 24, 2))
    # Piel (cara)
    pygame.draw.rect(s, COLOR_PLAYER_SKIN, (6, 8, 20, 12))
    pygame.draw.rect(s, COLOR_PLAYER_SKIN, (0, 12, 6, 8))
    pygame.draw.rect(s, COLOR_PLAYER_SKIN, (26, 12, 6, 8))
    # Ojos
    pygame.draw.rect(s, COLOR_PLAYER_EYES, (10, 12, 4, 4))
    pygame.draw.rect(s, COLOR_PLAYER_EYES, (18, 12, 4, 4))
    # Boca
    pygame.draw.rect(s, COLOR_PLAYER_EYES, (10, 18, 12, 2))
    # Overalls (cuerpo azul)
    pygame.draw.rect(s, COLOR_PLAYER_BODY, (4, 20, 24, 8))
    pygame.draw.rect(s, COLOR_PLAYER_BODY, (0, 20, 6, 6))
    pygame.draw.rect(s, COLOR_PLAYER_BODY, (26, 20, 6, 6))
    # Overalls arnes
    pygame.draw.rect(s, COLOR_PLAYER_HAT, (8, 20, 4, 4))
    pygame.draw.rect(s, COLOR_PLAYER_HAT, (20, 20, 4, 4))
    # Botones
    pygame.draw.rect(s, COLOR_GOLD, (12, 22, 2, 2))
    pygame.draw.rect(s, COLOR_GOLD, (18, 22, 2, 2))
    # Zapatos
    pygame.draw.rect(s, (100, 50, 20), (2, 28, 12, 4))
    pygame.draw.rect(s, (100, 50, 20), (18, 28, 12, 4))
    return s


def create_player_color_sprite(base_color):
    """Crea un sprite del jugador con color de gorra personalizado."""
    s = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Gorra con color de clase
    pygame.draw.rect(s, base_color, (2, 0, 28, 8))
    darker = tuple(max(0, c - 50) for c in base_color)
    pygame.draw.rect(s, darker, (4, 0, 24, 2))
    # Piel
    pygame.draw.rect(s, COLOR_PLAYER_SKIN, (6, 8, 20, 12))
    pygame.draw.rect(s, COLOR_PLAYER_SKIN, (0, 12, 6, 8))
    pygame.draw.rect(s, COLOR_PLAYER_SKIN, (26, 12, 6, 8))
    # Ojos
    pygame.draw.rect(s, COLOR_PLAYER_EYES, (10, 12, 4, 4))
    pygame.draw.rect(s, COLOR_PLAYER_EYES, (18, 12, 4, 4))
    # Boca
    pygame.draw.rect(s, COLOR_PLAYER_EYES, (10, 18, 12, 2))
    # Cuerpo
    pygame.draw.rect(s, COLOR_PLAYER_BODY, (4, 20, 24, 8))
    pygame.draw.rect(s, COLOR_PLAYER_BODY, (0, 20, 6, 6))
    pygame.draw.rect(s, COLOR_PLAYER_BODY, (26, 20, 6, 6))
    # Tirantes
    pygame.draw.rect(s, base_color, (8, 20, 4, 4))
    pygame.draw.rect(s, base_color, (20, 20, 4, 4))
    pygame.draw.rect(s, COLOR_GOLD, (12, 22, 2, 2))
    pygame.draw.rect(s, COLOR_GOLD, (18, 22, 2, 2))
    # Zapatos
    pygame.draw.rect(s, (100, 50, 20), (2, 28, 12, 4))
    pygame.draw.rect(s, (100, 50, 20), (18, 28, 12, 4))
    return s


def create_wall_sprite():
    """Crea un sprite de ladrillo SMB (TILE_W x TILE_H)."""
    s = pygame.Surface((TILE_W, TILE_H))
    s.fill(COLOR_BRICK_LIGHT)
    pygame.draw.rect(s, COLOR_BRICK_DARK, (0, 0, TILE_W, TILE_H), 2)
    pygame.draw.line(s, COLOR_BRICK_DARK, (0, TILE_H // 2), (TILE_W, TILE_H // 2), 1)
    pygame.draw.line(s, COLOR_BRICK_DARK, (TILE_W // 2, 0), (TILE_W // 2, TILE_H // 2), 1)
    pygame.draw.line(s, COLOR_BRICK_DARK, (TILE_W // 4, TILE_H // 2),
                     (TILE_W // 4, TILE_H), 1)
    return s


def create_floor_sprite():
    """Crea un sprite de suelo oscuro."""
    s = pygame.Surface((TILE_W, TILE_H))
    s.fill(COLOR_FLOOR)
    # Detalle de textura
    pygame.draw.rect(s, COLOR_FLOOR_LT, (2, 2, TILE_W - 4, TILE_H - 4), 1)
    pygame.draw.rect(s, COLOR_FLOOR_LT, (TILE_W // 2, TILE_H // 2, 2, 2))
    return s


def create_enemy_sprite(symbol, color):
    """Crea un sprite de enemigo con su simbolo y color.

    Args:
        symbol: Letra del politico (ej. 'G' para Figaredo).
        color: Tupla RGB del color asociado.
    """
    s = pygame.Surface((30, 32), pygame.SRCALPHA)
    # Cuerpo oscuro
    pygame.draw.rect(s, COLOR_ENEMY_BG, (0, 0, 30, 32), border_radius=3)
    # Borde de color
    pygame.draw.rect(s, color, (0, 0, 30, 32), 2, border_radius=3)
    # Cara/cuerpo
    pygame.draw.rect(s, color, (4, 4, 22, 16))
    # Ojos malvados
    pygame.draw.rect(s, COLOR_WHITE, (6, 6, 8, 6))
    pygame.draw.rect(s, COLOR_WHITE, (16, 6, 8, 6))
    pygame.draw.rect(s, COLOR_BLACK, (8, 8, 4, 4))
    pygame.draw.rect(s, COLOR_BLACK, (18, 8, 4, 4))
    # Boca
    pygame.draw.rect(s, COLOR_BLACK, (8, 14, 14, 3))
    # Piernas
    pygame.draw.rect(s, color, (6, 22, 6, 8))
    pygame.draw.rect(s, color, (18, 22, 6, 8))
    # Letra del nombre
    font = pygame.font.SysFont("monospace", 12, bold=True)
    letter = font.render(symbol, True, COLOR_WHITE)
    lx = (30 - letter.get_width()) // 2
    ly = (32 - letter.get_height()) // 2
    s.blit(letter, (lx, ly))
    return s


def create_gold_sprite():
    """Sprite de moneda de oro."""
    s = pygame.Surface((TILE_W, TILE_H), pygame.SRCALPHA)
    pygame.draw.circle(s, COLOR_GOLD, (TILE_W // 2, TILE_H // 2), TILE_W // 2 - 2)
    pygame.draw.circle(s, (200, 170, 0), (TILE_W // 2, TILE_H // 2), TILE_W // 2 - 4)
    # S de dollar
    font = pygame.font.SysFont("monospace", 10, bold=True)
    letter = font.render("$", True, (180, 140, 0))
    s.blit(letter, ((TILE_W - letter.get_width()) // 2,
                    (TILE_H - letter.get_height()) // 2))
    return s


def create_potion_sprite():
    """Sprite de pocion (frasco azul)."""
    s = pygame.Surface((TILE_W, TILE_H), pygame.SRCALPHA)
    pygame.draw.rect(s, (100, 100, 100), (8, 2, 6, 4))  # Tapa
    pygame.draw.rect(s, COLOR_CYAN, (6, 6, 12, 14))      # Frasco
    pygame.draw.rect(s, (0, 255, 255), (8, 8, 8, 10))     # Liquido
    pygame.draw.rect(s, COLOR_GRAY, (6, 6, 12, 14), 1)    # Borde
    return s


def create_health_sprite():
    """Sprite de fuente de salud (corazon rojo)."""
    s = pygame.Surface((TILE_W, TILE_H), pygame.SRCALPHA)
    cx, cy = TILE_W // 2, TILE_H // 2
    pygame.draw.circle(s, COLOR_HEALTH, (cx - 4, cy - 2), 6)
    pygame.draw.circle(s, COLOR_HEALTH, (cx + 4, cy - 2), 6)
    pygame.draw.polygon(s, COLOR_HEALTH, [
        (cx - 10, cy), (cx + 10, cy), (cx, cy + 10)
    ])
    pygame.draw.polygon(s, COLOR_WHITE, [
        (cx - 6, cy - 2), (cx - 2, cy - 2), (cx - 6, cy + 2)
    ], 1)
    return s


class PygameUI:
    """Renderizado grafico completo del juego con Pygame."""

    def __init__(self, screen):
        """Inicializa la UI.

        Args:
            screen: Superficie de Pygame donde dibujar.
        """
        self.screen = screen
        self.anim_timer = 0  # Contador para animaciones (en frames).

        # Fuentes.
        self.font_sm = pygame.font.SysFont("monospace", 14, bold=True)
        self.font_md = pygame.font.SysFont("monospace", 18, bold=True)
        self.font_lg = pygame.font.SysFont("monospace", 28, bold=True)
        self.font_xl = pygame.font.SysFont("monospace", 40, bold=True)

        # Sprites pregenerados.
        self.player_sprites = {}
        for cls_key, color in CLASS_COLORS.items():
            self.player_sprites[cls_key] = create_player_color_sprite(color)
        self.wall_sprite = create_wall_sprite()
        self.floor_sprite = create_floor_sprite()
        self.gold_sprite = create_gold_sprite()
        self.potion_sprite = create_potion_sprite()
        self.health_sprite = create_health_sprite()
        self.enemy_sprites = {}  # Se genera dinamicamente.

    def _get_enemy_sprite(self, enemy):
        """Obtiene o genera el sprite de un enemigo (cacheado).

        Args:
            enemy: Instancia de Enemy.

        Returns:
            pygame.Surface: Sprite del enemigo.
        """
        key = enemy.symbol
        if key not in self.enemy_sprites:
            color = get_enemy_color(enemy.name)
            self.enemy_sprites[key] = create_enemy_sprite(key, color)
        return self.enemy_sprites[key]

    def tick(self):
        """Avanza el temporizador de animacion."""
        self.anim_timer += 1

    def _center_text(self, y, text, font, color, x=None):
        """Dibuja texto centrado horizontalmente o en posicion x.

        Args:
            y: Fila en pixeles.
            text: Cadena.
            font: Fuente de Pygame.
            color: Color (tupla RGB).
            x: Posicion X opcional (None = centrado en pantalla).
        """
        surf = font.render(text, True, color)
        if x is None:
            x = (self.screen.get_width() - surf.get_width()) // 2
        else:
            x = x - surf.get_width() // 2
        self.screen.blit(surf, (x, y))

    # --- Pantalla titulo ---

    def draw_title(self):
        """Dibuja la pantalla de titulo estilo SMB con titulo grande y caja."""
        w, h = self.screen.get_width(), self.screen.get_height()
        self.screen.fill(COLOR_SKY)

        # Titulo "madeinsPAIN"
        self._center_text(h // 2 - 120, "MADEINSPAIN", self.font_xl, COLOR_GOLD)

        # Subtitulo
        self._center_text(h // 2 - 60, "~ RPG Edition ~", self.font_md, COLOR_WHITE)

        # Marco decorativo
        box_w, box_h = 380, 80
        box_x = (w - box_w) // 2
        box_y = h // 2 - 10
        pygame.draw.rect(self.screen, COLOR_MENU_BG, (box_x, box_y, box_w, box_h))
        pygame.draw.rect(self.screen, COLOR_GOLD, (box_x, box_y, box_w, box_h), 3)

        self._center_text(box_y + 12, "ENTER - COMENZAR", self.font_md, COLOR_WHITE)
        self._center_text(box_y + 42, "ESC - Salir", self.font_sm, COLOR_GRAY)

    # --- Seleccion de clase ---

    def draw_select_class(self, selected):
        """Dibuja el menu de seleccion de clase social.

        Args:
            selected: Indice de la clase seleccionada (0-3).
        """
        w, h = self.screen.get_width(), self.screen.get_height()
        self.screen.fill(COLOR_SKY)

        self._center_text(20, "SELECCIONA TU CLASE SOCIAL", self.font_lg, COLOR_WHITE)

        classes = [
            ("trabajador", "Trabajador", COLOR_PLAYER_HAT,
             "HP 120 | DMG 15-25 | Defensa 3"),
            ("parado", "Parado", (0, 180, 0),
             "HP 90 | DMG 12-22 | Esquiva 20%"),
            ("parado_largo", "Parado de larga duracion", (0, 120, 255),
             "HP 70 | DMG 22-38 | Alto dano"),
            ("empresario", "Empresario", (180, 0, 180),
             "HP 50 | DMG 18-32 | 50 oro inicial"),
        ]

        for i, (key, name, color, desc) in enumerate(classes):
            y = 70 + i * 82
            bg_color = (60, 60, 100) if i == selected else (30, 30, 60)
            pygame.draw.rect(self.screen, bg_color, (40, y, w - 80, 70))
            if i == selected:
                pygame.draw.rect(self.screen, COLOR_GOLD, (40, y, w - 80, 70), 3)

            prefix = "> " if i == selected else "  "
            text_color = COLOR_GOLD if i == selected else COLOR_GRAY
            self._center_text(y + 10, f"{prefix}[{key[0].upper()}] {name}",
                              self.font_md, text_color)
            self._center_text(y + 42, desc, self.font_sm,
                              COLOR_WHITE if i == selected else COLOR_DARK_GRAY)

        self._center_text(h - 25, "ENTER: confirmar  |  Flechas: elegir  |  ESC: salir",
                          self.font_sm, COLOR_BLACK)

    # --- Tutorial / Instrucciones ---

    def draw_tutorial(self, page):
        """Dibuja una de las paginas del tutorial antes de empezar.

        Args:
            page: Numero de pagina (0-3).
        """
        w, h = self.screen.get_width(), self.screen.get_height()
        self.screen.fill(COLOR_SKY)

        pages = [
            # Pagina 0: Objetivo
            {
                "title": "BIENVENIDO A madeinsPAIN",
                "color": COLOR_GOLD,
                "lines": [
                    "Eres un ciudadano que quiere conseguir la JUBILACION.",
                    "",
                    "Para ello debes recorrer mapas llenos de politicos,",
                    "derrotarlos en combate por turnos y subir de nivel.",
                    "",
                    "Al llegar al NIVEL 10 conseguiras tu jubilacion",
                    "y habras ganado el juego.",
                    "",
                    "Tambien puedes comprar LEYES entre niveles",
                    "para hacerte mas fuerte con el oro que recojas.",
                ],
            },
            # Pagina 1: Mapa y enemigos
            {
                "title": "EL MAPA Y LOS ENEMIGOS",
                "color": (100, 200, 255),
                "lines": [
                    "El mapa esta lleno de politicos que se mueven",
                    "por las casillas. Al pisar uno, entraras en COMBATE.",
                    "",
                    "Los politicos de derechas son los mas debiles.",
                    "Los de izquierdas y independentistas son mas duros.",
                    "",
                    "Cada enemigo da ORO y EXPERIENCIA al derrotarlo.",
                    "Cuanto mas dificil, mas recompensa obtienes.",
                    "",
                    "Si eliminas a todos, se genera un mapa nuevo.",
                ],
            },
            # Pagina 2: Recompensas
            {
                "title": "RECOMPENSAS",
                "color": COLOR_GOLD,
                "lines": [
                    "Por el mapa encontraras objetos que puedes recoger:",
                    "",
                    "  $  ORO (amarillo) - Monedas para comprar leyes.",
                    "  !  POCION (azul) - Cura ~40% de tu HP en combate.",
                    "  +  FUENTE DE SALUD (rojo) - Cura HP inmediatamente.",
                    "",
                    "El oro es muy importante: te permite comprar",
                    "LEYES que te dan habilidades permanentes.",
                    "",
                    "Recolecta todo lo que puedas antes de combatir.",
                ],
            },
            # Pagina 3: Tienda de leyes
            {
                "title": "LA TIENDA DE LEYES",
                "color": (100, 255, 150),
                "lines": [
                    "Al SUBIR DE NIVEL se abre la TIENDA DE LEYES.",
                    "",
                    "Hay 5 tipos de leyes con diferentes efectos:",
                    "",
                    "  Leyes Organicas    - Aumentan HP y dano.",
                    "  Leyes Ordinarias   - Mejoran defensa y dano.",
                    "  Normas rango ley   - Suben HP y defensa.",
                    "  Reglamentos        - Dan esquiva y dano.",
                    "  Leyes Autonomicas  - Pociones y esquiva.",
                    "",
                    "Cada ley que compres hace a los enemigos un 15%",
                    "mas fuerte. Elige bien tus compras.",
                    "",
                    "ENTER para continuar  |  Flechas: pagina",
                ],
            },
        ]

        p = pages[page]

        # Titulo de la pagina.
        self._center_text(20, p["title"], self.font_lg, p["color"])

        # Indicador de pagina.
        indicator = f"Pagina {page + 1} / {len(pages)}"
        ind_surf = self.font_sm.render(indicator, True, COLOR_DARK_GRAY)
        self.screen.blit(ind_surf, (w - ind_surf.get_width() - 15, 15))

        # Contenido de la pagina.
        y = 70
        for line in p["lines"]:
            if line == "":
                y += 8
                continue
            text_surf = self.font_sm.render(line, True, COLOR_WHITE)
            self.screen.blit(text_surf, (40, y))
            y += 20

        # Controles en la parte inferior.
        if page < len(pages) - 1:
            ctrl = "ENTER / Flecha derecha: siguiente pagina  |  Flecha izq: anterior"
        else:
            ctrl = "ENTER: empezar a jugar  |  Flecha izquierda: anterior"
        self._center_text(h - 25, ctrl, self.font_sm, COLOR_DARK_GRAY)

    # --- Introduccion nombre ---

    def draw_name_input(self, name, cls_name):
        """Dibuja la pantalla de entrada del nombre.

        Args:
            name: Nombre actualmente escrito.
            cls_name: Nombre de la clase seleccionada.
        """
        w, h = self.screen.get_width(), self.screen.get_height()
        self.screen.fill(COLOR_SKY)

        self._center_text(h // 4, f"Clase: {cls_name}", self.font_md, COLOR_GOLD)
        self._center_text(h // 4 + 50, "Como te llamas, aventurero?",
                          self.font_lg, COLOR_WHITE)

        # Caja de entrada
        box_w = 400
        box_x = (w - box_w) // 2
        box_y = h // 2
        pygame.draw.rect(self.screen, (20, 20, 40), (box_x, box_y, box_w, 50))
        pygame.draw.rect(self.screen, COLOR_GOLD, (box_x, box_y, box_w, box_h := 50), 2)

        cursor = "_" if (self.anim_timer // 30) % 2 == 0 else " "
        name_surf = self.font_lg.render(f"> {name}{cursor}", True, COLOR_WHITE)
        self.screen.blit(name_surf, (box_x + 15, box_y + 8))

        self._center_text(h // 2 + 80, "ENTER: confirmar  |  ESC: salir",
                          self.font_sm, COLOR_GRAY)

    # --- Mapa ---

    def draw_map(self, game_map, player):
        """Dibuja el mapa de exploracion con todos los sprites.

        Implementa una camara que sigue al jugador y recorta el mapa
        visible para que siempre se vea el area alrededor del personaje.
        Los enemigos oscilan por tiles (no por pixeles) para que se vean
        moverse claramente.

        Args:
            game_map: Instancia de GameMap.
            player: Instancia de Player.
        """
        w, h = self.screen.get_width(), self.screen.get_height()
        map_draw_h = h - HUD_H  # Alto disponible para el mapa.
        self.screen.fill(COLOR_SKY)

        # --- Camara centrada en el jugador ---
        player_px = player.x * TILE_W
        player_py = player.y * TILE_H

        cam_x = player_px - w // 2 + TILE_W // 2
        cam_y = player_py - map_draw_h // 2 + TILE_H // 2

        map_px_w = game_map.width * TILE_W
        map_px_h = game_map.height * TILE_H
        cam_x = max(0, min(cam_x, map_px_w - w))
        cam_y = max(0, min(cam_y, map_px_h - map_draw_h))

        # Solo renderizar tiles visibles.
        start_tx = max(0, cam_x // TILE_W)
        start_ty = max(0, cam_y // TILE_H)
        end_tx = min(game_map.width,  (cam_x + w) // TILE_W + 2)
        end_ty = min(game_map.height, (cam_y + map_draw_h) // TILE_H + 2)

        # --- Terreno y entidades ---
        for ty in range(start_ty, end_ty):
            for tx in range(start_tx, end_tx):
                sx = tx * TILE_W - cam_x
                sy = ty * TILE_H - cam_y

                cell = game_map.grid[ty][tx]

                if cell == WALL:
                    self.screen.blit(self.wall_sprite, (sx, sy))
                else:
                    self.screen.blit(self.floor_sprite, (sx, sy))

                # Recompensas.
                reward = game_map.get_reward_at(tx, ty)
                if reward:
                    if reward.rtype == "gold":
                        self.screen.blit(self.gold_sprite, (sx, sy))
                    elif reward.rtype == "potion":
                        self.screen.blit(self.potion_sprite, (sx, sy))
                    else:
                        self.screen.blit(self.health_sprite, (sx, sy))

        # --- Enemigos (se dibujan por encima, con desplazamiento por tiles) ---
        # Pre-calcular posiciones de todos los enemigos para evitar solapamientos.
        occupied = set()
        for enemy in game_map.enemies:
            phase = (enemy.x + enemy.y) * 1.3
            oscillation = math.sin(self.anim_timer * 0.04 + phase)
            tile_offset = round(ENEMY_MOVE_TILES * oscillation)

            draw_x = enemy.x + tile_offset
            direction = 1 if tile_offset > 0 else -1 if tile_offset < 0 else 0

            # Validar que el destino esta dentro del rango y es suelo.
            in_range = (enemy.x - ENEMY_MOVE_TILES <= draw_x
                        <= enemy.x + ENEMY_MOVE_TILES)
            in_bounds = 0 <= draw_x < game_map.width
            is_floor = in_bounds and game_map.grid[enemy.y][draw_x] == FLOOR

            if in_range and in_bounds and is_floor:
                pass  # Destino valido.
            elif direction != 0:
                # Deslizar DENTRO del rango hacia la posicion de origen.
                best = enemy.x  # Volver a casa por defecto.
                for step in range(abs(tile_offset), 0, -1):
                    candidate = enemy.x + step * direction
                    # Verificar que esta en rango, en mapa, y es suelo.
                    c_in_range = (enemy.x - ENEMY_MOVE_TILES <= candidate
                                  <= enemy.x + ENEMY_MOVE_TILES)
                    c_in_bounds = 0 <= candidate < game_map.width
                    c_is_floor = (c_in_bounds
                                  and game_map.grid[enemy.y][candidate] == FLOOR)
                    if c_in_range and c_in_bounds and c_is_floor:
                        best = candidate
                        break
                draw_x = best
            else:
                draw_x = enemy.x

            # Comprobacion final de que la posicion es suelo.
            if (draw_x < 0 or draw_x >= game_map.width
                    or game_map.grid[enemy.y][draw_x] != FLOOR):
                draw_x = enemy.x

            pos = (draw_x, enemy.y)

            # Si la posicion ya esta ocupada por otro enemigo, volver a casa.
            if pos in occupied:
                draw_x = enemy.x
                pos = (draw_x, enemy.y)
                if pos in occupied:
                    # Casa tambien ocupada: saltar este enemigo.
                    enemy._current_x = enemy.x
                    continue

            occupied.add(pos)
            enemy._current_x = draw_x  # Posicion visual real (para combate).
            enemy._draw_x = draw_x

        for enemy in game_map.enemies:
            draw_x = getattr(enemy, '_draw_x', enemy.x)
            sx = draw_x * TILE_W - cam_x
            sy = enemy.y * TILE_H - cam_y

            if sx + TILE_W < 0 or sx > w or sy + TILE_H < 0 or sy > map_draw_h:
                continue

            es = self._get_enemy_sprite(enemy)
            self.screen.blit(es, (sx - 4, sy - 10))

        # --- Sprite del jugador ---
        ps = self.player_sprites.get(player.char_class,
                                     self.player_sprites["trabajador"])
        px = player_px - cam_x - 5
        py = player_py - cam_y - 10
        self.screen.blit(ps, (px, py))

        # --- Barra de estado HUD (fija en la parte inferior, ancho completo) ---
        hud_y = h - HUD_H

        pygame.draw.rect(self.screen, COLOR_MENU_BG, (0, hud_y, w, HUD_H))
        pygame.draw.rect(self.screen, COLOR_GOLD, (0, hud_y, w, 2))

        # Linea 1: nombre y clase
        name_text = f"{player.name} ({player.class_name})"
        line1 = self.font_sm.render(name_text, True, COLOR_GOLD)
        self.screen.blit(line1, (20, hud_y + 5))

        # Barra de HP
        hp_ratio = player.hp / player.max_hp if player.max_hp > 0 else 0
        hp_color = (COLOR_HP_GREEN if hp_ratio > 0.5
                    else COLOR_HP_YELLOW if hp_ratio > 0.25
                    else COLOR_HP_RED)
        bar_x = 20
        bar_y = hud_y + 26
        pygame.draw.rect(self.screen, COLOR_HP_BAR_BG, (bar_x, bar_y, 150, 14))
        pygame.draw.rect(self.screen, hp_color,
                         (bar_x, bar_y, int(150 * hp_ratio), 14))
        pygame.draw.rect(self.screen, COLOR_WHITE, (bar_x, bar_y, 150, 14), 1)
        hp_text = self.font_sm.render(f"HP: {player.hp}/{player.max_hp}", True, COLOR_WHITE)
        self.screen.blit(hp_text, (175, bar_y - 2))

        # Linea 2: stats
        stats = (f"  Nivel: {player.level}/10  |  Oro: {player.gold}  |  "
                 f"Pociones: {player.potions}  |  "
                 f"Leyes: {player.ability_count}  |  "
                 f"XP: {player.xp}/{player.xp_to_level}")
        line2 = self.font_sm.render(stats, True, COLOR_GRAY)
        self.screen.blit(line2, (20, hud_y + 42))

        # Controles
        ctrl_text = self.font_sm.render("Flechas/WASD: mover  |  ESC: salir",
                                        True, COLOR_DARK_GRAY)
        self.screen.blit(ctrl_text, (w - ctrl_text.get_width() - 20, hud_y + 5))

    # --- Pantalla de presentacion de combate ---

    def draw_fight_intro(self, player, enemy, music_on=True):
        """Dibuja la pantalla de presentacion antes de un combate.

        Muestra el jugador y el enemigo enfrentados con un efecto dramatico.

        Args:
            player: Instancia de Player.
            enemy: Instancia de Enemy.
        """
        w, h = self.screen.get_width(), self.screen.get_height()
        self.screen.fill((10, 10, 30))

        # Fondo con franjas diagonales decorativas.
        for i in range(0, w + h, 40):
            pygame.draw.line(self.screen, (20, 20, 50), (0, i), (i, 0), 2)

        # Titulo "COMBATE" parpadeante.
        flash = (self.anim_timer // 8) % 2 == 0
        title_color = COLOR_PLAYER_HAT if flash else COLOR_GOLD
        self._center_text(20, "C O M B A T E", self.font_xl, title_color)

        # Sprite del jugador (izquierda).
        ps = self.player_sprites.get(player.char_class,
                                     self.player_sprites["trabajador"])
        p_x = w // 4 - 32
        p_y = h // 2 - 32
        self.screen.blit(ps, (p_x, p_y))

        # Nombre y stats del jugador (alineados bajo el sprite).
        self._center_text(p_y + 70, player.name, self.font_md, COLOR_GOLD, x=p_x + 32)
        p_stats = f"HP: {player.hp}/{player.max_hp}  DMG: {player.min_dmg}-{player.max_dmg}"
        self._center_text(p_y + 95, p_stats, self.font_sm, COLOR_WHITE, x=p_x + 32)

        # VS central.
        vs_color = COLOR_GOLD if flash else COLOR_PLAYER_HAT
        self._center_text(h // 2 - 20, "VS", self.font_xl, vs_color)

        # Sprite del enemigo (derecha).
        es = self._get_enemy_sprite(enemy)
        e_x = 3 * w // 4 - 30
        e_y = h // 2 - 32
        self.screen.blit(es, (e_x, e_y))

        # Nombre y stats del enemigo (alineados bajo el sprite).
        self._center_text(e_y + 70, enemy.name, self.font_md, COLOR_PLAYER_HAT, x=e_x + 30)
        e_stats = f"HP: {enemy.hp}/{enemy.max_hp}  DMG: {enemy.min_dmg}-{enemy.max_dmg}"
        self._center_text(e_y + 95, e_stats, self.font_sm, COLOR_WHITE, x=e_x + 30)

        # Dificultad basada en habilidades (indicador visual).
        diff_text = f"Dificultad: x{1 + 0.15 * len(player.abilities):.2f}"
        diff_color = COLOR_HP_GREEN if len(player.abilities) < 3 else (
            COLOR_HP_YELLOW if len(player.abilities) < 6 else COLOR_HP_RED)
        self._center_text(h - 60, diff_text, self.font_sm, diff_color)

        # Indicador de musica (M).
        music_text = "[M] Silenciar" if music_on else "[M] Musica"
        self._center_text(h - 45, music_text, self.font_sm, COLOR_DARK_GRAY)

        # Controles.
        self._center_text(h - 30, "ENTER: comenzar combate  |  ESC: huir (50%)",
                          self.font_sm, COLOR_DARK_GRAY)

    # --- Combate ---

    def draw_combat(self, player, enemy, msg="", msg_color=COLOR_WHITE,
                    flash_player=False, flash_enemy=False,
                    arrow_dir="none", arrow_progress=0.0):
        """Dibuja la pantalla de combate estilo Street Fighter.

        Args:
            player: Instancia de Player.
            enemy: Instancia de Enemy.
            msg: Mensaje a mostrar.
            msg_color: Color del mensaje.
            flash_player: Parpadeo invertido en el jugador.
            flash_enemy: Parpadeo invertido en el enemigo.
            arrow_dir: "right" (jugador ataca), "left" (enemigo ataca), o "none".
            arrow_progress: Progreso de la flecha 0.0-1.0.
        """
        w, h = self.screen.get_width(), self.screen.get_height()
        self.screen.fill(COLOR_COMBAT_BG)

        # Titulo
        title = self.font_lg.render("COMBATE", True, COLOR_PLAYER_HAT)
        self.screen.blit(title, ((w - title.get_width()) // 2, 10))

        # --- Sprite del jugador (izquierda) ---
        ps = self.player_sprites.get(player.char_class,
                                     self.player_sprites["trabajador"])
        p_x = 40
        p_y = 80
        p_rect = ps.get_rect(topleft=(p_x, p_y))

        if flash_player:
            flash = pygame.Surface(p_rect.size, pygame.SRCALPHA)
            flash.fill((255, 255, 255, 150))
            ps_copy = ps.copy()
            ps_copy.blit(flash, (0, 0))
            self.screen.blit(ps_copy, p_rect)
        else:
            self.screen.blit(ps, p_rect)

        # Barra de vida del jugador
        self._draw_hp_bar(p_x, p_y - 25, BAR_W, player.name,
                          player.hp, player.max_hp, COLOR_HP_GREEN, "left")

        # --- Sprite del enemigo (derecha) ---
        es = self._get_enemy_sprite(enemy)
        e_x = w - 40 - 30
        e_y = 80
        e_rect = es.get_rect(topleft=(e_x, e_y))

        if flash_enemy:
            flash = pygame.Surface(e_rect.size, pygame.SRCALPHA)
            flash.fill((255, 255, 255, 150))
            es_copy = es.copy()
            es_copy.blit(flash, (0, 0))
            self.screen.blit(es_copy, e_rect)
        else:
            self.screen.blit(es, e_rect)

        # Barra de vida del enemigo
        self._draw_hp_bar(e_x - BAR_W + 30, e_y - 25, BAR_W, enemy.name,
                          enemy.hp, enemy.max_hp, COLOR_HP_RED, "right")

        # --- VS ---
        vs_surf = self.font_lg.render("VS", True, COLOR_GOLD)
        vs_x = (p_rect.right + e_rect.left) // 2 - vs_surf.get_width() // 2
        self.screen.blit(vs_surf, (vs_x, 85))

        # --- Flecha de ataque animada ---
        if arrow_dir != "none" and arrow_progress > 0:
            arrow_start = p_rect.right + 10
            arrow_end = e_rect.left - 10
            arrow_len = int((arrow_end - arrow_start) * arrow_progress)
            arrow_y = 95

            if arrow_dir == "right":
                for i in range(0, arrow_len, 8):
                    ax = arrow_start + i
                    color = COLOR_GOLD if (i // 8 + self.anim_timer // 5) % 2 == 0 else COLOR_WHITE
                    pygame.draw.rect(self.screen, color, (ax, arrow_y, 6, 3))
                # Punta de flecha
                if arrow_len > 10:
                    tip_x = arrow_start + arrow_len
                    pygame.draw.polygon(self.screen, COLOR_GOLD, [
                        (tip_x, arrow_y + 1),
                        (tip_x - 10, arrow_y - 5),
                        (tip_x - 10, arrow_y + 7),
                    ])
            else:  # left
                for i in range(0, arrow_len, 8):
                    ax = arrow_end - i
                    color = COLOR_GOLD if (i // 8 + self.anim_timer // 5) % 2 == 0 else COLOR_WHITE
                    pygame.draw.rect(self.screen, color, (ax, arrow_y, 6, 3))
                if arrow_len > 10:
                    tip_x = arrow_end - arrow_len
                    pygame.draw.polygon(self.screen, COLOR_GOLD, [
                        (tip_x, arrow_y + 1),
                        (tip_x + 10, arrow_y - 5),
                        (tip_x + 10, arrow_y + 7),
                    ])

        # --- Mensaje ---
        if msg:
            msg_surf = self.font_md.render(msg, True, msg_color)
            self.screen.blit(msg_surf, ((w - msg_surf.get_width()) // 2, 140))

        # --- Menu de acciones ---
        menu_y = 180
        actions = [
            ("[A] Atacar", COLOR_PLAYER_HAT),
            ("[D] Defender", (0, 120, 255)),
            ("[P] Pocion", COLOR_CYAN),
            ("[H] Huir", COLOR_HP_RED),
        ]
        total_w = len(actions) * 160 + (len(actions) - 1) * 10
        menu_x = (w - total_w) // 2

        for i, (text, color) in enumerate(actions):
            bx = menu_x + i * 170
            pygame.draw.rect(self.screen, (20, 20, 50), (bx, menu_y, 155, 30))
            pygame.draw.rect(self.screen, color, (bx, menu_y, 155, 30), 2)
            txt = self.font_sm.render(text, True, COLOR_WHITE)
            self.screen.blit(txt, (bx + 8, menu_y + 5))

        # Stats del jugador
        stats_y = menu_y + 40
        stats = (f"Pociones: {player.potions}  |  Oro: {player.gold}  |  "
                 f"Nivel: {player.level}")
        self._center_text(stats_y, stats, self.font_sm, COLOR_GRAY)

    def _draw_hp_bar(self, x, y, width, name, hp, max_hp, default_color, align="left"):
        """Dibuja una barra de vida con nombre y numero.

        Args:
            x, y: Posicion.
            width: Ancho de la barra.
            name: Nombre del combatiente.
            hp: HP actual.
            max_hp: HP maximo.
            default_color: Color por defecto de la barra.
            align: "left" o "right" para alinear el texto.
        """
        ratio = max(0, min(1, hp / max_hp if max_hp > 0 else 0))
        color = (COLOR_HP_GREEN if ratio > 0.5
                 else COLOR_HP_YELLOW if ratio > 0.25
                 else COLOR_HP_RED)

        # Nombre
        name_surf = self.font_sm.render(name[:12].upper(), True, COLOR_WHITE)
        if align == "left":
            self.screen.blit(name_surf, (x, y - 18))
        else:
            self.screen.blit(name_surf, (x + width - name_surf.get_width(), y - 18))

        # Barra
        pygame.draw.rect(self.screen, COLOR_HP_BAR_BG, (x, y, width, 16))
        pygame.draw.rect(self.screen, color, (x, y, int(width * ratio), 16))
        pygame.draw.rect(self.screen, COLOR_WHITE, (x, y, width, 16), 2)

        # Numeros
        hp_text = self.font_sm.render(f"{hp}/{max_hp}", True, COLOR_WHITE)
        self.screen.blit(hp_text, (x + width // 2 - hp_text.get_width() // 2, y - 1))

    # --- Pantallas de resultado ---

    def draw_reward(self, reward):
        """Pantalla de recompensa recogida.

        Args:
            reward: Instancia de Reward.
        """
        w, h = self.screen.get_width(), self.screen.get_height()
        self.screen.fill((20, 20, 60))

        self._center_text(h // 2 - 80, "HAS ENCONTRADO ALGO!",
                          self.font_lg, COLOR_GOLD)

        if reward.rtype == "gold":
            msg = f"{reward.amount} monedas de oro!"
            color = COLOR_GOLD
            icon = self.gold_sprite
        elif reward.rtype == "potion":
            msg = "Una pocion de curacion!"
            color = COLOR_CYAN
            icon = self.potion_sprite
        else:
            msg = f"Una fuente de salud! +{reward.amount} HP"
            color = COLOR_HEALTH
            icon = self.health_sprite

        icon_big = pygame.transform.scale(icon, (64, 64))
        self.screen.blit(icon_big, (w // 2 - 32, h // 2 - 20))

        msg_surf = self.font_md.render(msg, True, color)
        self.screen.blit(msg_surf, ((w - msg_surf.get_width()) // 2, h // 2 + 55))

        self._center_text(h // 2 + 100, "ENTER para continuar...",
                          self.font_sm, COLOR_GRAY)

    def draw_victory(self, enemy_name, gold, xp, leveled, level):
        """Pantalla de victoria tras un combate.

        Args:
            enemy_name: Nombre del enemigo derrotado.
            gold: Oro ganado.
            xp: XP ganada.
            leveled: True si el jugador subio de nivel.
            level: Nivel actual del jugador.
        """
        w, h = self.screen.get_width(), self.screen.get_height()
        self.screen.fill(COLOR_VICTORY_BG)

        self._center_text(h // 2 - 100, f"VICTORIA!",
                          self.font_xl, COLOR_GOLD)
        self._center_text(h // 2 - 50, f"Has derrotado a {enemy_name}!",
                          self.font_md, COLOR_WHITE)

        rewards_text = f"+{gold} oro    +{xp} XP"
        self._center_text(h // 2, rewards_text, self.font_lg, COLOR_GOLD)

        if leveled:
            self._center_text(h // 2 + 50, f"SUBISTE DE NIVEL! Nivel {level}",
                              self.font_md, COLOR_CYAN)

        self._center_text(h // 2 + 100, "ENTER para continuar...",
                          self.font_sm, COLOR_GRAY)

    def draw_zone_cleared(self, player):
        """Pantalla de transicion al limpiar una zona.

        Args:
            player: Instancia de Player.
        """
        w, h = self.screen.get_width(), self.screen.get_height()
        self.screen.fill(COLOR_ZONE_BG)

        self._center_text(h // 2 - 80, "ZONA LIMPIADA!",
                          self.font_xl, COLOR_GOLD)
        self._center_text(h // 2 - 30,
                          "Eliminaste a todos los politicos de esta zona",
                          self.font_md, COLOR_WHITE)

        stats = f"Nivel: {player.level} | Oro: {player.gold} | Pociones: {player.potions}"
        self._center_text(h // 2 + 20, stats, self.font_sm, COLOR_GRAY)

        self._center_text(h // 2 + 60, "Generando nueva zona...",
                          self.font_lg, COLOR_CYAN)
        self._center_text(h // 2 + 110, "ENTER para continuar...",
                          self.font_sm, COLOR_GRAY)

    def draw_defeat(self, player):
        """Pantalla de derrota.

        Args:
            player: Instancia de Player.
        """
        w, h = self.screen.get_width(), self.screen.get_height()
        self.screen.fill(COLOR_DEFEAT_BG)

        self._center_text(h // 2 - 80, "GAME OVER",
                          self.font_xl, COLOR_PLAYER_HAT)
        self._center_text(h // 2 - 20, "Has sido derrotado...",
                          self.font_md, COLOR_WHITE)

        stats = (f"Nivel: {player.level} | Oro: {player.gold} | "
                 f"Nivel: {player.level}")
        self._center_text(h // 2 + 30, stats, self.font_sm, COLOR_GRAY)
        self._center_text(h // 2 + 80, "ENTER para continuar...",
                          self.font_sm, COLOR_GRAY)

    def draw_retirement(self, player):
        """Pantalla de victoria final: jubilacion.

        Args:
            player: Instancia de Player.
        """
        w, h = self.screen.get_width(), self.screen.get_height()
        self.screen.fill(COLOR_RETIRE_BG)

        # Marco decorativo
        box_w, box_h = 480, 200
        box_x = (w - box_w) // 2
        box_y = h // 2 - box_h // 2
        pygame.draw.rect(self.screen, (60, 40, 10), (box_x, box_y, box_w, box_h))
        pygame.draw.rect(self.screen, COLOR_GOLD, (box_x, box_y, box_w, box_h), 4)

        self._center_text(box_y + 20, "ENHORABUENA!", self.font_lg, COLOR_GOLD)
        self._center_text(box_y + 65, "HAS CONSEGUIDO", self.font_md, COLOR_WHITE)
        self._center_text(box_y + 100, "LA JUBILACION!", self.font_xl, COLOR_GOLD)

        info = f"{player.name} - Nivel {player.level} - {player.gold} oro"
        self._center_text(box_y + 160, info, self.font_sm, COLOR_GRAY)

        self._center_text(h // 2 + box_h // 2 + 30,
                          "Tras anos de lucha... por fin puedes descansar.",
                          self.font_sm, COLOR_GRAY)
        self._center_text(h // 2 + box_h // 2 + 60,
                          "ENTER para salir",
                          self.font_md, COLOR_WHITE)

    # --- Tienda de leyes ---

    def draw_shop(self, player, selected):
        """Dibuja la tienda de leyes donde el jugador compra habilidades.

        Args:
            player: Instancia de Player.
            selected: Indice global del item seleccionado (0-14).
        """
        w, h = self.screen.get_width(), self.screen.get_height()
        self.screen.fill(COLOR_MENU_BG)

        # Leyes organizadas por categoria (5 x 3 = 15 items).
        categories = [
            ("Leyes Organicas", [
                ("amnistia", "Ley de amnistia"),
                ("educacion", "Ley de educacion"),
            ]),
            ("Leyes Ordinarias", [
                ("presupuestos", "Ley de presupuestos"),
                ("seguridad", "Ley de seguridad ciudadana"),
            ]),
            ("Normas rango ley", [
                ("decreto_ley", "Real Decreto-ley"),
                ("refuerzo", "Ley de refuerzo"),
            ]),
            ("Reglamentos", [
                ("europeo", "Reglamento europeo"),
                ("sancionador", "Reglamento sancionador"),
            ]),
            ("Leyes Autonomicas", [
                ("parlament", "Ley del Parlament"),
                ("decreto_78", "Decreto 78/2025"),
            ]),
        ]

        # Construir lista plana: (category_name, key, name).
        flat = []
        for cat_name, items in categories:
            for key, name in items:
                flat.append((cat_name, key, name))

        total = len(flat)
        cat_names = [c[0] for c in categories]

        # Previsualizaciones por item.
        previews = {
            "amnistia":    "+20% HP maximo y se restaura al completo.",
            "educacion":   "+15% de dano en ataques (min y max).",
            "presupuestos":"+5 dano minimo y maximo en ataques.",
            "seguridad":   "+3 puntos de defensa.",
            "decreto_ley": "+2 defensa y +25 HP maximo.",
            "refuerzo":    "+30 HP maximo y se restaura.",
            "europeo":     "+10% probabilidad de esquivar ataques.",
            "sancionador": "+3 dano (min y max) y +1 defensa.",
            "parlament":   "+2 pociones y +10 HP maximo.",
            "decreto_78":  "+8% esquiva y +1 defensa.",
        }

        # Colores de categoria.
        cat_colors = [
            (180, 50, 50),    # Organicas - rojo
            (50, 120, 200),   # Ordinarias - azul
            (200, 150, 50),   # Normas rango ley - amarillo
            (50, 180, 100),   # Reglamentos - verde
            (150, 50, 200),   # Autonomicas - morado
        ]

        # Colores de fondo segun disponibilidad.
        color_owned   = (60, 100, 60)   # Verde oscuro: ya comprada.
        color_can_buy = (50, 50, 90)    # Azul oscuro: puede comprar.
        color_cant    = (60, 30, 30)    # Rojo oscuro: no puede comprar.

        # --- Layout ---
        sidebar_w = 160
        list_x = sidebar_w + 5
        list_w = w - sidebar_w - 10
        item_h = max(24, (h - 65) // total - 2)

        # Titulo.
        self._center_text(5, f"TIENDA DE LEYES  |  Oro: {player.gold}",
                          self.font_md, COLOR_GOLD)

        # --- Barra lateral: categorias ---
        cat_idx = 0
        cat_y = 30
        for ci, (cat_name, items) in enumerate(categories):
            block_h = len(items) * (item_h + 2)
            pygame.draw.rect(self.screen, cat_colors[ci],
                             (0, cat_y, sidebar_w, block_h))
            pygame.draw.rect(self.screen, COLOR_GOLD,
                             (0, cat_y, sidebar_w, block_h), 1)
            self._center_text(cat_y + block_h // 2 - 8,
                              cat_name, self.font_sm, COLOR_WHITE)
            cat_y += block_h

        # --- Lista de items ---
        for i, (cat_name, key, name) in enumerate(flat):
            iy = 30 + i * (item_h + 2)
            is_sel = i == selected
            owned = key in player.abilities
            can_buy = player.can_afford(key)

            # Color de fondo.
            if owned:
                bg = color_owned
            elif can_buy:
                bg = color_can_buy if is_sel else (30, 30, 50)
            else:
                bg = color_cant if is_sel else (40, 20, 20)

            pygame.draw.rect(self.screen, bg, (list_x, iy, list_w, item_h))
            if is_sel:
                pygame.draw.rect(self.screen, COLOR_GOLD,
                                 (list_x, iy, list_w, item_h), 2)

            # Indicador de seleccion.
            prefix = ">" if is_sel else " "
            cost = ABILITY_COSTS.get(key, 0)

            # Texto del item.
            if owned:
                text = f"{prefix} [X] {name}"
                text_color = (100, 255, 100)
            else:
                text = f"{prefix} [{cost} oro] {name}"
                text_color = COLOR_WHITE if can_buy else (120, 120, 120)

            txt = self.font_sm.render(text, True, text_color)
            self.screen.blit(txt, (list_x + 8, iy + (item_h - 14) // 2))

        # --- Panel de previsualizacion ---
        prev_y = 30 + total * (item_h + 2) + 5
        prev_h = h - prev_y - 10
        if prev_h > 30:
            pygame.draw.rect(self.screen, (20, 20, 40),
                             (0, prev_y, w, prev_h))
            pygame.draw.rect(self.screen, COLOR_GOLD,
                             (0, prev_y, w, prev_h), 1)

            sel_key = flat[selected][1] if selected < total else ""
            sel_name = flat[selected][2] if selected < total else ""

            # Nombre de la ley.
            name_txt = self.font_md.render(sel_name, True, COLOR_GOLD)
            self.screen.blit(name_txt, (list_x + 8, prev_y + 5))

            # Previsualizacion del efecto.
            preview_text = previews.get(sel_key, "")
            if preview_text:
                lines = self._wrap_text(preview_text, list_w - 16, self.font_sm)
                for li, line in enumerate(lines):
                    lt = self.font_sm.render(line, True, COLOR_WHITE)
                    self.screen.blit(lt, (list_x + 8, prev_y + 30 + li * 16))

            # Coste y estado.
            if sel_key in player.abilities:
                status = "COMPRADA"
                status_color = (100, 255, 100)
            elif player.can_afford(sel_key):
                status = f"Coste: {ABILITY_COSTS.get(sel_key, 0)} oro  |  ENTER: comprar"
                status_color = COLOR_GOLD
            else:
                status = f"Coste: {ABILITY_COSTS.get(sel_key, 0)} oro  |  No tienes suficiente"
                status_color = (255, 80, 80)
            st = self.font_sm.render(status, True, status_color)
            self.screen.blit(st, (list_x + 8, prev_y + prev_h - 22))

        # Controles inferiores.
        ctrl = "Flechas: elegir  |  ENTER: comprar  |  ESC: salir"
        ct = self.font_sm.render(ctrl, True, COLOR_DARK_GRAY)
        self.screen.blit(ct, ((w - ct.get_width()) // 2, h - 18))

    def _wrap_text(self, text, max_width, font):
        """Divide un texto en lineas que quepan en un ancho dado.

        Args:
            text: Texto completo.
            max_width: Ancho maximo en pixeles.
            font: Fuente de Pygame.

        Returns:
            list[str]: Lista de lineas.
        """
        words = text.split()
        lines = []
        current = ""
        for word in words:
            test = current + (" " if current else "") + word
            if font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines
