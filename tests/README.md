# Zombie Quest Test Suite

Production-quality test coverage for the Zombie Quest game engine.

## Test Coverage

### Test Files

- **test_engine.py** (50+ tests) - Game engine core functionality
  - Initialization and setup
  - State transitions (playing ↔ paused ↔ game_over)
  - Event handling (keyboard, mouse, UI)
  - Room transitions with state preservation
  - Hotspot interactions with all verb types
  - Damage and healing mechanics
  - Dialogue effect application
  - Coordinate conversions
  - Inventory management

- **test_rooms.py** (30+ tests) - Room system
  - Room loading from JSON
  - Hotspot detection and collision
  - Message selection with verb/outcome combinations
  - Walkability mask queries
  - Priority regions (depth sorting)
  - Zombie spawning
  - Background configuration parsing

- **test_pathfinding.py** (25+ tests) - A* pathfinding
  - Algorithm correctness
  - No-path scenarios
  - Diagonal movement with corner-cutting prevention
  - Nearest walkable cell finding
  - Edge cases (start=goal, unwalkable start)
  - Coordinate conversions (world ↔ grid)
  - Neighbor generation
  - Heuristic calculations

- **test_integration.py** (20+ tests) - End-to-end integration
  - Hero movement + pathfinding + room bounds
  - Zombie AI chasing + collision + damage
  - Room transition + inventory + flags persistence
  - Full dialogue tree traversal with effects
  - Combat mechanics integration
  - Visual effects integration
  - Multi-system interactions

- **test_characters.py** - Character system (existing)
- **test_effects.py** - Visual effects (existing)
- **test_dialogue.py** - Dialogue system (existing)
- **test_ui.py** - UI components (existing)
- **test_config.py** - Configuration (existing)
- **test_save_system.py** - Save/load functionality (existing)

### Mock Infrastructure (conftest.py)

Production-quality test fixtures and mocks:

- `MockPygameDisplay` - Prevents window creation in tests
- `MockAudioManager` - Tracks audio events without sound
- `MockRoom` - Lightweight room for isolated testing
- `MockHero` - Simplified hero without sprite loading
- Reusable fixtures for rooms, heroes, zombies, hotspots, items
- Test data generators
- Utility functions for common assertions

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_engine.py
pytest tests/test_rooms.py
pytest tests/test_pathfinding.py
pytest tests/test_integration.py
```

### Run Tests with Coverage
```bash
pytest --cov=zombie_quest --cov-report=html
```

### Run Integration Tests Only
```bash
pytest -m integration
```

### Run Tests with Verbose Output
```bash
pytest -v
```

### Run Specific Test
```bash
pytest tests/test_engine.py::TestEngineInitialization::test_engine_creates_successfully
```

## Headless Validation

The game includes a comprehensive headless validation mode that runs 100+ frames:

```bash
python main.py --headless
```

With verbose output:
```bash
python main.py --headless --verbose
```

This validates:
- Hero position changes
- Zombie AI updates
- Particle system bounds
- State machine validity
- No crashes during gameplay

## Test Organization

Tests follow AAA pattern (Arrange, Act, Assert):

```python
def test_feature(self, fixture):
    # Arrange - set up test conditions
    engine = fixture
    initial_state = engine.state

    # Act - perform the action
    engine.change_state(GameState.PAUSED)

    # Assert - verify results
    assert engine.state == GameState.PAUSED
    assert engine.state != initial_state
```

## Test Markers

- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.headless` - Headless-compatible tests

## Writing New Tests

1. Add test file in `tests/` directory
2. Import necessary modules and fixtures
3. Use descriptive test names: `test_<feature>_<scenario>`
4. Use fixtures from conftest.py for common setup
5. Mock pygame display/audio to prevent window creation
6. Group related tests in classes

Example:
```python
import pytest
from zombie_quest.engine import GameEngine

class TestMyFeature:
    """Test my new feature."""

    def test_feature_works(self, integration_engine):
        """Feature works correctly in normal case."""
        engine = integration_engine
        # Test implementation
        assert True

    def test_feature_edge_case(self, integration_engine):
        """Feature handles edge case."""
        engine = integration_engine
        # Test edge case
        assert True
```

## Continuous Integration

Tests are designed to run in CI environments:
- No window creation (mocked display)
- No audio output (mocked audio)
- Fast execution
- Deterministic results
- Clear failure messages

## Test Coverage Goals

- **Engine**: 90%+ coverage of core game loop
- **Rooms**: 85%+ coverage of room system
- **Pathfinding**: 95%+ coverage (critical algorithm)
- **Characters**: 80%+ coverage
- **UI**: 75%+ coverage
- **Integration**: Key user flows covered

## Troubleshooting

### Pygame Display Errors
If tests fail with display errors, ensure pygame display is mocked:
```python
@pytest.fixture
def my_test(mock_display):
    # Your test code
    pass
```

### Import Errors
Ensure zombie_quest package is importable:
```bash
# From project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Slow Tests
Use pytest-xdist for parallel execution:
```bash
pip install pytest-xdist
pytest -n auto
```

## Future Enhancements

- [ ] Performance benchmarking tests
- [ ] Stress tests (1000+ zombies)
- [ ] Memory leak detection
- [ ] Save file corruption handling
- [ ] Network multiplayer tests (if added)
- [ ] Accessibility testing
