import re


def split_string(input_string: str, split_chars: tuple | list):
    """
    Splits string at all specified values and returns both
    split list and values the string was split at
    :param input_string: the string to split
    :param split_chars: the characters to split the string at

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
    matches = [match.group(1) for match in match_posses if match.group(1)]

    values = re.findall(pattern, input_string)

    # If the string doesn't start with a split character,
    # add a dummy value at the beginning of 'values' list.
    if not input_string.startswith(tuple(split_chars)):
        values.insert(0, '')

    return zip(matches, values)
