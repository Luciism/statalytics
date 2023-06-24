from discord.app_commands import AppCommandError


class MCUserNotFoundError(AppCommandError):
    """
    Minecraft user not found exception class\n
    Used for returning out of nested functions"""
    pass


class ThemeNotFoundError(Exception):
    """Theme not found exception class."""

    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message


class NoLinkedAccountError(Exception):
    """No linked account exception class."""

    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message
