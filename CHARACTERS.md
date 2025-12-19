# Zombie Quest - Core Character Sprites

This document describes the 5 new core character sprites created for Zombie Quest, each hand-crafted at 24x48 pixels with 4 animation frames.

## Character Overview

### 1. MAYA - The Lost Bandmate
**File**: `zombie_quest/sprites.py` → `create_maya_sprite(frame)`
**Size**: 24x48 pixels
**Color Scheme**: Purple/Green (transformation colors)

**Description**: Your former bandmate, caught mid-transformation between human and zombie. Half her face remains human with warm skin tones, while the other half has taken on the greenish pallor of the undead. Glowing infected veins pulse across her zombie arm, and her eyes tell two different stories - one human, one supernatural.

**Visual Details**:
- Split face design (human left, zombie right)
- Purple torn band t-shirt
- Black leather pants
- Bass guitar strapped across back
- Wild rocker hair with purple highlights
- One human eye, one glowing zombie eye
- Visible infected veins on zombie arm

**Animation Frames**:
- **Frame 0**: Idle/breathing - Subtle breathing animation
- **Frame 1**: Walking - Movement with bob
- **Frame 2**: Playing bass - Bass guitar in playing position
- **Frame 3**: Transforming - Veins glow intensely across body

**Character Arc**: Maya represents the tragedy of the outbreak - someone you knew personally who's fighting to retain their humanity through music.

---

### 2. JOHNNY CHROME - The Friendly Zombie
**File**: `zombie_quest/sprites.py` → `create_johnny_chrome_sprite(frame)`
**Size**: 24x48 pixels
**Color Scheme**: Chrome/Silver (1950s vintage)

**Description**: A dignified zombie in a vintage 1950s suit who maintains his composure despite decomposition. Johnny is lucid, philosophical, and proves that death doesn't have to mean losing your class. His slicked-back hair is patchy, but he still maintains it with pride.

**Visual Details**:
- Vintage gray suit with perfect creases
- White shirt and dark tie
- Sunglasses hiding hollow eyes
- Unlit cigarette in mouth
- Patchy slicked hair
- Polished shoes
- Sunken zombie cheeks

**Animation Frames**:
- **Frame 0**: Standing dignified - Classic pose
- **Frame 1**: Gesturing - Arm raised in conversation
- **Frame 2**: Contemplating - Hand to chin, philosophical
- **Frame 3**: Grooving - Subtle sway to unheard music

**Dialogue Style**: Philosophical, noir detective vibes. "Death is merely a key change, friend."

---

### 3. THE PROMOTER - The Villain
**File**: `zombie_quest/sprites.py` → `create_promoter_sprite(frame)`
**Size**: 24x48 pixels
**Color Scheme**: Red/Black (sinister 80s excess)

**Description**: The sleazy music industry executive behind the zombie outbreak. Power suit with MASSIVE 80s shoulder pads, gold chains, and a sinister smile that never reaches his eyes. Occult symbols hide in plain sight on his tie, and his contracts promise fame but demand something far darker.

**Visual Details**:
- Red power suit with enormous shoulder pads
- White shirt
- Black tie with hidden occult symbols
- Multiple gold chains
- Slicked hair with product shine
- Expensive black shoes
- Contracts in hand
- Sinister smile with tooth glint

**Animation Frames**:
- **Frame 0**: Intimidating - Power stance with contracts
- **Frame 1**: Scheming - Narrowed eyes, calculating
- **Frame 2**: Ritual casting - Hands raised, symbols glowing
- **Frame 3**: Transforming - Dark aura revealed, eyes glowing red

**Role**: Primary antagonist. His occult business dealings caused the outbreak.

---

### 4. RECORD STORE CLERK - Enhanced NPC
**File**: `zombie_quest/sprites.py` → `create_clerk_sprite(frame)`
**Size**: 24x48 pixels
**Color Scheme**: Flannel red/brown (authentic music nerd)

**Description**: The knowledgeable gatekeeper of underground music culture. Thick-rimmed glasses, flannel shirt over a band tee, perpetual coffee cup nearby. This is someone who lives and breathes music, and they're not impressed unless you prove you're legitimate.

**Visual Details**:
- Red/brown plaid flannel shirt
- Band t-shirt visible at collar
- Blue jeans
- Thick-rimmed glasses with glint
- Messy brown hair
- White sneakers
- Vinyl record in hand
- Coffee cup always nearby

