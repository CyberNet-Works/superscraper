import pandas as pd
import mysql.connector
from dotenv import dotenv_values
import os

# Get the full path to the .env file
env_file_path = os.path.join('C:\\Users\\USER\\Desktop\\Code\\SuperScraper', '.env')

# Load environment variables from .env file
env_vars = dotenv_values(env_file_path)

# Define the path to the CSV file
csv_path = r'C:\Users\USER\Desktop\Code\SuperScraper\newlist.csv'

# Read CSV file and extract search terms
df = pd.read_csv(csv_path)
search_terms = df['search_term'].tolist()

# Connect to MySQL database
try:
    connection = mysql.connector.connect(
        host=env_vars['DB_HOST'],
        port=env_vars['DB_PORT'],
        user=env_vars['DB_USER'],
        password=env_vars['DB_PASSWORD'],
        database=env_vars['DB_DATABASE']
    )
    if connection.is_connected():
        cursor = connection.cursor()
        
        # Read the latest campaign name from the campaigns table
        cursor.execute("SELECT campaign_name FROM campaigns ORDER BY campaign_id DESC LIMIT 1")
        latest_campaign_row = cursor.fetchone()
        if latest_campaign_row:
            latest_campaign_name = latest_campaign_row[0]
        else:
            latest_campaign_name = 0  # or any other initial value you prefer

        # Generate the new campaign name
        new_campaign_name = int(latest_campaign_name) + 1 



        # Insert the new campaign into the campaigns table
        cursor.execute("INSERT INTO campaigns (campaign_name) VALUES (%s)", (new_campaign_name,))
        connection.commit()

        # Get the maximum campaign ID
        cursor.execute("SELECT MAX(campaign_id) FROM campaigns")
        max_campaign_id = cursor.fetchone()[0]

        # Insert search terms into the superscraper_queue table with the max campaign ID
        for term in search_terms:
            insert_query = "INSERT INTO superscraper_queue (campaign_id, search_keyword) VALUES (%s, %s)"
            cursor.execute(insert_query, (max_campaign_id, term))
        
        # Commit changes and close connection
        connection.commit()
        cursor.close()
        connection.close()
        print("Search terms inserted successfully.")

except mysql.connector.Error as error:
    print("Error while connecting to MySQL:", error)
 