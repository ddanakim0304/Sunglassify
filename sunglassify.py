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
        self.setWindowTitle('Sunglassify')
        self.setGeometry(100, 100, 800, 600)

        # Create layout
        layout = QVBoxLayout()

        # Create upload button, connected with corresponding method
        self.upload_button = QPushButton('Upload Photo', self)
        self.upload_button.clicked.connect(self.upload_photo)  
        layout.addWidget(self.upload_button)

        # Create lable for original image
        self.original_photo_label = QLabel('Original Photo', self)
        self.original_photo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.original_photo_label)
        
        # Create process image button
        self.process_button = QPushButton('Sunglassify 😎', self)
        self.process_button.clicked.connect(self.process_photo)
        layout.addWidget(self.process_button)
        
        # Create processed image label
        self.processed_photo_label = QLabel('Sunglassified Photo', self)
        self.processed_photo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.processed_photo_label)

        # Create save image button
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
        # Check if an image is uploaded
        if not hasattr(self, 'image_path') or not self.image_path:
            QMessageBox.warning(self, "Warning", "Please upload an image first.")
            return
        image = cv2.imread(self.image_path)

        # Convert image to RGB for Mediapipe
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Initialize Mediapipe Face Mesh
        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True)

        # Process the image to detect landmarks
        results = face_mesh.process(rgb_image)

        # Check if landmarks are detected
        if not results.multi_face_landmarks:
            QMessageBox.warning(self, "Warning", "No face detected in the image!")
            return

        # Extract left and right eye landmarks
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

        # Move on to overlaying sunglasses image with the coordinates and image 
        self.overlay_sunglasses(image, left_eye_coords, right_eye_coords)
    
    def overlay_sunglasses(self, image, left_eye_coords, right_eye_coords):
        # Calculate centers and distance
        left_eye_center = np.mean(left_eye_coords, axis=0).astype(int)
        right_eye_center = np.mean(right_eye_coords, axis=0).astype(int)
        eye_center = np.mean([left_eye_center, right_eye_center], axis=0).astype(int)
        eye_distance = np.linalg.norm(right_eye_center - left_eye_center)
    
        # Calculate rotation angle
        dy = right_eye_center[1] - left_eye_center[1]
        dx = right_eye_center[0] - left_eye_center[0]
        angle = np.degrees(np.arctan2(dy, dx))
    
        # Resize and rotate sunglasses
        sunglasses = Image.open('sunglasses.png').convert('RGBA')
        scaling_factor = eye_distance / sunglasses.width * 2.4
        new_width = int(sunglasses.width * scaling_factor)
        new_height = int(sunglasses.height * scaling_factor)
        resized_sunglasses = sunglasses.resize((new_width, new_height), Image.Resampling.LANCZOS)
        rotated_sunglasses = resized_sunglasses.rotate(-angle, expand=True, resample=Image.Resampling.BICUBIC)
    
        # Calculate new position considering rotation
        x = eye_center[0] - rotated_sunglasses.width // 2
        y_offset = int(eye_distance * 0.1)
        y = eye_center[1] - rotated_sunglasses.height // 2 + y_offset
    
        # Overlay the rotated sunglasses
        background = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        background.paste(rotated_sunglasses, (x, y), rotated_sunglasses)
    
        # Convert back to OpenCV format
        self.processed_image = cv2.cvtColor(np.array(background), cv2.COLOR_RGB2BGR)
        self.display_result(self.processed_image)

        # Convert the image to Qt format (fixed version)
        height, width, _ = self.processed_image.shape
        bytes_per_line = 3 * width
        qt_image = QImage(self.processed_image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()

        # Display the image in the label
        self.processed_photo_label.setPixmap(QPixmap.fromImage(qt_image).scaled(
            self.processed_photo_label.width(),
            self.processed_photo_label.height(),
            Qt.KeepAspectRatio
        ))

        self.save_button.setEnabled(True)

        

    def save_photo(self):
        # Check if a processed image exists
        if not hasattr(self, 'processed_image') or self.processed_image is None:
            QMessageBox.warning(self, "Warning", "No processed image to save!")
            return
        options = QFileDialog.Options()
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)", options=options)

        if not save_path:
            QMessageBox.warning(self, "Warning", "No save path selected!")
            return

        # Save the processed image
        try:
            cv2.imwrite(save_path, self.processed_image)
            QMessageBox.information(self, "Success", f"Image saved successfully at:\n{save_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save image: {str(e)}")
            print(f"Error saving image: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Sunglassify()
    window.show()
    sys.exit(app.exec_())
