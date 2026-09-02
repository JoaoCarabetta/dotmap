Agent instructions for this repo live in [`AGENTS.md`](../AGENTS.md). Project layout is in [`structure.md`](structure.md). How to serve the map from the versioned MBTiles is in [`local-setup.md`](local-setup.md). The public page is [https://carabetta.xyz/dataviz/brazildots/](https://carabetta.xyz/dataviz/brazildots/).

# Zoom Levels and Dot Density Configuration

This document describes the relationship between zoom levels and dot density in the map visualization.

## Configuration Table

Source of truth is [`makefiles.sh`](../makefiles.sh) (`per_dot` + aggregation). The legend in `index.html` matches zooms 3–6; zooms 7–14 in the legend are still the older city/census table and do **not** match the pipeline.

| Zoom | Aggregation | People per dot (`per_dot`) | Approx. RJ dots | Circle radius (px) |
|------|-------------|----------------------------|-----------------|--------------------|
| 3 | Municipality (`city`) | 24 000 | ~670 | 0.8 |
| 4 | Municipality (`city`) | 12 000 | ~1 300 | 0.8 |
| 5 | Municipality (`city`) | 6 000 | ~2 700 | 0.8 |
| 6 | Municipality (`city`) | 3 000 | ~5 300 | 0.8 |
| 7 | Census tract | 150 | ~110 000 | 0.8 |
| 8 | Census tract | 120 | | 1.0 |
| 9 | Census tract | 90 | | 1.0 |
| 10 | Census tract | 70 | | 1.1 |
| 11 | Census tract | 50 | | 1.1 |
| 12 | Census tract | 35 | | 1.2 |
| 13 | Census tract | 25 | | 1.2 |
| 14 | Census tract | 20 | | 1.2 |

## Details

- **Municipality (zoom 3–6):** Points are scattered inside each município. At zoom 3–4 the continent/country fits the screen; `per_dot` stays high so filled states read as clusters, not a blob. Towns smaller than `per_dot` can receive zero points.
- **Census tract (zoom 7–14):** Higher precision. The jump from zoom 6 (~5k municipal dots in RJ) to zoom 7 (~110k setor dots in RJ) is intentional with the current pipeline; the original TODO table used city aggregation at zoom 7 (`per_dot` 2000) to soften that step.
- Recorte atual dos pontos: **RJ, RR, AP, AC**. O resto do Brasil fica vazio até a próxima onda (TO, RO, SE, …, SP).
- The Mapbox map `minzoom` option is exclusive (`zoom > min`), so `index.html` sets it to **2** in order to reach the z=3 tiles. The vector source still advertises `minzoom: 3`.

# Demographic Data Structure

This document describes the structure of the demographic data files.

## Files

### Census Tract Level

`output/tiles/race/census_tract.geojson`
Contains demographic data at the census tract level with the following attributes:
- `id_setor_censitario`: Census tract ID
- `sigla_uf`: State code
- `populacao`: Total population
- `branca`: White population count
- `preta`: Black population count
- `amarela`: Asian population count
- `parda`: Brown/Mixed population count
- `indigena`: Indigenous population count

### Municipality Level

`output/tiles/race/municipality.geojson` (local hover file used by the map)
Contains aggregated demographic data at the municipality level with the following attributes:
- `id_municipio`: Municipality code
- `sigla_uf`: State code
- `municipio`: Municipality name
- `populacao`: Total population
- `branca`: White population count
- `preta`: Black population count
- `amarela`: Asian population count
- `parda`: Brown/Mixed population count
- `indigena`: Indigenous population count

## Usage Notes
- Census tract data is suitable for detailed local analysis
- Municipality data is better for regional patterns and overview
- All population counts are absolute numbers

# Interactive Race Filter

Race filters live in the **legend card** (`.detail-card`), pinned to the bottom-left above the slim footer. Each legend row is a toggle. There is no Raça chip or dropdown. Do not add other layer chips yet.

## Legend rows
- One row per IBGE category: color swatch + name. Clicking the row **toggles** that race. Multi-select is the default. Off rows fade (`is-off`).
- Each row has an **S** (solo) button. On hover/focus it appears; on ≤640px it stays visible because there is no hover.

## Available Categories
- Branca (White)
- Preta (Black)
- Amarela (Asian)
- Parda (Brown/Mixed)
- Indígena (Indigenous)

Do not add categories beyond these five IBGE keys (`branca`, `preta`, `amarela`, `parda`, `indigena`).

## Technical Implementation
- Mapbox GL JS `setFilter` / `circle-opacity` on the `points` layer
- A `Set` of active races
- Separate handlers on `.race-row-toggle` and `.solo-button`
- `syncFilterUi()` keeps the legend rows in the same Set

# Basemap

The map uses Mapbox **dark-v10** (`mapbox://styles/mapbox/dark-v10`): a dark street basemap so the race-dot colors stay the visual focus.

Hover outlines on `setores-border` and `municipios-border` are `white` so they stay visible on the dark style.

Dot colors are unchanged. The two floating cards, the search field, and the slim footer use light chrome (white surfaces, dark text) on top of the dark map.

# Map chrome

The map is full-bleed (`#map` is `100vw` / `100vh`). There is **no** fixed header and **no left icon rail**. Chrome is two floating cards plus a slim full-width footer (~32px): intro top-left (`.chrome-stack`, 14px inset) and the legend bottom-left, above the footer. Zoom `+/-` stays at the bottom-right, just above the footer.

## Left card (`.intro-card`)

White rounded card, top-left. Title + explainer + divider + search (Arquivo da Violência layout).

The product title (`h1.intro-title` and the page `<title>`) is **Onde o Brasil mora**. It is product-level so later views can share the same name. The explainer (`p.intro-explainer`) is:

**Cada ponto é um grupo de pessoas. A cor é a raça declarada no Censo Demográfico 2022 (IBGE). O número de pessoas por ponto muda com o zoom.**

Do not say “um ponto por pessoa”: one dot is N people and N changes with zoom. Do not restore the old h1 “Distribuição Racial no Brasil” (too close to Pata’s 2015 *Mapa Racial do Brasil*). Future views rewrite the explanation, not the h1.

Search sits **inside** this card, powered by [`mapbox-gl-geocoder`](https://github.com/mapbox/mapbox-gl-geocoder) v5 against Mapbox Temporary Geocoding — the same token as the basemap, no Google key. Placeholder: **Busque por cidade, bairro, estado ou CEP**. Results are limited to Brazil and to an RJ bounding box (`[-44.89, -23.37, -40.75, -20.76]`) with proximity to Rio, because the dots only exist in that recorte. Selecting a result `fitBounds` the map; there is no persistent pin so the marker would not compete with the race-dot colors. Full Brazilian CEPs (`XXXXX-XXX`) are resolved via [BrasilAPI](https://brasilapi.com.br/) (`/cep/v2`) because Mapbox postcode matching is weak for that format; city, bairro, and address stay on Mapbox. CEPs outside RJ are dropped.

Do not restore a standalone search chrome or a Raça chip.

## Legend card (`.detail-card`)

White rounded card, pinned **bottom-left** (`position: fixed; left: 14px`), sitting above the slim footer (`bottom: calc(var(--footer-height) + 14px)`). Compact (~268px wide). It is **not** stacked under the intro card. It holds:

1. The five race rows (the filter — see [Interactive Race Filter](#interactive-race-filter)).
2. `1 ponto = N pessoas` (existing zoom scale).

Hover numbers live in the Mapbox **popup on the map** (município below zoom 10, setor from zoom 10): name, race shares, and população. The white hover outline stays on the map. The legend card does not repeat those numbers.

There is no logo. Zoom is the Mapbox `NavigationControl` at the bottom-right; there is no on-screen “Zoom level: N” badge. The public URL slug remains `brazildots`.

On ≤640px the intro card can shrink so it does not collide with the bottom-left legend. Solo buttons stay visible on that breakpoint.

# Credits

Credits sit in `.map-footer`, a slim full-width bar (~32px, wraps on narrow screens), not in either card and not as a second explainer. “Dados: IBGE” links to the official [Agregados por Setores Censitários 2022](https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/) FTP collection (the source documented in [`fontes.md`](fontes.md)), not the IBGE homepage. “Censo Demográfico 2022” links to the [Censo 2022 dataset on Base dos Dados](https://basedosdados.org/dataset/08a1546e-251f-4546-9fe0-b1e6ab2b203d) (the 2022-specific page, not the older `br-ibge-censo-demografico` collection). Then: [GitHub](https://github.com/JoaoCarabetta/dotmap) (this repo), [Carabetta.xyz](https://carabetta.xyz), and `© 2026 Carabetta.xyz`.
