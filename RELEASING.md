# Releasing Bookmark Theme Selector

This document covers manual release steps using VS Code tasks and the GitHub CLI (`gh`).

## Prerequisites

- `git` installed and authenticated for this repository
- `gh` installed and authenticated (`gh auth status`)
- PowerShell available (tasks use `pwsh`)

## Recommended Release Flow

1. Update `metadata.txt` version.
2. Add a matching section in `CHANGELOG.md` (for example, `## [0.3.0] - 2026-03-10`).
3. Commit changes and push the branch.
4. Create and push tag `vX.Y.Z`.
5. Run the VS Code task `Release: Package Plugin Zip`.
6. Run the VS Code task `Release: Upload With gh`.

## VS Code Tasks

Open Command Palette and run `Tasks: Run Task`.

- `Release: Package Plugin Zip`
  - Runs `scripts/package_plugin.ps1`
  - Produces `dist/bookmark_theme-X.Y.Z.zip`

- `Release: Upload With gh`
  - Prompts for release version
  - Extracts matching section from `CHANGELOG.md`
  - Uploads zip and creates GitHub release via `gh release create`

## Notes

- The upload task expects tag `vX.Y.Z` to already exist.
- If the release already exists, use `gh release upload` manually to add assets.
- GitHub Actions release automation can still be used in parallel (tag push flow).
