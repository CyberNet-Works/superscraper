#superscraper by cyber-networks
#make sure to check params: inputfilename, start_row, last_row, results_to_return.


import csv
import requests
from bs4 import BeautifulSoup
import urllib.parse
import datetime
import time
import logging
import re

# Default parameters
default_params = {
    "input_filename": "input.csv",
    "start_row": 1,
    "last_row": 999,
    "results_to_return": 25,
    "search_engine": "DuckDuckGo"
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
print("\033[91mConfirmation:\033[0m")
for key, value in default_params.items():
    print(f"\033[92m{key}:\033[0m {value}")
confirmation = input("Continue with these parameters? (y/n): ")
if confirmation.lower() != 'y':
    print("Script execution aborted.")
    exit()

# Configure logging
logging.basicConfig(filename=default_params["error_log_name"], level=logging.ERROR)

# Variables to store statistics
start_time = time.time()
rows_processed = 0
total_results_retrieved = 0

def search_duckduckgo(search_term):
    try:
        encoded_search_term = urllib.parse.quote(search_term)
        url = f"https://duckduckgo.com/html/?q={encoded_search_term}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        result_divs = soup.find_all('a', class_='result__url')
        results = []
        for i, result_div in enumerate(result_divs):
            if i < default_params["results_to_return"]:
                results.append(result_div['href'])
        return results
    except Exception as e:
        logging.error(f"Error processing search term '{search_term}' on DuckDuckGo: {e}")
        return []

def get_search_results(search_term):
    if default_params["search_engine"] == "DuckDuckGo":
        return search_duckduckgo(search_term)
    else:
        logging.error(f"Unsupported search engine: {default_params['search_engine']}")
        return []

def main(input_csv, output_csv):
    global rows_processed, total_results_retrieved
    with open(input_csv, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        total_rows = sum(1 for _ in csv_reader)
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
                navbar = f"\033[91m\033[40mStart Time:\033[0m {datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')} | \033[30m\033[42mRuntime:\033[0m {datetime.timedelta(seconds=int(runtime))} | \033[30m\033[42mCurrent Row:\033[0m {row_number} | \033[30m\033[42mRows Processed:\033[0m {rows_processed}/{total_rows_in_range} | \033[30m\033[42mTotal Results Retrieved:\033[0m {total_results_retrieved} | \033[30m\033[42mRate:\033[0m {average_time_per_row:.2f} sec/row | \033[92m\033[40mPercent Complete:\033[0m {percent_complete:.2f}% | \033[92m\033[40mTime Remaining:\033[0m {datetime.timedelta(seconds=int(time_remaining))} | \033[92m\033[40mCurrent Time:\033[0m {current_time} | \033[92m\033[40mSearch Engine:\033[0m {default_params['search_engine']}"
                print('\033[7m' + navbar + '\033[0m')

if __name__ == "__main__":
    print("\n\033[92mStarting script execution...\033[0m\n")
    main(default_params["input_filename"], default_params["output_filename"])
