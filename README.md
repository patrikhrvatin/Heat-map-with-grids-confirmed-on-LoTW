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
Quick Setup (Must-Do)

To make the script work with your specific logbook data, you must perform these two steps:

    Add Your Log File: Export your logbook file (from LoTW, QRZ, or N1MM) as an .adi file. Place it in the same folder as the script and rename it to lotwreport.adi.

    Update Your Locator: Open your Python script, find the MY_HOME_GRID variable, and change it to your actual grid square:
    Python

MY_HOME_GRID = "YOUR_GRID_HERE"  # e.g., "JN65XF"
Usage

    Run the script:
    Bash

    python map_generator.py

    View Results: Open the generated world_total_heatmap.html file in any web browser.

Customization

    Target Bands: You can modify the target_bands list in the script to include or exclude specific bands.

    Visuals: Colors and UI styles are fully customizable within the macro_element variable inside the script.

Troubleshooting

    Script fails to start: Ensure your log file is named exactly lotwreport.adi and that MY_HOME_GRID contains a valid 6-character locator.

    Missing Labels: The script uses a setTimeout to ensure the map loads correctly; if labels don't appear, refresh the browser page.

License

This project is licensed under the MIT License.
