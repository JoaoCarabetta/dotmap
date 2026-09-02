"""Build municipality_{UF}.geojson without geopandas/geobr.

Stdlib aggregates the national race CSV for one UF; the IBGE municipal
shapefile + mapshaper supply polygons and the join. Writes the per-UF
file and refreshes the concatenated hover GeoJSON.
"""

from __future__ import annotations

import csv
import sys
from collections import defaultdict

from ibge_uf import (
    CSV_PATH,
    RACE_DIR,
    RACES,
    RAW_DIR,
    SRC_COLS,
    UF_CODES,
    csv_fieldmap,
    download,
    find_shp,
    merge_hover,
    num,
    parse_uf,
    run_mapshaper,
    unzip,
)

MALHA_URL = (
    "https://geoftp.ibge.gov.br/organizacao_do_territorio/"
    "malhas_territoriais/malhas_municipais/municipio_2022/UFs/{uf}/"
    "{uf}_Municipios_2022.zip"
)


def aggregate_counts(uf: str) -> None:
    prefix = UF_CODES[uf]
    agg: dict[str, dict[str, float]] = defaultdict(lambda: {r: 0.0 for r in RACES})
    with CSV_PATH.open(encoding="latin-1", newline="") as fh:
        reader = csv.DictReader(fh, delimiter=";")
        fieldmap = csv_fieldmap(reader.fieldnames)
        for row in reader:
            setor = row[fieldmap["CD_SETOR"]].strip('"')
            if not setor.startswith(prefix):
                continue
            mun = setor[:7]
            for dest, src in zip(RACES, SRC_COLS):
                agg[mun][dest] += num(row[fieldmap[src]])

    counts_csv = RACE_DIR / f"municipality_{uf}_counts.csv"
    counts_csv.parent.mkdir(parents=True, exist_ok=True)
    with counts_csv.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["id_municipio", "sigla_uf", *RACES, "populacao"]
        )
        writer.writeheader()
        for mun, counts in sorted(agg.items()):
            pop = int(sum(counts[r] for r in RACES))
            writer.writerow(
                {
                    "id_municipio": mun,
                    "sigla_uf": uf,
                    "populacao": pop,
                    **{r: int(counts[r]) for r in RACES},
                }
            )
    print(f"wrote {counts_csv} municipalities={len(agg)}")


def ensure_malha(uf: str):
    dest_dir = RAW_DIR / f"{uf}_Municipios_2022"
    shp = dest_dir / f"{uf}_Municipios_2022.shp"
    if shp.exists():
        return shp
    zip_path = RAW_DIR / f"{uf}_Municipios_2022.zip"
    if not zip_path.exists():
        download(MALHA_URL.format(uf=uf), zip_path)
    unzip(zip_path, dest_dir)
    return find_shp(dest_dir)


def mapshaper_join(uf: str, shp) -> None:
    counts_csv = RACE_DIR / f"municipality_{uf}_counts.csv"
    out_path = RACE_DIR / f"municipality_{uf}.geojson"
    run_mapshaper(
        [
            str(shp),
            "-rename-fields",
            "id_municipio=CD_MUN,municipio=NM_MUN,sigla_uf=SIGLA_UF",
            "-join",
            str(counts_csv),
            "keys=id_municipio,id_municipio",
            "string-fields=id_municipio",
            "-drop",
            "fields=AREA_KM2",
            "-o",
            "format=geojson",
            str(out_path),
        ]
    )
    print(f"wrote {out_path}")


def main(argv: list[str] | None = None) -> None:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 1:
        raise SystemExit(f"Usage: {sys.argv[0]} <UF>")
    uf = parse_uf(args[0])
    if not CSV_PATH.exists():
        raise SystemExit(f"Missing national race CSV: {CSV_PATH}")
    aggregate_counts(uf)
    shp = ensure_malha(uf)
    mapshaper_join(uf, shp)
    merge_hover()


if __name__ == "__main__":
    main()
