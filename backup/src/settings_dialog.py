import customtkinter as ctk
from src.constants import (
    COLORS,
    MOUSE_POSITIONS,
    DEFAULT_MOUSE_POSITIONS,
    SHORTCUTS_DESCRIPTIONS,
)
from pynput.mouse import Button, Listener as MouseListener
from pynput.keyboard import (
    Key,
    Controller as KeyboardController,
    Listener as KeyboardListener,
)
import threading
import time


class CaptureDialog(ctk.CTkToplevel):
    def __init__(self, parent, callback, duration=5):
        super().__init__(parent)
        self.callback = callback
        self.duration = duration
        self.current_keys = []
        self.remaining_time = duration

        self.title("Capture de raccourci")
        self.geometry("500x300")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        # Center window
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 500) // 2
        y = (screen_height - 300) // 2
        self.geometry(f"+{x}+{y}")

        # Visual configuration
        self.configure(fg_color=COLORS["gradient_dark"])
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Main container for better spacing
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(2, weight=1)

        # Enhanced header
        title = ctk.CTkLabel(
            main_container,
            text="⌨️ Capture de Raccourci",
            font=("Helvetica", 24, "bold"),
            text_color=COLORS["primary"],
        )
        title.grid(row=0, column=0, sticky="w", pady=(0, 10))

        # More descriptive subtitle
        subtitle = ctk.CTkLabel(
            main_container,
            text="Appuyez sur la combinaison de touches souhaitée\nÉchap pour annuler",
            font=("Helvetica", 14),
            text_color=COLORS["text_secondary"],
        )
        subtitle.grid(row=1, column=0, pady=(0, 20))

        # Visual key display container
        key_display = ctk.CTkFrame(
            main_container,
            fg_color=COLORS["secondary_bg"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
        )
        key_display.grid(row=2, column=0, sticky="ew", pady=15, ipady=10)
        key_display.grid_columnconfigure(0, weight=1)

        self.keys_label = ctk.CTkLabel(
            key_display,
            text="En attente des touches...",
            font=("Helvetica", 18, "bold"),
            text_color=COLORS["text"],
        )
        self.keys_label.grid(row=0, column=0, pady=10)

        # Timer with progress
        timer_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        timer_frame.grid(row=3, column=0, sticky="ew", pady=(20, 0))
        timer_frame.grid_columnconfigure(1, weight=1)

        self.timer_label = ctk.CTkLabel(
            timer_frame,
            text=f"{self.duration}s",
            font=("Helvetica", 16),
            text_color=COLORS["text_secondary"],
        )
        self.timer_label.grid(row=0, column=0, padx=(0, 10))

        self.progress = ctk.CTkProgressBar(
            timer_frame,
            mode="determinate",
            progress_color=COLORS["primary"],
            fg_color=COLORS["secondary_bg"],
        )
        self.progress.grid(row=0, column=1, sticky="ew")
        self.progress.set(1)

        self.update_timer()
        self.start_listener()

    def update_timer(self):
        if self.remaining_time > 0:
            self.timer_label.configure(text=f"{self.remaining_time}s")
            self.progress.set(self.remaining_time / self.duration)
            self.remaining_time -= 1
            self.after(1000, self.update_timer)
        else:
            if self.current_keys:
                self.finish_capture()
            else:
                self.current_keys = []
                self.finish_capture()

    def start_listener(self):
        def on_press(key):
            if key == Key.esc:
                self.current_keys = []
                self.finish_capture()
                return False

            try:
                key_name = key.char
            except AttributeError:
                key_name = key.name if hasattr(key, "name") else str(key)

            self.current_keys.append(key_name)
            keys_text = " + ".join(self.current_keys)
            self.keys_label.configure(
                text=keys_text if keys_text else "En attente des touches..."
            )

        def on_release(key):
            return True

        self.keyboard_listener = KeyboardListener(
            on_press=on_press, on_release=on_release
        )
        self.keyboard_listener.start()

    def finish_capture(self):
        if hasattr(self, "keyboard_listener"):
            self.keyboard_listener.stop()
        self.grab_release()
        self.callback(self.current_keys)
        self.destroy()


class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent, settings_manager, keyboard_controller):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.keyboard_controller = keyboard_controller
        self.parent = parent

        self.transient(parent)
        self.grab_set()

        self.title("Paramètres")
        self.geometry("900x700")
        self.minsize(900, 700)

        # Center on screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 900) // 2
        y = (screen_height - 700) // 2
        self.geometry(f"+{x}+{y}")

        self.configure(fg_color=COLORS["gradient_dark"])
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Enhanced header with search (future feature)
        header = ctk.CTkFrame(self, fg_color=COLORS["gradient_dark"], height=80)
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 0))
        header.grid_columnconfigure(1, weight=1)
        header.grid_propagate(False)

        title = ctk.CTkLabel(
            header,
            text="⚙️ Paramètres",
            font=("Helvetica", 28, "bold"),
            text_color=COLORS["text"],
        )
        title.grid(row=0, column=0, sticky="w", padx=10)

        # Main container with enhanced tabs
        self.tab_view = ctk.CTkTabview(
            self,
            fg_color=COLORS["secondary_bg"],
            segmented_button_fg_color=COLORS["gradient_dark"],
            segmented_button_selected_color=COLORS["primary"],
            segmented_button_selected_hover_color=COLORS["primary_hover"],
            text_color=COLORS["text"],
        )
        self.tab_view.grid(row=1, column=0, sticky="nsew", padx=30, pady=20)
        # Make tab view use all available space
        self.tab_view.grid_columnconfigure(0, weight=1)
        self.tab_view.grid_rowconfigure(0, weight=1)

        # Tabs with icons and better spacing
        self.shortcuts_tab = self.tab_view.add("⌨️  Raccourcis")
        self.shortcuts_tab.grid_columnconfigure(0, weight=1)
        self.create_shortcuts_tab(self.shortcuts_tab)

        self.mouse_tab = self.tab_view.add("🎯  Positions")
        self.mouse_tab.grid_columnconfigure(0, weight=1)
        self.create_mouse_tab(self.mouse_tab)

        # Footer with action buttons
        footer = ctk.CTkFrame(self, fg_color="transparent", height=70)
        footer.grid(row=2, column=0, sticky="ew", padx=30, pady=(0, 20))
        footer.grid_columnconfigure(1, weight=1)
        footer.grid_propagate(False)

        reset_button = ctk.CTkButton(
            footer,
            text="↺ Réinitialiser l'onglet",
            command=self.reset_settings,
            width=180,
            height=45,
            font=("Helvetica", 14),
            fg_color=COLORS["gradient_light"],
            hover_color=COLORS["command_hover"],
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border"],
        )
        reset_button.grid(row=0, column=0, padx=(0, 10))

        save_button = ctk.CTkButton(
            footer,
            text="💾 Sauvegarder",
            command=self.save_settings,
            width=180,
            height=45,
            font=("Helvetica", 14, "bold"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            corner_radius=8,
        )
        save_button.grid(row=0, column=2, padx=(10, 0))

    def create_shortcuts_tab(self, parent):
        """Creates the keyboard shortcuts interface"""
        # Enhanced description
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(20, 5))
        header.grid_columnconfigure(0, weight=1)

        description = ctk.CTkLabel(
            header,
            text="Personnalisez vos raccourcis clavier pour une navigation plus efficace",
            font=("Helvetica", 14),
            text_color=COLORS["text_secondary"],
        )
        description.grid(row=0, column=0, sticky="w")

        # Scrollable container for shortcuts
        # Make parent use all available space
        parent.grid_rowconfigure(1, weight=1)

        # Configure scrollable frame to fill parent
        shortcuts_frame = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
        )
        shortcuts_frame.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        shortcuts_frame.grid_columnconfigure(0, weight=1)

        # Configure the scrollable frame's parent frame to expand
        shortcuts_frame._parent_frame.grid_columnconfigure(0, weight=1)
        shortcuts_frame._parent_frame.grid_rowconfigure(0, weight=1)

        # Make groups expand horizontally
        groups = {
            "Navigation": [
                "monte",
                "baisse",
                "monte_tout_en_haut",
                "baisse_tout_en_bas",
                "onglet_suivant",
                "onglet_precedent",
                "accepte",
                "refuse",
            ],
            "Recherche et formatage": [
                "format_text",
                "search_word",
                "word_next",
                "word_prev",
                "select_word",
            ],
            "Terminal": ["new_terminal", "last_terminal", "show_explorer"],
            "Fichiers": [
                "new_folder",
                "new_file",
                "open_file",
                "open_folder",
                "command_palette",
            ],
            "Général": ["enter", "esc", "sauvegarde"],
        }

        self.shortcut_entries = {}
        row = 0

        for group_name, shortcuts in groups.items():
            # Group container
            group_container = ctk.CTkFrame(
                shortcuts_frame,
                fg_color=COLORS["secondary_bg"],
                corner_radius=12,
                border_width=1,
                border_color=COLORS["border"],
            )
            group_container.grid(row=row, column=0, sticky="ew", pady=10, padx=2)
            group_container.grid_columnconfigure(0, weight=1)

            # Group header
            group_header = ctk.CTkFrame(
                group_container,
                fg_color=COLORS["gradient_dark"],
                corner_radius=12,
                height=50,
            )
            group_header.grid(row=0, column=0, sticky="ew", padx=2, pady=2)
            group_header.grid_propagate(False)
            group_header.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                group_header,
                text=f"📑  {group_name}",
                font=("Helvetica", 16, "bold"),
                text_color=COLORS["primary"],
            ).grid(row=0, column=0, sticky="w", padx=15)

            # Shortcuts container
            shortcuts_container = ctk.CTkFrame(
                group_container,
                fg_color="transparent",
            )
            shortcuts_container.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
            shortcuts_container.grid_columnconfigure(1, weight=1)

            for i, shortcut_name in enumerate(shortcuts):
                if shortcut_name not in SHORTCUTS_DESCRIPTIONS:
                    continue

                # Action container with hover effect
                action_frame = ctk.CTkFrame(
                    shortcuts_container,
                    fg_color="transparent",
                    height=45,
                )
                action_frame.grid(row=i, column=0, columnspan=2, sticky="ew", pady=3)
                action_frame.grid_columnconfigure(1, weight=1)
                action_frame.grid_propagate(False)

                # Description
                desc_label = ctk.CTkLabel(
                    action_frame,
                    text=SHORTCUTS_DESCRIPTIONS[shortcut_name],
                    font=("Helvetica", 13),
                    text_color=COLORS["text"],
                )
                desc_label.grid(row=0, column=0, sticky="w", padx=15)

                # Wider shortcut button
                current = self.settings_manager.get_shortcut(shortcut_name)
                current_text = (
                    " + ".join(str(k) for k in current)
                    if isinstance(current, list)
                    else str(current)
                )

                entry = ctk.CTkButton(
                    action_frame,
                    text=current_text,
                    font=("Helvetica", 13),
                    width=250,
                    height=35,
                    fg_color=COLORS["textbox_bg"],
                    text_color=COLORS["text"],
                    hover_color=COLORS["command_hover"],
                    corner_radius=6,
                    border_width=1,
                    border_color=COLORS["border"],
                    command=lambda n=shortcut_name: self.start_shortcut_capture(n),
                )
                entry.grid(row=0, column=1, sticky="e", padx=15)
                self.shortcut_entries[shortcut_name] = entry

            row += 1

    def start_shortcut_capture(self, shortcut_name):
        def on_capture_complete(keys):
            if keys:
                self.settings_manager.update_shortcut(shortcut_name, keys)
                self.shortcut_entries[shortcut_name].configure(text=" + ".join(keys))
            else:
                current = self.settings_manager.get_shortcut(shortcut_name)
                current_text = (
                    " + ".join(str(k) for k in current)
                    if isinstance(current, list)
                    else str(current)
                )
                self.shortcut_entries[shortcut_name].configure(text=current_text)

        capture_dialog = CaptureDialog(self, on_capture_complete)
        capture_dialog.focus()

    def create_mouse_tab(self, parent):
        # Make parent use all available space
        parent.grid_rowconfigure(1, weight=1)

        # Enhanced header
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(20, 5))
        header.grid_columnconfigure(0, weight=1)

        description = ctk.CTkLabel(
            header,
            text="Définissez les positions où l'assistant cliquera automatiquement",
            font=("Helvetica", 14),
            text_color=COLORS["text_secondary"],
        )
        description.grid(row=0, column=0, sticky="w")

        # Scrollable container for positions
        positions_frame = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
        )
        positions_frame.grid(row=1, column=0, sticky="nsew", pady=(10, 0))

        # Configure the scrollable frame's parent frame to expand
        positions_frame._parent_frame.grid_columnconfigure(0, weight=1)
        positions_frame._parent_frame.grid_rowconfigure(0, weight=1)
        positions_frame.grid_columnconfigure(0, weight=1)

        self.position_buttons = {}

        # Positions groups with better organization
        groups = {
            "Menu IA": {
                "cline_trigger": "Position pour 'jarvis ia' (ouvrir l'IA)",
                "cline_prompt_trigger": "Position pour 'jarvis ia commande'",
                "cline_accept": "Position pour 'jarvis ia accepte'",
                "cline_reject": "Position pour 'jarvis ia refuse'",
            },
        }

        row = 0
        for group_name, positions in groups.items():
            # Group container
            group_container = ctk.CTkFrame(
                positions_frame,
                fg_color=COLORS["secondary_bg"],
                corner_radius=12,
                border_width=1,
                border_color=COLORS["border"],
            )
            group_container.grid(row=row, column=0, sticky="ew", pady=10, padx=2)
            group_container.grid_columnconfigure(0, weight=1)

            # Group header
            group_header = ctk.CTkFrame(
                group_container,
                fg_color=COLORS["gradient_dark"],
                corner_radius=12,
                height=50,
            )
            group_header.grid(row=0, column=0, sticky="ew", padx=2, pady=2)
            group_header.grid_propagate(False)
            group_header.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                group_header,
                text=f"🎯  {group_name}",
                font=("Helvetica", 16, "bold"),
                text_color=COLORS["primary"],
            ).grid(row=0, column=0, sticky="w", padx=15)

            # Positions container
            positions_container = ctk.CTkFrame(
                group_container,
                fg_color="transparent",
            )
            positions_container.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
            positions_container.grid_columnconfigure(1, weight=1)

            for i, (pos_name, desc) in enumerate(positions.items()):
                # Position frame
                pos_frame = ctk.CTkFrame(
                    positions_container,
                    fg_color="transparent",
                    height=45,
                )
                pos_frame.grid(row=i, column=0, columnspan=2, sticky="ew", pady=2)
                pos_frame.grid_columnconfigure(1, weight=1)
                pos_frame.grid_propagate(False)

                # Description
                ctk.CTkLabel(
                    pos_frame,
                    text=desc,
                    font=("Helvetica", 13),
                    text_color=COLORS["text"],
                ).grid(row=0, column=0, sticky="w", padx=15)

                # Position button
                current_pos = self.settings_manager.get_mouse_position(pos_name)
                button = ctk.CTkButton(
                    pos_frame,
                    text=f"📍  ({current_pos[0]}, {current_pos[1]})",
                    command=lambda p=pos_name: self.start_position_config(p),
                    width=180,
                    height=35,
                    font=("Helvetica", 13),
                    fg_color=COLORS["primary"],
                    hover_color=COLORS["primary_hover"],
                    corner_radius=6,
                )
                button.grid(row=0, column=1, sticky="e", padx=15)
                self.position_buttons[pos_name] = button

            row += 1

    def start_position_config(self, position_name):
        button = self.position_buttons[position_name]
        button.configure(
            text="🎯 Cliquez à l'endroit souhaité...",
            fg_color=COLORS["command_hover"],
        )

        # Enhanced visual indicator
        indicator = ctk.CTkToplevel()
        indicator.attributes("-topmost", True)
        indicator.overrideredirect(True)
        indicator.configure(fg_color=COLORS["gradient_dark"])
        indicator.geometry("300x60")

        indicator_content = ctk.CTkFrame(
            indicator,
            fg_color=COLORS["secondary_bg"],
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border"],
        )
        indicator_content.pack(expand=True, fill="both", padx=2, pady=2)

        ctk.CTkLabel(
            indicator_content,
            text="🎯 Cliquez n'importe où pour définir la position\nÉchap pour annuler",
            font=("Helvetica", 13),
            text_color=COLORS["text"],
        ).pack(expand=True, fill="both", padx=10)

        # Fade effect
        windows_to_fade = [self, self.parent]
        for window in windows_to_fade:
            if not hasattr(window, "_original_alpha"):
                window._original_alpha = window.attributes("-alpha")
            window.attributes("-alpha", 0.2)

        # Center indicator
        screen_width = indicator.winfo_screenwidth()
        screen_height = indicator.winfo_screenheight()
        x = (screen_width - 300) // 2
        y = 50
        indicator.geometry(f"+{x}+{y}")

        self._temp_indicator = indicator

        def on_click(x, y, button, pressed):
            if pressed:
                if hasattr(self, "_temp_indicator"):
                    self._temp_indicator.destroy()
                    delattr(self, "_temp_indicator")
                self.after(
                    0, lambda: self._handle_position_click(position_name, (x, y))
                )
                return False
            return True

        self.mouse_listener = MouseListener(on_click=on_click)
        self.mouse_listener.start()

        def cleanup(event=None):
            if hasattr(self, "_temp_indicator"):
                self._temp_indicator.destroy()
                delattr(self, "_temp_indicator")
            for window in windows_to_fade:
                if hasattr(window, "_original_alpha"):
                    window.attributes("-alpha", window._original_alpha)
                    delattr(window, "_original_alpha")

        indicator.bind("<Escape>", cleanup)

    def _handle_position_click(self, position_name, coordinates):
        button = self.position_buttons[position_name]
        button.configure(
            text=f"📍  ({coordinates[0]}, {coordinates[1]})",
            fg_color=COLORS["primary"],
        )

        self._temp_positions = getattr(self, "_temp_positions", {})
        self._temp_positions[position_name] = coordinates

        def restore_window(window, target_alpha, delay_ms=0):
            steps = 20
            current = float(window.attributes("-alpha"))
            step_size = (target_alpha - current) / steps
            duration_per_step = 25

            def step(remaining_steps, current_alpha):
                if remaining_steps > 0:
                    next_alpha = current_alpha + step_size
                    window.attributes("-alpha", next_alpha)
                    window.after(
                        duration_per_step, lambda: step(remaining_steps - 1, next_alpha)
                    )
                elif delay_ms > 0 and window == self:
                    self.after(delay_ms, self._restore_window_focus)

            window.after(delay_ms, lambda: step(steps, current))

        for i, window in enumerate([self.parent, self]):
            if hasattr(window, "_original_alpha"):
                restore_window(window, window._original_alpha, i * 100)
                delattr(window, "_original_alpha")

    def _restore_window_focus(self):
        self.lift()
        self.focus_force()
        self.attributes("-topmost", True)
        self.after(100, lambda: self.attributes("-topmost", False))

    def reset_shortcuts(self):
        for shortcut_name, button in self.shortcut_entries.items():
            default = self.settings_manager.default_shortcuts[shortcut_name]
            text = (
                " + ".join(str(k) for k in default)
                if isinstance(default, list)
                else str(default)
            )
            button.configure(text=text)
        self.settings_manager.reset_shortcuts()

    def reset_mouse_positions(self):
        for pos_name, button in self.position_buttons.items():
            default_pos = DEFAULT_MOUSE_POSITIONS[pos_name]
            button.configure(
                text=f"📍  ({default_pos[0]}, {default_pos[1]})",
                fg_color=COLORS["primary"],
            )
        self._temp_positions = {}
        self.settings_manager.reset_mouse_positions()

    def reset_settings(self):
        current_tab = self.tab_view.get()
        if "Raccourcis" in current_tab:
            self.reset_shortcuts()
        elif "Positions" in current_tab:
            self.reset_mouse_positions()

    def save_settings(self):
        if hasattr(self, "_temp_positions"):
            for pos_name, coords in self._temp_positions.items():
                self.settings_manager.update_mouse_position(pos_name, coords)
        self.grab_release()
        self.destroy()
