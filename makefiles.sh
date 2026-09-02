#!/bin/bash
# Check if UF argument is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <UF> [zooms]"
    echo "Example: $0 RJ"
    echo "Example: $0 RJ 3,4,5,6"
    exit 1
fi

UF=$1
# Optional comma-separated zoom list so we can rebuild 3-6 without touching 7-14.
ONLY_ZOOMS="${2:-}"

# Increase Node.js memory limit
export NODE_OPTIONS="--max-old-space-size=8192"

# Define input GeoJSON files for different aggregation levels
census_tract_geojson="data/censo2022/output/tiles/race/census_tract_${UF}.geojson"
municipality_geojson="data/censo2022/output/tiles/race/municipality_${UF}.geojson"
output_directory="dots"
tiles_directory="tiles"

# Never rm -rf tiles/: zooms 7-14 are versioned and expensive to regenerate.
# Each zoom dir below is overwritten only if that zoom is in this run.

# Define races
races=("branca" "preta" "amarela" "parda" "indigena")

# Combine races into a string for Mapshaper
fields=$(IFS=,; echo "${races[*]}")
echo ">> Fields for Mapshaper: $fields"

# Create tiles directory
echo ">> Creating tiles directory"
mkdir -p $tiles_directory

# mapshaper is not always on PATH; npx matches how tileserver-gl is invoked.
if command -v mapshaper >/dev/null 2>&1; then
    MAPSHAPER=(mapshaper)
else
    MAPSHAPER=(npx --yes mapshaper)
fi

# Zoom 3-6 = municipality (city); 7-14 = census tract.
# per_dot doubles each step out from 4 so continental views stay a cluster, not a blob.
min_zoom_levels=(3     4     5    6    7   8   9   10  11  12  13  14)
max_zoom_levels=(3     4     5    6    7   8   9   10  11  12  13  14)
per_dot_values=(24000 12000 6000 3000 150 120 90  70  50  35  25  20)
aggregation_levels=("city" "city" "city" "city" "census" "census" "census" "census" "census" "census" "census" "census")

# Loop through zoom level ranges
echo ">> Generating dot density files and tilesets"
for i in "${!min_zoom_levels[@]}"; do
    min_zoom=${min_zoom_levels[$i]}
    max_zoom=${max_zoom_levels[$i]}
    per_dot=${per_dot_values[$i]}
    aggregation=${aggregation_levels[$i]}

    if [ -n "$ONLY_ZOOMS" ]; then
        case ",$ONLY_ZOOMS," in
            *",$min_zoom,"*) ;;
            *) continue ;;
        esac
    fi

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

    if [ ! -f "$input_geojson" ]; then
        echo "Error: missing input $input_geojson"
        exit 1
    fi

    # Generate dot density file for the zoom level range with race data
    echo ">> Running mapshaper for zoom levels $min_zoom to $max_zoom using ${aggregation} data"
    "${MAPSHAPER[@]}" $input_geojson -dots fields=$fields values=$fields \
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
    tippecanoe -o "${tileset_directory}/tiles.mbtiles" -z$max_zoom -Z$min_zoom $output_geojson --force -P -r1 --drop-fraction-as-needed

    # Check for errors
    if [ $? -ne 0 ]; then
        echo "Error in tippecanoe command"
        exit 1
    fi
done

# Merge all tilesets into a single file
echo ">> Merging tilesets"
mkdir -p data/tiles
# tippecanoe's tile-join uses -f (overwrite), not --force
tile-join -f -o "data/tiles/censo2022.mbtiles" $tiles_directory/*/tiles.mbtiles
echo ">> Done"
