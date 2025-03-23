class MousePositionError(Exception):
    """Exception levée en cas d'erreur avec les positions de la souris"""

    pass


class MouseConfigurationError(MousePositionError):
    """Exception levée quand une position de souris n'est pas configurée"""

    def __init__(self, position_name):
        self.position_name = position_name
        super().__init__(f"La position '{position_name}' n'est pas configurée")
