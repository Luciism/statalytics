"""String splitting utilities."""

import re


def split_string(input_string: str, split_chars: tuple | list) -> list[tuple[str, str]]:
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

    # Find the splits and their codes
    parts = re.split(f"({pattern})", input_string)
    if not parts:
        return [(input_string, '')]

    result = []
    current_code = ''
    for part in parts:
        if part in split_chars:
            current_code = part
        else:
            result.append((part, current_code))
            current_code = ''  # reset only if you want new code to apply per block

    # remove any empty initial tuple if nothing before first code
    if result and result[0][0] == '' and result[0][1] == '':
        result.pop(0)

    return result
