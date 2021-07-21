import base64
import requests
import hashlib
import os


def send_image():
    url = "http://localhost:5000/api/upload_image"
    for current_dir, sub_dir, files in os.walk('images'):
        for file in files:
            if file.endswith('.jpg'):
                with open(os.path.join(current_dir, file), 'rb') as image_file:
                    encoded_string = base64.b64encode(image_file.read())
                    md5_value = hashlib.md5(encoded_string)
                    request_data = {
                        "image_str": encoded_string.decode('utf-8'),
                        "description": file.split('.jpg')[0],
                        "md5_hash": md5_value.hexdigest(),
                    }
                    response = requests.post(url, json=request_data)
                    print(response.json())


if __name__ == "__main__":
    send_image()
