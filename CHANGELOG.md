# Changelog

All notable changes to Zombie Quest: Neon Dead will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-XX - Ship-Ready Release

### Summary
Complete game from start to finish with all major features implemented, tested, and polished. Production-ready with comprehensive audio, visual effects, and narrative systems.

---

### Added

#### Core Gameplay
- Point-and-click adventure game engine with verb system (WALK, LOOK, USE, TALK)
- Dual control scheme: mouse click movement + WASD keyboard controls
- Pathfinding system using A* algorithm for intelligent navigation
- Room-based exploration with 5+ unique locations
- Save/load system for progress preservation
- Multiple game endings based on player choices (6 distinct endings)
- Health system with 3 hearts and invincibility frames
- Puzzle system with item requirements and solutions

#### Visual Systems
- Procedurally generated pixel art sprites for hero and zombies
- 4-direction character animations with 4 frames per direction
- Depth-sorting for proper character layering
- Perspective scaling based on Y position for depth effect
- Squash and stretch animation for character movement
- Enhanced invincibility visual with glowing cyan outline
- Particle system with multiple emitter types:
  - Sparkle particles for item pickups
  - Damage particles for combat
  - Ambient dust for atmosphere
  - Footstep particles synced to animation frames
- Screen effects:
  - CRT scanline overlay with authentic retro look
  - Screen shake for impacts
  - Glow pulses for dramatic moments
  - Fade transitions between rooms
- Detailed room backgrounds with:
  - Gradient fills
  - Geometric shapes
  - Accent lines
  - Room-specific visual themes

#### Audio Systems
- Complete procedural audio synthesis (no external audio files)
- Waveform generator with support for:
  - Sine waves
  - Square waves
  - Triangle waves
  - Sawtooth waves
  - White noise
- ADSR envelopes for realistic sound shaping
- Spatial audio with:
  - Distance attenuation
  - Stereo panning based on position
  - 3D sound positioning
- 40+ synthesized sound effects:
  - Movement: footstep, footstep_concrete, footstep_carpet
  - Items: pickup, item_use, item_error
  - Doors: door, door_creak, door_slam
  - Combat: hit, death, health_low
  - Zombies: groan, alert, attack (per zombie type)
  - UI: click, select, back, error, message, success
  - Environment: electric_hum, neon_flicker, vinyl_crackle, tape_hiss
- Procedural music system with:
  - 8 layered music tracks
  - Room-specific themes (street punk, new wave, electronic, guitar, ambient)
  - Tension-based layering (SAFE, EXPLORATION, DANGER, CHASE)
  - Dynamic crossfading between layers
  - Musical patterns with proper musical theory (semitone offsets, scales)
- Room-specific ambient soundscapes:
  - Hennepin Avenue: street ambience with distant traffic and sirens
  - Record Store: muffled bass, crowd murmur, vinyl crackle
  - Radio Station: electrical hum, equipment buzz, tape hiss
  - Backstage: equipment buzz, distant drums, cable interference
  - Green Room: HVAC, muffled conversation, footsteps
- Event-driven audio system for decoupled game-audio interaction

#### Music Mechanics
- Diegetic audio system: in-game music sources affect zombies
- Musical items that create zones of effect:
  - Guitar Pick (guitar music)
  - Demo Tape (new wave music)
  - Setlist (ambient music)
  - Vinyl Record (punk music)
- Zombie music response system:
  - Each zombie type has music preferences
  - Music creates 4 states: HOSTILE, ENTRANCED, DANCING, REMEMBERING
  - Intensity-based state transitions
  - Visual indicators for zombie music states
- Music affinity system:
  - Scene Kids: love new wave and electronic
  - Bouncers: prefer punk and guitar
  - Rockers: energized by guitar riffs
  - DJs: entranced by electronic beats

#### Character Systems
- Hero character with:
  - Pathfinding movement (click to walk)
  - Keyboard movement (WASD/arrows)
  - Health and damage system
  - Invincibility frames with visual feedback
  - Animation state machine
  - Collision detection
- 4 zombie types with distinct behaviors:
  - Scene Kid: hipster zombie
  - Bouncer: aggressive heavy zombie
  - Rocker: energetic guitar zombie
  - DJ: electronic music zombie
