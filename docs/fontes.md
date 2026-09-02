# Sources

Log of census files used by this project. Raw downloads stay under `data/` (gitignored).

## Censo 2022 — cor ou raça por setor (universo)

- **Official name:** Agregados por Setores Censitários — Pessoas, Cor ou Raça (resultados do universo)
- **URL:** https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Setor_csv/Agregados_por_setores_cor_ou_raca_BR.zip
- **Downloaded:** 2026-09-01
- **Local path:** `data/censo2022/raw/Agregados_por_setores_cor_ou_raca_BR.csv` (zip kept beside it)
- **Format:** CSV, `;` delimiter, quoted headers, `latin-1`
- **Grain:** one row = one setor censitário (`CD_SETOR`)
- **Coverage:** 458,772 setores (IBGE malha has ~468,097; missing rows are setores with no people in this table). National race sums with `X`→0: 202,321,691 people. Official 2022 total is ~203.1M; the gap is IBGE suppression (`X`), not a download error.
- **Race columns (same keys as the current map):** `V01317` branca, `V01318` preta, `V01319` amarela, `V01320` parda, `V01321` indígena
- **License / republication:** IBGE public statistical data; cite IBGE / Censo Demográfico 2022
- **Caveats:** `X` is a confidentiality mark, not a true zero. The notebook currently replaces `X` with `0` so dots can be generated. That undercounts small groups (especially amarela and indígena).

## Dictionary

- **Official name:** Dicionário de dados — Agregados por Setores Censitários 2022
- **URL:** https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/dicionario_de_dados_agregados_por_setores_censitarios_20260520.xlsx
- **Downloaded:** 2026-09-01
- **Local path:** `data/censo2022/raw/dicionario_de_dados_agregados_por_setores_censitarios_20260520.xlsx`

## Malha municipal 2022 — RJ (polígonos para dots 4–6)

- **Official name:** Malha Municipal Digital 2022 — municípios do Rio de Janeiro
- **URL:** https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2022/UFs/RJ/RJ_Municipios_2022.zip
- **Used by:** `scripts/build_municipality_rj.py` (join onto race counts aggregated from the national setor CSV; input for zoom 3–6 city dots)
- **Fields used:** `CD_MUN` → `id_municipio`, `NM_MUN` → `municipio`, `SIGLA_UF` → `sigla_uf`
- **Coverage after join:** 92/92 RJ municipalities; race sum with `X`→0 is 15,996,360 (suppression, same caveat as the setor table)

## Not downloaded in this slice

- Setor malha 2022 (`BR_setores_CD2022.gpkg`, ~1.4 GB). Use `geobr.read_census_tract(year=2022)` when building GeoJSON.
- Alfabetização, saneamento, and religião files. See the national-themes plan.

## Re-download

```sh
mkdir -p data/censo2022/raw
cd data/censo2022/raw
curl -fL -O https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Setor_csv/Agregados_por_setores_cor_ou_raca_BR.zip
curl -fL -O https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/dicionario_de_dados_agregados_por_setores_censitarios_20260520.xlsx
unzip -o Agregados_por_setores_cor_ou_raca_BR.zip
```
