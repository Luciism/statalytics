"""Common error classes."""

from discord.app_commands import AppCommandError


class PlayerNotFoundError(AppCommandError):
    """
    Minecraft user not found exception class.
    Used for returning out of nested functions.
    """


class SessionNotFoundError(AppCommandError):
    """
    Session not found exception class.
    Used for returning out of nested functions.
    """


class HypixelInvalidResponseError(AppCommandError):
    """Hypixel request timeout exception class."""


class HypixelRateLimitedError(AppCommandError):
    """Hypixel rate limit exception class."""


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
    """Mojang invalid response error."""


class MojangRateLimitError(MojangInvalidResponseError):
    """Mojang rate limit error."""


class UserBlacklistedError(AppCommandError):
    """User is blacklisted error."""

class MissingPermissionsError(AppCommandError):
    """User is missing required error."""

class DataNotFoundError(Exception):
    """Expected data was not found in the database."""