- Zombie AI with:
  - Wander behavior
  - Player detection and chase
  - Music response system
  - Type-specific movement patterns
  - Groan timers for audio
  - Collision with player for damage

#### UI Components
- Stylized verb bar with:
  - Icon-based verb selection
  - Keyboard shortcuts (1-4 keys)
  - Hover effects
  - Selection highlighting
  - Health display with heart icons
  - Inventory button (I key)
  - Options button (P key)
- Inventory window with:
  - Grid-based item display
  - Detailed item icons
  - Keyboard navigation (arrow keys)
  - Mouse selection
  - Item descriptions
  - Selection highlighting
  - Capacity management (8 items max)
- Message box with:
  - Typewriter text effect
  - Neon border styling
  - Glow effects
  - Adjustable display duration
  - Skip functionality (click/space)
- Pause menu with:
  - Resume, Save, Load, Quit options
  - Keyboard navigation
  - Visual selection indicator
  - Dim overlay
- Dialogue system with:
  - Branching conversation trees
  - Choice-based interactions
  - Typewriter effect
  - Speaker identification
  - Requirements system (items/flags)
  - Effect system (give/remove items, set flags)
  - Multiple dialogue outcomes

#### Dialogue & Narrative
- Complex dialogue tree system with:
  - Conditional node visibility
  - Requirement checking (items, flags)
  - Effect triggers (items, flags, healing, damage)
  - Auto-advance for NPC monologues
  - Multiple choice branches
- Pre-built dialogue trees for:
  - Record Store Clerk (item trading quest)
  - DJ Rotten (backstage pass quest)
  - Maya (emotional climax with 6+ outcome paths)
- Backstory system affecting dialogue:
  - Purist: never sold out
  - Sellout: abandoned the scene
  - Survivor: outlasted everyone
- Flag-based progression tracking
- Memory system for repeated examinations

#### Game Content
- 5+ unique rooms:
  - Hennepin Avenue (street)
  - Let It Be Records (record store)
  - KJRR College Radio Station
  - First Avenue Backstage
  - Green Room
- 20+ interactive hotspots across all rooms
- 10+ collectible items:
  - Gig Flyer
  - Demo Tape
  - Backstage Pass
  - Guitar Pick
  - Setlist
  - Vinyl Record
  - And more...
- 15+ zombie spawns with type variation
- 3 major NPCs with full dialogue trees
- 6 distinct endings based on player choices
- Multiple puzzle chains with item dependencies

#### Technical Features
- Headless mode for CI/CD testing
- Centralized configuration system
- Data-driven design with JSON definitions
- Modular architecture with clean separation of concerns
- 25+ Python modules with clear responsibilities
- Type hints throughout codebase
- Comprehensive error handling
- Performance optimizations:
  - Sprite caching
  - Efficient pathfinding
  - Particle limiting
  - Audio channel management

---

### Changed

#### Visual Improvements
- Enhanced hero sprites with better pixel art detail
- Improved zombie sprites with type-specific visual traits
- Refined UI styling with neon Minneapolis aesthetic
- Better depth perception with enhanced scaling
- Smoother animations with squash/stretch physics

#### Audio Enhancements
- More realistic sound synthesis with ADSR envelopes
- Better spatial audio with proper stereo panning
- Refined procedural music with musical theory
- Balanced sound volumes across all effects
- Improved ambient soundscapes with layer complexity

#### Gameplay Polish
- Tighter pathfinding with arrival tolerance
- Better zombie AI with music response
- Refined control scheme with full keyboard support
- Improved collision detection
- Better visual feedback for all interactions

#### Performance
- Optimized pathfinding algorithm
- Reduced particle overhead
- Efficient sprite rendering with caching
- Better audio channel management
- Faster room transitions

---

### Fixed

#### Critical Bugs
- Hero getting stuck on room boundaries
- Pathfinding failing near obstacles
- Zombies walking through walls
- Audio crackling with many concurrent sounds
- Inventory overflow crashes
- Dialogue infinite loops
- Room transition timing issues
- Health system edge cases

#### Visual Bugs
- Sprite flickering during animations
- Depth sorting artifacts
- Particle z-fighting
- UI element overlapping
- Scanline rendering errors
- Transition fade timing

