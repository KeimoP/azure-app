# db_connect.py
import pyodbc

server = 'tcp:sql-{yourname}-001.database.windows.net,1433'
database = 'sqldb-webapp-{yourname}-001'
username = 'sqladmin'
password = 'Complex.Pass123!'
driver = '{ODBC Driver 17 for SQL Server}'

connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'

def get_db_connection():
    try:
        return pyodbc.connect(connection_string)
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        return None