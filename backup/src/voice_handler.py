import speech_recognition as sr
from threading import Thread
import time
import re
from pynput.keyboard import Key
from pynput.mouse import Button
from src.utils import extract_number_from_text


class VoiceHandler:
    def __init__(
        self,
        keyboard_controller,
        settings_manager,
        update_status_callback=None,
        log_callback=None,
    ):
        """Initialisation du gestionnaire vocal"""
        self.keyboard_controller = keyboard_controller
        self.settings_manager = settings_manager
        self.update_status = update_status_callback or (lambda *args, **kwargs: None)
        self.log = log_callback or (lambda *args, **kwargs: None)

        self.recognizer = sr.Recognizer()

        # Optimisation des paramètres audio
        self.recognizer.pause_threshold = 0.3
        self.recognizer.phrase_threshold = 0.1
        self.recognizer.non_speaking_duration = 0.3
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.energy_threshold = 600

        self.audio_device = None
        self.is_listening = False
        self.dictation_mode = False
        self.search_mode = False  # New flag for search mode
        self.listening_thread = None

    def get_audio_devices(self):
        """Retourne la liste des périphériques audio disponibles"""
        devices = ["Défaut"]
        try:
            devices.extend(sr.Microphone.list_microphone_names())
        except Exception as e:
            self.log(f"Erreur lors de la récupération des périphériques: {str(e)}")
        return devices

    def set_audio_device(self, device_name):
        """Configure le périphérique audio à utiliser"""
        try:
            if device_name == "Défaut":
                self.audio_device = None
            else:
                devices = sr.Microphone.list_microphone_names()
                device_index = devices.index(device_name)
                self.audio_device = device_index - 1
            self.log(f"Périphérique audio configuré: {device_name}")
        except Exception as e:
            self.log(f"Erreur lors de la configuration du périphérique: {str(e)}")

    def handle_command_action(self, action, args=None):
        """Gère les actions des commandes vocales"""
        if action == "monte":
            self.keyboard_controller.press_keys([Key.page_up])
        elif action == "baisse":
            self.keyboard_controller.press_keys([Key.page_down])
        elif action == "monte_tout_en_haut":
            self.keyboard_controller.press_keys([Key.ctrl, Key.home])
        elif action == "baisse_tout_en_bas":
            self.keyboard_controller.press_keys([Key.ctrl, Key.end])
        elif action == "new_terminal":
            self.keyboard_controller.press_keys([Key.ctrl, Key.shift, "ù"])
        elif action == "last_terminal":
            self.keyboard_controller.press_keys([Key.ctrl, "ù"])
        elif action == "new_file":
            self.keyboard_controller.press_keys([Key.ctrl, Key.shift, "p"])
            self.keyboard_controller.type_text("File: New File", add_enter=True)
        elif action == "new_folder":
            self.keyboard_controller.press_keys([Key.ctrl, Key.shift, "p"])
            self.keyboard_controller.type_text("File: New Folder", add_enter=True)
        elif action in [
            "cline_trigger",
            "cline_prompt_trigger",
            "cline_accept",
            "cline_reject",
        ]:
            pos = self.settings_manager.get_mouse_position(action)
            try:
                # Déplacement et clic instantanés
                self.keyboard_controller.move_mouse_to(pos[0], pos[1])
                self.keyboard_controller.click_mouse(Button.left)
                self.log(f"Clic effectué à la position {pos}")
            except Exception as e:
                self.log(f"Erreur lors du clic souris : {e}")
        elif action == "show_explorer":
            self.keyboard_controller.press_keys([Key.ctrl, Key.shift, "e"])
        elif action == "onglet_suivant":
            count = 1
            if args:
                try:
                    count = extract_number_from_text(args) or 1
                except ValueError:
                    count = 1
            self.keyboard_controller.next_file(count)
            self.log(f"Navigation vers l'onglet suivant ({count} fois)")
        elif action == "onglet_precedent":
            count = 1
            if args:
                try:
                    count = extract_number_from_text(args) or 1
                except ValueError:
                    count = 1
            self.keyboard_controller.previous_file(count)
            self.log(f"Navigation vers l'onglet précédent ({count} fois)")
        elif action == "open_item":
            try:
                if args:
                    num = extract_number_from_text(args)
                    if num:
                        self._navigate_to_explorer_item(num)
            except ValueError:
                self.log("Numéro d'élément non valide")
        elif action == "accepte":
            self.keyboard_controller.press_keys([Key.alt, "a"])
            self.keyboard_controller.press_keys([Key.ctrl, "s"])
            self.log("Suggestion acceptée et sauvegardée")
        elif action == "refuse":
            self.keyboard_controller.press_keys([Key.alt, "r"])
            self.keyboard_controller.press_keys([Key.ctrl, "s"])
            self.log("Suggestion refusée et sauvegardée")
        elif action == "sauvegarde":
            self.keyboard_controller.press_keys([Key.ctrl, "s"])
            self.log("Fichier sauvegardé")
        elif action == "listen":
            self.dictation_mode = True
            self.log("Mode dictée activé")
        elif action == "stop":
            if self.dictation_mode:
                self.dictation_mode = False
                self.log("Mode dictée désactivé")
            else:
                self.keyboard_controller.press_keys([Key.esc])
        elif action == "cancel":
            self.keyboard_controller.press_keys([Key.esc])
        elif action == "format_text":
            self.keyboard_controller.press_keys([Key.alt, "z"])
        elif action == "search_word":
            self.keyboard_controller.press_keys([Key.ctrl, "f"])
            if args:
                self.keyboard_controller.type_text(args.strip(), add_enter=False)
            self.search_mode = True
        elif action == "word_next":
            self.keyboard_controller.press_keys(["enter"])
        elif action == "word_prev":
            self.keyboard_controller.press_keys([Key.shift, "enter"])
        elif action == "select_word":
            self.keyboard_controller.press_keys([Key.esc])
            self.search_mode = False
        elif action == "open_file":
            self.keyboard_controller.press_keys([Key.ctrl, "o"])
        elif action == "open_folder":
            self.keyboard_controller.press_keys([Key.ctrl, "k"])
            time.sleep(0.1)  # Small delay between key combinations
            self.keyboard_controller.press_keys([Key.ctrl, "o"])

    def process_command(self, command, source):
        """Traite une commande vocale"""
        try:
            command = command.lower().strip()
            self.log(f"Commande reçue: {command}")

            # If in search mode, type letters directly
            if self.search_mode:
                if len(command) == 1:  # Single letter
                    self.keyboard_controller.type_text(command, add_enter=False)
                    return
                else:  # Check for commands that might exit search mode
                    action = self.settings_manager.get_voice_command(command)
                    if action == "exit_search":
                        self.handle_command_action(action)
                        return

            # Check for "ouvre X" command to navigate explorer
            if command.startswith("ouvre "):
                num = extract_number_from_text(command[len("ouvre ") :])
                if num is not None:
                    self._navigate_to_explorer_item(num)
                    return

            # Check for monte/baisse commands
            if command == "monte":
                self.handle_command_action("monte")
                return
            elif command == "baisse":
                self.handle_command_action("baisse")
                return

            # Check for "monte/baisse de X" commands
            if command.startswith("monte de "):
                try:
                    num = extract_number_from_text(command[len("monte de ") :])
                    if num:
                        for _ in range(num):
                            self.handle_command_action("monte")
                    return
                except ValueError:
                    pass
            elif command.startswith("baisse de "):
                try:
                    num = extract_number_from_text(command[len("baisse de ") :])
                    if num:
                        for _ in range(num):
                            self.handle_command_action("baisse")
                    return
                except ValueError:
                    pass

            # Vérifie les commandes vocales configurées
            command_action = None
            command_args = None

            # Vérifie les correspondances exactes
            action = self.settings_manager.get_voice_command(command)
            if action:
                command_action = action
            else:
                # Vérifie les commandes qui commencent par une phrase
                for phrase, act in self.settings_manager.voice_commands.items():
                    if command.startswith(phrase):
                        command_action = act
                        command_args = command[len(phrase) :].strip()
                        break

            if command_action:
                self.handle_command_action(command_action, command_args)
                return

            # Gestion des commandes spéciales
            if "tout le fichier" in command:
                self.keyboard_controller.press_keys([Key.ctrl, "a"])
                self.indent_selection_with_voice(source)
                return

            # Navigation par numéro de ligne
            if "ligne" in command:
                parts = command.split("à")
                try:
                    if len(parts) == 2:  # Plage de lignes
                        start_text = parts[0].replace("ligne", "").strip()
                        end_text = parts[1].strip()
                        start_line = extract_number_from_text(start_text)
                        end_line = extract_number_from_text(end_text)

                        if not start_line or not end_line:
                            self.log("Numéros de ligne non valides")
                            return

                        if start_line < 1:
                            self.log(
                                "Numéro de ligne invalide: doit être supérieur à 0"
                            )
                            return

                        if end_line < start_line:
                            self.log(
                                "La ligne de fin doit être supérieure à la ligne de début"
                            )
                            return

                        # Aller au début du fichier
                        self.keyboard_controller.press_keys([Key.ctrl, Key.home])

                        # Aller à la première ligne
                        for _ in range(start_line - 1):
                            self.keyboard_controller.press_keys([Key.down])

                        # Sélectionner jusqu'à la dernière ligne
                        self.keyboard_controller.keyboard.press(Key.shift)
                        for _ in range(end_line - start_line + 1):
                            self.keyboard_controller.press_keys([Key.down])
                        self.keyboard_controller.keyboard.release(Key.shift)

                        self.indent_selection_with_voice(source)
                    else:  # Ligne simple
                        line_text = command.replace("ligne", "").strip()
                        line_num = extract_number_from_text(line_text)

                        if not line_num:
                            self.log("Numéro de ligne non valide")
                            return

                        if line_num < 1:
                            self.log(
                                "Numéro de ligne invalide: doit être supérieur à 0"
                            )
                            return

                        # Aller au début du fichier
                        self.keyboard_controller.press_keys([Key.ctrl, Key.home])

                        # Aller à la ligne spécifiée
                        for _ in range(line_num - 1):
                            self.keyboard_controller.press_keys([Key.down])
                except ValueError:
                    self.log("Numéro de ligne non valide")
                return

            # Si en mode dictée, écrire le texte
            if self.dictation_mode:
                self.keyboard_controller.type_text(command + " ", add_enter=False)
                if command in ["stop", "arrête"]:
                    self.keyboard_controller.press_keys([Key.enter])
                    self.dictation_mode = False
                    self.log("Mode dictée désactivé")
                return

            self.log("Commande non reconnue")

        except Exception as e:
            self.log(f"Erreur lors du traitement de la commande: {str(e)}")

    def continuous_listening(self, source):
        """Mode de dictée continue"""
        self.log(
            f"Mode dictée activé - dites '{self.settings_manager.get_wake_word()} stop' pour arrêter"
        )
        max_retries = 3
        retry_count = 0

        while True:
            try:
                self.update_status(is_active=True)
                audio = self.recognizer.listen(source)
                self.update_status(is_processing=True)
                text = self.recognizer.recognize_google(audio, language="fr-FR")
                text_lower = text.lower().strip()
                retry_count = 0

                wake_word = self.settings_manager.get_wake_word()
                if wake_word in text_lower:
                    if "stop" in text_lower or "arrête" in text_lower:
                        self.keyboard_controller.press_keys([Key.enter])
                        self.log("Mode dictée désactivé")
                        break
                    elif "écoute" in text_lower or "annule" in text_lower:
                        continue
                else:
                    cleaned_text = " ".join(
                        word
                        for word in text.split()
                        if word.lower() != self.settings_manager.get_wake_word()
                    )
                    if cleaned_text:
                        self.keyboard_controller.type_text(
                            cleaned_text + " ", add_enter=False
                        )
                        self.log(f"Transcrit: {cleaned_text}")

            except sr.UnknownValueError:
                retry_count += 1
                if retry_count >= max_retries:
                    self.log(
                        "Plusieurs échecs de reconnaissance consécutifs, mode dictée désactivé"
                    )
                    break
                continue
            except sr.RequestError:
                self.log("Erreur de connexion au service de reconnaissance vocale")
                break
            except Exception as e:
                self.log(f"Erreur pendant la dictée: {str(e)}")
                break
            finally:
                self.update_status(is_processing=False)

    def indent_selection_with_voice(self, source):
        """Indente la sélection et attend une saisie vocale"""
        self.keyboard_controller.press_keys([Key.ctrl, "i"])
        try:
            self.update_status(is_active=True)
            audio = self.recognizer.listen(source)
            self.update_status(is_processing=True)
            text = self.recognizer.recognize_google(audio, language="fr-FR")
            text_lower = text.lower()

            wake_word = self.settings_manager.get_wake_word()
            if wake_word in text_lower and (
                "annule" in text_lower or "annuler" in text_lower
            ):
                self.keyboard_controller.press_keys([Key.esc])
                self.log("Indentation annulée (Échap)")
            else:
                self.log(f"Texte saisi: {text}")
                self.keyboard_controller.type_text(text, add_enter=False)
                self.keyboard_controller.press_keys([Key.enter])

        except sr.UnknownValueError:
            self.log("Aucun texte détecté")
        except sr.RequestError:
            self.log("Erreur de connexion au service de reconnaissance vocale")
        except Exception as e:
            self.log(f"Erreur: {str(e)}")
        finally:
            self.update_status(is_active=False)

    def listen_loop(self):
        """Boucle principale d'écoute des commandes"""
        try:
            with sr.Microphone(device_index=self.audio_device) as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
                self.log("Calibration du bruit ambiant effectuée")

                while self.is_listening:
                    try:
                        self.update_status(is_active=True)
                        self.log("En écoute...")
                        audio = self.recognizer.listen(source)
                        self.update_status(is_processing=True)
                        text = self.recognizer.recognize_google(audio, language="fr-FR")
                        text_lower = text.lower().strip()

                        wake_word = self.settings_manager.get_wake_word()
                        if wake_word in text_lower:
                            cmd = text_lower.split(wake_word, 1)[1].strip()
                            self.log(f"Texte reçu: {text_lower}")
                            self.log(f"Commande extraite: {cmd}")

                            if cmd == "écoute":
                                self.continuous_listening(source)
                            elif cmd:
                                self.process_command(cmd, source)

                        self.update_status(is_active=True, is_processing=False)

                    except sr.UnknownValueError:
                        self.update_status(is_processing=False)
                        continue
                    except sr.RequestError:
                        self.log(
                            "Erreur de connexion au service de reconnaissance vocale"
                        )
                    except Exception as e:
                        self.log(f"Erreur: {str(e)}")
                    finally:
                        if not self.is_listening:
                            break

        except Exception as e:
            self.log(f"Erreur d'initialisation du microphone: {str(e)}")
        finally:
            self.update_status(is_active=False)

    def start_listening(self):
        """Démarre l'écoute vocale"""
        if not self.is_listening:
            self.is_listening = True
            self.dictation_mode = False
            self.search_mode = False
            self.listening_thread = Thread(target=self.listen_loop)
            self.listening_thread.start()

    def _navigate_to_explorer_item(self, num):
        """Navigate to and select an item in the explorer by number"""
        # 1. Make sure explorer is visible
        self.keyboard_controller.press_keys([Key.ctrl, Key.shift, "e"])
        time.sleep(0.2)  # Wait for explorer to show

        # 2. Open command palette
        self.keyboard_controller.press_keys([Key.ctrl, Key.shift, "p"])
        time.sleep(0.1)  # Wait for palette
        # 3. Type and execute explorer focus command
        self.keyboard_controller.type_text(
            "File: Files: Focus on Explorer", add_enter=True
        )
        time.sleep(0.3)  # Wait for focus

        # 3. Always make sure we're at the very top by pressing Home multiple times
        for _ in range(3):  # Press Home key 3 times to ensure we're at the top
            self.keyboard_controller.press_keys([Key.home])
            time.sleep(0.1)  # Wait between each Home press

        # 4. Adjust navigation index (0 and 1 mean first item, 2 means second item, etc.)
        nav_index = max(0, num - 1)

        # 5. Navigate if needed
        if nav_index > 0:
            for _ in range(nav_index):
                self.keyboard_controller.press_keys([Key.down])
                time.sleep(0.05)  # Tiny delay for reliability

        # 5. Select with Enter
        self.keyboard_controller.press_keys([Key.enter])
        self.log(f"Navigation à l'élément {num} dans l'explorateur")

    def stop_listening(self):
        """Arrête l'écoute vocale"""
        self.is_listening = False
        self.dictation_mode = False
        self.search_mode = False
        if self.listening_thread and self.listening_thread.is_alive():
            self.listening_thread.join(timeout=1)
        if self.update_status:
            self.update_status(is_active=False)
        self.log("Écoute vocale désactivée")
