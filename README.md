# dotmap

Mapa de densidade de pontos da distribuição racial no Brasil (Censo 2022 / IBGE). Frontend Mapbox GL JS; tiles vetoriais servidos localmente pelo tileserver-gl.

Ao vivo: [https://carabetta.xyz/dataviz/brazildots/](https://carabetta.xyz/dataviz/brazildots/).

Guia completo: [docs/local-setup.md](docs/local-setup.md).

## Run locally (tiles already in the repo)

A fresh clone does **not** include `data/` (gitignored). Merge the versioned per-zoom MBTiles first.

Dependencies: Node.js (for `npx tileserver-gl`), [tippecanoe](https://github.com/felt/tippecanoe) (`brew install tippecanoe`), [uv](https://docs.astral.sh/uv/).

```sh
mkdir -p data/tiles
# --no-tile-size-limit: default 500KB/tile drops SP+MG at z7 (~508KB).
tile-join -f --no-tile-size-limit -o data/tiles/censo2022.mbtiles tiles/*/*/tiles.mbtiles

npx --yes tileserver-gl -c config.json -V
```

In another terminal:

```sh
uv run python -m http.server 8001
```

Open `http://localhost:8001`. Tiles come from `http://localhost:8080/data/censo2022/{z}/{x}/{y}.pbf` — that port is hardcoded in `index.html`.

If 8000 is free you can use `uv run python -m http.server` instead (default 8000).

Without restoring extra files from elsewhere:

- **Works:** light-v10 basemap (labels hidden) + colored race dots (zooms 3–14; 3–6 clustered setor). Coverage in git: **27 UFs** (nacional).
- **404:** hover tiles (`data/tiles/hover.mbtiles`) until `python3 scripts/ibge_uf.py tiles`

## Create the dataset from scratch

Needs the national race CSV under `data/` (see [docs/fontes.md](docs/fontes.md)). Do not run this just to view the map: a full `./makefiles.sh UF` regenerates zooms 7–14 for that state (expensive). Other UFs already in `tiles/` are left alone.

Add or rebuild one UF (all 27 are already in `tiles/`, including SP and MG):

```sh
python3 scripts/build_municipality.py RR
python3 scripts/build_census_tract.py RR
python3 scripts/build_density_clusters.py RR   # clustered setores for zooms 3–6
./makefiles.sh RR            # all zooms 3–14 for that UF, then tile-join every UF
./makefiles.sh RR 3,4,5,6    # clustered zooms only (needs the cluster GeoJSON)
```
