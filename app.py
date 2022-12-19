from urllib import response
import pandas as pd
import rasterio as rio
from rasterio.transform import Affine
from flask import Flask, send_file, request
from flask_cors import CORS, cross_origin
import json
from snr_analyze import *



app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route("/api", methods=["POST"])
# @cross_origin()
def api_snr():
    radar_id = request.args.get('id')
    data = dict(request.form)
    return data
    with open('0-5m-above_the_ground.json', 'r') as f:
        json_file = json.load(f)
    return json_file


@app.route("/analyze", methods=["POST"])
@cross_origin()
def geotiff_provider():
    geotiff_response = {}
    # print(request.data)
    radars = json.loads(request.data)
    access_token = get_access_token()
    time.sleep(10)
    print(access_token)
    for radar in radars:
        cfar = 'true' if radar['cfar'] == 1 else 'false'
        radar_params = {
            'Power': radar['power'],
            'Frequency': radar['frequency'],
            'Bandwidth': radar['bandwidth'],
            'ReceiverGain': radar['receiver_gain'],
            'ReceiverLoss': radar['receiver_loss'],
            'TransmitterLoss': radar['transmitter_loss'],
            'NoiseFigure': radar['noise_figure'],
            'IntegratedPulseNumber': radar['integrated_pulse_number'],
            'Polarization': radar['polarization'],
            'ProcessingGain': radar['processing_gain'],
            'PRF': radar['prf'],
            'NormalRange': radar['normal_range'],
            'RFTemp': radar['rf_temp'],
            'RFLoss': radar['rf_loss'],
            'TotalCell': radar['total_cell'],
            'Gpc': radar['gpc'],
            'ReceiverType': radar['receiver_type'],
            'Amplitude': radar['amplitude'],
            'VxScaleFactor': radar['vx_scale_factor'],
            'VyScaleFactor': radar['vy_scale_factor'],
            'Cfar': cfar,
            'CfarType': radar['cfar_type'],
            'M': radar['m'],
            'Ng': radar['ng'],
            'PFalseAlarm': radar['p_false_alarm'],
            'CFAROrder': radar['cfar_order'],
            'Threshold': radar['threshold'],
        }
        radar_id = create_radar(radar_params)
        time.sleep(5)

        analyses_params = {
            'HorizontalStep': 10_000,
            'VerticalStep': 500,
            'RadarPosition_x': radar['lng'],
            'RadarPosition_y': radar['lat'],
            'RadarPosition_z': 2500,
        }

        analyses_params['MinimumLat'] = analyses_params['RadarPosition_y'] - 2
        analyses_params['MaximumLat'] = analyses_params['RadarPosition_y'] + 2
        analyses_params['MinimumLong'] = analyses_params['RadarPosition_x'] - 2
        analyses_params['MaximumLong'] = analyses_params['RadarPosition_x'] + 2
        analyses_params['MinimumHeight'] = analyses_params['RadarPosition_z'] + 500
        analyses_params['MaximumHeight'] = analyses_params['RadarPosition_z'] + 500
        
        radar_index = radar['radarIndex']

        radar_analyses = get_radar_analyses(radar_id, analyses_params)
        print(radar_analyses)
        tiff_path = create_tiff(radar_analyses, analyses_params['MinimumHeight'], radar_index)
        geotiff_response[radar_index] = tiff_path
        print(tiff_path)

    return geotiff_response
    snr_df = pd.read_json('0-5m-above_the_ground.json')
    snr_df = pd.DataFrame(snr_df.to_numpy().reshape(-1))
    df = pd.DataFrame.from_records(snr_df.explode(0).to_numpy().reshape(-1))
    df = df.replace("-Infinity", df['SNR'].min() * 1.2)
    df_h1 = df[df['Z'] == 883.0]
    # df_h2 = df[df['Z'] == 888.0]

    grid = df_h1['SNR'].to_numpy().reshape(df_h1['X'].unique().shape[0], df_h1['Y'].unique().shape[0])


    x_min, x_max = df_h1['X'].min(), df_h1['X'].max()
    y_min, y_max = df_h1['Y'].min(), df_h1['Y'].max()
    x_size, y_size = grid.shape

    x_res = (x_max - x_min) / x_size
    y_res = (y_max - y_min) / y_size
    transform = Affine.translation(x_min - x_res / 2, y_min - y_res / 2) * Affine.scale(x_res, y_res)
    # print(transform)

    new_dataset = rio.open(
        './tiff/snr-0-5m.tif',
        'w',
        driver='GTiff',
        height=grid.shape[0],
        width=grid.shape[1],
        count=2,
        dtype=grid.dtype,
        crs='+proj=latlong',
        transform=transform,
    )

    new_dataset.write(grid, 1)
    new_dataset.close()
    return send_file('./tiff/snr-0-5m.tif')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)