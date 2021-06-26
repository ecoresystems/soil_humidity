from flask import Flask

import configparser
import ipaddress
import secrets
import sqlite3

import mysql.connector

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


@app.route("/")
def hello():
    return "<h1 style='color:blue'>Hello There!</h1>"


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
    if bcrypt.check_password_hash(user_info[0],password):
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


@app.route("/api/device_status_update")
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
        metric_value = eval(info["metric_value"])
        cursor.execute(
            queries.log_status(device_serial, metric_name, float(metric_value))
        )
        cnx.commit()
        return jsonify("Status logged"), 200
    else:
        return jsonify("Device serial and authorization token mismatch"), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0")
