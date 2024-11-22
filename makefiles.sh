#!/bin/bash
# Check if UF argument is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <UF>"
    echo "Example: $0 AC"
    exit 1
fi

UF=$1

# Increase Node.js memory limit
export NODE_OPTIONS="--max-old-space-size=8192"

# Define input GeoJSON files for different aggregation levels
census_tract_geojson="data/censo2022/output/tiles/race/census_tract_${UF}.geojson"
municipality_geojson="data/censo2022/output/tiles/race/municipality_${UF}.geojson"
output_directory="dots"
tiles_directory="tiles"

# Remove the existing tiles directory if it exists
echo ">> Removing existing tiles directory if it exists"
rm -rf $tiles_directory

# Define races
races=("branca" "preta" "amarela" "parda" "indigena")

# Combine races into a string for Mapshaper
fields=$(IFS=,; echo "${races[*]}")
echo ">> Fields for Mapshaper: $fields"

# Create tiles directory
echo ">> Creating tiles directory"
mkdir -p $tiles_directory

# Define zoom level ranges and corresponding per-dot values based on reference table
# Format: zoom levels, dots per person, and aggregation level
min_zoom_levels=(4  5  6  7  8  9  10 11 12 13)
max_zoom_levels=(4  5  6  7  8  9  10 11 12 13)
per_dot_values=(500 500 500 500 500 500 200 120 60 40)
# City level: zoom 4-7, Census tract level: zoom 8-13
aggregation_levels=("census" "census" "census" "census" "census" "census" "census" "census" "census" "census")

# Loop through zoom level ranges
echo ">> Generating dot density files and tilesets"
for i in "${!min_zoom_levels[@]}"; do
    min_zoom=${min_zoom_levels[$i]}
    max_zoom=${max_zoom_levels[$i]}
    per_dot=${per_dot_values[$i]}
    aggregation=${aggregation_levels[$i]}
    output_geojson="${output_directory}/zoom${min_zoom}-${max_zoom}/points.geojson"

    echo ">> Processing zoom levels: $min_zoom to $max_zoom with per-dot value: $per_dot (${aggregation} level)"

    # Create directory for dot density files
    mkdir -p "$(dirname "$output_geojson")"

    # Select input file based on aggregation level
    input_geojson=""
    if [ "$aggregation" = "city" ]; then
        input_geojson=$municipality_geojson
    else
        input_geojson=$census_tract_geojson
    fi

    # Generate dot density file for the zoom level range with race data
    echo ">> Running mapshaper for zoom levels $min_zoom to $max_zoom using ${aggregation} data"
    mapshaper $input_geojson -dots fields=$fields values=$fields \
    save-as=race per-dot=$per_dot evenness=0.5 -o $output_geojson 

    # Check for errors
    if [ $? -ne 0 ]; then
        echo "Error in mapshaper command"
        exit 1
    fi

    # Create tileset for the zoom level range and save in a directory
    tileset_directory="${tiles_directory}/zoom${min_zoom}-${max_zoom}"
    mkdir -p $tileset_directory

    # Generate tileset
    echo ">> Running tippecanoe for zoom levels $min_zoom to $max_zoom"
    tippecanoe -o "${tileset_directory}/tiles.mbtiles" -z$max_zoom -Z$min_zoom $output_geojson --force -P -r1

    # Check for errors
    if [ $? -ne 0 ]; then
        echo "Error in tippecanoe command"
        exit 1
    fi
done

# Merge all tilesets into a single file
echo ">> Merging tilesets"
mkdir -p output
tile-join -o "data/tiles/censo2022.mbtiles" $tiles_directory/*/tiles.mbtiles --force
echo ">> Done"
