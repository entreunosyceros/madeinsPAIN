#!/usr/bin/env python3
"""
player.py

Define las clases de personaje jugable y su modelo de datos:
vida, danio, defensa, esquiva, inventario y progresion de nivel.

Cada clase representa un arquetipo social con stats ajustados:
- Trabajador: resistente, defensa alta.
- Parado: agil, puede esquivar.
- Parado de larga duracion: fragil pero con mucho danio.
- Empresario: vida baja, danio alto y oro inicial extra.
"""

import random

# Diccionario global con la configuracion de cada clase.
# Se utiliza tanto aqui como en ui.py para mostrar la ficha de seleccion.
CLASSES = {
    "trabajador": {
        "name": "Trabajador",
        "hp": 120,
        "max_hp": 120,
        "min_dmg": 15,
        "max_dmg": 25,
        "char": "T",
        "color": 1,
        "defense": 3,
    },
    "parado": {
        "name": "Parado",
        "hp": 90,
        "max_hp": 90,
        "min_dmg": 12,
        "max_dmg": 22,
        "char": "D",
        "color": 3,
        "defense": 2,
        "dodge": 0.2,
    },
    "parado_largo": {
        "name": "Parado de larga duracion",
        "hp": 70,
        "max_hp": 70,
        "min_dmg": 22,
        "max_dmg": 38,
        "char": "L",
        "color": 2,
        "defense": 1,
    },
    "empresario": {
        "name": "Empresario",
        "hp": 50,
        "max_hp": 50,
        "min_dmg": 18,
        "max_dmg": 32,
        "char": "E",
        "color": 5,
        "defense": 1,
        "dodge": 0.15,
        "start_gold": 50,
    },
}


# --- Habilidades disponibles en la tienda de leyes ---
# Cada habilidad esta asociada a un tipo de ley.

ABILITY_COSTS = {
    # Leyes Organicas
    "amnistia":     120,
    "educacion":    150,
    # Leyes Ordinarias
    "presupuestos":  80,
    "seguridad":    100,
    # Normas con rango de ley
    "decreto_ley":   70,
    "refuerzo":      90,
    # Reglamentos
    "europeo":       50,
    "sancionador":   60,
    # Leyes Autonomicas
    "parlament":     40,
    "decreto_78":    55,
}

ABILITY_EFFECTS = {
    # Leyes Organicas
    "amnistia":     lambda p: (setattr(p, "max_hp", int(p.max_hp * 1.2)),
                               setattr(p, "hp", p.max_hp)),
    "educacion":    lambda p: (setattr(p, "min_dmg", int(p.min_dmg * 1.15)),
                               setattr(p, "max_dmg", int(p.max_dmg * 1.15))),
    # Leyes Ordinarias
    "presupuestos": lambda p: (setattr(p, "min_dmg", p.min_dmg + 5),
                               setattr(p, "max_dmg", p.max_dmg + 5)),
    "seguridad":    lambda p: setattr(p, "defense", p.defense + 3),
    # Normas con rango de ley
    "decreto_ley":  lambda p: (setattr(p, "defense", p.defense + 2),
                               setattr(p, "max_hp", p.max_hp + 25),
                               setattr(p, "hp", p.hp + 25)),
    "refuerzo":     lambda p: (setattr(p, "max_hp", p.max_hp + 30),
                               setattr(p, "hp", p.hp + 30)),
    # Reglamentos
    "europeo":      lambda p: setattr(p, "dodge", min(0.6, p.dodge + 0.10)),
    "sancionador":  lambda p: (setattr(p, "min_dmg", p.min_dmg + 3),
                               setattr(p, "max_dmg", p.max_dmg + 3),
                               setattr(p, "defense", p.defense + 1)),
    # Leyes Autonomicas
    "parlament":    lambda p: (setattr(p, "potions", p.potions + 2),
                               setattr(p, "max_hp", p.max_hp + 10),
                               setattr(p, "hp", p.hp + 10)),
    "decreto_78":   lambda p: (setattr(p, "dodge", min(0.6, p.dodge + 0.08)),
                               setattr(p, "defense", p.defense + 1)),
}


