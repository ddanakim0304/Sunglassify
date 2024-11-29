import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Sunglassify()
    window.show()
    sys.exit(app.exec_())
