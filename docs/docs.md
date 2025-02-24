# Zoom Levels and Dot Density Configuration

This document describes the relationship between zoom levels and dot density in the map visualization.

## Configuration Table


| Dot Density | Aggregation | Zoom Level | Dot Size (px) |
|-------------|-------------|------------|---------------|
| 5          | Census      |   14        | 1.2           |
| 10          | Census      |   13       | 1.2           |
| 15          | Census      |   12      | 1.2           |
| 20          | Census      |   11      | 1.1           |
| 25          | Census      |   10      | 1.1           |
| 30          | Census      |   9       | 1.0           |
| 35          | Census      |   8       | 1.0           |
| 40          | Census      |   7       | 0.8           |


## Details

- **Census Tract Level (Zoom 8-13)**: Higher precision representation with lower dots-per-person values, suitable for detailed neighborhood analysis
- **City Level (Zoom 4-7)**: More aggregated view with higher dots-per-person values, suitable for broader regional patterns
- **Dot Density**: Values are chosen to maintain visual clarity while accurately representing population distribution at each zoom level 

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

`output/tiles/race/municipality.geojson`
Contains aggregated demographic data at the municipality level with the following attributes:
- `id_municipio`: Municipality code
-  `sigla_uf`: State code
- `municipio`: Municipality name
- `populacao`: Total population
- `branca`: White population count
- `preta`: Black population ount
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
  
  