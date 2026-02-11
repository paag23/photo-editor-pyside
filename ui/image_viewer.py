# ui/image_viewer.py

from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


class ImageViewer(QGraphicsView):
    def __init__(self):
        super().__init__()

        # Escena que contendrá los elementos gráficos (la imagen)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # Elemento gráfico que contendrá el pixmap (la imagen)
        self.pixmap_item = None

        # Factor de zoom actual
        self.zoom_factor = 1.0

        # Configuración visual
        self.setRenderHints(self.renderHints())
        self.setDragMode(QGraphicsView.ScrollHandDrag)  # pan con mouse
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

        # Fondo neutro (criterio fotográfico)
        self.setStyleSheet("background-color: #2b2b2b;")

    def set_image(self, pixmap: QPixmap):
        """
        Coloca una imagen nueva en el visor
        """
        self.scene.clear()  # eliminamos cualquier imagen previa
        self.pixmap_item = self.scene.addPixmap(pixmap)

        # Ajustamos la escena al tamaño de la imagen
        self.scene.setSceneRect(self.pixmap_item.boundingRect())

        # Reiniciamos el zoom
        self.resetTransform()
        self.zoom_factor = 1.0

    def wheelEvent(self, event):
        """
        Zoom usando la rueda del mouse
        """
        if self.pixmap_item is None:
            return

        # Sensibilidad del zoom
        zoom_in_factor = 1.25
        zoom_out_factor = 0.8

        # Detectamos dirección de la rueda
        if event.angleDelta().y() > 0:
            zoom = zoom_in_factor
        else:
            zoom = zoom_out_factor

        # Aplicamos el escalado
        self.scale(zoom, zoom)
        self.zoom_factor *= zoom
