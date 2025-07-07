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
    return render_template_string("""
    <!doctype html>
    <html lang="en">
      <head>
        <title>Flood Raster Downloader</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
      </head>
      <body class="bg-light">
        <div class="container mt-5">
          <div class="card shadow p-4">
            <h1 class="mb-4 text-primary">Flood Raster Downloader</h1>
            <form action="/process" method="get" onsubmit="showLoading()">
              <div class="mb-3">
                <label for="iso" class="form-label">Select Country:</label>
                <select class="form-select" name="iso" id="iso" required>
                  <option value="">Choose a country</option>
                  <option value="AFG">Afghanistan</option>
                  <option value="ALB">Albania</option>
                  <option value="DZA">Algeria</option>
                  <option value="AND">Andorra</option>
                  <option value="AGO">Angola</option>
                  <option value="ARG">Argentina</option>
                  <option value="ARM">Armenia</option>
                  <option value="AUS">Australia</option>
                  <option value="AUT">Austria</option>
                  <option value="AZE">Azerbaijan</option>
                  <option value="BDI">Burundi</option>
                  <option value="BEL">Belgium</option>
                  <option value="BEN">Benin</option>
                  <option value="BFA">Burkina Faso</option>
                  <option value="BGD">Bangladesh</option>
                  <option value="BGR">Bulgaria</option>
                  <option value="BOL">Bolivia</option>
                  <option value="BRA">Brazil</option>
                  <option value="BTN">Bhutan</option>
                  <option value="BWA">Botswana</option>
                  <option value="CAF">Central African Republic</option>
                  <option value="CAN">Canada</option>
                  <option value="CHE">Switzerland</option>
                  <option value="CHL">Chile</option>
                  <option value="CHN">China</option>
                  <option value="CIV">Côte d'Ivoire</option>
                  <option value="CMR">Cameroon</option>
                  <option value="COG">Congo</option>
                  <option value="COL">Colombia</option>
                  <option value="COD">Democratic Republic of the Congo</option>
                  <option value="CRI">Costa Rica</option>
                  <option value="CUB">Cuba</option>
                  <option value="CYP">Cyprus</option>
                  <option value="CZE">Czech Republic</option>
                  <option value="DEU">Germany</option>
                  <option value="DJI">Djibouti</option>
                  <option value="DNK">Denmark</option>
                  <option value="DOM">Dominican Republic</option>
                  <option value="DZA">Algeria</option>
                  <option value="ECU">Ecuador</option>
                  <option value="EGY">Egypt</option>
                  <option value="ERI">Eritrea</option>
                  <option value="ESP">Spain</option>
                  <option value="EST">Estonia</option>
                  <option value="ETH">Ethiopia</option>
                  <option value="FIN">Finland</option>
                  <option value="FJI">Fiji</option>
                  <option value="FRA">France</option>
                  <option value="GAB">Gabon</option>
                  <option value="GBR">United Kingdom</option>
                  <option value="GEO">Georgia</option>
                  <option value="GHA">Ghana</option>
                  <option value="GIN">Guinea</option>
                  <option value="GMB">Gambia</option>
                  <option value="GNB">Guinea-Bissau</option>
                  <option value="GRC">Greece</option>
                  <option value="GTM">Guatemala</option>
                  <option value="GUY">Guyana</option>
                  <option value="HND">Honduras</option>
                  <option value="HRV">Croatia</option>
                  <option value="HTI">Haiti</option>
                  <option value="HUN">Hungary</option>
                  <option value="IDN">Indonesia</option>
                  <option value="IND">India</option>
                  <option value="IRL">Ireland</option>
                  <option value="IRN">Iran</option>
                  <option value="IRQ">Iraq</option>
                  <option value="ISL">Iceland</option>
                  <option value="ISR">Israel</option>
                  <option value="ITA">Italy</option>
                  <option value="JAM">Jamaica</option>
                  <option value="JOR">Jordan</option>
                  <option value="JPN">Japan</option>
                  <option value="KAZ">Kazakhstan</option>
                  <option value="KEN">Kenya</option>
                  <option value="KGZ">Kyrgyzstan</option>
                  <option value="KHM">Cambodia</option>
                  <option value="KOR">South Korea</option>
                  <option value="KWT">Kuwait</option>
                  <option value="LAO">Laos</option>
                  <option value="LBN">Lebanon</option>
                  <option value="LBR">Liberia</option>
                  <option value="LBY">Libya</option>
                  <option value="LKA">Sri Lanka</option>
                  <option value="LSO">Lesotho</option>
                  <option value="LTU">Lithuania</option>
                  <option value="LUX">Luxembourg</option>
                  <option value="LVA">Latvia</option>
                  <option value="MAR">Morocco</option>
                  <option value="MDA">Moldova</option>
                  <option value="MDG">Madagascar</option>
                  <option value="MEX">Mexico</option>
                  <option value="MKD">North Macedonia</option>
                  <option value="MLI">Mali</option>
                  <option value="MMR">Myanmar</option>
                  <option value="MNG">Mongolia</option>
                  <option value="MOZ">Mozambique</option>
                  <option value="MRT">Mauritania</option>
                  <option value="MUS">Mauritius</option>
                  <option value="MWI">Malawi</option>
                  <option value="MYS">Malaysia</option>
                  <option value="NAM">Namibia</option>
                  <option value="NCL">New Caledonia</option>
                  <option value="NER">Niger</option>
                  <option value="NGA">Nigeria</option>
                  <option value="NIC">Nicaragua</option>
                  <option value="NLD">Netherlands</option>
                  <option value="NOR">Norway</option>
                  <option value="NPL">Nepal</option>
                  <option value="NZL">New Zealand</option>
                  <option value="OMN">Oman</option>
                  <option value="PAK">Pakistan</option>
                  <option value="PAN">Panama</option>
                  <option value="PER">Peru</option>
                  <option value="PHL">Philippines</option>
                  <option value="PNG">Papua New Guinea</option>
                  <option value="POL">Poland</option>
                  <option value="PRT">Portugal</option>
                  <option value="PRY">Paraguay</option>
                  <option value="QAT">Qatar</option>
                  <option value="ROU">Romania</option>
                  <option value="RUS">Russia</option>
                  <option value="RWA">Rwanda</option>
                  <option value="SAU">Saudi Arabia</option>
                  <option value="SDN">Sudan</option>
                  <option value="SEN">Senegal</option>
                  <option value="SLB">Solomon Islands</option>
                  <option value="SLE">Sierra Leone</option>
                  <option value="SLV">El Salvador</option>
                  <option value="SOM">Somalia</option>
                  <option value="SRB">Serbia</option>
                  <option value="SUR">Suriname</option>
                  <option value="SVK">Slovakia</option>
                  <option value="SVN">Slovenia</option>
                  <option value="SWE">Sweden</option>
                  <option value="SWZ">Eswatini</option>
                  <option value="SYR">Syria</option>
                  <option value="TCD">Chad</option>
                  <option value="TGO">Togo</option>
                  <option value="THA">Thailand</option>
                  <option value="TJK">Tajikistan</option>
                  <option value="TKM">Turkmenistan</option>
                  <option value="TLS">Timor-Leste</option>
                  <option value="TTO">Trinidad and Tobago</option>
                  <option value="TUN">Tunisia</option>
                  <option value="TUR">Turkey</option>
                  <option value="TZA">Tanzania</option>
                  <option value="UGA">Uganda</option>
                  <option value="UKR">Ukraine</option>
                  <option value="URY">Uruguay</option>
                  <option value="USA">United States</option>
                  <option value="UZB">Uzbekistan</option>
                  <option value="VEN">Venezuela</option>
                  <option value="VNM">Vietnam</option>
                  <option value="YEM">Yemen</option>
                  <option value="ZAF">South Africa</option>
                  <option value="ZMB">Zambia</option>
                  <option value="ZWE">Zimbabwe</option>
                </select>
              </div>
              <div class="mb-3">
                <label for="rp" class="form-label">Return Period:</label>
                <select class="form-select" name="rp" id="rp" required>
                  <option value="10">10 years</option>
                  <option value="20">20 years</option>
                  <option value="50">50 years</option>
                  <option value="75">75 years</option>
                  <option value="100">100 years</option>
                  <option value="200">200 years</option>
                  <option value="500">500 years</option>
                </select>
              </div>
              <button type="submit" class="btn btn-primary">Generate and Download</button>
            </form>

            <div id="loading" class="mt-4" style="display:none;">
              <div class="alert alert-info">
                <strong>Processing your request...</strong><br>
                This may take a few minutes. Please don’t refresh the page.
              </div>
            </div>

            <script>
              function showLoading() {
                document.getElementById("loading").style.display = "block";
              }
            </script>

          </div>
        </div>
      </body>
    </html>
    """)

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
    <!doctype html>
    <html lang="en">
      <head>
        <title>Flood Raster Generated</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
      </head>
      <body class="bg-light">
        <div class="container mt-5">
          <div class="card shadow p-4 text-center">
            <h2 class="text-success mb-4">Raster successfully generated</h2>
            <p class="fs-5">Country: <strong>{iso}</strong></p>
            <p class="fs-5">Return Period: <strong>{rp}</strong></p>
            <a href="/download?iso={iso}&rp={rp}" class="btn btn-primary btn-lg mt-3">
              Download TIFF
            </a>
          </div>
        </div>
      </body>
    </html>
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