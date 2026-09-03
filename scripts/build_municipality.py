"""Build themed municipality_{UF}.geojson without geopandas/geobr.

Income uses IBGE's municipality file because setor medians are not
additive. Race and mortality can be aggregated from their setor CSVs.
"""

from __future__ import annotations

import csv
import sys
import zipfile
from collections import defaultdict

from ibge_uf import (
    RACE_DIR,
    RAW_DIR,
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
from themes import Theme, get_theme
from build_census_tract import ensure_theme_source

MALHA_URL = (
    "https://geoftp.ibge.gov.br/organizacao_do_territorio/"
    "malhas_territoriais/malhas_municipais/municipio_2022/UFs/{uf}/"
    "{uf}_Municipios_2022.zip"
)


def ensure_municipality_source(theme: Theme) -> None:
    if theme.id != "income" or (theme.municipality_path and theme.municipality_path.exists()):
        return
    if not theme.municipality_url or not theme.municipality_zip or not theme.municipality_path:
        raise SystemExit("Income municipality source is not configured")
    download(theme.municipality_url, theme.municipality_zip)
    with zipfile.ZipFile(theme.municipality_zip) as zf:
        csv_names = [name for name in zf.namelist() if name.lower().endswith(".csv")]
        if len(csv_names) != 1:
            raise SystemExit(f"Expected one CSV in {theme.municipality_zip}")
        with zf.open(csv_names[0]) as src, theme.municipality_path.open("wb") as dest:
            dest.write(src.read())


def aggregate_counts(uf: str, theme: Theme) -> None:
    prefix = UF_CODES[uf]
    source = theme.municipality_path if theme.id == "income" else theme.source_path
    if source is None or not source.exists():
        raise SystemExit(f"Missing source CSV: {source}")
    key = "CD_MUN" if theme.id == "income" else theme.key_field
    agg: dict[str, dict[str, float]] = defaultdict(
        lambda: {category: 0.0 for category in theme.categories}
    )
    metrics: dict[str, dict[str, float]] = {}
    with source.open(encoding="latin-1", newline="") as fh:
        reader = csv.DictReader(fh, delimiter=";")
        fieldmap = csv_fieldmap(reader.fieldnames)
        for row in reader:
            geo_id = row[fieldmap[key]].strip('"')
            if not geo_id.startswith(prefix):
                continue
            mun = geo_id[:7]
            values = theme.extract(row, fieldmap)
            for category in theme.categories:
                agg[mun][category] += float(values[category])
            if theme.id == "income":
                metrics[mun] = {
                    "renda_media": float(values["renda_media"]),
                    "renda_mediana": float(values["renda_mediana"]),
                    theme.total_field: float(values[theme.total_field]),
                }
            else:
                metrics.setdefault(mun, {theme.total_field: 0.0})
                metrics[mun][theme.total_field] += float(values[theme.total_field])

    out_dir = theme.output_dir
    counts_csv = out_dir / f"municipality_{uf}_counts.csv"
    counts_csv.parent.mkdir(parents=True, exist_ok=True)
    extra_fields = ["renda_media", "renda_mediana"] if theme.id == "income" else []
    with counts_csv.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "id_municipio",
                "sigla_uf",
                *theme.categories,
                theme.total_field,
                *extra_fields,
            ],
        )
        writer.writeheader()
        for mun, counts in sorted(agg.items()):
            writer.writerow(
                {
                    "id_municipio": mun,
                    "sigla_uf": uf,
                    **{category: int(counts[category]) for category in theme.categories},
                    **metrics[mun],
                }
            )
    print(f"wrote {counts_csv} theme={theme.id} municipalities={len(agg)}")


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


def enrich_race_hover(uf: str, counts_csv) -> None:
    base = RACE_DIR / f"municipality_{uf}.geojson"
    if not base.exists():
        return
    temp = RACE_DIR / f"municipality_{uf}_enriched.geojson"
    run_mapshaper(
        [
            str(base),
            "-join",
            str(counts_csv),
            "keys=id_municipio,id_municipio",
            "string-fields=id_municipio",
            "force",
            "-o",
            "format=geojson",
            str(temp),
        ]
    )
    temp.replace(base)


def mapshaper_join(uf: str, shp, theme: Theme) -> None:
    counts_csv = theme.output_dir / f"municipality_{uf}_counts.csv"
    out_path = theme.output_dir / f"municipality_{uf}.geojson"
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
    if theme.id != "race":
        enrich_race_hover(uf, counts_csv)


def main(argv: list[str] | None = None) -> None:
    args = argv if argv is not None else sys.argv[1:]
    if not 1 <= len(args) <= 2:
        raise SystemExit(f"Usage: {sys.argv[0]} <UF> [race|income|deaths]")
    uf = parse_uf(args[0])
    theme = get_theme(args[1] if len(args) > 1 else None)
    ensure_theme_source(theme)
    ensure_municipality_source(theme)
    aggregate_counts(uf, theme)
    shp = ensure_malha(uf)
    mapshaper_join(uf, shp, theme)
    # Theme builds are batched; `python3 scripts/ibge_uf.py` performs one
    # national hover rebuild after all theme fields have been appended.
    if theme.id == "race":
        merge_hover()


if __name__ == "__main__":
    main()
