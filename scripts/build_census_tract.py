"""Build census_tract_{UF}.geojson without geopandas/geobr.

Downloads the official 2022 setor shapefile for one UF and joins the
national race CSV on CD_SETOR. Per-UF meshes stay small; the national
GPKG (~1.4 GB) is never required.
"""

from __future__ import annotations

import csv
import sys

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

# Official 2022 malha (not the preliminar tree). Files sit directly under UF/.
MALHA_URL = (
    "https://geoftp.ibge.gov.br/organizacao_do_territorio/"
    "malhas_territoriais/malhas_de_setores_censitarios__divisoes_intramunicipais/"
    "censo_2022/setores/shp/UF/{uf}_setores_CD2022.zip"
)


def write_setor_counts(uf: str) -> None:
    prefix = UF_CODES[uf]
    counts_csv = RACE_DIR / f"census_tract_{uf}_counts.csv"
    counts_csv.parent.mkdir(parents=True, exist_ok=True)
    rows = 0
    with CSV_PATH.open(encoding="latin-1", newline="") as fh_in, counts_csv.open(
        "w", encoding="utf-8", newline=""
    ) as fh_out:
        reader = csv.DictReader(fh_in, delimiter=";")
        fieldmap = csv_fieldmap(reader.fieldnames)
        writer = csv.DictWriter(
            fh_out,
            fieldnames=["id_setor_censitario", "sigla_uf", *RACES, "populacao"],
        )
        writer.writeheader()
        for row in reader:
            setor = row[fieldmap["CD_SETOR"]].strip('"')
            if not setor.startswith(prefix):
                continue
            counts = {dest: num(row[fieldmap[src]]) for dest, src in zip(RACES, SRC_COLS)}
            writer.writerow(
                {
                    "id_setor_censitario": setor,
                    "sigla_uf": uf,
                    "populacao": int(sum(counts.values())),
                    **{r: int(counts[r]) for r in RACES},
                }
            )
            rows += 1
    print(f"wrote {counts_csv} setores={rows}")


def ensure_malha(uf: str):
    dest_dir = RAW_DIR / f"{uf}_setores_CD2022"
    existing = list(dest_dir.rglob("*.shp")) if dest_dir.exists() else []
    if existing:
        return existing[0]
    zip_path = RAW_DIR / f"{uf}_setores_CD2022.zip"
    if not zip_path.exists():
        download(MALHA_URL.format(uf=uf), zip_path)
    unzip(zip_path, dest_dir)
    return find_shp(dest_dir)


def mapshaper_join(uf: str, shp) -> None:
    counts_csv = RACE_DIR / f"census_tract_{uf}_counts.csv"
    out_path = RACE_DIR / f"census_tract_{uf}.geojson"
    # Rename first so the join key matches the counts CSV. Drop bulky IBGE
    # columns we do not render; keep municipio for a future tooltip label.
    run_mapshaper(
        [
            str(shp),
            "-rename-fields",
            "id_setor_censitario=CD_SETOR,id_municipio=CD_MUN,municipio=NM_MUN",
            "-join",
            str(counts_csv),
            "keys=id_setor_censitario,id_setor_censitario",
            "string-fields=id_setor_censitario,id_municipio",
            "-filter-fields",
            "id_setor_censitario,id_municipio,municipio,sigla_uf,"
            "populacao,branca,preta,amarela,parda,indigena",
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
    write_setor_counts(uf)
    shp = ensure_malha(uf)
    mapshaper_join(uf, shp)
    merge_hover()


if __name__ == "__main__":
    main()
