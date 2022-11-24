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

    cnnString = 'DRIVER=' + driver + \
        ';SERVER=tcp:' + server + \
        ',1433;DATABASE=com682RDatabase;UID=' + username + \
        ';PWD=' + password + ';Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'

    conn = pyodbc.connect(cnnString)
    cursor = conn.cursor()

    # Request params
    username = req.form['username']
    emailAddress = req.form['emailAddress']
    forename = req.form['forename']
    surname = req.form['surname']
    isAdmin = req.form['isAdmin']
    password = req.form['password']

    # Prevent duplicated username or email addresses
    selectQuery = """SELECT COUNT(userID) FROM users WHERE username = '""" + \
        username + """' OR emailAddress = '""" + emailAddress + """';"""

    cursor.execute(selectQuery)
    row = cursor.fetchone()

    if row[0] >= 1:
        return func.HttpResponse("Username or email address already exists", status_code=409)

    # Generate a hashed password.
    hashedPassword = str(bcrypt.hashpw(
        password.encode('utf8'), bcrypt.gensalt()))
    hashedPassword = hashedPassword.split("'", 3)
    query = 'INSERT INTO users (username, emailAddress, forename, surname, isAdmin, password) ' + \
            """VALUES ('""" + username + """','""" + emailAddress + """','""" + \
        forename + """','""" + surname + """','""" + isAdmin + """','""" + \
            str(hashedPassword[1]) + """');"""

    cursor.execute(query)
    conn.commit()
    conn.close()

    return func.HttpResponse("Account created successfully.", status_code=200)
