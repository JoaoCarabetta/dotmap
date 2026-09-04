"""Shared IBGE UF helpers for the per-state GeoJSON builders.

geopandas/geobr hang in this environment, so the builders stay on stdlib
plus mapshaper. Keep UF codes and race columns in one place so municipality
and census-tract outputs join on the same keys.
"""

from __future__ import annotations

import subprocess
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data/censo2022/raw/Agregados_por_setores_cor_ou_raca_BR.csv"
RAW_DIR = ROOT / "data/censo2022/raw"
RACE_DIR = ROOT / "data/censo2022/output/tiles/race"

# IBGE CD_UF / first two digits of CD_SETOR. Keys are the sigla used on disk.
UF_CODES = {
    "RO": "11",
    "AC": "12",
    "AM": "13",
    "RR": "14",
    "PA": "15",
    "AP": "16",
    "TO": "17",
    "MA": "21",
    "PI": "22",
    "CE": "23",
    "RN": "24",
    "PB": "25",
    "PE": "26",
    "AL": "27",
    "SE": "28",
    "BA": "29",
    "MG": "31",
    "ES": "32",
    "RJ": "33",
    "SP": "35",
    "PR": "41",
    "SC": "42",
    "RS": "43",
    "MS": "50",
    "MT": "51",
    "GO": "52",
    "DF": "53",
}

RACES = ("branca", "preta", "amarela", "parda", "indigena")
SRC_COLS = ("V01317", "V01318", "V01319", "V01320", "V01321")


def parse_uf(raw: str) -> str:
    uf = (raw or "").strip().upper()
    if uf not in UF_CODES:
        known = ", ".join(sorted(UF_CODES))
        raise SystemExit(f"Unknown UF {raw!r}. Expected one of: {known}")
    return uf


def num(value: str) -> float:
    # IBGE uses X for confidentiality and "." for unavailable aggregates.
    # Both become 0 for arithmetic, while docs/UI retain the caveat that
    # these are unknown values rather than observed zeroes.
    value = (value or "").strip().strip('"')
    if value in ("", "X", ".", ".."):
        return 0.0
    # Some newer aggregate files use decimal commas even though older
    # national CSVs use decimal points.
    return float(value.replace(",", "."))


def csv_fieldmap(fieldnames: list[str] | None) -> dict[str, str]:
    return {name.strip('"'): name for name in (fieldnames or [])}


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"downloading {url}")
    # IBGE sometimes rejects the default Python user-agent.
    req = urllib.request.Request(url, headers={"User-Agent": "dotmap/1.0"})
    with urllib.request.urlopen(req, timeout=180) as src, dest.open("wb") as out:
        while True:
            chunk = src.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)


def unzip(zip_path: Path, dest_dir: Path) -> None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(dest_dir)


def find_shp(directory: Path) -> Path:
    matches = sorted(directory.rglob("*.shp"))
    if not matches:
        raise FileNotFoundError(f"No .shp under {directory}")
    return matches[0]


def mapshaper() -> list[str]:
    # Same fallback as makefiles.sh: mapshaper is not always on PATH.
    from shutil import which

    if which("mapshaper"):
        return ["mapshaper"]
    return ["npx", "--yes", "mapshaper"]


def run_mapshaper(args: list[str]) -> None:
    subprocess.run([*mapshaper(), *args], check=True)


def merge_hover() -> None:
    """Concatenate every per-UF GeoJSON, then cut hover vector tiles.

    Census-tract polygons stay full-resolution in the per-UF files (dots
    need the shape). The merged hover GeoJSON is simplified only as an
    intermediate: loading it in Mapbox (248MB at 27 UFs) freezes the map
    at high zoom, so the browser reads `data/tiles/hover.pmtiles` instead.
    """
    RACE_DIR.mkdir(parents=True, exist_ok=True)
    for kind in ("municipality", "census_tract"):
        parts = sorted(RACE_DIR.glob(f"{kind}_[A-Z][A-Z].geojson"))
        out = RACE_DIR / f"{kind}.geojson"
        if not parts:
            out.write_text('{"type":"FeatureCollection","features":[]}\n', encoding="utf-8")
            print(f"wrote {out} features=0 from 0 UF files")
            continue
        # Theme builders add renda/óbito columns to every UF. `force` keeps
        # those extra fields when an older file is missing a column.
        args = ["-i", *[str(p) for p in parts], "combine-files", "-merge-layers", "force"]
        # Intermediate only. Unsimplified IBGE polygons grow past 100MB.
        # Per-UF files used for dots stay full-res.
        args.extend(["-simplify", "dp", "0.001", "keep-shapes"])
        args.extend(["-o", "format=geojson", str(out)])
        run_mapshaper(args)
        print(f"wrote {out} from {len(parts)} UF files")
    build_hover_tiles()


def build_hover_tiles() -> None:
    """Municípios at z3–9 and setores at z10–14, one PMTiles archive.

    --generate-ids is required so setFeatureState can highlight the hover
    outline. Different zoom ranges keep setor tiles off the national view.
    Intermediate tippecanoe outputs stay MBTiles; only the joined file
    is PMTiles (what the browser range-requests).
    """
    mun = RACE_DIR / "municipality.geojson"
    setor = RACE_DIR / "census_tract.geojson"
    out_dir = ROOT / "data" / "tiles"
    out_dir.mkdir(parents=True, exist_ok=True)
    hover = out_dir / "hover.pmtiles"
    tmp_mun = out_dir / "hover_municipios.mbtiles"
    tmp_setor = out_dir / "hover_setores.mbtiles"
    if not mun.exists() and not setor.exists():
        print(f"skip hover tiles: no {mun.name} or {setor.name}")
        return
    if mun.exists():
        subprocess.run(
            [
                "tippecanoe",
                "-f",
                "-o",
                str(tmp_mun),
                "-l",
                "municipios",
                "-Z3",
                "-z9",
                "--generate-ids",
                str(mun),
            ],
            check=True,
        )
    if setor.exists():
        # Extra simplify so tippecanoe can finish: 0.001 national GeoJSON
        # is still 248MB and z11–14 of every setor never completed.
        setor_lite = RACE_DIR / "census_tract_hover.geojson"
        run_mapshaper(
            [
                str(setor),
                "-simplify",
                "dp",
                "0.008",
                "keep-shapes",
                "-o",
                "format=geojson",
                str(setor_lite),
            ]
        )
        subprocess.run(
            [
                "tippecanoe",
                "-f",
                "-o",
                str(tmp_setor),
                "-l",
                "setores",
                "-Z10",
                "-z12",
                "--generate-ids",
                "--simplification=12",
                str(setor_lite),
            ],
            check=True,
        )
    parts = [p for p in (tmp_mun, tmp_setor) if p.exists()]
    if parts:
        # Always join into PMTiles so a single-layer run is not left as MBTiles.
        subprocess.run(
            ["tile-join", "-f", "-o", str(hover), *[str(p) for p in parts]],
            check=True,
        )
        for part in parts:
            part.unlink(missing_ok=True)
    print(f"wrote {hover}")


if __name__ == "__main__":
    import sys

    if sys.argv[1:] == ["tiles"]:
        build_hover_tiles()
    else:
        merge_hover()
