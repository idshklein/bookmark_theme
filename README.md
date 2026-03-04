# Bookmark Theme Selector (QGIS Plugin)

Bookmark Theme Selector lets you save and apply **paired entries** of:

- a QGIS **Map Theme**
- a **Spatial Bookmark** (Project or User bookmark source)

Applying a pair restores both the selected theme and bookmark view (extent + rotation).

## Features

- Save theme + bookmark as one reusable pair
- Apply and remove saved pairs from a dropdown
- Read bookmarks from both Project and User bookmark managers
- Persist pairs inside the QGIS project metadata (`BookmarkTheme/pairs`)
- Graceful behavior when references are missing:
  - applies theme if bookmark is missing
  - applies bookmark if theme is missing

## Requirements

- QGIS 3.28+

## Installation (Local)

1. Copy this folder into your QGIS profile plugins directory:
   - `.../QGIS/QGIS3/profiles/default/python/plugins/bookmark_theme`
2. Open QGIS.
3. Go to **Plugins → Manage and Install Plugins**.
4. Enable **Bookmark Theme Selector**.

## Usage

1. Open plugin panel from toolbar or **Plugins → Bookmark Theme Selector**.
2. In **New Pair**, pick a Theme and Bookmark.
3. Optionally set a custom pair name.
4. Click **Add Pair**.
5. Select a saved pair from the dropdown and click **Apply**.

## Storage

- Pairs are saved in project metadata under scope/key:
  - Scope: `BookmarkTheme`
  - Key: `pairs`
- Stored value is JSON text.

## Project Structure

- `__init__.py` — QGIS class factory
- `metadata.txt` — plugin metadata
- `bookmark_theme.py` — plugin logic and persistence
- `bookmark_theme_dockwidget.py` — dock widget loader
- `bookmark_theme_dockwidget_base.ui` — UI layout

## Roadmap

- Rename/edit saved pairs in-place
- Reorder pairs
- Optional import/export of pair definitions

## License

MIT — see [LICENSE](LICENSE).
