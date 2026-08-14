import adif_io
import folium
from folium import FeatureGroup, LayerControl
from branca.element import Element
import json

# Your home locator
MY_HOME_GRID = "JN65XF"

# 1. Define bands to track
target_bands = ['160m', '80m', '40m', '30m', '20m', '17m', '15m', '12m', '10m', '6m']

# Statistics data structures
global_grid_stats = {}
band_counters = {band: 0 for band in target_bands}

# 2. Load ADIF file
adif_file_path = "lotwreport.adi"

try:
    with open(adif_file_path, "r", encoding="utf-8") as f:
        qsos, header = adif_io.read_from_string(f.read())
        for qso in qsos:
            band = qso.get("BAND", "").lower()
            if band not in target_bands:
                continue
            
            grid = qso.get("GRIDSQUARE", "").strip().upper()
            if len(grid) >= 4:
                quad_4 = grid[:4]
                callsign = qso.get("CALL", "").upper()
                
                if quad_4 not in global_grid_stats:
                    global_grid_stats[quad_4] = {band_name: {'worked': False, 'stations': set()} for band_name in target_bands}
                    global_grid_stats[quad_4]['all_stations'] = set()
                
                global_grid_stats[quad_4][band]['worked'] = True
                global_grid_stats[quad_4][band]['stations'].add(callsign)
                global_grid_stats[quad_4]['all_stations'].add(callsign)
                
except FileNotFoundError:
    print(f"Error: File '{adif_file_path}' not found.")
    exit()

# Calculate totals per band for buttons
for grid_name, data in global_grid_stats.items():
    for band in target_bands:
        if data[band]['worked']:
            band_counters[band] += 1

# 3. Helper functions
def locator_to_bbox(locator):
    try:
        locator = locator.upper()
        lon_field = (ord(locator[0]) - ord('A')) * 20 - 180
        lat_field = (ord(locator[1]) - ord('A')) * 10 - 90
        lon_square = int(locator[2]) * 2
        lat_square = int(locator[3]) * 1
        
        west = lon_field + lon_square
        east = west + 2
        south = lat_field + lat_square
        north = south + 1
        return south, north, west, east
    except Exception:
        return None

def home_locator_to_latlon(loc):
    try:
        loc = loc.upper()
        lon = (ord(loc[0]) - ord('A')) * 20 - 180 + int(loc[2]) * 2 + (ord(loc[4]) - ord('A') + 0.5) / 12
        lat = (ord(loc[1]) - ord('A')) * 10 - 90 + int(loc[3]) * 1 + (ord(loc[5]) - ord('A') + 0.5) / 24
        return lat, lon
    except Exception:
        return 45.229, 13.958

home_lat, home_lon = home_locator_to_latlon(MY_HOME_GRID)

# Heatmap color palette
heatmap_colors = ["#c8f7dc", "#a3f3c2", "#7eeba8", "#59e28e", "#34da74", "#2bc063", "#24a653", "#1d8c43", "#167233", "#0f5924"]

# 4. Prepare GeoJSON features
features_list = []

for grid_name, data in global_grid_stats.items():
    bbox = locator_to_bbox(grid_name)
    if not bbox:
        continue
    south, north, west, east = bbox
    
    worked_bands = [b for b in target_bands if data[b]['worked']]
    band_count = len(worked_bands)
    
    properties = {
        "grid": grid_name,
        "total_bands": band_count,
        "bands_list": ", ".join([b.upper() for b in sorted(worked_bands)]),
        "total_stations": len(data['all_stations']),
        "total_color": heatmap_colors[min(band_count - 1, 9)],
        "total_opacity": 0.35 + (band_count / 10.0) * 0.45,
        "all_stations_html": "<br>".join(sorted(list(data['all_stations'])))
    }
    
    for band in target_bands:
        properties[f"{band}_worked"] = data[band]['worked']
        properties[f"{band}_stations_count"] = len(data[band]['stations'])
        properties[f"{band}_stations_html"] = "<br>".join(sorted(list(data[band]['stations'])))
    
    feature = {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[west, south], [east, south], [east, north], [west, north], [west, south]]]
        },
        "properties": properties
    }
    features_list.append(feature)

