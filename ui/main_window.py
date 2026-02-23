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
    QListWidgetItem
)
from PySide6.QtCore import Qt
from core.image_manager import ImageManager
from ui.image_viewer import ImageViewer
from core.operations import BlurOperation
from core.operations import BlurOperation, SharpenOperation
from PySide6.QtWidgets import QListWidget
import copy 
from PySide6.QtCore import Qt



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Photo Editor – MVP 2")
        self.resize(1000, 700)
        self.image_manager = ImageManager()
        self._setup_ui()
        self.before_mode = False #Captura de eventos de TEclado
        self._updating_ui = False # Arregla Bug undo
        self._slider_active = False # Slider Estado 


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

        #---------Guarda Estado de Slider------------
        self.brightness_slider.sliderPressed.connect(self._begin_slider_change)
        self.brightness_slider.sliderReleased.connect(self._end_slider_change)

        self.contrast_slider.sliderPressed.connect(self._begin_slider_change)
        self.contrast_slider.sliderReleased.connect(self._end_slider_change)

        self.saturation_slider.sliderPressed.connect(self._begin_slider_change)
        self.saturation_slider.sliderReleased.connect(self._end_slider_change)

        self.curve_slider.sliderPressed.connect(self._begin_slider_change)
        self.curve_slider.sliderReleased.connect(self._end_slider_change)

        #--------- Etiquetas--------------
        brightness_label = QLabel("Brillo")
        contrast_label = QLabel("Contraste")
        saturation_label = QLabel("Saturación")

        # ---------- Botón reset ----------
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_image)
        
        # ---------- Botón Blur ----------
        self.blur_button = QPushButton("Blur")
        self.blur_button.clicked.connect(self.apply_blur)

        # ---------- Botón Sharpen ----------
        self.sharpen_button = QPushButton("Sharpen")
        self.sharpen_button.clicked.connect(self.apply_sharpen)
        
        # ---------- Listado de Operaciones ----------
        self.operations_list = QListWidget()
        self.operations_list.setMaximumHeight(120)

        #-------Detectar cambio de checkbox lista------
        self.operations_list.itemChanged.connect(self._operation_toggled)

        # ------------Eliminar Operaciiones 
        self.remove_button = QPushButton("Eliminar Operación")
        self.remove_button.clicked.connect(self.remove_selected_operation)
             

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

        # -------Layouts Blur-----------
        controls_layout.addWidget(self.blur_button)
        
        # -------Layouts Sharpen-----------
        controls_layout.addWidget(self.sharpen_button)
       
        # --------Crear slider en UI----------
        self.sharpen_slider = QSlider(Qt.Horizontal)
        self.sharpen_slider.setRange(0, 300)
        self.sharpen_slider.setValue(0)
        self.sharpen_slider.valueChanged.connect(self.update_sharpen)

        sharpen_label = QLabel("Sharpen")
        controls_layout.addWidget(sharpen_label)
        controls_layout.addWidget(self.sharpen_slider)


        # ---------- Layout principal ----------
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.open_button)
        main_layout.addLayout(controls_layout)
        main_layout.addWidget(self.viewer, stretch=1)
        main_layout.addWidget(self.operations_list)
        # -------Layouts Boton Remover Operacion---
        main_layout.addWidget(self.remove_button)

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

        if self._slider_active:
            # Solo preview
            pixmap = self.image_manager.preview_parameters(
                brightness,
                contrast,
                saturation,
                curve_strength
            )
        else:
            # Confirmar cambio real
            pixmap = self.image_manager.update_parameters(
                brightness,
                contrast,
                saturation,
                curve_strength
            )

        if pixmap:
            self.viewer.set_image(pixmap)
            self._update_operations_panel()

    def reset_image(self):
        pixmap = self.image_manager.reset_image()

        if pixmap:
            self.viewer.set_image(pixmap)
            self._update_operations_panel() # Panel de  Operaciones

            state = self.image_manager.get_current_state()
            self._sync_sliders(state)

    # -----FUNCIONES Botones Undo/Redo----------
    def undo_action(self):
        pixmap = self.image_manager.undo()

        if pixmap:
            self.viewer.set_image(pixmap)
            self._update_operations_panel() # Panel de  Operaciones

            state = self.image_manager.get_current_state()
            self._sync_sliders(state)


    def redo_action(self):
        pixmap = self.image_manager.redo()

        if pixmap:
            self.viewer.set_image(pixmap)
            self._update_operations_panel() # Panel de  Operaciones

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
        
        # Funcion metodo BLur 
    def apply_blur(self):
        pixmap = self.image_manager.add_operation(
            BlurOperation(kernel_size=7)
        )

        if pixmap:
            self.viewer.set_image(pixmap)
            self._update_operations_panel() # Panel de  Operaciones

    # Funcion metodo Sharpen
    def apply_sharpen(self):
        pixmap = self.image_manager.add_operation(
            SharpenOperation(amount=1.5, radius=5)
        )

        if pixmap:
            self.viewer.set_image(pixmap)
            self._update_operations_panel() # Panel de  Operaciones
    
    # Método para actualizar panel
    def _update_operations_panel(self):

        self.operations_list.clear()
        operations = self.image_manager.get_operations_info()

        for op in operations:
            item = QListWidgetItem(type(op).__name__)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)

            if op.enabled:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)

            self.operations_list.addItem(item)

    def update_sharpen(self):

        value = self.sharpen_slider.value()
        if value == 0:
            return

        amount = value / 100.0

        pixmap = self.image_manager.add_operation(
            SharpenOperation(amount=value/100.0, radius=5)
            )

        if pixmap:
            self.viewer.set_image(pixmap)
            self._update_operations_panel()

        # Eliminar Operaciones el Panel
    def remove_selected_operation(self):
        index = self.operations_list.currentRow()

        if index == -1:
            return

        pixmap = self.image_manager.remove_operation_at(index)

        if pixmap:
            self.viewer.set_image(pixmap)
            self._update_operations_panel()
        
        # Guarda el estado de los Sliders
    def _begin_slider_change(self):
        self._slider_active = True

    def _end_slider_change(self):
        self._slider_active = False

    # Detectar cambio de checkbox
    def _operation_toggled(self, item):

        index = self.operations_list.row(item)

        pixmap = self.image_manager.toggle_operation(index)

        if pixmap:
            self.viewer.set_image(pixmap)