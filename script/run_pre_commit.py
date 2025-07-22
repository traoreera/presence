#!/usr/bin/env python3
import subprocess
import sys


def run_hook(description, command):
    print(f"\n🔧 {description}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"❌ Échec lors de: {description}")
        sys.exit(result.returncode)
    print(f"✅ {description} réussi")


def main():
    print("🚀 Lancement manuel des hooks pre-commit...\n")

    # Formatage avec Black
    run_hook("Formatage Black", "black .")

    # Tri des imports avec isort
    run_hook("Tri des imports (isort)", "isort .")

    # Lint avec Flake8
    run_hook("Lint avec Flake8", "flake8")

    # Mots interdits (hook local)
    run_hook(
        "Vérification de mots interdits",
        "python scripts/check_banned_words.py $(git ls-files '*.py')",
    )

    print("\n🎉 Tous les hooks ont été exécutés avec succès.")


if __name__ == "__main__":
    main()
