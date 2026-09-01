# Project structure

```
dotmap/
├── AGENTS.md                 # Instructions for coding agents
├── README.md                 # How to build tiles and serve the map locally
├── index.html                # Map UI and all Mapbox GL JS logic
├── debugger.html             # OpenLayers inspector for local PBF tiles
├── server.py                 # Optional Flask static server (port 8000)
├── config.json               # tileserver-gl config (censo2022 MBTiles)
├── cors_settings.json        # CORS allowlist used when hosting tiles
├── makefiles.sh              # Dot-density + Tippecanoe pipeline (pass a UF)
├── pyproject.toml            # Python 3.12+ deps via uv
├── package.json              # Minimal Node deps (sqlite3)
├── js/
│   ├── map.js                # Empty placeholder (logic lives in index.html)
│   └── events.js             # Empty placeholder
├── notebooks/
│   └── treat_2022.ipynb      # Census + setor geometry → race GeoJSON
├── docs/
│   ├── docs.md               # Zoom, density, data schema, legend behavior
│   ├── local-setup.md        # How to merge tiles and serve locally
│   └── structure.md          # This file
├── assets/                   # Logo (not in git; header 404s without it)
├── tiles/                    # Per-zoom MBTiles committed in the repo
└── data/                     # gitignored: merged MBTiles, GeoJSON, raw census
```

`data/` and `dots/` are local-only. Rebuild the file `config.json` expects with:

```sh
mkdir -p data/tiles
tile-join -f -o data/tiles/censo2022.mbtiles tiles/*/tiles.mbtiles
```
