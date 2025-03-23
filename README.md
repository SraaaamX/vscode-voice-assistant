# Assistant Vocal VS Code 🎙️

Un assistant vocal en français pour Visual Studio Code + Cline qui permet de contrôler l'éditeur avec des commandes vocales.

## 🌟 Fonctionnalités

- Contrôle vocal complet de VS Code
- Interface graphique moderne et intuitive
- Reconnaissance vocale en français
- Mode dictée pour la saisie de texte
- Navigation intelligente dans le code
- Intégration avec l'IA de VS Code
- Personnalisation des commandes vocales

## 🚀 Commandes Vocales

Toutes les commandes commencent par le mot d'activation "Jarvis" suivi de la commande.

### 🗣️ Dictée
- `écoute` - Active la dictée continue
- `stop/arrête` - Arrête la dictée
- `annule` - Annule la saisie en cours

### 📝 Opérations sur le Texte
- `formater` - Active/désactive le retour à la ligne (Alt+Z)
- `cherche le mot [mot]` - Recherche le mot spécifié (Ctrl+F)
- `mot suivant` - Passe à l'occurrence suivante
- `mot précédent` - Passe à l'occurrence précédente
- `choisis le mot` - Quitte la recherche
- `ligne X` - Va à la ligne spécifiée
- `ligne X à Y` - Indente les lignes spécifiées
- `tout le fichier` - Indente tout le fichier

### 🔍 Navigation
- `monte/baisse` - Monte/descend d'une page
- `monte/baisse de X` - Monte/descend de X pages
- `monte tout en haut` - Va au début du fichier
- `baisse tout en bas` - Va à la fin du fichier
- `accepte` - Accepte la suggestion et sauvegarde
- `refuse` - Refuse la suggestion et sauvegarde
- `onglet suivant/précédent` - Change d'onglet
- `onglet suivant/précédent X` - Change de X onglets

### 🤖 Menu IA
- `ia` - Ouvre le Menu IA
- `ia commande` - Ouvre le prompt IA
- `ia accepte` - Accepte la suggestion IA
- `ia refuse` - Refuse la suggestion IA

### 🔧 Autres Actions
- `nouveau dossier/fichier` - Crée un nouveau dossier/fichier
- `explore` - Ouvre l'explorateur
- `ouvre X` - Ouvre l'élément X dans l'explorateur
- `ouvre fichier/dossier` - Ouvre la boîte de dialogue pour ouvrir un fichier/dossier
- `terminal` - Ouvre un nouveau terminal
- `dernier terminal` - Ouvre le dernier terminal
- `sauvegarde` - Sauvegarde le fichier

## 💻 Installation

1. Assurez-vous d'avoir Python 3.x installé
2. Installez les dépendances :
```bash
pip install customtkinter speech_recognition pynput
```
3. Clonez le dépôt :
```bash
git clone <repository-url>
cd voice-assistant
```
4. Lancez l'application :
```bash
python voice_assistant.py
```

## 🏗️ Architecture

Le projet est structuré en plusieurs composants :

```
voice_assistant/
├── src/
│   ├── keyboard/           # Gestion des entrées clavier
│   ├── constants.py        # Constantes et configuration
│   ├── gui.py             # Interface graphique
│   ├── main.py            # Point d'entrée
│   ├── settings_dialog.py # Dialogue des paramètres
│   ├── settings_manager.py # Gestion des paramètres
│   ├── utils.py           # Fonctions utilitaires
│   └── voice_handler.py   # Traitement vocal
├── config.json            # Configuration utilisateur
└── voice_assistant.py     # Script de lancement
```

### Composants Principaux

- **VoiceHandler** : Gère la reconnaissance vocale et le traitement des commandes
- **VoiceAssistantGUI** : Interface utilisateur moderne avec customtkinter
- **KeyboardController** : Contrôle le clavier et la souris
- **SettingsManager** : Gère la configuration et les paramètres

## 🛠️ Dépendances

- Python 3.x
- customtkinter
- speech_recognition
- pynput
- pyaudio (requis par speech_recognition)