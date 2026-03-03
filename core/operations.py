"""
Encapsula cada efecto como una operación independiente
para el modelo paramétrico no destructivo.
"""

import cv2
import numpy as np


# =====================================================
# BASE OPERATION
# =====================================================

class Operation:
    def __init__(self):
        self.enabled = True

    def apply(self, image):
        raise NotImplementedError

    def to_dict(self):
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data):
        raise NotImplementedError


# =====================================================
# BRIGHTNESS / CONTRAST
# =====================================================

class BrightnessContrastOperation(Operation):
    def __init__(self, brightness=0, contrast=1.0):
        super().__init__()
        self.brightness = brightness
        self.contrast = contrast

    def apply(self, image):
        if not self.enabled:
            return image

        result = image.astype(np.float32)
        result = result * self.contrast + self.brightness
        result = np.clip(result, 0, 255)

        return result.astype(np.uint8)

    def to_dict(self):
        return {
            "type": "BrightnessContrast",
            "brightness": self.brightness,
            "contrast": self.contrast,
            "enabled": self.enabled
        }

    @classmethod
    def from_dict(cls, data):
        op = cls(data["brightness"], data["contrast"])
        op.enabled = data["enabled"]
        return op


# =====================================================
# SATURATION
# =====================================================

class SaturationOperation(Operation):
    def __init__(self, saturation=1.0):
        super().__init__()
        self.saturation = saturation

    def apply(self, image):
        if not self.enabled:
            return image

        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV).astype(np.float32)

        hsv[..., 1] *= self.saturation
        hsv[..., 1] = np.clip(hsv[..., 1], 0, 255)

        hsv = hsv.astype(np.uint8)

        return cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)

    def to_dict(self):
        return {
            "type": "Saturation",
            "saturation": self.saturation,
            "enabled": self.enabled
        }

    @classmethod
    def from_dict(cls, data):
        op = cls(data["saturation"])
        op.enabled = data["enabled"]
        return op


# =====================================================
# CURVE (S-CURVE SIMPLE)
# =====================================================

class CurveOperation(Operation):
    def __init__(self, strength=0.0):
        super().__init__()
        self.strength = strength

    def apply(self, image):
        if not self.enabled:
            return image

        if abs(self.strength) < 0.01:
            return image

        x = np.arange(256)
        midpoint = 128
        factor = 5 * self.strength

        y = 255 / (1 + np.exp(-(x - midpoint) * factor / 128))
        y = np.clip(y, 0, 255).astype(np.uint8)

        return cv2.LUT(image, y)

    def to_dict(self):
        return {
            "type": "Curve",
            "strength": self.strength,
            "enabled": self.enabled
        }

    @classmethod
    def from_dict(cls, data):
        op = cls(data["strength"])
        op.enabled = data["enabled"]
        return op


# =====================================================
# BLUR
# =====================================================

class BlurOperation(Operation):
    def __init__(self, kernel_size=5):
        super().__init__()
        self.kernel_size = kernel_size

    def apply(self, image):
        if not self.enabled:
            return image

        k = self.kernel_size

        if k % 2 == 0:
            k += 1

        return cv2.GaussianBlur(image, (k, k), 0)

    def to_dict(self):
        return {
            "type": "Blur",
            "kernel_size": self.kernel_size,
            "enabled": self.enabled
        }

    @classmethod
    def from_dict(cls, data):
        op = cls(data["kernel_size"])
        op.enabled = data["enabled"]
        return op


# =====================================================
# SHARPEN (Unsharp Mask)
# =====================================================

class SharpenOperation(Operation):
    def __init__(self, amount=1.0, radius=3):
        super().__init__()
        self.amount = amount
        self.radius = radius

    def apply(self, image):
        if not self.enabled:
            return image

        k = self.radius

        if k % 2 == 0:
            k += 1

        blurred = cv2.GaussianBlur(image, (k, k), 0)

        image_float = image.astype(np.float32)
        blurred_float = blurred.astype(np.float32)

        mask = image_float - blurred_float
        sharpened = image_float + self.amount * mask

        sharpened = np.clip(sharpened, 0, 255)

        return sharpened.astype(np.uint8)

    def to_dict(self):
        return {
            "type": "Sharpen",
            "amount": self.amount,
            "radius": self.radius,
            "enabled": self.enabled
        }

    @classmethod
    def from_dict(cls, data):
        op = cls(data["amount"], data["radius"])
        op.enabled = data["enabled"]
        return op
    
# ----------------------------------------
# FILTRO  FilmGrainOperation
# ----------------------------------------
class FilmGrainOperation(Operation):
    def __init__(self, intensidad=20):
        super().__init__()
        self.intensidad = intensidad

    def apply(self, image):
        if not self.enabled:
            return image

        image_array = image.astype(np.int16)

        lum = np.mean(image_array, axis=2, dtype=np.float32) / 255.0
        noise = np.random.randint(
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

    def to_dict(self):
        return {
            "type": "FilmGrain",
            "intensidad": self.intensidad,
            "enabled": self.enabled
        }

    @classmethod
    def from_dict(cls, data):
        op = cls(data["intensidad"])
        op.enabled = data["enabled"]
        return op