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
import os
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
from PySide6.QtWidgets import QComboBox
from PySide6.QtCore import Qt
from core.image_manager import ImageManager
from ui.image_viewer import ImageViewer
from core.operations import BlurOperation
from core.operations import BlurOperation, SharpenOperation
from PySide6.QtWidgets import QListWidget
import copy 
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog
from core.operations import FILTER_REGISTRY

from core.operations import (
    BrightnessContrastOperation,
    SaturationOperation,
    CurveOperation,
    BlurOperation,
    SharpenOperation
)

class MainWindow(QMainWindow):
# Metodo init     
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Photo Editor – MVP 2")
        self.resize(1000, 700)
        self.image_manager = ImageManager()
        self._setup_ui()
        self.before_mode = False #Captura de eventos de TEclado
        self._updating_ui = False # Arregla Bug undo
        self._slider_active = False # Slider Estado 

# User Interface 
    def _setup_ui(self):
        
        # ---------- Botón Exportar  ----------
        self.export_button = QPushButton("Exportar Imagen")
        self.export_button.clicked.connect(self.export_image)
        
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
        
        # --------Botones para mover Operaciones ----------
        self.move_up_button = QPushButton("↑")
        self.move_down_button = QPushButton("↓")

        self.move_up_button.clicked.connect(self.move_operation_up)
        self.move_down_button.clicked.connect(self.move_operation_down)
        
        # ------------ Guardar Proyecto --------------------
        self.save_project_button = QPushButton("Guardar Proyecto")
        self.load_project_button = QPushButton("Cargar Proyecto")

        self.save_project_button.clicked.connect(self.save_project)
        self.load_project_button.clicked.connect(self.load_project)
        


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
        
        #---------FILTROs ----------------
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Seleccionar Filtro")
        for name in FILTER_REGISTRY.keys():
            self.filter_combo.addItem(name)

        self.filter_combo.currentIndexChanged.connect(self.apply_selected_filter)

        controls_layout.addWidget(self.filter_combo)
        
        
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
        
        # ------------ Panel Dinamico filtros--------------
        self.filter_params_layout = QVBoxLayout()
        main_layout.addLayout(self.filter_params_layout)

        # -------Layouts Boton Remover Operacion---
        main_layout.addWidget(self.remove_button)
        
        # --------Layaouts mover Operaciones -----
        main_layout.addWidget(self.move_up_button)
        main_layout.addWidget(self.move_down_button)  

        # ---------Guardar Proyecto--------------
        main_layout.addWidget(self.save_project_button)
        main_layout.addWidget(self.load_project_button)

        # -------Layouts de Exportar ----------
        main_layout.addWidget(self.export_button)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)



