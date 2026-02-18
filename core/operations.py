'''
Esto encapsula cada efecto en un módulo independiente.
'''
import cv2
import numpy as np

class Operation:
    def apply(self, image):
        raise NotImplementedError


class BrightnessContrastOperation(Operation):
    def __init__(self, brightness=0, contrast=1.0):
        self.brightness = brightness
        self.contrast = contrast

    def apply(self, image):
        return cv2.convertScaleAbs(
            image,
            alpha=self.contrast,
            beta=self.brightness
        )


class SaturationOperation(Operation):
    def __init__(self, saturation=1.0):
        self.saturation = saturation

    def apply(self, image):
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV).astype(np.float32)
        hsv[..., 1] *= self.saturation
        hsv[..., 1] = np.clip(hsv[..., 1], 0, 255)
        hsv = hsv.astype(np.uint8)
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)


class CurveOperation(Operation):
    def __init__(self, strength=0.0):
        self.strength = strength

    def apply(self, image):
        if abs(self.strength) < 0.01:
            return image

        x = np.arange(256)
        midpoint = 128
        factor = 5 * self.strength
        y = 255 / (1 + np.exp(-(x - midpoint) * factor / 128))
        y = np.clip(y, 0, 255).astype(np.uint8)

        return cv2.LUT(image, y) 