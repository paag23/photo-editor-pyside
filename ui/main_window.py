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
        self.before_mode = False #Captura de eventos de TEclado
        self._updating_ui = False # Arregla Bug undo 


    def _setup_ui(self):
        # ---------- Botón abrir ----------
        self.open_button = QPushButton("Abrir imagen")
        self.open_button.clicked.connect(self.open_image)

        # -------Botones Undo / Redo-------
        self.undo_button = QPushButton("Undo")
        self.undo_button.clicked.connect(self.undo_action)
        
        self.redo_button = QPushButton("Redo")
        self.redo_button.clicked.connect(self.redo_action)

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
        
        #------- Slider Saturación---------
        self.saturation_slider = QSlider(Qt.Horizontal)
        self.saturation_slider.setRange(0, 300)  # 0.0 a 3.0
        self.saturation_slider.setValue(100)
        self.saturation_slider.valueChanged.connect(self.update_image)

        # -------Slider Curva toanal-----------
        self.curve_slider = QSlider(Qt.Horizontal)
        self.curve_slider.setRange(-100, 100)
        self.curve_slider.setValue(0)
        self.curve_slider.valueChanged.connect(self.update_image)
        curve_label = QLabel("Curva")

        #--------- Etiquetas--------------
        brightness_label = QLabel("Brillo")
        contrast_label = QLabel("Contraste")
        saturation_label = QLabel("Saturación")

        # ---------- Botón reset ----------
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_image)

        # -------Layouts de controles ----------
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(brightness_label)
        controls_layout.addWidget(self.brightness_slider)
        controls_layout.addWidget(contrast_label)
        controls_layout.addWidget(self.contrast_slider)
        controls_layout.addWidget(self.reset_button)
        
        # -------Layouts Boton Undo/Redo-----------
        controls_layout.addWidget(self.undo_button)
        controls_layout.addWidget(self.redo_button)
        
        # -------Layouts Saturacion-----------
        controls_layout.addWidget(saturation_label)
        controls_layout.addWidget(self.saturation_slider)

        # -------Layouts Curva-----------
        controls_layout.addWidget(curve_label)
        controls_layout.addWidget(self.curve_slider)

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
            self.viewer.set_image(pixmap, reset_view=True)

            # Reiniciamos sliders
            self.brightness_slider.setValue(0)
            self.contrast_slider.setValue(100)

    def update_image(self):

        brightness = self.brightness_slider.value()
        contrast = self.contrast_slider.value() / 100.0
        saturation = self.saturation_slider.value() / 100.0
        curve_strength = self.curve_slider.value() / 100.0

        pixmap = self.image_manager.update_parameters(
            brightness,
            contrast,
            saturation,
            curve_strength
        )

        if pixmap:
            self.viewer.set_image(pixmap)



    def reset_image(self):
        pixmap = self.image_manager.reset_image()

        if pixmap:
            self.viewer.set_image(pixmap)

            state = self.image_manager.get_current_state()
            self._sync_sliders(state)

    # -----FUNCIONES Botones Undo/Redo----------
    def undo_action(self):
        pixmap = self.image_manager.undo()

        if pixmap:
            self.viewer.set_image(pixmap)

            state = self.image_manager.get_current_state()
            self._sync_sliders(state)


    def redo_action(self):
        pixmap = self.image_manager.redo()

        if pixmap:
            self.viewer.set_image(pixmap)

            state = self.image_manager.get_current_state()
            self._sync_sliders(state)

    
    # -----FUNCIONES Captura de Tecla para Berfore/After----------
    def keyPressEvent(self, event):
        """
        Detecta cuando se presiona una tecla
        """
        if event.key() == Qt.Key_Space and not self.before_mode:
            self.before_mode = True

            pixmap = self.image_manager.get_original_pixmap()

            if pixmap:
                self.viewer.set_image(pixmap)

    def keyReleaseEvent(self, event):
        """
        Detecta cuando se suelta la tecla
        """
        if event.key() == Qt.Key_Space and self.before_mode:
            self.before_mode = False

        # Volvemos al estado procesado actual
            pixmap = self.image_manager.get_processed_pixmap()
 
            if pixmap:
                self.viewer.set_image(pixmap)


    def _sync_sliders(self, state):
            sliders = [
            (self.brightness_slider, state["brightness"]),
            (self.contrast_slider, int(state["contrast"] * 100)),
            (self.saturation_slider, int(state["saturation"] * 100)),
            (self.curve_slider, int(state["curve_strength"] * 100)),
            ]

            for slider, value in sliders:
                slider.blockSignals(True)
                slider.setValue(value)
                slider.blockSignals(False)



