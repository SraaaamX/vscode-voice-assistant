from pynput.keyboard import Key

# Configuration par défaut des positions de la souris
# Description des positions souris
MOUSE_DESCRIPTIONS = {
    "cline_trigger": "Position pour 'ia' (ouvrir Cline)",
    "cline_prompt_trigger": "Position pour 'ia prompt'",
    "cline_accept": "Position pour 'ia accepte' (clic de validation)",
    "cline_reject": "Position pour 'ia refuse' (clic de refus)",
}

DEFAULT_MOUSE_POSITIONS = {
    "cline_trigger": (35, 920),
    "cline_prompt_trigger": (141, 920),
    "cline_accept": (263, 920),
    "cline_reject": (385, 920),
}

# Configuration actuelle des positions (peut être modifiée)
MOUSE_POSITIONS = DEFAULT_MOUSE_POSITIONS.copy()

# Configuration des raccourcis clavier
SHORTCUTS = {
    "enter": ["enter"],  # Touche Entrée
    "esc": ["esc"],  # Touche Échap
    "command_palette": [Key.ctrl, Key.shift, "p"],  # Ctrl + Shift + P
    "new_terminal": [Key.ctrl, Key.shift, "ù"],  # Ctrl + Shift + ù (Nouveau terminal)
    "last_terminal": [Key.ctrl, "ù"],  # Ctrl + ù (Dernier terminal)
    # Navigation
    "monte": [Key.page_up],  # Page Up (Monter d'une page)
    "baisse": [Key.page_down],  # Page Down (Descendre d'une page)
    "monte_tout_en_haut": [Key.ctrl, Key.home],  # Ctrl + Home (Début du fichier)
    "baisse_tout_en_bas": [Key.ctrl, Key.end],  # Ctrl + End (Fin du fichier)
    # Raccourcis IA
    "accepte": [Key.alt, "a"],  # Alt + A
    "refuse": [Key.alt, "r"],  # Alt + R
    "sauvegarde": [Key.ctrl, "s"],  # Ctrl + S
    # Fichiers & Fenêtres
    "new_file": [Key.ctrl, Key.shift, "p"],  # Ctrl + Shift + P
    "new_folder": [Key.ctrl, Key.shift, "p"],  # Ctrl + Shift + P
    "show_explorer": [Key.ctrl, Key.shift, "e"],  # Ctrl + Shift + E
    "open_file": [Key.ctrl, "o"],  # Ctrl + O
    "open_folder": [Key.ctrl, "k", Key.ctrl, "o"],  # Ctrl + K Ctrl + O
    "onglet_suivant": [Key.ctrl, Key.page_down],  # Ctrl + Page Down
    "onglet_precedent": [Key.ctrl, Key.page_up],  # Ctrl + Page Up
    # Recherche et formatage
    "format_text": [Key.alt, "z"],  # Alt + Z
    "search_word": [Key.ctrl, "f"],  # Ctrl + F
    "word_next": ["enter"],  # Enter
    "word_prev": [Key.shift, "enter"],  # Shift + Enter
    "select_word": ["esc"],  # Escape
}

# Description des raccourcis pour l'interface
SHORTCUTS_DESCRIPTIONS = {
    # Navigation
    "monte": "Monter d'une page (Page Up)",
    "baisse": "Descendre d'une page (Page Down)",
    "monte_tout_en_haut": "Aller en haut du fichier (Ctrl+Home)",
    "baisse_tout_en_bas": "Aller en bas du fichier (Ctrl+End)",
    # Terminal
    "new_terminal": "Nouveau terminal (Ctrl+Shift+ù)",
    "last_terminal": "Dernier terminal utilisé (Ctrl+ù)",
    # IA
    "accepte": "Accepter la suggestion (Alt+A)",
    "refuse": "Refuser la suggestion (Alt+R)",
    "sauvegarde": "Sauvegarder (Ctrl+S)",
    # Fichiers & Fenêtres
    "command_palette": "Ouvrir la palette de commandes",
    "new_folder": "Nouveau dossier (via palette)",
    "new_file": "Nouveau fichier (via palette)",
    "show_explorer": "Ouvrir l'explorateur (Ctrl+Shift+E)",
    "open_file": "Ouvrir un fichier (Ctrl+O)",
    "open_folder": "Ouvrir un dossier (Ctrl+K Ctrl+O)",
    "onglet_suivant": "Onglet suivant (Ctrl+PageUp)",
    "onglet_precedent": "Onglet précédent (Ctrl+PageDown)",
    # Recherche et formatage
    "format_text": "Formater le texte (Alt+Z)",
    "search_word": "Rechercher un mot (Ctrl+F)",
    "word_next": "Occurrence suivante (Entrée)",
    "word_prev": "Occurrence précédente (Shift+Entrée)",
    "select_word": "Quitter la recherche (Échap)",
    # Commandes Générales
    "enter": "Valider (Entrée)",
    "esc": "Annuler/Quitter (Échap)",
}

# Schéma de couleurs de l'application

# Schéma de couleurs de l'application
COLORS = {
    "bg": "#0A0A0A",
    "secondary_bg": "#121212",
    "gradient_dark": "#0F0F0F",
    "gradient_light": "#1A1A1A",
    "primary": "#FF3737",
    "primary_hover": "#FF5C5C",
    "text": "#FFFFFF",
    "text_secondary": "#A0A0A0",
    "border": "#2A2A2A",
    "border_focus": "#3A3A3A",
    "success": "#36B37E",
    "error": "#FF5630",
    "blur_bg": "#121212",
    "textbox_bg": "#1A1A1A",
    "highlight": "#252525",
    "status_active": "#36B37E",
    "status_inactive": "#FF5630",
    "command_hover": "#252525",
    "separator": "#2A2A2A",
}
