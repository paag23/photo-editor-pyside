import numpy as np
import cv2
import random
from core.operations import Operation, register_filter


@register_filter("PortraGrainOperation")
class PortraGrainOperation(Operation):

    PARAMS = {
        "strength": (0, 100, 25),
        "size": (1, 5, 2)
    }

    def __init__(self, strength=25, size=2, seed=None):
        super().__init__()

        self.strength = strength
        self.size = size
        self.seed = seed if seed else random.randint(0, 1_000_000)

    def apply(self, image):

        print("PORTRA APPLY:", self.strength, self.size)

        rng = np.random.default_rng(self.seed)

        img = image.astype(np.float32)

        h, w, c = img.shape

        # ruido base
        noise = rng.normal(0, 1, (h, w, 3)).astype(np.float32)

        # suavizar ruido → grano más orgánico
        k = self.size * 2 + 1
        noise = cv2.GaussianBlur(noise, (k, k), 0)

        # luminancia
        lum = np.mean(img, axis=2) / 255.0

        # más grano en sombras
        grain_strength = (1 - lum) * (self.strength / 100.0)

        grain_strength = grain_strength[:, :, np.newaxis]

        grain = noise * grain_strength * 300

        noise[:,:,0] *= 1.2
        noise[:,:,1] *= 0.9
        noise[:,:,2] *= 1.1

        result = img + grain

        result = np.clip(result, 0, 255)

        return result.astype(np.uint8)