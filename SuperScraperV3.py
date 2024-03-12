import csv
import requests
from bs4 import BeautifulSoup
import urllib.parse
import datetime
import time
import logging
import re
import threading

# Default parameters
default_params = {
    "input_filename": "input.csv",
    "start_row": 1,
    "last_row": "all",
    "results_to_return": 25,
    "search_engine": "DuckDuckGo",
    "retry_attempts": 3,
    "retry_delay": 10  # in seconds
}

# Generate timestamp
timestamp = datetime.datetime.now().strftime("%b%d_%Y_%I-%M-%S_%p").lower()

# Function to sanitize filename
def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

# Construct filename based on parameters
param_str = "_".join([f"{key}{value}" for key, value in default_params.items()])
param_str = sanitize_filename(param_str)
output_filename = f"output_{param_str}_{timestamp}.csv"
error_log_name = f"error_{param_str}_{timestamp}.txt"

# Update default_params with filenames
default_params["output_filename"] = output_filename
default_params["error_log_name"] = error_log_name

# Confirmation of parameters
print("\033[4m\033[31mConfirmation:\033[0m")
for key, value in default_params.items():
    print(f"\033[92m{key}:\033[0m  {value}")
confirmation = input("\033[31mContinue with these parameters? (\033[1my/n): \033[0m")
if confirmation.lower() != 'y':
    print("Script execution aborted.")
    exit()

# Configure logging
logging.basicConfig(filename=default_params["error_log_name"], level=logging.ERROR)

# Variables to store statistics
start_time = time.time()
rows_processed = 0
total_results_retrieved = 0

# Define a flag for pausing the script
pause_flag = threading.Event()

def search_duckduckgo(search_term, retry_attempts, retry_delay):
    for attempt in range(retry_attempts):
        try:
            encoded_search_term = urllib.parse.quote(search_term)
            url = f"https://duckduckgo.com/html/?q={encoded_search_term}"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise exception for non-200 status codes
            soup = BeautifulSoup(response.text, 'html.parser')
            result_divs = soup.find_all('a', class_='result__url')
            results = []
            for i, result_div in enumerate(result_divs):
                if i < default_params["results_to_return"]:
                    results.append(result_div['href'])
            if len(results) < 20:  # If less than 20 results retrieved, retry
                raise Exception("Less than 20 results retrieved")
            return results
        except Exception as e:
            logging.error(f"Error processing search term '{search_term}' on DuckDuckGo: {e}")
            if attempt < retry_attempts - 1:  # If not the last attempt
                time.sleep(retry_delay)  # Wait for retry_delay seconds before retrying
    return []


def get_search_results(search_term):
    if default_params["search_engine"] == "DuckDuckGo":
        return search_duckduckgo(search_term, default_params["retry_attempts"], default_params["retry_delay"])
    else:
        logging.error(f"Unsupported search engine: {default_params['search_engine']}")
        return []

def main(input_csv, output_csv):
    global rows_processed, total_results_retrieved
    with open(input_csv, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        total_rows = sum(1 for _ in csv_reader)
        if default_params["last_row"].lower() == "none" or default_params["last_row"].lower() == "all":
            default_params["last_row"] = total_rows  # Set last_row to total_rows if it's "None" or "none" or "all"
        else:
            default_params["last_row"] = int(default_params["last_row"])  # Convert last_row to int if it's not "None" or "none" or "all"
        total_rows_in_range = default_params["last_row"] - default_params["start_row"] + 1  # Calculate total rows in the specified range
        csv_file.seek(0)
        next(csv_reader)  # Skip header
        for _ in range(default_params["start_row"] - 1):
            next(csv_reader)  # Skip rows until start_row
        with open(output_csv, 'w', newline='') as output_file:
            csv_writer = csv.writer(output_file)
            header_row = ['Search Term'] + [f'Result {i+1}' for i in range(default_params["results_to_return"])]
            csv_writer.writerow(header_row)
            for row_number, row in enumerate(csv_reader, start=default_params["start_row"]):
                if row_number > default_params["last_row"]:
                    break
                if pause_flag.is_set():  # Check if pause flag is set
                    print("Script paused. Press Enter to resume.")
                    input()  # Wait for user input to resume
                    pause_flag.clear()  # Clear pause flag
                search_term = row[0]
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\033[92m{timestamp}\033[0m - \033[91mRow {row_number}\033[0m: \033[93mSearch Term:\033[0m {search_term}")
                search_results = get_search_results(search_term)
                if search_results:
                    csv_writer.writerow([search_term] + search_results)
                    total_results_retrieved += len(search_results)
                    for i, result in enumerate(search_results):
                        print(f"Result {i+1}: {result}")
                else:
                    print("No more results")
                    csv_writer.writerow([search_term] + ["No more results"])
                rows_processed += 1
                runtime = time.time() - start_time
                average_time_per_row = runtime / rows_processed if rows_processed else 0
                percent_complete = (rows_processed / total_rows_in_range) * 100
                time_remaining = (total_rows_in_range - rows_processed) * average_time_per_row
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                navbar = f"Start Time: {datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')}  Runtime: {datetime.timedelta(seconds=int(runtime))}  Row: {row_number}  Rows Processed: {rows_processed}/{total_rows_in_range}  Total Results Retrieved: {total_results_retrieved}  Rate: {average_time_per_row:.2f} sec/row  Percent Complete: {percent_complete:.2f}%  Time Remaining: {datetime.timedelta(seconds=int(time_remaining))}  Current Time: {current_time}  Search Engine: {default_params['search_engine']}  Retry Attempts: {default_params['retry_attempts']}  Retry Delay: {default_params['retry_delay']} seconds"
                print('\033[7m' + navbar + '\033[0m')

# Input handler thread function
def input_handler():
    global pause_flag
    while True:
        try:
            input("Press Enter to pause the script: ")
            pause_flag.set()  # Set pause flag
            print("Process paused.")
            input("Press Enter to resume the script: ")
            pause_flag.clear()  # Clear pause flag
            print("Process resumed.")
        except KeyboardInterrupt:
            print("\nInput handler terminated.")
            break



if __name__ == "__main__":
    # Start input handler thread
    input_thread = threading.Thread(target=input_handler, daemon=True)
    input_thread.start()

    print("\n\033[92mStarting script execution...\033[0m\n")
    main(default_params["input_filename"], default_params["output_filename"])
