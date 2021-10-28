from flask import Flask, redirect, url_for, render_template, request, flash, jsonify
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
import glob, rasterio
import numpy as np
import json, os, gc

USERNAME = 'jsdigisat'
PASSWORD = 'jsdigisat@space'
API_URL = 'https://scihub.copernicus.eu/dhus/'
PLATFORM_NAME = 'Sentinel-2'
PROCESSING_LEVEL = 'Level-1C'
FROM_DATE = '20201201'
TO_DATE = 'NOW'

app = Flask(__name__)
api = SentinelAPI(USERNAME, PASSWORD, API_URL)

@app.route('/')
def hello():
    return render_template('digisat.html')

@app.route('/render')
def render():
    return render_template('render.html')

@app.route('/download', methods=['POST'])
def download():
    try:
        aoi = request.json['coords']['value']

        footprint = geojson_to_wkt(aoi)
        products = api.query(footprint, date=(FROM_DATE,TO_DATE), platformname=PLATFORM_NAME, cloudcoverpercentage=(0, 2), processinglevel=PROCESSING_LEVEL)
        products_df = api.to_dataframe(products)
        
        if products_df.shape[0] > 0:
            api.download_all(products_df.iloc[[3]].index)
            return str(products_df.iloc[3].title)
        else:
            return "0"
    except:
        return "0"
    
@app.route('/resolve', methods=['POST'])
def resolve():

    try:
        tile = request.json['path']['value']
        tiles_render = []
        os.system('unzip ~/digisat/'+tile)

        files = glob.glob('/home/ubuntu/digisat/**/*.jp2', recursive = True)
        for file in files:
            if 'B01' in file or 'B05' in file or 'B12' in file:
                os.system('gdal_translate -of GTiff '+file+' ./'+file.split('.')[1].split('/')[-1]+'.tif')
                tiles_render.append(file.split('.')[1].split('/')[-1]+'.tif')

        os.system('gdalbuildvrt -separate stacked.vrt '+tiles_render[0]+' '+tiles_render[1]+' '+tiles_render[2])
        os.system('gdal_translate -ot UInt16 -of GTiff stacked.vrt stacked_original.tif')
        os.system('docker run --rm -v /home/ubuntu/digisat/:/home osgeo/gdal:alpine-small-latest gdal_translate /home/stacked_original.tif /home/stacked_original_cog.tif -of COG -co COMPRESS=LZW')
        
        files = glob.glob('/home/ubuntu/digisat/'+tile+'.SAFE/MTD*.xml', recursive = True)
        for xml_file in files:
            os.system('python ~/Sentinel_2A_PS/DSen2/testing/s2_tiles_supres.py '+xml_file)

        files = glob.glob('/home/ubuntu/digisat/*superresolution.tif')
        for resolved_file in files:
            os.system("gdal_translate -of GTiff -b 7 -b 1 -b 6 "+resolved_file+" stacked_enhanced.tif")

        os.system('docker run --rm -v /home/ubuntu/digisat/:/home osgeo/gdal:alpine-small-latest gdal_translate /home/stacked_enhanced.tif /home/stacked_enhanced_cog.tif -of COG -co COMPRESS=LZW')

        enhanced_raster = rasterio.open('/home/ubuntu/digisat/stacked_enhanced.tif').read()
        print(enhanced_raster.max(), type(enhanced_raster.max()))

        if enhanced_raster.max() == 0 or enhanced_raster.max() == np.nan:
            os.system('rm -rf /home/ubuntu/digisat/'+tile+'* *.tif *.vrt *.xml')
            return "False"
        else:
            del enhanced_raster
            gc.collect()
            os.system('aws s3 cp /home/ubuntu/digisat/stacked_enhanced_cog.tif s3://crossregionreplpuri/digisat/')
            os.system('aws s3 cp /home/ubuntu/digisat/stacked_original_cog.tif s3://crossregionreplpuri/digisat/')
            os.system('rm -rf /home/ubuntu/digisat/'+tile+'* *.tif *.vrt *.xml')
            return "True"
    except:
        os.system('rm -rf /home/ubuntu/digisat/'+tile+'* *.tif *.vrt *.xml')
        return "False"

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=5000)
 