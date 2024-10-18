from colorama import Fore, Style, init


def color_generator() -> str:
    """Return new color every time was calling."""
    colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE]
    while True:
        for color in colors:
            yield color
get_color = color_generator()


def aplly_hightlights(source_string: str, segments: dict[str, list[list[int]]]) -> str:
    """Return source string with the hightlighting.

    Example of segments:
    segments = {
        "sub_string_1": [[0,0], [4,5]],
        "sub_string_1": [[2,3]]
    }
    """
    result = []
    for key in segments:
        one_color_segments = segments[key]
        color = next(get_color)
        for segment in one_color_segments:
            segment.append(color)
            result.append(segment)

    # sorted by the start insex
    sorted_segments = sorted(result, key=lambda x: x[0])

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


source_string = "01234567"
segments = {
    "1": [[0,0], [4,5]],
    "2": [[2,3]]
}
print(aplly_hightlights(source_string, segments))