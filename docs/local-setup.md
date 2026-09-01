# Local setup

How to run the map on this machine. Verified 2026-09-01 with the MBTiles already in `tiles/`.

## What git gives you vs what it does not

In the repo:

- `index.html` (map UI)
- `tiles/zoom7-7` … `tiles/zoom14-14` (per-zoom MBTiles, RJ)
- `config.json` (expects a merged file at `data/tiles/censo2022.mbtiles`)

Not in git (`data/` and `assets/` are missing on a fresh clone):

- `data/tiles/censo2022.mbtiles` — build it with `tile-join` (below)
- `data/censo2022/output/tiles/race/census_tract_RJ.geojson` — hover/tooltip from zoom 10
- `data/censo2022/output/tiles/race/municipality_RJ.geojson` — hover/tooltip below zoom 10
- `assets/logo.png` — header logo (page still works; image 404s)

## Dependencies

| Tool | Why | Install |
|---|---|---|
| Node.js + npm | run tileserver-gl | already on PATH if you use nvm/fnm; else install Node 22+ |
| tileserver-gl 5.x | serve PBF on :8080 | `npx tileserver-gl` (no global install required) |
| tippecanoe (`tile-join`) | merge per-zoom MBTiles | `brew install tippecanoe` |
| uv + Python 3.12 | static file server | `uv` uses `.python-version` |

`mapshaper` is only needed to **regenerate** dots via `makefiles.sh`, not to serve existing tiles.

Do **not** run `./makefiles.sh` just to view the map. The script requires a UF argument (`./makefiles.sh RJ`), deletes `tiles/`, and needs GeoJSON under `data/` that is not in git.

## Serve existing tiles (reproduced path)

```sh
# 1. Merge the versioned per-zoom files into the path config.json expects.
#    tile-join uses -f (overwrite), not --force.
mkdir -p data/tiles
tile-join -f -o data/tiles/censo2022.mbtiles tiles/*/tiles.mbtiles

# 2. Vector tiles (must stay on 8080; index.html hardcodes that host/port)
npx --yes tileserver-gl -c config.json -V

# 3. UI. Default in the README is 8000; use another port if 8000 is taken
#    (Docker was listening on 8000 here).
uv run python -m http.server 8001
```

Open `http://localhost:8001`. Tiles are requested from `http://localhost:8080/data/censo2022/{z}/{x}/{y}.pbf`.

Sanity checks used in the reproduction:

- `GET /data/censo2022.json` → `minzoom` 7, `maxzoom` 14, layer `points`, field `race`
- Sample PBF at zoom 7 (`7/48/72.pbf`) returns 200
- A real browser over the RJ center requested zooms 7–12 and received 200s
- `census_tract_RJ.geojson`, `municipality_RJ.geojson`, and `assets/logo.png` return 404 until those files are restored

## Public URL

The map is published at [https://carabetta.xyz/dataviz/brazildots/](https://carabetta.xyz/dataviz/brazildots/). Production serves tiles from `tileserver-gl-light` in Docker on the VPS (`carabetta.xyz/dataviz/brazildots/docker-compose.yml`), proxied at `/dataviz/brazildots/tiles/`. The Mapbox source must use an absolute `origin + /dataviz/brazildots/tiles/{z}/{x}/{y}.pbf` URL — workers resolve relative paths against `blob:` and never hit nginx. Hover GeoJSON is not on the public page.

## Create the dataset from scratch (not reproduced here)

Needs GCP access to `rj-escritorio-dev` and raw files that live only under `data/`.

1. Run the BigQuery notebook linked from [README.md](../README.md).
2. Or run [notebooks/treat_2022.ipynb](../notebooks/treat_2022.ipynb) against `data/censo2022/raw/censo.csv` + `setores.gpkg`. It writes `census_tract_RJ.geojson` and `municipality_RJ.geojson`.
3. Generate dots and MBTiles (this **wipes** `tiles/`):

```sh
./makefiles.sh RJ
```

4. Then serve as in the section above. `makefiles.sh` already writes `data/tiles/censo2022.mbtiles`.
