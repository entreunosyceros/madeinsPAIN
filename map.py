#!/usr/bin/env python3
"""
map.py

Generacion procedural del mapa de juego y entidades que lo pueblan.

- GameMap: crea una cuadricula con muros, coloca enemigos y recompensas
  en posiciones libres aleatorias.
- Enemy: datos de un enemigo (politico) con vida, danio y recompensas.
- Reward: objetos recolectables sobre el suelo (oro, pociones, curacion).
"""

import random

# Constantes de terreno para facilitar la lectura del codigo.
WALL = "#"
FLOOR = "."


# Constante de escalado: cada habilidad aumenta stats un 15%.
ENEMY_SCALE_PER_ABILITY = 0.15


class Enemy:
    """Representa un enemigo (politico) sobre el mapa."""

    def __init__(self, x, y, name, hp, min_dmg, max_dmg, symbol):
        """Inicializa un enemigo.

        Args:
            x, y: Coordenadas iniciales sobre la cuadricula.
            name: Nombre visible en combate (ej. "Figaredo").
            hp: Puntos de vida.
            min_dmg, max_dmg: Rango de danio por ataque.
            symbol: Caracter ASCII que se dibuja en el mapa (ej. "F").
        """
        self.x = x
        self.y = y
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.min_dmg = min_dmg
        self.max_dmg = max_dmg
        self.symbol = symbol
        # Recompensas aleatorias al ser derrotado.
        self.gold_reward = random.randint(10, 30)
        self.xp_reward = random.randint(15, 40)
        # Stats base (sin escalar) para poder re-escalar al comprar habilidades.
        self.base_hp = hp
        self.base_min_dmg = min_dmg
        self.base_max_dmg = max_dmg

    def scale(self, ability_count):
        """Escala los stats del enemigo segun el numero de habilidades.

        Args:
            ability_count: Numero de habilidades compradas por el jugador.
        """
        mult = 1 + ENEMY_SCALE_PER_ABILITY * ability_count
        self.max_hp = int(self.base_hp * mult)
        self.hp = self.max_hp
        self.min_dmg = int(self.base_min_dmg * mult)
        self.max_dmg = int(self.base_max_dmg * mult)

    def attack_damage(self):
        """Returns:
            int: Danio aleatorio dentro del rango del enemigo.
        """
        return random.randint(self.min_dmg, self.max_dmg)

    def is_alive(self):
        """Returns:
            bool: True si aun tiene HP.
        """
        return self.hp > 0


class Reward:
    """Objeto coleccionable sobre el mapa."""

    def __init__(self, x, y, rtype):
        """Crea una recompensa.

        Args:
            x, y: Coordenadas en el mapa.
            rtype: Tipo de recompensa: "gold", "potion" o "health".
        """
        self.x = x
        self.y = y
        self.rtype = rtype

        # Configuracion visual y valores segun el tipo.
        if rtype == "potion":
            self.symbol = "!"
            self.color = 6  # Cyan
            self.amount = 1
        elif rtype == "health":
            self.symbol = "+"
            self.color = 4  # Amarillo
            self.amount = 30
        else:  # gold
            self.symbol = "$"
            self.color = 4  # Amarillo
            self.amount = random.randint(10, 30)


