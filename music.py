#!/usr/bin/env python3
"""
music.py

Generador de musica chiptune procedural estilo RPG de los 80.

Genera audio en tiempo real usando ondas cuadradas (square waves) para
conseguir el sonido clasico de consolas de 8 bits. No requiere archivos
de audio externos.

Incluye tres temas:
- menu: melodia epica para pantallas de titulo y menus.
- combat: ritmo rapido y agresivo para los combates.
- shop: melodia tranquila para la tienda de leyes.
"""

import math
import array
import struct

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


# --- Constantes de audio ---
SAMPLE_RATE = 44100  # Frecuencia estandar de pygame.mixer.
CHANNELS = 2
BITS = -16  # AUDIO_S16SYS: signed 16-bit, system byte order.
MIXER_FORMAT = -16  # AUDIO_S16SYS: signed 16-bit, system byte order.


# --- Notas musicales (frecuencias en Hz) ---
# Octava 4 (central): C4=261.63, D4=293.66, E4=329.63, F4=349.23
#                G4=392.00, A4=440.00, B4=493.88
# Octava 5: C5=523.25, D5=587.33, E5=659.25, F5=698.46
#                G5=783.99, A5=880.00, B5=987.77

def note_freq(name):
    """Convierte nombre de nota a frecuencia. Ej: 'C4', 'A#3', 'Eb5'."""
    note_names = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
    n = name[0].upper()
    idx = 1
    semitone = note_names[n]
    if len(name) > 1 and name[1] == '#':
        semitone += 1
        idx += 1
    elif len(name) > 1 and name[1] == 'b':
        semitone -= 1
        idx += 1
    octave = int(name[idx:])
    midi = (octave + 1) * 12 + semitone
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def make_note(freq, duration, volume=0.3, wave_type="square", attack=0.01,
              decay=0.05, sustain_level=0.7, release=0.05):
    """Genera una nota musical como bytes de audio stereo 16-bit.

    Args:
        freq: Frecuencia en Hz.
        duration: Duracion en segundos.
        volume: Volumen (0.0 a 1.0).
        wave_type: "square", "triangle" o "sawtooth".
        attack, decay, release: Envolvente ADSR en segundos.
        sustain_level: Nivel de sustain (0.0 a 1.0).

    Returns:
        bytes: Muestras de audio en formato stereo 16-bit signed.
    """
    n_samples = int(SAMPLE_RATE * duration)
    buf = array.array('h', [0] * n_samples * CHANNELS)

    for i in range(n_samples):
        t = i / SAMPLE_RATE
        phase = (t * freq) % 1.0

        # Tipo de onda.
        if wave_type == "square":
            sample = 0.6 if phase < 0.5 else -0.6
        elif wave_type == "triangle":
            sample = 4.0 * abs(phase - 0.5) - 1.0
        elif wave_type == "sawtooth":
            sample = 2.0 * phase - 1.0
        else:
            sample = 0.6 if phase < 0.5 else -0.6

        # Envolvente ADSR.
        if t < attack:
            env = t / attack
        elif t < attack + decay:
            env = 1.0 - (1.0 - sustain_level) * ((t - attack) / decay)
        elif t < duration - release:
            env = sustain_level
        else:
            remaining = duration - t
            env = max(0, sustain_level * (remaining / release))

        val = int(sample * env * volume * 32767)
        val = max(-32767, min(32767, val))
        buf[i * CHANNELS] = val
        buf[i * CHANNELS + 1] = val

    return bytes(buf)


def make_rest(duration):
    """Genera silencio como bytes de audio stereo 16-bit."""
    n_samples = int(SAMPLE_RATE * duration)
    return bytes(n_samples * CHANNELS * 2)


