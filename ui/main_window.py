# ui/main_window.py

'''
Responsabilidades:
    - Crear la ventana
    - Botón “Abrir imagen”
    - Área de visualización
    - Llamar al ImageManager

Observaciones clave:
    - La UI no sabe qué es OpenCV
    - Solo recibe un QPixmap
    - Escalado con KeepAspectRatio (muy importante en fotografía)
'''
# ui/main_window.py

from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QFileDialog,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSlider,
)
from PySide6.QtCore import Qt
from core.image_manager import ImageManager
from ui.image_viewer import ImageViewer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Photo Editor – MVP 2")
        self.resize(1000, 700)
        self.image_manager = ImageManager()
        self._setup_ui()

    def _setup_ui(self):
        # ---------- Botón abrir ----------
        self.open_button = QPushButton("Abrir imagen")
        self.open_button.clicked.connect(self.open_image)

        # ---------- Visor ----------
        self.viewer = ImageViewer()

        # ---------- Sliders ----------
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(0)
        self.brightness_slider.valueChanged.connect(self.update_image)

        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(50, 300)  # 0.5 a 3.0
        self.contrast_slider.setValue(100)
        self.contrast_slider.valueChanged.connect(self.update_image)

        # Etiquetas
        brightness_label = QLabel("Brillo")
        contrast_label = QLabel("Contraste")

        # ---------- Botón reset ----------
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_image)

        # ---------- Layout de controles ----------
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(brightness_label)
        controls_layout.addWidget(self.brightness_slider)
        controls_layout.addWidget(contrast_label)
        controls_layout.addWidget(self.contrast_slider)
        controls_layout.addWidget(self.reset_button)

        # ---------- Layout principal ----------
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.open_button)
        main_layout.addLayout(controls_layout)
        main_layout.addWidget(self.viewer, stretch=1)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir imagen",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )

        if not file_path:
            return

        pixmap = self.image_manager.load_image(file_path)

        if pixmap:
            self.viewer.set_image(pixmap)

            # Reiniciamos sliders
            self.brightness_slider.setValue(0)
            self.contrast_slider.setValue(100)

    def update_image(self):
        """
        Se ejecuta cada vez que se mueve un slider
        """
        brightness = self.brightness_slider.value()
        contrast = self.contrast_slider.value() / 100.0

        pixmap = self.image_manager.apply_brightness_contrast(
            brightness,
            contrast
        )

        if pixmap:
            self.viewer.set_image(pixmap)

    def reset_image(self):
        pixmap = self.image_manager.reset_image()

        if pixmap:
            self.viewer.set_image(pixmap)
            self.brightness_slider.setValue(0)
            self.contrast_slider.setValue(100)