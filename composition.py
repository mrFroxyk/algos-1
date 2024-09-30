from typing import Self


class Composition:
    """Composition class."""

    def __init__(self, path: str) -> None:
        self.path = path

    def __eq__(self, other: Self) -> bool:
        """Check if two compositions are equal."""
        if not other:
            return False

        if not isinstance(other, Composition):
            return False

        return self.path == other.path
