# Zombie Quest - Narrative Systems Quick Start Guide

## How to Experience the New Narrative Features

### 1. Protagonist Backstory

**Where it's set:** `game_data.json` line 26

**Current Selection:** `"purist"` (can be changed to `"sellout"` or `"survivor"`)

**To change your backstory:**
```json
"selected_backstory": "sellout"  // or "purist" or "survivor"
```

This will change:
- How Maya reacts to you in the rooftop confrontation
- Which dialogue options are available
- Memory reflections throughout the game

---

### 2. Memory System (Progressive Hotspot Text)

**How to trigger:**
1. Look at any hotspot once → See standard description
2. Look at the same hotspot again → See deeper observation
3. Look a third time → See personal memory or reflection
4. Look 3+ times → 30% chance of triggering a random backstory/location memory

**Best hotspots to revisit:**
- Poster Kiosk (Hennepin Avenue)
- Listening Booth (Record Store)
- Poster Wall (College Radio)
- Vintage Couch (Green Room)
- Maya (Rooftop Confrontation)

**Example progression (Poster Kiosk):**
- 1st look: "Flyers for Husker Du and The Suburbs flutter..."
- 2nd look: "Beneath the fresh flyers, you spot older ones—bands that never made it..."
- 3rd look: "Your own band's flyer used to hang here. Maya designed it..."

---

### 3. Maya Confrontation

**How to reach:**
Navigate to the rooftop_confrontation room (ID: `"rooftop_confrontation"`)

**Location setup:** Add a door/transition from green_room to rooftop_confrontation:
```json
{
  "name": "Rooftop Stairs",
  "rect": [X, Y, W, H],
  "walk_position": [X, Y],
  "verbs": {
    "look": "Stairs leading up to the rooftop. You sense something waiting there.",
    "use": "You climb the stairs toward the rooftop."
  },
  "target_room": "rooftop_confrontation",
  "target_position": [50, 175],
  "transition_verb": "use"
}
```

**How it works:**
1. Talk to Maya on the rooftop
2. Your dialogue options change based on your backstory
3. Each choice leads to different emotional beats
4. Final choices determine which ending flags are set

**Key Maya dialogue flags:**
- `maya_saved` → Leads to good endings
- `maya_abandoned` → Leads to selfish artist ending
- `accepted_transformation` → Leads to transcendence ending
- `walked_away` → Leads to human ending

---

### 4. Four Endings

**How endings are triggered:**
Endings are checked automatically when `trigger_ending()` is called in the engine.

**To manually trigger ending check:**
```python
# In engine.py or wherever appropriate
ending_id = self.check_ending_conditions()
if ending_id:
    self.trigger_ending(ending_id)
```

**Ending Conditions:**

#### Together in the Neon (Best Ending)
- ✅ Required: `maya_saved`, `maya_forgiven`
- ❌ Forbidden: `maya_abandoned`, `chose_selfishness`

#### Solo in the Spotlight (Dark Ending)
- ✅ Required: `maya_abandoned`
- ❌ Forbidden: `maya_saved`

#### Eternal Groove (Transcendent Ending)
- ✅ Required: `accepted_transformation`, `maya_transformed`
- ❌ Forbidden: `rejected_transformation`

#### Walking Away (Bittersweet Ending)
- ✅ Required: `walked_away`, `chose_humanity`
- ❌ Forbidden: `accepted_transformation`, `stayed_for_show`

---

### 5. Testing the Systems

**Test Memory System:**
```bash
./run_game.sh
# In game: Look at the same hotspot 3-5 times in a row
# Should see different text each time
```

**Test Maya Dialogue:**
```bash
# 1. Edit game_data.json to set different backstories
# 2. Navigate to rooftop_confrontation
# 3. Talk to Maya
# 4. Try different dialogue choices
# 5. Check which flags are set in engine.game_flags
```

**Test Endings:**
```bash
# 1. Play through to rooftop confrontation
# 2. Make choices that set specific flags
# 3. Call trigger_ending() or check_ending_conditions()
# 4. Verify correct ending displays
```

---

### 6. Debug Commands (if needed)

**Check current flags:**
```python
print(self.game_flags)  # In engine.py
```

**Manually set flags for testing:**
```python
# In engine.py __init__ or anywhere
self.game_flags["maya_saved"] = True
self.game_flags["maya_forgiven"] = True
```

