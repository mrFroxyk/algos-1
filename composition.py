""" Модуль композиции """
from typing import Self


class Composition():
    """ Класс композиции """
    def __init__(self, path: str):
        self.path = path

    def __eq__(self, other: Self) -> bool:
        if not other:
            return False

        return self.path == other.path
