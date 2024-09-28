""" Модуль плейлиста """
import pygame
from linked_list import LinkedList
from composition import Composition


class Playlist(LinkedList):
    """ Класс плейлиста """
    def __init__(self, data = None):
        super().__init__(data)
        self._current = None

    def play_all(self, track) -> Composition:
        """ Проигрывать все треки с начала """
        self._current = track
        pygame.mixer.music.load(self.current.path)
        pygame.mixer.music.play()

    def next_track(self) -> Composition:
        """ Перейти к следующему треку """
        if self._current:
            self.play_all(self._current.next_item)

    def previous_track(self) -> Composition:
        """ Перейти к предыдущему треку """
        if self._current:
            self.play_all(self._current.previous_item)

    @property
    def current(self):
        """ Возвращает текущий трек """
        if not self._current:
            return None

        return self._current.data

    @current.setter
    def current(self, current) -> None:
        self._current = current
