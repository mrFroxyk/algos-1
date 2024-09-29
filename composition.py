"""Модуль композиции"""
from typing import Self


class Composition:
    """Класс композиции"""

    def __init__(self, path: str):
        self.path = path

    def __eq__(self, other) -> bool:
        if not other:
            return False

        if not isinstance(other, Composition):
            return False

        return self.path == other.path
