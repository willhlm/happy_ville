# Opening Sequence Design — False Heaven Structure

## Design Goal
Create an opening where the player willingly accepts a benevolent authority, only to later realize they were manipulated.

The twist must come from player interpretation, not exposition.

---

## Core Emotional Arc
Curiosity → Comfort → Trust → Duty → Unease → Suspicion → Defiance

---

## High Level Flow

### Phase 1 — Living Forest
No combat. Player learns interaction and movement through environment.

### Phase 2 — The Ascent Trigger
Player voluntarily interacts with altar.

### Phase 3 — Heaven
Perfect, symmetrical, controlled environment.
The guide appears and assigns a mission.

### Phase 4 — Player Choice
Player may attack guide at any time.

### Phase 5 — World Quest
Player defeats other guardians, slowly realizing something is wrong.

---

## Practical Implementation Notes

### Transition to Heaven
Do NOT hard fade and load a new level.

Instead:
1. Lock player movement for 0.3s
2. Pull particles upward
3. Reduce ambient sound
4. Desaturate colors
5. Replace skybox
6. Swap nearby tiles (local radius only)
7. Restore player control

Total duration: ~2 seconds

Reason:
A fade implies cutscene.
A transformation implies reality change.

---

### Player Control
Never remove control longer than 1 second.
Player must feel present during world shift.

---

### Guide Encounter
Guide never attacks first.
Dialogue minimal.
No UI confirmation of morality.

---

### Suspicion Building
Each later boss:
- defensive behavior
- peaceful arena
- reacts to player aggression

---

### Attack Input
Player can always attack guide.
No prompts, no warnings.

---

## Ending Rules

Obedience Ending:
World becomes static and calm.

True Ending:
World becomes imperfect but alive.

