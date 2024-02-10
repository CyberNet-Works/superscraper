SuperScraper by Cyber-Networks
SuperScraper is a Python script designed for web scraping search results from DuckDuckGo based on user-defined search terms. It offers various features for customization and efficient data retrieval.

Features:
Customizable Parameters: Users can adjust parameters such as input filename, start row, last row, and number of results to return.
Error Logging: SuperScraper includes error logging functionality to track and troubleshoot any issues encountered during execution.
Real-Time Progress Tracking: Users can monitor the progress of the script in real-time, including statistics such as runtime, rows processed, and total results retrieved.
CSV Output Generation: The script generates a CSV file containing the search terms and their corresponding search results.

Usage:
Ensure to check and adjust the parameters in the script according to your requirements, especially input_filename, start_row, last_row, and results_to_return.
Execute the script, and follow the on-screen prompts to confirm the parameters and start the scraping process.
Monitor the progress and review the output CSV file for the scraped data.

Requirements:
Python 3.x
Libraries: csv, requests, BeautifulSoup, urllib, datetime, time, logging, re

Usage Example:
python
Copy code
python SuperScraper.py

Note:
Please ensure that you have proper permissions and adhere to the terms of service of the website being scraped.

Use responsibly and considerate of server load to avoid potential issues or bans.