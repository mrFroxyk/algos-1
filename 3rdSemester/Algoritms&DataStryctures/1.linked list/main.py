import pathlib
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
    """Music Player window."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Music Player")
        self.setGeometry(100, 100, 400, 400)
        self.current_playlist: Playlist | None = None
        self.playlist_objects: list[dict[str, Playlist]] = []

        pygame.mixer.init()

        self.selected_song_index: int | None = None

        self.layout = QVBoxLayout()

        self.add_playlist_button = QPushButton("Add Playlist")
        self.add_playlist_button.clicked.connect(self.create_new_playlist_dialog)
        self.layout.addWidget(self.add_playlist_button)

        self.remove_playlist_button = QPushButton("Delete Playlist")
        self.remove_playlist_button.clicked.connect(self.delete_playlist)
        self.layout.addWidget(self.remove_playlist_button)

        self.playlist_combobox = QComboBox()
        self.playlist_combobox.currentIndexChanged.connect(self.on_select_playlist_from_combobox)
        self.layout.addWidget(self.playlist_combobox)

        self.playlist_widget = QListWidget()
        self.layout.addWidget(self.playlist_widget)

        self.add_button = QPushButton("Add Composition")
        self.add_button.clicked.connect(self.add_song)
        self.layout.addWidget(self.add_button)

        self.remove_button = QPushButton("Delete Composition")
        self.remove_button.clicked.connect(self.remove_song)
        self.layout.addWidget(self.remove_button)

        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.choose_song)
        self.layout.addWidget(self.play_button)

        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.play_previous)
        self.layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.play_next)
        self.layout.addWidget(self.next_button)

        self.change_button = QPushButton("Change Position")
        self.change_button.clicked.connect(self.change_position_dialogue)
        self.layout.addWidget(self.change_button)

        self.setLayout(self.layout)
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.next_track_if_this_ended)

        # add default playlist
        if not self.playlist_objects:
            default_playlist_name = "Default Playlist"
            default_playlist = Playlist()
            self.playlist_objects.append({
                "name": default_playlist_name,
                "playlist": default_playlist,
            })
            self.playlist_combobox.addItem(default_playlist_name)
            self.playlist_combobox.setCurrentText(default_playlist_name)
            self.current_playlist = default_playlist

    def create_new_playlist_dialog(self) -> None:
        """Open a dialog to create a new playlist."""
        name, ok = QInputDialog.getText(self, "Create Playlist", "Enter playlist name:")

        if ok and name:
            if ',' in name:
                QMessageBox.warning(self, "Error", "Playlist name should not contain a comma.")
                return

            if get_playlist_object_by_name(name, self.playlist_objects):
                QMessageBox.warning(self, "Error", "A playlist with this name already exists.")
                return

            self.playlist_objects.append({
                "name": name,
                "playlist": Playlist(),
            })

            self.playlist_combobox.addItem(name)

    def delete_playlist(self) -> None:
        """Delete the selected playlist."""
        current_name = self.playlist_combobox.currentText()

        if not current_name:
            QMessageBox.warning(self, "Error", "Select a playlist to delete.")
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Delete Playlist",
            f"Are you sure you want to delete the playlist '{current_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            playlist_object = get_playlist_object_by_name(current_name, self.playlist_objects)
            if playlist_object:
                self.playlist_objects.remove(playlist_object)
                self.playlist_combobox.removeItem(self.playlist_combobox.currentIndex())
                self.current_playlist = None
                self.playlist_widget.clear()
                QMessageBox.information(
                    self,
                    "Deletion",
                    f"Playlist '{current_name}' successfully deleted.",
                )
            else:
                QMessageBox.warning(self, "Error", "Failed to find the playlist for deletion.")

        if self.playlist_combobox.count() == 0:
            self.current_playlist = None
            self.playlist_widget.clear()

    def on_select_playlist_from_combobox(self) -> None:
        """Handle for selecting a playlist from the combobox."""
        current_name = self.playlist_combobox.currentText()
        playlist_object = get_playlist_object_by_name(current_name, self.playlist_objects)
        if playlist_object:
            self.current_playlist = playlist_object["playlist"]
            self.update_playlist_widget()

    def update_playlist_widget(self) -> None:
        """Update the song list widget for the current playlist."""
        self.playlist_widget.clear()
        if self.current_playlist:
            for node in self.current_playlist:
                self.playlist_widget.addItem(pathlib.Path(node.data.path).name)

    def add_song(self) -> None:
        """Add songs to the playlist."""
        if self.current_playlist is None:
            QMessageBox.warning(self, "Error", "Please select a playlist first.")
            return

        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select music files", "", "Audio Files (*.mp3 *.wav)", options=options,
        )
        if files:
            for file in files:
                self.current_playlist.append(Composition(file))
                self.playlist_widget.addItem(pathlib.Path(file).name)

    def remove_song(self) -> None:
        """Remove selected songs from the playlist."""
        selected_items = self.playlist_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Error", "Select a composition to delete.")
            return
        for item in selected_items:
            row = self.playlist_widget.row(item)
            if self.current_playlist.current == self.current_playlist[row]:
                self.current_playlist.current = None
                pygame.mixer.music.unload()
                pygame.mixer.music.stop()

            self.current_playlist.remove(self.current_playlist[row])
            self.playlist_widget.takeItem(row)

    def find_song_by_id(self, sid: int) -> Composition | None:
        """Find a song by its ID."""
        for idx, track in enumerate(self.current_playlist):
            if idx == sid:
                return track
        return None

    def play_song_by_id(self, sid: int) -> None:
        """Plays a song by its ID."""
        track = self.find_song_by_id(sid)
        if track:
            self.current_playlist.play_all(track)
            self.timer.start()

    def choose_song(self) -> None:
        """Plays the selected song."""
        current_row = self.playlist_widget.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Select a composition to play.")
            return None

        if self.current_playlist[current_row] != self.current_playlist.current:
            return self.play_song_by_id(current_row)

    def play_previous(self) -> None:
        """Plays the previous song."""
        if self.current_playlist is None:
            QMessageBox.warning(self, "Error", "Please select a playlist first.")
            return

        if not pygame.mixer.music.get_busy():
            QMessageBox.warning(self, "Error", "No track is currently playing.")
            return

        self.current_playlist.previous_track()

    def play_next(self) -> None:
        """Plays the next song."""
        if self.current_playlist is None:
            QMessageBox.warning(self, "Error", "Please select a playlist first.")
            return

        if not pygame.mixer.music.get_busy():
            QMessageBox.warning(self, "Error", "No track is currently playing.")
            return

        self.current_playlist.next_track()

    def next_track_if_this_ended(self) -> None:
        """Plays the next track after the current one ends."""
        if pygame.mixer.music.get_busy():
            return

        self.current_playlist.next_track()

    def change_position_dialogue(self) -> None:
        """Display a dialog to change the song's position."""
        current_row = self.playlist_widget.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Select a composition to change its position.")
            return

        if self.current_playlist is None:
            QMessageBox.warning(self, "Error", "Please select a playlist first.")
            return

        if len(self.current_playlist) < 2:
            QMessageBox.warning(
                self, "Error", "The playlist must contain at least 2 compositions to rearrange.",
            )
            return

        response = QInputDialog.getInt(
            self,
            "Change Composition Position",
            f"Enter a number between 1 and {len(self.current_playlist)}",
            min=1,
            max=len(self.current_playlist),
        )

        if not response[1]:
            return

        new_position = response[0] - 1

        if current_row == new_position:
            return

        self.change_position(new_position, current_row)

    def change_position(self, position: int, current_row: int) -> None:
        """Change the position of a song."""
        selected_track = self.find_song_by_id(current_row)
        prev_track = self.find_song_by_id(position - 1)

        if current_row < position:
            prev_track = self.find_song_by_id(position)

        self.remove_song()
        self.current_playlist.insert(prev_track.data, selected_track.data)
        self.playlist_widget.clear()
        for node in self.current_playlist:
            self.playlist_widget.addItem(pathlib.Path(node.data.path).name)


def get_playlist_object_by_name(
    name: str,
    playlist_objects: list[dict[str, Playlist]],
) -> dict[str, Playlist] | None:
    """Search for a playlist object by name."""
    for obj in playlist_objects:
        if obj["name"] == name:
            return obj
    return None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MusicPlayer()
    window.show()
    sys.exit(app.exec_())
