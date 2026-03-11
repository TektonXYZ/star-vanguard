# Star Vanguard — Deep Space Recovery

A space shooter with fixed-map exploration, camera following, and healing mechanics.

## Story

Year 2197. The Andromeda Expeditionary Force has sent you, Commander, to recover lost resources from the debris field of the fallen Titan Station.

Your mission: Extract quantum crystals from asteroids, collect repair nanites from damaged supply drones, and survive the automated defense drones that still patrol the wreckage.

The Vanguard-7 is humanity's last hope for the journey home.

## Features

- **Fixed World Map** — 3000x3000 world with boundaries (no wrapping)
- **Camera Following** — Ship stays centered, world moves around you
- **Healing Drones** — Green plus-sign drones that restore 25 hull when destroyed
- **Resource Collection** — Destroy asteroids for crystals
- **Combat** — Fight enemy patrol drones
- **Particle Effects** — Explosions, engine trails, glowing effects

## Controls

- **WASD / Arrow Keys** — Move and rotate ship
- **SPACE** — Fire projectile
- **R** — Restart (when destroyed)

## Installation

```bash
pip install pygame
python star_vanguard.py
```

## Gameplay Tips

- Watch your hull bar (top left) — seek healing drones when low
- Green + drones heal you, red enemies damage you
- Collect crystals from gray asteroids
- Stay within the cyan world boundary
- Use your minimap awareness to find targets

## Technical

Built with Python and Pygame. No external assets required.