geojson_data = {"type": "FeatureCollection", "features": features_list}

# 5. Create map
print(f"Packing {len(global_grid_stats)} unique grid squares with band filter...")
m = folium.Map(location=[20.0, 0.0], zoom_start=3, tiles="CartoDB positron")

folium.Marker(
    location=[home_lat, home_lon],
    popup=f"<b>Home Station</b><br>Grid: {MY_HOME_GRID}",
    icon=folium.Icon(color="red", icon="star")
).add_to(m)

# 6. HTML/CSS/JS Injection
buttons_code = f"""
<div id="band-selector-container">
    <div class="band-title-area">
        <span class="band-title">Amateur Radio Band Filter Progress</span>
        <span id="active-stat-badge" class="band-counter-badge">Total: {len(global_grid_stats)} Grids</span>
    </div>
    <div class="button-group">
        <button class="band-btn total-btn active" onclick="switchBand('total', '{len(global_grid_stats)} Grids')">TOTAL ({len(global_grid_stats)})</button>
"""
for band in target_bands:
    count = band_counters[band]
    buttons_code += f'<button class="band-btn" id="btn-{band}" onclick="switchBand(\'{band}\', \'{count} Grids\')">{band.upper()} ({count})</button>\n'
buttons_code += "</div></div>"

macro_element = Element(f"""
<style>
    #band-selector-container {{
        position: absolute;
        top: 15px;
        left: 50px;
        z-index: 9999;
        background: rgba(255, 255, 255, 0.95);
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        display: flex;
        flex-direction: column;
        gap: 8px;
    }}
    .band-title-area {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #ddd;
        padding-bottom: 5px;
    }}
    .band-title {{ font-weight: bold; font-size: 14px; color: #222; }}
    .band-counter-badge {{
        background: #1b5e20; color: white; padding: 2px 8px; 
        border-radius: 12px; font-size: 12px; font-weight: bold;
    }}
    .button-group {{ display: flex; gap: 4px; flex-wrap: wrap; max-width: 550px; }}
    .band-btn {{
        background: #ffffff; border: 1px solid #cccccc; padding: 6px 12px;
        font-size: 12px; font-weight: 600; cursor: pointer; border-radius: 4px;
        transition: all 0.2s ease; color: #444;
    }}
    .band-btn:hover {{ background: #f0f0f0; border-color: #888; }}
    .band-btn.active {{ background: #2e7d32; color: white; border-color: #1b5e20; }}
    .band-btn.total-btn {{ background: #e8f5e9; color: #1b5e20; border-color: #c8f7dc; }}
    .band-btn.total-btn.active {{ background: #1b5e20; color: white; border-color: #0f5924; }}
</style>

{buttons_code}

<script>
    var rawGeoData = {json.dumps(geojson_data)};
    var currentBand = 'total';
    var geojsonLayer = null;
    var labelMarkersGroup = L.layerGroup();
    var mapReference = null;

    function switchBand(bandId, statText) {{
        currentBand = bandId;
        
        document.querySelectorAll('.band-btn').forEach(btn => btn.classList.remove('active'));
        if(bandId === 'total') {{
            document.querySelector('.total-btn').classList.add('active');
            document.getElementById('active-stat-badge').innerText = "Total: " + statText;
        }} else {{
            document.getElementById('btn-' + bandId).classList.add('active');
            document.getElementById('active-stat-badge').innerText = bandId.toUpperCase() + ": " + statText;
        }}
        
        if(geojsonLayer) {{
            geojsonLayer.setStyle(defStyle);
            geojsonLayer.eachLayer(function(layer) {{
                defTooltip(layer);
            }});
        }}
        
        updateLabelsVisibility();
    }}

    function defStyle(feature) {{
        if (currentBand === 'total') {{
            return {{
                fillColor: feature.properties.total_color,
                color: feature.properties.total_bands > 6 ? "#0f5924" : "#4caf50",
                weight: 0.4,
                fillOpacity: feature.properties.total_opacity
            }};
        }} else {{
            var workedKey = currentBand + "_worked";
            var isWorked = feature.properties[workedKey];
            if (isWorked) {{
                return {{
                    fillColor: "#90ee90",
                    color: "#1b5e20",
                    weight: 0.4,
                    fillOpacity: 0.6
                }};
            }} else {{
                return {{
                    fillColor: "transparent",
                    color: "transparent",
                    weight: 0,
                    fillOpacity: 0
                }};
            }}
        }}
    }}

    function defTooltip(layer) {{
        var props = layer.feature.properties;
        var html = "<div style='font-family: sans-serif; max-height: none; overflow-y: visible; min-width: 190px; font-size: 12px;'>";
        html += "<b style='font-size: 14px;'>Grid: " + props.grid + "</b><br>";
        
        if (currentBand === 'total') {{
            html += "Bands Worked: <b style='color: #0f5924;'>" + props.total_bands + " / 10</b><br>";
            html += "<span style='font-size: 10px; color: #555;'>(" + props.bands_list + ")</span><br>";
            html += "Unique Stations: <b>" + props.total_stations + "</b><br>";
            html += "<hr style='margin:6px 0;'>";
            html += "<b style='font-size: 11px; color: #222;'>Station List:</b><br>";
            html += "<span style='font-size: 10px; color: #444;'>" + props.all_stations_html + "</span>";
        }} else {{
            var countKey = currentBand + "_stations_count";
            var htmlKey = currentBand + "_stations_html";
            html += "Band: <b style='color: #0f5924;'>" + currentBand.toUpperCase() + "</b><br>";
            html += "Stations on this band: <b>" + props[countKey] + "</b>";
            html += "<hr style='margin:6px 0;'>";
            html += "<b style='font-size: 11px; color: #222;'>Station List (" + currentBand.toUpperCase() + "):</b><br>";
            html += "<span style='font-size: 10px; color: #444;'>" + props[htmlKey] + "</span>";
        }}
        html += "</div>";
        layer.bindTooltip(html, {{sticky: true}});
    }}

    function updateLabelsVisibility() {{
        labelMarkersGroup.clearLayers();
        if (!mapReference) return;
        
        geojsonLayer.eachLayer(function(layer) {{
            var props = layer.feature.properties;
            var showIt = false;
            
            if (currentBand === 'total') {{
                showIt = true;
            }} else {{
                showIt = props[currentBand + "_worked"] === true;
            }}
            
            if (showIt) {{
                var center = layer.getBounds().getCenter();
                var gridIcon = L.divIcon({{
                    className: 'grid-label-icon',
                    html: "<div style='font-size: 9px; font-weight: bold; color: #053010; text-align: center; text-shadow: 1px 1px 0px #fff; pointer-events: none;'>" + props.grid + "</div>",
                    iconSize: [50, 20],
                    iconAnchor: [25, 10]
                }});
                var labelMarker = L.marker(center, {{icon: gridIcon, interactive: false}});
                labelMarkersGroup.addLayer(labelMarker);
            }}
        }});
    }}

    setTimeout(function() {{
        var mapVarName = Object.keys(window).find(key => key.startsWith('map_'));
        if(mapVarName) {{
            mapReference = window[mapVarName];
            
            geojsonLayer = L.geoJson(rawGeoData, {{
                style: defStyle,
                onEachFeature: function(feature, layer) {{
                    defTooltip(layer);
                }}
            }});
            
            geojsonLayer.addTo(mapReference);
            labelMarkersGroup.addTo(mapReference);
            updateLabelsVisibility();
        }}
    }}, 200);
</script>
""")

m.get_root().html.add_child(macro_element)
LayerControl(collapsed=False).add_to(m)

output_html = "world_total_heatmap.html"
m.save(output_html)
print(f"\nSuccessfully generated map: {output_html}")