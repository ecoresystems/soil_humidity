import configparser

import requests


def get_ADC_value():
    # TODO: Acquire ADC value here
    return "Test metric", 2.048


def send_update():
    config = configparser.ConfigParser()
    config.read('config.ini')
    url = config['DEFAULT']['StatusUpdateEndPoint']
    device_serial = config['DEFAULT']['DeviceSerial']
    authorization_token = config['DEFAULT']['AuthorizationToken']
    metric_name, metric_value = get_ADC_value()
    request_data = {
        "metric_name": metric_name,
        "metric_value": metric_value,
        "device_serial": device_serial,
        "authorization_token": authorization_token,
    }
    response = requests.post(url, json=request_data)
    print(response.json())


if __name__ == "__main__":
    send_update()