**Check memory system state:**
```python
# In engine.py
print(self.memory_system.hotspot_memories)
print(self.memory_system.get_examination_count("hennepin_outside", "Poster Kiosk"))
```

**Test specific ending:**
```python
# In engine.py
self.trigger_ending("together")  # Force specific ending
```

---

### 7. Recommended Play Flow

**First Playthrough (Purist Path):**
1. Start as The Purist
2. Examine hotspots 2-3 times each to see progressive text
3. Navigate to green room
4. (Add transition to rooftop if needed)
5. Go to rooftop, talk to Maya
6. Choose honest/vulnerable options
7. Aim for "Together in the Neon" ending

**Second Playthrough (Sellout Path):**
1. Change backstory to "sellout"
2. Go directly to rooftop confrontation
3. Choose defensive/cruel options
4. Experience "Solo in the Spotlight" ending

**Third Playthrough (Transcendence Path):**
1. Any backstory
2. Talk to Maya on rooftop
3. Choose transformation/evolution options
4. Accept transformation when offered
5. Experience "Eternal Groove" ending

---

### 8. Integration Checklist

To fully integrate the narrative systems:

- [x] Protagonist backstory loaded from game_data.json
- [x] Memory system tracks hotspot examinations
- [x] Memory system provides progressive text
- [x] Maya dialogue tree created with 25+ nodes
- [x] Maya dialogue integrated into engine
- [x] Four endings defined in game_data.json
- [x] Ending system checks flags
- [x] Ending system displays appropriate ending
- [ ] **TODO:** Add transition from green_room to rooftop_confrontation
- [ ] **TODO:** Add trigger for ending check (e.g., when entering final_stage)
- [ ] **TODO:** Add UI/visual feedback for memory unlocks (optional)

---

### 9. File Locations

**Protagonist Data:** `/home/user/Zombie-Quest/game_data.json` (lines 2-27)
**Endings Data:** `/home/user/Zombie-Quest/game_data.json` (lines 120-161)
**Maya Room:** `/home/user/Zombie-Quest/game_data.json` (lines 785-856)
**Final Stage Room:** `/home/user/Zombie-Quest/game_data.json` (lines 857-918)
**Maya Dialogue:** `/home/user/Zombie-Quest/zombie_quest/dialogue.py` (lines 479-872)
**Memory System:** `/home/user/Zombie-Quest/zombie_quest/memory.py` (entire file)
**Engine Integration:** `/home/user/Zombie-Quest/zombie_quest/engine.py` (imports, init, hotspot handling, ending methods)

---

### 10. Known Issues & Solutions

**Issue:** Maya dialogue not appearing
**Solution:** Verify "maya" is in `self.dialogue_trees` dict (line 105 of engine.py)

**Issue:** Progressive text not working
**Solution:** Verify memory_system.record_examination() is called in perform_hotspot_action()

**Issue:** Wrong ending triggered
**Solution:** Check flag conditions in game_data.json match dialogue.py flag setting

**Issue:** Can't reach rooftop
**Solution:** Add hotspot transition from green_room to rooftop_confrontation

**Issue:** Memory spam
**Solution:** Memories only trigger 30% of the time on 3+ examinations (intended behavior)

---

## Quick Reference: Flag Names

### Backstory Flags (Auto-set)
- `backstory_sellout`
- `backstory_purist`
- `backstory_survivor`
- `knows_industry` (sellout)
- `burned_bridges` (sellout)
- `scene_respect` (purist)
- `uncompromising` (purist)
- `seen_darkness` (survivor)
- `weathered` (survivor)

### Maya Dialogue Flags (Set during confrontation)
- `maya_saved`
- `maya_forgiven`
- `maya_abandoned`
- `maya_transformed`
- `player_transformed`
- `accepted_transformation`
- `rejected_transformation`
- `chose_selfishness`
- `maya_acceptance`
- `guilt_path`
- `cruel_choice`
- `maya_lost`
- `redemption_achieved`
- `bittersweet_ending`
- `stayed_for_show`
- `last_show_together`

### Ending Flags (Required for specific endings)
- `walked_away`
- `chose_humanity`

---

## Support

For detailed implementation info, see: `NARRATIVE_SYSTEMS_IMPLEMENTATION.md`

For code issues: Check syntax with `python3 -m py_compile zombie_quest/*.py`

For JSON issues: Validate with `python3 -c "import json; json.load(open('game_data.json'))"`

---

**Last Updated:** December 19, 2025
**Status:** ✅ Ready for playtesting
