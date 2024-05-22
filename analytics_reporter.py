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

def construct_log_file(view_id, report_name, sequence=None, log_type="progress"):
    """Construct the log file name based on provided parameters."""
    log_file_name = f"{view_id}_{log_type}.log"
    if sequence:
        log_file_name = f"{view_id}_{log_type}.log"
    return log_file_name

def log_sampling_info(output_dir, view_id, report_name, sampling_info, sequence=None):
    """Log sampling information to a log file."""
    sampling_log_file = os.path.join(output_dir, construct_log_file(view_id, report_name, sequence, "sampling"))
    with open(sampling_log_file, 'a') as log_file:
        log_file.write(f"Sampling Info for View ID {view_id}, Report: {report_name}:\n")
        log_file.write(f"  Is Sampled: {sampling_info['is_sampled']}\n")
        log_file.write(f"  Samples Read Counts: {sampling_info['samples_read_counts']}\n")
        log_file.write(f"  Sampling Space Sizes: {sampling_info['sampling_space_sizes']}\n")
        log_file.write("\n")

def construct_output_file(property_name, view_id, report_id, report_name, sequence=None):
    """Construct the output file name based on provided parameters."""
    property_name_clean = clean_name(property_name) if property_name else ""
    report_name_clean = clean_name(report_name)

    output_dir = f"output/{view_id}_{property_name_clean}"
    os.makedirs(output_dir, exist_ok=True)

    if property_name_clean:
        if sequence:
            return f"{output_dir}/{property_name_clean}_{view_id}_{report_id}_{report_name_clean}_report_{sequence}.csv"
        else:
            return f"{output_dir}/{property_name_clean}_{view_id}_{report_id}_{report_name_clean}_report.csv"
    else:
        if sequence:
            return f"{output_dir}/{view_id}_{report_id}_{report_name_clean}_report_{sequence}.csv"
        else:
            return f"{output_dir}/{view_id}_{report_id}_{report_name_clean}_report.csv"

def log_quota_exceeded(view_id):
    """Log the date and time when quota is exceeded."""
    quota_log_file = f"quota_exceeded.log"
    with open(quota_log_file, 'a') as log_file:
        log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


def generate_report(report_config, start_date, end_date, api_key, view_id, report_name, output_file, sequence=None):
    """Generate report based on provided configuration."""
    global interrupted
    success = False
    data = []

    if not report_config:
        logging.error("Report configuration not found.")
        return

    dimensions = report_config['dimensions']
    metrics = report_config['metrics']
    page_size = report_config.get('page_size', 5000)  # Default to 5000 if not specified
    sampling_level = report_config.get('sampling_level', 'DEFAULT')  # Default to 'DEFAULT' if not specified
    metrics_filter = report_config.get('metrics_filter', False)

    output_dir = os.path.dirname(output_file)
    progress_file = os.path.join(output_dir, construct_log_file(view_id, report_name, sequence, "progress"))
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
                data, next_page_token, sampling_info, quota_exceeded = get_data(api_key, view_id, dimensions, metrics, start_date, end_date, format_date, page_size, next_page_token, sampling_level, metrics_filter)
                if quota_exceeded:
                    log_quota_exceeded(view_id)
                    break
                if sampling_info['is_sampled']:
                  logging.info("Data is sampled.")
                  logging.info(f"Sampling Read Counts: {sampling_info['samples_read_counts']}")
                  logging.info(f"Sample Space Sizes:, {sampling_info['sampling_space_sizes']}")
                  log_sampling_info(output_dir, view_id, report_name, sampling_info, sequence)
                else:
                  logging.info("Data is not sampled.")
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

            except ValueError as e:
                logging.error(f"ValueError: {e}")
                logging.error(traceback.format_exc())
                break  # Exit the loop on any error and save progress
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

def generate_all_reports(report_configs, start_date, end_date, api_key, view_id, property_name, sequence=None):
    """Generate all reports specified in the configuration."""
    property_name_clean = clean_name(property_name) if property_name else ""

    for report_config in report_configs:
        report_name = report_config['name']
        output_file = construct_output_file(property_name, view_id, report_config['id'], report_name, sequence)

        logging.info(f"Generating report for {report_name}")
        generate_report(report_config, start_date, end_date, api_key, view_id, report_name, output_file, sequence)
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
    parser.add_argument('--sequence', type=str, help='Optional sequence prefix for the output file name')
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
        output_file = construct_output_file(property_name, view_id, args.report_id, report_name, args.sequence)

        logging.info(f"Generate report for {report_name}")
        generate_report(report_config, start_date, end_date, api_key, view_id, report_name, output_file, sequence)
    else:
        generate_all_reports(report_configs['reports'], args.start, args.end, api_key, view_id, property_name, args.sequence)

if __name__ == "__main__":
    main()
