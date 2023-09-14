from discord.app_commands import AppCommandError


class PlayerNotFoundError(AppCommandError):
    """
    Minecraft user not found exception class\n
    Used for returning out of nested functions"""


class SessionNotFoundError(AppCommandError):
    """
    Session not found exception class\n
    Used for returning out of nested functions"""


class HypixelInvalidResponseError(AppCommandError):
    """Hypixel request timeout exception class."""


class HypixelRateLimitedError(AppCommandError):
    """Hypixel rate limit exception class"""


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


class MojangInvalidResponseError(AppCommandError):
    """Mojang invalid response error"""


class MojangRateLimitError(MojangInvalidResponseError):
    """Mojang rate limit error"""
