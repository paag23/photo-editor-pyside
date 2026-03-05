import numpy as np
import random
from core.operations import Operation, register_filter


@register_filter("FilmGrainOperation")
class FilmGrainOperation(Operation):

    PARAMS = {
        "intensidad": (0, 100, 20)
    }

    def __init__(self, intensidad=20, seed=None):
        super().__init__()
        self.intensidad = intensidad

        # semilla fija por operación
        self.seed = seed if seed is not None else random.randint(0, 1_000_000)

    def apply(self, image):

        rng = np.random.default_rng(self.seed)

        image_array = image.astype(np.int16)

        lum = np.mean(image_array, axis=2, dtype=np.float32) / 255.0

        noise = rng.integers(
            -self.intensidad,
            self.intensidad + 1,
            lum.shape,
            dtype=np.int16
        )

        scale = 0.5 + 0.5 * lum
        noise_scaled = (noise * scale).astype(np.int16)

        noisy_image = np.clip(
            image_array + noise_scaled[:, :, np.newaxis],
            0,
            255
        ).astype(np.uint8)

        return noisy_image