def convert_french_number(text):
    """Convertit un nombre en lettres ou en chiffres vers un entier"""
    number_words = {
        "zéro": 0,
        "un": 1,
        "une": 1,
        "deux": 2,
        "trois": 3,
        "quatre": 4,
        "cinq": 5,
        "six": 6,
        "sept": 7,
        "huit": 8,
        "neuf": 9,
        "dix": 10,
        "onze": 11,
        "douze": 12,
        "treize": 13,
        "quatorze": 14,
        "quinze": 15,
        "seize": 16,
        "vingt": 20,
        "trente": 30,
        "quarante": 40,
        "cinquante": 50,
        "soixante": 60,
        "soixante-dix": 70,
        "quatre-vingt": 80,
        "quatre-vingt-dix": 90,
        "cent": 100,
    }

    # Si c'est déjà un chiffre, le convertir directement
    if text.isdigit():
        return int(text)

    # Sinon, chercher dans le dictionnaire des nombres en lettres
    text = text.lower()
    if text in number_words:
        return number_words[text]

    # Gestion des cas composés
    if "soixante-et-onze" in text:
        return 71
    elif text.startswith("quatre-vingt-"):
        units = text.split("-")[-1]
        if units in number_words:
            return 80 + number_words[units]
    elif text.startswith("soixante-"):
        units = text.split("-")[-1]
        if units in number_words:
            return 60 + number_words[units]

    # Si aucune conversion possible, lever une exception
    raise ValueError(f"Impossible de convertir '{text}' en nombre")


def extract_number_from_text(text):
    """Extrait et convertit un nombre d'un texte, qu'il soit en chiffres ou en lettres"""
    words = text.split()
    for word in words:
        try:
            return convert_french_number(word)
        except ValueError:
            continue
    return None  # Si aucun nombre n'est trouvé
