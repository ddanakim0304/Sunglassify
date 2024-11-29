import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

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
        print("Add sunglasses button clicked!")

    def save_photo(self):
        print("Save button clicked!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Sunglassify()
    window.show()
    sys.exit(app.exec_())
