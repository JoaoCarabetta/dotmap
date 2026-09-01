# dotmap

Mapa de densidade de pontos da distribuição racial no Brasil (Censo 2022 / IBGE). Frontend Mapbox GL JS; tiles vetoriais servidos localmente pelo tileserver-gl.

Ao vivo: [https://carabetta.xyz/dataviz/brazildots/](https://carabetta.xyz/dataviz/brazildots/).

Guia completo: [docs/local-setup.md](docs/local-setup.md).

## Run locally (tiles already in the repo)

A fresh clone does **not** include `data/` (gitignored). Merge the versioned per-zoom MBTiles first.

Dependencies: Node.js (for `npx tileserver-gl`), [tippecanoe](https://github.com/felt/tippecanoe) (`brew install tippecanoe`), [uv](https://docs.astral.sh/uv/).

```sh
mkdir -p data/tiles
tile-join -f -o data/tiles/censo2022.mbtiles tiles/*/tiles.mbtiles

npx --yes tileserver-gl -c config.json -V
```

In another terminal:

```sh
uv run python -m http.server 8001
```

Open `http://localhost:8001`. Tiles come from `http://localhost:8080/data/censo2022/{z}/{x}/{y}.pbf` — that port is hardcoded in `index.html`.

If 8000 is free you can use `uv run python -m http.server` instead (default 8000).

Without restoring extra files from elsewhere:

- **Works:** basemap + colored race dots (zooms 7–14)
- **404:** hover GeoJSON (`data/censo2022/output/tiles/race/*_RJ.geojson`) and `assets/logo.png`

## Create the dataset from scratch

Only if you have the BigQuery project / raw census files. Do not run this just to view the map: `makefiles.sh` deletes `tiles/` and requires GeoJSON that is not in git.

1. Run the notebook https://console.cloud.google.com/bigquery?ws=!1m7!1m6!12m5!1m3!1srj-escritorio-dev!2ssouthamerica-east1!3s371e01b4-ccd6-429a-b0ef-c73c384a1dd7!2e2 (or `notebooks/treat_2022.ipynb`).
2. Download / write GeoJSON under `data/censo2022/output/tiles/race/`.
3. Build dots and tiles for one UF (argument is required):

```sh
./makefiles.sh RJ
```
