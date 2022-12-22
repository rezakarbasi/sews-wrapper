import pandas as pd
import rasterio as rio
from rasterio.transform import Affine
import json
import random
from client import PishgamanClient

client = PishgamanClient()


def create_radar(radar_params):
    response = client.post('/api/RadarSNR/SetData', data=radar_params)
    radar_id = response.text
    return radar_id


def get_radar_analyses(radar_id, analyses_params):
    url = f'/api/RadarSNR/RadarSNRAnalysis?id={radar_id}'
    response = client.post( url, data=analyses_params)
    return json.loads(response.body)


def create_tiff(radar_analyses, min_latitude, radar_index):
    min_snr = -100
    snr_df = pd.DataFrame.from_records(radar_analyses)
    snr_df = pd.DataFrame(snr_df.to_numpy().reshape(-1))
    df = pd.DataFrame.from_records(snr_df.explode(0).to_numpy().reshape(-1))
    df = df.replace("-Infinity", min_snr)

    df_h1 = df[df['Z'] == min_latitude]

    snr_grid = df_h1['SNR'].to_numpy().reshape(df_h1['X'].unique().shape[0], df_h1['Y'].unique().shape[0])


    x_min, x_max = df_h1['X'].min(), df_h1['X'].max()
    y_min, y_max = df_h1['Y'].min(), df_h1['Y'].max()
    x_size, y_size = snr_grid.shape

    x_res = (x_max - x_min) / x_size
    y_res = (y_max - y_min) / y_size
    transform = Affine.translation(x_min - x_res / 2, y_max - y_res / 2) * Affine.scale(x_res, y_res)

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
