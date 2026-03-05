import numpy as np
from core.operations import Operation, register_filter


@register_filter("WesAndersonOperation")
class WesAndersonOperation(Operation):

    PARAMS = {
        "strength": (0, 200, 100)
    }

    def __init__(self, strength=1.0):
        super().__init__()
        self.strength = strength

    def apply(self, image):

        img = image.astype(np.float32) / 255.0

        contrast_factor = 0.85
        img = img * contrast_factor + (1 - contrast_factor) * 0.5

        brightness_factor = 1.15
        img = np.clip(img * brightness_factor, 0, 1)

        img[:, :, 0] *= 1.08
        img[:, :, 1] *= 1.05
        img[:, :, 2] *= 0.95

        pink_overlay = np.array([1.0, 0.92, 0.92], dtype=np.float32)

        strength = 0.25 * self.strength
        img = img * (1 - strength) + pink_overlay * strength

        return np.clip(img * 255, 0, 255).astype(np.uint8)