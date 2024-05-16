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
from ga_data_fetcher import get_data
from utils import format_date, write_to_csv, append_to_csv, read_last_page_token, clear_csv_file

interrupted = False  # Global variable to track if an interrupt signal was received

def load_yaml_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def signal_handler(sig, frame):
    global interrupted
    print("You pressed Ctrl+C! Waiting for the current request to complete...")
    interrupted = True

def generate_report(report_config, start_date, end_date, api_key, view_id, output_file):
    global interrupted
    if not report_config:
        print("Report configuration not found.")
        return

    dimensions = report_config['dimensions']
    metrics = report_config['metrics']
    page_size = report_config.get('page_size', 1000)  # Default to 1000 if not specified
    sampling_level = report_config.get('sampling_level', 'DEFAULT')  # Default to 'DEFAULT' if not specified
    metrics_filter = report_config.get('metrics_filter', False)

    progress_file = output_file + '.progress'
    total_records_downloaded = 0
    first_page = True

    if os.path.exists(progress_file):
        next_page_token, total_records_downloaded = read_last_page_token(progress_file)
        total_records_downloaded = int(total_records_downloaded)
        first_page = False  # Continue appending data if resuming
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

            print(f"Downloading records {current_start} to {current_start + page_size - 1} for {output_file}")

            try:
                data, next_page_token = get_data(api_key, view_id, dimensions, metrics, start_date, end_date, format_date, page_size, next_page_token, sampling_level, metrics_filter)
                if not data:
                    print(f"No more data to download for {output_file}")
                    break

                print(f"Fetched {len(data)} records.")

                if first_page:
                    write_to_csv(data, output_file)
                    first_page = False
                else:
                    append_to_csv(data, output_file)

                total_records_downloaded += len(data)

                with open(progress_file, 'w') as pf:
                    pf.write(f"{next_page_token if next_page_token else ''},{total_records_downloaded}")

                if not next_page_token or interrupted:
                    break

            except Exception as e:
                print(f"An error occurred while fetching data: {e}")
                print(traceback.format_exc())
                break  # Exit the loop on any error and save progress

    except KeyboardInterrupt:
        pass  # This block will not be used, since signal handler handles SIGINT
    finally:
        if os.path.exists(progress_file):
            if not next_page_token:
                os.remove(progress_file)
        print(f"Successfully saved report to CSV file: {output_file}")

def generate_all_reports(report_configs, start_date, end_date, api_key, view_id):
    for report_config in report_configs:
        report_name = report_config['name'].replace(' ', '-').lower()
        output_file = f"{report_config['id']}_{report_name}_report.csv"
        print(f"Generating report for {report_name}")
        generate_report(report_config, start_date, end_date, api_key, view_id, output_file)
        if interrupted:
            print("Interrupted! Stopping further report generation.")
            break

def main():
    parser = argparse.ArgumentParser(description='Generate Google Analytics reports.')
    parser.add_argument('-id', '--report_id', type=int, help='ID of the report to generate')
    parser.add_argument('-s', '--start', type=str, required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('-e', '--end', type=str, required=True, help='End date (YYYY-MM-DD)')
    args = parser.parse_args()

    settings = load_yaml_config("settings.yml")
    report_configs = load_yaml_config(settings['analytics_settings']['reports_config'])

    api_key = settings['analytics_settings']['api_key']
    view_id = settings['analytics_settings']['view_id']

    # Set up signal handler for CTRL+C
    signal.signal(signal.SIGINT, signal_handler)

    if args.report_id:
        report_config = next((r for r in report_configs['reports'] if r['id'] == args.report_id), None)
        if not report_config:
            print(f"Report configuration for ID {args.report_id} not found.")
            return
        report_name = report_config['name'].replace(' ', '-').lower()
        output_file = f"{args.report_id}_{report_name}_report.csv"
        print(f"Generate report for {report_name}")
        generate_report(report_config, args.start, args.end, api_key, view_id, output_file)
    else:
        generate_all_reports(report_configs['reports'], args.start, args.end, api_key, view_id)

if __name__ == "__main__":
    main()

