import argparse
import configparser
import requests
import getpass


def main():
    url = "http://kyushu-aws.ecoresystems.cn/api/register_device"
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
    response = requests.post(url, data=request_data)
    print(response)


def get_device_info():
    with open("/proc/cpuinfo", "r") as sys_info_file:
        sys_info = sys_info_file.readlines()
        device_serial = sys_info[-2].split(": ")[1].strip()
        device_model = sys_info[-1].split(": ")[1].strip()
    return device_serial, device_model


if __name__ == "__main__":
    main()
