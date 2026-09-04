# Project structure

```
dotmap/
├── AGENTS.md                 # Instructions for coding agents
├── README.md                 # How to build tiles and serve the map locally
├── index.html                # Map UI and all MapLibre + PMTiles logic
├── debugger.html             # Legacy OpenLayers XYZ inspector (not the map path)
├── server.py                 # Optional Flask static server (port 8000, Range for PMTiles)
├── config.json               # Unused tileserver-gl leftover
├── cors_settings.json        # CORS allowlist used when hosting tiles
├── makefiles.sh              # Dot-density + Tippecanoe pipeline (pass a UF)
├── pyproject.toml            # Python 3.12+ deps via uv
├── package.json              # Minimal Node deps (sqlite3)
├── js/
│   ├── map.js                # Empty placeholder (logic lives in index.html)
│   └── events.js             # Empty placeholder
├── scripts/
│   ├── ibge_uf.py                # UF codes, IBGE download, hover merge + tiles
│   ├── themes.py                 # Race/income/deaths fields, sources, units and density scales
│   ├── build_municipality.py     # Themed CSV + municipal malha → hover GeoJSON
│   ├── build_census_tract.py     # Themed CSV + setor malha → detailed GeoJSON
│   ├── build_density_clusters.py # Themed adjacent setores → cluster_{UF}_z3…z6.geojson
│   ├── serve.py                  # Static server with HTTP Range for PMTiles
│   ├── build_theme_uf.sh         # One UF × theme: GeoJSON, clusters, tiles
│   ├── build_theme_pair.sh       # One UF: income then deaths
│   └── build_municipality_rj.py  # Wrapper: build_municipality.py RJ
├── notebooks/
│   └── treat_2022.ipynb      # Census + setor geometry → race GeoJSON
├── docs/
│   ├── docs.md               # Zoom, density, schema, one-panel + mobile sheet chrome, footer
│   ├── fontes.md             # IBGE download URLs and raw-file caveats
│   ├── local-setup.md        # How to merge tiles and serve locally
│   └── structure.md          # This file
├── assets/                   # Optional extras (not in git; unused by the current UI)
├── tiles/                    # race MBTiles versioned as tiles/{UF}; income/deaths built locally
└── data/                     # gitignored: merged PMTiles, GeoJSON, raw census
```

`data/` and `dots/` are local-only. Rebuild the national PMTiles the page reads with:

```sh
mkdir -p data/tiles
# --no-tile-size-limit keeps SP+MG z7 (~508KB); default 500KB/tile drops it.
tile-join -f --no-tile-size-limit -o data/tiles/censo2022.pmtiles tiles/*/*/tiles.mbtiles
tile-join -f --no-tile-size-limit -o data/tiles/censo2022_income.pmtiles tiles/income/*/*/tiles.mbtiles
tile-join -f --no-tile-size-limit -o data/tiles/censo2022_deaths.pmtiles tiles/deaths/*/*/tiles.mbtiles
```
