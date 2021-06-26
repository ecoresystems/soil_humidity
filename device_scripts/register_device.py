import argparse
import configparser
import requests
import getpass


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    url = config['DEFAULT']['RegistrationEndPoint']
    parser = argparse.ArgumentParser()
    parser.add_argument("device_location")
    parser.add_argument("description")
    args = parser.parse_args()
    device_location = args.device_location
    description = args.description
    user_name = input("User Name:")
    password = getpass.getpass()
    device_serial, device_model = get_device_info()
    request_data = {
        "user_name": user_name,
        "password": password,
        "device_location": device_location,
        "description": description,
        "device_serial": device_serial,
        "device_model": device_model,
    }
    response = requests.post(url, json=request_data)
    authorization_token = response.json()['authorization_token']
    config['DEFAULT']['DeviceLocation'] = device_location
    config['DEFAULT']['Description'] = description
    config['DEFAULT']['DeviceSerial'] = device_serial
    config['DEFAULT']['DeviceModel'] = device_model
    config['DEFAULT']['AuthorizationToken'] = authorization_token
    with open('config.ini', 'w') as configfile:
        config.write(configfile)


def get_device_info():
    with open("/proc/cpuinfo", "r") as sys_info_file:
        sys_info = sys_info_file.readlines()
        device_serial = sys_info[-2].split(": ")[1].strip()
        device_model = sys_info[-1].split(": ")[1].strip()
    return device_serial, device_model


if __name__ == "__main__":
    main()
