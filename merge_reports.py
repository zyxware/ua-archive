import os
import pandas as pd
from glob import glob
import argparse
import re

def merge_report_files(input_dir, output_dir):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Dictionary to hold report file information
    report_files = {}

    # Regex to match report files
    report_file_pattern = re.compile(r'^(.*)_(\d+)_(\d+)_([a-zA-Z-]+)_report_(\d+)\.csv$')

    # Find all matching files
    for filepath in glob(os.path.join(input_dir, '*.csv')):
        filename = os.path.basename(filepath)
        match = report_file_pattern.match(filename)
        if match:
            base_name = match.group(1)
            view_id = match.group(2)
            report_id = match.group(3)
            report_name = match.group(4)
            sequence = int(match.group(5))

            key = f"{base_name}_{view_id}_{report_id}_{report_name}"
            if key not in report_files:
                report_files[key] = []
            report_files[key].append((sequence, filepath))
        else:
            print(f"Skipping file {filename}: Filename does not match expected pattern")

    # Merge files for each report
    with open(os.path.join(output_dir, 'all_reports.log'), 'w') as log_file:
        for key, files in report_files.items():
            files.sort()  # Sort files by sequence number
            output_file = os.path.join(output_dir, f"{key}_report_full.csv")
            total_records = 0
            start_date = None
            end_date = None
            num_files_merged = len(files)

            merged_df = pd.DataFrame()
            for seq, filepath in files:
                df = pd.read_csv(filepath)
                if 'ga:date' in df.columns:
                    if start_date is None:
                        start_date = df['ga:date'].iloc[0]
                    end_date = df['ga:date'].iloc[-1]
                num_records = len(df)  # Count all rows, no header adjustment
                total_records += num_records
                merged_df = pd.concat([merged_df, df], ignore_index=True)

            # Write the merged dataframe to CSV
            merged_df.to_csv(output_file, index=False)

            log_file.write(f"{output_file},{start_date or ''},{end_date or ''},{num_files_merged},{total_records}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Merge report files into a single file for each report.')
    parser.add_argument('input_dir', type=str, help='Path to the input directory containing report files.')
    parser.add_argument('output_dir', type=str, nargs='?', default='.', help='Path to the output directory where merged files will be stored. Defaults to current directory.')

    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir

    merge_report_files(input_dir, output_dir)
