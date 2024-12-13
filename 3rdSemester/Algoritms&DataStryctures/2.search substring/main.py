import pathlib

import click

import search
from hightlighting import aplly_hightlights, calculate_color_segment
from timer import timer


@click.command()
@click.argument(
    'string',
    type=str,
)
@click.option(
    '--sub-string',
    '-s',
    multiple=True,
    required=True,
    help="List of substrings to search for.",
)
@click.option(
    '--case-sensitivity',
    is_flag=True,
    help="Case-sensitive search.",
)
@click.option(
    '--method',
    type=click.Choice(search.Method, case_sensitive=False),
    default=search.Method.FIRST,
    help="Search method: first or last occurrence.",
)
@click.option(
    '--count',
    type=int,
    help="Number of occurrences to return.",
)
@click.option(
    '--file',
    type=click.Path(exists=True),
    help="Path to a txt file. Only first 10 lines will be processed.",
)
@timer
def main(
    string: str,
    sub_string: list[str],
    case_sensitivity: bool,
    method: search.Method,
    count:int,
    file: pathlib.Path,
):
    """Start CLI tool to highlight substrings in a given string."""
    if file:
        print("First 10 file line analyze:")  # noqa: T201
        file_path = pathlib.Path(file)

        if file_path.is_file():
            with file_path.open('r', encoding='utf-8') as f:
                lines = f.readlines()[:10]

            for line in lines:
                pre_segments = search.search(
                    string=line.strip(),
                    sub_string=sub_string,
                    case_sensitivity=case_sensitivity,
                    method=method,
                    count=count,
                )
                segments = calculate_color_segment(pre_segments)
                highlighted_string = aplly_hightlights(line.strip(), segments)
                print(highlighted_string) # noqa: T201

    if string:
        print("\n" + "String analyze:")  # noqa: T201
        pre_segments = search.search(
            string=string,
            sub_string=sub_string,
            case_sensitivity=case_sensitivity,
            method=method,
            count=count,
        )

        if isinstance(pre_segments, tuple):
            pre_segments = {sub_string[0]: pre_segments}
            segments = calculate_color_segment(pre_segments)
        else:
            segments = calculate_color_segment(pre_segments)

        highlighted_string = aplly_hightlights(string, segments)
        print(highlighted_string) # noqa: T201

if __name__ == "__main__":
    main()