**Animation Frames**:
- **Frame 0**: Flipping through records - Vinyl in hand
- **Frame 1**: Nodding to music - Head bob
- **Frame 2**: Talking - Mouth open, recommending albums
- **Frame 3**: Pointing - Showing you something important

**Personality**: Cool but discerning. "Scene kids only. What have you got?"

---

### 5. DJ ROTTEN - Enhanced NPC
**File**: `zombie_quest/sprites.py` → `create_dj_rotten_sprite(frame)`
**Size**: 24x48 pixels
**Color Scheme**: Punk aesthetic (black leather, bright mohawk)

**Description**: A punk rock zombie DJ who refuses to let death stop the music. Pink mohawk (slightly wilted), leather jacket covered in patches, headphones perpetually on. DJ Rotten is the voice of the underground, broadcasting through the apocalypse.

**Visual Details**:
- Black leather jacket with band patches
- Pink/magenta mohawk (slightly wilted from death)
- Headphones (one cup on ear, one around neck)
- Tight black pants
- Combat boots with laces
- Microphone in hand (when announcing)
- Visible zombie skin tone
- Intense eyes

**Animation Frames**:
- **Frame 0**: Spinning records - Hands on turntables
- **Frame 1**: Announcing - Mic to mouth, shouting
- **Frame 2**: Headbanging - Mohawk swaying
- **Frame 3**: Pointing - Engaging with listener

**Voice**: Raspy zombie voice that still rocks. "Got anything raw for the airwaves?"

---

## Integration with Game

### In game_data.json

Characters are referenced in hotspots using the `"character_sprite"` field:

```json
{
  "name": "Record Clerk",
  "character_sprite": "clerk",
  "verbs": {
    "look": "Description...",
    "talk": "Dialogue..."
  }
}
```

### Sprite Mapping

The game engine maps these IDs to sprite functions:
- `"maya"` → `create_maya_sprite()`
- `"johnny_chrome"` → `create_johnny_chrome_sprite()`
- `"promoter"` → `create_promoter_sprite()`
- `"clerk"` → `create_clerk_sprite()`
- `"dj_rotten"` → `create_dj_rotten_sprite()`

### Current Locations in Game

- **Maya**: Green Room (`green_room`)
- **Johnny Chrome**: Green Room (`green_room`)
- **The Promoter**: Promoter's Office (`promoter_office`)
- **Record Store Clerk**: Record Store (`record_store`)
- **DJ Rotten**: College Radio Station (`college_station`)

---

## Technical Details

### Sprite Format
- **Dimensions**: 24x48 pixels (double the standard 16x32)
- **Format**: PNG with alpha transparency
- **Animation**: 4 frames per character
- **Color Depth**: 32-bit RGBA

### Palette Design Philosophy

Each character has a distinct color palette that:
1. **Communicates personality** (Maya's purple/green = transformation)
2. **Reflects era** (Johnny's chrome = 1950s, Promoter's red = 80s excess)
3. **Aids readability** at low resolution
4. **Creates instant recognition** via silhouette

### Animation System

All sprites use consistent frame timing:
- Frame duration: ~150ms per frame
- Loop style: Continuous (0→1→2→3→0)
- Special frames: Frame 3 typically has unique effects

### Design Principles

1. **Silhouette Recognition**: Each character must be identifiable by outline alone
2. **Period Authenticity**: 1982 Minneapolis punk/new wave aesthetic
3. **Pixel-Perfect Details**: Every pixel serves the character design
4. **Expressive Animation**: Personality visible in movement
5. **Color Coding**: Purple/green = transformation, Chrome = class, Red/black = evil

---

## Testing the Sprites

Run the sprite viewer:
```bash
python test_new_sprites.py
```

This displays all 5 characters with:
- 4 animation frames cycling
- Character names and descriptions
- Frame-by-frame control (SPACE to advance)
- 2x scale for visibility

---

## Future Expansion

Potential additional characters:
- **The Sound Engineer** - Technical zombie who tweaks levels eternally
- **The Groupie** - Superfan who became undead at a show
- **The Roadie** - Eternally loading equipment in/out
- **Prince's Ghost** - Minneapolis music royalty as spectral guide

---

## Credits

These sprites embody:
- 1982 Minneapolis punk/new wave culture
- Period-authentic fashion (shoulder pads, mohawks, flannel)
- Classic adventure game pixel art tradition
- Love for music and the undead

Each character was hand-crafted pixel-by-pixel to create instantly recognizable, expressive designs that enhance the game's narrative and atmosphere.

---

**Last Updated**: 2025-12-19
**Game Version**: Zombie Quest - Minneapolis 1982 Edition
