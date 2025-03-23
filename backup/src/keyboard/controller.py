import time
from pynput.keyboard import Key, Controller as PynputKeyboardController
from pynput.mouse import Button, Controller as PynputMouseController
from src.constants import SHORTCUTS, MOUSE_POSITIONS


class KeyboardController:
    def __init__(self):
        """Initialisation du contrôleur"""
        self.keyboard = PynputKeyboardController()
        self.mouse = PynputMouseController()

    def press_keys(self, keys):
        """Appuie sur des touches et les relâche dans l'ordre inverse"""
        if not isinstance(keys, list):
            keys = [keys]

        # Appuie sur les touches dans l'ordre
        pressed_keys = []
        for key in keys:
            if isinstance(key, str):
                if len(key) == 1:  # Caractère unique
                    self.keyboard.press(key)
                    pressed_keys.append(key)
                else:  # Nom de touche spéciale
                    special_key = getattr(Key, key.lower(), None)
                    if special_key:
                        self.keyboard.press(special_key)
                        pressed_keys.append(special_key)
            else:  # Déjà une instance de Key
                self.keyboard.press(key)
                pressed_keys.append(key)

        # Relâche les touches dans l'ordre inverse
        for key in reversed(pressed_keys):
            self.keyboard.release(key)

    def get_current_mouse_position(self):
        """Retourne la position actuelle de la souris"""
        return tuple(map(int, self.mouse.position))

    def move_mouse_to(self, x, y):
        """Déplace la souris à une position donnée"""
        try:
            # Déplacement instantané
            self.mouse.position = (float(x), float(y))
        except Exception as e:
            print(f"Erreur lors du déplacement de la souris: {e}")
            raise

    def click_mouse(self, button=Button.left):
        """Clique avec le bouton de souris spécifié"""
        try:
            self.mouse.click(button)
        except Exception as e:
            print(f"Erreur lors du clic souris: {e}")
            raise

    def execute_mouse_sequence(self, position_name):
        """Exécute une séquence de mouvements de souris"""
        # Récupère la position depuis la configuration
        print(f"Positions disponibles: {MOUSE_POSITIONS}")  # Debug
        print(f"Position demandée: {position_name}")  # Debug
        position = MOUSE_POSITIONS.get(position_name)
        if not position:
            raise ValueError(
                f"Position non configurée: {position_name}. Positions disponibles: {list(MOUSE_POSITIONS.keys())}"
            )

        try:
            # Déplace la souris et clique
            current_pos = self.get_current_mouse_position()
            print(f"Position actuelle: {current_pos}")  # Debug
            print(f"Position cible '{position_name}': {position}")  # Debug

            self.move_mouse_to(*position)
            self.click_mouse()  # Clic instantané
        except Exception as e:
            print(
                f"Erreur lors de l'exécution de la séquence souris '{position_name}': {e}"
            )
            print(f"Position actuelle: {self.get_current_mouse_position()}")
            raise

    def type_text(self, text, add_enter=False):
        """Écrit du texte"""
        self.keyboard.type(text)
        if add_enter:
            self.execute_shortcut("enter")

    def cancel_action(self):
        """Annule l'action en cours"""
        self.execute_shortcut("cancel")

    def accept_ia(self):
        """Accepte la suggestion IA"""
        self.execute_shortcut("ia_accept")

    def reject_ia(self):
        """Refuse la suggestion IA"""
        self.execute_shortcut("ia_reject")

    def execute_code(self):
        """Exécute le code"""
        self.execute_shortcut("execute")

    def stop_execution(self):
        """Arrête l'exécution"""
        self.execute_shortcut("stop")

    def execute_shortcut(self, shortcut_name):
        """Exécute un raccourci clavier"""
        shortcut = SHORTCUTS.get(shortcut_name)
        if shortcut:
            self.press_keys(shortcut)

    def new_file(self):
        """Crée un nouveau fichier"""
        self.execute_shortcut("new_file")

    def next_file(self, count=1):
        """Navigue vers l'onglet suivant

        Args:
            count (int): Nombre de fois à répéter la navigation
        """
        for _ in range(count):
            self.press_keys([Key.ctrl, Key.page_down])

    def previous_file(self, count=1):
        """Navigue vers l'onglet précédent

        Args:
            count (int): Nombre de fois à répéter la navigation
        """
        for _ in range(count):
            self.press_keys([Key.ctrl, Key.page_up])
