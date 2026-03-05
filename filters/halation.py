import numpy as np
import cv2
from core.operations import Operation, register_filter


@register_filter("HalationOperation")
class HalationOperation(Operation):

    PARAMS = {
        "strength": (0, 100, 40),
        "radius": (1, 20, 8),
        "threshold": (150, 255, 200)
    }

    def __init__(self, strength=40, radius=8, threshold=200):
        super().__init__()
        self.strength = strength
        self.radius = radius
        self.threshold = threshold

    def apply(self, image):

        img = image.astype(np.float32)

        # luminancia
        lum = cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_RGB2GRAY)

        # máscara de highlights
        mask = (lum > self.threshold).astype(np.float32)

        # blur para crear halo
        k = self.radius * 2 + 1
        halo = cv2.GaussianBlur(mask, (k, k), 0)

        halo = halo[:, :, np.newaxis]

        # glow rojo característico del film
        red_glow = np.zeros_like(img)
        red_glow[:,:,0] = halo[:,:,0] * self.strength * 2

        result = img + red_glow

        return np.clip(result, 0, 255).astype(np.uint8)