def make_theme(notes_data, bpm, bass_data=None):
    """Genera un tema musical completo mezclando melodia y bajo.

    Args:
        notes_data: Lista de (nota, duracion_en_pulsos, wave_type) para melodia.
        bpm: Pulsos por minuto.
        bass_data: Lista de (nota, duracion_en_pulsos) para el bajo (opcional).

    Returns:
        bytes: Audio stereo 16-bit del tema completo.
    """
    beat_duration = 60.0 / bpm
    all_samples = []

    # Generar melodia.
    for note_info in notes_data:
        note_name, beats, wave = note_info
        dur = beats * beat_duration
        if note_name == "R":
            all_samples.append(make_rest(dur))
        else:
            freq = note_freq(note_name)
            all_samples.append(make_note(freq, dur, volume=0.25,
                                         wave_type=wave, attack=0.005,
                                         decay=0.03, sustain_level=0.7,
                                         release=0.03))

    # Generar bajo si se proporciona.
    if bass_data:
        bass_samples = []
        for bass_info in bass_data:
            note_name, beats = bass_info
            dur = beats * beat_duration
            if note_name == "R":
                bass_samples.append(make_rest(dur))
            else:
                freq = note_freq(note_name)
                bass_samples.append(make_note(freq, dur, volume=0.15,
                                              wave_type="triangle",
                                              attack=0.01, decay=0.05,
                                              sustain_level=0.6,
                                              release=0.05))

        # Mezclar melodia y bajo (el mas largo determina la duracion total).
        melody_raw = b"".join(all_samples)
        bass_raw = b"".join(bass_samples)

        max_len = max(len(melody_raw), len(bass_raw))

        # Rellenar con silencio el mas corto.
        if len(melody_raw) < max_len:
            melody_raw += b"\x00" * (max_len - len(melody_raw))
        if len(bass_raw) < max_len:
            bass_raw += b"\x00" * (max_len - len(bass_raw))

        # Mezclar.
        combined = array.array('h', [0] * (max_len // 2))
        melody_arr = array.array('h', melody_raw)
        bass_arr = array.array('h', bass_raw)
        for i in range(len(combined)):
            combined[i] = max(-32767, min(32767,
                               melody_arr[i] + bass_arr[i]))
        return bytes(combined)

    return b"".join(all_samples)


# --- Definicion de temas ---

def create_menu_theme():
    """Tema del menu: melodia epica con progresion Am-F-G-Em."""
    melody = [
        # Barra 1-2: Melodia principal (A menor)
        ("A4", 1, "square"), ("C5", 1, "square"), ("E5", 1, "square"),
        ("A5", 2, "square"), ("G5", 1, "square"), ("E5", 1, "square"),
        ("C5", 2, "square"), ("A4", 1, "square"), ("R", 1, "square"),
        ("G4", 1, "square"), ("B4", 1, "square"), ("D5", 1, "square"),
        ("G5", 2, "square"), ("F5", 1, "square"), ("D5", 1, "square"),
        ("B4", 2, "square"), ("G4", 1, "square"), ("R", 1, "square"),
        # Barra 3-4: Continuacion
        ("F4", 1, "square"), ("A4", 1, "square"), ("C5", 1, "square"),
        ("F5", 2, "square"), ("E5", 1, "square"), ("C5", 1, "square"),
        ("A4", 2, "square"), ("F4", 1, "square"), ("R", 1, "square"),
        ("E4", 1, "square"), ("G4", 1, "square"), ("B4", 1, "square"),
        ("E5", 2, "square"), ("D5", 1, "square"), ("B4", 1, "square"),
        ("G4", 2, "square"), ("E4", 1, "square"), ("R", 1, "square"),
    ]

    bass = [
        ("A2", 4), ("A2", 4),
        ("G2", 4), ("G2", 4),
        ("F2", 4), ("F2", 4),
        ("E2", 4), ("E2", 4),
    ]

    return make_theme(melody, bpm=100, bass_data=bass)


def create_combat_theme():
    """Tema de combate: ritmo rapido y agresivo."""
    melody = [
        # Barra 1: Motivo agresivo
        ("E5", 0.5, "square"), ("E5", 0.5, "square"), ("R", 0.5, "square"),
        ("E5", 0.5, "square"), ("D5", 0.5, "square"), ("C5", 0.5, "square"),
        ("B4", 1, "square"), ("R", 0.5, "square"), ("A4", 0.5, "square"),
        # Barra 2
        ("E5", 0.5, "square"), ("E5", 0.5, "square"), ("R", 0.5, "square"),
        ("G5", 0.5, "square"), ("F5", 0.5, "square"), ("E5", 0.5, "square"),
        ("D5", 1, "square"), ("R", 0.5, "square"), ("C5", 0.5, "square"),
        # Barra 3
        ("A4", 0.5, "square"), ("B4", 0.5, "square"), ("C5", 0.5, "square"),
        ("D5", 0.5, "square"), ("E5", 0.5, "square"), ("F5", 0.5, "square"),
        ("G5", 1, "square"), ("R", 0.5, "square"), ("E5", 0.5, "square"),
        # Barra 4
        ("A5", 0.5, "square"), ("G5", 0.5, "square"), ("F5", 0.5, "square"),
        ("E5", 0.5, "square"), ("D5", 0.5, "square"), ("C5", 0.5, "square"),
        ("B4", 1, "square"), ("A4", 1, "square"),
    ]

    bass = [
        ("A2", 1), ("A2", 1), ("A2", 1), ("A2", 1),
        ("G2", 1), ("G2", 1), ("G2", 1), ("G2", 1),
        ("F2", 1), ("F2", 1), ("F2", 1), ("F2", 1),
        ("E2", 1), ("E2", 1), ("E2", 1), ("E2", 1),
    ]

    return make_theme(melody, bpm=150, bass_data=bass)


def create_shop_theme():
    """Tema de la tienda: melodia tranquila y misteriosa."""
    melody = [
        # Barra 1
        ("C5", 2, "triangle"), ("E5", 1, "triangle"), ("G5", 1, "triangle"),
        ("A5", 2, "triangle"), ("G5", 1, "triangle"), ("E5", 1, "triangle"),
        # Barra 2
        ("F5", 2, "triangle"), ("A5", 1, "triangle"), ("C6", 1, "triangle"),
        ("B5", 2, "triangle"), ("G5", 1, "triangle"), ("E5", 1, "triangle"),
        # Barra 3
        ("D5", 2, "triangle"), ("F5", 1, "triangle"), ("A5", 1, "triangle"),
        ("G5", 2, "triangle"), ("E5", 1, "triangle"), ("C5", 1, "triangle"),
        # Barra 4
        ("A4", 2, "triangle"), ("C5", 1, "triangle"), ("E5", 1, "triangle"),
        ("A4", 4, "triangle"),
    ]

    bass = [
        ("A2", 4), ("F2", 4),
        ("D3", 4), ("A2", 4),
    ]

    return make_theme(melody, bpm=75, bass_data=bass)


class MusicPlayer:
    """Reproductor de musica chiptune para el juego."""

    def __init__(self):
        """Inicializa el mezclador de Pygame y genera los temas."""
        self.enabled = False
        self.current_theme = None
        self.sounds = {}
        self.muted = False
        self._saved_volume = 0.4

        if not PYGAME_AVAILABLE:
            return

        try:
            # El mixer ya puede estar inicializado por pygame.init().
            # Solo inicializar si no lo esta.
            if not pygame.mixer.get_init():
                pygame.mixer.pre_init(SAMPLE_RATE, BITS, CHANNELS, 1024)
                pygame.mixer.init()
            pygame.mixer.set_num_channels(4)
            self.enabled = True

            # Generar los tres temas.
            self.sounds["menu"] = pygame.mixer.Sound(
                buffer=create_menu_theme())
            self.sounds["combat"] = pygame.mixer.Sound(
                buffer=create_combat_theme())
            self.sounds["shop"] = pygame.mixer.Sound(
                buffer=create_shop_theme())

            # Ajustar volumenes.
            self.sounds["menu"].set_volume(0.4)
            self.sounds["combat"].set_volume(0.35)
            self.sounds["shop"].set_volume(0.3)

        except Exception:
            self.enabled = False

    def play(self, theme_name):
        """Reproduce un tema en bucle. Si ya esta sonando, no lo reinicia.

        Args:
            theme_name: "menu", "combat" o "shop".
        """
        if not self.enabled:
            return
        if self.current_theme == theme_name:
            return  # Ya esta sonando.
        self.stop()
        sound = self.sounds.get(theme_name)
        if sound:
            sound.play(-1)  # -1 = bucle infinito.
            self.current_theme = theme_name

    def stop(self):
        """Detiene toda la musica."""
        if not self.enabled:
            return
        pygame.mixer.stop()
        self.current_theme = None

    def set_volume(self, volume):
        """Ajusta el volumen global de la musica.

        Args:
            volume: Volumen entre 0.0 (silencio) y 1.0 (maximo).
        """
        if not self.enabled:
            return
        for sound in self.sounds.values():
            sound.set_volume(volume)

    def toggle(self):
        """Activa o desactiva el sonido. Devuelve el nuevo estado (bool)."""
        if not self.enabled:
            return False
        if self.muted:
            self.muted = False
            self.set_volume(self._saved_volume)
            if self.current_theme:
                self.play(self.current_theme)
        else:
            self.muted = True
            self._saved_volume = self.sounds[list(self.sounds.keys())[0]].get_volume()
            self.set_volume(0.0)
            self.stop()
        return not self.muted
