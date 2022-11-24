import logging
import azure.functions as func
from azure.appconfiguration import AzureAppConfigurationClient
import pyodbc
import bcrypt
import config
import jwt
import datetime
import json

server = 'com682-rossg.database.windows.net'
database = 'com682RDatabase',
table = 'users',
driver = '{ODBC Driver 17 for SQL Server}'
app_config = 'Endpoint=https://rg-secrets-a2.azconfig.io;Id=GCgR-l8-s0:edHmEHeCDeA3x1KHcmv7;Secret=jdIKdPPslmeJQlsQkdTyRg8aNluYh68ZI35csCCl8kc='


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    app_config_client = AzureAppConfigurationClient.from_connection_string(
        app_config)
    username = app_config_client.get_configuration_setting(
        key='DB_USERNAME').value
    password = app_config_client.get_configuration_setting(
        key='DB_PASSWORD').value
    secret_key = app_config_client.get_configuration_setting(
        key='SECRET_KEY').value

    cnnString = 'DRIVER=' + driver + \
        ';SERVER=tcp:' + server + \
        ',1433;DATABASE=com682RDatabase;UID=' + username + \
        ';PWD=' + password + ';Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'

    conn = pyodbc.connect(cnnString)
    cursor = conn.cursor()

    username = req.form['username']
    password = req.form['password']

    # Check username exists
    selectQuery = """SELECT * FROM users WHERE username = '""" + \
        username + """';"""

    cursor.execute(selectQuery)
    row = cursor.fetchone()

    if row is not None:
        checkPassword = bytes(row[6], 'UTF-8')
        if bcrypt.checkpw(bytes(password, 'UTF-8'),
                          checkPassword):
            myJWT = jwt.encode({
                'username': username,
                'userID': row[0],
                'isAdmin': row[5],
                'exp': datetime.datetime.utcnow() +
                datetime.timedelta(minutes=30)
            }, secret_key)

            return func.HttpResponse(myJWT.decode('UTF-8'), status_code=200)

    conn.close()

    return func.HttpResponse("Username or password is incorrect.", status_code=401)