class Player:
    """Avatar del jugador sobre el mapa y en combate."""

    def __init__(self, name="Hero", char_class="trabajador"):
        """Crea un personaje aplicando los stats de su clase.

        Args:
            name: Nombre personalizado introducido por el usuario.
            char_class: Clave del diccionario CLASSES (ej. "trabajador").
        """
        self.name = name
        self.char_class = char_class
        stats = CLASSES[char_class]

        # Posicion inicial sobre el mapa (se asegura que sea suelo en GameMap).
        self.x = 2
        self.y = 2

        # Stats basicos de combate.
        self.hp = stats["hp"]
        self.max_hp = stats["max_hp"]
        self.min_dmg = stats["min_dmg"]
        self.max_dmg = stats["max_dmg"]

        # Representacion visual.
        self.symbol = stats["char"]
        self.color = stats["color"]
        self.class_name = stats["name"]

        # Stats secundarios.
        self.defense = stats.get("defense", 0)
        self.dodge = stats.get("dodge", 0)

        # Inventario y progresion.
        self.potions = 2
        self.gold = stats.get("start_gold", 0)
        self.level = 1
        self.xp = 0
        self.xp_to_level = 50  # XP necesaria para subir del nivel 1 al 2.

        # Habilidades compradas en la tienda de leyes.
        self.abilities = []  # Lista de keys (str) ya compradas.

    # --- Tienda de leyes ---

    @property
    def ability_count(self):
        """Numero de habilidades adquiridas (para escalado de enemigos)."""
        return len(self.abilities)

    def can_afford(self, key):
        """Comprueba si el jugador puede pagar una habilidad.

        Args:
            key: Identificador de la habilidad (ej. "amnistia").

        Returns:
            bool: True si tiene oro suficiente y no la ha comprado ya.
        """
        if key in self.abilities:
            return False
        cost = ABILITY_COSTS.get(key, 99999)
        return self.gold >= cost

    def buy_ability(self, key):
        """Compra una habilidad, descuenta oro y aplica su efecto.

        Args:
            key: Identificador de la habilidad.

        Returns:
            bool: True si la compra fue exitosa.
        """
        if not self.can_afford(key):
            return False
        cost = ABILITY_COSTS[key]
        self.gold -= cost
        self.abilities.append(key)
        ABILITY_EFFECTS[key](self)
        return True

    # --- Movimiento ---

    def move(self, dx, dy, game_map):
        """Intenta mover al jugador si la celda destino es transitable.

        Args:
            dx: Desplazamiento en X (-1, 0, 1).
            dy: Desplazamiento en Y (-1, 0, 1).
            game_map: Instancia de GameMap para consultar colisiones.

        Returns:
            bool: True si el movimiento fue exitoso.
        """
        new_x = self.x + dx
        new_y = self.y + dy
        if 0 <= new_x < game_map.width and 0 <= new_y < game_map.height:
            if game_map.is_walkable(new_x, new_y):
                self.x = new_x
                self.y = new_y
                return True
        return False

    # --- Combate ---

    def attack_damage(self):
        """Calcula el danio de un ataque de forma aleatoria dentro del rango.

        Returns:
            int: Valor de danio.
        """
        return random.randint(self.min_dmg, self.max_dmg)

    def take_damage(self, dmg):
        """Aplica danio al jugador teniendo en cuenta esquiva y defensa.

        Args:
            dmg: Danio bruto recibido.

        Returns:
            int: Danio realmente sufrido (0 si esquiva el golpe).
        """
        if random.random() < self.dodge:
            return 0
        reduced = max(0, dmg - self.defense)
        self.hp = max(0, self.hp - reduced)
        return reduced

    def heal(self, amount=None):
        """Recupera HP sin sobrepasar el maximo.

        Args:
            amount: Cantidad a curar. Si es None, cura un 40 % del maximo.

        Returns:
            int: HP realmente recuperados.
        """
        if amount is None:
            amount = int(self.max_hp * 0.4)
        old = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old

    def is_alive(self):
        """Returns:
            bool: True si el jugador tiene HP > 0.
        """
        return self.hp > 0

    # --- Progresion ---

    def add_xp(self, amount):
        """Suma experiencia y comprueba si sube de nivel.

        Cada nivel requiere un 30 % mas de XP que el anterior.
        Al subir: +15 HP max, recupera vida al maximo y +2 al rango de danio.

        Args:
            amount: XP ganada en el combate.

        Returns:
            bool: True si ha subido de nivel en esta llamada.
        """
        self.xp += amount
        if self.xp >= self.xp_to_level:
            self.level += 1
            self.xp -= self.xp_to_level
            self.xp_to_level = int(self.xp_to_level * 1.3)
            self.max_hp += 15
            self.hp = self.max_hp
            self.min_dmg += 2
            self.max_dmg += 2
            return True
        return False
