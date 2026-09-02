"""Build municipality_RJ.geojson without geopandas/geobr.

Those imports hang in this environment. Stdlib aggregates the national
race CSV; IBGE shapefile + mapshaper supply polygons and the join.
"""

from __future__ import annotations

import csv
import subprocess
import urllib.request
import zipfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data/censo2022/raw/Agregados_por_setores_cor_ou_raca_BR.csv"
MALHA_URL = (
    "https://geoftp.ibge.gov.br/organizacao_do_territorio/"
    "malhas_territoriais/malhas_municipais/municipio_2022/UFs/RJ/"
    "RJ_Municipios_2022.zip"
)
MALHA_ZIP = ROOT / "data/censo2022/raw/RJ_Municipios_2022.zip"
MALHA_DIR = ROOT / "data/censo2022/raw/RJ_Municipios_2022"
COUNTS_CSV = ROOT / "data/censo2022/output/tiles/race/municipality_RJ_counts.csv"
OUT_PATH = ROOT / "data/censo2022/output/tiles/race/municipality_RJ.geojson"

RACES = ("branca", "preta", "amarela", "parda", "indigena")
SRC_COLS = ("V01317", "V01318", "V01319", "V01320", "V01321")


def _num(value: str) -> float:
    # IBGE marks suppressed cells as X; treat as 0 so dots can be generated.
    value = (value or "").strip().strip('"')
    if value in ("", "X"):
        return 0.0
    return float(value)


def aggregate_rj_counts() -> None:
    agg: dict[str, dict[str, float]] = defaultdict(lambda: {r: 0.0 for r in RACES})
    with CSV_PATH.open(encoding="latin-1", newline="") as fh:
        reader = csv.DictReader(fh, delimiter=";")
        fieldmap = {name.strip('"'): name for name in (reader.fieldnames or [])}
        for row in reader:
            setor = row[fieldmap["CD_SETOR"]].strip('"')
            if not setor.startswith("33"):
                continue
            mun = setor[:7]
            for dest, src in zip(RACES, SRC_COLS):
                agg[mun][dest] += _num(row[fieldmap[src]])

    COUNTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    with COUNTS_CSV.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["id_municipio", "sigla_uf", *RACES, "populacao"]
        )
        writer.writeheader()
        for mun, counts in sorted(agg.items()):
            pop = int(sum(counts[r] for r in RACES))
            writer.writerow(
                {
                    "id_municipio": mun,
                    "sigla_uf": "RJ",
                    "populacao": pop,
                    **{r: int(counts[r]) for r in RACES},
                }
            )
    print(f"wrote {COUNTS_CSV} municipalities={len(agg)}")


def ensure_malha() -> Path:
    shp = MALHA_DIR / "RJ_Municipios_2022.shp"
    if shp.exists():
        return shp
    MALHA_ZIP.parent.mkdir(parents=True, exist_ok=True)
    print(f"downloading {MALHA_URL}")
    urllib.request.urlretrieve(MALHA_URL, MALHA_ZIP)
    MALHA_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(MALHA_ZIP) as zf:
        zf.extractall(MALHA_DIR)
    return shp


def mapshaper_join(shp: Path) -> None:
    cmd = [
        "npx",
        "--yes",
        "mapshaper",
        str(shp),
        "-rename-fields",
        "id_municipio=CD_MUN,municipio=NM_MUN,sigla_uf=SIGLA_UF",
        "-join",
        str(COUNTS_CSV),
        "keys=id_municipio,id_municipio",
        "string-fields=id_municipio",
        "-drop",
        "fields=AREA_KM2",
        "-o",
        "format=geojson",
        str(OUT_PATH),
    ]
    subprocess.run(cmd, check=True)
    print(f"wrote {OUT_PATH}")


def main() -> None:
    aggregate_rj_counts()
    shp = ensure_malha()
    mapshaper_join(shp)


if __name__ == "__main__":
    main()
