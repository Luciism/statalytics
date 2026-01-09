"""Common error classes."""


class PlayerNotFoundError(Exception):
    """
    Minecraft user not found exception class.
    Used for returning out of nested functions.
    """


class SessionNotFoundError(Exception):
    """
    Session not found exception class.
    Used for returning out of nested functions.
    """


class HypixelInvalidResponseError(Exception):
    """Hypixel request timeout exception class."""


class HypixelRateLimitedError(Exception):
    """Hypixel rate limit exception class."""


class ThemeNotFoundError(Exception):
    """Theme not found exception class."""


class ThemeUnavailableError(Exception):
    """The theme not available to a user."""

class NoLinkedAccountError(Exception):
    """No linked account exception class."""


class MojangInvalidResponseError(Exception):
    """Mojang invalid response error."""


class MojangRateLimitError(MojangInvalidResponseError):
    """Mojang rate limit error."""


class UserBlacklistedError(Exception):
    """User is blacklisted error."""

class MissingPermissionsError(Exception):
    """User is missing required error."""

class DataNotFoundError(Exception):
    """Expected data was not found in the database."""

class BackgroundPropertiesNotFoundError(Exception):
    """No properties were found for the provided background ID."""
