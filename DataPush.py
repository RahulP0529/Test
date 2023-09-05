import pyodbc
from Logins import SQLLogins

class SQLPush(object):
    def create_data(self, data_list):
        try:
            # Establish a connection
            self.SQLLogins = SQLLogins()
            conn = pyodbc.connect(self.SQLLogins.connection_string)
            print("Connected to Azure SQL Server!")

            # Create a cursor object
            cursor = conn.cursor()

            # Check if the table exists
            table_check_query = "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'ValorantStats'"
            cursor.execute(table_check_query)
            table_exists = cursor.fetchone()[0]
            if table_exists == 0:
                print("Table does not exist")

            insert_query = "INSERT INTO ValorantStats (Date, Username, Team, Opponent, Kills, Deaths, Assists, KD_Diff, ADR, HS, FK_DIFF) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

            for entry in data_list:
                cursor.execute(insert_query, tuple(entry.values()))
                conn.commit()

            print("Data inserted successfully!")

            # Close the connection when done
            conn.close()
            print("Connection closed.")

        except pyodbc.Error as e:
            print("Error:", e)