# Metodo para abrir una imagen en app
    def open_image(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir imagen",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )

        if not file_path:
            return

#  Cargar imagen en el modelo
        self.image_manager.load_image(file_path)

    #  Obtener pixmap procesado
        pixmap = self.image_manager.get_pixmap()

        if pixmap:
            self.viewer.set_image(pixmap, reset_view=True)

        # Reiniciar sliders
            self.brightness_slider.setValue(0)
            self.contrast_slider.setValue(100)
            self.saturation_slider.setValue(100)
            self.curve_slider.setValue(0)

            self._update_operations_panel()

# Actualiza la  imagen
    def update_image(self):

        brightness = self.brightness_slider.value()
        contrast = self.contrast_slider.value() / 100.0
        saturation = self.saturation_slider.value() / 100.0
        curve_strength = self.curve_slider.value() / 100.0

    # ---------- Brightness / Contrast ----------
        self._update_or_create_operation(
            BrightnessContrastOperation,
            brightness != 0 or contrast != 1.0,
            brightness=brightness,
            contrast=contrast
        )

    # ---------- Saturation ----------
        self._update_or_create_operation(
            SaturationOperation,
            saturation != 1.0,
            saturation=saturation
        )

    # ---------- Curve ----------
        self._update_or_create_operation(
            CurveOperation,
            curve_strength != 0.0,
            strength=curve_strength
        )

        pixmap = self.image_manager.get_pixmap()

        if pixmap:
            self.viewer.set_image(pixmap)
            self._update_operations_panel()

# Metodo para Resetear Cambios
    def reset_image(self):

        #  Bloquear señales
        sliders = [
            self.brightness_slider,
            self.contrast_slider,
            self.saturation_slider,
            self.curve_slider,
            self.sharpen_slider
        ]

        for s in sliders:
            s.blockSignals(True)

    #  Resetear modelo
        self.image_manager.reset_image()

    #  Resetear sliders
        self.brightness_slider.setValue(0)
        self.contrast_slider.setValue(100)
        self.saturation_slider.setValue(100)
        self.curve_slider.setValue(0)
        self.sharpen_slider.setValue(0)

        for s in sliders:
            s.blockSignals(False)

    #  Render limpio
        pixmap = self.image_manager.get_pixmap()

        if pixmap:
            self.viewer.set_image(pixmap, reset_view=True)
            self._update_operations_panel()

# Metodo para Desacer
    def undo_action(self):

        img = self.image_manager.undo()

        if img is None:
            return

        pixmap = self.image_manager.get_pixmap()

        if pixmap:
            self.viewer.set_image(pixmap)
            self._update_operations_panel()

            state = self.image_manager.get_current_state()
            self._sync_sliders(state)

# Metodo para Reacer
    def redo_action(self):

        img = self.image_manager.redo()

        if img is None:
            return

        pixmap = self.image_manager.get_pixmap()

        if pixmap:
            self.viewer.set_image(pixmap)
            self._update_operations_panel()

            state = self.image_manager.get_current_state()
            self._sync_sliders(state)

    
 # Captura de Tecla para Berfore/After----------
    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Space and not self.before_mode:
            self.before_mode = True

            pixmap = self.image_manager.get_original_pixmap()

            if pixmap:
                self.viewer.set_image(pixmap)

# Detecta cuando se libera la tecla 
    def keyReleaseEvent(self, event):

        if event.key() == Qt.Key_Space and self.before_mode:
            self.before_mode = False

            pixmap = self.image_manager.get_pixmap()

            if pixmap:
                self.viewer.set_image(pixmap)

# Sincroniza los Sliders
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

        self.image_manager.add_operation(
            BlurOperation(kernel_size=7)
        )

        pixmap = self.image_manager.get_pixmap()

        if pixmap:
            self.viewer.set_image(pixmap)
            self._update_operations_panel()

# Funcion metodo Sharpen
    def apply_sharpen(self):

        self.image_manager.add_operation(
            SharpenOperation(amount=1.5, radius=5)
        )

        pixmap = self.image_manager.get_pixmap()

        if pixmap:
            self.viewer.set_image(pixmap)
            self._update_operations_panel()
    
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

# Actualiza el sharpen
    def update_sharpen(self):

        value = self.sharpen_slider.value()
        amount = value / 100.0

    # Buscar operación Sharpen existente
        found = False
        for op in self.image_manager.operations:
            if isinstance(op, SharpenOperation):
                op.amount = amount
                found = True
                break

    # Si no existe y el valor no es 0 → crearla
        if not found and value != 0:
            self.image_manager.add_operation(
                SharpenOperation(amount=amount, radius=5)
            )

        pixmap = self.image_manager.get_pixmap()

        if pixmap:
            self.viewer.set_image(pixmap)
            self._update_operations_panel()

# Eliminar Operaciones el Panel
    def remove_selected_operation(self):
        index = self.operations_list.currentRow()

        if index == -1:
            return

        self.image_manager.remove_operation_at(index)

        pixmap = self.image_manager.get_pixmap()

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

        self.image_manager.toggle_operation(index)

        pixmap = self.image_manager.get_pixmap()

        if pixmap:
            self.viewer.set_image(pixmap)

# Metdod para mover arriba/abajo Operaciones
    def move_operation_up(self):

        index = self.operations_list.currentRow()

        self.image_manager.move_operation(index, -1)

        pixmap = self.image_manager.get_pixmap()

        if pixmap:
            self.viewer.set_image(pixmap)
            self._update_operations_panel()
            self.operations_list.setCurrentRow(index - 1)

    def move_operation_down(self):

        index = self.operations_list.currentRow()

        if index < 0 or index >= len(self.image_manager.operations) - 1:
            return

        ops = self.image_manager.operations

        # Intercambiar posiciones
        ops[index], ops[index + 1] = ops[index + 1], ops[index]

        # Actualizar vista
        pixmap = self.image_manager.get_pixmap()

        if pixmap:
            self.viewer.set_image(pixmap)

        self._update_operations_panel()

# Guardar Proyecto 
    def save_project(self):

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Proyecto",
            "",
            "JSON Files (*.json)"
        )
        
        if path:
            self.image_manager.save_project(path)

