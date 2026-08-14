# Ham Radio Grid Progress Map

[![Python](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python-based utility that transforms your Amateur Radio ADIF log files into an interactive, filterable world map. Visualize your progress across different bands, see which grid squares you've worked, and explore station statistics with ease.

## Key Features

*   **Interactive Visualization**: Uses `Folium` and `Leaflet.js` to render a responsive world map.
*   **Band Filtering**: Toggle between 160m and 6m bands (and everything in between) using a clean, modern UI.
*   **Dynamic Stats**: Hover over any grid square to see:
    *   The total number of bands worked for that grid.
    *   A complete list of callsigns worked in that grid.
    *   Band-specific station counts.
*   **Heatmap Styling**: Grid squares are color-coded based on your progress (intensity of bands worked).
*   **Customizable**: Easily adapt the home location and target bands.

## Prerequisites

Before running the script, ensure you have Python 3 installed. You will need the following libraries:

```bash
pip install folium adif_io
