# Testing

- **Headless validation** - `python main.py --headless` must pass before commits (draws every frame; rendering crashes fail it)
- **Pytest suite** - ~294 tests in `tests/`; run `pytest tests/ -q` before commits
- **Room transitions** - Verify pathfinding still works after room edits
- **Visual review** - `python main.py --headless --screenshot-dir build/screens` dumps per-room frames; look at them after visual changes
