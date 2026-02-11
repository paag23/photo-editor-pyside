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
# core/image_manager.py
import cv2
import numpy as np
from PySide6.QtGui import QImage, QPixmap

class ImageManager:
    def __init__(self):
        # Imagen original en RGB (intocable)
        self.original_image = None

        # Parámetros actuales del pipeline
        self.current_params = {
            "brightness": 0,
            "contrast": 1.0
        }

        # Pilas de historial (paramétricas)
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

        # Reiniciar parámetros e historial
        self.current_params = {
            "brightness": 0,
            "contrast": 1.0
        }
        self.undo_stack.clear()
        self.redo_stack.clear()

        return self._process_pipeline()

    # -------------------------------------------------
    # APLICAR NUEVOS PARÁMETROS
    # -------------------------------------------------
    def update_parameters(self, brightness: int, contrast: float) -> QPixmap | None:
        if self.original_image is None:
            return None

        # Guardamos estado anterior en UNDO
        self.undo_stack.append(self.current_params.copy())

        # Actualizamos estado actual
        self.current_params = {
            "brightness": brightness,
            "contrast": contrast
        }

        # Limpiamos REDO porque hay nueva acción
        self.redo_stack.clear()

        return self._process_pipeline()

    # -------------------------------------------------
    # UNDO
    # -------------------------------------------------
    def undo(self) -> QPixmap | None:
        if not self.undo_stack:
            return None

        # Movemos estado actual a REDO
        self.redo_stack.append(self.current_params.copy())

        # Recuperamos último estado de UNDO
        self.current_params = self.undo_stack.pop()

        return self._process_pipeline()

    # -------------------------------------------------
    # REDO
    # -------------------------------------------------
    def redo(self) -> QPixmap | None:
        if not self.redo_stack:
            return None

        # Movemos estado actual a UNDO
        self.undo_stack.append(self.current_params.copy())

        # Recuperamos estado futuro
        self.current_params = self.redo_stack.pop()

        return self._process_pipeline()

    # -------------------------------------------------
    # PIPELINE CENTRAL (NO DESTRUCTIVO)
    # -------------------------------------------------
    def _process_pipeline(self) -> QPixmap:
        """
        Recalcula imagen desde original_image usando current_params
        """

        brightness = self.current_params["brightness"]
        contrast = self.current_params["contrast"]

        # Aplicamos fórmula: imagen * alpha + beta
        processed = cv2.convertScaleAbs(
            self.original_image,
            alpha=contrast,
            beta=brightness
        )

        return self._to_qpixmap(processed)

    # -------------------------------------------------
    # CONVERSIÓN A QPIXMAP
    # -------------------------------------------------
    def _to_qpixmap(self, image: np.ndarray) -> QPixmap:
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