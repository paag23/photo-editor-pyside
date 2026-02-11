# core/image_manager.py
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
import numpy as np
from PySide6.QtGui import QImage, QPixmap

class ImageManager:
    def __init__(self):
        # Imagen original en RGB (intocable)
        self.original_image = None

        # Imagen de trabajo en RGB (editable)
        self.current_image = None

    def load_image(self, path: str) -> QPixmap | None:
        # Cargamos imagen con OpenCV (BGR)
        image_bgr = cv2.imread(path)

        if image_bgr is None:
            return None

        # Convertimos a RGB
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

        # Guardamos copias separadas
        self.original_image = image_rgb.copy()
        self.current_image = image_rgb.copy()

        # Devolvemos la imagen lista para Qt
        return self._to_qpixmap(self.current_image)

    def apply_brightness_contrast(self, brightness: int, contrast: float) -> QPixmap:
        """
        Aplica brillo y contraste usando OpenCV
        brightness: beta (-100 a 100)
        contrast: alpha (0.5 a 3.0)
        """

        if self.original_image is None:
            return None

        # convertScaleAbs aplica: new = image * alpha + beta
        adjusted = cv2.convertScaleAbs(
            self.original_image,
            alpha=contrast,
            beta=brightness
        )

        # Actualizamos imagen de trabajo
        self.current_image = adjusted

        return self._to_qpixmap(self.current_image)

    def reset_image(self) -> QPixmap | None:
        """
        Restaura la imagen original
        """
        if self.original_image is None:
            return None

        self.current_image = self.original_image.copy()
        return self._to_qpixmap(self.current_image)

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