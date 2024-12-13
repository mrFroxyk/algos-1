from enum import StrEnum


class Method(StrEnum):
    """Search method."""

    FIRST = "first"
    LAST = "last"



def search(
        string: str,
        sub_string: str | list[str],
        case_sensitivity: bool = False,
        method: str=Method.FIRST,
        count: int | None=None,
    ) -> tuple[int, ...] | dict[str, tuple[int, ...]]:
        """Search sunstring(s) in string."""
        if isinstance(sub_string, str):
            sub_string = [sub_string]

        # case sensitivity logic
        string = string.upper() if not case_sensitivity else string

        result = {}

        for sb_string in sub_string:
            # case sensitivity logic
            case_sb_strint = sb_string.upper() if not case_sensitivity else sb_string
            result[sb_string] = single_search(
                string,
                case_sb_strint,
                method,
                count,
            )

        # If we have only one sub string we must returnt just turple
        if len(result) == 1:
            result = next(iter(result.values()))
            return result
        # Else we must return dict with turples
        return result


def compute_prefix(sub_string: str):
    """Compute the longest proper prefix which is also a suffix (LPS array).

    :param sub_string: sub_string string.
    :return: LPS array.
    """
    lps = [0] * len(sub_string)
    length = 0
    i = 1

    while i < len(sub_string):
        if sub_string[i] == sub_string[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1

    return lps


def single_search(
        string: str,
        sub_string: str,
        method: str = 'first',
        count: int | None = None,
    ) -> tuple[int, ...] | None:
    """Search for occurrences of the sub_string in the string using KMP algorithm.

    :param string: The main string where we search.
    :param sub_string: The substring we are searching for.
    :return: Starting indices where the sub_string is found in the string.
    """
    lps = compute_prefix(sub_string)
    i = 0  # index for string
    j = 0  # index for sub_string
    result = []
    cur_count = 0

    # Reverse strings if the search method is 'last'
    if method == 'last':
        string = string[::-1]
        sub_string = sub_string[::-1]

    while i < len(string):
        if string[i] == sub_string[j]:
            i += 1
            j += 1

        if j == len(sub_string):
            result.append(i - j)
            cur_count += 1
            j = lps[j - 1]
            if count and cur_count == count:
                break

        elif i < len(string) and string[i] != sub_string[j]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1

    # If the method is 'last', reverse the result indices back
    if method == 'last':
        result = [len(string) - ans - len(sub_string) for ans in result[::-1]][::-1]

    return tuple(result)
