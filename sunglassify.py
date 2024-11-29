import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QFileDialog, QMessageBox
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import cv2
import mediapipe as mp
from PIL import Image
import numpy as np
from PIL import Image

class SunglassifyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Sunglassify')
        self.setGeometry(100, 100, 800, 600)
        self.image_path = ''
        self.processed_image = None
        self.init_ui()

    def init_ui(self):
        # Create widgets
        self.upload_button = QPushButton('Upload Photo', self)
        self.upload_button.clicked.connect(self.upload_photo)

        self.process_button = QPushButton('Add Sunglasses', self)
        self.process_button.clicked.connect(self.process_photo)
        self.process_button.setEnabled(False)

        self.save_button = QPushButton('Save Photo', self)
        self.save_button.clicked.connect(self.save_photo)
        self.save_button.setEnabled(False)

        self.original_image_label = QLabel('Original Image', self)
        self.original_image_label.setAlignment(Qt.AlignCenter)

        self.result_image_label = QLabel('Result Image', self)
        self.result_image_label.setAlignment(Qt.AlignCenter)

        # Create layout
        layout = QVBoxLayout()
        layout.addWidget(self.upload_button)
        layout.addWidget(self.original_image_label)
        layout.addWidget(self.process_button)
        layout.addWidget(self.result_image_label)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def upload_photo(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp)",
            options=options
        )
        if file_name:
            self.image_path = file_name
            pixmap = QPixmap(self.image_path)
            self.original_image_label.setPixmap(pixmap.scaled(
                self.original_image_label.width(),
                self.original_image_label.height(),
                Qt.KeepAspectRatio
            ))
            self.process_button.setEnabled(True)

    def process_photo(self):
        if not self.image_path:
            QMessageBox.warning(self, "Warning", "Please upload an image first.")
            return

        # Read the image
        image = cv2.imread(self.image_path)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Initialize MediaPipe Face Mesh
        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True)

        # Process the image and find face landmarks
        result = face_mesh.process(rgb_image)

        # Check if landmarks are detected
        if not result.multi_face_landmarks:
            QMessageBox.warning(self, "Warning", "No face detected in the image.")
            return

        # Get the first face's landmarks
        face_landmarks = result.multi_face_landmarks[0]

        # Extract the eye coordinates
        left_eye_coords = []
        right_eye_coords = []

        # Indices for left and right eye landmarks in MediaPipe Face Mesh
        LEFT_EYE = [33, 133, 160, 159, 158, 157, 173, 246]
        RIGHT_EYE = [362, 263, 387, 386, 385, 384, 398, 466]

        image_height, image_width, _ = image.shape

        for idx in LEFT_EYE:
            x = int(face_landmarks.landmark[idx].x * image_width)
            y = int(face_landmarks.landmark[idx].y * image_height)
            left_eye_coords.append((x, y))

        for idx in RIGHT_EYE:
            x = int(face_landmarks.landmark[idx].x * image_width)
            y = int(face_landmarks.landmark[idx].y * image_height)
            right_eye_coords.append((x, y))

        # Overlay the sunglasses
        self.overlay_sunglasses(image, left_eye_coords, right_eye_coords)

    def overlay_sunglasses(self, image, left_eye_coords, right_eye_coords):
        # Load the sunglasses image with transparency (RGBA)
        sunglasses = Image.open('sunglasses.png').convert('RGBA')

        # Calculate the position and size
        left_eye_center = np.mean(left_eye_coords, axis=0).astype(int)
        right_eye_center = np.mean(right_eye_coords, axis=0).astype(int)
        eye_center = ((left_eye_center + right_eye_center) // 2).astype(int)
        eye_width = np.linalg.norm(right_eye_center - left_eye_center)
        scaling_factor = eye_width / sunglasses.width * 1.5

        # Resize the sunglasses image
        new_width = int(sunglasses.width * scaling_factor * 2)
        new_height = int(sunglasses.height * scaling_factor * 2)
        resized_sunglasses = sunglasses.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Calculate the position to place the sunglasses
        x = eye_center[0] - new_width // 2
        y = eye_center[1] - new_height // 2

        # Convert the OpenCV image to PIL format
        background = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        # Paste the sunglasses onto the background
        background.paste(resized_sunglasses, (x, y), resized_sunglasses)

        # Convert back to OpenCV format
        self.processed_image = cv2.cvtColor(np.array(background), cv2.COLOR_RGB2BGR)

        # Display the result
        self.display_result(self.processed_image)

    def display_result(self, image):
        # Convert the image to Qt format
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        qt_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()

        # Display the image
        self.result_image_label.setPixmap(QPixmap.fromImage(qt_image).scaled(
            self.result_image_label.width(),
            self.result_image_label.height(),
            Qt.KeepAspectRatio
        ))
        self.save_button.setEnabled(True)

    def save_photo(self):
        if self.processed_image is None:
            QMessageBox.warning(self, "Warning", "No processed image to save.")
            return

        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save Image",
            "",
            "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg);;All Files (*)",
            options=options
        )
        if file_name:
            cv2.imwrite(file_name, self.processed_image)
            QMessageBox.information(self, "Saved", "Image saved successfully!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SunglassifyApp()
    window.show()
    sys.exit(app.exec_())
