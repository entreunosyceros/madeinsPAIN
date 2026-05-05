#!/usr/bin/env python3
"""
run_app.py

Lanzador automatico de madeinsPAIN.

Responsabilidades:
    1. Comprueba si el entorno virtual (.venv) existe; si no, lo crea.
    2. Instala las dependencias de requirements.txt si faltan.
    3. Presenta un menu al usuario para elegir version (terminal o grafica).
    4. Lanza la version seleccionada.
"""

import os
import sys
import subprocess
import venv

# Ruta del entorno virtual dentro del proyecto.
VENV_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv")


def get_venv_python():
    """Devuelve la ruta del ejecutable de Python dentro del entorno virtual.

    Returns:
        str: Ruta absoluta al binario python del .venv.
    """
    if os.name == "nt":  # Windows
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    else:  # Linux / macOS
        return os.path.join(VENV_DIR, "bin", "python3")


def ensure_venv():
    """Crea el entorno virtual si no existe.

    Muestra el progreso al usuario porque puede tardar unos segundos.
    """
    if os.path.isdir(VENV_DIR):
        print("  Entorno virtual encontrado.")
        return

    print("  Creando entorno virtual...")
    venv.create(VENV_DIR, with_pip=True)
    print("  Entorno virtual creado.")


def install_requirements():
    """Instala las dependencias de requirements.txt si faltan.

    Comprueba si pygame ya esta importable; si no, ejecuta pip install.
    """
    python = get_venv_python()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    req_file = os.path.join(script_dir, "requirements.txt")

    # Comprobacion rapida: intentar importar pygame desde el venv.
    check = subprocess.run(
        [python, "-c", "import pygame"],
        capture_output=True,
        text=True,
    )

    if check.returncode == 0:
        print("  Dependencias instaladas.")
        return

    print("  Instalando dependencias (pygame)...")
    if not os.path.isfile(req_file):
        print("  ERROR: requirements.txt no encontrado.")
        sys.exit(1)

    subprocess.run(
        [python, "-m", "pip", "install", "-r", req_file],
        check=True,
    )
    print("  Dependencias instaladas.")


def show_menu():
    """Muestra el menu de seleccion de version.

    Returns:
        str: "terminal", "grafico" o "quit".
    """
    print()
    print("=" * 44)
    print()
    print("       m a d e i n s P A I N")
    print("          ~  RPG Terminal  ~")
    print()
    print("=" * 44)
    print()
    print("  1 - Terminal  (curses)")
    print("  2 - Grafico   (Pygame)")
    print("  3 - Salir")
    print()

    while True:
        choice = input("  Elige una opcion: ").strip()
        if choice == "1":
            return "terminal"
        elif choice == "2":
            return "grafico"
        elif choice == "3":
            return "quit"


def launch(mode):
    """Lanza la version seleccionada del juego.

    Args:
        mode: "terminal" o "grafico".
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    python = get_venv_python()

    if mode == "terminal":
        script = os.path.join(script_dir, "main.py")
    else:
        script = os.path.join(script_dir, "pygame_game.py")

    print()
    print(f"  Lanzando version {mode}...")
    print()

    # Ejecuta el juego como subproceso y espera a que termine.
    # cwd se fija al directorio del proyecto para que los imports relativos
    # funcionen igual que si se lanzase manualmente.
    subprocess.run([python, script], cwd=script_dir)


def main():
    print()
    print("  === madeinsPAIN - Lanzador ===")
    print()

    # 1. Preparar entorno virtual.
    ensure_venv()
    install_requirements()

    # 2. Seleccionar modo de juego.
    mode = show_menu()

    if mode == "quit":
        print("  Hasta luego!")
        return

    # 3. Ejecutar.
    launch(mode)


if __name__ == "__main__":
    main()
