import configparser

import adafruit_ads1x15.ads1115 as ADS
import board
import busio
import requests
from adafruit_ads1x15.analog_in import AnalogIn


def channels(channel: int):
    return {
        0: ADS.P0,
        1: ADS.P1,
        2: ADS.P2,
        3: ADS.P3,
    }[channel]


def get_ADC_value(channel: int = 0):
    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1115(i2c)
    return f"Voltage/CH{channel}", AnalogIn(ads, channels(channel)).voltage


def send_update(channel: int = 0):
    config = configparser.ConfigParser()
    config.read('config.ini')
    url = config['DEFAULT']['StatusUpdateEndPoint']
    device_serial = config['DEFAULT']['DeviceSerial']
    authorization_token = config['DEFAULT']['AuthorizationToken']
    metric_name, metric_value = get_ADC_value(channel)
    request_data = {
        "metric_name": metric_name,
        "metric_value": metric_value,
        "device_serial": device_serial,
        "authorization_token": authorization_token,
    }
    response = requests.post(url, json=request_data)
    print(response.json())


if __name__ == "__main__":
    active_channels = [0, 1]
    for query_channel in active_channels:
        send_update(query_channel)
