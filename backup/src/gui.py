import customtkinter as ctk
from queue import Queue
from threading import Thread
from src.constants import COLORS
from src.settings_manager import SettingsManager
from src.settings_dialog import SettingsDialog
from pynput.mouse import Button, Listener as MouseListener


class ScrollableFrame(ctk.CTkScrollableFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grid_columnconfigure(0, weight=1)


class CommandCategory(ctk.CTkFrame):
    def __init__(self, master, title, commands, icon="", **kwargs):
        super().__init__(
            master, fg_color=COLORS["textbox_bg"], corner_radius=8, **kwargs
        )

        # Grid configuration
        self.grid_columnconfigure(1, weight=1)

        # Header with icon
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(
            row=0, column=0, columnspan=2, sticky="ew", padx=15, pady=(10, 5)
        )

        if icon:
            icon_label = ctk.CTkLabel(
                header_frame,
                text=icon,
                font=("Helvetica", 16),
                text_color=COLORS["primary"],
            )
            icon_label.pack(side="left", padx=(0, 8))

        title_label = ctk.CTkLabel(
            header_frame,
            text=title,
            font=("Helvetica", 16, "bold"),
            text_color=COLORS["text"],
        )
        title_label.pack(side="left")

        # Commands
        for i, (command, description) in enumerate(commands.items()):
            cmd_frame = ctk.CTkFrame(self, fg_color="transparent")
            cmd_frame.grid(
                row=i + 1, column=0, columnspan=2, sticky="ew", padx=15, pady=2
            )

            cmd = ctk.CTkLabel(
                cmd_frame,
                text=command,
                font=("Helvetica", 14),
                text_color=COLORS["primary"],
            )
            cmd.pack(side="left")

            desc = ctk.CTkLabel(
                cmd_frame,
                text=f"→ {description}",
                font=("Helvetica", 14),
                text_color=COLORS["text_secondary"],
            )
            desc.pack(side="left", padx=(8, 0))


class VoiceAssistantGUI:
    def __init__(
        self,
        toggle_listening_callback,
        save_audio_preferences_callback,
        get_audio_devices_callback,
        keyboard_controller,
    ):
        """Initialisation de l'interface"""
        self.toggle_listening_callback = toggle_listening_callback
        self.save_audio_preferences_callback = save_audio_preferences_callback
        self.get_audio_devices_callback = get_audio_devices_callback
        self.keyboard_controller = keyboard_controller
        self.settings_manager = None

        self.update_queue = Queue()
        self.setup_gui()
        self.start_update_loop()

    def start_update_loop(self):
        """Démarre la boucle de mise à jour de l'interface"""

        def check_queue():
            try:
                while not self.update_queue.empty():
                    update_func, args, kwargs = self.update_queue.get_nowait()
                    update_func(*args, **kwargs)
            except Exception as e:
                print(f"Erreur lors du traitement des mises à jour: {str(e)}")
            finally:
                # Schedule next check
                self.window.after(100, check_queue)

        # Start first check
        self.window.after(100, check_queue)

    def queue_update(self, func, *args, **kwargs):
        self.update_queue.put((func, args, kwargs))

    def update_status(self, is_active=False, is_processing=False):
        if is_processing:
            color = COLORS["primary"]
            text = "Traitement en cours..."
        elif is_active:
            color = COLORS["status_active"]
            text = "En écoute"
        else:
            color = COLORS["status_inactive"]
            text = "En attente"

        def update():
            self.status_indicator.configure(text_color=color)
            self.status_text.configure(text=text)

        self.queue_update(update)

    def log(self, message):
        def update():
            import time

            self.logs.insert("end", f"{time.strftime('%H:%M:%S')} - {message}\n")
            self.logs.see("end")

        self.queue_update(update)

    def open_settings(self):
        if not self.settings_manager:
            self.log("Erreur: Gestionnaire de paramètres non initialisé")
            return

        settings_dialog = SettingsDialog(
            self.window, self.settings_manager, self.keyboard_controller
        )
        settings_dialog.focus()

    def update_toggle_button(self, is_listening):
        if is_listening:
            self.toggle_button.configure(
                text="⏹️ Arrêter",
                fg_color=COLORS["error"],
                hover_color=COLORS["primary_hover"],
                text_color=COLORS["text"],
            )
        else:
            self.toggle_button.configure(
                text="🎤 Démarrer",
                fg_color=COLORS["primary"],
                hover_color=COLORS["primary_hover"],
                text_color=COLORS["text"],
            )

    def setup_gui(self):
        self.window = ctk.CTk()
        self.window.title("Assistant Vocal VS Code")
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.window.minsize(1200, 800)
        ctk.set_appearance_mode("dark")

        self.window.configure(fg_color=COLORS["bg"])
        self.window.attributes("-alpha", 0.98)
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=1)

        # Header
        header_frame = ctk.CTkFrame(
            self.window,
            fg_color=COLORS["gradient_dark"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
        )
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        header_frame.grid_columnconfigure(1, weight=1)

        # Title and status
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="w", padx=20)

        title = ctk.CTkLabel(
            title_frame,
            text="🎙️ Assistant Vocal VS Code",
            font=("Helvetica", 28, "bold"),
            text_color=COLORS["text"],
        )
        title.pack(side="left")

        self.status_indicator = ctk.CTkLabel(
            title_frame,
            text="●",
            font=("Helvetica", 28),
            text_color=COLORS["status_inactive"],
            width=40,
        )
        self.status_indicator.pack(side="left", padx=(12, 0))

        # Control buttons
        control_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        control_frame.grid(row=0, column=1, sticky="e", padx=20)

        settings_button = ctk.CTkButton(
            control_frame,
            text="⚙️ Paramètres",
            command=self.open_settings,
            width=120,
            height=40,
            font=("Helvetica", 14),
            fg_color=COLORS["secondary_bg"],
            hover_color=COLORS["highlight"],
            text_color=COLORS["text"],
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border"],
        )
        settings_button.pack(side="left", padx=(0, 10))

        self.toggle_button = ctk.CTkButton(
            control_frame,
            text="🎤 Démarrer",
            command=self.toggle_listening_callback,
            width=160,
            height=40,
            font=("Helvetica", 14, "bold"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            text_color=COLORS["text"],
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border"],
        )
        self.toggle_button.pack(side="left")

        # Main content
        main_scroll = ScrollableFrame(
            self.window,
            fg_color="transparent",
            corner_radius=0,
        )
        main_scroll.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))

        # Audio device section
        audio_frame = ctk.CTkFrame(
            main_scroll,
            fg_color=COLORS["gradient_dark"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
        )
        audio_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        audio_frame.grid_columnconfigure(1, weight=1)

        audio_label = ctk.CTkLabel(
            audio_frame,
            text="🎙️ Périphérique Audio",
            font=("Helvetica", 16, "bold"),
            text_color=COLORS["text"],
        )
        audio_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        input_devices = self.get_audio_devices_callback()
        self.input_menu = ctk.CTkOptionMenu(
            audio_frame,
            values=input_devices,
            command=self.save_audio_preferences_callback,
            width=300,
            height=40,
            font=("Helvetica", 14),
            fg_color=COLORS["textbox_bg"],
            button_color=COLORS["textbox_bg"],
            button_hover_color=COLORS["highlight"],
            dropdown_fg_color=COLORS["textbox_bg"],
            dropdown_hover_color=COLORS["highlight"],
            text_color=COLORS["text"],
            dropdown_text_color=COLORS["text"],
            corner_radius=8,
        )
        self.input_menu.grid(row=0, column=1, padx=20, pady=15, sticky="e")
        self.input_menu.set("Défaut")

        # Commands section header
        commands_header = ctk.CTkFrame(main_scroll, fg_color="transparent")
        commands_header.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        commands_header.grid_columnconfigure(1, weight=1)

        commands_title = ctk.CTkLabel(
            commands_header,
            text="📝 Commandes Disponibles",
            font=("Helvetica", 20, "bold"),
            text_color=COLORS["text"],
        )
        commands_title.grid(row=0, column=0, sticky="w")

        commands_tip = ctk.CTkLabel(
            commands_header,
            text="🗣️ Dites 'Jarvis' suivi de votre commande",
            font=("Helvetica", 14),
            text_color=COLORS["text_secondary"],
        )
        commands_tip.grid(row=0, column=1, sticky="e")

        # Commands categories in a grid layout
        categories_frame = ctk.CTkFrame(main_scroll, fg_color="transparent")
        categories_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        categories_frame.grid_columnconfigure((0, 1), weight=1)

        # Dictation commands
        dictation_commands = {
            "écoute": "active la dictée continue",
            "stop/arrête": "arrête la dictée",
            "annule": "annule la saisie en cours",
        }
        dictation_category = CommandCategory(
            categories_frame, "Dictée", dictation_commands, icon="🗣️"
        )
        dictation_category.grid(
            row=0, column=0, sticky="ew", padx=(0, 10), pady=(0, 10)
        )

        # Text Operations commands
        text_commands = {
            "formater": "active/désactive le retour à la ligne (Alt+Z)",
            "cherche le mot [mot]": "recherche le mot spécifié (Ctrl+F)",
            "mot suivant": "passe à l'occurrence suivante (Entrée)",
            "mot précédent": "passe à l'occurrence précédente (Shift+Entrée)",
            "choisis le mot": "quitte la recherche (Échap)",
            "ligne X": "va à la ligne spécifiée",
            "ligne X à Y": "indente les lignes spécifiées",
            "tout le fichier": "indente tout le fichier",
        }
        text_category = CommandCategory(
            categories_frame, "Opérations sur le Texte", text_commands, icon="📝"
        )
        text_category.grid(row=0, column=1, sticky="ew", pady=(0, 10))

        # Navigation commands
        navigation_commands = {
            "monte": "monte d'une page",
            "baisse": "descend d'une page",
            "monte de X": "monte de X pages",
            "baisse de X": "descend de X pages",
            "monte tout en haut": "va au début du fichier",
            "baisse tout en bas": "va à la fin du fichier",
            "accepte": "accepte la suggestion et sauvegarde",
            "refuse": "refuse la suggestion et sauvegarde",
            "onglet suivant": "passe à l'onglet suivant",
            "onglet suivant X": "passe X onglets vers la droite",
            "onglet précédent": "passe à l'onglet précédent",
            "onglet précédent X": "passe X onglets vers la gauche",
        }
        navigation_category = CommandCategory(
            categories_frame, "Navigation", navigation_commands, icon="🔍"
        )
        navigation_category.grid(row=1, column=0, sticky="ew", padx=(0, 10))

        # Commandes Menu IA
        ai_commands = {
            "ia": "ouvre le Menu IA (clic aux coordonnées)",
            "ia commande": "ouvre le prompt IA (clic aux coordonnées)",
            "ia accepte": "accepte la suggestion IA (clic aux coordonnées)",
            "ia refuse": "refuse la suggestion IA (clic aux coordonnées)",
        }
        ai_category = CommandCategory(
            categories_frame, "Menu IA", ai_commands, icon="🤖"
        )
        ai_category.grid(row=2, column=0, sticky="ew", padx=(0, 10))

        # Autres commandes
        other_commands = {
            "nouveau dossier": "crée un dossier (Ctrl+Shift+P → File: New Folder)",
            "nouveau fichier": "crée un fichier (Ctrl+Shift+P → File: New File)",
            "explore": "ouvre l'explorateur (Ctrl+Shift+E)",
            "ouvre X": "Focus sur l'explorateur et ouvre l'élément X (0 ou 1=premier, 2=deuxième, etc.)",
            "ouvre fichier": "ouvre la boîte de dialogue pour ouvrir un fichier (Ctrl+O)",
            "ouvre dossier": "ouvre la boîte de dialogue pour ouvrir un dossier (Ctrl+K Ctrl+O)",
            "terminal": "ouvre un nouveau terminal (Ctrl+Shift+ù)",
            "dernier terminal": "ouvre le dernier terminal (Ctrl+ù)",
            "sauvegarde": "sauvegarde le fichier (Ctrl+S)",
        }
        other_category = CommandCategory(
            categories_frame, "Autres Actions", other_commands, icon="🔧"
        )
        other_category.grid(row=2, column=1, sticky="ew")

        # Activity log
        logs_frame = ctk.CTkFrame(
            main_scroll,
            fg_color=COLORS["gradient_dark"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
        )
        logs_frame.grid(row=3, column=0, sticky="ew")
        logs_frame.grid_columnconfigure(0, weight=1)

        logs_label = ctk.CTkLabel(
            logs_frame,
            text="📋 Journal d'activité",
            font=("Helvetica", 20, "bold"),
            text_color=COLORS["text"],
        )
        logs_label.grid(row=0, column=0, sticky="w", padx=20, pady=10)

        self.logs = ctk.CTkTextbox(
            logs_frame,
            font=("Helvetica", 14),
            fg_color=COLORS["textbox_bg"],
            text_color=COLORS["text_secondary"],
            border_width=0,
            corner_radius=8,
            height=150,
        )
        self.logs.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))

        # Status
        self.status_text = ctk.CTkLabel(
            header_frame,
            text="En attente",
            font=("Helvetica", 14),
            text_color=COLORS["text_secondary"],
        )
        self.status_text.grid(row=0, column=2, padx=20)

    def set_settings_manager(self, settings_manager):
        self.settings_manager = settings_manager

    def run(self):
        self.window.mainloop()
