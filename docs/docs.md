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

# Interactive Legend Controls

## Race Category Toggles

The legend provides two ways to control the visibility of racial categories:

### Category Toggle
- Click on any category label to toggle its visibility
- Multiple categories can be visible simultaneously
- Categories can be toggled independently

### Solo Mode
- Each category has a "S" (Solo) button that appears on hover
- Click the Solo button to show only that category
- All other categories will be automatically hidden
- Useful for analyzing individual racial distributions

### Visual Feedback
- Disabled categories appear semi-transparent
- Hover effects indicate interactive elements
- Solo buttons appear on hover for a cleaner interface
- All categories are visible by default

### Available Categories
- Branca (White)
- Preta (Black)
- Amarela (Asian)
- Parda (Brown/Mixed)
- Indígena (Indigenous)

### Technical Implementation
- Uses Mapbox GL JS filters for visibility control
- Maintains a Set of active races for efficient filtering
- Separate click handlers for toggle and solo modes
- Updates are applied immediately to the map visualization

# Basemap

The map uses Mapbox **dark-v10** (`mapbox://styles/mapbox/dark-v10`): a dark street basemap so the race-dot colors stay the visual focus.

Hover outlines on `setores-border` and `municipios-border` are `white` so they stay visible on the dark style.

Dot colors are unchanged. The floating sidebar and the hover tooltip use light chrome (white panels, dark text) on top of the dark map.

# Sidebar chrome

The map is full-bleed (`#map` is `100vw` / `100vh`). There is no fixed header or footer bar. Title, explanation, search, race legend, and credits live in a single floating left card (`.sidebar`, ~340px, 16px from the top-left) so the map is not letterboxed by 60px chrome and so the legend is not a second competing box.

The product title (`h1.sidebar-title` and the page `<title>`) is **Onde o Brasil mora**. It is product-level so later views (other census themes) can share the same name. The subtitle (`p.sidebar-subtitle`) is **Cada ponto é um grupo de pessoas. A cor é a raça no Censo 2022.** — it explains the viz for someone who has never seen the map (what the dots are, then what the colors mean and the source). Do not say “um ponto por pessoa”: one dot is N people and N changes with zoom. Do not restore the old h1 “Distribuição Racial no Brasil” (too close to Pata’s 2015 *Mapa Racial do Brasil*) or a one-word “Raça” label. Future views rewrite the explanation, not the h1. There is no logo. Zoom is changed with the Mapbox control (top-right, 16px inset on desktop; bottom-right on viewports ≤520px so it does not sit on the full-width card); there is no on-screen “Zoom level: N” badge. The public URL slug remains `brazildots`. The hover tooltip stays a map overlay; it is not in the sidebar.

The card also has a **search box** powered by [`mapbox-gl-geocoder`](https://github.com/mapbox/mapbox-gl-geocoder) v5 against Mapbox Temporary Geocoding — the same token as the basemap, no Google key. Placeholder: **Buscar cidade, CEP ou endereço**. Results are limited to Brazil and to an RJ bounding box (`[-44.89, -23.37, -40.75, -20.76]`) with proximity to Rio, because the dots only exist in that recorte. Selecting a result `fitBounds` the map; there is no persistent pin so the marker would not compete with the race-dot colors. Full Brazilian CEPs (`XXXXX-XXX`) are resolved via [BrasilAPI](https://brasilapi.com.br/) (`/cep/v2`) because Mapbox postcode matching is weak for that format; city, bairro, and address stay on Mapbox. CEPs outside RJ are dropped.

On viewports ≤520px the card stays a short top strip (title, subtitle, search). A chevron (`#sidebar-toggle`) expands or collapses the legend and credits so a ~390px-wide phone still has a usable map. Solo buttons stay visible on that breakpoint because there is no hover.

# Credits

Credits sit at the bottom of the sidebar card, not in a full-width footer. “Dados: IBGE” links to the official [Agregados por Setores Censitários 2022](https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/) FTP collection (the source documented in [`fontes.md`](fontes.md)), not the IBGE homepage. “Censo Demográfico 2022” links to the [Censo 2022 dataset on Base dos Dados](https://basedosdados.org/dataset/08a1546e-251f-4546-9fe0-b1e6ab2b203d) (the 2022-specific page, not the older `br-ibge-censo-demografico` collection). Then: [GitHub](https://github.com/JoaoCarabetta/dotmap) (this repo), [Carabetta.xyz](https://carabetta.xyz), and `© 2026 Carabetta.xyz`.
