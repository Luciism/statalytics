"""String splitting utilities."""

import re


def split_string(
    input_string: str,
    split_chars: tuple | list
) -> list[tuple[str, str]]:
    """
    Split a string at all specified substrings and returns both
    split list with their respective substrings.

    :param input_string: The string to split.
    :param split_chars: The characters to split the string at.
    :return: A list of tuples containing the split substrings.

    Example usage:
    ```python
    >>> input_string = "Hello &aWorld &bPython &cProgramming"
    >>> split_chars = ["&a", "&b", "&c"]
    >>> results = split_string(input_string, split_chars)
    >>> tuple(results)
    (('Hello ', ''), ('World ', '&a'), ('Python ', '&b'), ('Programming', '&c'))
    ```
    """
    pattern = '|'.join(map(re.escape, split_chars))

    # Extract the matched substrings from the match_posses and filter out empty strings
    match_posses = re.finditer(f"(.*?)(?:{pattern}|$)", input_string)
    matches = [match.group(1) for i, match in enumerate(match_posses) if i != 0]

    values = re.findall(pattern, input_string)

    # If the string doesn't start with a split character,
    # add a dummy value at the beginning of 'values' list.
    if not input_string.startswith(tuple(split_chars)):
        values.insert(0, '')

    return zip(matches, values)
