import numpy as np
import cv2
from core.operations import Operation, register_filter


@register_filter("BloomOperation")
class BloomOperation(Operation):

    PARAMS = {
        "strength": (0, 100, 35),
        "radius": (1, 25, 12)
    }

    def __init__(self, strength=35, radius=12):
        super().__init__()
        self.strength = strength
        self.radius = radius

    def apply(self, image):

        img = image.astype(np.float32)

        k = self.radius * 2 + 1

        blur = cv2.GaussianBlur(img, (k, k), 0)

        result = img + (blur - img) * (self.strength / 100.0)

        return np.clip(result, 0, 255).astype(np.uint8)