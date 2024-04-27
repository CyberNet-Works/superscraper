import pandas as pd
import mysql.connector
from dotenv import dotenv_values

# Define the path to the CSV file
csv_path = r'C:\Users\USER\Desktop\Code\SuperScraper\newlist.csv'

# Load environment variables from .env file
env_vars = dotenv_values('.env')

# Read CSV file and extract search terms
df = pd.read_csv(csv_path)
search_terms = df['search_term'].tolist()

# Connect to MySQL database
try:
    connection = mysql.connector.connect(
        host=env_vars['DB_HOST'],
        user=env_vars['DB_USER'],
        password=env_vars['DB_PASSWORD'],
        database=env_vars['DB_DATABASE']
    )
    if connection.is_connected():
        cursor = connection.cursor()

        # Insert search terms into the database
        for term in search_terms:
            insert_query = "INSERT INTO superscraper_queue (search_keyword) VALUES (%s)"
            cursor.execute(insert_query, (term,))
        
        # Commit changes and close connection
        connection.commit()
        cursor.close()
        connection.close()
        print("Search terms inserted successfully.")

except mysql.connector.Error as error:
    print("Error while connecting to MySQL:", error)