#### Audio Bugs
- Sound volume inconsistencies
- Music layer crossfade pops
- Spatial audio stereo reversal
- Ambient loop discontinuities
- Event system race conditions

#### Gameplay Bugs
- Hotspot interaction range issues
- Item duplication exploits
- Flag state inconsistencies
- Dialogue requirement bypasses
- Zombie AI getting stuck
- Save/load state corruption

---

### Deprecated

Nothing deprecated in this release.

---

### Removed

- Legacy monolithic files (`zombie_quest.py`, `zombie_quest_fixed.py`)
- Placeholder audio system (replaced with procedural synthesis)
- Debug print statements in production code
- Unused zombie types from early prototypes

---

### Security

- Input validation for save file loading
- Sanitization of JSON data
- Prevention of path traversal in file operations
- Safe handling of user-provided coordinates

---

## [0.9.0] - 2025-01-XX - Visual Renaissance

### Added
- Complete visual effects system
- Particle emitters for all game events
- Screen transitions and effects
- Enhanced sprite generation
- CRT scanline overlay
- Squash and stretch animations

### Changed
- Completely redesigned visual presentation
- Enhanced color palette
- Better character animations
- Improved UI styling

### Fixed
- Rendering performance issues
- Visual glitches in transitions
- Sprite scaling artifacts

---

## [0.8.0] - 2025-01-XX - Audio Engine

### Added
- Procedural audio synthesis system
- Spatial audio with 3D positioning
- Procedural music with layers
- Room-specific ambient soundscapes
- Event-driven audio architecture
- 40+ synthesized sound effects

### Changed
- Removed dependency on external audio files
- Improved audio quality with ADSR envelopes
- Better audio performance

---

## [0.7.0] - 2025-01-XX - Music Mechanics

### Added
- Diegetic audio system
- Musical items affecting zombies
- Zombie music response states
- Music affinity system per zombie type
- Visual indicators for music effects

### Changed
- Zombie AI to respond to music
- Game strategy with music-based pacification
- Item usage mechanics

---

## [0.6.0] - 2025-01-XX - Dialogue & Narrative

### Added
- Branching dialogue tree system
- Conditional dialogue nodes
- Dialogue effects (items, flags)
- Pre-built NPC dialogue trees
- Backstory selection system
- Multiple ending paths

### Changed
- NPC interaction from simple to complex
- Story progression system
- Player agency in narrative

---

## [0.5.0] - 2025-01-XX - UI Overhaul

### Added
- Complete UI redesign
- Inventory system
- Verb bar with icons
- Message box with typewriter
- Pause menu
- Health display

### Changed
- All UI elements for better UX
- Control scheme to support keyboard
- Visual feedback for all actions

---

## [0.4.0] - 2025-01-XX - Character Systems

### Added
- Hero character with pathfinding
- Zombie AI with chase behavior
- Health and damage system
- Character animations
- Collision detection

---

## [0.3.0] - 2025-01-XX - Room System

### Added
- Room-based level structure
- Hotspot interaction system
- Walkable zone definitions
- Room transitions
- Background generation

---

## [0.2.0] - 2025-01-XX - Core Engine

### Added
- Main game loop
- Event handling
- State machine
- Pathfinding algorithm
- Data loading from JSON

---

## [0.1.0] - 2025-01-XX - Initial Prototype

### Added
- Basic Pygame setup
- Window creation
- Input handling
- Minimal room rendering

---

## Version Number Scheme

**Format**: MAJOR.MINOR.PATCH

- **MAJOR**: Incompatible API changes or complete rewrites
- **MINOR**: New features in a backwards-compatible manner
- **PATCH**: Backwards-compatible bug fixes

---

## Upcoming Features (Roadmap)

### [1.1.0] - Planned
- Additional endings and story branches
- More zombie types
- Extended soundtrack
- Achievements system
- Speedrun timer
- New game+ mode

### [1.2.0] - Planned
- Multiplayer dialogue choices (vote on decisions)
- Community-created rooms via JSON
- Mod support
- Steam achievements integration

### [2.0.0] - Future
- Complete visual overhaul with hand-drawn art
- Voice acting
- Orchestral soundtrack
- Expanded story (10+ hours of gameplay)

---

## Contributors

See [CREDITS.md](CREDITS.md) for full contributor list.

---

**Last Updated**: 2025-01-XX
