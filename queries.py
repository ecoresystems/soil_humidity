from datetime import datetime


class Queries:
    def __init__(self):
        pass

    @staticmethod
    def create_authorized_users_table():
        return (
            "CREATE TABLE IF NOT EXISTS AUTHORIZED_USERS("
            "ID INT AUTO_INCREMENT PRIMARY KEY,"
            "USER_NAME VARCHAR(50) NOT NULL UNIQUE ,"
            "PASSWORD VARCHAR(128) NOT NULL,"
            "REGISTRATION_TIME TIMESTAMP NOT NULL )"
        )

    @staticmethod
    def create_devices_table():
        return (
            "CREATE TABLE IF NOT EXISTS DEVICES("
            "DEVICE_ID INT AUTO_INCREMENT PRIMARY KEY ,"
            "DEVICE_SERIAL VARCHAR(30) NOT NULL UNIQUE ,"
            "DEVICE_LOCATION VARCHAR(50),"
            "DESCRIPTION VARCHAR(100),"
            "AUTHORIZATION_TOKEN VARCHAR(32) NOT NULL,"
            "REGISTRATION_TIME TIMESTAMP NOT NULL,"
            "DEVICE_MODEL VARCHAR(30) NOT NULL)"
        )

    @staticmethod
    def create_device_status_table():
        return (
            "CREATE TABLE IF NOT EXISTS DEVICE_STATUS("
            "STATUS_ID BIGINT AUTO_INCREMENT PRIMARY KEY ,"
            "DEVICE_SERIAL VARCHAR(30),"
            "METRIC_NAME VARCHAR(32) NOT NULL ,"
            "METRIC_VALUE FLOAT NOT NULL,"
            "LOGGING_TIME TIMESTAMP )"
        )

    @staticmethod
    def log_status(device_serial: str, metric_name: str, metric_value: float):
        return f"INSERT INTO DEVICE_STATUS (DEVICE_SERIAL,METRIC_NAME,METRIC_VALUE,LOGGING_TIME) VALUES ('{device_serial}','{metric_name}',{metric_value},'{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}')"

    @staticmethod
    def register_user(user_name: str, pw_hash: str):
        return (
            f"INSERT INTO AUTHORIZED_USERS (USER_NAME,PASSWORD,REGISTRATION_TIME) VALUES ('{user_name}','{pw_hash}',"
            f"'{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}')"
        )

    @staticmethod
    def get_user_password(user_name: str):
        return f"SELECT PASSWORD FROM AUTHORIZED_USERS WHERE USER_NAME = '{user_name}'"

    @staticmethod
    def register_device(
            device_serial: str,
            device_location: str,
            description: str,
            authorization_token: str,
            device_model: str
    ):
        return (
            f"INSERT INTO DEVICES (DEVICE_SERIAL,DEVICE_LOCATION,DESCRIPTION,AUTHORIZATION_TOKEN,REGISTRATION_TIME,DEVICE_MODEL)"
            f"VALUES ('{device_serial}','{device_location}','{description}','{authorization_token}','{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}',"
            f"'{device_model}')"
        )

    @staticmethod
    def get_device_authorization_token(device_serial: str):
        return f"SELECT AUTHORIZATION_TOKEN FROM DEVICES WHERE DEVICE_SERIAL = '{device_serial}'"

    @staticmethod
    def get_all_devices():
        return "SELECT * FROM DEVICES"

    @staticmethod
    def get_latest_status(device_serial: str, metric_name: str):
        return f"select * from DEVICE_STATUS WHERE DEVICE_SERIAL = \'{device_serial}\' AND METRIC_NAME = \'{metric_name}\' ORDER BY LOGGING_TIME DESC LIMIT 1"

    @staticmethod
    def get_device_history(device_serial: str, metric_name: str):
        return f"select * from DEVICE_STATUS where DEVICE_SERIAL = \'{device_serial}\' AND METRIC_NAME = \'{metric_name}\' ORDER BY LOGGING_TIME DESC"

    @staticmethod
    def get_device_info(device_serial: str):
        return f"select * from DEVICES where DEVICE_SERIAL = \'{device_serial}\'"

    @staticmethod
    def get_unique_metrics_for_device(device_serial: str):
        return f"select distinct METRIC_NAME from DEVICE_STATUS where DEVICE_SERIAL = \'{device_serial}\'"
