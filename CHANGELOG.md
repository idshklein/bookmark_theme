# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

### Added
- Generate QGIS Print Layouts from saved pairs
- Layout grouping support on pairs (`layout_group`) for batch layout generation
- Per-pair aspect-ratio option (`preserve_aspect_ratio`) for bookmark extent fitting
- Optional map labels in generated layouts based on pair names

### Changed
- Saved pairs now display layout group details in the dropdown when present
- Pair persistence schema extended with backward-compatible optional fields

## [0.2.0] - 2026-03-08

### Added
- GitHub Actions workflow to package and publish tagged releases
- Automated extraction of changelog section as GitHub release notes

### Changed
- Bumped plugin version to `0.2.0` in metadata

## [0.1.0] - 2026-03-04

### Added
- Initial QGIS plugin scaffold
- Dock UI for saving/applying Theme + Bookmark pairs
- Saved pairs dropdown management (apply/remove)
- Project-level pair persistence under `BookmarkTheme/pairs`
- Support for both Project and User bookmark sources
