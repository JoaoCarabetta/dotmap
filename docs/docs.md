# Zoom Levels and Dot Density Configuration

This document describes the relationship between zoom levels and dot density in the map visualization.

## Configuration Table

| Dot Density | Aggregation | Zoom Level |
|-------------|-------------|-----------|
| 40          | Census      |   13      |
| 60          | Census      |   12      |
| 120         | Census      |   11      |
| 200         | Census      |   10      |
| 500         | Census      |   9       |
| 500        | Census      |   8       |
| 500        | Census        |   7       |
| 500        | Census        |   6       |
| 500        | Census        |   5       |
| 500       | Census        |   4       |


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
  
  