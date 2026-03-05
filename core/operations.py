"""
Encapsula cada efecto como una operación independiente
para el modelo paramétrico no destructivo.
"""

import cv2
import numpy as np
import importlib
import pkgutil


FILTER_REGISTRY = {}

def register_filter(name):
    def decorator(cls):
        FILTER_REGISTRY[name] = cls
        return cls
    return decorator

# =====================================================
# BASE OPERATION
# =====================================================
class Operation:

    def __init__(self):
        self.enabled = True

    def apply(self, image):
        raise NotImplementedError

    def to_dict(self):

        data = {
            "type": self.__class__.__name__,
            "enabled": self.enabled
        }

        # guardar todos los atributos del objeto
        for key, value in self.__dict__.items():

            if key != "enabled":
                data[key] = value

        return data

    @classmethod
    def from_dict(cls, data):

        params = dict(data)

        params.pop("type", None)
        enabled = params.pop("enabled", True)

        op = cls(**params)
        op.enabled = enabled

        return op

# =====================================================
# BRIGHTNESS / CONTRAST
# =====================================================

@register_filter("BrightnessContrast")
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
@register_filter("Saturation")
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
@register_filter("Curve")
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
@register_filter("Blur")
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
@register_filter("Sharpen")
class SharpenOperation(Operation):

    PARAMS = {
        "amount": (0, 300, 100),
        "radius": (1, 15, 5)
    }

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
            "type": "FilmGrainOperation",
            "intensidad": self.intensidad,
            "seed": self.seed,
            "enabled": self.enabled
        }

    @classmethod
    def from_dict(cls, data):
        op = cls(
            intensidad=data["intensidad"],
            seed=data.get("seed")
        )
        op.enabled = data["enabled"]
        return op
# ----------------------------------------
# CARGAR Filtros Plugins
# ----------------------------------------
def load_filters():
    import filters

    for loader, module_name, is_pkg in pkgutil.iter_modules(filters.__path__):
        importlib.import_module(f"filters.{module_name}")

print("Filtros registrados:", FILTER_REGISTRY)