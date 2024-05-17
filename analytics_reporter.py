"""
Analytics Reporter

Author: Vimal Joseph
More Information: https://www.zyxware.com/article/6662/backup-universal-analytics-data-python

This script generates reports based on Google Analytics data.
"""
import argparse
import yaml
import signal
import os
import traceback
import json
import logging
from ga_data_fetcher import get_data
from utils import format_date, write_to_csv, append_to_csv, clear_csv_file, clean_name, load_progress, save_progress

interrupted = False  # Global variable to track if an interrupt signal was received

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Suppress detailed logging from oauth2client and other external libraries
logging.getLogger('oauth2client').setLevel(logging.WARNING)
logging.getLogger('googleapiclient').setLevel(logging.WARNING)

def load_yaml_config(file_path):
    """Load YAML configuration file."""
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        logging.error(f"Failed to load YAML config: {e}")
        raise

def signal_handler(sig, frame):
    """Handle interrupt signal (Ctrl+C)."""
    global interrupted
    logging.info("You pressed Ctrl+C! Waiting for the current request to complete...")
    interrupted = True

def construct_output_file(property_name, view_id, report_id, report_name):
    """Construct the output file name based on provided parameters."""
    property_name_clean = clean_name(property_name) if property_name else ""
    report_name_clean = clean_name(report_name)
    if property_name_clean:
        return f"{property_name_clean}_{view_id}_{report_id}_{report_name_clean}_report.csv"
    else:
        return f"{view_id}_{report_id}_{report_name_clean}_report.csv"

def generate_report(report_config, start_date, end_date, api_key, view_id, output_file):
    """Generate report based on provided configuration."""
    global interrupted
    success = False
    data = []

    if not report_config:
        logging.error("Report configuration not found.")
        return

    dimensions = report_config['dimensions']
    metrics = report_config['metrics']
    page_size = report_config.get('page_size', 500)  # Default to 500 if not specified
    sampling_level = report_config.get('sampling_level', 'DEFAULT')  # Default to 'DEFAULT' if not specified
    metrics_filter = report_config.get('metrics_filter', False)

    progress_file = f"{view_id}_progress.log"
    progress_data = load_progress(progress_file)

    total_records_downloaded = 0
    first_page = True

    if output_file in progress_data:
        next_page_token, total_records_downloaded = progress_data[output_file]
        total_records_downloaded = int(total_records_downloaded)
        first_page = False
    else:
        clear_csv_file(output_file)
        next_page_token = None

    try:
        while True:
            if interrupted:
                break

            if next_page_token is None:
                current_start = 1
            else:
                current_start = total_records_downloaded + 1

            logging.info(f"Downloading data for {output_file}")

            if not first_page and not next_page_token:
                logging.info(f"No more data to download for {output_file}")
                success = False
                break

            try:
                data, next_page_token = get_data(api_key, view_id, dimensions, metrics, start_date, end_date, format_date, page_size, next_page_token, sampling_level, metrics_filter)
                if not data:
                    logging.info(f"No data available to download for {output_file}")
                    break

                if first_page:
                    write_to_csv(data, output_file)
                    first_page = False
                else:
                    append_to_csv(data, output_file)

                total_records_downloaded += len(data)

                logging.info(f"Total records downloaded for {output_file}: {total_records_downloaded}")

                progress_data[output_file] = (next_page_token if next_page_token else '', total_records_downloaded)
                save_progress(progress_file, progress_data)

                if not next_page_token or interrupted:
                    break

            except Exception as e:
                logging.error(f"An error occurred while fetching data: {e}")
                logging.error(traceback.format_exc())
                break  # Exit the loop on any error and save progress

        success = True  # Set success to True if the loop completes without interruption

    except KeyboardInterrupt:
        pass  # This block will not be used, since signal handler handles SIGINT

    finally:
        if success and data:
            logging.info(f"Data available in CSV file: {output_file}")

def generate_all_reports(report_configs, start_date, end_date, api_key, view_id, property_name):
    """Generate all reports specified in the configuration."""
    property_name_clean = clean_name(property_name) if property_name else ""

    for report_config in report_configs:
        report_name = report_config['name']
        output_file = construct_output_file(property_name, view_id, report_config['id'], report_name)

        logging.info(f"Generating report for {report_name}")
        generate_report(report_config, start_date, end_date, api_key, view_id, output_file)
        if interrupted:
            logging.info("Interrupted! Stopping further report generation.")
            break
    else:
        logging.info("Downloaded all reports")

def main():
    """Main function to parse arguments and initiate report generation."""
    parser = argparse.ArgumentParser(description='Generate Google Analytics reports.')
    parser.add_argument('-id', '--report_id', type=int, help='ID of the report to generate')
    parser.add_argument('-s', '--start', type=str, required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('-e', '--end', type=str, required=True, help='End date (YYYY-MM-DD)')
    parser.add_argument('--settings', type=str, help='Path to settings YAML file')
    args = parser.parse_args()

    settings_file = args.settings if args.settings else "settings.yml"
    settings = load_yaml_config(settings_file)
    report_configs = load_yaml_config(settings['analytics_settings']['reports_config'])

    api_key = settings['analytics_settings']['api_key']
    view_id = settings['analytics_settings']['view_id']
    property_name = settings['analytics_settings'].get('property_name', '')

    # Set up signal handler for CTRL+C
    signal.signal(signal.SIGINT, signal_handler)

    if args.report_id:
        report_config = next((r for r in report_configs['reports'] if r['id'] == args.report_id), None)
        if not report_config:
            logging.error(f"Report configuration for ID {args.report_id} not found.")
            return
        report_name = report_config['name']
        output_file = construct_output_file(property_name, view_id, args.report_id, report_name)

        logging.info(f"Generate report for {report_name}")
        generate_report(report_config, args.start, args.end, api_key, view_id, output_file)
    else:
        generate_all_reports(report_configs['reports'], args.start, args.end, api_key, view_id, property_name)

if __name__ == "__main__":
    main()
