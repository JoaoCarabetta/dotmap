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

## Censo 2022 — renda do responsável por setor (universo)

- **Official name:** Agregados por Setores Censitários — Rendimento do Responsável
- **URL:** https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios_Rendimento_do_Responsavel/Agregados_por_setores_renda_responsavel_BR_20260508_csv.zip
- **Local CSV:** `data/censo2022/raw/Agregados_por_setores_renda_responsavel_BR_20260508.csv`
- **Grain:** one row per setor (`CD_SETOR`); 458,772 rows nationally.
- **Fields used:** `V06001` responsible persons in occupied permanent private households; `V06004` mean nominal monthly income among responsible persons with income; `V06006` median.
- **Map interpretation:** dot quantity represents households via `V06001`; every dot in a setor receives the setor's `V06006` class. It does not reconstruct each household's income.
- **Bins:** fixed multiples of the 2022 minimum wage (R$ 1,212): up to 1, 1–2, 2–3, 3–5, 5–10, over 10; unavailable median is separate.
- **Coverage in this repo:** income dots for all 27 UFs.

## Censo 2022 — óbitos por setor (universo)

- **URL:** https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Setor_csv/Agregados_por_setores_obitos_BR.zip
- **Local CSV:** `data/censo2022/raw/Agregados_por_setores_obitos_BR.csv`
- **Period:** January 2019 through July 2022.
- **Categories:** age at death `0–14`, `15–29`, `30–59`, `60+`; male and female columns are summed and gender is not exposed.
- **Suppression:** age cells are heavily suppressed. Nationally, visible sex totals contain about 3.63M deaths, while about 1.91M have visible detailed ages. The residual is mapped as **Idade suprimida**, not zero.
- **Limitations:** no cause of death and no race of the deceased. Race columns in this theme refer to the household responsible person.
- **Coverage in this repo:** mortality dots for all 27 UFs.

## Malha municipal 2022 — por UF (polígonos de hover)

- **Official name:** Malha Municipal Digital 2022 — municípios por UF
- **URL pattern:** `https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2022/UFs/{UF}/{UF}_Municipios_2022.zip`
- **Used by:** `scripts/build_municipality.py` (hover polygons z3–9; dots at z3–6 use clustered setores instead)
- **Fields used:** `CD_MUN` → `id_municipio`, `NM_MUN` → `municipio`, `SIGLA_UF` → `sigla_uf`
- **Built so far:** all 27 UFs

## Malha de setores 2022 — por UF (polígonos para dots 3–14)

- **Official name:** Malha de Setores Censitários 2022 (oficial, não a preliminar)
- **URL pattern:** `https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_de_setores_censitarios__divisoes_intramunicipais/censo_2022/setores/shp/UF/{UF}_setores_CD2022.zip`
- **Used by:** `scripts/build_census_tract.py` (join on `CD_SETOR`; input for zoom 7–14) and `scripts/build_density_clusters.py` (`CD_SIT` / `AREA_KM2`; input for zoom 3–6 clustered dots)
- **Why per-UF:** the national `BR_setores_CD2022.gpkg` is ~1.4 GB and is not downloaded
- **Join caveat:** malha has more setores than the race table (empty / no-people cells). Unmatched polygons get zero dots. All 27 UFs are built.

## Not downloaded in this slice

- National setor malha (`BR_setores_CD2022.gpkg`, ~1.4 GB). Do not download it; use the per-UF SHP above.
- Alfabetização, saneamento, and religião files.

## Re-download

```sh
mkdir -p data/censo2022/raw
cd data/censo2022/raw
curl -fL -O https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Setor_csv/Agregados_por_setores_cor_ou_raca_BR.zip
curl -fL -O https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/dicionario_de_dados_agregados_por_setores_censitarios_20260520.xlsx
unzip -o Agregados_por_setores_cor_ou_raca_BR.zip
```
