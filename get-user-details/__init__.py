import logging
import azure.functions as func
from azure.appconfiguration import AzureAppConfigurationClient
import pyodbc
import config
import json
import collections

server = 'server'
database = 'database',
table = 'users',
driver = '{ODBC Driver 17 for SQL Server}'
app_config = 'app_config'


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    app_config_client = AzureAppConfigurationClient.from_connection_string(
        app_config)
    username = app_config_client.get_configuration_setting(
        key='DB_USERNAME').value
    password = app_config_client.get_configuration_setting(
        key='DB_PASSWORD').value

    cnnString = 'DRIVER=' + driver + \
        ';SERVER=tcp:' + server + \
        ',1433;DATABASE=com682RDatabase;UID=' + username + \
        ';PWD=' + password + ';Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'

    conn = pyodbc.connect(cnnString)
    cursor = conn.cursor()

    userID = req.route_params.get("userID")

    selectQuery = """SELECT * FROM users WHERE userID = '""" + \
        userID + """';"""

    cursor.execute(selectQuery)
    row = cursor.fetchone()

    userDetails = []

    details = collections.OrderedDict()
    details["userID"] = row[0]
    details["username"] = row[1]
    details["emailAddress"] = row[2]
    details["forename"] = row[3]
    details["surname"] = row[4]
    details["isAdmin"] = row[5]
    userDetails.append(details)

    conn.close()

    return func.HttpResponse(json.dumps(userDetails), status_code=200)
