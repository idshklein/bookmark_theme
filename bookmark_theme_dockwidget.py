import os

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDockWidget


FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "bookmark_theme_dockwidget_base.ui")
)


class BookmarkThemeDockWidget(QDockWidget, FORM_CLASS):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
