'''
Responsabilidades:
    - Cargar imagen con OpenCV
    - Convertir BGR → RGB
    - Convertir numpy.ndarray → QPixmap

Decisiones correctas desde ahora:
    - RGB como estándar interno
    - Imagen original intocable
    - Imagen de trabajo separada (clave para edición no destructiva)
'''
import cv2
import copy
from PySide6.QtGui import QImage, QPixmap

from core.operations import (
    BrightnessContrastOperation,
    SaturationOperation,
    CurveOperation,
    BlurOperation,
    SharpenOperation
)


class ImageManager:
    def __init__(self):
        self.original_image = None
        self.operations = []

        self.undo_stack = []
        self.redo_stack = []

    # -------------------------------------------------
    # LOAD
    # -------------------------------------------------
    def load_image(self, path: str):

        image_bgr = cv2.imread(path)

        if image_bgr is None:
            return None

        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

        self.original_image = image_rgb.copy()

        self.base_operations = []
        self.extra_operations = []

        self.undo_stack.clear()
        self.redo_stack.clear()

        return self._process_pipeline()

    # -------------------------------------------------
    # PREVIEW (sliders while dragging)
    # -------------------------------------------------
    def preview_parameters(self, brightness, contrast, saturation, curve_strength):

        if self.original_image is None:
            return None

        temp_base = []

        if brightness != 0 or contrast != 1.0:
            temp_base.append(
                BrightnessContrastOperation(brightness, contrast)
            )

        if saturation != 1.0:
            temp_base.append(
                SaturationOperation(saturation)
            )

        if curve_strength != 0.0:
            temp_base.append(
                CurveOperation(curve_strength)
            )

        img = self.original_image.copy()

        for op in temp_base + self.extra_operations:
            if op.enabled:
                img = op.apply(img)

        return self._to_qpixmap(img)

    # -------------------------------------------------
    # UPDATE BASE PARAMETERS (confirm slider change)
    # -------------------------------------------------
    def update_parameters(self, brightness, contrast, saturation, curve_strength):

        if self.original_image is None:
            return None

        self.undo_stack.append(copy.deepcopy(self.operations))
        self.redo_stack.clear()

    # Eliminar operaciones base existentes
        self.operations = [
            op for op in self.operations
            if not isinstance(op, (
                BrightnessContrastOperation,
                SaturationOperation,
                CurveOperation
            ))
        ]

    # Agregar nuevas si no están neutras
        if brightness != 0 or contrast != 1.0:
            self.operations.append(
                BrightnessContrastOperation(brightness, contrast)
            )

        if saturation != 1.0:
            self.operations.append(
                SaturationOperation(saturation)
            )

        if curve_strength != 0.0:
            self.operations.append(
                CurveOperation(curve_strength)
            )

        return self._process_pipeline()

    # -------------------------------------------------
    # ADD EXTRA OPERATION
    # -------------------------------------------------
    def add_operation(self, operation):

        if self.original_image is None:
            return None

        self.undo_stack.append(copy.deepcopy(self.operations))
        self.redo_stack.clear()

        self.operations.append(operation)

        return self._process_pipeline()

    # -------------------------------------------------
    # REMOVE OPERATION
    # -------------------------------------------------
    def remove_operation_at(self, index):

        if index < 0 or index >= len(self.operations):
            return None

        self.undo_stack.append(copy.deepcopy(self.operations))
        self.redo_stack.clear()

        del self.operations[index]

        return self._process_pipeline()

    # -------------------------------------------------
    # TOGGLE
    # -------------------------------------------------
    def toggle_operation(self, index):

        if index < 0 or index >= len(self.operations):
            return None

        self.undo_stack.append(copy.deepcopy(self.operations))
        self.redo_stack.clear()

        self.operations[index].enabled = \
            not self.operations[index].enabled

        return self._process_pipeline()

    # -------------------------------------------------
    # UNDO/REDO
    # -------------------------------------------------
    def undo(self):

        if not self.undo_stack:
            return None

        self.redo_stack.append(copy.deepcopy(self.operations))
        self.operations = self.undo_stack.pop()

        return self._process_pipeline()


    def redo(self):

        if not self.redo_stack:
            return None

        self.undo_stack.append(copy.deepcopy(self.operations))
        self.operations = self.redo_stack.pop()

        return self._process_pipeline()
    # -------------------------------------------------
    # RESET
    # -------------------------------------------------
    def reset_image(self):

        if self.original_image is None:
            return None

        self.undo_stack.append(copy.deepcopy(self.operations))
        self.redo_stack.clear()

        self.operations = []

        return self._process_pipeline()

    # -------------------------------------------------
    # PROCESS PIPELINE
    # -------------------------------------------------
    def _process_pipeline(self):

        if self.original_image is None:
            return None

        img = self.original_image.copy()

        for op in self.operations:
         if op.enabled:
                img = op.apply(img)

        return self._to_qpixmap(img)

    # -------------------------------------------------
    # PANEL INFO
    # -------------------------------------------------
    def get_operations_info(self):
        return self.operations
    
    # -------------------------------------------------
    # QPIXMAP
    # -------------------------------------------------
    def _to_qpixmap(self, image):

        height, width, channels = image.shape
        bytes_per_line = channels * width

        q_image = QImage(
            image.data,
            width,
            height,
            bytes_per_line,
            QImage.Format_RGB888
        )

        return QPixmap.fromImage(q_image)
    # -------------------------------------------------
    # GET CURRENT STATE
    # -------------------------------------------------
    def get_current_state(self):

        state = {
            "brightness": 0,
            "contrast": 1.0,
            "saturation": 1.0,
            "curve_strength": 0.0
        }

        for op in self.operations:

            if isinstance(op, BrightnessContrastOperation):
                state["brightness"] = op.brightness
                state["contrast"] = op.contrast

            elif isinstance(op, SaturationOperation):
                state["saturation"] = op.saturation

            elif isinstance(op, CurveOperation):
                state["curve_strength"] = op.strength

        return state
# -------------------------------------------------
# BEFORE / AFTER
# -------------------------------------------------
    def get_original_pixmap(self):

        if self.original_image is None:
            return None

        return self._to_qpixmap(self.original_image)


    def get_processed_pixmap(self):
        return self._process_pipeline()
# ---------------------------------------------------
#  MOVER Operaciones
# ---------------------------------------------------
    def move_operation(self, index, direction):

        new_index = index + direction

        if (
            index < 0
            or new_index < 0
            or index >= len(self.operations)
            or new_index >= len(self.operations)
        ):
            return None

        self.undo_stack.append(copy.deepcopy(self.operations))
        self.redo_stack.clear()

        self.operations[index], self.operations[new_index] = \
        self.operations[new_index], self.operations[index]

        return self._process_pipeline()