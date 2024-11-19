import os
import cv2
import time
import numpy as np
import mss
from screeninfo import get_monitors
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, QSpinBox, QFileDialog, QMessageBox)
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, QUrl
from PyQt6.QtGui import QDesktopServices
from datetime import datetime
import sys

# Constants for UI states
STATUS_READY = "Status: Ready"
STATUS_RECORDING = "Status: Recording"
STATUS_STOPPED = "Status: Recording Stopped"
STATUS_COMPLETED = "Status: Recording Completed"

MAX_RECORDINGS = 12  # Maximum number of recordings to keep in the folder

class ScreenRecorderThread(QThread):
    recording_done = pyqtSignal(str)

    def __init__(self, monitor_selection, record_duration, save_folder, parent=None):
        super().__init__(parent)
        self.monitor_selection = monitor_selection
        self.record_duration = record_duration
        self.save_folder = save_folder
        self.stop_flag = False

    def run(self):
        timestamp = datetime.now().strftime("%d%m%y_%H%M%S")
        video_file_name = f"screen_recording_{timestamp}.avi"
        self.record_video(video_file_name)

    def record_video(self, video_file_name):
        monitor = get_monitors()[self.monitor_selection]
        screen_region = {"top": monitor.y, "left": monitor.x, "width": monitor.width, "height": monitor.height}
        screen_width, screen_height = monitor.width, monitor.height

        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        video_writer = cv2.VideoWriter(os.path.join(self.save_folder, video_file_name), fourcc, 20, (screen_width, screen_height))

        with mss.mss() as sct:
            start_time = time.time()
            try:
                while not self.stop_flag:
                    screen_shot = sct.grab(screen_region)
                    frame = np.array(screen_shot)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                    video_writer.write(frame)

                    if time.time() - start_time > self.record_duration:
                        break
            finally:
                video_writer.release()
                self.recording_done.emit(video_file_name)

    def stop_recording(self):
        self.stop_flag = True
        self.quit()
        self.wait()


class ScreenRecorderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screen Recorder")
        self.setGeometry(300, 300, 400, 300)

        self.recording = False
        self.monitor_selection = 0
        self.record_duration = 300
        self.save_folder = ""

        # Initialize UI components
        self.init_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

        # Prompt user to select folder for saving recordings if not already set
        self.select_save_folder()

    def init_ui(self):
        layout = QVBoxLayout()

        self.screen_label = QLabel("Screen Selection:")
        layout.addWidget(self.screen_label)

        self.screen_combo = QComboBox(self)
        monitors = get_monitors()
        for monitor in monitors:
            self.screen_combo.addItem(f"{monitor.name} ({monitor.width}x{monitor.height})")
        layout.addWidget(self.screen_combo)

        self.duration_label = QLabel("Recording Duration (seconds):")
        layout.addWidget(self.duration_label)

        self.duration_spinbox = QSpinBox(self)
        self.duration_spinbox.setRange(1, 3600)
        self.duration_spinbox.setValue(self.record_duration)
        layout.addWidget(self.duration_spinbox)

        self.start_button = QPushButton("Start Recording", self)
        self.start_button.clicked.connect(self.start_recording)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Recording", self)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_recording)
        layout.addWidget(self.stop_button)

        self.status_label = QLabel(STATUS_READY, self)
        layout.addWidget(self.status_label)

        self.show_button = QPushButton("Show Recordings", self)
        self.show_button.clicked.connect(self.open_recordings_folder)
        layout.addWidget(self.show_button)

        self.quit_button = QPushButton("Exit", self)
        self.quit_button.clicked.connect(self.quit_application)
        layout.addWidget(self.quit_button)

        self.setLayout(layout)

    def select_save_folder(self):
        """Prompt the user to select a folder for saving recordings if not already set."""
        if not self.save_folder:
            folder = QFileDialog.getExistingDirectory(self, "Select Save Folder")
            if folder:
                self.save_folder = self.create_unique_folder(folder, "Screen Recordings")
            else:
                QMessageBox.warning(self, "No Folder Selected", "No folder selected for saving recordings. Exiting application.")
                QApplication.quit()

    def create_unique_folder(self, parent_folder, folder_name):
        """Create a folder with a unique name by appending a number if the folder already exists."""
        target_folder = os.path.join(parent_folder, folder_name)
        counter = 1

        # If folder already exists, append a number to the folder name
        while os.path.exists(target_folder):
            target_folder = os.path.join(parent_folder, f"{folder_name} {counter}")
            counter += 1

        # Create the folder
        os.makedirs(target_folder)
        return target_folder

    def start_recording(self):
        self.recording = True
        self.monitor_selection = self.screen_combo.currentIndex()
        self.record_duration = self.duration_spinbox.value()

        self.status_label.setText(f"{STATUS_RECORDING} ({self.record_duration} seconds)")

        self.time_left = self.record_duration
        self.timer.start(1000)

        self.record_thread = ScreenRecorderThread(self.monitor_selection, self.record_duration, self.save_folder)
        self.record_thread.recording_done.connect(self.on_recording_done)
        self.record_thread.start()

        self.stop_button.setEnabled(True)
        self.start_button.setEnabled(False)

    def stop_recording(self):
        self.recording = False
        self.record_thread.stop_recording()
        self.stop_button.setEnabled(False)
        self.start_button.setEnabled(True)
        self.status_label.setText(STATUS_STOPPED)
        self.timer.stop()

    def on_recording_done(self, video_file_name):
        self.status_label.setText(f"Recording completed: {video_file_name}")
        print(f"Screen recording completed: {video_file_name}")

        # Check and remove the oldest recording if there are more than MAX_RECORDINGS files
        self.manage_recordings()

        # If the recording is still active (not stopped by the user), start a new recording
        if self.recording:
            self.start_recording()

    def manage_recordings(self):
        """Check the folder for the number of files and delete the oldest if there are more than MAX_RECORDINGS."""
        recordings = [f for f in os.listdir(self.save_folder) if f.endswith('.avi')]
        if len(recordings) > MAX_RECORDINGS:
            # Sort the recordings by modification time (oldest first)
            recordings.sort(key=lambda x: os.path.getmtime(os.path.join(self.save_folder, x)))
            oldest_file = os.path.join(self.save_folder, recordings[0])
            os.remove(oldest_file)
            print(f"Old recording deleted: {oldest_file}")

    def update_timer(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.status_label.setText(f"{STATUS_RECORDING} ({self.time_left} seconds left)")
        else:
            self.status_label.setText(STATUS_COMPLETED)
            self.timer.stop()

    def open_recordings_folder(self):
        """Open the folder where recordings are saved."""
        if self.save_folder:
            url = QUrl.fromLocalFile(os.path.abspath(self.save_folder))  # Convert string to QUrl
            QDesktopServices.openUrl(url)

    def quit_application(self):
        """Quit the application."""
        if self.recording:
            self.stop_recording()
        QApplication.quit()

    def closeEvent(self, event):
        """Ensure thread is properly cleaned up when closing the app."""
        if self.recording:
            self.stop_recording()  # Stop the recording if active
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScreenRecorderApp()
    window.show()
    sys.exit(app.exec())