class GameMap:
    """Mapa procedural con muros, enemigos y recompensas."""

    def __init__(self, width=40, height=18):
        """Genera un nuevo mapa con entidades.

        Args:
            width: Ancho en casillas (por defecto 40).
            height: Alto en casillas (por defecto 18).
        """
        self.width = width
        self.height = height
        self.grid = self._generate()
        self.enemies = []
        self.rewards = []
        self._place_entities()

    # --- Generacion del terreno ---

    def _generate(self):
        """Crea la cuadricula de terreno.

        Los bordes siempre son muros. El interior es suelo con un 12 % de
        probabilidad de convertirse en muro aleatorio. La casilla (2,2)
        se fuerza a suelo para asegurar el spawn del jugador.

        Returns:
            list[list[str]]: Matriz bidimensional de caracteres.
        """
        grid = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                if x == 0 or y == 0 or x == self.width - 1 or y == self.height - 1:
                    row.append(WALL)
                else:
                    row.append(FLOOR if random.random() > 0.12 else WALL)
            grid.append(row)
        grid[2][2] = FLOOR  # Spawn del jugador.
        return grid

    def is_walkable(self, x, y):
        """Comprueba si una casilla es transitable (no es muro).

        Args:
            x, y: Coordenadas a consultar.

        Returns:
            bool: True si se puede caminar por ahi.
        """
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return False
        return self.grid[y][x] != WALL

    # --- Colocacion de entidades ---

    def _free_positions(self):
        """Obtiene todas las casillas de suelo libres (sin contar el spawn).

        Returns:
            list[tuple[int, int]]: Lista de (x, y) transitables.
        """
        positions = []
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.grid[y][x] == FLOOR and not (x == 2 and y == 2):
                    positions.append((x, y))
        return positions

    def _place_entities(self):
        """Coloca enemigos y recompensas en posiciones aleatorias.

        Los 3 primeros enemigos salen de las posiciones mas faciles (derecha);
        a partir del cuarto puede aparecer cualquier politico.
        """
        free = self._free_positions()
        random.shuffle(free)

        # Ordenados de mas facil (derecha) a mas dificil (izquierda).
        enemy_types = [
            ("Figaredo", 20, 2, 5, "G"),
            ("Feijoo", 30, 3, 7, "F"),
            ("Abascal", 35, 4, 9, "A"),
            ("Ayuso", 40, 5, 10, "I"),
            ("Puigdemont", 45, 5, 11, "C"),
            ("Yolanda Diaz", 60, 8, 15, "Y"),
            ("Sanchez", 70, 10, 18, "S"),
            ("Rufian", 80, 11, 20, "R"),
            ("Ione Belarra", 85, 12, 21, "B"),
            ("Junqueras", 95, 13, 23, "J"),
        ]

        num = random.randint(6, 10)
        for i in range(min(num, len(free))):
            pos = free.pop()
            # Los 3 primeros enemigos salen de la pool facil (derecha).
            # A partir del 4o puede aparecer cualquier politico.
            et = random.choice(enemy_types[:3] if i < 3 else enemy_types)
            self.enemies.append(Enemy(pos[0], pos[1], *et))

        num = random.randint(5, 9)
        for i in range(min(num, len(free))):
            pos = free.pop()
            rt = random.choice(["gold", "gold", "potion", "health"])
            self.rewards.append(Reward(pos[0], pos[1], rt))

    # --- Consultas sobre entidades ---

    def get_enemy_at(self, x, y):
        """Busca un enemigo en una casilla concreta (posicion original).

        Returns:
            Enemy|None: El enemigo encontrado o None.
        """
        for e in self.enemies:
            if e.x == x and e.y == y:
                return e
        return None

    def get_enemy_at_visual(self, x, y):
        """Busca un enemigo en una casilla (posicion visual actual).

        Comprueba la posicion visual (_current_x) si existe, o la original.

        Returns:
            Enemy|None: El enemigo encontrado o None.
        """
        for e in self.enemies:
            vx = getattr(e, '_current_x', e.x)
            if vx == x and e.y == y:
                return e
        return None

    def get_reward_at(self, x, y):
        """Busca una recompensa en una casilla concreta.

        Returns:
            Reward|None: La recompensa encontrada o None.
        """
        for r in self.rewards:
            if r.x == x and r.y == y:
                return r
        return None

    def remove_enemy(self, enemy):
        """Elimina un enemigo del mapa tras derrotarlo.

        Args:
            enemy: Instancia de Enemy a eliminar.
        """
        if enemy in self.enemies:
            self.enemies.remove(enemy)

    def remove_reward(self, reward):
        """Elimina una recompensa del mapa tras recogerla.

        Args:
            reward: Instancia de Reward a eliminar.
        """
        if reward in self.rewards:
            self.rewards.remove(reward)
