# Ham Radio Grid Progress Map

A Python-based utility that transforms your Amateur Radio ADIF log files into an interactive, filterable world map. Visualize your progress across different bands, see which grid squares you've worked, and explore station statistics with ease.

## Key Features

* **Interactive Visualization**: Uses `Folium` and `Leaflet.js` to render a responsive world map.
* **Band Filtering**: Toggle between 160m and 6m bands using a clean, modern UI.
* **Dynamic Stats**: Hover over any grid square to see station lists and band-specific counts.
* **Heatmap Styling**: Color-coded progress based on the number of bands worked.

## Prerequisites

Before running the script, ensure you have Python 3 installed. Install the required libraries by running the following command in your terminal:

```bash
pip install folium adif_io
