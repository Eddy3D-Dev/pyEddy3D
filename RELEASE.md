# Release Guide

Steps to publish a GitHub release for pyEddy3D.

1. Ensure working tree is clean and tests pass:
   - `uv run pytest`
2. Update version (already bumped to 1.0.0) and changelog if needed.
3. Commit changes:
   - `git add pyproject.toml CHANGELOG.md`
   - `git commit -m "Release v1.0.0"`
4. Tag the release:
   - `git tag -a v1.0.0 -m "pyEddy3D v1.0.0"`
5. Push main and tags to GitHub:
   - `git push origin main --tags`
6. Create a GitHub release from tag `v1.0.0` and paste notes from `CHANGELOG.md`.
7. (Optional) Build and publish to PyPI if desired:
   - `uv build`
   - `uv publish` (requires credentials)
