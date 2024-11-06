from colorama import Fore, Style


def color_generator() -> str:
    """Return new color every time was calling."""
    colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE]
    while True:
        yield from colors

get_color = color_generator()


def aplly_hightlights(source_string: str, segments: dict[str, list[list[int]]]) -> str:
    r"""Return source string with the hightlighting.

    Example of segments:
    [[7, 8, '\x1b[31m'], [4, 5, '\x1b[31m'], [2, 3, '\x1b[32m']]
    """
    # sorted by the start insex
    sorted_segments = sorted(segments, key=lambda x: x[0])
    for index, segment in enumerate(sorted_segments[:-1]):
        start, end, color = segment
        next_segment_start = sorted_segments[index+1][0]

        if end >= next_segment_start:
            segment[1] = next_segment_start -1

    highlighted_string = []
    last_index = 0
    for start, end, color in sorted_segments:
        highlighted_string.append(source_string[last_index:start])
        highlighted_string.append(color + source_string[start:end + 1] + Style.RESET_ALL)
        last_index = end + 1
    highlighted_string.append(source_string[last_index:])

    return "".join(highlighted_string)


def calculate_color_segment(
    sub_string_indexes: dict[str, list[list[int]]],
) -> list[tuple[int | str]]:
    """Calculate segment to hightlighting.

    Example of segments:
    segments = {
        "sub_string_1": [[0,0], [4,5]],
        "sub_string_1": [[2,3]]
    }
    """
    result = []
    for key in sub_string_indexes:
        start_indexes = sub_string_indexes[key]
        color = next(get_color)
        sub_string_value = len(key)
        for start_index in start_indexes:
            segment = [start_index, start_index + sub_string_value - 1, color]
            result.append(segment)
    return result

