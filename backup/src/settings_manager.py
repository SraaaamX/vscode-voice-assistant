import json
import os
from src.constants import DEFAULT_MOUSE_POSITIONS, MOUSE_POSITIONS, SHORTCUTS
from pynput.keyboard import Key


class SettingsManager:
    def __init__(self):
        self.config_file = os.path.join(os.getcwd(), "config.json")
        # Store a copy of initial shortcuts as defaults
        self.default_shortcuts = SHORTCUTS.copy()
        # Default wake word
        self.wake_word = "jarvis"
        # Default voice commands
        self.voice_commands = {
            # Navigation
            "monte": "monte",
            "baisse": "baisse",
            "monte de": "monte",
            "baisse de": "baisse",
            "monte tout en haut": "monte_tout_en_haut",
            "baisse tout en bas": "baisse_tout_en_bas",
            # Terminal
            "terminal": "new_terminal",
            "dernier terminal": "last_terminal",
            # Fichiers
            "nouveau dossier": "new_folder",
            "nouveau fichier": "new_file",
            "ouvre fichier": "open_file",
            "ouvre dossier": "open_folder",
            "explore": "show_explorer",
            "onglet suivant": "onglet_suivant",
            "onglet précédent": "onglet_precedent",
            # Contrôle IA - Souris
            "prompt": "cline_trigger",
            "prompt accepte": "cline_accept",
            "prompt refuse": "cline_reject",
            # Contrôle IA - Clavier
            "accepte": "accepte",
            "refuse": "refuse",
            "sauvegarde": "sauvegarde",
            # Autres
            "ouvre": "open_item",
            "écoute": "listen",
            "stop": "stop",
            "arrête": "stop",
            "annule": "cancel",
            "annuler": "cancel",
        }
        self.load_settings()

    def load_settings(self):
        """Charge les paramètres depuis le fichier de configuration"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)

                    # Load wake word
                    self.wake_word = config.get("wake_word", self.wake_word)

                    # Load voice commands
                    voice_commands = config.get("voice_commands", {})
                    if voice_commands:
                        self.voice_commands.update(voice_commands)

                    # Mise à jour des positions de souris
                    mouse_positions = config.get(
                        "mouse_positions", DEFAULT_MOUSE_POSITIONS
                    )
                    MOUSE_POSITIONS.clear()
                    MOUSE_POSITIONS.update(
                        {
                            k: tuple(v) if isinstance(v, list) else v
                            for k, v in mouse_positions.items()
                        }
                    )

                    # Mise à jour des raccourcis
                    # Conversion des raccourcis chargés
                    shortcuts = config.get("shortcuts", self.default_shortcuts)
                    SHORTCUTS.clear()
                    for name, keys in shortcuts.items():
                        SHORTCUTS[name] = [
                            (
                                Key[k[4:]]
                                if isinstance(k, str) and k.startswith("Key.")
                                else k
                            )
                            for k in keys
                        ]
            else:
                self.save_settings()  # Crée le fichier avec les valeurs par défaut
        except Exception as e:
            print(f"Erreur lors du chargement des paramètres: {str(e)}")
            # Restaure les valeurs par défaut en cas d'erreur
            MOUSE_POSITIONS.clear()
            MOUSE_POSITIONS.update(DEFAULT_MOUSE_POSITIONS)
            SHORTCUTS.clear()
            SHORTCUTS.update(self.default_shortcuts)

    def save_settings(self):
        """Sauvegarde les paramètres dans le fichier de configuration"""
        try:
            config = {
                "wake_word": self.wake_word,
                "voice_commands": self.voice_commands,
                "mouse_positions": {
                    k: list(v) if isinstance(v, tuple) else v
                    for k, v in MOUSE_POSITIONS.items()
                },
                "shortcuts": {
                    name: [f"Key.{k.name}" if isinstance(k, Key) else k for k in keys]
                    for name, keys in SHORTCUTS.items()
                },
            }
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des paramètres: {str(e)}")

    def reset_shortcuts(self):
        """Réinitialise les raccourcis clavier aux valeurs par défaut"""
        SHORTCUTS.clear()
        SHORTCUTS.update(self.default_shortcuts)
        self.save_settings()

    def reset_mouse_positions(self):
        """Réinitialise les positions de souris aux valeurs par défaut"""
        MOUSE_POSITIONS.clear()
        MOUSE_POSITIONS.update(DEFAULT_MOUSE_POSITIONS)
        self.save_settings()

    def reset_to_defaults(self):
        """Réinitialise tous les paramètres aux valeurs par défaut"""
        self.reset_shortcuts()
        self.reset_mouse_positions()
        self.wake_word = "jarvis"
        self.voice_commands = {
            # Navigation
            "monte": "monte",
            "baisse": "baisse",
            "monte de": "monte",
            "baisse de": "baisse",
            "monte tout en haut": "monte_tout_en_haut",
            "baisse tout en bas": "baisse_tout_en_bas",
            # Terminal
            "terminal": "new_terminal",
            "dernier terminal": "last_terminal",
            # Fichiers
            "nouveau dossier": "new_folder",
            "nouveau fichier": "new_file",
            "ouvre fichier": "open_file",
            "ouvre dossier": "open_folder",
            "explore": "show_explorer",
            "onglet suivant": "onglet_suivant",
            "onglet précédent": "onglet_precedent",
            # Contrôle IA - Souris
            "prompt": "cline_trigger",
            "prompt accepte": "cline_accept",
            "prompt refuse": "cline_reject",
            # Contrôle IA - Clavier
            "accepte": "accepte",
            "refuse": "refuse",
            # Autres
            "ouvre": "open_item",
            "écoute": "listen",
            "stop": "stop",
            "arrête": "stop",
            "annule": "cancel",
            "annuler": "cancel",
        }

    def get_wake_word(self):
        """Récupère le mot déclencheur"""
        return self.wake_word

    def set_wake_word(self, word):
        """Modifie le mot déclencheur"""
        self.wake_word = word.lower()
        self.save_settings()

    def get_voice_command(self, command):
        """Récupère une commande vocale"""
        return self.voice_commands.get(command)

    def set_voice_command(self, phrase, action):
        """Modifie une commande vocale"""
        self.voice_commands[phrase.lower()] = action
        self.save_settings()

    def update_mouse_position(self, position_name, coordinates):
        """Met à jour une position de souris"""
        MOUSE_POSITIONS[position_name] = coordinates
        self.save_settings()

    def update_shortcut(self, shortcut_name, keys):
        """Met à jour un raccourci clavier"""
        SHORTCUTS[shortcut_name] = keys
        self.save_settings()

    def get_mouse_position(self, position_name):
        """Récupère une position de souris"""
        return MOUSE_POSITIONS.get(
            position_name, DEFAULT_MOUSE_POSITIONS.get(position_name)
        )

    def get_shortcut(self, shortcut_name):
        """Récupère un raccourci clavier"""
        return SHORTCUTS.get(shortcut_name, self.default_shortcuts.get(shortcut_name))
