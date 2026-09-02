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

- **Municipality (zoom 3–6):** Points are scattered inside each município. At zoom 3–4 the continent/country fits the screen and only RJ has dots, so a high `per_dot` keeps the state as a readable cluster instead of a solid blob. Towns smaller than `per_dot` can receive zero points.
- **Census tract (zoom 7–14):** Higher precision. The jump from zoom 6 (~5k municipal dots) to zoom 7 (~110k setor dots) is intentional with the current pipeline; the original TODO table used city aggregation at zoom 7 (`per_dot` 2000) to soften that step.
- Recorte atual: RJ only. Zooming out to 3–6 shows an empty rest of Brazil.
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

`output/tiles/race/municipality.geojson` (local hover file is `municipality_RJ.geojson`)
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

# Footer

The footer credits IBGE / Censo 2022 on the left. On the right: GitHub, a link to [Carabetta.xyz](https://carabetta.xyz), and `© 2026 Carabetta.xyz`.
