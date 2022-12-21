import pandas as pd
import rasterio as rio
from rasterio.transform import Affine
import json
import requests
import random
import urllib.parse
with open('./0-5m-above_the_ground.json') as json_file: tiff_test = json.load(json_file)

base_url = 'http://127.0.0.1:8080'
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
}

def get_access_token(username='war', password='1'):
    url = f'{base_url}/token'
    payload = urllib.parse.urlencode({
        'username': username,
        'password': password,
        'grant_type': 'password',
    })
    response = requests.request('POST', url, headers=headers, data=payload)
    json_response = json.loads(response.text)
    access_token = json_response['access_token']
    headers['Authorization'] = f'Bearer {access_token}'
    return access_token


def create_radar(radar_params):
    url = f'{base_url}/api/RadarSNR/SetData'
    payload = urllib.parse.urlencode(radar_params)
    response = requests.request('POST', url, headers=headers, data=payload)
    radar_id = response.text
    return radar_id


# def get_radar_analyses(radar_id, analyses_params):
def get_radar_analyses():
    # url = f'{base_url}/api/RadarSNR/RadarSNRAnalysis?id={radar_id}'
    # payload = urllib.parse.urlencode(analyses_params)
    # response = requests.request('POST', url, headers=headers, data=payload)
    return tiff_test


def create_tiff(radar_analyses, min_latitude, radar_index):
    min_snr = -100
    snr_df = pd.DataFrame.from_records(radar_analyses)
    snr_df = pd.DataFrame(snr_df.to_numpy().reshape(-1))
    df = pd.DataFrame.from_records(snr_df.explode(0).to_numpy().reshape(-1))
    df = df.replace("-Infinity", min_snr)
    
    # df.to_json('json/.json', orient='records')

    df_h1 = df[df['Z'] == min_latitude]

    snr_grid = df_h1['SNR'].to_numpy().reshape(df_h1['X'].unique().shape[0], df_h1['Y'].unique().shape[0])


    x_min, x_max = df_h1['X'].min(), df_h1['X'].max()
    y_min, y_max = df_h1['Y'].min(), df_h1['Y'].max()
    x_size, y_size = snr_grid.shape

    # x_res = (x_max - x_min) / x_size
    x_res = (x_max - x_min) / random.randint(1, 1000)
    # y_res = (y_max - y_min) / y_size
    y_res = (y_max - y_min) / random.randint(1, 1000)
    transform = Affine.translation(x_min - x_res / 2, y_max - y_res / 2) * Affine.scale(x_res, y_res)
    # print(transform)

    tiff_path = f'./tiff/snr-radar{radar_index}.tif'

    new_dataset = rio.open(
        tiff_path,
        'w',
        driver='GTiff',
        height=snr_grid.shape[0],
        width=snr_grid.shape[1],
        count=2,
        dtype=snr_grid.dtype,
        crs='+proj=latlong',
        transform=transform,
    )

    new_dataset.write(snr_grid, 1)
    new_dataset.close()
    return tiff_path

# if __name__ == '__main__':
#     access_token = get_access_token(username='war', password='1')
#     # set bearer token
#     headers['Authorization'] = f'Bearer {access_token}'


#     time.sleep(10)

#     radar_params = {
#         'Power': 30_000,
#         'Frequency': 2_500_000_000,
#         'Bandwidth': 1_000_000,
#         'ReceiverGain': 45,
#         'ReceiverLoss': 0,
#         'TransmitterLoss': 0,
#         'NoiseFigure': 3,
#         'IntegratedPulseNumber': 20,
#         'Polarization': 0,
#         'ProcessingGain': 40,
#         'PRF': 1_000,
#         'NormalRange': 150_000,
#         'RFTemp': 290,
#         'RFLoss': 0,
#         'TotalCell': 1_000,
#         'Gpc': 0,
#         'ReceiverType': 0,
#         'Amplitude': 0,
#         'VxScaleFactor': 1,
#         'VyScaleFactor': 1,
#         'Cfar': 'true',
#         'CfarType': 0,
#         'M': 20,
#         'Ng': 0,
#         'PFalseAlarm': 0.000_01,
#         'CFAROrder': 1,
#         'Threshold': 0.000_37,
#     }
#     radar_id = create_radar(radar_params)

#     time.sleep(5)

#     radars = [
#         {'city': "Bushehr", 'latitude': 28.876111, 'longitude': 50.852500, 'elevation': 534},
#         {'city': "Dezful", 'latitude': 32.514167, 'longitude': 48.418611, 'elevation': 197},
#         {'city': "Mashhad", 'latitude': 36.196944, 'longitude': 59.787778, 'elevation': 1015},
#         {'city': "Karaj", 'latitude': 35.791944, 'longitude': 51.085278, 'elevation': 2522},
#         {'city': "Anarak", 'latitude': 33.089722, 'longitude': 53.424444, 'elevation': 1061},
#         {'city': "Hashem Abad", 'latitude': 32.707500, 'longitude': 52.781667, 'elevation': 2661},
#     ]
#     for radar in radars:

#         analyses_params = {
#             'HorizontalStep': 10_000,
#             'VerticalStep': 100,
#             'RadarPosition_x': radar['longitude'],
#             'RadarPosition_y': radar['latitude'],
#             'RadarPosition_z': radar['elevation'],
#         }

#         analyses_params['MinimumLat'] = analyses_params['RadarPosition_y'] - 2
#         analyses_params['MaximumLat'] = analyses_params['RadarPosition_y'] + 2
#         analyses_params['MinimumLong'] = analyses_params['RadarPosition_x'] - 2
#         analyses_params['MaximumLong'] = analyses_params['RadarPosition_x'] + 2
#         analyses_params['MinimumHeight'] = analyses_params['RadarPosition_z'] + 1200
#         analyses_params['MaximumHeight'] = analyses_params['RadarPosition_z'] + 1200
#         city = radar['city']

#         radar_analyses = get_radar_analyses(radar_id, analyses_params)
#         create_tiff(radar_analyses, analyses_params['MinimumHeight'], city)