# Cargar Proyecto
    def load_project(self):

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir Proyecto",
            "",
            "Project Files (*.json)"
        )

        if path:
            self.image_manager.load_project(path)
            pixmap = self.image_manager.get_pixmap()

            if pixmap:
                self.viewer.set_image(pixmap)
                self._update_operations_panel()

                state = self.image_manager.get_current_state()
                self._sync_sliders(state)           

# Exportar Imagen
    def export_image(self):

        if self.image_manager.original_image is None:
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Imagen",
            "",
            "JPEG (*.jpg);;PNG (*.png);;BMP (*.bmp)"
        )

        if not path:
            return

        # Asegurar que tenga extensión
        if not os.path.splitext(path)[1]:
            path += ".jpg"

        self.image_manager.export_image(path)

# Metodo Auxiliar
    def _update_or_create_operation(self, operation_class, condition, **params):

    # Buscar operación existente
        found = None

        for op in self.image_manager.operations:
            if isinstance(op, operation_class):
                found = op
                break

    # Si debe existir
        if condition:

            if found:
            # actualizar parámetros
                for key, value in params.items():
                    setattr(found, key, value)

            else:
            # crear nueva operación
                op = operation_class(**params)
                self.image_manager.add_operation(op)

        else:
        # eliminar si existe
            if found:
                self.image_manager.operations.remove(found)    

 # Metodo Aplicar Filtro seleccionado
    def apply_selected_filter(self):

        filter_name = self.filter_combo.currentText()

        if filter_name == "Seleccionar Filtro":
            return

    # Obtener clase del filtro
        op_class = FILTER_REGISTRY.get(filter_name)

        if not op_class:
            return

    # Crear instancia
        operation = op_class()

    # Añadir al pipeline
        self.image_manager.add_operation(operation)

    # Crear panel dinámico
        self.build_filter_panel(operation)

    # Renderizar imagen
        pixmap = self.image_manager.get_pixmap()

        if pixmap:
            self.viewer.set_image(pixmap)
            self._update_operations_panel()

    # Reset combo
        self.filter_combo.setCurrentIndex(0)
        
# ------------------------------------------------
# Función que crea sliders automáticamente
# ------------------------------------------------
    def build_filter_panel(self, operation):

    # limpiar panel anterior
        while self.filter_params_layout.count():
            item = self.filter_params_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not hasattr(operation, "PARAMS"):
            return

        for param, (minv, maxv, default) in operation.PARAMS.items():

            label = QLabel(param)

            slider = QSlider(Qt.Horizontal)
            slider.setRange(minv, maxv)
            slider.setValue(default)

            slider.valueChanged.connect(
                lambda value, p=param, op=operation: self.update_filter_param(op, p, value)
            )

            self.filter_params_layout.addWidget(label)
            self.filter_params_layout.addWidget(slider)        

# ------------------------------------------------
# Función que actualiza el parámetro
# ------------------------------------------------
    def update_filter_param(self, operation, param, value):

        setattr(operation, param, value)

        pixmap = self.image_manager.get_pixmap()

        if pixmap:
            self.viewer.set_image(pixmap)