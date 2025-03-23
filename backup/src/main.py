import os
from src.gui import VoiceAssistantGUI
from src.voice_handler import VoiceHandler
from src.keyboard.controller import KeyboardController
from src.settings_manager import SettingsManager


def create_assistant():
    """Crée et configure l'assistant vocal"""
    try:
        # S'assure que le dossier de travail est correct
        os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        # Initialise les composants dans le bon ordre
        keyboard_controller = KeyboardController()
        settings_manager = SettingsManager()

        # Crée le gestionnaire vocal avec les dépendances nécessaires
        voice_handler = VoiceHandler(
            keyboard_controller=keyboard_controller, settings_manager=settings_manager
        )

        # Fonction de basculement de l'écoute
        def toggle_listening(gui):
            if voice_handler.is_listening:
                voice_handler.stop_listening()
                gui.update_status(is_active=False)
                gui.update_toggle_button(False)
            else:
                voice_handler.start_listening()
                gui.update_status(is_active=True)
                gui.update_toggle_button(True)

        # Crée l'interface graphique
        gui = VoiceAssistantGUI(
            toggle_listening_callback=lambda: toggle_listening(gui),
            save_audio_preferences_callback=voice_handler.set_audio_device,
            get_audio_devices_callback=voice_handler.get_audio_devices,
            keyboard_controller=keyboard_controller,
        )

        # Configure les callbacks de l'interface
        voice_handler.update_status = gui.update_status
        voice_handler.log = gui.log

        # Configure le gestionnaire de paramètres dans l'interface
        gui.set_settings_manager(settings_manager)

        return gui, settings_manager

    except Exception as e:
        print(f"Erreur lors de l'initialisation: {str(e)}")
        raise


def main():
    """Point d'entrée principal"""
    try:
        gui, settings_manager = create_assistant()
        try:
            gui.run()
        finally:
            settings_manager.save_settings()
    except Exception as e:
        print(f"\nErreur lors du démarrage: {str(e)}")
        raise


if __name__ == "__main__":
    main()
