import configparser
import ipaddress
import secrets
import sqlite3

import mysql.connector
from flask import Flask, render_template
from flask import jsonify
from flask import request
from flask_bcrypt import Bcrypt

from queries import Queries

app = Flask(__name__)
bcrypt = Bcrypt(app)
config = configparser.ConfigParser()
config.read("config.ini")
default_config = config["DEFAULT"]
if default_config["DatabaseType"] == "MySQL":
    cnx = mysql.connector.connect(
        host=default_config["MysqlEndpoint"],
        user=default_config["DatabaseUserName"],
        password=default_config["DatabasePassword"],
        database=default_config["DatabaseName"],
    )
elif default_config["DatabaseType"] == "SQLite":
    cnx = sqlite3.connect(default_config["DatabaseName"] + ".db", check_same_thread=False)

else:
    raise ValueError

authorized_networks = ipaddress.IPv4Network(default_config["AuthorizedNetwork"])

cursor = cnx.cursor()
queries = Queries()

cursor.execute(queries.create_authorized_users_table())
cursor.execute(queries.create_devices_table())
cursor.execute(queries.create_device_status_table())
cursor.execute(queries.create_image_table())


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/ito')
def ito():
    ssh = paramiko.SSHClient()
    key = paramiko.RSAKey.from_private_key_file('/home/centos/.ssh/ito-key',password="ito-key")
    ssh.connect("52.197.196.51", username=q70209a, pkey=key)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("pjstat")
    return render_template('ito.html', status=ssh_stdout)


@app.route('/api/get_latest_status', methods=['GET'])
def get_latest_status():
    # start of test section
    result_list = []
    cursor.execute(queries.get_all_devices())
    for device in cursor.fetchall():
        device_serial = device[1]
        cursor.execute(queries.get_unique_metrics_for_device(device_serial))
        for metric in cursor.fetchall():
            metric_name = metric[0]
            cursor.execute(queries.get_latest_status(device_serial, metric_name))
            status = cursor.fetchone()
            cursor.execute(queries.get_average_value(device_serial, metric_name))
            avg_value = cursor.fetchone()[0]
            result_list.append(
                {
                    "device_serial": device_serial,
                    "device_location": device[2],
                    "description": device[3],
                    "device_model": device[6],
                    "metric_name": status[2],
                    "metric_value": status[3],
                    "logging_time": status[4],
                    "avg_value": avg_value
                })
    # end of test section
    return jsonify(latest_status=result_list, critical_threshold=0.1)


@app.route('/api/get_device_log', methods=['GET'])
def get_device_log():
    result_list = []
    device_serial = request.args.get('device_serial')
    metric_name = request.args.get('metric_name')
    cursor.execute(queries.get_device_history(device_serial, metric_name))
    for status in cursor.fetchall():
        result_list.append(
            {
                "device_serial": status[1],
                "metric_name": status[2],
                "metric_value": status[3],
                "logging_time": status[4]
            }
        )
    return jsonify(device_log=result_list)


@app.route("/api/device_registration", methods=["POST"])
def device_registration():
    info = request.json
    print(request)
    user_name = info["user_name"]
    password = info["password"]
    cursor.execute(queries.get_user_password(user_name))
    user_info = cursor.fetchone()
    print(info)
    print(user_info)
    if user_info is None:
        return jsonify("User not found"), 404
    if bcrypt.check_password_hash(user_info[0], password):
        device_serial = info["device_serial"]
        device_location = info["device_location"]
        description = info["description"]
        device_model = info["device_model"]
        authorization_token = secrets.token_urlsafe(32)
        cursor.execute(
            queries.register_device(
                device_serial, device_location, description, authorization_token, device_model
            )
        )
        cnx.commit()
        return jsonify({"authorization_token": authorization_token}), 200
    else:
        return jsonify("Invalid username/password combination"), 400
    pass


@app.route("/api/user_registration", methods=["POST"])
def user_registration():
    remote_addr = request.environ.get("HTTP_X_REAL_IP", request.remote_addr)
    if (
            ipaddress.ip_address(remote_addr) in authorized_networks
            or remote_addr == "127.0.0.1"
    ):
        info = request.json
        user_name = info["user_name"]
        password = info["password"]
        pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        print(queries.register_user(user_name, pw_hash))
        cursor.execute(queries.register_user(user_name, pw_hash))
        cnx.commit()
        return jsonify(f"Created user {user_name}")
    else:
        return jsonify("Request from Unauthorized Network"), 400


@app.route("/api/device_status_update", methods=['POST'])
def device_status_update():
    info = request.json
    device_serial = info["device_serial"]
    authorization_token = info["authorization_token"]
    cursor.execute(queries.get_device_authorization_token(device_serial))
    device_info = cursor.fetchone()
    if device_info is None:
        return jsonify("Device not found"), 404
    elif authorization_token == device_info[0]:
        metric_name = info["metric_name"]
        print(info["metric_value"])
        metric_value = info["metric_value"]
        cursor.execute(
            queries.log_status(device_serial, metric_name, float(metric_value))
        )
        cnx.commit()
        return jsonify("Status logged"), 200
    else:
        return jsonify("Device serial and authorization token mismatch"), 400


@app.route("/api/upload_image", methods=['POST'])
def upload_image():
    img_info = request.json
    image_str = img_info["image_str"]
    image_description = img_info['description']
    md5_hash = img_info['md5_hash']
    cursor.execute(queries.insert_image(image_str, image_description, md5_hash))
    cnx.commit()
    return jsonify("Image uploaded"), 200


@app.route("/api/get_images", methods=['GET'])
def get_all_images():
    cursor.execute(queries.get_all_images())
    image_list = []
    for row in cursor.fetchall():
        image_list.append({
            "base64_str": row[0],
            "description": row[1],
            "md5_hash": row[2]}
        )
    return jsonify(image_data=image_list), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0")
