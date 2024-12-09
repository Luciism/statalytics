"""Useful functions for formatting strings."""

from datetime import timedelta


def fname(username: str):
    """Escapes underscore characters to bypass Discord's markdown."""
    return username.replace("_", r"\_")


def ordinal(n: int) -> str:  # pylint: disable=invalid-name
    """
    Formats a day of the month, for example `21` would be `21st`.

    :param n: The number to format.
    """
    if 4 <= n % 100 <= 20:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


def format_seconds(seconds):
    """
    Format a duration of seconds into a string such as `36 Mins`,
    `48 Hours`, or `12 Days`.

    :param seconds: The duration in seconds to format.
    """
    delta = timedelta(seconds=round(seconds))
    days = delta.days

    if days > 0:
        return f"{days} Day{'s' if days > 1 else ''}"

    hours = delta.seconds // 3600
    if hours > 0:
        return f"{hours} Hour{'s' if hours > 1 else ''}"

    minutes = (delta.seconds // 60) % 60
    return f"{minutes} Min{'s' if minutes > 1 else ''}"


def format_12hr_time(hour: int, minute: int) -> str:
    """Format time as hr:min(AM/PM)"""
    hour_12 = hour % 12
    hour_12 = 12 if hour_12 == 0 else hour_12

    period = "AM" if hour < 12 else "PM"
    return f"{hour_12}:{minute:02d}{period}"


def pluralize(number: int, word: str, suffix: str='s') -> str:
    """
    Pluralizes a word based on a given number.

    :param number: The number to determine whether to pluralize.
    :param word: The word to pluralize.
    :param suffix: The plural suffix to add to the word.
    """
    if number != 1:
        return f'{word}{suffix}'
    return word


def comma_separated_to_list(comma_seperated_list: str) -> list:
    """
    Converts a comma seperated list (string) to a list of strings.
    Example `"foo,bar"` -> `["foo", "bar"]`.

    :param comma_seperated_list: The comma seperated list of items.
    """
    if comma_seperated_list:
        return comma_seperated_list.split(',')
    return []


def prefix_int(integer: int | float) -> str:
    """
    Prefixes a given number with `+` or `-` and returns it as a string.

    :param integer: The integer to be prefixed.
    """
    prefix = "+" if integer >= 0 else ""
    return f'{prefix}{integer:,}'
