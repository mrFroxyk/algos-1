"""Модуль интерфейса"""
import os
import sys

import pygame
from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QInputDialog,
    QListWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from composition import Composition
from playlist import Playlist


class MusicPlayer(QWidget):
    """Окно музыкального плеера"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Music Player")
        self.setGeometry(100, 100, 400, 400)
        self.current_playlist = None
        self.playlist_objects = []

        pygame.mixer.init()

        self.selected_song_index = None

        self.layout = QVBoxLayout()

        self.add_playlist_button = QPushButton("Добавить плейлист")
        self.add_playlist_button.clicked.connect(self.create_new_playlist_dialog)
        self.layout.addWidget(self.add_playlist_button)

        self.remove_playlist_button = QPushButton("Удалить плейлист")
        self.remove_playlist_button.clicked.connect(self.delete_playlist)
        self.layout.addWidget(self.remove_playlist_button)

        self.playlist_combobox = QComboBox()
        self.playlist_combobox.currentIndexChanged.connect(self.on_select_playlist_from_combobox)
        self.layout.addWidget(self.playlist_combobox)

        self.playlist_widget = QListWidget()
        self.layout.addWidget(self.playlist_widget)

        self.add_button = QPushButton("Добавить композицию")
        self.add_button.clicked.connect(self.add_song)
        self.layout.addWidget(self.add_button)

        self.remove_button = QPushButton("Удалить композицию")
        self.remove_button.clicked.connect(self.remove_song)
        self.layout.addWidget(self.remove_button)

        self.play_button = QPushButton("Играть")
        self.play_button.clicked.connect(self.choose_song)
        self.layout.addWidget(self.play_button)

        self.prev_button = QPushButton("Предыдущая")
        self.prev_button.clicked.connect(self.play_previous)
        self.layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Следующая")
        self.next_button.clicked.connect(self.play_next)
        self.layout.addWidget(self.next_button)

        self.change_button = QPushButton("Изменить позицию")
        self.change_button.clicked.connect(self.change_position_dialogue)
        self.layout.addWidget(self.change_button)

        self.setLayout(self.layout)
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.next_track_if_this_ended)

    def create_new_playlist_dialog(self):
        """Открывает диалог для создания нового плейлиста"""
        name, ok = QInputDialog.getText(self, "Создать плейлист", "Введите название плейлиста:")

        if ok and name:
            if ',' in name:
                QMessageBox.warning(self, "Ошибка", "Название плейлиста не должно содержать запятую.")
                return

            if get_playlist_object_by_name(name, self.playlist_objects):
                QMessageBox.warning(self, "Ошибка", "Плейлист с таким названием уже существует.")
                return

            # Создаем новый плейлист и добавляем его в список
            self.playlist_objects.append({
                "name": name,
                "playlist": Playlist(),
            })

            self.playlist_combobox.addItem(name)

    def delete_playlist(self):
        """Удаляет выбранный плейлист"""
        current_name = self.playlist_combobox.currentText()

        if not current_name:
            QMessageBox.warning(self, "Ошибка", "Выберите плейлист для удаления.")
            return

        # Подтверждение удаления
        reply = QMessageBox.question(
            self, "Удаление плейлиста",
            f"Вы уверены, что хотите удалить плейлист '{current_name}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            # Находим и удаляем плейлист
            playlist_object = get_playlist_object_by_name(current_name, self.playlist_objects)
            if playlist_object:
                self.playlist_objects.remove(playlist_object)
                self.playlist_combobox.removeItem(self.playlist_combobox.currentIndex())
                self.current_playlist = None
                self.playlist_widget.clear()
                QMessageBox.information(self, "Удаление", f"Плейлист '{current_name}' успешно удален.")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось найти плейлист для удаления.")

        # Если больше нет плейлистов, очищаем список
        if self.playlist_combobox.count() == 0:
            self.current_playlist = None
            self.playlist_widget.clear()

    def on_select_playlist_from_combobox(self):
        """Хендлер для выбора плейлиста из комбобокса."""
        current_name = self.playlist_combobox.currentText()
        playlist_object = get_playlist_object_by_name(current_name, self.playlist_objects)
        if playlist_object:
            self.current_playlist = playlist_object["playlist"]
            self.update_playlist_widget()

    def update_playlist_widget(self):
        """Обновляет виджет списка песен для текущего плейлиста."""
        self.playlist_widget.clear()
        if self.current_playlist:
            for node in self.current_playlist:
                self.playlist_widget.addItem(os.path.basename(node.data.path))

    def add_song(self):
        """Добавление песен."""
        if self.current_playlist is None:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите плейлист")
            return

        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(
            self, "Выберите музыкальные файлы", "", "Audio Files (*.mp3 *.wav)", options=options,
        )
        if files:
            for file in files:
                self.current_playlist.append(Composition(file))
                self.playlist_widget.addItem(os.path.basename(file))

    def remove_song(self):
        """Удаление песен."""
        selected_items = self.playlist_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите композицию для удаления.")
            return
        for item in selected_items:
            row = self.playlist_widget.row(item)
            if self.current_playlist.current == self.current_playlist[row]:
                self.current_playlist.current = None
                pygame.mixer.music.unload()
                pygame.mixer.music.stop()

            self.current_playlist.remove(self.current_playlist[row])
            self.playlist_widget.takeItem(row)

    def find_song_by_id(self, sid):
        """Поиск песни по id."""
        for idx, track in enumerate(self.current_playlist):
            if idx == sid:
                return track

        return None

    def play_song_by_id(self, sid):
        """Проигрывание песни по id."""
        track = self.find_song_by_id(sid)
        if track:
            self.current_playlist.play_all(track)
            self.timer.start()
        return

    def choose_song(self):
        """Проигрывание выбранной песни."""
        current_row = self.playlist_widget.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите композицию для воспроизведения.")
            return None

        if self.current_playlist[current_row] != self.current_playlist.current:
            return self.play_song_by_id(current_row)

    def play_previous(self):
        """Проигрывание предыдущей песни."""
        if self.current_playlist is None:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите плейлист")
            return

        if not pygame.mixer.music.get_busy():
            QMessageBox.warning(self, "Ошибка", "Сейчас не проигрывается трек")
            return

        self.current_playlist.previous_track()

    def play_next(self):
        """Проигрывание следующей песни."""
        if self.current_playlist is None:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите плейлист")
            return

        if not pygame.mixer.music.get_busy():
            QMessageBox.warning(self, "Ошибка", "Сейчас не проигрывается трек")
            return

        self.current_playlist.next_track()

    def next_track_if_this_ended(self):
        """Проигрывание следующего трека после завершения предыдущего."""
        if pygame.mixer.music.get_busy():
            return

        self.current_playlist.next_track()

    def change_position_dialogue(self) -> None:
        """Окно смены позиции песни"""
        current_row = self.playlist_widget.currentRow()
        if current_row < 0:
            QMessageBox.warning(
                self, "Ошибка", "Выберите композицию для смены позиции.",
            )
            return

        if self.current_playlist is None:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите плейлист")
            return

        if len(self.current_playlist) < 2:
            QMessageBox.warning(
                self, "Ошибка", "В плейлисте должно быть минимум 2 композиции для перестановки",
            )
            return

        response = QInputDialog.getInt(
            self, "Место композиции", f"Введите число от 1 до {len(self.current_playlist)}",
            min=1, max=len(self.current_playlist),
        )

        if response[1] is False:
            return

        new_position = response[0] - 1  # Корректируем индекс для вставки (0-based индекс)

        if current_row == new_position:
            return

        self.change_position(new_position, current_row)

    def change_position(self, new_position: int, current_row: int) -> None:
        """Смена позиции песни"""
        if current_row == new_position:
            return  # Ничего не делать, если позиции одинаковы

        # Получаем трек по индексу
        selected_track = self.current_playlist[current_row]

        # import ipdb; ipdb.set_trace()
        # Удаляем трек с текущей позиции
        self.current_playlist.remove(selected_track)

        # Вставляем трек на новую позицию
        self.current_playlist.insert(new_position, selected_track)

        self.update_playlist_widget()

def get_playlist_object_by_name(name, playlist_objects):
    for playlist in playlist_objects:
        if playlist['name'] == name:
            return playlist

    return None


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MusicPlayer()
    window.show()
    sys.exit(app.exec_())
