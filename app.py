from flask import Flask, request, send_from_directory
import json
from snr_analyze import *


# implement login settings in static mode
# add direct point snr


app = Flask(__name__)


@app.route("/api", methods=["POST"])
def api_snr():
    radar_id = request.args.get('id')
    data = dict(request.form)
    return data
    # with open('0-5m-above_the_ground.json', 'r') as f:
    #     json_file = json.load(f)
    # return json_file


@app.route("/analyze", methods=["POST"])
def geotiff_provider():
    geotiff_response = []
    radars = json.loads(request.data)
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
        radar_params = {
            "Power":40000,
            "Frequency":3000000000,
            "Bandwidth":1000000,
            "ReceiverGain":45,
            "ReceiverLoss":0,
            "TransmitterLoss":0,
            "NoiseFigure":3,
            "IntegratedPulseNumber":20,
            "Polarization":0,
            "ProcessingGain":40,
            "PRF":1000,
            "NormalRange":150000,
            "RFTemp":320,
            "RFLoss":0,
            "TotalCell":1000,
            "Gpc":0,
            "ReceiverType":0,
            "Amplitude":0,
            "VxScaleFactor":1,
            "VyScaleFactor":1,
            "Cfar":"true",
            "CfarType":0,
            "M":20,
            "Ng":0,
            "PFalseAlarm":"0.00001",
            "CFAROrder":1,
            "Threshold":0.00037
        }
        radar_id = create_radar(radar_params)

        analyses_params = {
            'HorizontalStep': 1000,
            'VerticalStep': 1000,
            'RadarPosition_x': 57.1 or radar['lng'],
            'RadarPosition_y': 26.4 or radar['lat'],
            'RadarPosition_z': 3 or 2500,
        }

        analyses_params['MinimumLat'] = 26.2 or analyses_params['RadarPosition_y'] - 2
        analyses_params['MaximumLat'] = 26.6 or analyses_params['RadarPosition_y'] + 2
        analyses_params['MinimumLong'] = 56.6 or analyses_params['RadarPosition_x'] - 2
        analyses_params['MaximumLong'] = 57 or analyses_params['RadarPosition_x'] + 2
        analyses_params['MinimumHeight'] = 5000 or analyses_params['RadarPosition_z'] + 500
        analyses_params['MaximumHeight'] = 6000 or analyses_params['RadarPosition_z'] + 500

        analyses_params = {
            "MinimumLat": 26.2,
            "MaximumLat":26.6,
            "MinimumLong":56.6,
            "MaximumLong":57,
            "MinimumHeight":5000,
            "MaximumHeight":6000,
            "HorizontalStep":1000,
            "VerticalStep":1000,
            "RadarPosition_x":57.1,
            "RadarPosition_y":26.4,
            "RadarPosition_z":3,
        }
        
        radar_index = radar['radarIndex']

        radar_analyses = get_radar_analyses(radar_id, analyses_params)
        print(radar_analyses)
        tiff_path = create_tiff(radar_analyses, analyses_params['MinimumHeight'], radar_index)
        geotiff_response.append({
            "radar_index": radar_index,
            "path": tiff_path

        })

    return geotiff_response

@app.route('/static/tiff/<file>')
def serve_file(file):
    print(file)
    # return []
    return send_from_directory("tiff", file)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
