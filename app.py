from flask import Flask, request, render_template_string, send_file
import os
import requests
import math
import geopandas as gpd
import urllib.request
import rasterio
import rasterio.merge
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def home():
    return '''
        <h1>Flood Raster Downloader</h1>
        <form action="/process" method="get">
            ISO Code (e.g., KEN): <input name="iso" required><br>
            Return Period (e.g., 10): <input name="rp" type="number" required><br>
            <input type="submit" value="Generate and Download">
        </form>
    '''

@app.route('/process')
def process():
    iso = request.args.get('iso').upper()
    rp = request.args.get('rp', type=int)

    if not iso or not rp:
        return "Missing ISO code or return period.", 400

    # --- Get geometry from UNHCR API ---
    geometry_url = "https://gis.unhcr.org/arcgis/rest/services/core_v2/wrl_polbnd_adm1_a_unhcr/MapServer/0/query"
    params = {
        "where": f"iso3 = '{iso}'",
        "outFields": "*",
        "outSR": "4326",
        "f": "geojson"
    }
    response = requests.get(geometry_url, params=params)
    if response.status_code != 200:
        return f"Failed to fetch geometry for {iso}", 500

    data = response.json()
    if "features" not in data or not data["features"]:
        return f"No features found for {iso}", 404

    gdf = gpd.GeoDataFrame.from_features(data["features"])
    bounds = gdf.total_bounds  # [left, bottom, right, top]

    # --- Determine tiles to download ---
    top = math.ceil(bounds[3] / 10) * 10
    left = (int(bounds[0]) // 10) * 10
    right = math.ceil(bounds[2] / 10) * 10
    bottom = (int(bounds[1]) // 10) * 10

    url_base = f"https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/CEMS-GLOFAS/flood_hazard/RP{rp}/"
    page = requests.get(url_base)
    soup = BeautifulSoup(page.text, "html.parser")
    all_links = [a['href'] for a in soup.find_all('a') if a['href'].endswith('.tif')]

    tif_paths = []
    col = left
    while col < right:
        row = top
        while row > bottom:
            prefix = f"{'N' if row >= 0 else 'S'}{abs(row)}_{'E' if col >= 0 else 'W'}{abs(col)}"
            match = [l for l in all_links if prefix in l]
            if match:
                tif_paths.append(match[0])
            row -= 10
        col += 10

    # --- Download and merge ---
    local_paths = []
    for tif in tif_paths:
        remote = url_base + tif
        local = f"/tmp/{tif}"
        urllib.request.urlretrieve(remote, local)
        local_paths.append(local)

    sources = [rasterio.open(p) for p in local_paths]
    mosaic, transform = rasterio.merge.merge(sources)

    out_meta = sources[0].meta.copy()
    out_meta.update({
        "driver": "GTiff",
        "height": mosaic.shape[1],
        "width": mosaic.shape[2],
        "transform": transform
    })

    output_path = f"/tmp/merged_raster_{iso}_{rp}.tif"
    with rasterio.open(output_path, "w", **out_meta) as dest:
        dest.write(mosaic)

    for src in sources:
        src.close()
    for f in local_paths:
        os.remove(f)

    return render_template_string(f"""
        <h2>Raster generated for {iso}, RP {rp}</h2>
        <a href="/download?iso={iso}&rp={rp}">
            <button>Download TIFF</button>
        </a>
    """)

@app.route('/download')
def download():
    iso = request.args.get('iso').upper()
    rp = request.args.get('rp', type=int)
    output_path = f"/tmp/merged_raster_{iso}_{rp}.tif"

    if not os.path.exists(output_path):
        return "File not found. Please re-run the process.", 404

    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)