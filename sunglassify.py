import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
import cv2
import mediapipe as mp
import numpy as np
from PIL import Image


class Sunglassify(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PyQt GUI Setup')
        self.setGeometry(100, 100, 800, 600)

        # Create layout and widgets
        layout = QVBoxLayout()

        # Create buttons and labels
        self.upload_button = QPushButton('Upload Photo', self)
        self.upload_button.clicked.connect(self.upload_photo)  
        layout.addWidget(self.upload_button)

        self.original_photo_label = QLabel('Original Photo', self)
        self.original_photo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.original_photo_label)
        
        self.process_button = QPushButton('Add Sunglasses 😎', self)
        self.process_button.clicked.connect(self.process_photo)
        layout.addWidget(self.process_button)
            
        self.processed_photo_label = QLabel('Sunglassified Photo', self)
        self.processed_photo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.processed_photo_label)

        self.save_button = QPushButton('Save Photo', self)  
        self.save_button.clicked.connect(self.save_photo)      
        layout.addWidget(self.save_button)
        
        # Set the layout
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
            # Check whether loading image is possible
            pixmap = QPixmap(file_name)
            # If the imaged is loaded successfully
            if not pixmap.isNull():
                # Set the pixmap of the label and scale it to fit the label
                self.original_photo_label.setPixmap(pixmap.scaled(self.original_photo_label.width(), self.original_photo_label.height(), Qt.KeepAspectRatio))
                self.image_path = file_name
            # If the image cannot be loaded, show a warning message
            else:
                QMessageBox.warning(self, "Warning", "Cannot load image!")
                print("Cannot load image.")

            print(f"Image loaded: {file_name}")
        else:
            # If no image is selected, show a warning message
            QMessageBox.warning(self, "Warning", "No image selected!")
            print("No image selected.")

    def process_photo(self):
        # Step 1: Ensure an image is uploaded
        if not hasattr(self, 'image_path') or not self.image_path:
            QMessageBox.warning(self, "Warning", "Please upload an image first.")
            return

        # Step 2: Read the image with OpenCV
        image = cv2.imread(self.image_path)

        # Step 3: Convert the image to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Step 4: Initialize Mediapipe Face Mesh
        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True)

        # Step 5: Process the image to detect landmarks
        results = face_mesh.process(rgb_image)

        # Step 6: Check if landmarks are detected
        if not results.multi_face_landmarks:
            QMessageBox.warning(self, "Warning", "No face detected in the image!")
            return

        # Step 7: Extract left and right eye landmarks
        LEFT_EYE = [33, 133, 160, 159, 158, 157, 173, 246]
        RIGHT_EYE = [362, 263, 387, 386, 385, 384, 398, 466]

        image_height, image_width, _ = image.shape

        left_eye_coords = [
            (int(landmark.x * image_width), int(landmark.y * image_height))
            for landmark in [results.multi_face_landmarks[0].landmark[idx] for idx in LEFT_EYE]
        ]
        
        right_eye_coords = [
            (int(landmark.x * image_width), int(landmark.y * image_height))
            for landmark in [results.multi_face_landmarks[0].landmark[idx] for idx in RIGHT_EYE]
        ]

        # Step 8: Overlay sunglasses on the image
        self.overlay_sunglasses(image, left_eye_coords, right_eye_coords)
    
    def overlay_sunglasses(self, image, left_eye_coords, right_eye_coords):
        # Step 1: Calculate the center and distance between the eyes
        left_eye_center = np.mean(left_eye_coords, axis=0).astype(int)
        right_eye_center = np.mean(right_eye_coords, axis=0).astype(int)

        eye_center = np.mean([left_eye_center, right_eye_center], axis=0).astype(int)

        eye_distance = np.linalg.norm(right_eye_center - left_eye_center)

        # Step 2: Load and resize the sunglasses image
        sunglasses = Image.open('sunglasses.png').convert('RGBA')

        # Resize the sunglasses
        scaling_factor = eye_distance / sunglasses.width * 1.25

        new_width = int(sunglasses.width * scaling_factor)
        new_height = int(sunglasses.height * scaling_factor)
        resized_sunglasses = sunglasses.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Step 3: Calculate the top-left corner for placing the sunglasses
        x = eye_center[0] - new_width // 2
        y = eye_center[1] - new_height // 2

        # Step 4: Convert OpenCV image to PIL and overlay sunglasses
        background = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        background.paste(resized_sunglasses, (x, y), resized_sunglasses)

        # Step 5: Convert the final image back to OpenCV format
        processed_image = cv2.cvtColor(np.array(background), cv2.COLOR_RGB2BGR)

        # Step 6: Display or return the final processed image
        self.display_result(processed_image)

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
        print("Save button clicked!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Sunglassify()
    window.show()
    sys.exit(app.exec_())
