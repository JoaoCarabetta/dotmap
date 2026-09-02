Agent instructions for this repo live in [`AGENTS.md`](../AGENTS.md). Project layout is in [`structure.md`](structure.md). How to serve the map from the versioned MBTiles is in [`local-setup.md`](local-setup.md). The public page is [https://carabetta.xyz/dataviz/brazildots/](https://carabetta.xyz/dataviz/brazildots/).

# Zoom Levels and Dot Density Configuration

This document describes the relationship between zoom levels and dot density in the map visualization.

## Configuration Table

Source of truth for **how tiles are generated** is [`makefiles.sh`](../makefiles.sh): `aggregation_levels` (`city` → `municipality_{UF}.geojson`, otherwise `census_tract_{UF}.geojson`) plus `per_dot_values`. The legend (`1 ponto = N pessoas`) and the localhost HUD **fonte** / pessoas/ponto use this same table. Zoom 15 has no tiles; N is the z14 value (20).

### Geometry source by zoom (`makefiles.sh`)

| Zoom | Geometry source | `per_dot` (people per dot) |
|------|-----------------|----------------------------|
| 3 | município (`city` → `municipality_*.geojson`) | 24 000 |
| 4 | município (`city`) | 12 000 |
| 5 | município (`city`) | 6 000 |
| 6 | município (`city`) | 3 000 |
| 7 | setor censitário (`census` → `census_tract_*.geojson`) | 150 |
| 8 | setor censitário | 120 |
| 9 | setor censitário | 90 |
| 10 | setor censitário | 70 |
| 11 | setor censitário | 50 |
| 12 | setor censitário | 35 |
| 13 | setor censitário | 25 |
| 14 | setor censitário | 20 |
| 15 | *(no tiles — camera overzooms the z=14 setor set)* | 20 |

Hover on the map is a different cutoff: município polygons below zoom 10, setor from 10. Do not read hover as the tile-generation unit.

The comment in `makefiles.sh` (“Zoom 3-6 = municipality; 7-14 = census tract”) matches the arrays. The next line (“per_dot doubles each step out from 4”) is only true for zooms 3–6; the jump from 3 000 (z6) to 150 (z7) is not a doubling.

| Zoom | Aggregation | People per dot (`per_dot`) | Approx. RJ dots | Circle radius (px) |
|------|-------------|----------------------------|-----------------|--------------------|
| 3 | Municipality (`city`) | 24 000 | ~670 | 0.96 |
| 4 | Municipality (`city`) | 12 000 | ~1 300 | 0.96 |
| 5 | Municipality (`city`) | 6 000 | ~2 700 | 0.96 |
| 6 | Municipality (`city`) | 3 000 | ~5 300 | 0.96 |
| 7 | Census tract | 150 | ~110 000 | 0.96 |
| 8 | Census tract | 120 | | 1.04 |
| 9 | Census tract | 90 | | 1.12 |
| 10 | Census tract | 70 | | 1.20 |
| 11 | Census tract | 50 | | 1.28 |
| 12 | Census tract | 35 | | 1.36 |
| 13 | Census tract | 25 | | 2.16 |
| 14 | Census tract | 20 | | 2.16 |
| 15 | Census tract (overzoom) | 20 | | 2.16 |

## Details

- **Municipality (zoom 3–6):** Points are scattered inside each município. At zoom 3–4 the continent/country fits the screen; `per_dot` stays high so filled states read as clusters, not a blob. Towns smaller than `per_dot` can receive zero points.
- **Census tract (zoom 7–14):** Higher precision. The jump from zoom 6 (~5k municipal dots in RJ) to zoom 7 (~110k setor dots in RJ) is intentional with the current pipeline; the original TODO table used city aggregation at zoom 7 (`per_dot` 2000) to soften that step.
- Recorte atual dos pontos: **27 UFs** (cobertura nacional). Hover de município/setor vem de `data/tiles/hover.mbtiles` (não do GeoJSON concatenado): o `census_tract.geojson` nacional (~248 MB) trava o Mapbox no zoom alto.
- The Mapbox map `minZoom` option is exclusive (`zoom > min`), so `index.html` sets it to **2** in order to reach the z=3 tiles. Camera `maxZoom` is **15** so the local Rio shortcut can overzoom; the vector source still advertises `minzoom: 3` / `maxzoom: 14` (no z=15 PBF).
- The map **opens on Brazil as a whole**, not Rio: constructor fallback `[-51.9, -14.2]` at zoom 3.5, then `fitBounds` of `[[-74, -34], [-32, 6]]` on load so Norte/Sul stay on screen across viewports. Point tiles cover all 27 UFs. A `tile-join` without `--no-tile-size-limit` still drops the SP+MG overlap at z7 (XYZ `7/47/72`, ~508 KB vs the 500 KB default) and leaves São Paulo blank even though `tiles/SP/` is complete.
- Circle radius is a linear interpolate on stops 3 / 7 / 12 / 13 (`0.96` → `0.96` → `1.36` → `2.16` px): ×1.2 everywhere, then an extra ×1.5 from zoom 13 (held through 15). The z12 stop keeps the 50% kick from ramping in at 12. People-per-dot is unchanged.

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

`output/tiles/race/municipality.geojson` (intermediate; the map reads `data/tiles/hover.mbtiles`)
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

The map uses Mapbox **light-v10** (`mapbox://styles/mapbox/light-v10`): land/water, coastlines, admin boundaries, and light roads, paired with Mapbox GL JS 2.3.1. After the style is ready, every `symbol` layer is set to `visibility: none` so place/road/POI labels stay off. Geography layers stay. Do not switch back to dark-v10 or to a blank custom style.

Hover outlines on `setores-border` and `municipios-border` are `#202124` so they stay visible on the light style. The matching fill layers (`setores-fill`, `municipios-fill`) stay a hit target at opacity 0 and pick up an 8% `#202124` tint only while hovered.

### Dot colors

| Key | Hex | Why |
|---|---|---|
| `branca` | `#4daf4a` | green — ColorBrewer Set1, permuted from HUD test; contrast on light-v10 |
| `preta` | `#ff7f00` | orange |
| `amarela` | `#377eb8` | blue |
| `parda` | `#e41a1c` | red |
| `indigena` | `#984ea3` | purple |

This mapping is the product default (`circle-color` match + legend swatches) and HUD **Atual**. Production users get it with no HUD. Do not restore the old red/gold/mint set (`#fb3640` / `#d4b000` / `#89ffa7` / `#3899c9` / `#e8800c`). The two floating cards, the search field, and the slim footer keep light chrome (white surfaces, dark text) on top of the light map.

# Map chrome

The map is full-bleed (`#map` is `100vw` / `100vh`). There is **no** fixed header and **no left icon rail**. Chrome is two floating cards plus a slim full-width footer (~32px): intro top-left (`.chrome-stack`, 14px inset) and the legend bottom-left, above the footer. Zoom `+/-` stays at the bottom-right, just above the footer. The first camera is a Brazil overview (`fitBounds` of `[[-74, -34], [-32, 6]]`); search still uses the RJ bbox.

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

Hover numbers live in the Mapbox **popup on the map** (município below zoom 10, setor from zoom 10): name, race shares, and população. The dark hover outline stays on the map. The legend card does not repeat those numbers.

There is no logo. Zoom is the Mapbox `NavigationControl` at the bottom-right; the public page has no on-screen “Zoom level: N” badge. The public URL slug remains `brazildots`.

On ≤640px the intro card can shrink so it does not collide with the bottom-left legend. Solo buttons stay visible on that breakpoint.

# Local dev panel

A compact HUD is injected only on loopback hosts (`localhost`, `127.0.0.1`, `::1`, `*.localhost`). Production (`carabetta.xyz`) never gets the toggle or the panel.

- Off by default. Toggle with the top-right **dev** button or `D` / `` ` `` (ignored while typing in the search field). `sessionStorage` key `dotmap-dev-panel` keeps it open across refresh.
- Live fields, updated on `move` / `zoom`: pessoas/ponto (same `peoplePerDot` table as the legend and `makefiles.sh`), center, bbox, hover layer (`município` below zoom 10, `setor` from 10), and **fonte** (tile-generation unit from `makefiles.sh`: município at z3–6, setor at z7–14, setor overzoom at 15). Fonte is not hover.
- **Zoom** and **raio** are editable (localhost only). Zoom is a slider + number (2–15) that calls `map.setZoom`. Raio is a **multiplier** (0.5×–3×, default 1) on top of the coded interpolate (so the z13 ×1.5 bump stays). `reset` returns the multiplier to 1. The effective px is shown next to the control. Multiplier is stored in `sessionStorage` key `dotmap-dev-radius-mult`. Keyboard shortcuts ignore these inputs the same way as the geocoder.
- **Cores** (localhost only): a select of 5-hue presets mapped to `branca`, `preta`, `amarela`, `parda`, `indigena`. Applying a palette updates the points `circle-color` match and the legend swatches. Presets: **Atual** (product default — ColorBrewer Set1 hues permuted from HUD test), **Dark2** (ColorBrewer), **Set1** (ColorBrewer, unpermuted), **Okabe–Ito** (colorblind-safer; skips `#F0E442` because it vanishes on light-v10), **Print** (high-contrast), **Terra** (muted earth tones). **permutar** rotates assignment (each race takes the next of the same 5 hues; 5 steps, not 5! buttons). **embaralhar** shuffles those 5 hues once. **reset** restores the selected palette’s default mapping. Compact swatch + hex list shows the current key → color. Stored in `sessionStorage` as `dotmap-dev-palette`, `dotmap-dev-permute` (rotation index 0–4), and `dotmap-dev-hues` (working order after shuffle). Production (`carabetta.xyz`) never loads this UI or these keys.
- Camera jumps (localhost only, ignored while typing in search): **1** Brasil (`fitBounds` of the default country bbox), **2** Rio center `[-43.1729, -22.9068]` at zoom **15**. Same actions as the two HUD buttons.
- Monospace overlay, not a product card. All logic stays in `index.html`. The panel scrolls if the color block would otherwise cover zoom/footer.

# Credits

Credits sit in `.map-footer`, a slim full-width bar (~32px, wraps on narrow screens), not in either card and not as a second explainer. “Dados: IBGE” links to the official [Agregados por Setores Censitários 2022](https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/) FTP collection (the source documented in [`fontes.md`](fontes.md)), not the IBGE homepage. “Censo Demográfico 2022” links to the [Censo 2022 dataset on Base dos Dados](https://basedosdados.org/dataset/08a1546e-251f-4546-9fe0-b1e6ab2b203d) (the 2022-specific page, not the older `br-ibge-censo-demografico` collection). Then: [GitHub](https://github.com/JoaoCarabetta/dotmap) (this repo), [Carabetta.xyz](https://carabetta.xyz), and `© 2026 Carabetta.xyz`.
