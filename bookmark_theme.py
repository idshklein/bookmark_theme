import json

from qgis.core import QgsApplication, QgsProject, Qgis
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QAction
from .bookmark_theme_dockwidget import BookmarkThemeDockWidget


class BookmarkThemePlugin:
    PAIRS_PROPERTY_SCOPE = "BookmarkTheme"
    PAIRS_PROPERTY_KEY = "pairs"

    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.dockwidget = None
        self._pairs = []

    def initGui(self):
        self.action = QAction("Bookmark Theme Selector", self.iface.mainWindow())
        self.action.triggered.connect(self.show_dock)

        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&Bookmark Theme Selector", self.action)

    def unload(self):
        if self.action is not None:
            self.iface.removePluginMenu("&Bookmark Theme Selector", self.action)
            self.iface.removeToolBarIcon(self.action)
            self.action = None

        if self.dockwidget is not None:
            try:
                self._disconnect_signals()
            except Exception:
                pass
            self.dockwidget.close()
            self.iface.removeDockWidget(self.dockwidget)
            self.dockwidget = None

    def show_dock(self):
        if self.dockwidget is None:
            self.dockwidget = BookmarkThemeDockWidget(self.iface.mainWindow())
            self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockwidget)
            self._connect_signals()
            self._load_pairs()
            self.refresh_sources()
            self.refresh_pair_list()

        self.dockwidget.show()
        self.dockwidget.raise_()

    def _connect_signals(self):
        self.dockwidget.addPairButton.clicked.connect(self.add_pair)
        self.dockwidget.removePairButton.clicked.connect(self.remove_selected_pair)
        self.dockwidget.applyPairButton.clicked.connect(self.apply_selected_pair)
        self.dockwidget.refreshButton.clicked.connect(self.refresh_sources)
        self.dockwidget.themeComboBox.currentIndexChanged.connect(self._update_add_button_state)
        self.dockwidget.bookmarkComboBox.currentIndexChanged.connect(self._update_add_button_state)

        project = QgsProject.instance()
        project.readProject.connect(self.on_project_changed)
        project.cleared.connect(self.on_project_changed)

        project_bookmarks = project.bookmarkManager()
        if project_bookmarks is not None and hasattr(project_bookmarks, "changed"):
            project_bookmarks.changed.connect(self.refresh_sources)

        user_bookmarks = QgsApplication.bookmarkManager()
        if user_bookmarks is not None and hasattr(user_bookmarks, "changed"):
            user_bookmarks.changed.connect(self.refresh_sources)

        theme_collection = project.mapThemeCollection()
        if theme_collection is not None and hasattr(theme_collection, "mapThemesChanged"):
            theme_collection.mapThemesChanged.connect(self.refresh_sources)

    def _disconnect_signals(self):
        if self.dockwidget is None:
            return

        try:
            self.dockwidget.addPairButton.clicked.disconnect(self.add_pair)
            self.dockwidget.removePairButton.clicked.disconnect(self.remove_selected_pair)
            self.dockwidget.applyPairButton.clicked.disconnect(self.apply_selected_pair)
            self.dockwidget.refreshButton.clicked.disconnect(self.refresh_sources)
            self.dockwidget.themeComboBox.currentIndexChanged.disconnect(self._update_add_button_state)
            self.dockwidget.bookmarkComboBox.currentIndexChanged.disconnect(self._update_add_button_state)
        except Exception:
            pass

        project = QgsProject.instance()
        try:
            project.readProject.disconnect(self.on_project_changed)
            project.cleared.disconnect(self.on_project_changed)
        except Exception:
            pass

        project_bookmarks = project.bookmarkManager()
        if project_bookmarks is not None and hasattr(project_bookmarks, "changed"):
            try:
                project_bookmarks.changed.disconnect(self.refresh_sources)
            except Exception:
                pass

        user_bookmarks = QgsApplication.bookmarkManager()
        if user_bookmarks is not None and hasattr(user_bookmarks, "changed"):
            try:
                user_bookmarks.changed.disconnect(self.refresh_sources)
            except Exception:
                pass

        theme_collection = project.mapThemeCollection()
        if theme_collection is not None and hasattr(theme_collection, "mapThemesChanged"):
            try:
                theme_collection.mapThemesChanged.disconnect(self.refresh_sources)
            except Exception:
                pass

    def on_project_changed(self, *args):
        self._load_pairs()
        self.refresh_sources()
        self.refresh_pair_list()

    def refresh_sources(self):
        if self.dockwidget is None:
            return

        previous_theme = self.dockwidget.themeComboBox.currentText()
        previous_bookmark = self.dockwidget.bookmarkComboBox.currentData()
        previous_bookmark_key = None
        if isinstance(previous_bookmark, dict):
            previous_bookmark_key = (
                previous_bookmark.get("source"),
                str(previous_bookmark.get("id", "")),
            )

        self.dockwidget.themeComboBox.blockSignals(True)
        self.dockwidget.bookmarkComboBox.blockSignals(True)

        self.dockwidget.themeComboBox.clear()
        themes = sorted(QgsProject.instance().mapThemeCollection().mapThemes())
        if themes:
            self.dockwidget.themeComboBox.addItems(themes)
            if previous_theme in themes:
                self.dockwidget.themeComboBox.setCurrentText(previous_theme)
        else:
            self.dockwidget.themeComboBox.addItem("<No themes available>")

        self.dockwidget.bookmarkComboBox.clear()
        bookmarks = self._all_bookmarks()
        for bookmark_item in bookmarks:
            self.dockwidget.bookmarkComboBox.addItem(bookmark_item["label"], bookmark_item)

        if not bookmarks:
            self.dockwidget.bookmarkComboBox.addItem("<No bookmarks available>", None)
        elif previous_bookmark_key is not None:
            for index, bookmark_item in enumerate(bookmarks):
                bookmark_key = (bookmark_item.get("source"), str(bookmark_item.get("id", "")))
                if bookmark_key == previous_bookmark_key:
                    self.dockwidget.bookmarkComboBox.setCurrentIndex(index)
                    break

        self.dockwidget.themeComboBox.blockSignals(False)
        self.dockwidget.bookmarkComboBox.blockSignals(False)
        self._update_add_button_state()

    def refresh_pair_list(self):
        if self.dockwidget is None:
            return

        selected_index = self.dockwidget.savedPairComboBox.currentIndex()
        self.dockwidget.savedPairComboBox.clear()

        for pair in self._pairs:
            label = f"{pair['name']}  ·  {pair['theme_name']}  +  [{pair['bookmark_source']}] {pair['bookmark_name']}"
            self.dockwidget.savedPairComboBox.addItem(label, pair)

        if self._pairs:
            if 0 <= selected_index < len(self._pairs):
                self.dockwidget.savedPairComboBox.setCurrentIndex(selected_index)
            else:
                self.dockwidget.savedPairComboBox.setCurrentIndex(0)

    def add_pair(self):
        if self.dockwidget is None:
            return

        theme_name = self.dockwidget.themeComboBox.currentText().strip()
        bookmark = self.dockwidget.bookmarkComboBox.currentData()

        if not theme_name or theme_name == "<No themes available>":
            self._message("No map theme selected.", Qgis.Warning)
            return

        if not isinstance(bookmark, dict):
            self._message("No bookmark selected.", Qgis.Warning)
            return

        pair_name = self.dockwidget.pairNameLineEdit.text().strip()
        if not pair_name:
            pair_name = f"Theme: {theme_name} | Bookmark: {bookmark['name']}"

        pair = {
            "name": pair_name,
            "theme_name": theme_name,
            "bookmark_source": bookmark["source"],
            "bookmark_id": bookmark["id"],
            "bookmark_name": bookmark["name"],
        }

        self._pairs.append(pair)
        self._save_pairs()
        self.refresh_pair_list()
        self.dockwidget.savedPairComboBox.setCurrentIndex(len(self._pairs) - 1)
        self.dockwidget.pairNameLineEdit.clear()

        self._message(f"Saved pair '{pair_name}'.", Qgis.Info)

    def remove_selected_pair(self):
        if self.dockwidget is None:
            return

        index = self.dockwidget.savedPairComboBox.currentIndex()
        if index < 0 or index >= len(self._pairs):
            return

        removed = self._pairs.pop(index)
        self._save_pairs()
        self.refresh_pair_list()
        self._message(f"Removed pair '{removed['name']}'.", Qgis.Info)

    def apply_selected_pair(self, *args):
        if self.dockwidget is None:
            return

        index = self.dockwidget.savedPairComboBox.currentIndex()
        if index < 0 or index >= len(self._pairs):
            self._message("Select a pair to apply.", Qgis.Warning)
            return

        pair = self._pairs[index]
        self._apply_pair(pair)

    def _apply_pair(self, pair):
        theme_applied = self._apply_theme(pair.get("theme_name", ""))
        bookmark_applied = self._apply_bookmark_for_pair(pair)

        if theme_applied and bookmark_applied:
            self._message(f"Applied '{pair['name']}'.", Qgis.Success)
            return

        if theme_applied and not bookmark_applied:
            self._message(
                f"Applied theme only for '{pair['name']}' (bookmark not found).",
                Qgis.Warning,
            )
            return

        if not theme_applied and bookmark_applied:
            self._message(
                f"Applied bookmark only for '{pair['name']}' (theme not found).",
                Qgis.Warning,
            )
            return

        self._message(
            f"Could not apply '{pair['name']}' (theme and bookmark missing).",
            Qgis.Critical,
        )

    def _apply_theme(self, theme_name):
        if not theme_name:
            return False

        project = QgsProject.instance()
        theme_collection = project.mapThemeCollection()
        if theme_name not in theme_collection.mapThemes():
            return False

        layer_tree_view = self.iface.layerTreeView()
        layer_tree_model = layer_tree_view.layerTreeModel() if layer_tree_view else None
        theme_collection.applyTheme(theme_name, project.layerTreeRoot(), layer_tree_model)
        return True

    def _apply_bookmark_for_pair(self, pair):
        bookmark = self._resolve_bookmark(pair)
        if bookmark is None:
            return False

        map_canvas = self.iface.mapCanvas()
        extent = bookmark.extent()
        if hasattr(map_canvas, "setReferencedExtent"):
            map_canvas.setReferencedExtent(extent)
        else:
            map_canvas.setExtent(extent)

        map_canvas.setRotation(bookmark.rotation())
        map_canvas.refresh()
        return True

    def _resolve_bookmark(self, pair):
        source = pair.get("bookmark_source")
        bookmark_id = str(pair.get("bookmark_id", ""))
        bookmark_name = pair.get("bookmark_name", "")

        manager = self._bookmark_manager(source)
        if manager is None:
            return None

        for bookmark in manager.bookmarks():
            if str(bookmark.id()) == bookmark_id:
                return bookmark

        if bookmark_name:
            for bookmark in manager.bookmarks():
                if bookmark.name() == bookmark_name:
                    return bookmark

        return None

    def _bookmark_manager(self, source):
        if source == "project":
            return QgsProject.instance().bookmarkManager()
        if source == "user":
            return QgsApplication.bookmarkManager()
        return None

    def _all_bookmarks(self):
        bookmark_items = []

        project_manager = QgsProject.instance().bookmarkManager()
        if project_manager is not None:
            for bookmark in project_manager.bookmarks():
                bookmark_items.append(
                    {
                        "label": f"[Project] {bookmark.name()}",
                        "source": "project",
                        "id": str(bookmark.id()),
                        "name": bookmark.name(),
                    }
                )

        user_manager = QgsApplication.bookmarkManager()
        if user_manager is not None:
            for bookmark in user_manager.bookmarks():
                bookmark_items.append(
                    {
                        "label": f"[User] {bookmark.name()}",
                        "source": "user",
                        "id": str(bookmark.id()),
                        "name": bookmark.name(),
                    }
                )

        bookmark_items.sort(key=lambda item: item["label"].lower())
        return bookmark_items

    def _load_pairs(self):
        raw = self._read_project_value("[]")
        if isinstance(raw, str):
            try:
                parsed = json.loads(raw)
            except Exception:
                parsed = []
        elif isinstance(raw, list):
            parsed = raw
        else:
            parsed = []

        self._pairs = []
        for pair in parsed:
            if not isinstance(pair, dict):
                continue

            if "theme_name" not in pair or "bookmark_source" not in pair:
                continue

            normalized = {
                "name": str(pair.get("name") or "Unnamed Pair"),
                "theme_name": str(pair.get("theme_name") or ""),
                "bookmark_source": str(pair.get("bookmark_source") or "project"),
                "bookmark_id": str(pair.get("bookmark_id") or ""),
                "bookmark_name": str(pair.get("bookmark_name") or ""),
            }
            self._pairs.append(normalized)

    def _save_pairs(self):
        serialized = json.dumps(self._pairs)
        self._write_project_value(serialized)

    def _read_project_value(self, default_value):
        project = QgsProject.instance()

        if hasattr(project, "customProperty"):
            return project.customProperty(
                f"{self.PAIRS_PROPERTY_SCOPE}/{self.PAIRS_PROPERTY_KEY}",
                default_value,
            )

        if hasattr(project, "readEntry"):
            value, ok = project.readEntry(
                self.PAIRS_PROPERTY_SCOPE,
                self.PAIRS_PROPERTY_KEY,
                default_value,
            )
            return value if ok else default_value

        return default_value

    def _write_project_value(self, value):
        project = QgsProject.instance()

        if hasattr(project, "setCustomProperty"):
            project.setCustomProperty(
                f"{self.PAIRS_PROPERTY_SCOPE}/{self.PAIRS_PROPERTY_KEY}",
                value,
            )
            return

        if hasattr(project, "writeEntry"):
            project.writeEntry(
                self.PAIRS_PROPERTY_SCOPE,
                self.PAIRS_PROPERTY_KEY,
                value,
            )

    def _update_add_button_state(self, *args):
        if self.dockwidget is None:
            return

        theme_name = self.dockwidget.themeComboBox.currentText().strip()
        bookmark = self.dockwidget.bookmarkComboBox.currentData()
        has_theme = bool(theme_name and theme_name != "<No themes available>")
        has_bookmark = isinstance(bookmark, dict)
        self.dockwidget.addPairButton.setEnabled(has_theme and has_bookmark)

    def _message(self, text, level=Qgis.Info):
        self.iface.messageBar().pushMessage("Bookmark Theme", text, level=level, duration=3)
