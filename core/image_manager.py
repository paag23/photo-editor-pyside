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
    CurveOperation
)

class ImageManager:
    def __init__(self):
        self.original_image = None
        self.operations = []

        self.undo_stack = []
        self.redo_stack = []

    # -------------------------------------------------
    # CARGA DE IMAGEN
    # -------------------------------------------------
    def load_image(self, path: str) -> QPixmap | None:
        image_bgr = cv2.imread(path)

        if image_bgr is None:
            return None

        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

        self.original_image = image_rgb.copy()

        self.operations = []
        self.undo_stack.clear()
        self.redo_stack.clear()

        return self._process_pipeline()

    # -------------------------------------------------
    # ACTUALIZAR PARÁMETROS
    # -------------------------------------------------
    def update_parameters(self, brightness, contrast, saturation, curve_strength):
        if self.original_image is None:
            return None

        # Guardar estado anterior
        self.undo_stack.append(copy.deepcopy(self.operations))
        self.redo_stack.clear()

        # Reconstruir operaciones
        self.operations = [
            BrightnessContrastOperation(brightness, contrast),
            SaturationOperation(saturation),
            CurveOperation(curve_strength)
        ]
        print("UPDATE")
        print("UNDO:", len(self.undo_stack), "REDO:", len(self.redo_stack))

        return self._process_pipeline()

    # -------------------------------------------------
    # UNDO
    # -------------------------------------------------
    def undo(self):
        if not self.undo_stack:
            return None

        self.redo_stack.append(copy.deepcopy(self.operations))
        self.operations = self.undo_stack.pop()

        print("UNDO ACTION")
        print("UNDO:", len(self.undo_stack), "REDO:", len(self.redo_stack))


        return self._process_pipeline()

    # -------------------------------------------------
    # REDO
    # -------------------------------------------------
    def redo(self):
        if not self.redo_stack:
            return None

        self.undo_stack.append(copy.deepcopy(self.operations))
        self.operations = self.redo_stack.pop()

        print("REDO ACTION")
        print("UNDO:", len(self.undo_stack), "REDO:", len(self.redo_stack))


        return self._process_pipeline()

    # -------------------------------------------------
    # RESET
    # -------------------------------------------------
    def reset_image(self):
        if self.original_image is None:
            return None

        self.operations = []
        self.undo_stack.clear()
        self.redo_stack.clear()

        return self._process_pipeline()

    # -------------------------------------------------
    # PIPELINE
    # -------------------------------------------------
    def _process_pipeline(self):
        if self.original_image is None:
            return None

        img = self.original_image.copy()

        for operation in self.operations:
            img = operation.apply(img)

        return self._to_qpixmap(img)

    # -------------------------------------------------
    # GET STATE (para sincronizar UI)
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
    # CONVERSIÓN QPIXMAP
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
    # BEFORE
    # -------------------------------------------------
    def get_original_pixmap(self):
        if self.original_image is None:
            return None

        return self._to_qpixmap(self.original_image)

    def get_processed_pixmap(self):
        return self._process_pipeline()
