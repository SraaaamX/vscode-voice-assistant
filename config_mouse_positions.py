from src.keyboard.controller import KeyboardController
import time


def main():
    controller = KeyboardController()
    print("\nConfiguration des positions de la souris")
    print("----------------------------------------")
    print("Pour chaque position:")
    print("1. Placez votre souris à l'endroit désiré")
    print("2. Appuyez sur Entrée pour capturer la position")
    print("3. Les coordonnées seront affichées\n")

    positions = {
        "accept_pos1": "première position pour accepter",
        "accept_pos2": "deuxième position pour accepter",
        "reject_pos": "position pour refuser",
    }

    results = {}

    for pos_name, description in positions.items():
        input(
            f"\nPositionnez la souris pour la {description} puis appuyez sur Entrée..."
        )
        time.sleep(0.5)  # Petit délai pour s'assurer que la souris est bien positionnée
        pos = controller.get_current_mouse_position()
        results[pos_name] = pos
        print(f"Position enregistrée: {pos}")

    print("\nConfiguration terminée!")
    print("\nCopiez ces lignes dans src/constants.py:")
    print("\nMOUSE_POSITIONS = {")
    for pos_name, pos in results.items():
        print(f'    "{pos_name}": {pos},')
    print("}")


if __name__ == "__main__":
    main()
