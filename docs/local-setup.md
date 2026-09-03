# Local setup

How to run the map on this machine. Verified 2026-09-02 with per-UF tiles under `tiles/{UF}/` (27 UFs) and map `minzoom` 2 (Mapbox treats the floor as exclusive).

## What git gives you vs what it does not

In the repo:

- `index.html` (map UI; Mapbox **light-v10** basemap with symbol/label layers hidden; opens on Brazil via `fitBounds`, not Rio)
- `tiles/{UF}/zoom3-3` … `tiles/{UF}/zoom14-14` (per-UF race MBTiles; 27 UFs; 3–6 clustered setor)
- `config.json` (expects race, income, deaths, and hover MBTiles under `data/tiles/`)
- Theme builders (`scripts/themes.py`, `makefiles.sh` with a theme arg). **Income/deaths per-UF MBTiles are not versioned** — generate them locally, then `tile-join`

Not in git (`data/` is missing on a fresh clone):

- `data/tiles/censo2022.mbtiles` — build it with `tile-join` (below)
- `data/tiles/censo2022_income.mbtiles` and `censo2022_deaths.mbtiles`
- `data/tiles/hover.mbtiles` — município (z3–9) and setor (z10–12, overzoom after) hover; `python3 scripts/ibge_uf.py tiles`
- `data/censo2022/output/tiles/race/census_tract.geojson` — intermediate for hover tiles (do not load in the browser)
- `data/censo2022/output/tiles/race/municipality.geojson` — intermediate for hover tiles

## Dependencies

| Tool | Why | Install |
|---|---|---|
| Node.js + npm | run tileserver-gl | already on PATH if you use nvm/fnm; else install Node 22+ |
| tileserver-gl 5.x | serve PBF on :8080 | `npx tileserver-gl` (no global install required) |
| tippecanoe (`tile-join`) | merge per-zoom MBTiles | `brew install tippecanoe` |
| uv + Python 3.12 | static file server | `uv` uses `.python-version` |

`mapshaper` is only needed to **regenerate** dots via `makefiles.sh`, not to serve existing tiles.

Do **not** run `./makefiles.sh` just to view the map. The script requires a UF argument (`./makefiles.sh RR`) and needs GeoJSON under `data/` that is not in git. A full run regenerates 7–14 for **that UF only**; other states in `tiles/` stay put. To rebuild only clustered z3–6: `python3 scripts/build_density_clusters.py RR` then `./makefiles.sh RR 3,4,5,6`. For all 27 UFs, set `SKIP_TILE_JOIN=1` per UF and run one `tile-join` at the end.

## Serve existing tiles (reproduced path)

```sh
# 1. Merge the versioned per-zoom files into the path config.json expects.
#    -f overwrites (not --force). --no-tile-size-limit is required: tippecanoe's
#    default 500KB/tile drops the SP+MG overlap at z7 (XYZ 7/47/72, ~508KB)
#    and São Paulo goes blank even though tiles/SP/ exists for all 27 UFs.
mkdir -p data/tiles
tile-join -f --no-tile-size-limit -o data/tiles/censo2022.mbtiles tiles/*/*/tiles.mbtiles
tile-join -f --no-tile-size-limit -o data/tiles/censo2022_income.mbtiles tiles/income/*/*/tiles.mbtiles
tile-join -f --no-tile-size-limit -o data/tiles/censo2022_deaths.mbtiles tiles/deaths/*/*/tiles.mbtiles
python3 scripts/ibge_uf.py tiles

# 2. Vector tiles (must stay on 8080; index.html hardcodes that host/port).
#    Full tileserver-gl can fail on Node 23 (native mbgl); use light then:
#    npx --yes tileserver-gl-light@4.1.1 -c config.json
npx --yes tileserver-gl -c config.json -V

# 3. UI. Default in the README is 8000; use another port if 8000 is taken
#    (Docker was listening on 8000 here).
uv run python -m http.server 8001
```

Open `http://localhost:8001`. The switcher shows **Raça** and **Renda** (Óbitos stays hidden; `HIDDEN_VIEWS` in `index.html`). Race tiles are versioned; Renda/Óbitos need the local theme join above.

On localhost a top-right **dev** button (or `D` / `` ` ``) toggles a HUD. Zoom and raio are sliders (raio is a 0.5×–3× multiplier on the coded radius curve; **reset** returns to 1×). `1` jumps to the Brazil overview; `2` jumps to Rio at zoom 15 (tiles still max out at 14). It is not injected on `carabetta.xyz`.

Sanity checks used in the reproduction:

- `GET /data/censo2022.json` → `minzoom` 3, `maxzoom` 14, layer `points`, field `race`
- `GET /data/censo2022_income.json` and `/data/censo2022_deaths.json` → zooms 3–14, layer `points`, field `cat`
- Sample PBF at zoom 3 (`3/3/4.pbf`), zoom 4 (`4/6/9.pbf`) and zoom 7 (`7/48/72.pbf`) return 200
- SP at z7 (`7/47/72.pbf`, TMS `7/47/55`) is present and large (~508 KB). A join without `--no-tile-size-limit` drops it.
- If 8080 is down, Mapbox overzooms the last cached zoom and 10–14 look frozen even though native tiles exist.
- A real browser over the RJ center requested zooms 3–12 and received 200s
- Hover is `GET /data/hover/{z}/{x}/{y}.pbf` (not the GeoJSON). Rebuild with `python3 scripts/ibge_uf.py tiles` after the concatenated files exist.

## Public URL

The map is published at [https://carabetta.xyz/dataviz/brazildots/](https://carabetta.xyz/dataviz/brazildots/). Production serves tiles from `tileserver-gl-light` in Docker on the VPS (`carabetta.xyz/dataviz/brazildots/docker-compose.yml`), proxied at `/dataviz/brazildots/tiles/`. The Mapbox source must use an absolute `origin + /dataviz/brazildots/tiles/{z}/{x}/{y}.pbf` URL — workers resolve relative paths against `blob:` and never hit nginx. Hover GeoJSON is not on the public page.

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
tile-join -f --no-tile-size-limit -o data/tiles/censo2022_income.mbtiles tiles/income/*/*/tiles.mbtiles
tile-join -f --no-tile-size-limit -o data/tiles/censo2022_deaths.mbtiles tiles/deaths/*/*/tiles.mbtiles
python3 scripts/ibge_uf.py
```

3. Generate dots and MBTiles for that UF. A full run regenerates 7–14 for that state only:

```sh
./makefiles.sh RR            # all zooms 3–14 for RR, then tile-join every UF
./makefiles.sh RR 3,4,5,6    # clustered zooms only
# National z3–6 rebuild: SKIP_TILE_JOIN=1 ./makefiles.sh UF 3,4,5,6 per UF, then one join
```

4. Then serve as in the section above. `makefiles.sh` already writes `data/tiles/censo2022.mbtiles`.
