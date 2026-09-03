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
├── scripts/
│   ├── ibge_uf.py                # UF codes, IBGE download, hover merge + tiles
│   ├── build_municipality.py     # National race CSV + malha → municipality_{UF}.geojson
│   ├── build_census_tract.py     # National race CSV + setor malha → census_tract_{UF}.geojson
│   ├── build_density_clusters.py # Adjacent setores by density → cluster_{UF}_z3…z6.geojson
│   └── build_municipality_rj.py  # Wrapper: build_municipality.py RJ
├── notebooks/
│   └── treat_2022.ipynb      # Census + setor geometry → race GeoJSON
├── docs/
│   ├── docs.md               # Zoom, density, data schema, legend filter, two-card chrome, footer
│   ├── fontes.md             # IBGE download URLs and raw-file caveats
│   ├── local-setup.md        # How to merge tiles and serve locally
│   └── structure.md          # This file
├── assets/                   # Optional extras (not in git; unused by the current UI)
├── tiles/                    # tiles/{UF}/zoomN-N/tiles.mbtiles (27 UFs; see AGENTS.md)
└── data/                     # gitignored: merged MBTiles, GeoJSON, raw census
```

`data/` and `dots/` are local-only. Rebuild the file `config.json` expects with:

```sh
mkdir -p data/tiles
# --no-tile-size-limit keeps SP+MG z7 (~508KB); default 500KB/tile drops it.
tile-join -f --no-tile-size-limit -o data/tiles/censo2022.mbtiles tiles/*/*/tiles.mbtiles
```
