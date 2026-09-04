# Local setup

How to run the map on this machine. Verified 2026-09-04 with per-UF tiles under `tiles/{UF}/` (27 UFs) and MapLibre `minZoom` 3 (inclusive; first point tileset is z=3).

## What git gives you vs what it does not

In the repo:

- `index.html` (map UI; Mapbox **light-v10** basemap via the Style API, symbol/label layers hidden; opens on Brazil via `fitBounds`, not Rio)
- `tiles/{UF}/zoom3-3` … `tiles/{UF}/zoom14-14` (per-UF race MBTiles; 27 UFs; 3–6 clustered setor)
- Theme builders (`scripts/themes.py`, `makefiles.sh` with a theme arg). **Income/deaths per-UF MBTiles are not versioned** — generate them locally, then `tile-join` to PMTiles

Not in git (`data/` is missing on a fresh clone):

- `data/tiles/censo2022.pmtiles` — build it with `tile-join` (below)
- `data/tiles/censo2022_income.pmtiles` and `censo2022_deaths.pmtiles`
- `data/tiles/hover.pmtiles` — município (z3–9) and setor (z10–12, overzoom after) hover; `python3 scripts/ibge_uf.py tiles`
- `data/censo2022/output/tiles/race/census_tract.geojson` — intermediate for hover tiles (do not load in the browser)
- `data/censo2022/output/tiles/race/municipality.geojson` — intermediate for hover tiles

`config.json` is a leftover tileserver-gl config. The map does not read it.

## Dependencies

| Tool | Why | Install |
|---|---|---|
| tippecanoe (`tile-join`) | merge per-zoom MBTiles into national PMTiles | `brew install tippecanoe` |
| uv + Python 3.12 | static file server (Range requests) | `uv` uses `.python-version` |

`mapshaper` / Node.js are only needed to **regenerate** dots via `makefiles.sh`, not to serve existing tiles.

Do **not** run `./makefiles.sh` just to view the map. The script requires a UF argument (`./makefiles.sh RR`) and needs GeoJSON under `data/` that is not in git. A full run regenerates 7–14 for **that UF only**; other states in `tiles/` stay put. To rebuild only clustered z3–6: `python3 scripts/build_density_clusters.py RR` then `./makefiles.sh RR 3,4,5,6`. For all 27 UFs, set `SKIP_TILE_JOIN=1` per UF and run one `tile-join` at the end.

## Serve existing tiles (reproduced path)

```sh
# 1. Merge the versioned per-zoom files into the PMTiles the page range-requests.
#    -f overwrites (not --force). --no-tile-size-limit is required: tippecanoe's
#    default 500KB/tile drops the SP+MG overlap at z7 (XYZ 7/47/72, ~508KB)
#    and São Paulo goes blank even though tiles/SP/ exists for all 27 UFs.
#    Do not gzip the .pmtiles file (Range + inner gzip tiles would break).
mkdir -p data/tiles
tile-join -f --no-tile-size-limit -o data/tiles/censo2022.pmtiles tiles/*/*/tiles.mbtiles
tile-join -f --no-tile-size-limit -o data/tiles/censo2022_income.pmtiles tiles/income/*/*/tiles.mbtiles
tile-join -f --no-tile-size-limit -o data/tiles/censo2022_deaths.pmtiles tiles/deaths/*/*/tiles.mbtiles
python3 scripts/ibge_uf.py tiles

# 2. Page + archives on one port. scripts/serve.py speaks Range; some Python
#    3.12 http.server builds ignore it and would send the whole 200MB+ archive.
python3 scripts/serve.py
```

Open `http://localhost:8000`. The switcher shows **Raça** and **Renda** (Óbitos stays hidden; `HIDDEN_VIEWS` in `index.html`). Race tiles are versioned; Renda/Óbitos need the local theme join above.

On localhost a top-right **dev** button (or `D` / `` ` ``) toggles a HUD. Zoom and raio are sliders (raio is a 0.5×–3× multiplier on the coded radius curve; **reset** returns to 1×). `1` jumps to the Brazil overview; `2` jumps to Rio at zoom 15 (tiles still max out at 14). It is not injected on `carabetta.xyz`.

Sanity checks used in the reproduction:

- `curl -I http://localhost:8000/data/tiles/censo2022.pmtiles` → `Accept-Ranges: bytes`
- `curl -H 'Range: bytes=0-16383' -o /dev/null -w '%{http_code}\n' http://localhost:8000/data/tiles/censo2022.pmtiles` → `206`
- Browser DevTools: Range `206` on the `.pmtiles` files, no `{z}/{x}/{y}.pbf` and nothing on port 8080
- SP at z7 is present in the archive (~508 KB). A join without `--no-tile-size-limit` drops it.
- If the `.pmtiles` file is missing, dots never appear (the page does not fall back to tileserver-gl)
- Hover is `data/tiles/hover.pmtiles` (not the GeoJSON). Rebuild with `python3 scripts/ibge_uf.py tiles` after the concatenated files exist.

`python3 scripts/serve.py --port 8001` if 8000 is taken. `uv run python server.py` is the Flask alternative. Do not use `python -m http.server` unless you have confirmed it returns 206 on Range.

## Public URL

The map is published at [https://carabetta.xyz/dotsbr/](https://carabetta.xyz/dotsbr/). `index.html` resolves archives as `data/tiles/{name}.pmtiles` relative to the page, so production copies those four files next to the deployed HTML (`/dotsbr/data/tiles/…`). Nginx must send `Accept-Ranges: bytes` and **not** gzip the `.pmtiles` body. Push to `main` or `master` deploys the HTML; tile uploads stay a local `./deploy.sh --tiles`. See [`deploy.md`](deploy.md).

## Create the dataset from scratch (not reproduced here)

Needs GCP access to `rj-escritorio-dev` and raw files that live only under `data/`.

1. Run the BigQuery notebook linked from [README.md](../README.md).
2. Or build one UF at a time (stdlib + mapshaper; no geopandas). See [fontes.md](fontes.md):

```sh
python3 scripts/build_municipality.py RR
python3 scripts/build_census_tract.py RR
python3 scripts/build_density_clusters.py RR
```

For income or deaths, pass the theme. National rebuild (two UFs in parallel):

```sh
printf '%s\n' AC AL AM AP BA CE DF ES GO MA MG MS MT PA PB PE PI PR RJ RN RO RR RS SC SE SP TO \
  | xargs -P 2 -n 1 ./scripts/build_theme_pair.sh
tile-join -f --no-tile-size-limit -o data/tiles/censo2022_income.pmtiles tiles/income/*/*/tiles.mbtiles
tile-join -f --no-tile-size-limit -o data/tiles/censo2022_deaths.pmtiles tiles/deaths/*/*/tiles.mbtiles
python3 scripts/ibge_uf.py
```

3. Generate dots and per-UF MBTiles for that UF. A full run regenerates 7–14 for that state only, then joins a national PMTiles:

```sh
./makefiles.sh RR            # all zooms 3–14 for RR, then tile-join every UF → .pmtiles
./makefiles.sh RR 3,4,5,6    # clustered zooms only
# National z3–6 rebuild: SKIP_TILE_JOIN=1 ./makefiles.sh UF 3,4,5,6 per UF, then one join
```

4. Then serve as in the section above. `makefiles.sh` already writes `data/tiles/censo2022.pmtiles`.
