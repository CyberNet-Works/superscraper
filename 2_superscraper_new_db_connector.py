import requests
from bs4 import BeautifulSoup
import urllib.parse
import datetime
import time
import logging
import re
import mysql.connector
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Default parameters
default_params = {
    "campaign_id": 1,  # Add your campaign ID here
    "results_to_return": 25,
    "search_engine": "DuckDuckGo"
}


# Database connection
db_connection = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_DATABASE"),  # Changed to use DB_DATABASE instead of DB_NAME
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

# Generate timestamp
timestamp = datetime.datetime.now().strftime("%b%d_%Y_%I-%M-%S_%p").lower()

# Function to sanitize filename
def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

# Construct filename based on parameters
param_str = "_".join([f"{key}{value}" for key, value in default_params.items()])
param_str = sanitize_filename(param_str)
error_log_name = f"error_{param_str}_{timestamp}.txt"

# Update default_params with filenames
default_params["error_log_name"] = error_log_name

# Configure logging
logging.basicConfig(filename=default_params["error_log_name"], level=logging.ERROR)

# Variables to store statistics
start_time = time.time()
total_results_retrieved = 0

def search_duckduckgo(search_keyword):
    try:
        encoded_search_keyword = urllib.parse.quote(search_keyword)
        url = f"https://duckduckgo.com/html/?q={encoded_search_keyword}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        result_divs = soup.find_all('a', class_='result__url')
        results = []
        for i, result_div in enumerate(result_divs):
            if i < default_params["results_to_return"]:
                url = result_div['href']
                print(url)  # Print the URL
                results.append(url)
        return results
    except Exception as e:
        logging.error(f"Error processing search term '{search_keyword}' on DuckDuckGo: {e}")
        return []


def update_queue_table(cursor, search_results, queue_id):
    try:
        results_count = len(search_results)
        
        print(f"Updating queue_id: {queue_id}, Results count: {results_count}")  # Add this line for debugging
        cursor.execute("UPDATE superscraper_queue SET results_count = %s, status = 'incomplete' WHERE queue_id = %s", (results_count, queue_id))
        print("Update successful")  # Add this line for debugging
    except Exception as e:
        logging.error(f"Error updating superscraper_queue table: {e}")

def insert_results_table(cursor, search_results, queue_id):
    try:
        for result in search_results:
            cursor.execute("INSERT INTO superscraper_results (url, queue_id) VALUES (%s, %s)", (result, queue_id))
    except Exception as e:
        logging.error(f"Error inserting into superscraper_results table: {e}")

def get_unprocessed_rows(cursor):
    try:
        cursor.execute("SELECT queue_id, search_keyword FROM superscraper_queue WHERE campaign_id = %s AND (status = '' OR status = 'incomplete')", (default_params["campaign_id"],))
        return cursor.fetchall()
    except Exception as e:
        logging.error(f"Error fetching unprocessed rows from superscraper_queue table: {e}")
        return []

def main():
    global total_results_retrieved
    try:
        cursor = db_connection.cursor()
        print("Connected to the database.")  # Add this line
        unprocessed_rows = get_unprocessed_rows(cursor)
        print(f"Found {len(unprocessed_rows)} rows to process.")  # Add this line
        for row in unprocessed_rows:
            queue_id, search_keyword = row
            print(f"{timestamp} Processing queue_id: {queue_id}, Search Term: {search_keyword}")  # Add this line
            search_results = search_duckduckgo(search_keyword)
            if search_results:
                total_results_retrieved += len(search_results)
                update_queue_table(cursor, search_results, queue_id)
                insert_results_table(cursor, search_results, queue_id)
                db_connection.commit()
            else:
                logging.error("No more results for queue_id: {queue_id}, Search Term: {search_keyword}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        if db_connection.is_connected():
            cursor.close()
            db_connection.close()
        print("Disconnected from the database.")  # Add this line
        
if __name__ == "__main__":
    print("\nStarting script execution...\n")
    main()
