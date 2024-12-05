# Sunglassify 😎

### More detailed explanation [here!](https://medium.com/@ddanakim0304/how-i-used-pyqt-and-computer-vision-to-add-swag-to-photos-84e2e617755a)

<img width="447" alt="image" src="https://github.com/user-attachments/assets/d867f308-95da-4049-a1a4-27f76b8c2914">


Sunglassify is a desktop application that overlays virtual sunglasses on photos using advanced computer vision techniques. Built with Python, it provides an intuitive interface to upload, process, and save transformed images.

![ezgif-3-6643745efe](https://github.com/user-attachments/assets/4ffb5ea6-abf8-47c8-bdb8-72d0ab19023f)


## Algorithm
```mermaid
graph TD
    A[Upload Photo] --> B[Detect Eyes with Computer Vision Model]
    B --> C[Find Coordinates and Angle of Eyes]
    C --> D[Adjust Size & Angle of Sunglasses]
    D --> E[Overlay Sunglasses onto Original Image]
```


## Features

- **GUI with PyQt5**: User-friendly interface for seamless interactions.
- **Face Detection with Mediapipe**: Uses Mediapipe's Face Mesh for precise eye landmark detection.
- **Image Processing with OpenCV and Pillow**: Powered by OpenCV and Pillow for efficient transformations.
- **Save Functionality**: Export edited images in various formats.

## Installation

### Prerequisites

- Python 3.6+  
- pip (Python package installer)

### Steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/sunglassify.git
   cd sunglassify

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt

3. **Run the Application**:
   ```bash
   python sunglassify.py
Ensure a sunglasses.png image is in the same directory for overlays.
