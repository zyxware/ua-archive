"""
Analytics Reporter

Author: Vimal Joseph
More Information: https://www.zyxware.com/article/6662/backup-universal-analytics-data-python

This script generates reports based on Google Analytics data.
"""
import argparse
import yaml
from ga_data_fetcher import get_data
from utils import format_date, write_to_csv

def load_yaml_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def generate_report(report_config, start_date, end_date, api_key, view_id, output_file):
    if not report_config:
        print("Report configuration not found.")
        return

    dimensions = report_config['dimensions']
    metrics = report_config['metrics']

    data = get_data(api_key, view_id, dimensions, metrics, start_date, end_date, format_date)

    if data:
        write_to_csv(data, output_file)
        print(f"Successfully saved report to CSV file: {output_file}")
    else:
        print("No data received for the report.")

def main():
    parser = argparse.ArgumentParser(description='Generate Google Analytics reports.')
    parser.add_argument('-id', '--report_id', type=int, required=True, help='ID of the report to generate')
    parser.add_argument('-s', '--start', type=str, required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('-e', '--end', type=str, required=True, help='End date (YYYY-MM-DD)')
    args = parser.parse_args()

    settings = load_yaml_config("settings.yml")
    report_configs = load_yaml_config(settings['analytics_settings']['reports_config'])

    report_id = args.report_id
    start_date = args.start
    end_date = args.end
    api_key = settings['analytics_settings']['api_key']
    view_id = settings['analytics_settings']['view_id']

    report_config = next((r for r in report_configs['reports'] if r['id'] == report_id), None)
    if not report_config:
        print(f"Report configuration for ID {report_id} not found.")
        return
    # Construct the file name
    report_name = report_config['name'].replace(' ', '-').lower()
    output_file = f"{report_id}_{report_name}_report.csv"
    generate_report(report_config, start_date, end_date, api_key, view_id, output_file)


if __name__ == "__main__":
    main()

