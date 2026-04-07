# BrickCraft — Minecraft to LEGO Converter

Turn your Minecraft builds into real-life LEGO brick shopping lists.

## Features

- **Upload** `.schem`, `.schematic`, `.litematic` files
- **AI mapping** of 200+ Minecraft block types → nearest LEGO colors
- **Brick optimization** — merges 1×1 into 1×2, 2×4 etc.
- **3D preview** in browser (Three.js)
- **BrickLink XML** export — one-click order
- **LDR file** download for LDraw-compatible viewers

## Quick Start

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000

## Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | Vanilla HTML/CSS/JS, Three.js |
| Backend | Python, FastAPI, nbtlib |
| Color Mapping | Weighted Delta-E color distance |
| Optimization | Greedy layer merge algorithm |
| Export | LDraw (.ldr), BrickLink XML |

## License

MIT
